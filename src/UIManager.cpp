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

UIManager& UIManager::Instance() {
    static UIManager instance;
    return instance;
}

UIManager::UIManager()
    : m_menuID(nullptr)
    , m_menuItem_AutoMode(-1)
    , m_menuItem_StartStop(-1)
    , m_menuItem_ShowStatus(-1)
    , m_showStatusWindow(false)
    , m_notificationTime(0.0f)
    , m_imguiInitialized(false)
    , m_imguiWindow(nullptr) {
}

void UIManager::Init() {
    CreateMenu();
    InitImGui();
    LogInfo("UI initialized");
}

void UIManager::Cleanup() {
    CleanupImGui();
    
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
    
    // Create our submenu with menu handler
    int menuIndex = XPLMAppendMenuItem(pluginsMenu, "XBlackBox", nullptr, 0);
    m_menuID = XPLMCreateMenu("XBlackBox", pluginsMenu, menuIndex, 
                               MenuCallback_AutoMode, nullptr);
    
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
    XPLMMenuID levelMenu = XPLMCreateMenu("Recording Level", m_menuID, levelMenuItem,
                                           MenuCallback_LevelSimple, nullptr);
    XPLMAppendMenuItem(levelMenu, "Simple (Basic flight data)", 
                       reinterpret_cast<void*>(1), 0);
    XPLMAppendMenuItem(levelMenu, "Normal (+ Controls & systems)", 
                       reinterpret_cast<void*>(2), 0);
    XPLMAppendMenuItem(levelMenu, "Detailed (Everything)", 
                       reinterpret_cast<void*>(3), 0);
    
    // Recording interval submenu
    int intervalMenuItem = XPLMAppendMenuItem(m_menuID, "Recording Interval", nullptr, 0);
    XPLMMenuID intervalMenu = XPLMCreateMenu("Recording Interval", m_menuID, intervalMenuItem,
                                              MenuCallback_Interval20Hz, nullptr);
    XPLMAppendMenuItem(intervalMenu, "20 Hz (0.05 sec) - Very Fast", 
                       reinterpret_cast<void*>(20), 0);
    XPLMAppendMenuItem(intervalMenu, "10 Hz (0.10 sec) - Fast", 
                       reinterpret_cast<void*>(10), 0);
    XPLMAppendMenuItem(intervalMenu, "4 Hz (0.25 sec) - Normal", 
                       reinterpret_cast<void*>(4), 0);
    XPLMAppendMenuItem(intervalMenu, "1 Hz (1.0 sec) - Slow", 
                       reinterpret_cast<void*>(1), 0);
    
    // Separator
    XPLMAppendMenuSeparator(m_menuID);
    
    // Show status
    m_menuItem_ShowStatus = XPLMAppendMenuItem(m_menuID, "Show Status", 
                                                reinterpret_cast<void*>(2), 0);
    
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
}

void UIManager::ShowNotification(const std::string& message) {
    m_notificationMessage = message;
    m_notificationTime = NOTIFICATION_DURATION;
    LogInfo(message);
}

// Menu callbacks
void UIManager::MenuCallback_AutoMode(void* menuRef, void* itemRef) {
    (void)menuRef;  // Unused
    int item = reinterpret_cast<intptr_t>(itemRef);
    
    // Auto mode toggle
    if (item == 0) {
        bool newMode = !Settings::Instance().GetAutoMode();
        Settings::Instance().SetAutoMode(newMode);
        Settings::Instance().Save();
        UIManager::Instance().UpdateMenu();
        UIManager::Instance().ShowNotification("Auto mode " + std::string(newMode ? "enabled" : "disabled"));
    }
    // Start/Stop recording
    else if (item == 1) {
        if (Recorder::Instance().IsRecording()) {
            Recorder::Instance().Stop();
            UIManager::Instance().ShowNotification("Recording stopped");
        } else {
            Recorder::Instance().Start();
            UIManager::Instance().ShowNotification("Recording started");
        }
        UIManager::Instance().UpdateMenu();
    }
    // Show status
    else if (item == 2) {
        UIManager::Instance().ToggleStatusWindow();
    }
    // Open folder
    else if (item == 3) {
        UIManager::Instance().OpenOutputFolder();
    }
}

void UIManager::MenuCallback_LevelSimple(void* menuRef, void* itemRef) {
    (void)menuRef;  // Unused
    int item = reinterpret_cast<intptr_t>(itemRef);
    
    RecordingLevel level;
    std::string levelName;
    
    if (item == 1) {
        level = RecordingLevel::Simple;
        levelName = "Simple";
    } else if (item == 2) {
        level = RecordingLevel::Normal;
        levelName = "Normal";
    } else if (item == 3) {
        level = RecordingLevel::Detailed;
        levelName = "Detailed";
    } else {
        return;
    }
    
    Settings::Instance().SetRecordingLevel(level);
    DatarefManager::Instance().Reload();
    Settings::Instance().Save();
    UIManager::Instance().ShowNotification("Recording level: " + levelName);
}

void UIManager::MenuCallback_LevelNormal(void* menuRef, void* itemRef) {
    MenuCallback_LevelSimple(menuRef, itemRef);
}

void UIManager::MenuCallback_LevelDetailed(void* menuRef, void* itemRef) {
    MenuCallback_LevelSimple(menuRef, itemRef);
}

void UIManager::MenuCallback_Interval20Hz(void* menuRef, void* itemRef) {
    (void)menuRef;  // Unused
    int hz = reinterpret_cast<intptr_t>(itemRef);
    float interval;
    std::string name;
    
    switch (hz) {
        case 20: interval = 0.05f; name = "20 Hz"; break;
        case 10: interval = 0.10f; name = "10 Hz"; break;
        case 4: interval = 0.25f; name = "4 Hz"; break;
        case 1: interval = 1.0f; name = "1 Hz"; break;
        default: return;
    }
    
    Settings::Instance().SetRecordingInterval(interval);
    Settings::Instance().Save();
    UIManager::Instance().ShowNotification("Recording interval: " + name);
}

void UIManager::MenuCallback_Interval10Hz(void* menuRef, void* itemRef) {
    MenuCallback_Interval20Hz(menuRef, itemRef);
}

void UIManager::MenuCallback_Interval4Hz(void* menuRef, void* itemRef) {
    MenuCallback_Interval20Hz(menuRef, itemRef);
}

void UIManager::MenuCallback_Interval1Hz(void* menuRef, void* itemRef) {
    MenuCallback_Interval20Hz(menuRef, itemRef);
}

void UIManager::MenuCallback_ShowStatus(void* menuRef, void* itemRef) {
    (void)menuRef;  // Unused
    (void)itemRef;  // Unused
    UIManager::Instance().m_showStatusWindow = !UIManager::Instance().m_showStatusWindow;
}

void UIManager::MenuCallback_OpenFolder(void* menuRef, void* itemRef) {
    (void)menuRef;  // Unused
    (void)itemRef;  // Unused
    UIManager::Instance().OpenOutputFolder();
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
