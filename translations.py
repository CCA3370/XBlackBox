#!/usr/bin/env python3
"""
Internationalization support for XBlackBox XDR Viewer
"""

import locale
from typing import Dict

# Translation dictionaries
TRANSLATIONS = {
    'en_US': {
        # Window title
        'window_title': 'XBlackBox XDR Viewer - Modern Edition',
        
        # Menu items
        'menu_file': '&File',
        'menu_view': '&View',
        'menu_analysis': '&Analysis',
        'menu_help': '&Help',
        'menu_theme': '&Theme',
        'menu_language': '&Language',
        
        # File menu
        'action_open': '&Open XDR File...',
        'action_recent': 'Recent Files',
        'action_export_csv': 'Export to &CSV...',
        'action_save_plot': 'Save Plot &Image...',
        'action_exit': 'E&xit',
        'no_recent_files': 'No recent files',
        
        # View menu
        'action_refresh': '&Refresh Plot',
        'action_clear_plot': '&Clear Plot',
        'action_zoom_in': 'Zoom &In',
        'action_zoom_out': 'Zoom &Out',
        
        # Analysis menu
        'action_statistics': 'Show &Statistics',
        'action_fft': 'Show &Frequency Analysis',
        'action_3d_path': 'Show &3D Flight Path',
        
        # Theme menu
        'theme_dark': 'Dark Theme',
        'theme_light': 'Light Theme',
        'theme_high_contrast': 'High Contrast',
        
        # Language menu
        'lang_english': 'English',
        'lang_chinese': '中文 (Chinese)',
        'lang_system': 'Follow System',
        
        # Help menu
        'action_shortcuts': '&Keyboard Shortcuts',
        'action_about': '&About',
        
        # Toolbar
        'toolbar_open': 'Open',
        'toolbar_export': 'Export CSV',
        
        # File info
        'file_info_no_file': 'No file loaded',
        'file_info_title': 'Open an XDR file to begin',
        'file_info_status_complete': 'Complete',
        'file_info_status_recording': 'Recording...',
        'file_info_level': 'Level:',
        'file_info_interval': 'Interval:',
        'file_info_start': 'Start:',
        'file_info_end': 'End:',
        'file_info_duration': 'Duration:',
        'file_info_frames': 'Frames:',
        'file_info_parameters': 'Parameters:',
        'file_info_size': 'Size:',
        'file_info_in_progress': 'In progress',
        'file_info_ongoing': 'ongoing',
        'file_info_so_far': 'so far',
        
        # Parameters panel
        'param_group_title': 'Parameters to Plot',
        'param_filter': 'Filter:',
        'param_select_all': '✓ Select All',
        'param_clear_all': '✗ Clear All',
        'param_select_all_tooltip': 'Select all visible parameters',
        'param_clear_all_tooltip': 'Deselect all parameters',
        
        # Plot controls
        'time_range_label': '⏱️ Time Range:',
        'time_range_reset': '🔄 Reset',
        'time_range_reset_tooltip': 'Reset to full time range',
        'plot_options_label': '📊 Plot Options:',
        'option_separate_axes': 'Separate Axes',
        'option_separate_axes_tooltip': 'Plot each parameter on its own Y-axis',
        'option_grid': 'Grid',
        'option_grid_tooltip': 'Show grid lines on plots',
        'option_derivative': 'Derivative',
        'option_derivative_tooltip': 'Plot rate of change (d/dt) instead of raw values',
        'option_live_mode': '🔴 Live Mode',
        'option_live_mode_tooltip': 'Monitor recording in real-time',
        'btn_update_plot': '🔄 Update Plot',
        'btn_update_plot_tooltip': 'Refresh plot with current selection (F5)',
        
        # Tab names
        'tab_plot': 'Plot',
        'tab_data_table': 'Data Table',
        'tab_statistics': 'Statistics',
        'tab_correlation': 'Correlation',
        'tab_fft': 'Frequency Analysis',
        'tab_3d_path': '3D Flight Path',
        
        # Statistics
        'stats_title': '📊 Statistical Analysis',
        'stats_refresh': 'Refresh Statistics',
        'stats_parameter': 'Parameter',
        'stats_count': 'Count',
        'stats_min': 'Min',
        'stats_max': 'Max',
        'stats_mean': 'Mean',
        'stats_median': 'Median',
        'stats_std': 'Std Dev',
        'stats_range': 'Range',
        
        # Correlation
        'corr_title': '🔗 Parameter Correlation Analysis',
        'corr_info': 'Correlation coefficient ranges from -1 (negative correlation) to +1 (positive correlation)',
        'corr_refresh': '🔄 Calculate Correlations',
        'corr_refresh_tooltip': 'Calculate correlation matrix for selected parameters',
        'corr_min_params': 'Select at least 2 parameters to analyze correlations',
        
        # FFT
        'fft_title': '📡 Frequency Analysis (FFT)',
        'fft_info': 'Fast Fourier Transform reveals periodic patterns and oscillations in the data',
        'fft_select_param': 'Select Parameter:',
        'fft_analyze': '🔄 Analyze',
        'fft_analyze_tooltip': 'Calculate FFT for selected parameter',
        'fft_no_data': 'No data available. Please select parameters to analyze.',
        'fft_insufficient': '⚠️ Not enough data points for FFT analysis (minimum 4 required)',
        'fft_dominant_freq': 'Dominant Frequency:',
        'fft_period': 'Period:',
        'fft_magnitude': 'Magnitude:',
        
        # 3D Flight Path
        'path3d_title': '✈️ 3D Flight Path',
        'path3d_info': 'Interactive 3D visualization of aircraft trajectory using latitude, longitude, and altitude',
        'path3d_show_markers': 'Show Markers',
        'path3d_show_markers_tooltip': 'Show points along the flight path',
        'path3d_color_altitude': 'Color by Altitude',
        'path3d_color_altitude_tooltip': 'Color the path by altitude (blue=low, red=high)',
        'path3d_update': '🔄 Update',
        'path3d_update_tooltip': 'Refresh 3D flight path',
        'path3d_no_data': '⚠️ No data available',
        'path3d_missing_params': '⚠️ Required parameters not found (latitude, longitude, elevation)',
        'path3d_no_position': '⚠️ No position data available',
        'path3d_summary': 'Flight Path Summary:',
        'path3d_min_alt': 'Min Alt:',
        'path3d_max_alt': 'Max Alt:',
        'path3d_range': 'Range:',
        'path3d_distance': 'Distance:',
        'path3d_start': 'Start',
        'path3d_end': 'End',
        
        # Data table
        'data_show_frames': 'Show frames:',
        'data_to': 'to',
        'data_refresh': 'Refresh',
        'data_frame': 'Frame',
        'data_timestamp': 'Timestamp',
        
        # Status bar
        'status_ready': 'Ready - Open an XDR file or drag & drop to begin 🚀',
        'status_loaded': 'Loaded:',
        'status_frames': 'frames',
        'status_plotting': 'Plotting',
        'status_parameters': 'parameter(s)',
        'status_mode_derivative': 'derivative',
        'status_mode_value': 'value',
        'status_mode': 'mode',
        'status_live_enabled': 'Live mode enabled - refreshing every',
        'status_live_disabled': 'Live mode disabled',
        'status_live': 'Live:',
        'status_recording_complete': 'Recording complete -',
        'status_frames_total': 'frames total',
        'status_exported': 'Exported to:',
        'status_plot_saved': 'Plot saved to:',
        
        # Dialogs
        'dialog_open_title': 'Open XDR File',
        'dialog_export_title': 'Export to CSV',
        'dialog_save_plot_title': 'Save Plot',
        'dialog_file_filter_xdr': 'XDR Files (*.xdr);;All Files (*)',
        'dialog_file_filter_csv': 'CSV Files (*.csv);;All Files (*)',
        'dialog_file_filter_image': 'PNG Image (*.png);;PDF Document (*.pdf);;SVG Image (*.svg)',
        'dialog_error': 'Error',
        'dialog_warning': 'Warning',
        'dialog_success': 'Success',
        'dialog_info': 'Info',
        'error_load_file': 'Failed to open file:',
        'error_export_csv': 'Failed to export:',
        'error_save_plot': 'Failed to save plot:',
        'warning_no_file': 'Please open an XDR file first.',
        'warning_no_data_export': 'No data to export. Please open an XDR file first.',
        'warning_no_plot': 'No plot to save. Please select parameters first.',
        'success_exported': 'Data exported to:',
        'loading_file': 'Loading file...',
        'loading_cancel': 'Cancel',
        
        # About dialog
        'about_title': 'About XBlackBox XDR Viewer',
        'about_version': 'Modern Edition v3.0',
        'about_description': 'A powerful tool for visualizing X-Plane flight data recordings from the XBlackBox plugin.',
        'about_features': 'Key Features',
        'about_performance': 'Performance',
        'about_copyright': '© 2024 XBlackBox Project',
        'about_built_with': 'Built with Python, PySide6, and Matplotlib',
        
        # Other
        'restart_required': 'Please restart the application for language changes to take effect.',
        
        # Keyboard shortcuts
        'shortcuts_title': 'Keyboard Shortcuts',
        'shortcuts_file_ops': 'File Operations',
        'shortcuts_view_ops': 'View Operations',
        'shortcuts_analysis': 'Analysis',
        'shortcuts_help': 'Help',
        
        # Plot labels
        'plot_time': 'Time (seconds)',
        'plot_value': 'Value',
        'plot_rate': 'Rate of Change',
        'plot_frequency': 'Frequency (Hz)',
        'plot_magnitude': 'Magnitude',
        'plot_longitude': 'Longitude',
        'plot_latitude': 'Latitude',
        'plot_altitude': 'Altitude (ft)',
    },
    'zh_CN': {
        # Window title
        'window_title': 'XBlackBox XDR 查看器 - 现代版',
        
        # Menu items
        'menu_file': '文件(&F)',
        'menu_view': '查看(&V)',
        'menu_analysis': '分析(&A)',
        'menu_help': '帮助(&H)',
        'menu_theme': '主题(&T)',
        'menu_language': '语言(&L)',
        
        # File menu
        'action_open': '打开 XDR 文件(&O)...',
        'action_recent': '最近文件',
        'action_export_csv': '导出为 CSV(&C)...',
        'action_save_plot': '保存图表图像(&I)...',
        'action_exit': '退出(&X)',
        'no_recent_files': '无最近文件',
        
        # View menu
        'action_refresh': '刷新图表(&R)',
        'action_clear_plot': '清除图表(&C)',
        'action_zoom_in': '放大(&I)',
        'action_zoom_out': '缩小(&O)',
        
        # Analysis menu
        'action_statistics': '显示统计信息(&S)',
        'action_fft': '显示频率分析(&F)',
        'action_3d_path': '显示 3D 飞行路径(&3)',
        
        # Theme menu
        'theme_dark': '深色主题',
        'theme_light': '浅色主题',
        'theme_high_contrast': '高对比度',
        
        # Language menu
        'lang_english': 'English',
        'lang_chinese': '中文 (Chinese)',
        'lang_system': '跟随系统',
        
        # Help menu
        'action_shortcuts': '键盘快捷键(&K)',
        'action_about': '关于(&A)',
        
        # Toolbar
        'toolbar_open': '打开',
        'toolbar_export': '导出CSV',
        
        # File info
        'file_info_no_file': '未加载文件',
        'file_info_title': '打开 XDR 文件开始',
        'file_info_status_complete': '完成',
        'file_info_status_recording': '记录中...',
        'file_info_level': '级别:',
        'file_info_interval': '间隔:',
        'file_info_start': '开始:',
        'file_info_end': '结束:',
        'file_info_duration': '持续时间:',
        'file_info_frames': '帧数:',
        'file_info_parameters': '参数:',
        'file_info_size': '大小:',
        'file_info_in_progress': '进行中',
        'file_info_ongoing': '进行中',
        'file_info_so_far': '目前为止',
        
        # Parameters panel
        'param_group_title': '要绘制的参数',
        'param_filter': '筛选:',
        'param_select_all': '✓ 全选',
        'param_clear_all': '✗ 清除全部',
        'param_select_all_tooltip': '选择所有可见参数',
        'param_clear_all_tooltip': '取消选择所有参数',
        
        # Plot controls
        'time_range_label': '⏱️ 时间范围:',
        'time_range_reset': '🔄 重置',
        'time_range_reset_tooltip': '重置为完整时间范围',
        'plot_options_label': '📊 绘图选项:',
        'option_separate_axes': '分离坐标轴',
        'option_separate_axes_tooltip': '在单独的Y轴上绘制每个参数',
        'option_grid': '网格',
        'option_grid_tooltip': '在图表上显示网格线',
        'option_derivative': '导数',
        'option_derivative_tooltip': '绘制变化率 (d/dt) 而不是原始值',
        'option_live_mode': '🔴 实时模式',
        'option_live_mode_tooltip': '实时监控记录',
        'btn_update_plot': '🔄 更新图表',
        'btn_update_plot_tooltip': '使用当前选择刷新图表 (F5)',
        
        # Tab names
        'tab_plot': '图表',
        'tab_data_table': '数据表',
        'tab_statistics': '统计',
        'tab_correlation': '相关性',
        'tab_fft': '频率分析',
        'tab_3d_path': '3D 飞行路径',
        
        # Statistics
        'stats_title': '📊 统计分析',
        'stats_refresh': '刷新统计',
        'stats_parameter': '参数',
        'stats_count': '计数',
        'stats_min': '最小值',
        'stats_max': '最大值',
        'stats_mean': '平均值',
        'stats_median': '中位数',
        'stats_std': '标准差',
        'stats_range': '范围',
        
        # Correlation
        'corr_title': '🔗 参数相关性分析',
        'corr_info': '相关系数范围从 -1（负相关）到 +1（正相关）',
        'corr_refresh': '🔄 计算相关性',
        'corr_refresh_tooltip': '计算所选参数的相关性矩阵',
        'corr_min_params': '选择至少 2 个参数来分析相关性',
        
        # FFT
        'fft_title': '📡 频率分析 (FFT)',
        'fft_info': '快速傅里叶变换揭示数据中的周期性模式和振荡',
        'fft_select_param': '选择参数:',
        'fft_analyze': '🔄 分析',
        'fft_analyze_tooltip': '计算所选参数的 FFT',
        'fft_no_data': '无可用数据。请选择要分析的参数。',
        'fft_insufficient': '⚠️ FFT 分析的数据点不足（至少需要 4 个）',
        'fft_dominant_freq': '主频率:',
        'fft_period': '周期:',
        'fft_magnitude': '幅度:',
        
        # 3D Flight Path
        'path3d_title': '✈️ 3D 飞行路径',
        'path3d_info': '使用纬度、经度和高度的飞机轨迹交互式 3D 可视化',
        'path3d_show_markers': '显示标记',
        'path3d_show_markers_tooltip': '显示沿飞行路径的点',
        'path3d_color_altitude': '按高度着色',
        'path3d_color_altitude_tooltip': '按高度为路径着色（蓝色=低，红色=高）',
        'path3d_update': '🔄 更新',
        'path3d_update_tooltip': '刷新 3D 飞行路径',
        'path3d_no_data': '⚠️ 无可用数据',
        'path3d_missing_params': '⚠️ 未找到所需参数（纬度、经度、海拔）',
        'path3d_no_position': '⚠️ 无可用位置数据',
        'path3d_summary': '飞行路径摘要:',
        'path3d_min_alt': '最低高度:',
        'path3d_max_alt': '最高高度:',
        'path3d_range': '范围:',
        'path3d_distance': '距离:',
        'path3d_start': '开始',
        'path3d_end': '结束',
        
        # Data table
        'data_show_frames': '显示帧:',
        'data_to': '到',
        'data_refresh': '刷新',
        'data_frame': '帧',
        'data_timestamp': '时间戳',
        
        # Status bar
        'status_ready': '就绪 - 打开 XDR 文件或拖放开始 🚀',
        'status_loaded': '已加载:',
        'status_frames': '帧',
        'status_plotting': '绘制',
        'status_parameters': '个参数',
        'status_mode_derivative': '导数',
        'status_mode_value': '值',
        'status_mode': '模式',
        'status_live_enabled': '实时模式已启用 - 每',
        'status_live_disabled': '实时模式已禁用',
        'status_live': '实时:',
        'status_recording_complete': '记录完成 -',
        'status_frames_total': '总帧数',
        'status_exported': '导出到:',
        'status_plot_saved': '图表保存到:',
        
        # Dialogs
        'dialog_open_title': '打开 XDR 文件',
        'dialog_export_title': '导出为 CSV',
        'dialog_save_plot_title': '保存图表',
        'dialog_file_filter_xdr': 'XDR 文件 (*.xdr);;所有文件 (*)',
        'dialog_file_filter_csv': 'CSV 文件 (*.csv);;所有文件 (*)',
        'dialog_file_filter_image': 'PNG 图像 (*.png);;PDF 文档 (*.pdf);;SVG 图像 (*.svg)',
        'dialog_error': '错误',
        'dialog_warning': '警告',
        'dialog_success': '成功',
        'dialog_info': '信息',
        'error_load_file': '无法打开文件:',
        'error_export_csv': '无法导出:',
        'error_save_plot': '无法保存图表:',
        'warning_no_file': '请先打开 XDR 文件。',
        'warning_no_data_export': '无要导出的数据。请先打开 XDR 文件。',
        'warning_no_plot': '无要保存的图表。请先选择参数。',
        'success_exported': '数据导出到:',
        'loading_file': '加载文件...',
        'loading_cancel': '取消',
        
        # About dialog
        'about_title': '关于 XBlackBox XDR 查看器',
        'about_version': '现代版 v3.0',
        'about_description': '用于可视化 XBlackBox 插件的 X-Plane 飞行数据记录的强大工具。',
        'about_features': '主要功能',
        'about_performance': '性能',
        'about_copyright': '© 2024 XBlackBox 项目',
        'about_built_with': '使用 Python、PySide6 和 Matplotlib 构建',
        
        # Other
        'restart_required': '请重启应用程序以使语言更改生效。',
        
        # Keyboard shortcuts
        'shortcuts_title': '键盘快捷键',
        'shortcuts_file_ops': '文件操作',
        'shortcuts_view_ops': '查看操作',
        'shortcuts_analysis': '分析',
        'shortcuts_help': '帮助',
        
        # Plot labels
        'plot_time': '时间（秒）',
        'plot_value': '值',
        'plot_rate': '变化率',
        'plot_frequency': '频率 (Hz)',
        'plot_magnitude': '幅度',
        'plot_longitude': '经度',
        'plot_latitude': '纬度',
        'plot_altitude': '高度 (英尺)',
    }
}


class Translator:
    """Translation manager"""
    
    def __init__(self):
        self.current_language = 'en_US'
        self._detect_system_language()
        
    def _detect_system_language(self):
        """Detect system language"""
        try:
            sys_locale = locale.getdefaultlocale()[0]
            if sys_locale:
                if sys_locale.startswith('zh'):
                    self.current_language = 'zh_CN'
                else:
                    self.current_language = 'en_US'
        except:
            self.current_language = 'en_US'
    
    def set_language(self, lang_code: str):
        """Set current language"""
        if lang_code in TRANSLATIONS:
            self.current_language = lang_code
        elif lang_code == 'system':
            self._detect_system_language()
    
    def tr(self, key: str) -> str:
        """Translate a key"""
        return TRANSLATIONS.get(self.current_language, TRANSLATIONS['en_US']).get(key, key)
    
    def get_current_language(self) -> str:
        """Get current language code"""
        return self.current_language


# Global translator instance
_translator = Translator()

def tr(key: str) -> str:
    """Convenience function for translation"""
    return _translator.tr(key)

def set_language(lang_code: str):
    """Set application language"""
    _translator.set_language(lang_code)

def get_current_language() -> str:
    """Get current language code"""
    return _translator.get_current_language()
