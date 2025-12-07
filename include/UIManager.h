#pragma once

#include "common.h"
#include "Settings.h"
#include "Recorder.h"
#include "DatarefManager.h"

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
    
    // Render ImGui (called from draw callback)
    void RenderImGui();
    
private:
    UIManager();
    ~UIManager() = default;
    UIManager(const UIManager&) = delete;
    UIManager& operator=(const UIManager&) = delete;
    
    // Menu management
    void CreateMenu();
    void UpdateMenu();
    
    // ImGui management
    void InitImGui();
    void CleanupImGui();
    void CreateImGuiWindow();
    void UpdateImGuiInputs();
    
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
    void ToggleStatusWindow();
    
    // Helper for opening output folder
    void OpenOutputFolder();
    
    // Menu items
    XPLMMenuID m_menuID;
    int m_menuItem_AutoMode;
    int m_menuItem_StartStop;
    int m_menuItem_ShowStatus;
    
    // UI state
    bool m_showStatusWindow;
    
    // ImGui state
    bool m_imguiInitialized;
    XPLMWindowID m_imguiWindow;
    
    // Notification system
    void ShowNotification(const std::string& message);
    std::string m_notificationMessage;
    float m_notificationTime;
    static constexpr float NOTIFICATION_DURATION = 3.0f;
};
