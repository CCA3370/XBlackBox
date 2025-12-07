mod xdr;

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Mutex;
use tauri::State;

// Global state for XDR data
struct AppState {
    xdr_data: Mutex<Option<xdr::XDRData>>,
}

// Request/Response types
#[derive(Debug, Serialize)]
struct LoadFileResponse {
    success: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    error: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    header: Option<xdr::XDRHeader>,
    #[serde(skip_serializing_if = "Option::is_none")]
    parameters: Option<Vec<xdr::Parameter>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    frame_count: Option<usize>,
}

#[derive(Debug, Deserialize)]
struct GetDataRequest {
    parameters: Vec<xdr::Parameter>,
    #[serde(default = "default_downsample")]
    downsample: usize,
    time_range: Option<Vec<f32>>,
}

fn default_downsample() -> usize {
    1
}

#[derive(Debug, Serialize)]
struct ParameterData {
    timestamps: Vec<f32>,
    values: Vec<f64>,
}

#[derive(Debug, Deserialize)]
struct GetStatisticsRequest {
    parameters: Vec<xdr::Parameter>,
}

#[derive(Debug, Deserialize)]
struct GetFftRequest {
    index: usize,
    array_index: usize,
}

#[derive(Debug, Serialize)]
struct FftResponse {
    frequencies: Vec<f64>,
    magnitudes: Vec<f64>,
}

#[derive(Debug, Deserialize)]
struct GetCorrelationRequest {
    parameters: Vec<xdr::Parameter>,
}

#[derive(Debug, Serialize)]
struct CorrelationResponse {
    matrix: Vec<Vec<f64>>,
    names: Vec<String>,
}

#[derive(Debug, Serialize)]
struct FlightPathResponse {
    latitudes: Vec<f64>,
    longitudes: Vec<f64>,
    altitudes: Vec<f64>,
    timestamps: Vec<f32>,
}

#[derive(Debug, Deserialize)]
struct GetTableDataRequest {
    start: usize,
    count: usize,
}

#[derive(Debug, Serialize)]
struct TableRow {
    index: usize,
    timestamp: f32,
    values: Vec<DataValueJson>,
}

#[derive(Debug, Serialize)]
#[serde(untagged)]
enum DataValueJson {
    Float(f32),
    Int(i32),
    String(String),
}

#[derive(Debug, Serialize)]
struct TableDataResponse {
    headers: Vec<String>,
    rows: Vec<TableRow>,
    total: usize,
}

// Tauri Commands
#[tauri::command]
async fn load_file(filepath: String, state: State<'_, AppState>) -> Result<LoadFileResponse, String> {
    match xdr::XDRData::read(&filepath) {
        Ok(data) => {
            let header = data.header.clone();
            let parameters = data.get_all_plottable_parameters();
            let frame_count = data.frames.len();

            *state.xdr_data.lock().unwrap() = Some(data);

            Ok(LoadFileResponse {
                success: true,
                error: None,
                header: Some(header),
                parameters: Some(parameters),
                frame_count: Some(frame_count),
            })
        }
        Err(e) => Ok(LoadFileResponse {
            success: false,
            error: Some(e.to_string()),
            header: None,
            parameters: None,
            frame_count: None,
        }),
    }
}

#[tauri::command]
async fn get_data(
    request: GetDataRequest,
    state: State<'_, AppState>,
) -> Result<HashMap<String, ParameterData>, String> {
    let data_guard = state.xdr_data.lock().unwrap();
    let data = data_guard
        .as_ref()
        .ok_or_else(|| "No file loaded".to_string())?;

    let time_range = request.time_range.as_ref().and_then(|tr| {
        if tr.len() >= 2 {
            Some((tr[0], tr[1]))
        } else {
            None
        }
    });

    let mut result = HashMap::new();

    for param in request.parameters {
        let (timestamps, values) = data.get_parameter_data(
            param.index,
            param.array_index,
            time_range,
            request.downsample,
        );

        result.insert(
            param.name.clone(),
            ParameterData { timestamps, values },
        );
    }

    Ok(result)
}

#[tauri::command]
async fn get_statistics(
    request: GetStatisticsRequest,
    state: State<'_, AppState>,
) -> Result<Vec<xdr::Statistics>, String> {
    let data_guard = state.xdr_data.lock().unwrap();
    let data = data_guard
        .as_ref()
        .ok_or_else(|| "No file loaded".to_string())?;

    let mut result = Vec::new();

    for param in request.parameters {
        if let Some(stats) = data.get_parameter_statistics(param.index, param.array_index) {
            result.push(stats);
        }
    }

    Ok(result)
}

#[tauri::command]
async fn get_fft(
    request: GetFftRequest,
    state: State<'_, AppState>,
) -> Result<FftResponse, String> {
    let data_guard = state.xdr_data.lock().unwrap();
    let data = data_guard
        .as_ref()
        .ok_or_else(|| "No file loaded".to_string())?;

    let (_, values) = data.get_parameter_data(request.index, request.array_index, None, 1);

    if values.len() < 4 {
        return Ok(FftResponse {
            frequencies: vec![],
            magnitudes: vec![],
        });
    }

    // NOTE: FFT implementation not included in initial version
    // To add FFT support, include the rustfft crate and implement:
    // 1. De-mean the data
    // 2. Apply window function (Hanning)
    // 3. Compute FFT
    // 4. Calculate magnitude spectrum
    // For now, return empty arrays to maintain API compatibility
    Ok(FftResponse {
        frequencies: vec![],
        magnitudes: vec![],
    })
}

#[tauri::command]
async fn get_correlation(
    request: GetCorrelationRequest,
    state: State<'_, AppState>,
) -> Result<CorrelationResponse, String> {
    let data_guard = state.xdr_data.lock().unwrap();
    let data = data_guard
        .as_ref()
        .ok_or_else(|| "No file loaded".to_string())?;

    let n = request.parameters.len();
    let mut matrix = vec![vec![0.0; n]; n];
    let names: Vec<String> = request.parameters.iter().map(|p| p.name.clone()).collect();

    for i in 0..n {
        for j in 0..n {
            if i == j {
                matrix[i][j] = 1.0;
            } else {
                let corr = data.calculate_correlation(
                    request.parameters[i].index,
                    request.parameters[i].array_index,
                    request.parameters[j].index,
                    request.parameters[j].array_index,
                );
                matrix[i][j] = corr;
            }
        }
    }

    Ok(CorrelationResponse { matrix, names })
}

#[tauri::command]
async fn get_flight_path(state: State<'_, AppState>) -> Result<FlightPathResponse, String> {
    let data_guard = state.xdr_data.lock().unwrap();
    let data = data_guard
        .as_ref()
        .ok_or_else(|| "No file loaded".to_string())?;

    match data.get_flight_path() {
        Some((lats, lons, alts, times)) => Ok(FlightPathResponse {
            latitudes: lats,
            longitudes: lons,
            altitudes: alts,
            timestamps: times,
        }),
        None => Err("Position data not found".to_string()),
    }
}

#[tauri::command]
async fn get_table_data(
    request: GetTableDataRequest,
    state: State<'_, AppState>,
) -> Result<TableDataResponse, String> {
    let data_guard = state.xdr_data.lock().unwrap();
    let data = data_guard
        .as_ref()
        .ok_or_else(|| "No file loaded".to_string())?;

    let end = (request.start + request.count).min(data.frames.len());
    let mut rows = Vec::new();

    for i in request.start..end {
        let frame = &data.frames[i];
        let mut values = Vec::new();

        for value in &frame.values {
            match value {
                xdr::DataValue::Float(v) => values.push(DataValueJson::Float(*v)),
                xdr::DataValue::Int(v) => values.push(DataValueJson::Int(*v)),
                xdr::DataValue::String(v) => values.push(DataValueJson::String(v.clone())),
                xdr::DataValue::FloatArray(arr) => {
                    for v in arr {
                        values.push(DataValueJson::Float(*v));
                    }
                }
                xdr::DataValue::IntArray(arr) => {
                    for v in arr {
                        values.push(DataValueJson::Int(*v));
                    }
                }
            }
        }

        rows.push(TableRow {
            index: i,
            timestamp: frame.timestamp,
            values,
        });
    }

    // Build headers
    let mut headers = vec!["Index".to_string(), "Timestamp".to_string()];
    for dr in &data.datarefs {
        if dr.array_size > 0 {
            for j in 0..dr.array_size {
                headers.push(format!("{}[{}]", dr.name, j));
            }
        } else {
            headers.push(dr.name.clone());
        }
    }

    Ok(TableDataResponse {
        headers,
        rows,
        total: data.frames.len(),
    })
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .manage(AppState {
            xdr_data: Mutex::new(None),
        })
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            load_file,
            get_data,
            get_statistics,
            get_fft,
            get_correlation,
            get_flight_path,
            get_table_data,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
