#pragma once

#include "common.h"
#include <map>
#include <fstream>

class Settings {
public:
    // Singleton access
    static Settings& Instance();
    
    // Initialize and load settings
    void Init();
    
    // Load/Save settings
    void Load();
    void Save();
    
    // Getters
    RecordingLevel GetRecordingLevel() const { return m_recordingLevel; }
    float GetRecordingInterval() const { return m_recordingInterval; }
    bool GetAutoMode() const { return m_autoMode; }
    AutoCondition GetAutoStartCondition() const { return m_autoStartCondition; }
    float GetAutoStartThreshold() const { return m_autoStartThreshold; }
    AutoCondition GetAutoStopCondition() const { return m_autoStopCondition; }
    float GetAutoStopThreshold() const { return m_autoStopThreshold; }
    float GetAutoStopDelay() const { return m_autoStopDelay; }
    std::string GetOutputDirectory() const { return m_outputDirectory; }
    std::string GetFilePrefix() const { return m_filePrefix; }
    
    // Setters
    void SetRecordingLevel(RecordingLevel level) { m_recordingLevel = level; }
    void SetRecordingInterval(float interval) { m_recordingInterval = interval; }
    void SetAutoMode(bool enabled) { m_autoMode = enabled; }
    void SetAutoStartCondition(AutoCondition cond) { m_autoStartCondition = cond; }
    void SetAutoStartThreshold(float threshold) { m_autoStartThreshold = threshold; }
    void SetAutoStopCondition(AutoCondition cond) { m_autoStopCondition = cond; }
    void SetAutoStopThreshold(float threshold) { m_autoStopThreshold = threshold; }
    void SetAutoStopDelay(float delay) { m_autoStopDelay = delay; }
    
    // Helper functions
    std::string GetRecordingLevelName() const;
    std::string GetAutoConditionName(AutoCondition cond) const;
    
private:
    Settings();
    ~Settings() = default;
    Settings(const Settings&) = delete;
    Settings& operator=(const Settings&) = delete;
    
    void SetDefaults();
    void CreateOutputDirectory();
    
    // Settings
    RecordingLevel m_recordingLevel;
    float m_recordingInterval;
    bool m_autoMode;
    AutoCondition m_autoStartCondition;
    float m_autoStartThreshold;
    AutoCondition m_autoStopCondition;
    float m_autoStopThreshold;
    float m_autoStopDelay;
    std::string m_outputDirectory;
    std::string m_filePrefix;
    std::string m_configPath;
};
