#pragma once

#include "common.h"
#include "Settings.h"
#include "DatarefManager.h"
#include <fstream>
#include <vector>
#include <memory>
#include <chrono>
#include <string>
#include <cstring>

// Airport information structure
struct AirportInfo {
    char icao[8];      // ICAO code (e.g., "KSFO")
    char name[256];    // Airport name
    float lat;         // Latitude
    float lon;         // Longitude
    bool valid;        // Whether airport was detected
    
    AirportInfo() : lat(0.0f), lon(0.0f), valid(false) {
        memset(icao, 0, sizeof(icao));
        memset(name, 0, sizeof(name));
    }
};

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
    void UpdateHeaderWithArrival();
    
    // Auto recording
    bool CheckAutoStartCondition();
    bool CheckAutoStopCondition();
    
    // Airport detection
    AirportInfo DetectNearestAirport(float lat, float lon);
    float CalculateDistance(float lat1, float lon1, float lat2, float lon2);
    
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
    
    // Airport information
    AirportInfo m_departureAirport;
    AirportInfo m_arrivalAirport;
    
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
