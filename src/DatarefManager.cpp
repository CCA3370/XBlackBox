#include "DatarefManager.h"
#include <cmath>

DatarefManager& DatarefManager::Instance() {
    static DatarefManager instance;
    return instance;
}

DatarefManager::DatarefManager() {
}

void DatarefManager::Init() {
    LogInfo("Initializing DatarefManager...");
    LoadDatarefs();
}

void DatarefManager::Reload() {
    LogInfo("Reloading datarefs...");
    m_datarefs.clear();
    m_datarefIndex.clear();
    LoadDatarefs();
}

void DatarefManager::LoadDatarefs() {
    RecordingLevel level = Settings::Instance().GetRecordingLevel();
    
    // Recording levels are cumulative:
    // Level 1: Basic only
    // Level 2: Basic + Normal
    // Level 3: Basic + Normal + Detailed
    
    // Reserve space for datarefs to avoid reallocations
    // Estimated counts: Level 1 ~26, Level 2 ~163, Level 3 ~363
    size_t estimatedCount = (level == RecordingLevel::Simple) ? 30 : 
                           (level == RecordingLevel::Normal) ? 170 : 370;
    m_datarefs.reserve(estimatedCount);
    
    // Always load basic (Level 1)
    LoadBasicDatarefs();
    
    // Load normal if level >= 2 (Levels 2 and 3)
    if (level >= RecordingLevel::Normal) {
        LoadNormalDatarefs();
    }
    
    // Load detailed if level >= 3 (Level 3 only)
    if (level >= RecordingLevel::Detailed) {
        LoadDetailedDatarefs();
    }
    
    // Pre-allocate storage for values to avoid reallocations during runtime
    size_t floatCount = 0;
    size_t intCount = 0;
    size_t stringCount = 0;
    
    for (const auto& dr : m_datarefs) {
        size_t count = (dr.arraySize > 0) ? dr.arraySize : 1;
        if (dr.type == DatarefType::Float) {
            floatCount += count;
        } else if (dr.type == DatarefType::Int) {
            intCount += count;
        } else if (dr.type == DatarefType::String) {
            stringCount += count;
        }
    }
    
    m_floatValues.reserve(floatCount);
    m_intValues.reserve(intCount);
    m_stringValues.reserve(stringCount);
    
    LogInfo("Loaded " + std::to_string(m_datarefs.size()) + " datarefs for level " + 
            Settings::Instance().GetRecordingLevelName() + 
            " (" + std::to_string(floatCount) + " floats, " + 
            std::to_string(intCount) + " ints, " + 
            std::to_string(stringCount) + " strings)");
}

void DatarefManager::AddDataref(const std::string& name, const std::string& desc, 
                                 DatarefType type, int arraySize) {
    XPLMDataRef ref = XPLMFindDataRef(name.c_str());
    if (ref == nullptr) {
        // Dataref not available - this is normal for some aircraft
        return;
    }
    
    DatarefDef def(name, desc, type, arraySize);
    def.ref = ref;
    
    m_datarefIndex[name] = m_datarefs.size();
    m_datarefs.push_back(def);
}

void DatarefManager::LoadBasicDatarefs() {
    // LEVEL 1: BASIC FLIGHT DATA
    
    // Time
    AddDataref("sim/time/total_running_time_sec", "Total running time", DatarefType::Float);
    AddDataref("sim/time/zulu_time_sec", "Zulu time", DatarefType::Float);
    AddDataref("sim/time/local_date_days", "Local date days", DatarefType::Int);
    
    // Aircraft info
    AddDataref("sim/aircraft/view/acf_descrip", "Aircraft description", DatarefType::String);
    AddDataref("sim/aircraft/view/acf_ICAO", "Aircraft ICAO code", DatarefType::String);
    
    // Position
    AddDataref("sim/flightmodel/position/latitude", "Latitude", DatarefType::Float);
    AddDataref("sim/flightmodel/position/longitude", "Longitude", DatarefType::Float);
    AddDataref("sim/flightmodel/position/elevation", "Elevation MSL", DatarefType::Float);
    AddDataref("sim/flightmodel/position/y_agl", "Height AGL", DatarefType::Float);
    
    // Attitude
    AddDataref("sim/flightmodel/position/theta", "Pitch", DatarefType::Float);
    AddDataref("sim/flightmodel/position/phi", "Roll", DatarefType::Float);
    AddDataref("sim/flightmodel/position/psi", "Heading true", DatarefType::Float);
    AddDataref("sim/flightmodel/position/mag_psi", "Heading magnetic", DatarefType::Float);
    AddDataref("sim/flightmodel/position/hpath", "Ground track", DatarefType::Float);
    AddDataref("sim/flightmodel/position/beta", "Sideslip angle", DatarefType::Float);
    AddDataref("sim/flightmodel/position/alpha", "Angle of attack", DatarefType::Float);
    
    // Velocities
    AddDataref("sim/flightmodel/position/indicated_airspeed", "IAS", DatarefType::Float);
    AddDataref("sim/flightmodel/position/true_airspeed", "TAS", DatarefType::Float);
    AddDataref("sim/flightmodel/position/groundspeed", "Ground speed", DatarefType::Float);
    AddDataref("sim/flightmodel/position/vh_ind_fpm", "Vertical speed fpm", DatarefType::Float);
    
    // Angular velocities
    AddDataref("sim/flightmodel/position/P", "Roll rate", DatarefType::Float);
    AddDataref("sim/flightmodel/position/Q", "Pitch rate", DatarefType::Float);
    AddDataref("sim/flightmodel/position/R", "Yaw rate", DatarefType::Float);
    
    // G-forces
    AddDataref("sim/flightmodel/forces/g_nrml", "G-force normal", DatarefType::Float);
    AddDataref("sim/flightmodel/forces/g_axil", "G-force axial", DatarefType::Float);
    AddDataref("sim/flightmodel/forces/g_side", "G-force side", DatarefType::Float);
}

void DatarefManager::LoadNormalDatarefs() {
    // LEVEL 2: NORMAL (+ controls and systems)
    
    // Flight controls
    AddDataref("sim/joystick/yoke_pitch_ratio", "Yoke pitch", DatarefType::Float);
    AddDataref("sim/joystick/yoke_roll_ratio", "Yoke roll", DatarefType::Float);
    AddDataref("sim/joystick/yoke_heading_ratio", "Rudder pedals", DatarefType::Float);
    AddDataref("sim/flightmodel/controls/parkbrake", "Parking brake", DatarefType::Float);
    AddDataref("sim/flightmodel/controls/ldgbrk", "Landing brake", DatarefType::Float);
    
    // Control surfaces
    AddDataref("sim/flightmodel/controls/wing1l_ail1def", "Left aileron", DatarefType::Float);
    AddDataref("sim/flightmodel/controls/wing1r_ail1def", "Right aileron", DatarefType::Float);
    AddDataref("sim/flightmodel/controls/hstab1_elv1def", "Elevator", DatarefType::Float);
    AddDataref("sim/flightmodel/controls/vstab1_rud1def", "Rudder", DatarefType::Float);
    AddDataref("sim/flightmodel/controls/flaprqst", "Flap request", DatarefType::Float);
    AddDataref("sim/flightmodel/controls/flaprat", "Flap actual", DatarefType::Float);
    AddDataref("sim/flightmodel/controls/sbrkrqst", "Speedbrake request", DatarefType::Float);
    AddDataref("sim/flightmodel/controls/sbrkrat", "Speedbrake actual", DatarefType::Float);
    
    // Landing gear
    AddDataref("sim/flightmodel/controls/gear_request", "Gear request", DatarefType::Float);
    AddDataref("sim/flightmodel/movingparts/gear1def", "Gear 1 deploy", DatarefType::Float);
    AddDataref("sim/flightmodel/movingparts/gear2def", "Gear 2 deploy", DatarefType::Float);
    AddDataref("sim/flightmodel/movingparts/gear3def", "Gear 3 deploy", DatarefType::Float);
    AddDataref("sim/flightmodel2/gear/tire_rotation_speed_rad_sec", "Tire rotation speed", DatarefType::Float, MAX_LANDING_GEAR);
    
    // Throttle
    AddDataref("sim/flightmodel/engine/ENGN_thro", "Throttle", DatarefType::Float, MAX_ENGINES);
    AddDataref("sim/flightmodel/engine/ENGN_thro_use", "Throttle actual", DatarefType::Float, MAX_ENGINES);
    AddDataref("sim/flightmodel/engine/ENGN_mixt", "Mixture", DatarefType::Float, MAX_ENGINES);
    AddDataref("sim/flightmodel/engine/ENGN_prop", "Prop pitch", DatarefType::Float, MAX_ENGINES);
    
    // Engine basic
    AddDataref("sim/flightmodel/engine/ENGN_running", "Engine running", DatarefType::Int, MAX_ENGINES);
    AddDataref("sim/flightmodel/engine/ENGN_N1_", "N1", DatarefType::Float, MAX_ENGINES);
    AddDataref("sim/flightmodel/engine/ENGN_N2_", "N2", DatarefType::Float, MAX_ENGINES);
    AddDataref("sim/flightmodel/engine/ENGN_FF_", "Fuel flow", DatarefType::Float, MAX_ENGINES);
    AddDataref("sim/flightmodel/engine/ENGN_EGT", "EGT", DatarefType::Float, MAX_ENGINES);
    AddDataref("sim/flightmodel/engine/ENGN_ITT", "ITT", DatarefType::Float, MAX_ENGINES);
    AddDataref("sim/flightmodel/engine/ENGN_CHT", "CHT", DatarefType::Float, MAX_ENGINES);
    AddDataref("sim/flightmodel/engine/ENGN_TRQ", "Torque", DatarefType::Float, MAX_ENGINES);
    
    // Weight and fuel
    AddDataref("sim/flightmodel/weight/m_total", "Total weight", DatarefType::Float);
    AddDataref("sim/flightmodel/weight/m_fuel_total", "Total fuel weight", DatarefType::Float);
    AddDataref("sim/aircraft/weight/acf_m_fuel_tot", "Fuel quantity total", DatarefType::Float);
    
    // On ground
    AddDataref("sim/flightmodel/failures/onground_any", "On ground", DatarefType::Int);
    AddDataref("sim/flightmodel2/gear/on_ground", "Gear on ground", DatarefType::Int, MAX_LANDING_GEAR);
}

void DatarefManager::LoadDetailedDatarefs() {
    // LEVEL 3: DETAILED (everything)
    
    // Autopilot
    AddDataref("sim/cockpit/autopilot/autopilot_state", "Autopilot state", DatarefType::Int);
    AddDataref("sim/cockpit/autopilot/autopilot_mode", "Autopilot mode", DatarefType::Int);
    AddDataref("sim/cockpit/autopilot/altitude", "AP altitude target", DatarefType::Float);
    AddDataref("sim/cockpit/autopilot/heading", "AP heading target", DatarefType::Float);
    AddDataref("sim/cockpit/autopilot/airspeed", "AP airspeed target", DatarefType::Float);
    AddDataref("sim/cockpit/autopilot/vertical_velocity", "AP VS target", DatarefType::Float);
    
    // Navigation
    AddDataref("sim/cockpit/radios/nav1_freq_hz", "NAV1 frequency", DatarefType::Int);
    AddDataref("sim/cockpit/radios/nav2_freq_hz", "NAV2 frequency", DatarefType::Int);
    AddDataref("sim/cockpit/radios/com1_freq_hz", "COM1 frequency", DatarefType::Int);
    AddDataref("sim/cockpit/radios/com2_freq_hz", "COM2 frequency", DatarefType::Int);
    AddDataref("sim/cockpit/radios/nav1_dme_dist_m", "NAV1 DME distance", DatarefType::Float);
    AddDataref("sim/cockpit/radios/gps_dme_dist_m", "GPS distance", DatarefType::Float);
    
    // Pressurization and environment
    AddDataref("sim/cockpit2/pressurization/indicators/cabin_altitude_ft", "Cabin altitude", DatarefType::Float);
    AddDataref("sim/cockpit2/pressurization/indicators/cabin_vvi_fpm", "Cabin VS", DatarefType::Float);
    AddDataref("sim/cockpit2/temperature/outside_air_temp_degc", "OAT", DatarefType::Float);
    AddDataref("sim/weather/wind_speed_kt", "Wind speed", DatarefType::Float, 3);
    AddDataref("sim/weather/wind_direction_degt", "Wind direction", DatarefType::Float, 3);
    AddDataref("sim/weather/barometer_sealevel_inhg", "Barometer sea level", DatarefType::Float);
    
    // Electrical
    AddDataref("sim/cockpit2/electrical/battery_voltage_actual_volts", "Battery voltage", DatarefType::Float, MAX_BATTERIES);
    AddDataref("sim/cockpit2/electrical/battery_amps", "Battery amps", DatarefType::Float, MAX_BATTERIES);
    AddDataref("sim/cockpit2/electrical/generator_on", "Generator on", DatarefType::Int, MAX_GENERATORS);
    
    // Hydraulics
    AddDataref("sim/cockpit2/hydraulics/indicators/hydraulic_press_1", "Hydraulic pressure 1", DatarefType::Float);
    AddDataref("sim/cockpit2/hydraulics/indicators/hydraulic_press_2", "Hydraulic pressure 2", DatarefType::Float);
    
    // Additional engine data
    AddDataref("sim/flightmodel/engine/ENGN_MPR", "Manifold pressure", DatarefType::Float, MAX_ENGINES);
    AddDataref("sim/flightmodel/engine/ENGN_oil_press", "Oil pressure", DatarefType::Float, MAX_ENGINES);
    AddDataref("sim/flightmodel/engine/ENGN_oil_temp", "Oil temperature", DatarefType::Float, MAX_ENGINES);
    AddDataref("sim/flightmodel/engine/ENGN_cowl", "Cowl flaps", DatarefType::Float, MAX_ENGINES);
    
    // Flight director
    AddDataref("sim/cockpit/autopilot/flight_director_mode", "FD mode", DatarefType::Int);
    AddDataref("sim/cockpit/autopilot/flight_director_pitch", "FD pitch", DatarefType::Float);
    AddDataref("sim/cockpit/autopilot/flight_director_roll", "FD roll", DatarefType::Float);
    
    // Warnings and cautions
    AddDataref("sim/cockpit2/annunciators/master_warning", "Master warning", DatarefType::Int);
    AddDataref("sim/cockpit2/annunciators/master_caution", "Master caution", DatarefType::Int);
    AddDataref("sim/cockpit2/annunciators/stall_warning", "Stall warning", DatarefType::Int);
    AddDataref("sim/cockpit2/annunciators/low_vacuum", "Low vacuum", DatarefType::Int);
    AddDataref("sim/cockpit2/annunciators/low_voltage", "Low voltage", DatarefType::Int);
    AddDataref("sim/cockpit2/annunciators/fuel_quantity", "Fuel quantity warning", DatarefType::Int);
    
    // Ice and anti-ice
    AddDataref("sim/cockpit2/ice/ice_frame_anti_ice_on", "Frame anti-ice", DatarefType::Int);
    AddDataref("sim/cockpit2/ice/ice_inlet_heat_on", "Inlet heat", DatarefType::Int, MAX_ENGINES);
    AddDataref("sim/cockpit2/ice/ice_pitot_heat_on", "Pitot heat", DatarefType::Int, 2);
    AddDataref("sim/flightmodel/failures/rel_ice_frame", "Frame ice", DatarefType::Float);
    AddDataref("sim/flightmodel/failures/rel_ice_inlet", "Inlet ice", DatarefType::Float, MAX_ENGINES);
    AddDataref("sim/flightmodel/failures/rel_ice_pitot", "Pitot ice", DatarefType::Float, 2);
    
    // Additional forces
    AddDataref("sim/flightmodel/forces/fside_aero", "Side force", DatarefType::Float);
    AddDataref("sim/flightmodel/forces/fnrml_aero", "Normal force", DatarefType::Float);
    AddDataref("sim/flightmodel/forces/faxil_aero", "Axial force", DatarefType::Float);
    AddDataref("sim/flightmodel/forces/L_total", "Roll moment", DatarefType::Float);
    AddDataref("sim/flightmodel/forces/M_total", "Pitch moment", DatarefType::Float);
    AddDataref("sim/flightmodel/forces/N_total", "Yaw moment", DatarefType::Float);
    
    // Cockpit switches and lights
    AddDataref("sim/cockpit2/switches/battery_on", "Battery switches", DatarefType::Int, MAX_BATTERIES);
    AddDataref("sim/cockpit2/switches/avionics_power_on", "Avionics master switch", DatarefType::Int);
    AddDataref("sim/cockpit2/switches/landing_lights_on", "Landing lights switch", DatarefType::Int);
    AddDataref("sim/cockpit2/switches/beacon_on", "Beacon light switch", DatarefType::Int);
    AddDataref("sim/cockpit2/switches/strobe_lights_on", "Strobe lights switch", DatarefType::Int);
    AddDataref("sim/cockpit2/switches/navigation_lights_on", "Nav lights switch", DatarefType::Int);
    AddDataref("sim/cockpit2/switches/taxi_light_on", "Taxi light switch", DatarefType::Int);
    
    // TCAS and traffic
    AddDataref("sim/cockpit2/tcas/indicators/tcas_num_acf", "Number of TCAS targets", DatarefType::Int);
    
    // Enhanced autopilot status
    AddDataref("sim/cockpit2/autopilot/fms_vnav", "FMS VNAV mode", DatarefType::Int);
    AddDataref("sim/cockpit2/autopilot/approach_status", "Approach status: 0=off 1=armed 2=captured", DatarefType::Int);
    AddDataref("sim/cockpit2/autopilot/nav_status", "Nav status: 0=off 1=armed 2=captured", DatarefType::Int);
    
    // System failures monitoring
    AddDataref("sim/operation/failures/rel_servo_ailn", "Autopilot servo failed - ailerons", DatarefType::Int);
    AddDataref("sim/operation/failures/rel_servo_elev", "Autopilot servo failed - elevators", DatarefType::Int);
    AddDataref("sim/operation/failures/rel_servo_rudd", "Autopilot servo failed - rudder", DatarefType::Int);
    AddDataref("sim/operation/failures/rel_ss_dgy", "Directional gyro failure", DatarefType::Int);
    AddDataref("sim/operation/failures/rel_ss_ahz", "Artificial horizon failure", DatarefType::Int);
    AddDataref("sim/operation/failures/rel_ss_asi", "Airspeed indicator failure", DatarefType::Int);
    AddDataref("sim/operation/failures/rel_ss_alt", "Altimeter failure", DatarefType::Int);
    
    // Engine extended parameters
    AddDataref("sim/flightmodel2/engines/thrust_reverser_deploy_ratio", "Thrust reverser position", DatarefType::Float, MAX_ENGINES);
    AddDataref("sim/flightmodel2/engines/engine_is_burning_fuel", "Engine burning fuel status", DatarefType::Int, MAX_ENGINES);
    
    // Control trim settings
    AddDataref("sim/cockpit2/controls/elevator_trim", "Elevator trim", DatarefType::Float);
    AddDataref("sim/cockpit2/controls/aileron_trim", "Aileron trim", DatarefType::Float);
    AddDataref("sim/cockpit2/controls/rudder_trim", "Rudder trim", DatarefType::Float);
    
    // GPS navigation indicators
    AddDataref("sim/cockpit2/radios/indicators/gps_dme_distance_nm", "GPS DME distance", DatarefType::Float);
    AddDataref("sim/cockpit2/radios/indicators/gps_hdef_dots_pilot", "GPS HDEF dots pilot", DatarefType::Float);
    AddDataref("sim/cockpit2/radios/actuators/gps_course_degtm", "GPS course", DatarefType::Float);
    AddDataref("sim/cockpit2/radios/indicators/gps_vdef_dots_pilot", "GPS VDEF dots pilot", DatarefType::Float);
    
    // Weight and CG information
    AddDataref("sim/flightmodel/weight/m_fixed", "Payload weight", DatarefType::Float);
    AddDataref("sim/flightmodel/weight/m_jettison", "Jettisoned weight", DatarefType::Float);
    AddDataref("sim/flightmodel/misc/cgz_ref_to_default", "CG position longitudinal", DatarefType::Float);
    
    // Performance metrics
    AddDataref("sim/flightmodel/position/local_vx", "Local velocity X", DatarefType::Float);
    AddDataref("sim/flightmodel/position/local_vy", "Local velocity Y", DatarefType::Float);
    AddDataref("sim/flightmodel/position/local_vz", "Local velocity Z", DatarefType::Float);
    AddDataref("sim/flightmodel2/position/mag_psi", "Magnetic heading", DatarefType::Float);
    
    // Replay mode detection
    AddDataref("sim/time/is_in_replay", "In replay mode", DatarefType::Int);
    
    // Weather information
    AddDataref("sim/weather/visibility_reported_m", "Visibility in meters", DatarefType::Float);
    AddDataref("sim/weather/cloud_base_msl_m", "Cloud base MSL", DatarefType::Float, 3);
    AddDataref("sim/weather/cloud_coverage", "Cloud coverage", DatarefType::Float, 3);
    AddDataref("sim/weather/cloud_type", "Cloud type", DatarefType::Int, 3);
    AddDataref("sim/weather/temperature_sealevel_c", "Temperature at sea level", DatarefType::Float);
    AddDataref("sim/weather/temperature_ambient_c", "Ambient temperature", DatarefType::Float);
    
    // Pressurization controls
    AddDataref("sim/cockpit2/pressurization/actuators/safety_valve", "Safety valve position", DatarefType::Float);
    AddDataref("sim/cockpit2/pressurization/actuators/dump_all", "Dump all valve", DatarefType::Float);
    
    // Additional engine parameters
    AddDataref("sim/flightmodel2/engines/fuel_flow_kg_sec", "Fuel flow kg/sec", DatarefType::Float, MAX_ENGINES);
    AddDataref("sim/flightmodel2/engines/nacelle_temp_c", "Nacelle temperature", DatarefType::Float, MAX_ENGINES);
}

void DatarefManager::ReadCurrentValues() {
    m_floatValues.clear();
    m_intValues.clear();
    m_stringValues.clear();
    
    for (const auto& dr : m_datarefs) {
        // Check if dataref reference is valid
        if (!dr.ref) {
            // Handle missing dataref gracefully
            if (dr.type == DatarefType::Float) {
                for (int i = 0; i < (dr.arraySize > 0 ? dr.arraySize : 1); i++) {
                    m_floatValues.push_back(0.0f);
                }
            } else if (dr.type == DatarefType::Int) {
                for (int i = 0; i < (dr.arraySize > 0 ? dr.arraySize : 1); i++) {
                    m_intValues.push_back(0);
                }
            } else if (dr.type == DatarefType::String) {
                m_stringValues.push_back("");
            }
            continue;
        }
        
        if (dr.arraySize > 0) {
            // Handle array datarefs with bounds checking
            for (int i = 0; i < dr.arraySize; i++) {
                if (dr.type == DatarefType::Float) {
                    float values[256] = {0};
                    int count = XPLMGetDatavf(dr.ref, values, i, 1);
                    m_floatValues.push_back(count > 0 ? values[0] : 0.0f);
                } else if (dr.type == DatarefType::Int) {
                    int values[256] = {0};
                    int count = XPLMGetDatavi(dr.ref, values, i, 1);
                    m_intValues.push_back(count > 0 ? values[0] : 0);
                }
            }
        } else {
            // Handle single value datarefs with error checking
            if (dr.type == DatarefType::Float) {
                float value = XPLMGetDataf(dr.ref);
                // Check for invalid float values (NaN, infinity)
                if (std::isnan(value) || std::isinf(value)) {
                    value = 0.0f;
                }
                m_floatValues.push_back(value);
            } else if (dr.type == DatarefType::Int) {
                int value = XPLMGetDatai(dr.ref);
                m_intValues.push_back(value);
            } else if (dr.type == DatarefType::String) {
                char buffer[512] = {0};
                int len = XPLMGetDatab(dr.ref, buffer, 0, sizeof(buffer) - 1);
                // Ensure len is valid and doesn't exceed buffer size
                if (len > 0 && len <= static_cast<int>(sizeof(buffer) - 1)) {
                    buffer[len] = '\0';
                    m_stringValues.push_back(std::string(buffer));
                } else {
                    m_stringValues.push_back("");
                }
            }
        }
    }
}
