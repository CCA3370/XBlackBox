#pragma once

#include "common.h"
#include "Settings.h"
#include "DatarefManager.h"
#include <fstream>
#include <vector>
#include <memory>
#include <chrono>

class Recorder {
public:
    // Singleton access
    static Recorder& Instance();
    
    // Initialize recorder
    void Init();
    
    // Start/Stop recording
    bool Start();
    bool Stop();
    
    // Update (called every frame)
    void Update(float deltaTime);
    
    // Recording status
    bool IsRecording() const { return m_isRecording; }
    int GetRecordCount() const { return m_recordCount; }
    size_t GetBytesWritten() const { return m_bytesWritten; }
    int GetDuration() const;
    std::string GetCurrentFilePath() const { return m_currentFilePath; }
    
    // Performance statistics
    double GetAverageRecordTime() const { return m_averageRecordTime; }
    double GetMaxRecordTime() const { return m_maxRecordTime; }
    
private:
    Recorder();
    ~Recorder();
    Recorder(const Recorder&) = delete;
    Recorder& operator=(const Recorder&) = delete;
    
    // File writing
    void WriteHeader();
    void WriteFooter();
    void RecordFrame();
    
    // Auto recording
    bool CheckAutoStartCondition();
    bool CheckAutoStopCondition();
    
    // Binary writing helpers (little-endian)
    void WriteUInt8(uint8_t value);
    void WriteUInt16(uint16_t value);
    void WriteUInt32(uint32_t value);
    void WriteUInt64(uint64_t value);
    void WriteInt32(int32_t value);
    void WriteFloat(float value);
    void WriteString(const std::string& str);
    
    // Buffered writing for efficiency
    void FlushBuffer();
    
    bool m_isRecording;
    std::unique_ptr<std::ofstream> m_currentFile;
    std::string m_currentFilePath;
    std::time_t m_recordingStartTime;
    float m_lastRecordTime;
    float m_lastUpdateTime;
    float m_autoStopTimer;
    
    // Statistics
    int m_recordCount;
    size_t m_bytesWritten;
    
    // Performance tracking
    double m_averageRecordTime;
    double m_maxRecordTime;
    double m_totalRecordTime;
    int m_perfSampleCount;
    
    // Write buffer for efficiency
    std::vector<uint8_t> m_writeBuffer;
    static constexpr size_t BUFFER_SIZE = 65536;  // 64KB buffer
    static constexpr int FLUSH_INTERVAL = 10;  // Flush every N records
    static constexpr int PERF_LOG_INTERVAL = 1000;  // Log performance every N records
};
