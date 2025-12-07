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
        'theme_blue': 'Blue Theme',
        'theme_solarized_dark': 'Solarized Dark',
        'theme_nord': 'Nord Theme',
        
        # Language menu
        'lang_english': 'English',
        'lang_chinese': '中文 (Chinese)',
        'lang_japanese': '日本語 (Japanese)',
        'lang_spanish': 'Español (Spanish)',
        'lang_french': 'Français (French)',
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
        'theme_blue': '蓝色主题',
        'theme_solarized_dark': 'Solarized 深色',
        'theme_nord': 'Nord 主题',
        
        # Language menu
        'lang_english': 'English',
        'lang_chinese': '中文 (Chinese)',
        'lang_japanese': '日本語 (Japanese)',
        'lang_spanish': 'Español (Spanish)',
        'lang_french': 'Français (French)',
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
    },
    'ja_JP': {
        # Window title
        'window_title': 'XBlackBox XDR ビューア - モダンエディション',
        
        # Menu items
        'menu_file': 'ファイル(&F)',
        'menu_view': '表示(&V)',
        'menu_analysis': '分析(&A)',
        'menu_help': 'ヘルプ(&H)',
        'menu_theme': 'テーマ(&T)',
        'menu_language': '言語(&L)',
        
        # File menu
        'action_open': 'XDR ファイルを開く(&O)...',
        'action_recent': '最近使用したファイル',
        'action_export_csv': 'CSV にエクスポート(&C)...',
        'action_save_plot': 'プロット画像を保存(&I)...',
        'action_exit': '終了(&X)',
        'no_recent_files': '最近使用したファイルはありません',
        
        # View menu
        'action_refresh': 'プロットを更新(&R)',
        'action_clear_plot': 'プロットをクリア(&C)',
        'action_zoom_in': 'ズームイン(&I)',
        'action_zoom_out': 'ズームアウト(&O)',
        
        # Analysis menu
        'action_statistics': '統計を表示(&S)',
        'action_fft': '周波数分析を表示(&F)',
        'action_3d_path': '3D 飛行経路を表示(&3)',
        
        # Theme menu
        'theme_dark': 'ダークテーマ',
        'theme_light': 'ライトテーマ',
        'theme_high_contrast': 'ハイコントラスト',
        'theme_blue': 'ブルーテーマ',
        'theme_solarized_dark': 'Solarized ダーク',
        'theme_nord': 'Nord テーマ',
        
        # Language menu
        'lang_english': 'English',
        'lang_chinese': '中文 (Chinese)',
        'lang_japanese': '日本語 (Japanese)',
        'lang_spanish': 'Español (Spanish)',
        'lang_french': 'Français (French)',
        'lang_system': 'システムに従う',
        
        # Help menu
        'action_shortcuts': 'キーボードショートカット(&K)',
        'action_about': 'について(&A)',
        
        # Toolbar
        'toolbar_open': '開く',
        'toolbar_export': 'CSV エクスポート',
        
        # File info
        'file_info_no_file': 'ファイルが読み込まれていません',
        'file_info_title': 'XDR ファイルを開いて開始',
        'file_info_status_complete': '完了',
        'file_info_status_recording': '記録中...',
        'file_info_level': 'レベル:',
        'file_info_interval': '間隔:',
        'file_info_start': '開始:',
        'file_info_end': '終了:',
        'file_info_duration': '期間:',
        'file_info_frames': 'フレーム:',
        'file_info_parameters': 'パラメータ:',
        'file_info_size': 'サイズ:',
        'file_info_in_progress': '進行中',
        'file_info_ongoing': '進行中',
        'file_info_so_far': 'これまで',
        
        # Parameters panel
        'param_group_title': 'プロットするパラメータ',
        'param_filter': 'フィルタ:',
        'param_select_all': '✓ すべて選択',
        'param_clear_all': '✗ すべてクリア',
        'param_select_all_tooltip': 'すべての表示パラメータを選択',
        'param_clear_all_tooltip': 'すべてのパラメータの選択を解除',
        
        # Plot controls
        'time_range_label': '⏱️ 時間範囲:',
        'time_range_reset': '🔄 リセット',
        'time_range_reset_tooltip': '完全な時間範囲にリセット',
        'plot_options_label': '📊 プロットオプション:',
        'option_separate_axes': '軸を分離',
        'option_separate_axes_tooltip': '各パラメータを独自のY軸にプロット',
        'option_grid': 'グリッド',
        'option_grid_tooltip': 'プロットにグリッド線を表示',
        'option_derivative': '微分',
        'option_derivative_tooltip': '生の値の代わりに変化率 (d/dt) をプロット',
        'option_live_mode': '🔴 ライブモード',
        'option_live_mode_tooltip': 'リアルタイムで記録を監視',
        'btn_update_plot': '🔄 プロットを更新',
        'btn_update_plot_tooltip': '現在の選択でプロットを更新 (F5)',
        
        # Tab names
        'tab_plot': 'プロット',
        'tab_data_table': 'データテーブル',
        'tab_statistics': '統計',
        'tab_correlation': '相関',
        'tab_fft': '周波数分析',
        'tab_3d_path': '3D 飛行経路',
        
        # Statistics
        'stats_title': '📊 統計分析',
        'stats_refresh': '統計を更新',
        'stats_parameter': 'パラメータ',
        'stats_count': 'カウント',
        'stats_min': '最小',
        'stats_max': '最大',
        'stats_mean': '平均',
        'stats_median': '中央値',
        'stats_std': '標準偏差',
        'stats_range': '範囲',
        
        # Status bar
        'status_ready': '準備完了 - XDR ファイルを開くかドラッグ&ドロップして開始 🚀',
        'status_loaded': '読み込み済み:',
        'status_frames': 'フレーム',
        'status_plotting': 'プロット中',
        'status_parameters': 'パラメータ',
        
        # Dialogs
        'dialog_open_title': 'XDR ファイルを開く',
        'dialog_export_title': 'CSV にエクスポート',
        'dialog_save_plot_title': 'プロットを保存',
        'dialog_error': 'エラー',
        'dialog_warning': '警告',
        'dialog_success': '成功',
        'dialog_info': '情報',
        'error_load_file': 'ファイルを開けませんでした:',
        'warning_no_file': '最初に XDR ファイルを開いてください。',
        'loading_file': 'ファイルを読み込み中...',
        'loading_cancel': 'キャンセル',
        
        # About dialog
        'about_title': 'XBlackBox XDR ビューアについて',
        'about_version': 'モダンエディション v3.0',
        'about_description': 'XBlackBox プラグインの X-Plane 飛行データ記録を視覚化するための強力なツール。',
        
        # Other
        'restart_required': '言語の変更を有効にするには、アプリケーションを再起動してください。',
        
        # Plot labels
        'plot_time': '時間（秒）',
        'plot_value': '値',
        'plot_rate': '変化率',
        'plot_frequency': '周波数 (Hz)',
        'plot_magnitude': '大きさ',
        'plot_longitude': '経度',
        'plot_latitude': '緯度',
        'plot_altitude': '高度 (フィート)',
    },
    'es_ES': {
        # Window title
        'window_title': 'XBlackBox XDR Viewer - Edición Moderna',
        
        # Menu items
        'menu_file': '&Archivo',
        'menu_view': '&Ver',
        'menu_analysis': '&Análisis',
        'menu_help': '&Ayuda',
        'menu_theme': '&Tema',
        'menu_language': '&Idioma',
        
        # File menu
        'action_open': '&Abrir archivo XDR...',
        'action_recent': 'Archivos recientes',
        'action_export_csv': 'Exportar a &CSV...',
        'action_save_plot': 'Guardar imagen del &gráfico...',
        'action_exit': '&Salir',
        'no_recent_files': 'Sin archivos recientes',
        
        # View menu
        'action_refresh': '&Actualizar gráfico',
        'action_clear_plot': '&Limpiar gráfico',
        'action_zoom_in': '&Acercar',
        'action_zoom_out': 'A&lejar',
        
        # Analysis menu
        'action_statistics': 'Mostrar &estadísticas',
        'action_fft': 'Mostrar análisis de &frecuencia',
        'action_3d_path': 'Mostrar ruta de vuelo en &3D',
        
        # Theme menu
        'theme_dark': 'Tema oscuro',
        'theme_light': 'Tema claro',
        'theme_high_contrast': 'Alto contraste',
        'theme_blue': 'Tema azul',
        'theme_solarized_dark': 'Solarized oscuro',
        'theme_nord': 'Tema Nord',
        
        # Language menu
        'lang_english': 'English',
        'lang_chinese': '中文 (Chinese)',
        'lang_japanese': '日本語 (Japanese)',
        'lang_spanish': 'Español (Spanish)',
        'lang_french': 'Français (French)',
        'lang_system': 'Seguir sistema',
        
        # Help menu
        'action_shortcuts': 'Atajos de &teclado',
        'action_about': '&Acerca de',
        
        # Toolbar
        'toolbar_open': 'Abrir',
        'toolbar_export': 'Exportar CSV',
        
        # File info
        'file_info_no_file': 'Ningún archivo cargado',
        'file_info_title': 'Abra un archivo XDR para comenzar',
        'file_info_status_complete': 'Completo',
        'file_info_status_recording': 'Grabando...',
        'file_info_level': 'Nivel:',
        'file_info_interval': 'Intervalo:',
        'file_info_start': 'Inicio:',
        'file_info_end': 'Fin:',
        'file_info_duration': 'Duración:',
        'file_info_frames': 'Cuadros:',
        'file_info_parameters': 'Parámetros:',
        'file_info_size': 'Tamaño:',
        'file_info_in_progress': 'En progreso',
        'file_info_ongoing': 'en curso',
        'file_info_so_far': 'hasta ahora',
        
        # Parameters panel
        'param_group_title': 'Parámetros a graficar',
        'param_filter': 'Filtro:',
        'param_select_all': '✓ Seleccionar todo',
        'param_clear_all': '✗ Limpiar todo',
        'param_select_all_tooltip': 'Seleccionar todos los parámetros visibles',
        'param_clear_all_tooltip': 'Deseleccionar todos los parámetros',
        
        # Plot controls
        'time_range_label': '⏱️ Rango de tiempo:',
        'time_range_reset': '🔄 Restablecer',
        'time_range_reset_tooltip': 'Restablecer al rango de tiempo completo',
        'plot_options_label': '📊 Opciones de gráfico:',
        'option_separate_axes': 'Ejes separados',
        'option_separate_axes_tooltip': 'Graficar cada parámetro en su propio eje Y',
        'option_grid': 'Cuadrícula',
        'option_grid_tooltip': 'Mostrar líneas de cuadrícula en los gráficos',
        'option_derivative': 'Derivada',
        'option_derivative_tooltip': 'Graficar tasa de cambio (d/dt) en lugar de valores sin procesar',
        'option_live_mode': '🔴 Modo en vivo',
        'option_live_mode_tooltip': 'Monitorear grabación en tiempo real',
        'btn_update_plot': '🔄 Actualizar gráfico',
        'btn_update_plot_tooltip': 'Actualizar gráfico con selección actual (F5)',
        
        # Tab names
        'tab_plot': 'Gráfico',
        'tab_data_table': 'Tabla de datos',
        'tab_statistics': 'Estadísticas',
        'tab_correlation': 'Correlación',
        'tab_fft': 'Análisis de frecuencia',
        'tab_3d_path': 'Ruta de vuelo 3D',
        
        # Statistics
        'stats_title': '📊 Análisis estadístico',
        'stats_refresh': 'Actualizar estadísticas',
        'stats_parameter': 'Parámetro',
        'stats_count': 'Recuento',
        'stats_min': 'Mínimo',
        'stats_max': 'Máximo',
        'stats_mean': 'Media',
        'stats_median': 'Mediana',
        'stats_std': 'Desv. estándar',
        'stats_range': 'Rango',
        
        # Status bar
        'status_ready': 'Listo - Abra un archivo XDR o arrastre y suelte para comenzar 🚀',
        'status_loaded': 'Cargado:',
        'status_frames': 'cuadros',
        'status_plotting': 'Graficando',
        'status_parameters': 'parámetro(s)',
        
        # Dialogs
        'dialog_open_title': 'Abrir archivo XDR',
        'dialog_export_title': 'Exportar a CSV',
        'dialog_save_plot_title': 'Guardar gráfico',
        'dialog_error': 'Error',
        'dialog_warning': 'Advertencia',
        'dialog_success': 'Éxito',
        'dialog_info': 'Información',
        'error_load_file': 'Error al abrir el archivo:',
        'warning_no_file': 'Por favor, abra primero un archivo XDR.',
        'loading_file': 'Cargando archivo...',
        'loading_cancel': 'Cancelar',
        
        # About dialog
        'about_title': 'Acerca de XBlackBox XDR Viewer',
        'about_version': 'Edición Moderna v3.0',
        'about_description': 'Una herramienta potente para visualizar grabaciones de datos de vuelo de X-Plane del complemento XBlackBox.',
        
        # Other
        'restart_required': 'Reinicie la aplicación para que los cambios de idioma surtan efecto.',
        
        # Plot labels
        'plot_time': 'Tiempo (segundos)',
        'plot_value': 'Valor',
        'plot_rate': 'Tasa de cambio',
        'plot_frequency': 'Frecuencia (Hz)',
        'plot_magnitude': 'Magnitud',
        'plot_longitude': 'Longitud',
        'plot_latitude': 'Latitud',
        'plot_altitude': 'Altitud (pies)',
    },
    'fr_FR': {
        # Window title
        'window_title': 'XBlackBox XDR Viewer - Édition Moderne',
        
        # Menu items
        'menu_file': '&Fichier',
        'menu_view': '&Affichage',
        'menu_analysis': '&Analyse',
        'menu_help': '&Aide',
        'menu_theme': '&Thème',
        'menu_language': '&Langue',
        
        # File menu
        'action_open': '&Ouvrir un fichier XDR...',
        'action_recent': 'Fichiers récents',
        'action_export_csv': 'Exporter vers &CSV...',
        'action_save_plot': 'Enregistrer l\'&image du graphique...',
        'action_exit': '&Quitter',
        'no_recent_files': 'Aucun fichier récent',
        
        # View menu
        'action_refresh': '&Actualiser le graphique',
        'action_clear_plot': '&Effacer le graphique',
        'action_zoom_in': 'Zoom &avant',
        'action_zoom_out': 'Zoom &arrière',
        
        # Analysis menu
        'action_statistics': 'Afficher les &statistiques',
        'action_fft': 'Afficher l\'analyse de &fréquence',
        'action_3d_path': 'Afficher la trajectoire de vol en &3D',
        
        # Theme menu
        'theme_dark': 'Thème sombre',
        'theme_light': 'Thème clair',
        'theme_high_contrast': 'Contraste élevé',
        'theme_blue': 'Thème bleu',
        'theme_solarized_dark': 'Solarized sombre',
        'theme_nord': 'Thème Nord',
        
        # Language menu
        'lang_english': 'English',
        'lang_chinese': '中文 (Chinese)',
        'lang_japanese': '日本語 (Japanese)',
        'lang_spanish': 'Español (Spanish)',
        'lang_french': 'Français (French)',
        'lang_system': 'Suivre le système',
        
        # Help menu
        'action_shortcuts': 'Raccourcis &clavier',
        'action_about': 'À &propos',
        
        # Toolbar
        'toolbar_open': 'Ouvrir',
        'toolbar_export': 'Exporter CSV',
        
        # File info
        'file_info_no_file': 'Aucun fichier chargé',
        'file_info_title': 'Ouvrez un fichier XDR pour commencer',
        'file_info_status_complete': 'Terminé',
        'file_info_status_recording': 'Enregistrement...',
        'file_info_level': 'Niveau :',
        'file_info_interval': 'Intervalle :',
        'file_info_start': 'Début :',
        'file_info_end': 'Fin :',
        'file_info_duration': 'Durée :',
        'file_info_frames': 'Images :',
        'file_info_parameters': 'Paramètres :',
        'file_info_size': 'Taille :',
        'file_info_in_progress': 'En cours',
        'file_info_ongoing': 'en cours',
        'file_info_so_far': 'jusqu\'à présent',
        
        # Parameters panel
        'param_group_title': 'Paramètres à tracer',
        'param_filter': 'Filtre :',
        'param_select_all': '✓ Tout sélectionner',
        'param_clear_all': '✗ Tout effacer',
        'param_select_all_tooltip': 'Sélectionner tous les paramètres visibles',
        'param_clear_all_tooltip': 'Désélectionner tous les paramètres',
        
        # Plot controls
        'time_range_label': '⏱️ Plage de temps :',
        'time_range_reset': '🔄 Réinitialiser',
        'time_range_reset_tooltip': 'Réinitialiser à la plage de temps complète',
        'plot_options_label': '📊 Options de graphique :',
        'option_separate_axes': 'Axes séparés',
        'option_separate_axes_tooltip': 'Tracer chaque paramètre sur son propre axe Y',
        'option_grid': 'Grille',
        'option_grid_tooltip': 'Afficher les lignes de grille sur les graphiques',
        'option_derivative': 'Dérivée',
        'option_derivative_tooltip': 'Tracer le taux de changement (d/dt) au lieu des valeurs brutes',
        'option_live_mode': '🔴 Mode en direct',
        'option_live_mode_tooltip': 'Surveiller l\'enregistrement en temps réel',
        'btn_update_plot': '🔄 Actualiser le graphique',
        'btn_update_plot_tooltip': 'Actualiser le graphique avec la sélection actuelle (F5)',
        
        # Tab names
        'tab_plot': 'Graphique',
        'tab_data_table': 'Table de données',
        'tab_statistics': 'Statistiques',
        'tab_correlation': 'Corrélation',
        'tab_fft': 'Analyse de fréquence',
        'tab_3d_path': 'Trajectoire de vol 3D',
        
        # Statistics
        'stats_title': '📊 Analyse statistique',
        'stats_refresh': 'Actualiser les statistiques',
        'stats_parameter': 'Paramètre',
        'stats_count': 'Nombre',
        'stats_min': 'Minimum',
        'stats_max': 'Maximum',
        'stats_mean': 'Moyenne',
        'stats_median': 'Médiane',
        'stats_std': 'Écart type',
        'stats_range': 'Plage',
        
        # Status bar
        'status_ready': 'Prêt - Ouvrez un fichier XDR ou glissez-déposez pour commencer 🚀',
        'status_loaded': 'Chargé :',
        'status_frames': 'images',
        'status_plotting': 'Traçage',
        'status_parameters': 'paramètre(s)',
        
        # Dialogs
        'dialog_open_title': 'Ouvrir un fichier XDR',
        'dialog_export_title': 'Exporter vers CSV',
        'dialog_save_plot_title': 'Enregistrer le graphique',
        'dialog_error': 'Erreur',
        'dialog_warning': 'Avertissement',
        'dialog_success': 'Succès',
        'dialog_info': 'Information',
        'error_load_file': 'Échec de l\'ouverture du fichier :',
        'warning_no_file': 'Veuillez d\'abord ouvrir un fichier XDR.',
        'loading_file': 'Chargement du fichier...',
        'loading_cancel': 'Annuler',
        
        # About dialog
        'about_title': 'À propos de XBlackBox XDR Viewer',
        'about_version': 'Édition Moderne v3.0',
        'about_description': 'Un outil puissant pour visualiser les enregistrements de données de vol X-Plane du plugin XBlackBox.',
        
        # Other
        'restart_required': 'Veuillez redémarrer l\'application pour que les modifications de langue prennent effet.',
        
        # Plot labels
        'plot_time': 'Temps (secondes)',
        'plot_value': 'Valeur',
        'plot_rate': 'Taux de changement',
        'plot_frequency': 'Fréquence (Hz)',
        'plot_magnitude': 'Magnitude',
        'plot_longitude': 'Longitude',
        'plot_latitude': 'Latitude',
        'plot_altitude': 'Altitude (pieds)',
    }
}

# Default language
DEFAULT_LANGUAGE = 'system'
DEFAULT_FALLBACK_LANGUAGE = 'en_US'


class Translator:
    """Translation manager"""
    
    def __init__(self):
        self.current_language = DEFAULT_FALLBACK_LANGUAGE
        self._detect_system_language()
        
    def _detect_system_language(self):
        """Detect system language"""
        try:
            sys_locale = locale.getdefaultlocale()[0]
            if sys_locale:
                if sys_locale.startswith('zh'):
                    self.current_language = 'zh_CN'
                elif sys_locale.startswith('ja'):
                    self.current_language = 'ja_JP'
                elif sys_locale.startswith('es'):
                    self.current_language = 'es_ES'
                elif sys_locale.startswith('fr'):
                    self.current_language = 'fr_FR'
                else:
                    self.current_language = DEFAULT_FALLBACK_LANGUAGE
        except (locale.Error, TypeError, ValueError):
            self.current_language = DEFAULT_FALLBACK_LANGUAGE
    
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
