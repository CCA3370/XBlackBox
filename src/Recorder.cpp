#include "Recorder.h"
#include <ctime>
#include <iomanip>
#include <sstream>
#include <cstring>

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
    , m_bytesWritten(0) {
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
    
    LogInfo("Recording started: " + filename.str());
    return true;
}

bool Recorder::Stop() {
    if (!m_isRecording) {
        return false;
    }
    
    // Flush any remaining buffered data
    try {
        FlushBuffer();
    } catch (const std::exception& e) {
        LogError(std::string("Exception flushing buffer: ") + e.what());
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
        // Exit early if we started recording to avoid double processing
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
    
    // Version (2 bytes)
    WriteUInt16(1);
    
    // Recording level (1 byte)
    WriteUInt8(static_cast<uint8_t>(Settings::Instance().GetRecordingLevel()));
    
    // Recording interval (4 bytes float)
    WriteFloat(Settings::Instance().GetRecordingInterval());
    
    // Start timestamp (8 bytes)
    WriteUInt64(static_cast<uint64_t>(m_recordingStartTime));
    
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

void Recorder::RecordFrame() {
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
            int running[1] = {0};
            int count = XPLMGetDatavi(engRef, running, i, 1);
            if (count > 0 && running[0] == 1) {
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
            int running[1] = {0};
            int count = XPLMGetDatavi(engRef, running, i, 1);
            if (count > 0 && running[0] == 1) {
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
