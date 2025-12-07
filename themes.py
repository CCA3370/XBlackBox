#!/usr/bin/env python3
"""
Theme system for XBlackBox XDR Viewer
Provides multiple color themes for the application
"""

from typing import Dict

class Theme:
    """Base theme class"""
    
    def __init__(self, name: str):
        self.name = name
        self.colors = {}
        self.plot_colors = []
        
    def get_stylesheet(self) -> str:
        """Get Qt stylesheet for this theme"""
        raise NotImplementedError
        
    def get_plot_style(self) -> Dict:
        """Get matplotlib plot style"""
        raise NotImplementedError


class DarkTheme(Theme):
    """Dark theme (original modern theme)"""
    
    def __init__(self):
        super().__init__("Dark")
        self.colors = {
            'primary': '#0d7377',
            'background': '#1e1e1e',
            'surface': '#252525',
            'surface_alt': '#2d2d2d',
            'border': '#3d3d3d',
            'border_hover': '#4d4d4d',
            'text_primary': '#e0e0e0',
            'text_secondary': '#b0b0b0',
            'text_disabled': '#666666',
            'success': '#4ecdc4',
            'warning': '#ffe66d',
            'error': '#ff6b6b',
        }
        self.plot_colors = [
            '#0d7377', '#ff6b6b', '#4ecdc4', '#ffe66d', '#a8dadc',
            '#f06292', '#81c784', '#ffab91', '#ce93d8', '#64b5f6',
            '#ff8a65', '#aed581', '#9fa8da', '#90caf9', '#f48fb1',
            '#80cbc4', '#ffcc80', '#bcaaa4', '#b39ddb', '#80deea',
        ]
        
    def get_stylesheet(self) -> str:
        return f"""
            QMainWindow {{
                background-color: {self.colors['background']};
            }}
            QWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['text_primary']};
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
                font-size: 10pt;
            }}
            QMenuBar {{
                background-color: {self.colors['surface_alt']};
                border-bottom: 1px solid {self.colors['border']};
                padding: 4px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {self.colors['primary']};
                color: #ffffff;
            }}
            QMenuBar::item:pressed {{
                background-color: {self.colors['primary']};
                opacity: 0.8;
            }}
            QMenu {{
                background-color: {self.colors['surface_alt']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 24px 6px 12px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {self.colors['primary']};
                color: #ffffff;
            }}
            QMenu::separator {{
                height: 1px;
                background: {self.colors['border']};
                margin: 4px 8px;
            }}
            QToolBar {{
                background-color: {self.colors['surface_alt']};
                border: none;
                border-bottom: 1px solid {self.colors['border']};
                spacing: 6px;
                padding: 4px;
            }}
            QToolButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px;
            }}
            QToolButton:hover {{
                background-color: {self.colors['border']};
                border-color: {self.colors['border']};
            }}
            QToolButton:pressed {{
                background-color: {self.colors['primary']};
                border-color: {self.colors['primary']};
            }}
            QStatusBar {{
                background-color: {self.colors['surface_alt']};
                border-top: 1px solid {self.colors['border']};
                padding: 4px;
                color: {self.colors['text_secondary']};
            }}
            QGroupBox {{
                background-color: {self.colors['surface']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 16px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px;
                top: 8px;
                padding: 0 8px;
                color: {self.colors['primary']};
                font-size: 11pt;
            }}
            QPushButton {{
                background-color: {self.colors['primary']};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['primary']};
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            QPushButton:pressed {{
                background-color: {self.colors['primary']};
                opacity: 0.8;
            }}
            QPushButton:disabled {{
                background-color: {self.colors['border']};
                color: {self.colors['text_disabled']};
            }}
            QPushButton#secondaryButton {{
                background-color: {self.colors['border']};
                color: {self.colors['text_primary']};
            }}
            QPushButton#secondaryButton:hover {{
                background-color: {self.colors['border_hover']};
            }}
            QCheckBox {{
                spacing: 8px;
                color: {self.colors['text_primary']};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {self.colors['border']};
                background-color: {self.colors['surface_alt']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.colors['primary']};
                border-color: {self.colors['primary']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {self.colors['primary']};
            }}
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                background-color: {self.colors['surface_alt']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 6px 10px;
                color: {self.colors['text_primary']};
                selection-background-color: {self.colors['primary']};
            }}
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                border-color: {self.colors['primary']};
            }}
            QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {{
                border-color: {self.colors['border_hover']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QScrollArea {{
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                background-color: {self.colors['surface']};
            }}
            QScrollBar:vertical {{
                border: none;
                background-color: {self.colors['surface_alt']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.colors['border_hover']};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.colors['text_disabled']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background-color: {self.colors['surface_alt']};
                height: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {self.colors['border_hover']};
                border-radius: 6px;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {self.colors['text_disabled']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QTableWidget {{
                background-color: {self.colors['surface']};
                alternate-background-color: {self.colors['surface_alt']};
                gridline-color: {self.colors['border']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                selection-background-color: {self.colors['primary']};
                selection-color: #ffffff;
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
            QHeaderView::section {{
                background-color: {self.colors['surface_alt']};
                border: none;
                border-right: 1px solid {self.colors['border']};
                border-bottom: 1px solid {self.colors['border']};
                padding: 8px;
                font-weight: bold;
                color: {self.colors['primary']};
            }}
            QHeaderView::section:hover {{
                background-color: {self.colors['border']};
            }}
            QTabWidget::pane {{
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                top: -1px;
                background-color: {self.colors['surface']};
            }}
            QTabBar::tab {{
                background-color: {self.colors['surface_alt']};
                border: 1px solid {self.colors['border']};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 20px;
                margin-right: 4px;
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {self.colors['surface']};
                border-bottom-color: {self.colors['surface']};
                color: {self.colors['primary']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {self.colors['border']};
            }}
            QSplitter::handle {{
                background-color: {self.colors['border']};
                width: 2px;
                height: 2px;
            }}
            QSplitter::handle:hover {{
                background-color: {self.colors['primary']};
            }}
            QLabel {{
                color: {self.colors['text_primary']};
            }}
            QProgressBar {{
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                background-color: {self.colors['surface_alt']};
                text-align: center;
                color: {self.colors['text_primary']};
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['primary']};
                border-radius: 4px;
            }}
            QToolTip {{
                background-color: {self.colors['surface_alt']};
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['primary']};
                border-radius: 6px;
                padding: 6px;
            }}
        """
    
    def get_plot_style(self) -> Dict:
        return {
            'figure.facecolor': self.colors['background'],
            'axes.facecolor': self.colors['surface'],
            'axes.edgecolor': self.colors['border'],
            'axes.labelcolor': self.colors['text_primary'],
            'xtick.color': self.colors['text_secondary'],
            'ytick.color': self.colors['text_secondary'],
            'grid.color': self.colors['border_hover'],
            'text.color': self.colors['text_primary'],
            'legend.facecolor': self.colors['surface_alt'],
            'legend.edgecolor': self.colors['primary'],
        }


class LightTheme(Theme):
    """Light theme for better visibility in bright environments"""
    
    def __init__(self):
        super().__init__("Light")
        self.colors = {
            'primary': '#0d7377',
            'background': '#f5f5f5',
            'surface': '#ffffff',
            'surface_alt': '#e8e8e8',
            'border': '#cccccc',
            'border_hover': '#999999',
            'text_primary': '#212121',
            'text_secondary': '#616161',
            'text_disabled': '#9e9e9e',
            'success': '#00897b',
            'warning': '#fbc02d',
            'error': '#d32f2f',
        }
        self.plot_colors = [
            '#0d7377', '#d32f2f', '#00897b', '#f57c00', '#5e35b1',
            '#c2185b', '#388e3c', '#f4511e', '#7b1fa2', '#1976d2',
            '#e64a19', '#689f38', '#512da8', '#0288d1', '#c2185b',
            '#00796b', '#f57f17', '#5d4037', '#6a1b9a', '#0097a7',
        ]
        
    def get_stylesheet(self) -> str:
        return f"""
            QMainWindow {{
                background-color: {self.colors['background']};
            }}
            QWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['text_primary']};
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
                font-size: 10pt;
            }}
            QMenuBar {{
                background-color: {self.colors['surface']};
                border-bottom: 1px solid {self.colors['border']};
                padding: 4px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {self.colors['primary']};
                color: white;
            }}
            QMenuBar::item:pressed {{
                background-color: {self.colors['primary']};
                opacity: 0.8;
            }}
            QMenu {{
                background-color: {self.colors['surface']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 24px 6px 12px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {self.colors['primary']};
                color: white;
            }}
            QMenu::separator {{
                height: 1px;
                background: {self.colors['border']};
                margin: 4px 8px;
            }}
            QToolBar {{
                background-color: {self.colors['surface']};
                border: none;
                border-bottom: 1px solid {self.colors['border']};
                spacing: 6px;
                padding: 4px;
            }}
            QToolButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px;
            }}
            QToolButton:hover {{
                background-color: {self.colors['surface_alt']};
                border-color: {self.colors['border']};
            }}
            QToolButton:pressed {{
                background-color: {self.colors['primary']};
                border-color: {self.colors['primary']};
            }}
            QStatusBar {{
                background-color: {self.colors['surface']};
                border-top: 1px solid {self.colors['border']};
                padding: 4px;
                color: {self.colors['text_secondary']};
            }}
            QGroupBox {{
                background-color: {self.colors['surface']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 16px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px;
                top: 8px;
                padding: 0 8px;
                color: {self.colors['primary']};
                font-size: 11pt;
            }}
            QPushButton {{
                background-color: {self.colors['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['primary']};
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            QPushButton:pressed {{
                background-color: {self.colors['primary']};
                opacity: 0.8;
            }}
            QPushButton:disabled {{
                background-color: {self.colors['border']};
                color: {self.colors['text_disabled']};
            }}
            QPushButton#secondaryButton {{
                background-color: {self.colors['surface_alt']};
                color: {self.colors['text_primary']};
            }}
            QPushButton#secondaryButton:hover {{
                background-color: {self.colors['border']};
            }}
            QCheckBox {{
                spacing: 8px;
                color: {self.colors['text_primary']};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {self.colors['border']};
                background-color: {self.colors['surface']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.colors['primary']};
                border-color: {self.colors['primary']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {self.colors['primary']};
            }}
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                background-color: {self.colors['surface']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 6px 10px;
                color: {self.colors['text_primary']};
                selection-background-color: {self.colors['primary']};
            }}
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                border-color: {self.colors['primary']};
            }}
            QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {{
                border-color: {self.colors['border_hover']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QScrollArea {{
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                background-color: {self.colors['surface']};
            }}
            QScrollBar:vertical {{
                border: none;
                background-color: {self.colors['surface_alt']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.colors['border']};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.colors['border_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background-color: {self.colors['surface_alt']};
                height: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {self.colors['border']};
                border-radius: 6px;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {self.colors['border_hover']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QTableWidget {{
                background-color: {self.colors['surface']};
                alternate-background-color: #fafafa;
                gridline-color: {self.colors['border']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                selection-background-color: {self.colors['primary']};
                selection-color: white;
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
            QHeaderView::section {{
                background-color: {self.colors['surface_alt']};
                border: none;
                border-right: 1px solid {self.colors['border']};
                border-bottom: 1px solid {self.colors['border']};
                padding: 8px;
                font-weight: bold;
                color: {self.colors['primary']};
            }}
            QHeaderView::section:hover {{
                background-color: {self.colors['border']};
            }}
            QTabWidget::pane {{
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                top: -1px;
                background-color: {self.colors['surface']};
            }}
            QTabBar::tab {{
                background-color: {self.colors['surface_alt']};
                border: 1px solid {self.colors['border']};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 20px;
                margin-right: 4px;
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {self.colors['surface']};
                border-bottom-color: {self.colors['surface']};
                color: {self.colors['primary']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {self.colors['border']};
            }}
            QSplitter::handle {{
                background-color: {self.colors['border']};
                width: 2px;
                height: 2px;
            }}
            QSplitter::handle:hover {{
                background-color: {self.colors['primary']};
            }}
            QLabel {{
                color: {self.colors['text_primary']};
            }}
            QProgressBar {{
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                background-color: {self.colors['surface']};
                text-align: center;
                color: {self.colors['text_primary']};
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['primary']};
                border-radius: 4px;
            }}
            QToolTip {{
                background-color: {self.colors['surface']};
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['primary']};
                border-radius: 6px;
                padding: 6px;
            }}
        """
    
    def get_plot_style(self) -> Dict:
        return {
            'figure.facecolor': self.colors['background'],
            'axes.facecolor': self.colors['surface'],
            'axes.edgecolor': self.colors['border'],
            'axes.labelcolor': self.colors['text_primary'],
            'xtick.color': self.colors['text_secondary'],
            'ytick.color': self.colors['text_secondary'],
            'grid.color': self.colors['border'],
            'text.color': self.colors['text_primary'],
            'legend.facecolor': self.colors['surface'],
            'legend.edgecolor': self.colors['primary'],
        }


class HighContrastTheme(Theme):
    """High contrast theme for accessibility"""
    
    def __init__(self):
        super().__init__("High Contrast")
        self.colors = {
            'primary': '#00ffff',
            'background': '#000000',
            'surface': '#1a1a1a',
            'surface_alt': '#2a2a2a',
            'border': '#ffffff',
            'border_hover': '#00ffff',
            'text_primary': '#ffffff',
            'text_secondary': '#e0e0e0',
            'text_disabled': '#808080',
            'success': '#00ff00',
            'warning': '#ffff00',
            'error': '#ff0000',
        }
        self.plot_colors = [
            '#00ffff', '#ff00ff', '#ffff00', '#00ff00', '#ff8800',
            '#ff0088', '#88ff00', '#0088ff', '#ff0000', '#0000ff',
            '#ff6600', '#66ff00', '#0066ff', '#ff0066', '#6600ff',
            '#00ff66', '#ff6600', '#880088', '#008888', '#888800',
        ]
        
    def get_stylesheet(self) -> str:
        return f"""
            QMainWindow {{
                background-color: {self.colors['background']};
            }}
            QWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['text_primary']};
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
                font-size: 11pt;
            }}
            QMenuBar {{
                background-color: {self.colors['surface']};
                border-bottom: 2px solid {self.colors['border']};
                padding: 4px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 14px;
                border-radius: 4px;
                border: 1px solid transparent;
            }}
            QMenuBar::item:selected {{
                background-color: {self.colors['primary']};
                color: {self.colors['background']};
                border: 1px solid {self.colors['border']};
            }}
            QMenu {{
                background-color: {self.colors['surface']};
                border: 2px solid {self.colors['border']};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 10px 26px 10px 14px;
                border-radius: 4px;
                border: 1px solid transparent;
            }}
            QMenu::item:selected {{
                background-color: {self.colors['primary']};
                color: {self.colors['background']};
                border: 1px solid {self.colors['border']};
            }}
            QMenu::separator {{
                height: 2px;
                background: {self.colors['border']};
                margin: 6px 10px;
            }}
            QToolBar {{
                background-color: {self.colors['surface']};
                border: none;
                border-bottom: 2px solid {self.colors['border']};
                spacing: 8px;
                padding: 4px;
            }}
            QToolButton {{
                background-color: transparent;
                border: 2px solid transparent;
                border-radius: 6px;
                padding: 6px;
            }}
            QToolButton:hover {{
                border-color: {self.colors['border']};
            }}
            QToolButton:pressed {{
                background-color: {self.colors['primary']};
                border-color: {self.colors['primary']};
            }}
            QStatusBar {{
                background-color: {self.colors['surface']};
                border-top: 2px solid {self.colors['border']};
                padding: 6px;
                color: {self.colors['text_primary']};
            }}
            QGroupBox {{
                background-color: {self.colors['surface']};
                border: 2px solid {self.colors['border']};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 16px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px;
                top: 8px;
                padding: 0 8px;
                color: {self.colors['primary']};
                font-size: 12pt;
            }}
            QPushButton {{
                background-color: {self.colors['background']};
                color: {self.colors['text_primary']};
                border: 2px solid {self.colors['border']};
                border-radius: 6px;
                padding: 10px 22px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['primary']};
                color: {self.colors['background']};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['border']};
            }}
            QPushButton:disabled {{
                border-color: {self.colors['text_disabled']};
                color: {self.colors['text_disabled']};
            }}
            QPushButton#secondaryButton {{
                background-color: {self.colors['surface']};
            }}
            QCheckBox {{
                spacing: 10px;
                color: {self.colors['text_primary']};
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid {self.colors['border']};
                background-color: {self.colors['background']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.colors['primary']};
                border-color: {self.colors['primary']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {self.colors['primary']};
            }}
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                background-color: {self.colors['background']};
                border: 2px solid {self.colors['border']};
                border-radius: 6px;
                padding: 8px 12px;
                color: {self.colors['text_primary']};
                selection-background-color: {self.colors['primary']};
                selection-color: {self.colors['background']};
            }}
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                border-color: {self.colors['primary']};
                border-width: 3px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 28px;
            }}
            QScrollArea {{
                border: 2px solid {self.colors['border']};
                border-radius: 8px;
                background-color: {self.colors['surface']};
            }}
            QScrollBar:vertical {{
                border: 2px solid {self.colors['border']};
                background-color: {self.colors['background']};
                width: 18px;
                border-radius: 8px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.colors['border']};
                border-radius: 6px;
                min-height: 40px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.colors['primary']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: 2px solid {self.colors['border']};
                background-color: {self.colors['background']};
                height: 18px;
                border-radius: 8px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {self.colors['border']};
                border-radius: 6px;
                min-width: 40px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {self.colors['primary']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QTableWidget {{
                background-color: {self.colors['background']};
                alternate-background-color: {self.colors['surface']};
                gridline-color: {self.colors['border']};
                border: 2px solid {self.colors['border']};
                border-radius: 8px;
                selection-background-color: {self.colors['primary']};
                selection-color: {self.colors['background']};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QHeaderView::section {{
                background-color: {self.colors['surface']};
                border: 2px solid {self.colors['border']};
                border-right: none;
                border-top: none;
                padding: 10px;
                font-weight: bold;
                color: {self.colors['primary']};
            }}
            QTabWidget::pane {{
                border: 2px solid {self.colors['border']};
                border-radius: 8px;
                top: -2px;
                background-color: {self.colors['surface']};
            }}
            QTabBar::tab {{
                background-color: {self.colors['surface_alt']};
                border: 2px solid {self.colors['border']};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 22px;
                margin-right: 4px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background-color: {self.colors['surface']};
                border-bottom-color: {self.colors['surface']};
                color: {self.colors['primary']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {self.colors['primary']};
                color: {self.colors['background']};
            }}
            QSplitter::handle {{
                background-color: {self.colors['border']};
                width: 3px;
                height: 3px;
            }}
            QSplitter::handle:hover {{
                background-color: {self.colors['primary']};
            }}
            QLabel {{
                color: {self.colors['text_primary']};
            }}
            QProgressBar {{
                border: 2px solid {self.colors['border']};
                border-radius: 6px;
                background-color: {self.colors['background']};
                text-align: center;
                color: {self.colors['text_primary']};
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['primary']};
                border-radius: 4px;
            }}
            QToolTip {{
                background-color: {self.colors['surface']};
                color: {self.colors['text_primary']};
                border: 2px solid {self.colors['primary']};
                border-radius: 6px;
                padding: 8px;
                font-size: 11pt;
            }}
        """
    
    def get_plot_style(self) -> Dict:
        return {
            'figure.facecolor': self.colors['background'],
            'axes.facecolor': self.colors['surface'],
            'axes.edgecolor': self.colors['border'],
            'axes.labelcolor': self.colors['text_primary'],
            'xtick.color': self.colors['text_primary'],
            'ytick.color': self.colors['text_primary'],
            'grid.color': self.colors['border'],
            'text.color': self.colors['text_primary'],
            'legend.facecolor': self.colors['surface'],
            'legend.edgecolor': self.colors['primary'],
        }


class BlueTheme(Theme):
    """Blue theme with calming blue tones"""
    
    def __init__(self):
        super().__init__("Blue")
        self.colors = {
            'primary': '#2196f3',
            'background': '#0d1117',
            'surface': '#161b22',
            'surface_alt': '#21262d',
            'border': '#30363d',
            'border_hover': '#484f58',
            'text_primary': '#c9d1d9',
            'text_secondary': '#8b949e',
            'text_disabled': '#6e7681',
            'success': '#3fb950',
            'warning': '#d29922',
            'error': '#f85149',
        }
        self.plot_colors = [
            '#2196f3', '#f44336', '#4caf50', '#ff9800', '#9c27b0',
            '#00bcd4', '#ffeb3b', '#e91e63', '#8bc34a', '#673ab7',
            '#03a9f4', '#ff5722', '#cddc39', '#009688', '#ffc107',
            '#3f51b5', '#795548', '#607d8b', '#ff6f00', '#00e676',
        ]
        
    def get_stylesheet(self) -> str:
        return f"""
            QMainWindow {{
                background-color: {self.colors['background']};
            }}
            QWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['text_primary']};
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
                font-size: 10pt;
            }}
            QMenuBar {{
                background-color: {self.colors['surface_alt']};
                border-bottom: 1px solid {self.colors['border']};
                padding: 4px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {self.colors['primary']};
                color: #ffffff;
            }}
            QMenuBar::item:pressed {{
                background-color: {self.colors['primary']};
                opacity: 0.8;
            }}
            QMenu {{
                background-color: {self.colors['surface_alt']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 24px 6px 12px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {self.colors['primary']};
                color: #ffffff;
            }}
            QMenu::separator {{
                height: 1px;
                background: {self.colors['border']};
                margin: 4px 8px;
            }}
            QToolBar {{
                background-color: {self.colors['surface_alt']};
                border: none;
                border-bottom: 1px solid {self.colors['border']};
                spacing: 6px;
                padding: 4px;
            }}
            QToolButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px;
            }}
            QToolButton:hover {{
                background-color: {self.colors['border']};
                border-color: {self.colors['border']};
            }}
            QToolButton:pressed {{
                background-color: {self.colors['primary']};
                border-color: {self.colors['primary']};
            }}
            QStatusBar {{
                background-color: {self.colors['surface_alt']};
                border-top: 1px solid {self.colors['border']};
                padding: 4px;
                color: {self.colors['text_secondary']};
            }}
            QGroupBox {{
                background-color: {self.colors['surface']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 16px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px;
                top: 8px;
                padding: 0 8px;
                color: {self.colors['primary']};
                font-size: 11pt;
            }}
            QPushButton {{
                background-color: {self.colors['primary']};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['primary']};
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            QPushButton:pressed {{
                background-color: {self.colors['primary']};
                opacity: 0.8;
            }}
            QPushButton:disabled {{
                background-color: {self.colors['border']};
                color: {self.colors['text_disabled']};
            }}
            QPushButton#secondaryButton {{
                background-color: {self.colors['border']};
                color: {self.colors['text_primary']};
            }}
            QPushButton#secondaryButton:hover {{
                background-color: {self.colors['border_hover']};
            }}
            QCheckBox {{
                spacing: 8px;
                color: {self.colors['text_primary']};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {self.colors['border']};
                background-color: {self.colors['surface_alt']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.colors['primary']};
                border-color: {self.colors['primary']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {self.colors['primary']};
            }}
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                background-color: {self.colors['surface_alt']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 6px 10px;
                color: {self.colors['text_primary']};
                selection-background-color: {self.colors['primary']};
            }}
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                border-color: {self.colors['primary']};
            }}
            QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {{
                border-color: {self.colors['border_hover']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QScrollArea {{
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                background-color: {self.colors['surface']};
            }}
            QScrollBar:vertical {{
                border: none;
                background-color: {self.colors['surface_alt']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.colors['border_hover']};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.colors['text_disabled']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background-color: {self.colors['surface_alt']};
                height: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {self.colors['border_hover']};
                border-radius: 6px;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {self.colors['text_disabled']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QTableWidget {{
                background-color: {self.colors['surface']};
                alternate-background-color: #1c2128;
                gridline-color: {self.colors['border']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                selection-background-color: {self.colors['primary']};
                selection-color: #ffffff;
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
            QHeaderView::section {{
                background-color: {self.colors['surface_alt']};
                border: none;
                border-right: 1px solid {self.colors['border']};
                border-bottom: 1px solid {self.colors['border']};
                padding: 8px;
                font-weight: bold;
                color: {self.colors['primary']};
            }}
            QHeaderView::section:hover {{
                background-color: {self.colors['border']};
            }}
            QTabWidget::pane {{
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                top: -1px;
                background-color: {self.colors['surface']};
            }}
            QTabBar::tab {{
                background-color: {self.colors['surface_alt']};
                border: 1px solid {self.colors['border']};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 20px;
                margin-right: 4px;
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {self.colors['surface']};
                border-bottom-color: {self.colors['surface']};
                color: {self.colors['primary']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {self.colors['border']};
            }}
            QSplitter::handle {{
                background-color: {self.colors['border']};
                width: 2px;
                height: 2px;
            }}
            QSplitter::handle:hover {{
                background-color: {self.colors['primary']};
            }}
            QLabel {{
                color: {self.colors['text_primary']};
            }}
            QProgressBar {{
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                background-color: {self.colors['surface_alt']};
                text-align: center;
                color: {self.colors['text_primary']};
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['primary']};
                border-radius: 4px;
            }}
            QToolTip {{
                background-color: {self.colors['surface_alt']};
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['primary']};
                border-radius: 6px;
                padding: 6px;
            }}
        """
    
    def get_plot_style(self) -> Dict:
        return {
            'figure.facecolor': self.colors['background'],
            'axes.facecolor': self.colors['surface'],
            'axes.edgecolor': self.colors['border'],
            'axes.labelcolor': self.colors['text_primary'],
            'xtick.color': self.colors['text_secondary'],
            'ytick.color': self.colors['text_secondary'],
            'grid.color': self.colors['border_hover'],
            'text.color': self.colors['text_primary'],
            'legend.facecolor': self.colors['surface_alt'],
            'legend.edgecolor': self.colors['primary'],
        }


class SolarizedDarkTheme(Theme):
    """Solarized Dark theme - popular among developers"""
    
    def __init__(self):
        super().__init__("Solarized Dark")
        self.colors = {
            'primary': '#268bd2',
            'background': '#002b36',
            'surface': '#073642',
            'surface_alt': '#0e4050',
            'border': '#586e75',
            'border_hover': '#657b83',
            'text_primary': '#839496',
            'text_secondary': '#586e75',
            'text_disabled': '#073642',
            'success': '#859900',
            'warning': '#b58900',
            'error': '#dc322f',
        }
        self.plot_colors = [
            '#268bd2', '#dc322f', '#859900', '#b58900', '#d33682',
            '#2aa198', '#cb4b16', '#6c71c4', '#859900', '#b58900',
            '#268bd2', '#dc322f', '#2aa198', '#d33682', '#6c71c4',
            '#cb4b16', '#859900', '#b58900', '#dc322f', '#268bd2',
        ]
        
    def get_stylesheet(self) -> str:
        return f"""
            QMainWindow {{
                background-color: {self.colors['background']};
            }}
            QWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['text_primary']};
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
                font-size: 10pt;
            }}
            QMenuBar {{
                background-color: {self.colors['surface']};
                border-bottom: 1px solid {self.colors['border']};
                padding: 4px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {self.colors['primary']};
                color: {self.colors['background']};
            }}
            QMenuBar::item:pressed {{
                background-color: {self.colors['primary']};
                opacity: 0.8;
            }}
            QMenu {{
                background-color: {self.colors['surface']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 24px 6px 12px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {self.colors['primary']};
                color: {self.colors['background']};
            }}
            QMenu::separator {{
                height: 1px;
                background: {self.colors['border']};
                margin: 4px 8px;
            }}
            QToolBar {{
                background-color: {self.colors['surface']};
                border: none;
                border-bottom: 1px solid {self.colors['border']};
                spacing: 6px;
                padding: 4px;
            }}
            QToolButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px;
            }}
            QToolButton:hover {{
                background-color: {self.colors['surface_alt']};
                border-color: {self.colors['border']};
            }}
            QToolButton:pressed {{
                background-color: {self.colors['primary']};
                border-color: {self.colors['primary']};
            }}
            QStatusBar {{
                background-color: {self.colors['surface']};
                border-top: 1px solid {self.colors['border']};
                padding: 4px;
                color: {self.colors['text_secondary']};
            }}
            QGroupBox {{
                background-color: {self.colors['surface']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 16px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px;
                top: 8px;
                padding: 0 8px;
                color: {self.colors['primary']};
                font-size: 11pt;
            }}
            QPushButton {{
                background-color: {self.colors['primary']};
                color: {self.colors['background']};
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['primary']};
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            QPushButton:pressed {{
                background-color: {self.colors['primary']};
                opacity: 0.8;
            }}
            QPushButton:disabled {{
                background-color: {self.colors['surface_alt']};
                color: {self.colors['text_disabled']};
            }}
            QPushButton#secondaryButton {{
                background-color: {self.colors['surface_alt']};
                color: {self.colors['text_primary']};
            }}
            QPushButton#secondaryButton:hover {{
                background-color: {self.colors['border']};
            }}
            QCheckBox {{
                spacing: 8px;
                color: {self.colors['text_primary']};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {self.colors['border']};
                background-color: {self.colors['surface']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.colors['primary']};
                border-color: {self.colors['primary']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {self.colors['primary']};
            }}
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                background-color: {self.colors['surface']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 6px 10px;
                color: {self.colors['text_primary']};
                selection-background-color: {self.colors['primary']};
            }}
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                border-color: {self.colors['primary']};
            }}
            QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {{
                border-color: {self.colors['border_hover']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QScrollArea {{
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                background-color: {self.colors['surface']};
            }}
            QScrollBar:vertical {{
                border: none;
                background-color: {self.colors['surface']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.colors['border']};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.colors['border_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background-color: {self.colors['surface']};
                height: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {self.colors['border']};
                border-radius: 6px;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {self.colors['border_hover']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QTableWidget {{
                background-color: {self.colors['surface']};
                alternate-background-color: {self.colors['surface_alt']};
                gridline-color: {self.colors['border']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                selection-background-color: {self.colors['primary']};
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
            QHeaderView::section {{
                background-color: {self.colors['surface_alt']};
                border: none;
                border-right: 1px solid {self.colors['border']};
                border-bottom: 1px solid {self.colors['border']};
                padding: 8px;
                font-weight: bold;
                color: {self.colors['primary']};
            }}
            QHeaderView::section:hover {{
                background-color: {self.colors['border']};
            }}
            QTabWidget::pane {{
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                top: -1px;
                background-color: {self.colors['surface']};
            }}
            QTabBar::tab {{
                background-color: {self.colors['surface_alt']};
                border: 1px solid {self.colors['border']};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 20px;
                margin-right: 4px;
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {self.colors['surface']};
                border-bottom-color: {self.colors['surface']};
                color: {self.colors['primary']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {self.colors['border']};
            }}
            QSplitter::handle {{
                background-color: {self.colors['border']};
                width: 2px;
                height: 2px;
            }}
            QSplitter::handle:hover {{
                background-color: {self.colors['primary']};
            }}
            QLabel {{
                color: {self.colors['text_primary']};
            }}
            QProgressBar {{
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                background-color: {self.colors['surface']};
                text-align: center;
                color: {self.colors['text_primary']};
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['primary']};
                border-radius: 4px;
            }}
            QToolTip {{
                background-color: {self.colors['surface']};
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['primary']};
                border-radius: 6px;
                padding: 6px;
            }}
        """
    
    def get_plot_style(self) -> Dict:
        return {
            'figure.facecolor': self.colors['background'],
            'axes.facecolor': self.colors['surface'],
            'axes.edgecolor': self.colors['border'],
            'axes.labelcolor': self.colors['text_primary'],
            'xtick.color': self.colors['text_secondary'],
            'ytick.color': self.colors['text_secondary'],
            'grid.color': self.colors['border'],
            'text.color': self.colors['text_primary'],
            'legend.facecolor': self.colors['surface'],
            'legend.edgecolor': self.colors['primary'],
        }


class NordTheme(Theme):
    """Nord theme - arctic, north-bluish color palette"""
    
    def __init__(self):
        super().__init__("Nord")
        self.colors = {
            'primary': '#88c0d0',
            'background': '#2e3440',
            'surface': '#3b4252',
            'surface_alt': '#434c5e',
            'border': '#4c566a',
            'border_hover': '#5e6d8a',
            'text_primary': '#eceff4',
            'text_secondary': '#d8dee9',
            'text_disabled': '#4c566a',
            'success': '#a3be8c',
            'warning': '#ebcb8b',
            'error': '#bf616a',
        }
        self.plot_colors = [
            '#88c0d0', '#bf616a', '#a3be8c', '#ebcb8b', '#b48ead',
            '#5e81ac', '#d08770', '#8fbcbb', '#81a1c1', '#a3be8c',
            '#88c0d0', '#bf616a', '#b48ead', '#d08770', '#ebcb8b',
            '#5e81ac', '#8fbcbb', '#81a1c1', '#a3be8c', '#88c0d0',
        ]
        
    def get_stylesheet(self) -> str:
        return f"""
            QMainWindow {{
                background-color: {self.colors['background']};
            }}
            QWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['text_primary']};
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
                font-size: 10pt;
            }}
            QMenuBar {{
                background-color: {self.colors['surface_alt']};
                border-bottom: 1px solid {self.colors['border']};
                padding: 4px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {self.colors['primary']};
                color: {self.colors['background']};
            }}
            QMenuBar::item:pressed {{
                background-color: {self.colors['primary']};
                opacity: 0.8;
            }}
            QMenu {{
                background-color: {self.colors['surface_alt']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 24px 6px 12px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {self.colors['primary']};
                color: {self.colors['background']};
            }}
            QMenu::separator {{
                height: 1px;
                background: {self.colors['border']};
                margin: 4px 8px;
            }}
            QToolBar {{
                background-color: {self.colors['surface_alt']};
                border: none;
                border-bottom: 1px solid {self.colors['border']};
                spacing: 6px;
                padding: 4px;
            }}
            QToolButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px;
            }}
            QToolButton:hover {{
                background-color: {self.colors['border']};
                border-color: {self.colors['border']};
            }}
            QToolButton:pressed {{
                background-color: {self.colors['primary']};
                border-color: {self.colors['primary']};
            }}
            QStatusBar {{
                background-color: {self.colors['surface_alt']};
                border-top: 1px solid {self.colors['border']};
                padding: 4px;
                color: {self.colors['text_secondary']};
            }}
            QGroupBox {{
                background-color: {self.colors['surface']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 16px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px;
                top: 8px;
                padding: 0 8px;
                color: {self.colors['primary']};
                font-size: 11pt;
            }}
            QPushButton {{
                background-color: {self.colors['primary']};
                color: {self.colors['background']};
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['primary']};
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            QPushButton:pressed {{
                background-color: {self.colors['primary']};
                opacity: 0.8;
            }}
            QPushButton:disabled {{
                background-color: {self.colors['border']};
                color: {self.colors['text_disabled']};
            }}
            QPushButton#secondaryButton {{
                background-color: {self.colors['border']};
                color: {self.colors['text_primary']};
            }}
            QPushButton#secondaryButton:hover {{
                background-color: {self.colors['border_hover']};
            }}
            QCheckBox {{
                spacing: 8px;
                color: {self.colors['text_primary']};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {self.colors['border']};
                background-color: {self.colors['surface_alt']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.colors['primary']};
                border-color: {self.colors['primary']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {self.colors['primary']};
            }}
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                background-color: {self.colors['surface_alt']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 6px 10px;
                color: {self.colors['text_primary']};
                selection-background-color: {self.colors['primary']};
            }}
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                border-color: {self.colors['primary']};
            }}
            QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {{
                border-color: {self.colors['border_hover']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QScrollArea {{
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                background-color: {self.colors['surface']};
            }}
            QScrollBar:vertical {{
                border: none;
                background-color: {self.colors['surface_alt']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.colors['border_hover']};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.colors['text_disabled']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background-color: {self.colors['surface_alt']};
                height: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {self.colors['border_hover']};
                border-radius: 6px;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {self.colors['text_disabled']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QTableWidget {{
                background-color: {self.colors['surface']};
                alternate-background-color: {self.colors['surface_alt']};
                gridline-color: {self.colors['border']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                selection-background-color: {self.colors['primary']};
                selection-color: #ffffff;
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
            QHeaderView::section {{
                background-color: {self.colors['surface_alt']};
                border: none;
                border-right: 1px solid {self.colors['border']};
                border-bottom: 1px solid {self.colors['border']};
                padding: 8px;
                font-weight: bold;
                color: {self.colors['primary']};
            }}
            QHeaderView::section:hover {{
                background-color: {self.colors['border']};
            }}
            QTabWidget::pane {{
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                top: -1px;
                background-color: {self.colors['surface']};
            }}
            QTabBar::tab {{
                background-color: {self.colors['surface_alt']};
                border: 1px solid {self.colors['border']};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 20px;
                margin-right: 4px;
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {self.colors['surface']};
                border-bottom-color: {self.colors['surface']};
                color: {self.colors['primary']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {self.colors['border']};
            }}
            QSplitter::handle {{
                background-color: {self.colors['border']};
                width: 2px;
                height: 2px;
            }}
            QSplitter::handle:hover {{
                background-color: {self.colors['primary']};
            }}
            QLabel {{
                color: {self.colors['text_primary']};
            }}
            QProgressBar {{
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                background-color: {self.colors['surface_alt']};
                text-align: center;
                color: {self.colors['text_primary']};
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['primary']};
                border-radius: 4px;
            }}
            QToolTip {{
                background-color: {self.colors['surface_alt']};
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['primary']};
                border-radius: 6px;
                padding: 6px;
            }}
        """
    
    def get_plot_style(self) -> Dict:
        return {
            'figure.facecolor': self.colors['background'],
            'axes.facecolor': self.colors['surface'],
            'axes.edgecolor': self.colors['border'],
            'axes.labelcolor': self.colors['text_primary'],
            'xtick.color': self.colors['text_secondary'],
            'ytick.color': self.colors['text_secondary'],
            'grid.color': self.colors['border_hover'],
            'text.color': self.colors['text_primary'],
            'legend.facecolor': self.colors['surface_alt'],
            'legend.edgecolor': self.colors['primary'],
        }


class ModernDarkTheme(Theme):
    """Modern Dark theme with refined colors and spacing"""
    
    def __init__(self):
        super().__init__("Modern Dark")
        self.colors = {
            'primary': '#3794ff',
            'background': '#181818',
            'surface': '#1f1f1f',
            'surface_alt': '#2b2b2b',
            'border': '#3f3f3f',
            'border_hover': '#505050',
            'text_primary': '#e0e0e0',
            'text_secondary': '#a0a0a0',
            'text_disabled': '#606060',
            'success': '#4ec9b0',
            'warning': '#dcdcaa',
            'error': '#f44747',
        }
        self.plot_colors = [
            '#3794ff', '#f44747', '#4ec9b0', '#dcdcaa', '#ce9178',
            '#569cd6', '#9cdcfe', '#b5cea8', '#6a9955', '#d16969',
            '#c586c0', '#4fc1ff', '#d7ba7d', '#f44747', '#dcdcaa',
            '#9cdcfe', '#ce9178', '#4ec9b0', '#b5cea8', '#569cd6',
        ]
        
    def get_stylesheet(self) -> str:
        return f"""
            QMainWindow {{
                background-color: {self.colors['background']};
            }}
            QWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['text_primary']};
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', Arial, sans-serif;
                font-size: 10pt;
            }}
            QMenuBar {{
                background-color: {self.colors['surface']};
                border-bottom: 1px solid {self.colors['border']};
                padding: 4px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {self.colors['surface_alt']};
                color: {self.colors['primary']};
            }}
            QMenuBar::item:pressed {{
                background-color: {self.colors['border']};
            }}
            QMenu {{
                background-color: {self.colors['surface']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                padding: 6px;
            }}
            QMenu::item {{
                padding: 8px 24px 8px 12px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {self.colors['primary']};
                color: #ffffff;
            }}
            QMenu::separator {{
                height: 1px;
                background: {self.colors['border']};
                margin: 4px 8px;
            }}
            QToolBar {{
                background-color: {self.colors['surface']};
                border: none;
                border-bottom: 1px solid {self.colors['border']};
                spacing: 8px;
                padding: 6px;
            }}
            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 6px;
            }}
            QToolButton:hover {{
                background-color: {self.colors['surface_alt']};
            }}
            QToolButton:pressed {{
                background-color: {self.colors['border']};
            }}
            QStatusBar {{
                background-color: {self.colors['surface']};
                border-top: 1px solid {self.colors['border']};
                padding: 6px;
                color: {self.colors['text_secondary']};
            }}
            QGroupBox {{
                background-color: {self.colors['surface']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 16px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px;
                top: 8px;
                padding: 0 8px;
                color: {self.colors['primary']};
                font-size: 11pt;
            }}
            QPushButton {{
                background-color: {self.colors['primary']};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #4da3ff;
            }}
            QPushButton:pressed {{
                background-color: #2b7acc;
            }}
            QPushButton:disabled {{
                background-color: {self.colors['surface_alt']};
                color: {self.colors['text_disabled']};
            }}
            QPushButton#secondaryButton {{
                background-color: {self.colors['surface_alt']};
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['border']};
            }}
            QPushButton#secondaryButton:hover {{
                background-color: {self.colors['border']};
            }}
            QCheckBox {{
                spacing: 8px;
                color: {self.colors['text_primary']};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {self.colors['border']};
                background-color: {self.colors['surface_alt']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.colors['primary']};
                border-color: {self.colors['primary']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {self.colors['primary']};
            }}
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                background-color: {self.colors['surface_alt']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 6px 10px;
                color: {self.colors['text_primary']};
                selection-background-color: {self.colors['primary']};
            }}
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                border-color: {self.colors['primary']};
                background-color: {self.colors['surface']};
            }}
            QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {{
                border-color: {self.colors['border_hover']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QScrollArea {{
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                background-color: {self.colors['surface']};
            }}
            QScrollBar:vertical {{
                border: none;
                background-color: {self.colors['surface']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.colors['border']};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.colors['border_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background-color: {self.colors['surface']};
                height: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {self.colors['border']};
                border-radius: 6px;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {self.colors['border_hover']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QTableWidget {{
                background-color: {self.colors['surface']};
                alternate-background-color: {self.colors['surface_alt']};
                gridline-color: {self.colors['border']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                selection-background-color: {self.colors['primary']};
                selection-color: white;
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
            QHeaderView::section {{
                background-color: {self.colors['surface_alt']};
                border: none;
                border-right: 1px solid {self.colors['border']};
                border-bottom: 1px solid {self.colors['border']};
                padding: 8px;
                font-weight: bold;
                color: {self.colors['text_primary']};
            }}
            QHeaderView::section:hover {{
                background-color: {self.colors['border']};
            }}
            QTabWidget::pane {{
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
                top: -1px;
                background-color: {self.colors['surface']};
            }}
            QTabBar::tab {{
                background-color: {self.colors['surface_alt']};
                border: 1px solid {self.colors['border']};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 20px;
                margin-right: 4px;
                font-weight: 500;
                color: {self.colors['text_secondary']};
            }}
            QTabBar::tab:selected {{
                background-color: {self.colors['surface']};
                border-bottom-color: {self.colors['surface']};
                color: {self.colors['primary']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {self.colors['border']};
            }}
            QSplitter::handle {{
                background-color: {self.colors['border']};
                width: 1px;
                height: 1px;
            }}
            QSplitter::handle:hover {{
                background-color: {self.colors['primary']};
            }}
            QLabel {{
                color: {self.colors['text_primary']};
            }}
            QProgressBar {{
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                background-color: {self.colors['surface_alt']};
                text-align: center;
                color: {self.colors['text_primary']};
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['primary']};
                border-radius: 4px;
            }}
            QToolTip {{
                background-color: {self.colors['surface']};
                color: {self.colors['text_primary']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 6px;
            }}
        """
    
    def get_plot_style(self) -> Dict:
        return {
            'figure.facecolor': self.colors['background'],
            'axes.facecolor': self.colors['surface'],
            'axes.edgecolor': self.colors['border'],
            'axes.labelcolor': self.colors['text_primary'],
            'xtick.color': self.colors['text_secondary'],
            'ytick.color': self.colors['text_secondary'],
            'grid.color': self.colors['border'],
            'text.color': self.colors['text_primary'],
            'legend.facecolor': self.colors['surface'],
            'legend.edgecolor': self.colors['border'],
        }


# Available themes
THEMES = {
    'modern_dark': ModernDarkTheme(),
    'dark': DarkTheme(),
    'light': LightTheme(),
    'high_contrast': HighContrastTheme(),
    'blue': BlueTheme(),
    'solarized_dark': SolarizedDarkTheme(),
    'nord': NordTheme(),
}

# Default theme
DEFAULT_THEME = 'modern_dark'

# Current theme
_current_theme = THEMES[DEFAULT_THEME]


def get_current_theme() -> Theme:
    """Get current theme"""
    return _current_theme


def set_theme(theme_name: str):
    """Set current theme"""
    global _current_theme
    if theme_name in THEMES:
        _current_theme = THEMES[theme_name]


def get_theme_names() -> list:
    """Get list of available theme names"""
    return list(THEMES.keys())


def get_theme_by_name(theme_name: str) -> Theme:
    """Get a specific theme by name"""
    return THEMES.get(theme_name, THEMES[DEFAULT_THEME])
