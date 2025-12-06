#include "Settings.h"
#include <fstream>
#include <sstream>
#include <sys/stat.h>

#ifdef _WIN32
#include <direct.h>
#define mkdir(path, mode) _mkdir(path)
#endif

Settings& Settings::Instance() {
    static Settings instance;
    return instance;
}

Settings::Settings() {
    SetDefaults();
}

void Settings::SetDefaults() {
    m_recordingLevel = RecordingLevel::Detailed;
    m_recordingInterval = 0.25f;  // 4Hz
    m_autoMode = false;
    m_autoStartCondition = AutoCondition::GroundSpeed;
    m_autoStartThreshold = 5.0f;  // 5 knots
    m_autoStopCondition = AutoCondition::GroundSpeed;
    m_autoStopThreshold = 5.0f;  // 5 knots
    m_autoStopDelay = 30.0f;  // 30 seconds
    m_outputDirectory = GetOutputDirectory();
    m_filePrefix = "flightdata_";
    m_configPath = m_outputDirectory + "config.ini";
}

void Settings::Init() {
    SetDefaults();
    CreateOutputDirectory();
    Load();
}

void Settings::CreateOutputDirectory() {
    struct stat info;
    if (stat(m_outputDirectory.c_str(), &info) != 0) {
        // Directory doesn't exist, create it
        mkdir(m_outputDirectory.c_str(), 0755);
        LogInfo("Created output directory: " + m_outputDirectory);
    }
}

void Settings::Load() {
    std::ifstream file(m_configPath);
    if (!file.is_open()) {
        LogInfo("No config file found, using defaults");
        return;
    }
    
    std::string line;
    while (std::getline(file, line)) {
        // Skip comments and empty lines
        if (line.empty() || line[0] == '#' || line[0] == ';') {
            continue;
        }
        
        // Parse key=value
        size_t pos = line.find('=');
        if (pos == std::string::npos) {
            continue;
        }
        
        std::string key = line.substr(0, pos);
        std::string value = line.substr(pos + 1);
        
        // Trim whitespace
        key.erase(0, key.find_first_not_of(" \t"));
        key.erase(key.find_last_not_of(" \t") + 1);
        value.erase(0, value.find_first_not_of(" \t"));
        value.erase(value.find_last_not_of(" \t") + 1);
        
        // Remove quotes from string values
        if (value.size() >= 2 && value[0] == '"' && value[value.size()-1] == '"') {
            value = value.substr(1, value.size() - 2);
        }
        
        // Apply settings
        if (key == "recordingLevel") {
            int level = std::stoi(value);
            if (level >= 1 && level <= 3) {
                m_recordingLevel = static_cast<RecordingLevel>(level);
            }
        } else if (key == "recordingInterval") {
            m_recordingInterval = std::stof(value);
        } else if (key == "autoMode") {
            m_autoMode = (value == "true" || value == "1");
        } else if (key == "autoStartCondition") {
            if (value == "ground_speed") m_autoStartCondition = AutoCondition::GroundSpeed;
            else if (value == "engine_running") m_autoStartCondition = AutoCondition::EngineRunning;
            else if (value == "weight_on_wheels") m_autoStartCondition = AutoCondition::WeightOnWheels;
        } else if (key == "autoStartThreshold") {
            m_autoStartThreshold = std::stof(value);
        } else if (key == "autoStopCondition") {
            if (value == "ground_speed") m_autoStopCondition = AutoCondition::GroundSpeed;
            else if (value == "engine_running") m_autoStopCondition = AutoCondition::EngineRunning;
            else if (value == "weight_on_wheels") m_autoStopCondition = AutoCondition::WeightOnWheels;
        } else if (key == "autoStopThreshold") {
            m_autoStopThreshold = std::stof(value);
        } else if (key == "autoStopDelay") {
            m_autoStopDelay = std::stof(value);
        } else if (key == "filePrefix") {
            m_filePrefix = value;
        }
    }
    
    file.close();
    LogInfo("Settings loaded from " + m_configPath);
}

void Settings::Save() {
    std::ofstream file(m_configPath);
    if (!file.is_open()) {
        LogError("Could not save settings to " + m_configPath);
        return;
    }
    
    file << "# XBlackBox Configuration File\n";
    file << "# Recording Settings\n";
    file << "recordingLevel=" << static_cast<int>(m_recordingLevel) << "\n";
    file << "recordingInterval=" << m_recordingInterval << "\n";
    file << "\n# Auto Recording Mode\n";
    file << "autoMode=" << (m_autoMode ? "true" : "false") << "\n";
    file << "autoStartCondition=" << GetAutoConditionName(m_autoStartCondition) << "\n";
    file << "autoStartThreshold=" << m_autoStartThreshold << "\n";
    file << "autoStopCondition=" << GetAutoConditionName(m_autoStopCondition) << "\n";
    file << "autoStopThreshold=" << m_autoStopThreshold << "\n";
    file << "autoStopDelay=" << m_autoStopDelay << "\n";
    file << "\n# File Settings\n";
    file << "filePrefix=\"" << m_filePrefix << "\"\n";
    
    file.close();
    LogInfo("Settings saved to " + m_configPath);
}

std::string Settings::GetRecordingLevelName() const {
    switch (m_recordingLevel) {
        case RecordingLevel::Simple: return "Simple";
        case RecordingLevel::Normal: return "Normal";
        case RecordingLevel::Detailed: return "Detailed";
        default: return "Unknown";
    }
}

std::string Settings::GetAutoConditionName(AutoCondition cond) const {
    switch (cond) {
        case AutoCondition::GroundSpeed: return "ground_speed";
        case AutoCondition::EngineRunning: return "engine_running";
        case AutoCondition::WeightOnWheels: return "weight_on_wheels";
        default: return "ground_speed";
    }
}
