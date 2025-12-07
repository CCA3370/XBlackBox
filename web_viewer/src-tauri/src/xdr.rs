use byteorder::{LittleEndian, ReadBytesExt};
use chrono::DateTime;
use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::{self, BufReader, Read, Seek, SeekFrom};
use std::path::Path;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct XDRHeader {
    pub magic: String,
    pub version: u16,
    pub level: u8,
    pub level_name: String,
    pub interval: f32,
    pub start_timestamp: u64,
    pub start_datetime: String,
    pub dataref_count: u16,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub total_records: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub end_timestamp: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub end_datetime: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub duration: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatarefDef {
    pub name: String,
    #[serde(rename = "type")]
    pub data_type: String,
    pub array_size: u8,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(untagged)]
pub enum DataValue {
    Float(f32),
    Int(i32),
    String(String),
    FloatArray(Vec<f32>),
    IntArray(Vec<i32>),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DataFrame {
    pub timestamp: f32,
    pub values: Vec<DataValue>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Parameter {
    pub index: usize,
    pub array_index: usize,
    pub name: String,
    #[serde(rename = "type")]
    pub data_type: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Statistics {
    pub name: String,
    pub count: usize,
    pub min: f64,
    pub max: f64,
    pub mean: f64,
    pub median: f64,
    pub std: f64,
    pub range: f64,
}

pub struct XDRData {
    pub filepath: String,
    pub header: XDRHeader,
    pub datarefs: Vec<DatarefDef>,
    pub frames: Vec<DataFrame>,
    is_complete: bool,
}

impl XDRData {
    pub fn new() -> Self {
        XDRData {
            filepath: String::new(),
            header: XDRHeader {
                magic: String::new(),
                version: 0,
                level: 0,
                level_name: String::new(),
                interval: 0.0,
                start_timestamp: 0,
                start_datetime: String::new(),
                dataref_count: 0,
                total_records: None,
                end_timestamp: None,
                end_datetime: None,
                duration: None,
            },
            datarefs: Vec::new(),
            frames: Vec::new(),
            is_complete: false,
        }
    }

    pub fn read<P: AsRef<Path>>(filepath: P) -> io::Result<Self> {
        let mut data = XDRData::new();
        data.filepath = filepath.as_ref().to_string_lossy().to_string();

        let file = File::open(filepath)?;
        let mut reader = BufReader::new(file);

        data.read_header(&mut reader)?;
        data.read_dataref_definitions(&mut reader)?;
        data.read_frames(&mut reader)?;
        let _ = data.try_read_footer(&mut reader);

        Ok(data)
    }

    fn read_header<R: Read>(&mut self, reader: &mut R) -> io::Result<()> {
        let mut magic = [0u8; 4];
        reader.read_exact(&mut magic)?;

        if &magic != b"XFDR" {
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                format!("Invalid file format. Expected XFDR, got {:?}", magic),
            ));
        }

        let version = reader.read_u16::<LittleEndian>()?;
        let level = reader.read_u8()?;
        let interval = reader.read_f32::<LittleEndian>()?;
        let start_timestamp = reader.read_u64::<LittleEndian>()?;
        let dataref_count = reader.read_u16::<LittleEndian>()?;

        let level_name = match level {
            1 => "Simple",
            2 => "Normal",
            3 => "Detailed",
            _ => "Unknown",
        }
        .to_string();

        let start_datetime = DateTime::from_timestamp(start_timestamp as i64, 0)
            .map(|dt| dt.format("%Y-%m-%dT%H:%M:%S").to_string())
            .unwrap_or_else(|| "Invalid timestamp".to_string());

        self.header = XDRHeader {
            magic: String::from_utf8_lossy(&magic).to_string(),
            version,
            level,
            level_name,
            interval,
            start_timestamp,
            start_datetime,
            dataref_count,
            total_records: None,
            end_timestamp: None,
            end_datetime: None,
            duration: None,
        };

        Ok(())
    }

    fn read_dataref_definitions<R: Read>(&mut self, reader: &mut R) -> io::Result<()> {
        for _ in 0..self.header.dataref_count {
            let name_len = reader.read_u16::<LittleEndian>()?;
            let mut name_bytes = vec![0u8; name_len as usize];
            reader.read_exact(&mut name_bytes)?;
            let name = String::from_utf8_lossy(&name_bytes).to_string();

            let data_type_byte = reader.read_u8()?;
            let array_size = reader.read_u8()?;

            let data_type = match data_type_byte {
                0 => "float",
                1 => "int",
                2 => "string",
                _ => "unknown",
            }
            .to_string();

            self.datarefs.push(DatarefDef {
                name,
                data_type,
                array_size,
            });
        }

        Ok(())
    }

    fn read_frames<R: Read + Seek>(&mut self, reader: &mut R) -> io::Result<()> {
        loop {
            let mut marker = [0u8; 4];
            match reader.read_exact(&mut marker) {
                Ok(_) => {}
                Err(e) if e.kind() == io::ErrorKind::UnexpectedEof => break,
                Err(e) => return Err(e),
            }

            if &marker == b"ENDR" {
                reader.seek(SeekFrom::Current(-4))?;
                break;
            }
            if &marker != b"DATA" {
                reader.seek(SeekFrom::Current(-4))?;
                break;
            }

            let timestamp = reader.read_f32::<LittleEndian>()?;

            match self.read_frame_values(reader) {
                Ok(values) => {
                    self.frames.push(DataFrame { timestamp, values });
                }
                Err(_) => break,
            }
        }

        Ok(())
    }

    fn read_frame_values<R: Read>(&self, reader: &mut R) -> io::Result<Vec<DataValue>> {
        let mut values = Vec::new();

        for dr in &self.datarefs {
            if dr.array_size > 0 {
                match dr.data_type.as_str() {
                    "float" => {
                        let mut arr = Vec::new();
                        for _ in 0..dr.array_size {
                            arr.push(reader.read_f32::<LittleEndian>()?);
                        }
                        values.push(DataValue::FloatArray(arr));
                    }
                    "int" => {
                        let mut arr = Vec::new();
                        for _ in 0..dr.array_size {
                            arr.push(reader.read_i32::<LittleEndian>()?);
                        }
                        values.push(DataValue::IntArray(arr));
                    }
                    _ => {}
                }
            } else {
                match dr.data_type.as_str() {
                    "float" => {
                        values.push(DataValue::Float(reader.read_f32::<LittleEndian>()?));
                    }
                    "int" => {
                        values.push(DataValue::Int(reader.read_i32::<LittleEndian>()?));
                    }
                    "string" => {
                        let str_len = reader.read_u8()?;
                        if str_len > 0 {
                            let mut str_bytes = vec![0u8; str_len as usize];
                            reader.read_exact(&mut str_bytes)?;
                            values.push(DataValue::String(
                                String::from_utf8_lossy(&str_bytes).to_string(),
                            ));
                        } else {
                            values.push(DataValue::String(String::new()));
                        }
                    }
                    _ => {}
                }
            }
        }

        Ok(values)
    }

    fn try_read_footer<R: Read>(&mut self, reader: &mut R) -> io::Result<()> {
        let mut marker = [0u8; 4];
        if reader.read_exact(&mut marker).is_err() {
            return Ok(());
        }

        if &marker == b"ENDR" {
            self.is_complete = true;
            let total_records = reader.read_u32::<LittleEndian>()?;
            let end_timestamp = reader.read_u64::<LittleEndian>()?;

            let end_datetime = DateTime::from_timestamp(end_timestamp as i64, 0)
                .map(|dt| dt.format("%Y-%m-%dT%H:%M:%S").to_string())
                .unwrap_or_else(|| "Invalid timestamp".to_string());

            let duration = end_timestamp - self.header.start_timestamp;

            self.header.total_records = Some(total_records);
            self.header.end_timestamp = Some(end_timestamp);
            self.header.end_datetime = Some(end_datetime);
            self.header.duration = Some(duration);
        }

        Ok(())
    }

    pub fn get_all_plottable_parameters(&self) -> Vec<Parameter> {
        let mut params = Vec::new();

        for (i, dr) in self.datarefs.iter().enumerate() {
            if dr.data_type == "string" {
                continue;
            }

            if dr.array_size > 0 {
                for j in 0..dr.array_size {
                    params.push(Parameter {
                        index: i,
                        array_index: j as usize,
                        name: format!("{}[{}]", dr.name, j),
                        data_type: dr.data_type.clone(),
                    });
                }
            } else {
                params.push(Parameter {
                    index: i,
                    array_index: 0,
                    name: dr.name.clone(),
                    data_type: dr.data_type.clone(),
                });
            }
        }

        params
    }

    pub fn get_parameter_data(
        &self,
        dataref_index: usize,
        array_index: usize,
        time_range: Option<(f32, f32)>,
        downsample_factor: usize,
    ) -> (Vec<f32>, Vec<f64>) {
        let mut timestamps = Vec::new();
        let mut values = Vec::new();

        if dataref_index >= self.datarefs.len() {
            return (timestamps, values);
        }

        for (i, frame) in self.frames.iter().enumerate() {
            if i % downsample_factor != 0 {
                continue;
            }

            let timestamp = frame.timestamp;

            if let Some((min_t, max_t)) = time_range {
                if timestamp < min_t || timestamp > max_t {
                    continue;
                }
            }

            timestamps.push(timestamp);

            if dataref_index < frame.values.len() {
                let value = match &frame.values[dataref_index] {
                    DataValue::Float(v) => *v as f64,
                    DataValue::Int(v) => *v as f64,
                    DataValue::FloatArray(arr) => {
                        if array_index < arr.len() {
                            arr[array_index] as f64
                        } else {
                            0.0
                        }
                    }
                    DataValue::IntArray(arr) => {
                        if array_index < arr.len() {
                            arr[array_index] as f64
                        } else {
                            0.0
                        }
                    }
                    DataValue::String(_) => 0.0,
                };
                values.push(value);
            }
        }

        (timestamps, values)
    }

    pub fn get_parameter_statistics(
        &self,
        dataref_index: usize,
        array_index: usize,
    ) -> Option<Statistics> {
        let (_, values) = self.get_parameter_data(dataref_index, array_index, None, 1);

        if values.is_empty() {
            return None;
        }

        let count = values.len();
        let min = values.iter().cloned().fold(f64::INFINITY, f64::min);
        let max = values.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
        let mean = values.iter().sum::<f64>() / count as f64;

        let mut sorted_values = values.clone();
        sorted_values.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
        let median = if count % 2 == 0 {
            (sorted_values[count / 2 - 1] + sorted_values[count / 2]) / 2.0
        } else {
            sorted_values[count / 2]
        };

        let variance = values.iter().map(|v| (v - mean).powi(2)).sum::<f64>() / count as f64;
        let std = variance.sqrt();

        let param_name = if array_index > 0 {
            format!("{}[{}]", self.datarefs[dataref_index].name, array_index)
        } else {
            self.datarefs[dataref_index].name.clone()
        };

        Some(Statistics {
            name: param_name,
            count,
            min,
            max,
            mean,
            median,
            std,
            range: max - min,
        })
    }

    pub fn calculate_correlation(
        &self,
        param1_index: usize,
        param1_array_idx: usize,
        param2_index: usize,
        param2_array_idx: usize,
    ) -> f64 {
        let (_, values1) = self.get_parameter_data(param1_index, param1_array_idx, None, 1);
        let (_, values2) = self.get_parameter_data(param2_index, param2_array_idx, None, 1);

        if values1.len() != values2.len() || values1.len() < 2 {
            return 0.0;
        }

        let n = values1.len() as f64;
        let mean1 = values1.iter().sum::<f64>() / n;
        let mean2 = values2.iter().sum::<f64>() / n;

        let mut cov = 0.0;
        let mut var1 = 0.0;
        let mut var2 = 0.0;

        for i in 0..values1.len() {
            let diff1 = values1[i] - mean1;
            let diff2 = values2[i] - mean2;
            cov += diff1 * diff2;
            var1 += diff1 * diff1;
            var2 += diff2 * diff2;
        }

        if var1 == 0.0 || var2 == 0.0 {
            return 0.0;
        }

        cov / (var1 * var2).sqrt()
    }

    pub fn get_flight_path(&self) -> Option<(Vec<f64>, Vec<f64>, Vec<f64>, Vec<f32>)> {
        let mut lat_idx = None;
        let mut lon_idx = None;
        let mut alt_idx = None;

        for (i, dr) in self.datarefs.iter().enumerate() {
            let name = dr.name.to_lowercase();
            if name.contains("latitude") {
                lat_idx = Some(i);
            } else if name.contains("longitude") {
                lon_idx = Some(i);
            } else if (name.contains("elevation") || name.contains("altitude"))
                && !name.contains("agl")
            {
                alt_idx = Some(i);
            }
        }

        if lat_idx.is_none() || lon_idx.is_none() || alt_idx.is_none() {
            return None;
        }

        let downsample = (self.frames.len() / 1000).max(1);

        let (times, lats) = self.get_parameter_data(lat_idx.unwrap(), 0, None, downsample);
        let (_, lons) = self.get_parameter_data(lon_idx.unwrap(), 0, None, downsample);
        let (_, alts) = self.get_parameter_data(alt_idx.unwrap(), 0, None, downsample);

        Some((lats, lons, alts, times))
    }
}
