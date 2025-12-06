#include "UIManager.h"

#ifdef _WIN32
#include <windows.h>
#include <shellapi.h>
#elif __APPLE__
#include <stdlib.h>
#else
#include <stdlib.h>
#endif

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
    , m_notificationTime(0.0f) {
}

void UIManager::Init() {
    CreateMenu();
    LogInfo("UI initialized");
}

void UIManager::Cleanup() {
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
    // Draw status window if visible
    if (m_showStatusWindow) {
        DrawStatusWindow();
    }
    
    // Draw notification if active
    if (m_notificationTime > 0.0f && !m_notificationMessage.empty()) {
        // Simple text notification (could be enhanced with ImGui)
        // For now, we'll just use X-Plane's debug string
        // In a full implementation, we'd draw an ImGui notification
    }
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

void UIManager::DrawStatusWindow() {
    // Simple status display using ImGui
    ImGui::Begin("XBlackBox Status", &m_showStatusWindow);
    
    ImGui::Text("Recording: %s", Recorder::Instance().IsRecording() ? "YES" : "NO");
    ImGui::Text("Auto Mode: %s", Settings::Instance().GetAutoMode() ? "ON" : "OFF");
    ImGui::Text("Level: %s", Settings::Instance().GetRecordingLevelName().c_str());
    ImGui::Text("Interval: %.2f Hz", 1.0f / Settings::Instance().GetRecordingInterval());
    
    if (Recorder::Instance().IsRecording()) {
        ImGui::Separator();
        ImGui::Text("Records: %d", Recorder::Instance().GetRecordCount());
        ImGui::Text("Duration: %d sec", Recorder::Instance().GetDuration());
        ImGui::Text("Bytes: %zu", Recorder::Instance().GetBytesWritten());
        ImGui::Text("File: %s", Recorder::Instance().GetCurrentFilePath().c_str());
    }
    
    ImGui::End();
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
        UIManager::Instance().m_showStatusWindow = !UIManager::Instance().m_showStatusWindow;
    }
    // Open folder
    else if (item == 3) {
        std::string path = Settings::Instance().GetOutputDirectory();
        
#ifdef _WIN32
        ShellExecuteA(nullptr, "open", path.c_str(), nullptr, nullptr, SW_SHOWNORMAL);
#elif __APPLE__
        std::string cmd = "open \"" + path + "\"";
        system(cmd.c_str());
#else
        std::string cmd = "xdg-open \"" + path + "\"";
        system(cmd.c_str());
#endif
        
        UIManager::Instance().ShowNotification("Opening output folder");
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
    std::string path = Settings::Instance().GetOutputDirectory();
    
#ifdef _WIN32
    ShellExecuteA(nullptr, "open", path.c_str(), nullptr, nullptr, SW_SHOWNORMAL);
#elif __APPLE__
    std::string cmd = "open \"" + path + "\"";
    system(cmd.c_str());
#else
    std::string cmd = "xdg-open \"" + path + "\"";
    system(cmd.c_str());
#endif
    
    UIManager::Instance().ShowNotification("Opening output folder");
}
