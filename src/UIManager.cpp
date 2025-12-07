#include "UIManager.h"
#include "XPLMGraphics.h"
#include <cstring>

#ifdef _WIN32
#include <windows.h>
#include <shellapi.h>
#elif __APPLE__
#include <stdlib.h>
#else
#include <stdlib.h>
#endif

// Forward declarations for window callbacks
static void StatusWindowDraw(XPLMWindowID inWindowID, void* inRefcon);
static int StatusWindowClick(XPLMWindowID inWindowID, int x, int y, XPLMMouseStatus status, void* inRefcon);
static void StatusWindowKey(XPLMWindowID inWindowID, char key, XPLMKeyFlags flags, char vkey, void* inRefcon, int losingFocus);
static XPLMCursorStatus StatusWindowCursor(XPLMWindowID inWindowID, int x, int y, void* inRefcon);
static int StatusWindowWheel(XPLMWindowID inWindowID, int x, int y, int wheel, int clicks, void* inRefcon);

// Forward declarations for settings window callbacks
static void SettingsWindowDraw(XPLMWindowID inWindowID, void* inRefcon);
static int SettingsWindowClick(XPLMWindowID inWindowID, int x, int y, XPLMMouseStatus status, void* inRefcon);
static void SettingsWindowKey(XPLMWindowID inWindowID, char key, XPLMKeyFlags flags, char vkey, void* inRefcon, int losingFocus);
static XPLMCursorStatus SettingsWindowCursor(XPLMWindowID inWindowID, int x, int y, void* inRefcon);
static int SettingsWindowWheel(XPLMWindowID inWindowID, int x, int y, int wheel, int clicks, void* inRefcon);

UIManager& UIManager::Instance() {
    static UIManager instance;
    return instance;
}

UIManager::UIManager()
    : m_menuID(nullptr)
    , m_levelMenu(nullptr)
    , m_intervalMenu(nullptr)
    , m_menuItem_AutoMode(-1)
    , m_menuItem_StartStop(-1)
    , m_menuItem_ShowStatus(-1)
    , m_menuItem_Settings(-1)
    , m_levelItem_Simple(-1)
    , m_levelItem_Normal(-1)
    , m_levelItem_Detailed(-1)
    , m_intervalItem_20Hz(-1)
    , m_intervalItem_10Hz(-1)
    , m_intervalItem_4Hz(-1)
    , m_intervalItem_1Hz(-1)
    , m_showStatusWindow(false)
    , m_showSettingsWindow(false)
    , m_imguiInitialized(false)
    , m_imguiWindow(nullptr)
    , m_settingsWindow(nullptr)
    , m_notificationMessage("")
    , m_notificationTime(0.0f) {
}

void UIManager::Init() {
    CreateMenu();
    InitImGui();
    LogInfo("UI initialized");
}

void UIManager::Cleanup() {
    CleanupImGui();
    
    if (m_settingsWindow) {
        XPLMDestroyWindow(m_settingsWindow);
        m_settingsWindow = nullptr;
    }
    
    if (m_menuID) {
        XPLMDestroyMenu(m_menuID);
        m_menuID = nullptr;
    }
}

void UIManager::Update() {
    // Update notification timer
    if (m_notificationTime > 0.0f) {
        XPLMDataRef timeRef = XPLMFindDataRef("sim/time/framerate_period");
        float framePeriod = XPLMGetDataf(timeRef);
        m_notificationTime -= framePeriod;
    }
}

void UIManager::Draw() {
    // ImGui drawing is handled in the draw callback
    // This function is kept for compatibility but actual drawing
    // happens in ImGuiDrawCallback
}

void UIManager::CreateMenu() {
    // Find plugins menu
    XPLMMenuID pluginsMenu = XPLMFindPluginsMenu();
    if (!pluginsMenu) {
        LogError("Could not find plugins menu");
        return;
    }
    
    // Create our submenu with unified menu handler
    int menuIndex = XPLMAppendMenuItem(pluginsMenu, "XBlackBox", nullptr, 0);
    m_menuID = XPLMCreateMenu("XBlackBox", pluginsMenu, menuIndex, 
                               MenuCallback, nullptr);
    
    if (!m_menuID) {
        LogError("Failed to create menu");
        return;
    }
    
    // Auto mode toggle
    m_menuItem_AutoMode = XPLMAppendMenuItem(m_menuID, "Auto Mode: OFF", 
                                              reinterpret_cast<void*>(0), 0);
    
    // Start/Stop recording
    m_menuItem_StartStop = XPLMAppendMenuItem(m_menuID, "Start Recording", 
                                               reinterpret_cast<void*>(1), 0);
    
    // Separator
    XPLMAppendMenuSeparator(m_menuID);
    
    // Recording level submenu
    int levelMenuItem = XPLMAppendMenuItem(m_menuID, "Recording Level", nullptr, 0);
    m_levelMenu = XPLMCreateMenu("Recording Level", m_menuID, levelMenuItem,
                                  MenuCallback, nullptr);
    m_levelItem_Simple = XPLMAppendMenuItem(m_levelMenu, "Simple (Basic flight data)", 
                       reinterpret_cast<void*>(10), 0);
    m_levelItem_Normal = XPLMAppendMenuItem(m_levelMenu, "Normal (+ Controls & systems)", 
                       reinterpret_cast<void*>(11), 0);
    m_levelItem_Detailed = XPLMAppendMenuItem(m_levelMenu, "Detailed (Everything)", 
                       reinterpret_cast<void*>(12), 0);
    
    // Recording interval submenu
    int intervalMenuItem = XPLMAppendMenuItem(m_menuID, "Recording Interval", nullptr, 0);
    m_intervalMenu = XPLMCreateMenu("Recording Interval", m_menuID, intervalMenuItem,
                                     MenuCallback, nullptr);
    m_intervalItem_20Hz = XPLMAppendMenuItem(m_intervalMenu, "20 Hz (0.05 sec) - Very Fast", 
                       reinterpret_cast<void*>(20), 0);
    m_intervalItem_10Hz = XPLMAppendMenuItem(m_intervalMenu, "10 Hz (0.10 sec) - Fast", 
                       reinterpret_cast<void*>(21), 0);
    m_intervalItem_4Hz = XPLMAppendMenuItem(m_intervalMenu, "4 Hz (0.25 sec) - Normal", 
                       reinterpret_cast<void*>(22), 0);
    m_intervalItem_1Hz = XPLMAppendMenuItem(m_intervalMenu, "1 Hz (1.0 sec) - Slow", 
                       reinterpret_cast<void*>(23), 0);
    
    // Separator
    XPLMAppendMenuSeparator(m_menuID);
    
    // Show status
    m_menuItem_ShowStatus = XPLMAppendMenuItem(m_menuID, "Show Status", 
                                                reinterpret_cast<void*>(2), 0);
    
    // Settings
    m_menuItem_Settings = XPLMAppendMenuItem(m_menuID, "Settings...", 
                                              reinterpret_cast<void*>(4), 0);
    
    // Open output folder
    XPLMAppendMenuItem(m_menuID, "Open Output Folder", 
                       reinterpret_cast<void*>(3), 0);
    
    UpdateMenu();
}

void UIManager::UpdateMenu() {
    if (!m_menuID) return;
    
    // Update auto mode text
    XPLMSetMenuItemName(m_menuID, m_menuItem_AutoMode,
                        Settings::Instance().GetAutoMode() ? "Auto Mode: ON" : "Auto Mode: OFF", 0);
    
    // Update start/stop text
    XPLMSetMenuItemName(m_menuID, m_menuItem_StartStop,
                        Recorder::Instance().IsRecording() ? "Stop Recording" : "Start Recording", 0);
    
    // Update recording level checkmarks
    if (m_levelMenu) {
        RecordingLevel currentLevel = Settings::Instance().GetRecordingLevel();
        XPLMCheckMenuItem(m_levelMenu, m_levelItem_Simple, 
                         currentLevel == RecordingLevel::Simple ? xplm_Menu_Checked : xplm_Menu_Unchecked);
        XPLMCheckMenuItem(m_levelMenu, m_levelItem_Normal, 
                         currentLevel == RecordingLevel::Normal ? xplm_Menu_Checked : xplm_Menu_Unchecked);
        XPLMCheckMenuItem(m_levelMenu, m_levelItem_Detailed, 
                         currentLevel == RecordingLevel::Detailed ? xplm_Menu_Checked : xplm_Menu_Unchecked);
    }
    
    // Update recording interval checkmarks
    if (m_intervalMenu) {
        float currentInterval = Settings::Instance().GetRecordingInterval();
        XPLMCheckMenuItem(m_intervalMenu, m_intervalItem_20Hz, 
                         (currentInterval <= 0.051f && currentInterval >= 0.049f) ? xplm_Menu_Checked : xplm_Menu_Unchecked);
        XPLMCheckMenuItem(m_intervalMenu, m_intervalItem_10Hz, 
                         (currentInterval <= 0.101f && currentInterval >= 0.099f) ? xplm_Menu_Checked : xplm_Menu_Unchecked);
        XPLMCheckMenuItem(m_intervalMenu, m_intervalItem_4Hz, 
                         (currentInterval <= 0.251f && currentInterval >= 0.249f) ? xplm_Menu_Checked : xplm_Menu_Unchecked);
        XPLMCheckMenuItem(m_intervalMenu, m_intervalItem_1Hz, 
                         (currentInterval <= 1.01f && currentInterval >= 0.99f) ? xplm_Menu_Checked : xplm_Menu_Unchecked);
    }
}

void UIManager::ShowNotification(const std::string& message) {
    m_notificationMessage = message;
    m_notificationTime = NOTIFICATION_DURATION;
    LogInfo(message);
}

// Unified menu callback
void UIManager::MenuCallback(void* menuRef, void* itemRef) {
    (void)menuRef;  // Unused
    int item = reinterpret_cast<intptr_t>(itemRef);
    
    // Main menu items
    if (item == 0) {
        // Auto mode toggle
        bool newMode = !Settings::Instance().GetAutoMode();
        Settings::Instance().SetAutoMode(newMode);
        Settings::Instance().Save();
        UIManager::Instance().UpdateMenu();
        UIManager::Instance().ShowNotification("Auto mode " + std::string(newMode ? "enabled" : "disabled"));
    }
    else if (item == 1) {
        // Start/Stop recording
        if (Recorder::Instance().IsRecording()) {
            Recorder::Instance().Stop();
            UIManager::Instance().ShowNotification("Recording stopped");
        } else {
            Recorder::Instance().Start();
            UIManager::Instance().ShowNotification("Recording started");
        }
        UIManager::Instance().UpdateMenu();
    }
    else if (item == 2) {
        // Show status
        UIManager::Instance().ToggleStatusWindow();
    }
    else if (item == 3) {
        // Open folder
        UIManager::Instance().OpenOutputFolder();
    }
    else if (item == 4) {
        // Settings
        UIManager::Instance().ToggleSettingsWindow();
    }
    // Recording level submenu items (10-12)
    else if (item >= 10 && item <= 12) {
        RecordingLevel level;
        std::string levelName;
        
        if (item == 10) {
            level = RecordingLevel::Simple;
            levelName = "Simple";
        } else if (item == 11) {
            level = RecordingLevel::Normal;
            levelName = "Normal";
        } else {
            level = RecordingLevel::Detailed;
            levelName = "Detailed";
        }
        
        Settings::Instance().SetRecordingLevel(level);
        DatarefManager::Instance().Reload();
        Settings::Instance().Save();
        UIManager::Instance().UpdateMenu();
        UIManager::Instance().ShowNotification("Recording level: " + levelName);
    }
    // Recording interval submenu items (20-23)
    else if (item >= 20 && item <= 23) {
        float interval;
        std::string name;
        
        switch (item) {
            case 20: interval = 0.05f; name = "20 Hz"; break;
            case 21: interval = 0.10f; name = "10 Hz"; break;
            case 22: interval = 0.25f; name = "4 Hz"; break;
            case 23: interval = 1.0f; name = "1 Hz"; break;
            default: return;
        }
        
        Settings::Instance().SetRecordingInterval(interval);
        Settings::Instance().Save();
        UIManager::Instance().UpdateMenu();
        UIManager::Instance().ShowNotification("Recording interval: " + name);
    }
}

void UIManager::OpenOutputFolder() {
    std::string path = Settings::Instance().GetOutputDirectory();
    
#ifdef _WIN32
    // Windows: Use ShellExecuteA which is safe from command injection
    ShellExecuteA(nullptr, "open", path.c_str(), nullptr, nullptr, SW_SHOWNORMAL);
#elif __APPLE__
    // macOS: Use open command through system() with proper escaping
    // Replace any single quotes with '\'' to escape them properly
    std::string escaped_path = path;
    size_t pos = 0;
    while ((pos = escaped_path.find('\'', pos)) != std::string::npos) {
        escaped_path.replace(pos, 1, "'\\''");
        pos += 4;
    }
    std::string cmd = "open '" + escaped_path + "'";
    int result = system(cmd.c_str());
    (void)result;  // Unused
#else
    // Linux: Use xdg-open with proper escaping
    std::string escaped_path = path;
    size_t pos = 0;
    while ((pos = escaped_path.find('\'', pos)) != std::string::npos) {
        escaped_path.replace(pos, 1, "'\\''");
        pos += 4;
    }
    std::string cmd = "xdg-open '" + escaped_path + "'";
    int result = system(cmd.c_str());
    (void)result;  // Unused
#endif
    
    ShowNotification("Opening output folder");
}

// Status window using X-Plane native API
void UIManager::InitImGui() {
    // We use X-Plane's native window API instead of ImGui for better compatibility
    m_imguiInitialized = true;
    LogInfo("Native window system initialized");
}

void UIManager::CleanupImGui() {
    if (m_imguiWindow) {
        XPLMDestroyWindow(m_imguiWindow);
        m_imguiWindow = nullptr;
    }
    if (m_settingsWindow) {
        XPLMDestroyWindow(m_settingsWindow);
        m_settingsWindow = nullptr;
    }
    m_imguiInitialized = false;
}

void UIManager::CreateImGuiWindow() {
    if (m_imguiWindow) {
        // Window already exists, just show it
        XPLMSetWindowIsVisible(m_imguiWindow, 1);
        return;
    }
    
    // Get screen bounds
    int screenLeft, screenTop, screenRight, screenBottom;
    XPLMGetScreenBoundsGlobal(&screenLeft, &screenTop, &screenRight, &screenBottom);
    
    // Create a window in the center of the screen
    int winWidth = 350;
    int winHeight = 200;
    int left = screenLeft + (screenRight - screenLeft - winWidth) / 2;
    int top = screenTop - 100;
    int right = left + winWidth;
    int bottom = top - winHeight;
    
    // Create window parameters
    XPLMCreateWindow_t params;
    memset(&params, 0, sizeof(params));
    params.structSize = sizeof(params);
    params.left = left;
    params.top = top;
    params.right = right;
    params.bottom = bottom;
    params.visible = 1;
    params.drawWindowFunc = StatusWindowDraw;
    params.handleMouseClickFunc = StatusWindowClick;
    params.handleKeyFunc = StatusWindowKey;
    params.handleCursorFunc = StatusWindowCursor;
    params.handleMouseWheelFunc = StatusWindowWheel;
    params.refcon = this;
    params.decorateAsFloatingWindow = xplm_WindowDecorationRoundRectangle;
    params.layer = xplm_WindowLayerFloatingWindows;
    params.handleRightClickFunc = StatusWindowClick;
    
    m_imguiWindow = XPLMCreateWindowEx(&params);
    
    if (m_imguiWindow) {
        XPLMSetWindowTitle(m_imguiWindow, "XBlackBox Status");
        XPLMSetWindowResizingLimits(m_imguiWindow, 300, 150, 500, 400);
    }
}

void UIManager::UpdateImGuiInputs() {
    // Not needed for native windows
}

void UIManager::RenderImGui() {
    // Not needed - native windows handle their own drawing
}

void UIManager::DrawStatusWindow() {
    // This is called from the native window draw callback
    // Drawing is handled in StatusWindowDraw
}

// Toggle status window visibility
void UIManager::ToggleStatusWindow() {
    m_showStatusWindow = !m_showStatusWindow;
    
    if (m_showStatusWindow) {
        CreateImGuiWindow();
    } else if (m_imguiWindow) {
        XPLMSetWindowIsVisible(m_imguiWindow, 0);
    }
}

// Native window callbacks
static void StatusWindowDraw(XPLMWindowID inWindowID, void* inRefcon) {
    (void)inRefcon;
    
    // Get window geometry
    int left, top, right, bottom;
    XPLMGetWindowGeometry(inWindowID, &left, &top, &right, &bottom);
    
    // Set up drawing color (white text)
    float white[] = {1.0f, 1.0f, 1.0f};
    float green[] = {0.0f, 1.0f, 0.0f};
    float red[] = {1.0f, 0.3f, 0.3f};
    float yellow[] = {1.0f, 1.0f, 0.3f};
    
    int x = left + 10;
    int y = top - 25;
    int lineHeight = 18;
    
    // Title
    XPLMDrawString(white, x, y, (char*)"=== XBlackBox Status ===", nullptr, xplmFont_Proportional);
    y -= lineHeight + 5;
    
    // Recording status
    bool isRecording = Recorder::Instance().IsRecording();
    char buffer[256];
    
    snprintf(buffer, sizeof(buffer), "Recording: %s", isRecording ? "YES" : "NO");
    XPLMDrawString(isRecording ? green : red, x, y, buffer, nullptr, xplmFont_Proportional);
    y -= lineHeight;
    
    // Auto mode
    bool autoMode = Settings::Instance().GetAutoMode();
    snprintf(buffer, sizeof(buffer), "Auto Mode: %s", autoMode ? "ON" : "OFF");
    XPLMDrawString(autoMode ? green : yellow, x, y, buffer, nullptr, xplmFont_Proportional);
    y -= lineHeight;
    
    // Recording level
    snprintf(buffer, sizeof(buffer), "Level: %s", Settings::Instance().GetRecordingLevelName().c_str());
    XPLMDrawString(white, x, y, buffer, nullptr, xplmFont_Proportional);
    y -= lineHeight;
    
    // Recording interval
    snprintf(buffer, sizeof(buffer), "Interval: %.2f Hz", 1.0f / Settings::Instance().GetRecordingInterval());
    XPLMDrawString(white, x, y, buffer, nullptr, xplmFont_Proportional);
    y -= lineHeight;
    
    // If recording, show additional stats
    if (isRecording) {
        y -= 5;  // Extra spacing
        XPLMDrawString(white, x, y, (char*)"--- Recording Stats ---", nullptr, xplmFont_Proportional);
        y -= lineHeight;
        
        snprintf(buffer, sizeof(buffer), "Records: %d", Recorder::Instance().GetRecordCount());
        XPLMDrawString(green, x, y, buffer, nullptr, xplmFont_Proportional);
        y -= lineHeight;
        
        snprintf(buffer, sizeof(buffer), "Duration: %d sec", Recorder::Instance().GetDuration());
        XPLMDrawString(green, x, y, buffer, nullptr, xplmFont_Proportional);
        y -= lineHeight;
        
        snprintf(buffer, sizeof(buffer), "Bytes: %zu", Recorder::Instance().GetBytesWritten());
        XPLMDrawString(green, x, y, buffer, nullptr, xplmFont_Proportional);
        y -= lineHeight;
        
        // Truncate file path if too long
        std::string filePath = Recorder::Instance().GetCurrentFilePath();
        if (filePath.length() > 40) {
            filePath = "..." + filePath.substr(filePath.length() - 37);
        }
        snprintf(buffer, sizeof(buffer), "File: %s", filePath.c_str());
        XPLMDrawString(white, x, y, buffer, nullptr, xplmFont_Proportional);
    }
}

static int StatusWindowClick(XPLMWindowID inWindowID, int x, int y, XPLMMouseStatus status, void* inRefcon) {
    (void)inWindowID;
    (void)x;
    (void)y;
    (void)status;
    (void)inRefcon;
    return 1;  // Consume the click
}

static void StatusWindowKey(XPLMWindowID inWindowID, char key, XPLMKeyFlags flags, char vkey, void* inRefcon, int losingFocus) {
    (void)inWindowID;
    (void)key;
    (void)flags;
    (void)vkey;
    (void)inRefcon;
    (void)losingFocus;
}

static XPLMCursorStatus StatusWindowCursor(XPLMWindowID inWindowID, int x, int y, void* inRefcon) {
    (void)inWindowID;
    (void)x;
    (void)y;
    (void)inRefcon;
    return xplm_CursorDefault;
}

static int StatusWindowWheel(XPLMWindowID inWindowID, int x, int y, int wheel, int clicks, void* inRefcon) {
    (void)inWindowID;
    (void)x;
    (void)y;
    (void)wheel;
    (void)clicks;
    (void)inRefcon;
    return 1;  // Consume the wheel event
}

// Settings window implementation
void UIManager::CreateSettingsWindow() {
    if (m_settingsWindow) {
        // Window already exists, just show it
        XPLMSetWindowIsVisible(m_settingsWindow, 1);
        return;
    }
    
    // Get screen bounds
    int screenLeft, screenTop, screenRight, screenBottom;
    XPLMGetScreenBoundsGlobal(&screenLeft, &screenTop, &screenRight, &screenBottom);
    
    // Create a window in the center of the screen
    int winWidth = 450;
    int winHeight = 400;
    int left = screenLeft + (screenRight - screenLeft - winWidth) / 2;
    int top = screenTop - 100;
    int right = left + winWidth;
    int bottom = top - winHeight;
    
    // Create window parameters
    XPLMCreateWindow_t params;
    memset(&params, 0, sizeof(params));
    params.structSize = sizeof(params);
    params.left = left;
    params.top = top;
    params.right = right;
    params.bottom = bottom;
    params.visible = 1;
    params.drawWindowFunc = SettingsWindowDraw;
    params.handleMouseClickFunc = SettingsWindowClick;
    params.handleKeyFunc = SettingsWindowKey;
    params.handleCursorFunc = SettingsWindowCursor;
    params.handleMouseWheelFunc = SettingsWindowWheel;
    params.refcon = this;
    params.decorateAsFloatingWindow = xplm_WindowDecorationRoundRectangle;
    params.layer = xplm_WindowLayerFloatingWindows;
    params.handleRightClickFunc = SettingsWindowClick;
    
    m_settingsWindow = XPLMCreateWindowEx(&params);
    
    if (m_settingsWindow) {
        XPLMSetWindowTitle(m_settingsWindow, "XBlackBox Settings");
        XPLMSetWindowResizingLimits(m_settingsWindow, 400, 350, 600, 600);
    }
}

void UIManager::ToggleSettingsWindow() {
    m_showSettingsWindow = !m_showSettingsWindow;
    
    if (m_showSettingsWindow) {
        CreateSettingsWindow();
    } else if (m_settingsWindow) {
        XPLMSetWindowIsVisible(m_settingsWindow, 0);
    }
}

// Settings window draw callback
static void SettingsWindowDraw(XPLMWindowID inWindowID, void* inRefcon) {
    (void)inRefcon;
    
    // Get window geometry
    int left, top, right, bottom;
    XPLMGetWindowGeometry(inWindowID, &left, &top, &right, &bottom);
    
    // Set up drawing colors
    float white[] = {1.0f, 1.0f, 1.0f};
    float green[] = {0.0f, 1.0f, 0.0f};
    float yellow[] = {1.0f, 1.0f, 0.3f};
    float gray[] = {0.7f, 0.7f, 0.7f};
    
    int x = left + 10;
    int y = top - 25;
    int lineHeight = 20;
    
    // Title
    XPLMDrawString(white, x, y, (char*)"=== XBlackBox Settings ===", nullptr, xplmFont_Proportional);
    y -= lineHeight + 10;
    
    // Recording Level
    XPLMDrawString(yellow, x, y, (char*)"Recording Level:", nullptr, xplmFont_Proportional);
    y -= lineHeight;
    XPLMDrawString(gray, x + 10, y, (char*)"Use menu to change", nullptr, xplmFont_Proportional);
    y -= lineHeight - 5;
    
    char buffer[256];
    snprintf(buffer, sizeof(buffer), "  Current: %s", Settings::Instance().GetRecordingLevelName().c_str());
    XPLMDrawString(green, x + 10, y, buffer, nullptr, xplmFont_Proportional);
    y -= lineHeight + 5;
    
    // Recording Interval
    XPLMDrawString(yellow, x, y, (char*)"Recording Interval:", nullptr, xplmFont_Proportional);
    y -= lineHeight;
    XPLMDrawString(gray, x + 10, y, (char*)"Use menu to change", nullptr, xplmFont_Proportional);
    y -= lineHeight - 5;
    
    float hz = 1.0f / Settings::Instance().GetRecordingInterval();
    snprintf(buffer, sizeof(buffer), "  Current: %.0f Hz (%.2f sec)", hz, Settings::Instance().GetRecordingInterval());
    XPLMDrawString(green, x + 10, y, buffer, nullptr, xplmFont_Proportional);
    y -= lineHeight + 10;
    
    // Auto Mode
    XPLMDrawString(yellow, x, y, (char*)"Auto Recording Mode:", nullptr, xplmFont_Proportional);
    y -= lineHeight;
    
    bool autoMode = Settings::Instance().GetAutoMode();
    snprintf(buffer, sizeof(buffer), "  Auto Mode: %s", autoMode ? "ON" : "OFF");
    XPLMDrawString(autoMode ? green : white, x + 10, y, buffer, nullptr, xplmFont_Proportional);
    y -= lineHeight;
    
    if (autoMode) {
        // Auto Start Condition
        AutoCondition startCond = Settings::Instance().GetAutoStartCondition();
        const char* startCondName = "Ground Speed";
        const char* startOp = ">";
        if (startCond == AutoCondition::EngineRunning) {
            startCondName = "Engine Running";
            startOp = "=";
        } else if (startCond == AutoCondition::WeightOnWheels) {
            startCondName = "Weight on Wheels";
            startOp = "=";
        }
        
        float startThreshold = Settings::Instance().GetAutoStartThreshold();
        snprintf(buffer, sizeof(buffer), "  Start: %s %s %.1f", startCondName, startOp, startThreshold);
        XPLMDrawString(white, x + 10, y, buffer, nullptr, xplmFont_Proportional);
        y -= lineHeight;
        
        // Auto Stop Condition
        AutoCondition stopCond = Settings::Instance().GetAutoStopCondition();
        const char* stopCondName = "Ground Speed";
        const char* stopOp = "<";
        if (stopCond == AutoCondition::EngineRunning) {
            stopCondName = "Engine Running";
            stopOp = "=";
        } else if (stopCond == AutoCondition::WeightOnWheels) {
            stopCondName = "Weight on Wheels";
            stopOp = "=";
        }
        
        float stopThreshold = Settings::Instance().GetAutoStopThreshold();
        float stopDelay = Settings::Instance().GetAutoStopDelay();
        snprintf(buffer, sizeof(buffer), "  Stop: %s %s %.1f (delay: %.0fs)", stopCondName, stopOp, stopThreshold, stopDelay);
        XPLMDrawString(white, x + 10, y, buffer, nullptr, xplmFont_Proportional);
        y -= lineHeight;
    }
    
    y -= 10;
    
    // Instructions
    XPLMDrawString(gray, x, y, (char*)"Use the menu to adjust settings.", nullptr, xplmFont_Proportional);
    y -= lineHeight;
    XPLMDrawString(gray, x, y, (char*)"Changes are saved automatically.", nullptr, xplmFont_Proportional);
    y -= lineHeight + 10;
    
    // Output Directory
    XPLMDrawString(yellow, x, y, (char*)"Output Directory:", nullptr, xplmFont_Proportional);
    y -= lineHeight;
    
    std::string outDir = Settings::Instance().GetOutputDirectory();
    if (outDir.length() > 50) {
        outDir = "..." + outDir.substr(outDir.length() - 47);
    }
    snprintf(buffer, sizeof(buffer), "  %s", outDir.c_str());
    XPLMDrawString(white, x + 5, y, buffer, nullptr, xplmFont_Proportional);
    y -= lineHeight + 5;
    
    // File prefix
    XPLMDrawString(yellow, x, y, (char*)"File Prefix:", nullptr, xplmFont_Proportional);
    y -= lineHeight;
    snprintf(buffer, sizeof(buffer), "  %s", Settings::Instance().GetFilePrefix().c_str());
    XPLMDrawString(white, x + 5, y, buffer, nullptr, xplmFont_Proportional);
    
    // Note at bottom
    y = bottom + 30;
    XPLMDrawString(gray, x, y, (char*)"Note: This window shows current settings.", nullptr, xplmFont_Proportional);
    y -= lineHeight - 5;
    XPLMDrawString(gray, x, y, (char*)"Use the XBlackBox menu to modify them.", nullptr, xplmFont_Proportional);
}

static int SettingsWindowClick(XPLMWindowID inWindowID, int x, int y, XPLMMouseStatus status, void* inRefcon) {
    (void)inWindowID;
    (void)x;
    (void)y;
    (void)status;
    (void)inRefcon;
    return 1;  // Consume the click
}

static void SettingsWindowKey(XPLMWindowID inWindowID, char key, XPLMKeyFlags flags, char vkey, void* inRefcon, int losingFocus) {
    (void)inWindowID;
    (void)key;
    (void)flags;
    (void)vkey;
    (void)inRefcon;
    (void)losingFocus;
}

static XPLMCursorStatus SettingsWindowCursor(XPLMWindowID inWindowID, int x, int y, void* inRefcon) {
    (void)inWindowID;
    (void)x;
    (void)y;
    (void)inRefcon;
    return xplm_CursorDefault;
}

static int SettingsWindowWheel(XPLMWindowID inWindowID, int x, int y, int wheel, int clicks, void* inRefcon) {
    (void)inWindowID;
    (void)x;
    (void)y;
    (void)wheel;
    (void)clicks;
    (void)inRefcon;
    return 1;  // Consume the wheel event
}
