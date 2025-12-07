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
    
    // Unified menu callback
    static void MenuCallback(void* menuRef, void* itemRef);
    
    // Windows
    void DrawStatusWindow();
    void ToggleStatusWindow();
    void ToggleSettingsWindow();
    void CreateSettingsWindow();
    
    // Helper for opening output folder
    void OpenOutputFolder();
    
    // Menu items
    XPLMMenuID m_menuID;
    XPLMMenuID m_levelMenu;
    XPLMMenuID m_intervalMenu;
    int m_menuItem_AutoMode;
    int m_menuItem_StartStop;
    int m_menuItem_ShowStatus;
    int m_menuItem_Settings;
    
    // Submenu items for checkmarks
    int m_levelItem_Simple;
    int m_levelItem_Normal;
    int m_levelItem_Detailed;
    int m_intervalItem_20Hz;
    int m_intervalItem_10Hz;
    int m_intervalItem_4Hz;
    int m_intervalItem_1Hz;
    
    // UI state
    bool m_showStatusWindow;
    bool m_showSettingsWindow;
    
    // Window state
    bool m_imguiInitialized;
    XPLMWindowID m_imguiWindow;
    XPLMWindowID m_settingsWindow;
    
    // Notification system
    void ShowNotification(const std::string& message);
    std::string m_notificationMessage;
    float m_notificationTime;
    static constexpr float NOTIFICATION_DURATION = 3.0f;
};
