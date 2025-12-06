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
    std::ostringstream filename;
    filename << Settings::Instance().GetFilePrefix()
             << std::put_time(tm, "%Y%m%d_%H%M%S")
             << ".xdr";
    
    m_currentFilePath = Settings::Instance().GetOutputDirectory() + filename.str();
    
    // Open file in binary mode
    m_currentFile = std::make_unique<std::ofstream>(m_currentFilePath, 
                                                     std::ios::binary | std::ios::out);
    if (!m_currentFile->is_open()) {
        LogError("Could not create recording file: " + m_currentFilePath);
        m_currentFile.reset();
        return false;
    }
    
    // Write header
    WriteHeader();
    
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
    FlushBuffer();
    
    // Write footer
    WriteFooter();
    
    // Close file
    if (m_currentFile) {
        m_currentFile->close();
        m_currentFile.reset();
    }
    
    m_isRecording = false;
    
    int duration = static_cast<int>(std::time(nullptr) - m_recordingStartTime);
    LogInfo("Recording stopped - " + std::to_string(m_recordCount) + " records, " +
            std::to_string(m_bytesWritten) + " bytes, " + std::to_string(duration) + " seconds");
    
    return true;
}

void Recorder::Update(float deltaTime) {
    XPLMDataRef timeRef = XPLMFindDataRef("sim/time/total_running_time_sec");
    float currentTime = XPLMGetDataf(timeRef);
    
    // Update last update time
    m_lastUpdateTime = currentTime;
    
    // Check auto mode
    if (Settings::Instance().GetAutoMode() && !m_isRecording) {
        if (CheckAutoStartCondition()) {
            Start();
        }
    }
    
    // Check auto stop
    if (Settings::Instance().GetAutoMode() && m_isRecording) {
        if (CheckAutoStopCondition()) {
            m_autoStopTimer += deltaTime;
            if (m_autoStopTimer >= Settings::Instance().GetAutoStopDelay()) {
                Stop();
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
    if (!m_currentFile) return;
    
    // Magic number "XFDR" (note: keeping XFDR for compatibility, file extension is .xdr)
    m_currentFile->write("XFDR", 4);
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
        // Name length (2 bytes)
        WriteUInt16(static_cast<uint16_t>(dr.name.length()));
        // Name (string)
        m_currentFile->write(dr.name.c_str(), dr.name.length());
        m_bytesWritten += dr.name.length();
        
        // Type (1 byte: 0=float, 1=int, 2=string)
        uint8_t typeCode = (dr.type == DatarefType::Float) ? 0 : 
                           (dr.type == DatarefType::Int) ? 1 : 2;
        WriteUInt8(typeCode);
        
        // Array size (1 byte, 0 for non-array)
        WriteUInt8(static_cast<uint8_t>(dr.arraySize));
    }
    
    m_currentFile->flush();
}

void Recorder::WriteFooter() {
    if (!m_currentFile) return;
    
    // Footer marker "ENDR"
    m_currentFile->write("ENDR", 4);
    m_bytesWritten += 4;
    
    // Total records (4 bytes)
    WriteUInt32(static_cast<uint32_t>(m_recordCount));
    
    // End timestamp (8 bytes)
    WriteUInt64(static_cast<uint64_t>(std::time(nullptr)));
    
    m_currentFile->flush();
}

void Recorder::RecordFrame() {
    if (!m_currentFile) return;
    
    // Read current dataref values
    DatarefManager::Instance().ReadCurrentValues();
    
    // Frame marker "DATA"
    m_currentFile->write("DATA", 4);
    m_bytesWritten += 4;
    
    // Timestamp (4 bytes float - relative to start)
    XPLMDataRef timeRef = XPLMFindDataRef("sim/time/total_running_time_sec");
    float relativeTime = XPLMGetDataf(timeRef);
    WriteFloat(relativeTime);
    
    // Write all dataref values
    const auto& datarefs = DatarefManager::Instance().GetDatarefs();
    const auto& floatVals = DatarefManager::Instance().GetFloatValues();
    const auto& intVals = DatarefManager::Instance().GetIntValues();
    const auto& stringVals = DatarefManager::Instance().GetStringValues();
    
    size_t floatIdx = 0;
    size_t intIdx = 0;
    size_t stringIdx = 0;
    
    for (const auto& dr : datarefs) {
        if (dr.arraySize > 0) {
            // Write array values
            for (int i = 0; i < dr.arraySize; i++) {
                if (dr.type == DatarefType::Float) {
                    WriteFloat(floatVals[floatIdx++]);
                } else if (dr.type == DatarefType::Int) {
                    WriteInt32(intVals[intIdx++]);
                }
            }
        } else {
            // Write single value
            if (dr.type == DatarefType::Float) {
                WriteFloat(floatVals[floatIdx++]);
            } else if (dr.type == DatarefType::Int) {
                WriteInt32(intVals[intIdx++]);
            } else if (dr.type == DatarefType::String) {
                WriteString(stringVals[stringIdx++]);
            }
        }
    }
    
    m_recordCount++;
    
    // Flush periodically
    if (m_recordCount % FLUSH_INTERVAL == 0) {
        m_currentFile->flush();
    }
}

bool Recorder::CheckAutoStartCondition() {
    AutoCondition condition = Settings::Instance().GetAutoStartCondition();
    float threshold = Settings::Instance().GetAutoStartThreshold();
    
    if (condition == AutoCondition::GroundSpeed) {
        XPLMDataRef gsRef = XPLMFindDataRef("sim/flightmodel/position/groundspeed");
        float gs = XPLMGetDataf(gsRef);
        return gs > threshold;
    } else if (condition == AutoCondition::EngineRunning) {
        // Check if any engine is running
        XPLMDataRef engRef = XPLMFindDataRef("sim/flightmodel/engine/ENGN_running");
        if (engRef) {
            for (int i = 0; i < MAX_ENGINES; i++) {
                int running[1];
                XPLMGetDatavi(engRef, running, i, 1);
                if (running[0] == 1) {
                    return true;
                }
            }
        }
        return false;
    } else if (condition == AutoCondition::WeightOnWheels) {
        XPLMDataRef wowRef = XPLMFindDataRef("sim/flightmodel/failures/onground_any");
        int onGround = XPLMGetDatai(wowRef);
        return onGround == 0;  // Not on ground
    }
    
    return false;
}

bool Recorder::CheckAutoStopCondition() {
    AutoCondition condition = Settings::Instance().GetAutoStopCondition();
    float threshold = Settings::Instance().GetAutoStopThreshold();
    
    if (condition == AutoCondition::GroundSpeed) {
        XPLMDataRef gsRef = XPLMFindDataRef("sim/flightmodel/position/groundspeed");
        float gs = XPLMGetDataf(gsRef);
        return gs < threshold;
    } else if (condition == AutoCondition::EngineRunning) {
        // Check if all engines are stopped
        XPLMDataRef engRef = XPLMFindDataRef("sim/flightmodel/engine/ENGN_running");
        if (engRef) {
            for (int i = 0; i < MAX_ENGINES; i++) {
                int running[1];
                XPLMGetDatavi(engRef, running, i, 1);
                if (running[0] == 1) {
                    return false;
                }
            }
        }
        return true;
    } else if (condition == AutoCondition::WeightOnWheels) {
        XPLMDataRef wowRef = XPLMFindDataRef("sim/flightmodel/failures/onground_any");
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
    m_currentFile->write(reinterpret_cast<const char*>(&value), 4);
    m_bytesWritten += 4;
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
