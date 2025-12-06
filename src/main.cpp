#include "common.h"
#include "Settings.h"
#include "DatarefManager.h"
#include "Recorder.h"
#include "UIManager.h"

// Plugin information
#define PLUGIN_NAME "XBlackBox"
#define PLUGIN_SIG "com.xblackbox.plugin"
#define PLUGIN_DESC "Flight Data Recorder for X-Plane 12"

// Flight loop callback
static float FlightLoopCallback(float elapsedMe, float elapsedSim, int counter, void* refcon);

// Plugin entry points
PLUGIN_API int XPluginStart(char* outName, char* outSig, char* outDesc) {
    // Set plugin information
    strcpy(outName, PLUGIN_NAME);
    strcpy(outSig, PLUGIN_SIG);
    strcpy(outDesc, PLUGIN_DESC);
    
    LogInfo("Plugin starting...");
    
    // Initialize settings
    Settings::Instance().Init();
    
    // Initialize dataref manager
    DatarefManager::Instance().Init();
    
    // Initialize recorder
    Recorder::Instance().Init();
    
    // Initialize UI
    UIManager::Instance().Init();
    
    LogInfo("Plugin started successfully");
    
    return 1;
}

PLUGIN_API void XPluginStop(void) {
    LogInfo("Plugin stopping...");
    
    // Stop recording if active
    if (Recorder::Instance().IsRecording()) {
        Recorder::Instance().Stop();
    }
    
    // Save settings
    Settings::Instance().Save();
    
    // Cleanup UI
    UIManager::Instance().Cleanup();
    
    LogInfo("Plugin stopped");
}

PLUGIN_API int XPluginEnable(void) {
    LogInfo("Plugin enabled");
    
    // Register flight loop callback
    XPLMCreateFlightLoop_t flightLoopParams;
    flightLoopParams.structSize = sizeof(XPLMCreateFlightLoop_t);
    flightLoopParams.phase = xplm_FlightLoop_Phase_AfterFlightModel;
    flightLoopParams.callbackFunc = FlightLoopCallback;
    flightLoopParams.refcon = nullptr;
    
    XPLMFlightLoopID flightLoopID = XPLMCreateFlightLoop(&flightLoopParams);
    if (flightLoopID) {
        XPLMScheduleFlightLoop(flightLoopID, -1.0f, 1);  // Call every frame
    }
    
    return 1;
}

PLUGIN_API void XPluginDisable(void) {
    LogInfo("Plugin disabled");
    
    // Stop recording if active
    if (Recorder::Instance().IsRecording()) {
        Recorder::Instance().Stop();
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
static float FlightLoopCallback(float elapsedMe, float elapsedSim, int counter, void* refcon) {
    (void)elapsedMe;  // Unused
    (void)counter;    // Unused
    (void)refcon;     // Unused
    
    // Update recorder
    Recorder::Instance().Update(elapsedSim);
    
    // Update UI
    UIManager::Instance().Update();
    UIManager::Instance().Draw();
    
    // Return -1 to be called every frame
    return -1.0f;
}
