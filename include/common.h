#pragma once

#include <string>
#include <vector>
#include <memory>
#include <cstdint>
#include <ctime>

// X-Plane SDK
#include "XPLMDataAccess.h"
#include "XPLMPlugin.h"
#include "XPLMProcessing.h"
#include "XPLMUtilities.h"
#include "XPLMMenus.h"
#include "XPLMDisplay.h"

// ImGui
#include "imgui.h"

// Constants
constexpr int MAX_ENGINES = 8;
constexpr int MAX_BATTERIES = 8;
constexpr int MAX_GENERATORS = 8;
constexpr int MAX_LANDING_GEAR = 10;

// Recording levels
enum class RecordingLevel {
    Simple = 1,
    Normal = 2,
    Detailed = 3
};

// Auto recording conditions
enum class AutoCondition {
    GroundSpeed,
    EngineRunning,
    WeightOnWheels
};

// Dataref types
enum class DatarefType {
    Float,
    Int,
    String
};

// Dataref definition
struct DatarefDef {
    std::string name;
    std::string description;
    DatarefType type;
    int arraySize;  // 0 for non-array, >0 for arrays
    XPLMDataRef ref;
    
    DatarefDef(const std::string& n, const std::string& desc, DatarefType t, int arrSize = 0)
        : name(n), description(desc), type(t), arraySize(arrSize), ref(nullptr) {}
};

// Utility functions
inline std::string GetXPlaneDirectory() {
    char path[512];
    XPLMGetSystemPath(path);
    return std::string(path);
}

inline std::string GetOutputDirectory() {
    return GetXPlaneDirectory() + "Output/XBlackBox/";
}

inline void LogInfo(const std::string& message) {
    XPLMDebugString(("XBlackBox: " + message + "\n").c_str());
}

inline void LogError(const std::string& message) {
    XPLMDebugString(("XBlackBox ERROR: " + message + "\n").c_str());
}
