#include "Recorder.h"
#include <ctime>
#include <iomanip>
#include <sstream>
#include <cstring>
#include <cmath>
#include "XPLMNavigation.h"

// Constants for distance calculation
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
#define EARTH_RADIUS_NM 3443.92  // Earth radius in nautical miles (standard value)

Recorder& Recorder::Instance() {
    static Recorder instance;
    return instance;
}

Recorder::Recorder() 
    : m_isRecording(false)
    , m_recordingStartTime(0)
    , m_lastRecordTime(0.0f)
    , m_lastUpdateTime(0.0f)
    , m_autoStopTimer(0.0f)
    , m_recordCount(0)
    , m_bytesWritten(0)
    , m_averageRecordTime(0.0)
    , m_maxRecordTime(0.0)
    , m_totalRecordTime(0.0)
    , m_perfSampleCount(0) {
    m_writeBuffer.reserve(BUFFER_SIZE);
}

Recorder::~Recorder() {
    if (m_isRecording) {
        Stop();
    }
}

void Recorder::Init() {
    LogInfo("Recorder initialized");
}

bool Recorder::Start() {
    if (m_isRecording) {
        LogInfo("Already recording");
        return false;
    }
    
    // Create filename with timestamp
    std::time_t now = std::time(nullptr);
    std::tm* tm = std::localtime(&now);
    if (!tm) {
        LogError("Failed to get local time");
        return false;
    }
    
    std::ostringstream filename;
    filename << Settings::Instance().GetFilePrefix()
             << std::put_time(tm, "%Y%m%d_%H%M%S")
             << ".xdr";
    
    m_currentFilePath = Settings::Instance().GetOutputDirectory() + filename.str();
    
    // Open file in binary mode
    m_currentFile = std::make_unique<std::ofstream>(m_currentFilePath, 
                                                     std::ios::binary | std::ios::out);
    if (!m_currentFile || !m_currentFile->is_open()) {
        LogError("Could not create recording file: " + m_currentFilePath);
        m_currentFile.reset();
        return false;
    }
    
    // Verify file is writable
    if (!m_currentFile->good()) {
        LogError("File stream is not in good state: " + m_currentFilePath);
        m_currentFile->close();
        m_currentFile.reset();
        return false;
    }
    
    // Detect departure airport
    XPLMDataRef latRef = XPLMFindDataRef("sim/flightmodel/position/latitude");
    XPLMDataRef lonRef = XPLMFindDataRef("sim/flightmodel/position/longitude");
    if (latRef && lonRef) {
        float lat = XPLMGetDataf(latRef);
        float lon = XPLMGetDataf(lonRef);
        m_departureAirport = DetectNearestAirport(lat, lon);
        if (m_departureAirport.valid) {
            LogInfo("Departure airport detected: " + std::string(m_departureAirport.icao) + 
                    " - " + std::string(m_departureAirport.name));
        } else {
            LogInfo("No departure airport detected (not near any airport)");
        }
    }
    
    // Write header with error checking
    try {
        WriteHeader();
    } catch (const std::exception& e) {
        LogError(std::string("Exception writing header: ") + e.what());
        m_currentFile->close();
        m_currentFile.reset();
        return false;
    }
    
    // Verify header was written successfully
    if (!m_currentFile->good()) {
        LogError("File write failed during header write");
        m_currentFile->close();
        m_currentFile.reset();
        return false;
    }
    
    // Set state
    m_isRecording = true;
    m_recordingStartTime = now;
    m_lastRecordTime = 0.0f;
    m_recordCount = 0;
    m_bytesWritten = 0;
    m_autoStopTimer = 0.0f;
    m_writeBuffer.clear();
    
    // Reset performance tracking
    m_averageRecordTime = 0.0;
    m_maxRecordTime = 0.0;
    m_totalRecordTime = 0.0;
    m_perfSampleCount = 0;
    
    LogInfo("Recording started: " + filename.str());
    return true;
}

bool Recorder::Stop() {
    if (!m_isRecording) {
        return false;
    }
    
    // Detect arrival airport
    XPLMDataRef latRef = XPLMFindDataRef("sim/flightmodel/position/latitude");
    XPLMDataRef lonRef = XPLMFindDataRef("sim/flightmodel/position/longitude");
    if (latRef && lonRef) {
        float lat = XPLMGetDataf(latRef);
        float lon = XPLMGetDataf(lonRef);
        m_arrivalAirport = DetectNearestAirport(lat, lon);
        if (m_arrivalAirport.valid) {
            LogInfo("Arrival airport detected: " + std::string(m_arrivalAirport.icao) + 
                    " - " + std::string(m_arrivalAirport.name));
        } else {
            LogInfo("No arrival airport detected (not near any airport)");
        }
    }
    
    // Flush any remaining buffered data
    try {
        FlushBuffer();
    } catch (const std::exception& e) {
        LogError(std::string("Exception flushing buffer: ") + e.what());
    }
    
    // Update header with arrival airport information
    if (m_arrivalAirport.valid) {
        try {
            UpdateHeaderWithArrival();
        } catch (const std::exception& e) {
            LogError(std::string("Exception updating header with arrival: ") + e.what());
        }
    }
    
    // Write footer with error checking
    try {
        WriteFooter();
    } catch (const std::exception& e) {
        LogError(std::string("Exception writing footer: ") + e.what());
    }
    
    // Close file safely
    if (m_currentFile) {
        try {
            if (m_currentFile->is_open()) {
                m_currentFile->close();
            }
        } catch (const std::exception& e) {
            LogError(std::string("Exception closing file: ") + e.what());
        }
        m_currentFile.reset();
    }
    
    m_isRecording = false;
    
    int duration = static_cast<int>(std::time(nullptr) - m_recordingStartTime);
    
    // Log performance statistics if we recorded anything
    if (m_perfSampleCount > 0) {
        LogInfo("Performance stats - Avg record time: " + 
                std::to_string(m_averageRecordTime * 1000.0) + " ms, Max: " + 
                std::to_string(m_maxRecordTime * 1000.0) + " ms");
    }
    
    LogInfo("Recording stopped - " + std::to_string(m_recordCount) + " records, " +
            std::to_string(m_bytesWritten) + " bytes, " + std::to_string(duration) + " seconds");
    
    return true;
}

void Recorder::Update(float deltaTime) {
    // Early exit if not recording and auto mode is off - saves CPU cycles
    if (!m_isRecording && !Settings::Instance().GetAutoMode()) {
        return;
    }
    
    // Cache time dataref for efficiency (avoid repeated lookups)
    static XPLMDataRef timeRef = XPLMFindDataRef("sim/time/total_running_time_sec");
    if (!timeRef) {
        // Critical dataref missing - should not happen, but handle gracefully
        LogError("Critical dataref 'sim/time/total_running_time_sec' not found");
        return;
    }
    
    float currentTime = XPLMGetDataf(timeRef);
    
    // Update last update time
    m_lastUpdateTime = currentTime;
    
    // Check auto mode
    if (Settings::Instance().GetAutoMode() && !m_isRecording) {
        if (CheckAutoStartCondition()) {
            Start();
        }
        // Exit early if Start() failed (still not recording)
        if (!m_isRecording) {
            return;
        }
    }
    
    // Check auto stop
    if (Settings::Instance().GetAutoMode() && m_isRecording) {
        if (CheckAutoStopCondition()) {
            m_autoStopTimer += deltaTime;
            if (m_autoStopTimer >= Settings::Instance().GetAutoStopDelay()) {
                Stop();
                return;  // Exit after stopping
            }
        } else {
            m_autoStopTimer = 0.0f;
        }
    }
    
    // Record data if recording and interval has passed
    if (m_isRecording) {
        float interval = Settings::Instance().GetRecordingInterval();
        if (currentTime - m_lastRecordTime >= interval) {
            RecordFrame();
            m_lastRecordTime = currentTime;
        }
    }
}

int Recorder::GetDuration() const {
    if (m_isRecording) {
        return static_cast<int>(std::time(nullptr) - m_recordingStartTime);
    }
    return 0;
}

void Recorder::WriteHeader() {
    if (!m_currentFile) {
        LogError("WriteHeader called with null file");
        return;
    }
    
    if (!m_currentFile->good()) {
        LogError("File stream not in good state in WriteHeader");
        return;
    }
    
    // Magic number "XFDR" (note: keeping XFDR for compatibility, file extension is .xdr)
    m_currentFile->write("XFDR", 4);
    if (!m_currentFile->good()) {
        LogError("Failed to write magic number");
        return;
    }
    m_bytesWritten += 4;
    
    // Version (2 bytes) - updating to version 2 for airport info
    WriteUInt16(2);
    
    // Recording level (1 byte)
    WriteUInt8(static_cast<uint8_t>(Settings::Instance().GetRecordingLevel()));
    
    // Recording interval (4 bytes float)
    WriteFloat(Settings::Instance().GetRecordingInterval());
    
    // Start timestamp (8 bytes)
    WriteUInt64(static_cast<uint64_t>(m_recordingStartTime));
    
    // Airport information (new in version 2)
    // Departure airport ICAO (8 bytes, null-padded)
    m_currentFile->write(m_departureAirport.icao, 8);
    m_bytesWritten += 8;
    
    // Departure airport coordinates (8 bytes: 2 floats)
    WriteFloat(m_departureAirport.lat);
    WriteFloat(m_departureAirport.lon);
    
    // Departure airport name (256 bytes, null-padded)
    m_currentFile->write(m_departureAirport.name, 256);
    m_bytesWritten += 256;
    
    // Arrival airport fields are written as empty initially
    // They will be filled when updating header at Stop()
    char empty_icao[8] = {0};
    m_currentFile->write(empty_icao, 8);
    m_bytesWritten += 8;
    
    WriteFloat(0.0f);  // Arrival lat (placeholder)
    WriteFloat(0.0f);  // Arrival lon (placeholder)
    
    char empty_name[256] = {0};
    m_currentFile->write(empty_name, 256);
    m_bytesWritten += 256;
    
    // Dataref count (2 bytes)
    const auto& datarefs = DatarefManager::Instance().GetDatarefs();
    WriteUInt16(static_cast<uint16_t>(datarefs.size()));
    
    // Write dataref definitions
    for (const auto& dr : datarefs) {
        // Validate name length
        if (dr.name.length() > 65535) {
            LogError("Dataref name too long: " + dr.name);
            continue;
        }
        
        // Name length (2 bytes)
        WriteUInt16(static_cast<uint16_t>(dr.name.length()));
        // Name (string)
        m_currentFile->write(dr.name.c_str(), dr.name.length());
        if (!m_currentFile->good()) {
            LogError("Failed to write dataref name: " + dr.name);
        }
        m_bytesWritten += dr.name.length();
        
        // Type (1 byte: 0=float, 1=int, 2=string)
        uint8_t typeCode = (dr.type == DatarefType::Float) ? 0 : 
                           (dr.type == DatarefType::Int) ? 1 : 2;
        WriteUInt8(typeCode);
        
        // Array size (1 byte, 0 for non-array)
        WriteUInt8(static_cast<uint8_t>(dr.arraySize));
    }
    
    if (m_currentFile->good()) {
        m_currentFile->flush();
    } else {
        LogError("File stream error after writing header");
    }
}

void Recorder::WriteFooter() {
    if (!m_currentFile) {
        LogError("WriteFooter called with null file");
        return;
    }
    
    if (!m_currentFile->good()) {
        LogError("File stream not in good state in WriteFooter");
        return;
    }
    
    // Footer marker "ENDR"
    m_currentFile->write("ENDR", 4);
    if (!m_currentFile->good()) {
        LogError("Failed to write footer marker");
        return;
    }
    m_bytesWritten += 4;
    
    // Total records (4 bytes)
    WriteUInt32(static_cast<uint32_t>(m_recordCount));
    
    // End timestamp (8 bytes)
    WriteUInt64(static_cast<uint64_t>(std::time(nullptr)));
    
    if (m_currentFile->good()) {
        m_currentFile->flush();
    } else {
        LogError("File stream error after writing footer");
    }
}

void Recorder::UpdateHeaderWithArrival() {
    if (!m_currentFile) {
        LogError("UpdateHeaderWithArrival called with null file");
        return;
    }
    
    // Calculate offset to arrival airport fields in header
    // Header structure (version 2):
    // - Magic (4) + Version (2) + Level (1) + Interval (4) + Start timestamp (8) = 19 bytes
    // - Departure ICAO (8) + Departure lat/lon (8) + Departure name (256) = 272 bytes
    // - Arrival ICAO (8) at offset 19 + 272 = 291
    const std::streamoff arrivalIcaoOffset = 291;
    
    // Save current position
    std::streampos currentPos = m_currentFile->tellp();
    
    // Seek to arrival ICAO field
    m_currentFile->seekp(arrivalIcaoOffset);
    
    // Write arrival airport ICAO (8 bytes, null-padded)
    m_currentFile->write(m_arrivalAirport.icao, 8);
    
    // Write arrival coordinates (8 bytes: 2 floats)
    // We need to write these manually since WriteFloat updates m_bytesWritten
    uint32_t latBits, lonBits;
    std::memcpy(&latBits, &m_arrivalAirport.lat, sizeof(float));
    std::memcpy(&lonBits, &m_arrivalAirport.lon, sizeof(float));
    
    // Write as little-endian
    uint8_t latBytes[4] = {
        static_cast<uint8_t>(latBits & 0xFF),
        static_cast<uint8_t>((latBits >> 8) & 0xFF),
        static_cast<uint8_t>((latBits >> 16) & 0xFF),
        static_cast<uint8_t>((latBits >> 24) & 0xFF)
    };
    m_currentFile->write(reinterpret_cast<const char*>(latBytes), 4);
    
    uint8_t lonBytes[4] = {
        static_cast<uint8_t>(lonBits & 0xFF),
        static_cast<uint8_t>((lonBits >> 8) & 0xFF),
        static_cast<uint8_t>((lonBits >> 16) & 0xFF),
        static_cast<uint8_t>((lonBits >> 24) & 0xFF)
    };
    m_currentFile->write(reinterpret_cast<const char*>(lonBytes), 4);
    
    // Write arrival name (256 bytes, null-padded)
    m_currentFile->write(m_arrivalAirport.name, 256);
    
    // Restore file position
    m_currentFile->seekp(currentPos);
    
    if (!m_currentFile->good()) {
        LogError("File stream error after updating arrival airport");
    }
}

void Recorder::RecordFrame() {
    // Start performance timer
    auto startTime = std::chrono::high_resolution_clock::now();
    
    if (!m_currentFile) {
        LogError("RecordFrame called with null file");
        return;
    }
    
    // Check if file is still good
    if (!m_currentFile->good()) {
        LogError("File stream is in bad state, stopping recording");
        Stop();
        return;
    }
    
    // Read current dataref values from X-Plane
    // This bulk reads all configured datarefs for the current recording level
    try {
        DatarefManager::Instance().ReadCurrentValues();
    } catch (const std::exception& e) {
        LogError(std::string("Exception reading dataref values: ") + e.what());
        // Continue with partial data rather than crashing
    }
    
    // Write frame marker to identify this as a data frame in the file
    m_currentFile->write("DATA", 4);
    m_bytesWritten += 4;
    
    // Timestamp (4 bytes float - relative to recording start)
    // Using cached dataref reference for performance
    static XPLMDataRef timeRef = XPLMFindDataRef("sim/time/total_running_time_sec");
    if (timeRef) {
        float relativeTime = XPLMGetDataf(timeRef);
        WriteFloat(relativeTime);
    } else {
        // Fallback if dataref not available
        WriteFloat(0.0f);
        LogError("Time dataref not available in RecordFrame");
    }
    
    // Write all dataref values with bounds checking
    // Values are written in the same order as defined in the header
    const auto& datarefs = DatarefManager::Instance().GetDatarefs();
    const auto& floatVals = DatarefManager::Instance().GetFloatValues();
    const auto& intVals = DatarefManager::Instance().GetIntValues();
    const auto& stringVals = DatarefManager::Instance().GetStringValues();
    
    size_t floatIdx = 0;
    size_t intIdx = 0;
    size_t stringIdx = 0;
    
    // Iterate through each dataref definition and write its value(s)
    for (const auto& dr : datarefs) {
        if (dr.arraySize > 0) {
            // Write array values with bounds checking
            for (int i = 0; i < dr.arraySize; i++) {
                if (dr.type == DatarefType::Float) {
                    if (floatIdx < floatVals.size()) {
                        WriteFloat(floatVals[floatIdx++]);
                    } else {
                        WriteFloat(0.0f); // Safety fallback
                        LogError("Float array index out of bounds");
                    }
                } else if (dr.type == DatarefType::Int) {
                    if (intIdx < intVals.size()) {
                        WriteInt32(intVals[intIdx++]);
                    } else {
                        WriteInt32(0); // Safety fallback
                        LogError("Int array index out of bounds");
                    }
                }
            }
        } else {
            // Write single value with bounds checking
            if (dr.type == DatarefType::Float) {
                if (floatIdx < floatVals.size()) {
                    WriteFloat(floatVals[floatIdx++]);
                } else {
                    WriteFloat(0.0f);
                    LogError("Float index out of bounds");
                }
            } else if (dr.type == DatarefType::Int) {
                if (intIdx < intVals.size()) {
                    WriteInt32(intVals[intIdx++]);
                } else {
                    WriteInt32(0);
                    LogError("Int index out of bounds");
                }
            } else if (dr.type == DatarefType::String) {
                if (stringIdx < stringVals.size()) {
                    WriteString(stringVals[stringIdx++]);
                } else {
                    WriteString("");
                    LogError("String index out of bounds");
                }
            }
        }
    }
    
    m_recordCount++;
    
    // Periodically flush buffer to disk for data safety
    // Balances between performance and data loss risk
    if (m_recordCount % FLUSH_INTERVAL == 0) {
        if (m_currentFile->good()) {
            m_currentFile->flush();
        }
    }
    
    // Track performance metrics
    auto endTime = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = endTime - startTime;
    double recordTime = elapsed.count();
    
    m_totalRecordTime += recordTime;
    m_perfSampleCount++;
    m_averageRecordTime = m_totalRecordTime / m_perfSampleCount;
    
    if (recordTime > m_maxRecordTime) {
        m_maxRecordTime = recordTime;
    }
    
    // Periodically log performance statistics (only if performance is degrading)
    if (m_recordCount % PERF_LOG_INTERVAL == 0) {
        // Log if average time exceeds 1ms or max exceeds 5ms (performance concern)
        if (m_averageRecordTime > 0.001 || m_maxRecordTime > 0.005) {
            LogInfo("Performance check at " + std::to_string(m_recordCount) + " records - " +
                    "Avg: " + std::to_string(m_averageRecordTime * 1000.0) + " ms, " +
                    "Max: " + std::to_string(m_maxRecordTime * 1000.0) + " ms");
        }
    }
}

bool Recorder::CheckAutoStartCondition() {
    AutoCondition condition = Settings::Instance().GetAutoStartCondition();
    float threshold = Settings::Instance().GetAutoStartThreshold();
    
    if (condition == AutoCondition::GroundSpeed) {
        static XPLMDataRef gsRef = XPLMFindDataRef("sim/flightmodel/position/groundspeed");
        if (!gsRef) {
            LogError("Ground speed dataref not found");
            return false;
        }
        float gs = XPLMGetDataf(gsRef);
        return gs > threshold;
    } else if (condition == AutoCondition::EngineRunning) {
        // Check if any engine is running
        static XPLMDataRef engRef = XPLMFindDataRef("sim/flightmodel/engine/ENGN_running");
        if (!engRef) {
            LogError("Engine running dataref not found");
            return false;
        }
        
        for (int i = 0; i < MAX_ENGINES; i++) {
            int running = 0;
            int count = XPLMGetDatavi(engRef, &running, i, 1);
            if (count > 0 && running == 1) {
                return true;
            }
        }
        return false;
    } else if (condition == AutoCondition::WeightOnWheels) {
        static XPLMDataRef wowRef = XPLMFindDataRef("sim/flightmodel/failures/onground_any");
        if (!wowRef) {
            LogError("Weight on wheels dataref not found");
            return false;
        }
        int onGround = XPLMGetDatai(wowRef);
        return onGround == 0;  // Not on ground
    }
    
    return false;
}

bool Recorder::CheckAutoStopCondition() {
    AutoCondition condition = Settings::Instance().GetAutoStopCondition();
    float threshold = Settings::Instance().GetAutoStopThreshold();
    
    if (condition == AutoCondition::GroundSpeed) {
        static XPLMDataRef gsRef = XPLMFindDataRef("sim/flightmodel/position/groundspeed");
        if (!gsRef) {
            LogError("Ground speed dataref not found in auto stop");
            return false;
        }
        float gs = XPLMGetDataf(gsRef);
        return gs < threshold;
    } else if (condition == AutoCondition::EngineRunning) {
        // Check if all engines are stopped
        static XPLMDataRef engRef = XPLMFindDataRef("sim/flightmodel/engine/ENGN_running");
        if (!engRef) {
            LogError("Engine running dataref not found in auto stop");
            return false;
        }
        
        for (int i = 0; i < MAX_ENGINES; i++) {
            int running = 0;
            int count = XPLMGetDatavi(engRef, &running, i, 1);
            if (count > 0 && running == 1) {
                return false;
            }
        }
        return true;
    } else if (condition == AutoCondition::WeightOnWheels) {
        static XPLMDataRef wowRef = XPLMFindDataRef("sim/flightmodel/failures/onground_any");
        if (!wowRef) {
            LogError("Weight on wheels dataref not found in auto stop");
            return false;
        }
        int onGround = XPLMGetDatai(wowRef);
        return onGround == 1;  // On ground
    }
    
    return false;
}

// Binary writing helpers (little-endian)
void Recorder::WriteUInt8(uint8_t value) {
    m_currentFile->write(reinterpret_cast<const char*>(&value), 1);
    m_bytesWritten += 1;
}

void Recorder::WriteUInt16(uint16_t value) {
    uint8_t bytes[2];
    bytes[0] = value & 0xFF;
    bytes[1] = (value >> 8) & 0xFF;
    m_currentFile->write(reinterpret_cast<const char*>(bytes), 2);
    m_bytesWritten += 2;
}

void Recorder::WriteUInt32(uint32_t value) {
    uint8_t bytes[4];
    bytes[0] = value & 0xFF;
    bytes[1] = (value >> 8) & 0xFF;
    bytes[2] = (value >> 16) & 0xFF;
    bytes[3] = (value >> 24) & 0xFF;
    m_currentFile->write(reinterpret_cast<const char*>(bytes), 4);
    m_bytesWritten += 4;
}

void Recorder::WriteUInt64(uint64_t value) {
    uint8_t bytes[8];
    for (int i = 0; i < 8; i++) {
        bytes[i] = (value >> (i * 8)) & 0xFF;
    }
    m_currentFile->write(reinterpret_cast<const char*>(bytes), 8);
    m_bytesWritten += 8;
}

void Recorder::WriteInt32(int32_t value) {
    WriteUInt32(static_cast<uint32_t>(value));
}

void Recorder::WriteFloat(float value) {
    // Write float in little-endian format for consistency
    uint32_t intValue;
    std::memcpy(&intValue, &value, sizeof(float));
    WriteUInt32(intValue);
}

void Recorder::WriteString(const std::string& str) {
    // Limit string length to 255
    size_t len = std::min(str.length(), size_t(255));
    WriteUInt8(static_cast<uint8_t>(len));
    if (len > 0) {
        m_currentFile->write(str.c_str(), len);
        m_bytesWritten += len;
    }
}

void Recorder::FlushBuffer() {
    if (m_currentFile) {
        m_currentFile->flush();
    }
}

// Airport detection using X-Plane Navigation API
AirportInfo Recorder::DetectNearestAirport(float lat, float lon) {
    AirportInfo result;
    
    // Find nearest airport using X-Plane navigation database
    XPLMNavRef navRef = XPLMFindNavAid(
        nullptr,              // name fragment (null = any)
        nullptr,              // ID fragment (null = any)
        &lat,                 // search near this latitude
        &lon,                 // search near this longitude
        nullptr,              // frequency (null = any)
        xplm_Nav_Airport      // only airports
    );
    
    if (navRef != XPLM_NAV_NOT_FOUND) {
        XPLMNavType navType = xplm_Nav_Unknown;
        float navLat = 0.0f, navLon = 0.0f;
        char navID[32] = {0};
        char navName[256] = {0};
        
        XPLMGetNavAidInfo(navRef, &navType, &navLat, &navLon, 
                         nullptr, nullptr, nullptr,
                         navID, navName, nullptr);
        
        // Calculate distance to verify it's nearby (within 5 nm)
        float distance = CalculateDistance(lat, lon, navLat, navLon);
        
        if (distance <= 5.0f) {
            // Airport is close enough
            result.valid = true;
            result.lat = navLat;
            result.lon = navLon;
            
            // Safely copy ICAO code with explicit null termination
            std::strncpy(result.icao, navID, sizeof(result.icao) - 1);
            result.icao[sizeof(result.icao) - 1] = '\0';
            
            // Safely copy name with explicit null termination
            std::strncpy(result.name, navName, sizeof(result.name) - 1);
            result.name[sizeof(result.name) - 1] = '\0';
        }
    }
    
    return result;
}

// Calculate great circle distance between two coordinates in nautical miles
float Recorder::CalculateDistance(float lat1, float lon1, float lat2, float lon2) {
    // Convert degrees to radians
    float lat1Rad = lat1 * M_PI / 180.0f;
    float lon1Rad = lon1 * M_PI / 180.0f;
    float lat2Rad = lat2 * M_PI / 180.0f;
    float lon2Rad = lon2 * M_PI / 180.0f;
    
    // Haversine formula
    float dLat = lat2Rad - lat1Rad;
    float dLon = lon2Rad - lon1Rad;
    
    float a = std::sin(dLat / 2.0f) * std::sin(dLat / 2.0f) +
              std::cos(lat1Rad) * std::cos(lat2Rad) *
              std::sin(dLon / 2.0f) * std::sin(dLon / 2.0f);
    
    float c = 2.0f * std::atan2(std::sqrt(a), std::sqrt(1.0f - a));
    
    // Distance in nautical miles
    return EARTH_RADIUS_NM * c;
}
