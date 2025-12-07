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

#[derive(Debug, Serialize)]
struct FlightPhase {
    name: String,
    start_time: f32,
    end_time: f32,
    duration: f32,
}

#[derive(Debug, Serialize)]
struct FlightAnalysis {
    phases: Vec<FlightPhase>,
    total_flight_time: f32,
    max_altitude: f64,
    max_speed: f64,
    average_fuel_flow: Option<f64>,
    landing_g_force: Option<f64>,
}

#[tauri::command]
async fn analyze_flight(state: State<'_, AppState>) -> Result<FlightAnalysis, String> {
    let data_guard = state.xdr_data.lock().unwrap();
    let data = data_guard
        .as_ref()
        .ok_or_else(|| "No file loaded".to_string())?;

    if data.frames.is_empty() {
        return Err("No flight data available".to_string());
    }

    // Find altitude and speed datarefs
    let mut alt_idx = None;
    let mut speed_idx = None;
    let mut vspeed_idx = None;
    let mut fuel_flow_idx = None;
    let mut g_force_idx = None;

    for (i, dr) in data.datarefs.iter().enumerate() {
        let name = dr.name.to_lowercase();
        if name.contains("altitude") && name.contains("agl") {
            alt_idx = Some(i);
        } else if name.contains("groundspeed") || name.contains("ground_speed") {
            speed_idx = Some(i);
        } else if name.contains("vvi") || name.contains("vertical_speed") {
            vspeed_idx = Some(i);
        } else if name.contains("fuel_flow") {
            fuel_flow_idx = Some(i);
        } else if name.contains("g_nrml") || name.contains("g_load") {
            g_force_idx = Some(i);
        }
    }

    let mut phases = Vec::new();
    let mut max_altitude = 0.0;
    let mut max_speed = 0.0;
    let mut fuel_flow_sum = 0.0;
    let mut fuel_flow_count = 0;
    let mut landing_g = None;

    // Get altitude and speed data if available
    if let Some(alt_i) = alt_idx {
        let (_, altitudes) = data.get_parameter_data(alt_i, 0, None, 1);
        max_altitude = altitudes.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
        
        // Detect flight phases based on altitude
        let mut in_flight = false;
        let mut phase_start = 0.0;
        
        for (i, frame) in data.frames.iter().enumerate() {
            let alt = if alt_i < frame.values.len() {
                match &frame.values[alt_i] {
                    xdr::DataValue::Float(v) => *v as f64,
                    xdr::DataValue::Int(v) => *v as f64,
                    _ => 0.0,
                }
            } else {
                0.0
            };

            if !in_flight && alt > 10.0 {
                // Takeoff detected
                in_flight = true;
                phase_start = frame.timestamp;
                phases.push(FlightPhase {
                    name: "Takeoff".to_string(),
                    start_time: frame.timestamp,
                    end_time: frame.timestamp,
                    duration: 0.0,
                });
            } else if in_flight && alt < 10.0 && i > data.frames.len() / 2 {
                // Landing detected
                if let Some(last_phase) = phases.last_mut() {
                    last_phase.end_time = frame.timestamp;
                    last_phase.duration = frame.timestamp - last_phase.start_time;
                }
                phases.push(FlightPhase {
                    name: "Landing".to_string(),
                    start_time: frame.timestamp,
                    end_time: frame.timestamp,
                    duration: 0.0,
                });
                in_flight = false;
                
                // Record landing G-force if available
                if let Some(g_i) = g_force_idx {
                    if g_i < frame.values.len() {
                        if let xdr::DataValue::Float(v) = &frame.values[g_i] {
                            landing_g = Some(*v as f64);
                        }
                    }
                }
            }
        }
    }

    // Calculate max speed
    if let Some(spd_i) = speed_idx {
        let (_, speeds) = data.get_parameter_data(spd_i, 0, None, 1);
        max_speed = speeds.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    }

    // Calculate average fuel flow
    let average_fuel_flow = if let Some(ff_i) = fuel_flow_idx {
        let (_, fuel_flows) = data.get_parameter_data(ff_i, 0, None, 1);
        if !fuel_flows.is_empty() {
            fuel_flow_sum = fuel_flows.iter().sum();
            fuel_flow_count = fuel_flows.len();
            Some(fuel_flow_sum / fuel_flow_count as f64)
        } else {
            None
        }
    } else {
        None
    };

    let total_time = if !data.frames.is_empty() {
        data.frames.last().unwrap().timestamp - data.frames.first().unwrap().timestamp
    } else {
        0.0
    };

    Ok(FlightAnalysis {
        phases,
        total_flight_time: total_time,
        max_altitude,
        max_speed,
        average_fuel_flow,
        landing_g_force: landing_g,
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
            analyze_flight,
            get_correlation,
            get_flight_path,
            get_table_data,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
