#include "common.h"
#include "Settings.h"
#include "DatarefManager.h"
#include "Recorder.h"
#include "UIManager.h"
#include <cstring>

// Plugin information
#define PLUGIN_NAME "XBlackBox"
#define PLUGIN_SIG "com.xblackbox.plugin"
#define PLUGIN_DESC "Flight Data Recorder for X-Plane 12"

// Flight loop callback
static float FlightLoopCallback(float elapsedMe, float elapsedSim, int counter, void* refcon);

// Plugin entry points
PLUGIN_API int XPluginStart(char* outName, char* outSig, char* outDesc) {
    // Validate output parameters
    if (!outName || !outSig || !outDesc) {
        return 0;  // Failed initialization
    }
    
    // Set plugin information
    strcpy(outName, PLUGIN_NAME);
    strcpy(outSig, PLUGIN_SIG);
    strcpy(outDesc, PLUGIN_DESC);
    
    LogInfo("Plugin starting...");
    
    // Initialize settings first (other components may depend on it)
    try {
        Settings::Instance().Init();
    } catch (const std::exception& e) {
        LogError(std::string("Failed to initialize settings: ") + e.what());
        return 0;
    }
    
    // Initialize dataref manager
    try {
        DatarefManager::Instance().Init();
    } catch (const std::exception& e) {
        LogError(std::string("Failed to initialize dataref manager: ") + e.what());
        return 0;
    }
    
    // Initialize recorder
    try {
        Recorder::Instance().Init();
    } catch (const std::exception& e) {
        LogError(std::string("Failed to initialize recorder: ") + e.what());
        return 0;
    }
    
    // Initialize UI
    try {
        UIManager::Instance().Init();
    } catch (const std::exception& e) {
        LogError(std::string("Failed to initialize UI: ") + e.what());
        // UI failure is not critical, continue without UI
    }
    
    LogInfo("Plugin started successfully");
    
    return 1;
}

PLUGIN_API void XPluginStop(void) {
    LogInfo("Plugin stopping...");
    
    // Stop recording if active (with error handling)
    try {
        if (Recorder::Instance().IsRecording()) {
            Recorder::Instance().Stop();
        }
    } catch (const std::exception& e) {
        LogError(std::string("Exception stopping recording: ") + e.what());
    }
    
    // Save settings (with error handling)
    try {
        Settings::Instance().Save();
    } catch (const std::exception& e) {
        LogError(std::string("Exception saving settings: ") + e.what());
    }
    
    // Cleanup UI (with error handling)
    try {
        UIManager::Instance().Cleanup();
    } catch (const std::exception& e) {
        LogError(std::string("Exception cleaning up UI: ") + e.what());
    }
    
    LogInfo("Plugin stopped");
}

PLUGIN_API int XPluginEnable(void) {
    LogInfo("Plugin enabled");
    
    // Register flight loop callback with error handling
    try {
        XPLMCreateFlightLoop_t flightLoopParams;
        flightLoopParams.structSize = sizeof(XPLMCreateFlightLoop_t);
        flightLoopParams.phase = xplm_FlightLoop_Phase_AfterFlightModel;
        flightLoopParams.callbackFunc = FlightLoopCallback;
        flightLoopParams.refcon = nullptr;
        
        XPLMFlightLoopID flightLoopID = XPLMCreateFlightLoop(&flightLoopParams);
        if (flightLoopID) {
            XPLMScheduleFlightLoop(flightLoopID, -1.0f, 1);  // Call every frame
        } else {
            LogError("Failed to create flight loop");
            return 0;
        }
    } catch (const std::exception& e) {
        LogError(std::string("Exception enabling plugin: ") + e.what());
        return 0;
    }
    
    return 1;
}

PLUGIN_API void XPluginDisable(void) {
    LogInfo("Plugin disabled");
    
    // Stop recording if active (with error handling)
    try {
        if (Recorder::Instance().IsRecording()) {
            Recorder::Instance().Stop();
        }
    } catch (const std::exception& e) {
        LogError(std::string("Exception stopping recording during disable: ") + e.what());
    }
}

PLUGIN_API void XPluginReceiveMessage(XPLMPluginID inFrom, int inMsg, void* inParam) {
    (void)inFrom;   // Unused
    (void)inMsg;    // Unused
    (void)inParam;  // Unused
    // Handle messages if needed
    // For now, we don't need to handle any specific messages
}

// Flight loop callback - called every frame
// This is a performance-critical function, keep it lightweight
static float FlightLoopCallback(float elapsedMe, float elapsedSim, int counter, void* refcon) {
    (void)elapsedMe;  // Unused
    (void)counter;    // Unused
    (void)refcon;     // Unused
    
    try {
        // Update recorder (handles auto-recording and data writing)
        Recorder::Instance().Update(elapsedSim);
        
        // Update UI (handles notification timers, etc.)
        UIManager::Instance().Update();
    } catch (const std::exception& e) {
        // Log but don't crash - this is called every frame
        LogError(std::string("Exception in flight loop: ") + e.what());
    }
    
    // Return -1 to be called every frame
    return -1.0f;
}
