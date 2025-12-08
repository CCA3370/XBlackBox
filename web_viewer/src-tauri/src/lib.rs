mod xdr;
mod logger;
mod security;

use logger::AppLogger;
use security::{validate_file_path, sanitize_error_message};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Mutex;
use tauri::State;

// Global state for XDR data and logger
struct AppState {
    xdr_data: Mutex<Option<xdr::XDRData>>,
    logger: AppLogger,
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
    // Log the file load attempt
    state.logger.log_info(&format!("Attempting to load file: {}", sanitize_error_message(&filepath)));
    
    // Validate and sanitize the file path
    let validated_path = match validate_file_path(&filepath) {
        Ok(path) => path,
        Err(e) => {
            let error_msg = format!("File validation failed: {}", e);
            state.logger.log_error(&error_msg);
            return Ok(LoadFileResponse {
                success: false,
                error: Some(sanitize_error_message(&error_msg)),
                header: None,
                parameters: None,
                frame_count: None,
            });
        }
    };
    
    // Log validated path
    state.logger.log_debug(&format!("Validated path: {}", validated_path.display()));
    
    // Attempt to read the XDR file
    match xdr::XDRData::read(&validated_path) {
        Ok(data) => {
            let header = data.header.clone();
            let parameters = data.get_all_plottable_parameters();
            let frame_count = data.frames.len();

            state.logger.log_info(&format!(
                "Successfully loaded file: {} frames, {} parameters",
                frame_count,
                parameters.len()
            ));

            *state.xdr_data.lock().unwrap() = Some(data);

            Ok(LoadFileResponse {
                success: true,
                error: None,
                header: Some(header),
                parameters: Some(parameters),
                frame_count: Some(frame_count),
            })
        }
        Err(e) => {
            let error_msg = format!("Failed to read XDR file: {}", e);
            state.logger.log_error(&error_msg);
            
            Ok(LoadFileResponse {
                success: false,
                error: Some(sanitize_error_message(&e.to_string())),
                header: None,
                parameters: None,
                frame_count: None,
            })
        }
    }
}

#[tauri::command]
async fn get_data(
    request: GetDataRequest,
    state: State<'_, AppState>,
) -> Result<HashMap<String, ParameterData>, String> {
    state.logger.log_debug(&format!("get_data called with {} parameters", request.parameters.len()));
    
    let data_guard = state.xdr_data.lock().unwrap();
    let data = data_guard
        .as_ref()
        .ok_or_else(|| {
            state.logger.log_warning("get_data called but no file loaded");
            "No file loaded".to_string()
        })?;

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

    state.logger.log_debug(&format!("get_data returning {} parameter datasets", result.len()));
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
    #[serde(skip_serializing_if = "Option::is_none")]
    average_altitude: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    average_speed: Option<f64>,
}

#[derive(Debug, Serialize)]
struct ApproachAnalysis {
    stable_approach: bool,
    average_descent_rate: f64,
    touchdown_speed: f64,
    final_approach_altitude: f64,
}

#[derive(Debug, Serialize)]
struct Anomaly {
    timestamp: f32,
    severity: String, // "low", "medium", "high"
    description: String,
    parameter: String,
    value: f64,
}

#[derive(Debug, Serialize)]
struct FlightAnalysis {
    phases: Vec<FlightPhase>,
    total_flight_time: f32,
    max_altitude: f64,
    max_speed: f64,
    average_fuel_flow: Option<f64>,
    landing_g_force: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    max_climb_rate: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    max_descent_rate: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    approach_analysis: Option<ApproachAnalysis>,
    anomalies: Vec<Anomaly>,
}

// Constants for flight phase detection
const ALTITUDE_THRESHOLD_AGL: f64 = 10.0; // feet AGL threshold for takeoff/landing detection

#[tauri::command]
async fn analyze_flight(state: State<'_, AppState>) -> Result<FlightAnalysis, String> {
    state.logger.log_info("Starting flight analysis");
    
    let data_guard = state.xdr_data.lock().unwrap();
    let data = data_guard
        .as_ref()
        .ok_or_else(|| {
            state.logger.log_warning("analyze_flight called but no file loaded");
            "No file loaded".to_string()
        })?;

    if data.frames.is_empty() {
        state.logger.log_warning("Flight analysis attempted on empty data");
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
    let mut altitudes = Vec::new(); // Store for later use

    // Get altitude and speed data if available
    if let Some(alt_i) = alt_idx {
        let (_, alts) = data.get_parameter_data(alt_i, 0, None, 1);
        altitudes = alts.clone();
        max_altitude = altitudes.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
        
        // Detect flight phases based on altitude
        let mut in_flight = false;
        let mut phase_start_time = 0.0;
        let total_frames = data.frames.len();
        
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

            if !in_flight && alt > ALTITUDE_THRESHOLD_AGL {
                // Takeoff detected
                in_flight = true;
                phase_start_time = frame.timestamp;
                phases.push(FlightPhase {
                    name: "Takeoff".to_string(),
                    start_time: frame.timestamp,
                    end_time: frame.timestamp,
                    duration: 0.0,
                    average_altitude: None,
                    average_speed: None,
                });
            } else if in_flight && alt < ALTITUDE_THRESHOLD_AGL && i > total_frames / 2 {
                // Landing detected - only in second half of flight to avoid false positives during takeoff
                if let Some(last_phase) = phases.last_mut() {
                    last_phase.end_time = frame.timestamp;
                    last_phase.duration = frame.timestamp - last_phase.start_time;
                }
                
                let landing_start = frame.timestamp;
                phases.push(FlightPhase {
                    name: "Landing".to_string(),
                    start_time: landing_start,
                    end_time: landing_start,
                    duration: 0.0,
                    average_altitude: None,
                    average_speed: None,
                });
                
                // Continue to find landing end and calculate duration
                let landing_phase_idx = phases.len() - 1;
                for j in (i + 1)..data.frames.len() {
                    if let Some(next_frame) = data.frames.get(j) {
                        phases[landing_phase_idx].end_time = next_frame.timestamp;
                        phases[landing_phase_idx].duration = next_frame.timestamp - landing_start;
                        
                        // Stop updating once we're clearly on the ground (5+ seconds after touchdown)
                        if next_frame.timestamp - landing_start > 5.0 {
                            break;
                        }
                    }
                }
                
                in_flight = false;
                
                // Record landing G-force if available
                if let Some(g_i) = g_force_idx {
                    if g_i < frame.values.len() {
                        if let xdr::DataValue::Float(v) = &frame.values[g_i] {
                            landing_g = Some(*v as f64);
                        }
                    }
                }
                
                break; // Only detect first landing
            }
        }
    }

    // Calculate max speed
    if let Some(spd_i) = speed_idx {
        let (_, speeds) = data.get_parameter_data(spd_i, 0, None, 1);
        max_speed = speeds.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    }

    // Calculate max climb and descent rates
    let (max_climb_rate, max_descent_rate) = if let Some(vs_i) = vspeed_idx {
        let (_, vspeeds) = data.get_parameter_data(vs_i, 0, None, 1);
        if !vspeeds.is_empty() {
            let max_climb = vspeeds.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
            let max_descent = vspeeds.iter().cloned().fold(f64::INFINITY, f64::min);
            (Some(max_climb), Some(max_descent.abs()))
        } else {
            (None, None)
        }
    } else {
        (None, None)
    };

    // Approach analysis (if landing detected)
    let approach_analysis = if phases.iter().any(|p| p.name == "Landing") && vspeed_idx.is_some() && speed_idx.is_some() {
        let vs_i = vspeed_idx.unwrap();
        let spd_i = speed_idx.unwrap();
        
        // Analyze last 2 minutes before landing
        let landing_time = phases.iter().find(|p| p.name == "Landing").unwrap().start_time;
        let approach_start = (landing_time - 120.0).max(0.0);
        
        let (_, vspeeds) = data.get_parameter_data(vs_i, 0, Some((approach_start, landing_time)), 1);
        let (_, speeds) = data.get_parameter_data(spd_i, 0, Some((approach_start, landing_time)), 1);
        
        if !vspeeds.is_empty() && !speeds.is_empty() {
            let avg_descent = vspeeds.iter().sum::<f64>() / vspeeds.len() as f64;
            let touchdown_spd = speeds.last().copied().unwrap_or(0.0);
            
            // Check for stable approach (descent rate between 300-1000 fpm)
            // Use floating point for accurate percentage calculation
            let stable_count = vspeeds.iter().filter(|&&v| v < -300.0 && v > -1000.0).count();
            let stable = stable_count > (vspeeds.len() as f64 * 0.7) as usize; // 70% of approach should be stable
            
            // Safely calculate final approach altitude
            let final_alt_samples = altitudes.len().min(10);
            let final_approach_altitude = if final_alt_samples > 0 {
                altitudes.iter().rev().take(final_alt_samples).sum::<f64>() / final_alt_samples as f64
            } else {
                0.0
            };
            
            Some(ApproachAnalysis {
                stable_approach: stable,
                average_descent_rate: avg_descent,
                touchdown_speed: touchdown_spd,
                final_approach_altitude,
            })
        } else {
            None
        }
    } else {
        None
    };

    // Anomaly detection
    let mut anomalies = Vec::new();
    
    // Check for excessive descent rates
    if let Some(vs_i) = vspeed_idx {
        let (times, vspeeds) = data.get_parameter_data(vs_i, 0, None, 1);
        for (i, &vspeed) in vspeeds.iter().enumerate() {
            if vspeed < -2000.0 {
                anomalies.push(Anomaly {
                    timestamp: times[i],
                    severity: "high".to_string(),
                    description: "Excessive descent rate".to_string(),
                    parameter: "Vertical Speed".to_string(),
                    value: vspeed,
                });
            }
        }
    }
    
    // Check for excessive G-forces
    if let Some(g_i) = g_force_idx {
        let (times, g_forces) = data.get_parameter_data(g_i, 0, None, 1);
        for (i, &g) in g_forces.iter().enumerate() {
            if g > 2.5 || g < -1.0 {
                let severity = if g > 3.0 || g < -1.5 { "high" } else { "medium" };
                anomalies.push(Anomaly {
                    timestamp: times[i],
                    severity: severity.to_string(),
                    description: "Excessive G-force".to_string(),
                    parameter: "G Load".to_string(),
                    value: g,
                });
            }
        }
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

    state.logger.log_info(&format!(
        "Flight analysis completed: {} phases, {} anomalies detected",
        phases.len(),
        anomalies.len()
    ));

    Ok(FlightAnalysis {
        phases,
        total_flight_time: total_time,
        max_altitude,
        max_speed,
        average_fuel_flow,
        landing_g_force: landing_g,
        max_climb_rate,
        max_descent_rate,
        approach_analysis,
        anomalies,
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

#[tauri::command]
async fn get_log_path(state: State<'_, AppState>) -> Result<String, String> {
    Ok(state.logger.get_log_path())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // Initialize logger - this is critical for debugging and security auditing
    let logger = AppLogger::new().unwrap_or_else(|e| {
        eprintln!("FATAL: Failed to initialize logger: {}", e);
        eprintln!("The application requires write access to the home directory for logging.");
        panic!("Cannot initialize logging system: {}", e);
    });
    
    logger.log_info("Initializing XBlackBox Tauri application");
    
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .manage(AppState {
            xdr_data: Mutex::new(None),
            logger,
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
            get_log_path,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
