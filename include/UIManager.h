#pragma once

#include "common.h"
#include "Settings.h"
#include "Recorder.h"

class UIManager {
public:
    // Singleton access
    static UIManager& Instance();
    
    // Initialize UI
    void Init();
    
    // Cleanup UI
    void Cleanup();
    
    // Update (called every frame)
    void Update();
    
    // Draw UI (called every frame)
    void Draw();
    
private:
    UIManager();
    ~UIManager() = default;
    UIManager(const UIManager&) = delete;
    UIManager& operator=(const UIManager&) = delete;
    
    // Menu management
    void CreateMenu();
    void UpdateMenu();
    
    // Menu callbacks
    static void MenuCallback_AutoMode(void* menuRef, void* itemRef);
    static void MenuCallback_StartStop(void* menuRef, void* itemRef);
    static void MenuCallback_LevelSimple(void* menuRef, void* itemRef);
    static void MenuCallback_LevelNormal(void* menuRef, void* itemRef);
    static void MenuCallback_LevelDetailed(void* menuRef, void* itemRef);
    static void MenuCallback_Interval20Hz(void* menuRef, void* itemRef);
    static void MenuCallback_Interval10Hz(void* menuRef, void* itemRef);
    static void MenuCallback_Interval4Hz(void* menuRef, void* itemRef);
    static void MenuCallback_Interval1Hz(void* menuRef, void* itemRef);
    static void MenuCallback_ShowStatus(void* menuRef, void* itemRef);
    static void MenuCallback_OpenFolder(void* menuRef, void* itemRef);
    
    // ImGui windows
    void DrawStatusWindow();
    
    // Helper for opening output folder
    void OpenOutputFolder();
    
    // Menu items
    XPLMMenuID m_menuID;
    int m_menuItem_AutoMode;
    int m_menuItem_StartStop;
    int m_menuItem_ShowStatus;
    
    // UI state
    bool m_showStatusWindow;
    
    // Notification system
    void ShowNotification(const std::string& message);
    std::string m_notificationMessage;
    float m_notificationTime;
    static constexpr float NOTIFICATION_DURATION = 3.0f;
};
