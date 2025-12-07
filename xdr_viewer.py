#!/usr/bin/env python3
"""
XBlackBox XDR Viewer - PySide6 GUI Application
Visualize and analyze X-Plane flight data recordings

Enhanced with:
- Performance optimization with data downsampling
- Advanced statistics and analysis
- Recent files menu
- Drag and drop support
- Time range selection
- Keyboard shortcuts
"""

import sys
import struct
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from functools import partial

import numpy as np

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QLabel, QPushButton,
    QFileDialog, QMessageBox, QStatusBar, QGroupBox, QCheckBox,
    QScrollArea, QFrame, QComboBox, QSpinBox, QDoubleSpinBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QToolBar, QStyle, QSizePolicy, QProgressDialog, QSlider
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer, QSettings, QUrl
from PySide6.QtGui import QAction, QFont, QColor, QIcon, QKeySequence, QDragEnterEvent, QDropEvent

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class XDRData:
    """Container for XDR file data"""
    
    def __init__(self):
        self.filepath = ""
        self.header = {}
        self.datarefs = []
        self.frames = []
        self._data_start_pos = 0  # Position where frame data starts
        self._last_read_pos = 0   # Last read position for incremental reading
        self._is_complete = False # Whether file has ENDR marker
        
    def clear(self):
        self.filepath = ""
        self.header = {}
        self.datarefs = []
        self.frames = []
        self._data_start_pos = 0
        self._last_read_pos = 0
        self._is_complete = False
        
    def read(self, filepath: str):
        """Read the entire XDR file"""
        self.clear()
        self.filepath = filepath
        
        with open(filepath, 'rb') as f:
            self._read_header(f)
            self._read_dataref_definitions(f)
            self._data_start_pos = f.tell()  # Save position where frames start
            self._read_frames(f)
            self._try_read_footer(f)
            self._last_read_pos = f.tell()
            
    def read_new_frames(self) -> int:
        """Read any new frames added since last read. Returns number of new frames."""
        if not self.filepath or not self.datarefs:
            return 0
            
        new_frame_count = 0
        try:
            with open(self.filepath, 'rb') as f:
                f.seek(self._last_read_pos)
                
                while True:
                    marker = f.read(4)
                    if len(marker) < 4:
                        # Not enough data yet
                        break
                    if marker == b'ENDR':
                        # End of recording
                        self._is_complete = True
                        self._read_footer_data(f)
                        self._last_read_pos = f.tell()
                        break
                    if marker != b'DATA':
                        # Unknown marker or incomplete data, back up
                        break
                        
                    # Try to read the frame
                    timestamp_data = f.read(4)
                    if len(timestamp_data) < 4:
                        # Incomplete frame
                        break
                        
                    timestamp = struct.unpack('<f', timestamp_data)[0]
                    
                    # Calculate expected frame size
                    frame_size = self._calc_frame_value_size()
                    values_data = f.read(frame_size)
                    if len(values_data) < frame_size:
                        # Incomplete frame
                        break
                        
                    # Parse values from buffer
                    values = self._parse_frame_values(values_data)
                    
                    self.frames.append({
                        'timestamp': timestamp,
                        'values': values
                    })
                    new_frame_count += 1
                    self._last_read_pos = f.tell()
                    
        except Exception:
            pass
            
        return new_frame_count
        
    def _calc_frame_value_size(self) -> int:
        """Calculate the byte size of one frame's values"""
        size = 0
        for dr in self.datarefs:
            if dr['array_size'] > 0:
                size += 4 * dr['array_size']  # float or int array
            else:
                if dr['type'] == 'float':
                    size += 4
                elif dr['type'] == 'int':
                    size += 4
                elif dr['type'] == 'string':
                    size += 1  # Just the length byte minimum
        return size
        
    def _parse_frame_values(self, data: bytes) -> List:
        """Parse frame values from bytes buffer"""
        values = []
        pos = 0
        for dr in self.datarefs:
            if dr['array_size'] > 0:
                arr = []
                for _ in range(dr['array_size']):
                    if dr['type'] == 'float':
                        arr.append(struct.unpack('<f', data[pos:pos+4])[0])
                        pos += 4
                    elif dr['type'] == 'int':
                        arr.append(struct.unpack('<i', data[pos:pos+4])[0])
                        pos += 4
                values.append(arr)
            else:
                if dr['type'] == 'float':
                    values.append(struct.unpack('<f', data[pos:pos+4])[0])
                    pos += 4
                elif dr['type'] == 'int':
                    values.append(struct.unpack('<i', data[pos:pos+4])[0])
                    pos += 4
                elif dr['type'] == 'string':
                    str_len = data[pos]
                    pos += 1
                    if str_len > 0:
                        values.append(data[pos:pos+str_len].decode('utf-8'))
                        pos += str_len
                    else:
                        values.append('')
        return values
        
    def _try_read_footer(self, f):
        """Try to read file footer (may not exist if recording is in progress)"""
        try:
            marker = f.read(4)
            if marker == b'ENDR':
                self._is_complete = True
                self._read_footer_data(f)
            else:
                # No footer yet, file is being written
                self._is_complete = False
                if len(marker) == 4:
                    f.seek(-4, 1)  # Go back
        except:
            self._is_complete = False
            
    def _read_footer_data(self, f):
        """Read footer data after ENDR marker"""
        try:
            total_records = struct.unpack('<I', f.read(4))[0]
            end_timestamp = struct.unpack('<Q', f.read(8))[0]
            
            self.header['total_records'] = total_records
            self.header['end_timestamp'] = end_timestamp
            self.header['end_datetime'] = datetime.fromtimestamp(end_timestamp)
            self.header['duration'] = end_timestamp - self.header['start_timestamp']
        except:
            pass
        
    def is_recording_complete(self) -> bool:
        """Check if recording has finished (ENDR marker found)"""
        return self._is_complete
            
    def _read_header(self, f):
        """Read file header"""
        magic = f.read(4)
        if magic != b'XFDR':
            raise ValueError(f"Invalid file format. Expected XFDR, got {magic}")
            
        version = struct.unpack('<H', f.read(2))[0]
        level = struct.unpack('<B', f.read(1))[0]
        interval = struct.unpack('<f', f.read(4))[0]
        start_timestamp = struct.unpack('<Q', f.read(8))[0]
        dataref_count = struct.unpack('<H', f.read(2))[0]
        
        self.header = {
            'magic': magic.decode('ascii'),
            'version': version,
            'level': level,
            'level_name': {1: 'Simple', 2: 'Normal', 3: 'Detailed'}.get(level, 'Unknown'),
            'interval': interval,
            'start_timestamp': start_timestamp,
            'start_datetime': datetime.fromtimestamp(start_timestamp),
            'dataref_count': dataref_count
        }
        
    def _read_dataref_definitions(self, f):
        """Read dataref definitions"""
        for _ in range(self.header['dataref_count']):
            name_len = struct.unpack('<H', f.read(2))[0]
            name = f.read(name_len).decode('utf-8')
            data_type = struct.unpack('<B', f.read(1))[0]
            array_size = struct.unpack('<B', f.read(1))[0]
            
            type_name = ['float', 'int', 'string'][data_type]
            
            self.datarefs.append({
                'name': name,
                'type': type_name,
                'array_size': array_size
            })
            
    def _read_frames(self, f):
        """Read all data frames (handles incomplete files for live reading)"""
        while True:
            marker = f.read(4)
            if len(marker) < 4:
                # Incomplete data
                break
            if marker == b'ENDR':
                f.seek(-4, 1)
                break
            if marker != b'DATA':
                # Unknown marker, might be incomplete - stop reading
                f.seek(-4, 1)
                break
                
            # Try to read timestamp
            ts_data = f.read(4)
            if len(ts_data) < 4:
                f.seek(-4 - len(ts_data), 1)
                break
                
            timestamp = struct.unpack('<f', ts_data)[0]
            
            # Try to read frame values
            start_pos = f.tell()
            try:
                values = self._read_frame_values(f)
                self.frames.append({
                    'timestamp': timestamp,
                    'values': values
                })
                self._last_read_pos = f.tell()
            except:
                # Incomplete frame, go back
                f.seek(start_pos - 8, 0)  # Go back before DATA marker
                break
            
    def _read_frame_values(self, f):
        """Read values for one frame"""
        values = []
        for dr in self.datarefs:
            if dr['array_size'] > 0:
                arr = []
                for _ in range(dr['array_size']):
                    if dr['type'] == 'float':
                        arr.append(struct.unpack('<f', f.read(4))[0])
                    elif dr['type'] == 'int':
                        arr.append(struct.unpack('<i', f.read(4))[0])
                values.append(arr)
            else:
                if dr['type'] == 'float':
                    values.append(struct.unpack('<f', f.read(4))[0])
                elif dr['type'] == 'int':
                    values.append(struct.unpack('<i', f.read(4))[0])
                elif dr['type'] == 'string':
                    str_len = struct.unpack('<B', f.read(1))[0]
                    if str_len > 0:
                        values.append(f.read(str_len).decode('utf-8'))
                    else:
                        values.append('')
        return values
        
    def get_parameter_data(self, dataref_index: int, array_index: int = 0, 
                          time_range: Optional[tuple] = None, 
                          downsample_factor: int = 1) -> tuple:
        """Get timestamps and values for a specific parameter
        
        Args:
            dataref_index: Index of the dataref
            array_index: Index for array datarefs
            time_range: Optional (start_time, end_time) tuple to filter data
            downsample_factor: Factor to downsample data (1=no downsampling)
        """
        timestamps = []
        values = []
        
        dr = self.datarefs[dataref_index]
        
        for i, frame in enumerate(self.frames):
            # Apply downsampling
            if i % downsample_factor != 0:
                continue
                
            timestamp = frame['timestamp']
            
            # Apply time range filter
            if time_range:
                if timestamp < time_range[0] or timestamp > time_range[1]:
                    continue
            
            timestamps.append(timestamp)
            value = frame['values'][dataref_index]
            
            if dr['array_size'] > 0:
                values.append(value[array_index])
            else:
                if dr['type'] == 'string':
                    values.append(0)  # Can't plot strings
                else:
                    values.append(value)
                    
        return timestamps, values
        
    def get_parameter_statistics(self, dataref_index: int, array_index: int = 0,
                                 time_range: Optional[tuple] = None) -> Dict:
        """Calculate statistics for a parameter"""
        timestamps, values = self.get_parameter_data(
            dataref_index, array_index, time_range, downsample_factor=1
        )
        
        if not values:
            return {}
        
        values_array = np.array(values)
        
        return {
            'count': len(values),
            'min': float(np.min(values_array)),
            'max': float(np.max(values_array)),
            'mean': float(np.mean(values_array)),
            'median': float(np.median(values_array)),
            'std': float(np.std(values_array)),
            'range': float(np.max(values_array) - np.min(values_array))
        }
        
    def get_all_plottable_parameters(self) -> List[Dict]:
        """Get list of all parameters that can be plotted"""
        params = []
        for i, dr in enumerate(self.datarefs):
            if dr['type'] == 'string':
                continue
            if dr['array_size'] > 0:
                for j in range(dr['array_size']):
                    params.append({
                        'index': i,
                        'array_index': j,
                        'name': f"{dr['name']}[{j}]",
                        'type': dr['type']
                    })
            else:
                params.append({
                    'index': i,
                    'array_index': 0,
                    'name': dr['name'],
                    'type': dr['type']
                })
        return params
    
    def get_parameter_derivative(self, dataref_index: int, array_index: int = 0,
                                 time_range: Optional[tuple] = None) -> tuple:
        """Calculate derivative (rate of change) of a parameter
        
        Returns:
            tuple[List[float], List[float]]: (timestamps, derivative_values)
        """
        timestamps, values = self.get_parameter_data(
            dataref_index, array_index, time_range, downsample_factor=1
        )
        
        if len(timestamps) < 2:
            return [], []
        
        # Calculate derivative using numpy
        values_array = np.array(values)
        timestamps_array = np.array(timestamps)
        
        # Use gradient for better numerical derivative
        derivative = np.gradient(values_array, timestamps_array)
        
        return timestamps, derivative.tolist()
    
    def calculate_correlation(self, param1_index: int, param1_array_idx: int,
                             param2_index: int, param2_array_idx: int,
                             time_range: Optional[tuple] = None) -> float:
        """Calculate correlation coefficient between two parameters"""
        _, values1 = self.get_parameter_data(param1_index, param1_array_idx, time_range, 1)
        _, values2 = self.get_parameter_data(param2_index, param2_array_idx, time_range, 1)
        
        if len(values1) != len(values2) or len(values1) < 2:
            return 0.0
        
        return float(np.corrcoef(values1, values2)[0, 1])
        
    def export_to_csv(self, output_path: str):
        """Export data to CSV file"""
        with open(output_path, 'w', newline='') as csvfile:
            header_row = ['timestamp']
            for dr in self.datarefs:
                if dr['array_size'] > 0:
                    for i in range(dr['array_size']):
                        header_row.append(f"{dr['name']}[{i}]")
                else:
                    header_row.append(dr['name'])
                    
            writer = csv.writer(csvfile)
            writer.writerow(header_row)
            
            for frame in self.frames:
                row = [frame['timestamp']]
                for value in frame['values']:
                    if isinstance(value, list):
                        row.extend(value)
                    else:
                        row.append(value)
                writer.writerow(row)


class PlotCanvas(FigureCanvas):
    """Matplotlib canvas for plotting"""
    
    # Maximum number of points to plot before downsampling
    MAX_PLOT_POINTS = 5000
    
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.fig.set_facecolor('#2b2b2b')
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Dark theme for plots
        plt.style.use('dark_background')
        
        self.axes = []
        self.plots = []
        
    def clear_plots(self):
        """Clear all plots"""
        self.fig.clear()
        self.axes = []
        self.plots = []
        self.draw()
        
    def plot_parameters(self, data: XDRData, parameters: List[Dict], 
                        separate_axes: bool = False, show_grid: bool = True,
                        time_range: Optional[tuple] = None, plot_derivative: bool = False):
        """Plot multiple parameters with their assigned colors
        
        Args:
            data: XDR data container
            parameters: List of parameters to plot
            separate_axes: Whether to use separate axes for each parameter
            show_grid: Whether to show grid
            time_range: Optional (start, end) time range to plot
            plot_derivative: Whether to plot derivative instead of raw values
        """
        self.fig.clear()
        self.axes = []
        self.plots = []
        
        if not parameters:
            self.draw()
            return
        
        # Calculate downsampling factor based on data size
        total_frames = len(data.frames)
        downsample_factor = max(1, total_frames // self.MAX_PLOT_POINTS)
        
        if separate_axes:
            # Each parameter on its own axis
            n = len(parameters)
            for i, param in enumerate(parameters):
                ax = self.fig.add_subplot(n, 1, i + 1)
                ax.set_facecolor('#1e1e1e')
                self.axes.append(ax)
                
                if plot_derivative:
                    timestamps, values = data.get_parameter_derivative(
                        param['index'], param['array_index'], time_range
                    )
                    ylabel = f"d/dt {self._short_name(param['name'])}"
                else:
                    timestamps, values = data.get_parameter_data(
                        param['index'], param['array_index'],
                        time_range=time_range, downsample_factor=downsample_factor
                    )
                    ylabel = self._short_name(param['name'])
                
                # Use assigned color from parameter
                color = param.get('color', '#ffffff')
                line, = ax.plot(timestamps, values, color=color, linewidth=1.0)
                self.plots.append(line)
                
                ax.set_ylabel(ylabel, fontsize=8, color='white')
                ax.tick_params(colors='white', labelsize=8)
                ax.grid(show_grid, alpha=0.3)
                
                if i == len(parameters) - 1:
                    ax.set_xlabel('Time (seconds)', color='white')
                    
        else:
            # All parameters on same axis
            ax = self.fig.add_subplot(111)
            ax.set_facecolor('#1e1e1e')
            self.axes.append(ax)
            
            for i, param in enumerate(parameters):
                if plot_derivative:
                    timestamps, values = data.get_parameter_derivative(
                        param['index'], param['array_index'], time_range
                    )
                    label = f"d/dt {self._short_name(param['name'])}"
                else:
                    timestamps, values = data.get_parameter_data(
                        param['index'], param['array_index'],
                        time_range=time_range, downsample_factor=downsample_factor
                    )
                    label = self._short_name(param['name'])
                
                # Use assigned color from parameter
                color = param.get('color', '#ffffff')
                line, = ax.plot(timestamps, values, color=color, linewidth=1.0,
                               label=label)
                self.plots.append(line)
                
            ax.set_xlabel('Time (seconds)', color='white')
            ylabel = 'Rate of Change' if plot_derivative else 'Value'
            ax.set_ylabel(ylabel, color='white')
            ax.tick_params(colors='white')
            ax.grid(show_grid, alpha=0.3)
            ax.legend(loc='upper right', fontsize=8, facecolor='#2b2b2b', 
                     edgecolor='white', labelcolor='white')
            
        self.fig.tight_layout()
        self.draw()
        
    def _short_name(self, name: str) -> str:
        """Get shortened parameter name for display"""
        if len(name) > 40:
            parts = name.split('/')
            if len(parts) > 2:
                return f".../{parts[-2]}/{parts[-1]}"
        return name


# Color palette for parameters - 20 distinct colors
PARAMETER_COLORS = [
    '#1f77b4',  # blue
    '#ff7f0e',  # orange
    '#2ca02c',  # green
    '#d62728',  # red
    '#9467bd',  # purple
    '#8c564b',  # brown
    '#e377c2',  # pink
    '#7f7f7f',  # gray
    '#bcbd22',  # olive
    '#17becf',  # cyan
    '#aec7e8',  # light blue
    '#ffbb78',  # light orange
    '#98df8a',  # light green
    '#ff9896',  # light red
    '#c5b0d5',  # light purple
    '#c49c94',  # light brown
    '#f7b6d2',  # light pink
    '#c7c7c7',  # light gray
    '#dbdb8d',  # light olive
    '#9edae5',  # light cyan
]


class ParameterSelector(QWidget):
    """Widget for selecting parameters to plot"""
    
    selectionChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checkboxes = []
        self.parameters = []
        self.assigned_colors = {}  # Maps parameter name to assigned color
        self.next_color_index = 0  # Next color to assign
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Search/filter
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Filter:"))
        self.filter_edit = QComboBox()
        self.filter_edit.setEditable(True)
        self.filter_edit.setInsertPolicy(QComboBox.NoInsert)
        self.filter_edit.lineEdit().textChanged.connect(self.apply_filter)
        search_layout.addWidget(self.filter_edit, 1)
        layout.addLayout(search_layout)
        
        # Select all / none buttons
        btn_layout = QHBoxLayout()
        self.btn_select_all = QPushButton("Select All")
        self.btn_select_all.clicked.connect(self.select_all)
        self.btn_select_none = QPushButton("Select None")
        self.btn_select_none.clicked.connect(self.select_none)
        btn_layout.addWidget(self.btn_select_all)
        btn_layout.addWidget(self.btn_select_none)
        layout.addLayout(btn_layout)
        
        # Scrollable area for checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.checkbox_container = QWidget()
        self.checkbox_layout = QVBoxLayout(self.checkbox_container)
        self.checkbox_layout.setSpacing(2)
        self.checkbox_layout.setContentsMargins(5, 5, 5, 5)
        self.checkbox_layout.addStretch()
        
        scroll.setWidget(self.checkbox_container)
        layout.addWidget(scroll, 1)
        
    def set_parameters(self, parameters: List[Dict]):
        """Set available parameters"""
        # Clear existing
        for cb in self.checkboxes:
            self.checkbox_layout.removeWidget(cb)
            cb.deleteLater()
        self.checkboxes = []
        self.parameters = parameters
        
        # Reset color assignments for new file
        self.assigned_colors = {}
        self.next_color_index = 0
        
        # Add filter suggestions
        self.filter_edit.clear()
        self.filter_edit.addItem("")
        categories = set()
        for p in parameters:
            parts = p['name'].split('/')
            if len(parts) > 2:
                categories.add(parts[1])
        for cat in sorted(categories):
            self.filter_edit.addItem(cat)
        
        # Create checkboxes
        for i, param in enumerate(parameters):
            cb = QCheckBox(param['name'])
            cb.stateChanged.connect(lambda state, idx=i: self.on_checkbox_changed(idx, state))
            self.checkbox_layout.insertWidget(i, cb)
            self.checkboxes.append(cb)
            
    def apply_filter(self, text: str):
        """Filter visible parameters"""
        text = text.lower()
        for i, cb in enumerate(self.checkboxes):
            visible = text == "" or text in self.parameters[i]['name'].lower()
            cb.setVisible(visible)
            
    def select_all(self):
        """Select all visible parameters"""
        # Block signals to prevent multiple plot updates
        for i, cb in enumerate(self.checkboxes):
            if cb.isVisible():
                cb.blockSignals(True)
                cb.setChecked(True)
                
                # Manually assign color since signal is blocked
                param_name = self.parameters[i]['name']
                if param_name not in self.assigned_colors:
                    color = PARAMETER_COLORS[self.next_color_index % len(PARAMETER_COLORS)]
                    self.assigned_colors[param_name] = color
                    self.next_color_index += 1
                
                # Set text color
                color = self.assigned_colors[param_name]
                cb.setStyleSheet(f"color: {color};")
                
                cb.blockSignals(False)
        
        # Emit a single selection changed signal after all are selected
        self.selectionChanged.emit()
                
    def select_none(self):
        """Deselect all parameters"""
        # Block signals to prevent multiple plot updates
        for cb in self.checkboxes:
            cb.blockSignals(True)
            cb.setChecked(False)
            cb.setStyleSheet("")
            cb.blockSignals(False)
        
        # Clear color assignments when all deselected
        self.assigned_colors = {}
        self.next_color_index = 0
        
        # Emit a single selection changed signal after all are deselected
        self.selectionChanged.emit()
            
    def on_checkbox_changed(self, index: int, state: int):
        """Handle checkbox state change - assign color when checked"""
        param_name = self.parameters[index]['name']
        cb = self.checkboxes[index]
        
        if state == 2:  # Qt.Checked is 2
            # Assign a new color if not already assigned
            if param_name not in self.assigned_colors:
                color = PARAMETER_COLORS[self.next_color_index % len(PARAMETER_COLORS)]
                self.assigned_colors[param_name] = color
                self.next_color_index += 1
            
            # Set text color
            color = self.assigned_colors[param_name]
            cb.setStyleSheet(f"color: {color};")
        else:
            # Reset to default color
            cb.setStyleSheet("")
        
        self.selectionChanged.emit()
        
    def get_selected_parameters(self) -> List[Dict]:
        """Get list of selected parameters with their assigned colors"""
        selected = []
        for i, cb in enumerate(self.checkboxes):
            if cb.isChecked():
                param = self.parameters[i].copy()
                param_name = param['name']
                # Get assigned color
                param['color'] = self.assigned_colors.get(param_name, '#ffffff')
                selected.append(param)
        return selected


class FileInfoWidget(QWidget):
    """Widget displaying file information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.info_label = QLabel("No file loaded")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("QLabel { background-color: #1e1e1e; padding: 10px; border-radius: 5px; }")
        layout.addWidget(self.info_label)
        
    def update_info(self, data: XDRData):
        """Update displayed information"""
        if not data.header:
            self.info_label.setText("No file loaded")
            return
            
        h = data.header
        
        # Status indicator
        if data.is_recording_complete():
            status = '<span style="color: #00ff00;">✓ Complete</span>'
            end_time = str(h.get('end_datetime', 'Unknown'))
            duration = f"{h.get('duration', 0)} seconds"
            total_frames = h.get('total_records', len(data.frames))
        else:
            status = '<span style="color: #ff6600;">● Recording...</span>'
            end_time = '<i>In progress</i>'
            # Calculate approximate duration from frames
            if data.frames:
                approx_duration = data.frames[-1]['timestamp']
                duration = f"~{approx_duration:.1f} sec (ongoing)"
            else:
                duration = "N/A"
            total_frames = f"{len(data.frames)} (so far)"
        
        try:
            file_size = Path(data.filepath).stat().st_size
            file_size_str = f"{file_size:,} bytes"
        except:
            file_size_str = "N/A"
        
        info = f"""<b>File:</b> {Path(data.filepath).name}<br>
<b>Status:</b> {status}<br>
<b>Recording Level:</b> {h.get('level_name', 'Unknown')} (Level {h.get('level', '?')})<br>
<b>Recording Interval:</b> {h.get('interval', 0):.3f} sec ({1/h.get('interval', 1):.1f} Hz)<br>
<b>Start Time:</b> {h.get('start_datetime', 'Unknown')}<br>
<b>End Time:</b> {end_time}<br>
<b>Duration:</b> {duration}<br>
<b>Total Frames:</b> {total_frames}<br>
<b>Parameters:</b> {h.get('dataref_count', 0)}<br>
<b>File Size:</b> {file_size_str}"""
        
        self.info_label.setText(info)


class DataTableWidget(QWidget):
    """Widget for displaying data in table format"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Controls
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Show frames:"))
        self.spin_start = QSpinBox()
        self.spin_start.setMinimum(0)
        self.spin_start.setValue(0)
        controls.addWidget(self.spin_start)
        controls.addWidget(QLabel("to"))
        self.spin_end = QSpinBox()
        self.spin_end.setMinimum(0)
        self.spin_end.setValue(100)
        controls.addWidget(self.spin_end)
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.refresh_table)
        controls.addWidget(self.btn_refresh)
        controls.addStretch()
        layout.addLayout(controls)
        
        # Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
    def set_data(self, data: XDRData):
        """Set data source"""
        self.data = data
        if data and data.frames:
            self.spin_start.setMaximum(len(data.frames) - 1)
            self.spin_end.setMaximum(len(data.frames) - 1)
            self.spin_end.setValue(min(100, len(data.frames) - 1))
        self.refresh_table()
        
    def refresh_table(self):
        """Refresh table contents"""
        if not self.data or not self.data.frames:
            self.table.clear()
            return
            
        start = self.spin_start.value()
        end = min(self.spin_end.value() + 1, len(self.data.frames))
        
        # Build headers
        headers = ['Frame', 'Timestamp']
        for dr in self.data.datarefs:
            if dr['array_size'] > 0:
                for i in range(dr['array_size']):
                    headers.append(f"{dr['name']}[{i}]")
            else:
                headers.append(dr['name'])
                
        self.table.setColumnCount(len(headers))
        self.table.setRowCount(end - start)
        self.table.setHorizontalHeaderLabels(headers)
        
        # Fill data
        for row, frame_idx in enumerate(range(start, end)):
            frame = self.data.frames[frame_idx]
            self.table.setItem(row, 0, QTableWidgetItem(str(frame_idx)))
            self.table.setItem(row, 1, QTableWidgetItem(f"{frame['timestamp']:.3f}"))
            
            col = 2
            for value in frame['values']:
                if isinstance(value, list):
                    for v in value:
                        self.table.setItem(row, col, QTableWidgetItem(f"{v:.4f}" if isinstance(v, float) else str(v)))
                        col += 1
                else:
                    self.table.setItem(row, col, QTableWidgetItem(f"{value:.4f}" if isinstance(value, float) else str(value)))
                    col += 1


class StatisticsWidget(QWidget):
    """Widget for displaying parameter statistics"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = None
        self.selected_params = []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title = QLabel("<b>Statistics</b>")
        title.setStyleSheet("font-size: 12pt;")
        layout.addWidget(title)
        
        # Statistics table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        # Refresh button
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh Statistics")
        self.btn_refresh.clicked.connect(self.update_statistics)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
    def set_data(self, data: XDRData, selected_params: List[Dict]):
        """Set data and update statistics"""
        self.data = data
        self.selected_params = selected_params
        self.update_statistics()
        
    def update_statistics(self):
        """Update statistics table"""
        if not self.data or not self.selected_params:
            self.table.clear()
            self.table.setRowCount(0)
            return
        
        headers = ['Parameter', 'Count', 'Min', 'Max', 'Mean', 'Median', 'Std Dev', 'Range']
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(self.selected_params))
        
        for row, param in enumerate(self.selected_params):
            stats = self.data.get_parameter_statistics(
                param['index'], param['array_index']
            )
            
            if not stats:
                continue
            
            # Parameter name
            self.table.setItem(row, 0, QTableWidgetItem(param['name']))
            
            # Statistics
            self.table.setItem(row, 1, QTableWidgetItem(str(stats['count'])))
            self.table.setItem(row, 2, QTableWidgetItem(f"{stats['min']:.4f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{stats['max']:.4f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{stats['mean']:.4f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"{stats['median']:.4f}"))
            self.table.setItem(row, 6, QTableWidgetItem(f"{stats['std']:.4f}"))
            self.table.setItem(row, 7, QTableWidgetItem(f"{stats['range']:.4f}"))
        
        self.table.resizeColumnsToContents()


class CorrelationWidget(QWidget):
    """Widget for analyzing parameter correlations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = None
        self.selected_params = []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title = QLabel("<b>Parameter Correlation Analysis</b>")
        title.setStyleSheet("font-size: 12pt;")
        layout.addWidget(title)
        
        info = QLabel("Correlation coefficient ranges from -1 (negative correlation) to +1 (positive correlation)")
        info.setWordWrap(True)
        info.setStyleSheet("color: #aaaaaa; font-size: 9pt;")
        layout.addWidget(info)
        
        # Correlation table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        # Refresh button
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Calculate Correlations")
        self.btn_refresh.clicked.connect(self.update_correlations)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
    def set_data(self, data: XDRData, selected_params: List[Dict]):
        """Set data and update correlations"""
        self.data = data
        self.selected_params = selected_params
        self.update_correlations()
        
    def update_correlations(self):
        """Update correlation matrix"""
        if not self.data or len(self.selected_params) < 2:
            self.table.clear()
            self.table.setRowCount(0)
            if len(self.selected_params) < 2:
                self.table.setColumnCount(1)
                self.table.setHorizontalHeaderLabels(['Info'])
                self.table.setRowCount(1)
                self.table.setItem(0, 0, QTableWidgetItem("Select at least 2 parameters to analyze correlations"))
            return
        
        n = len(self.selected_params)
        param_names = [p['name'] for p in self.selected_params]
        
        self.table.setColumnCount(n + 1)
        self.table.setRowCount(n)
        
        headers = ['Parameter'] + [self._short_name(name) for name in param_names]
        self.table.setHorizontalHeaderLabels(headers)
        
        for i, param1 in enumerate(self.selected_params):
            # Set row header
            self.table.setItem(i, 0, QTableWidgetItem(self._short_name(param1['name'])))
            
            for j, param2 in enumerate(self.selected_params):
                if i == j:
                    # Diagonal - perfect correlation with itself
                    item = QTableWidgetItem("1.00")
                    item.setBackground(QColor(0, 200, 0, 100))
                else:
                    # Calculate correlation
                    corr = self.data.calculate_correlation(
                        param1['index'], param1['array_index'],
                        param2['index'], param2['array_index']
                    )
                    
                    item = QTableWidgetItem(f"{corr:.3f}")
                    
                    # Color code based on correlation strength
                    abs_corr = abs(corr)
                    if abs_corr > 0.7:
                        color = QColor(0, 200, 0, 100) if corr > 0 else QColor(200, 0, 0, 100)
                    elif abs_corr > 0.4:
                        color = QColor(200, 200, 0, 80)
                    else:
                        color = QColor(100, 100, 100, 50)
                    
                    item.setBackground(color)
                
                self.table.setItem(i, j + 1, item)
        
        self.table.resizeColumnsToContents()
    
    def _short_name(self, name: str) -> str:
        """Get shortened parameter name"""
        if len(name) > 30:
            parts = name.split('/')
            if len(parts) > 2:
                return f".../{parts[-1]}"
        return name


class MainWindow(QMainWindow):
    """Main application window"""
    
    MAX_RECENT_FILES = 10
    
    def __init__(self):
        super().__init__()
        self.data = XDRData()
        self.live_mode = False
        self.time_range = None  # (start, end) or None for full range
        
        # Settings for persistent configuration
        self.settings = QSettings('XBlackBox', 'XDRViewer')
        
        # Timer for live mode updates
        self.live_timer = QTimer(self)
        self.live_timer.setInterval(500)  # 500ms refresh interval
        self.live_timer.timeout.connect(self.on_live_timer)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().endswith('.xdr'):
                event.acceptProposedAction()
                
    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                filepath = urls[0].toLocalFile()
                if filepath.endswith('.xdr'):
                    self.load_file(filepath)
                    event.acceptProposedAction()
        
    def setup_ui(self):
        self.setWindowTitle("XBlackBox XDR Viewer - Enhanced Edition")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(self.get_stylesheet())
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Parameter selection
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # File info
        self.file_info = FileInfoWidget()
        left_layout.addWidget(self.file_info)
        
        # Parameter selector
        param_group = QGroupBox("Parameters to Plot")
        param_layout = QVBoxLayout(param_group)
        self.param_selector = ParameterSelector()
        self.param_selector.selectionChanged.connect(self.update_plot)
        param_layout.addWidget(self.param_selector)
        left_layout.addWidget(param_group, 1)
        
        splitter.addWidget(left_panel)
        
        # Right panel - Tabs for plot and data
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Time range selection
        time_range_layout = QHBoxLayout()
        time_range_layout.addWidget(QLabel("Time Range:"))
        
        self.spin_time_start = QDoubleSpinBox()
        self.spin_time_start.setMinimum(0)
        self.spin_time_start.setMaximum(99999)
        self.spin_time_start.setValue(0)
        self.spin_time_start.setSuffix(" s")
        self.spin_time_start.valueChanged.connect(self.on_time_range_changed)
        time_range_layout.addWidget(self.spin_time_start)
        
        time_range_layout.addWidget(QLabel("to"))
        
        self.spin_time_end = QDoubleSpinBox()
        self.spin_time_end.setMinimum(0)
        self.spin_time_end.setMaximum(99999)
        self.spin_time_end.setValue(99999)
        self.spin_time_end.setSuffix(" s")
        self.spin_time_end.valueChanged.connect(self.on_time_range_changed)
        time_range_layout.addWidget(self.spin_time_end)
        
        self.btn_reset_time_range = QPushButton("Reset")
        self.btn_reset_time_range.clicked.connect(self.reset_time_range)
        time_range_layout.addWidget(self.btn_reset_time_range)
        
        time_range_layout.addStretch()
        right_layout.addLayout(time_range_layout)
        
        # Plot options
        options_layout = QHBoxLayout()
        
        self.cb_separate_axes = QCheckBox("Separate Axes")
        self.cb_separate_axes.stateChanged.connect(self.update_plot)
        options_layout.addWidget(self.cb_separate_axes)
        
        self.cb_grid = QCheckBox("Show Grid")
        self.cb_grid.setChecked(True)
        self.cb_grid.stateChanged.connect(self.update_plot)
        options_layout.addWidget(self.cb_grid)
        
        self.cb_derivative = QCheckBox("Plot Derivative")
        self.cb_derivative.setToolTip("Plot rate of change instead of raw values")
        self.cb_derivative.stateChanged.connect(self.update_plot)
        options_layout.addWidget(self.cb_derivative)
        
        options_layout.addSpacing(20)
        
        # Live mode checkbox
        self.cb_live_mode = QCheckBox("Live Mode (实时更新)")
        self.cb_live_mode.setStyleSheet("QCheckBox { color: #00ff00; font-weight: bold; }")
        self.cb_live_mode.stateChanged.connect(self.toggle_live_mode)
        options_layout.addWidget(self.cb_live_mode)
        
        # Live mode interval selector
        options_layout.addWidget(QLabel("Interval:"))
        self.spin_live_interval = QSpinBox()
        self.spin_live_interval.setRange(100, 5000)
        self.spin_live_interval.setValue(500)
        self.spin_live_interval.setSuffix(" ms")
        self.spin_live_interval.valueChanged.connect(self.update_live_interval)
        options_layout.addWidget(self.spin_live_interval)
        
        options_layout.addStretch()
        
        self.btn_plot = QPushButton("Update Plot")
        self.btn_plot.clicked.connect(self.update_plot)
        options_layout.addWidget(self.btn_plot)
        
        right_layout.addLayout(options_layout)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Plot tab
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        
        self.canvas = PlotCanvas(self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas, 1)
        
        self.tabs.addTab(plot_widget, "Plot")
        
        # Data table tab
        self.data_table = DataTableWidget()
        self.tabs.addTab(self.data_table, "Data Table")
        
        # Statistics tab
        self.statistics_widget = StatisticsWidget()
        self.tabs.addTab(self.statistics_widget, "Statistics")
        
        # Correlation tab
        self.correlation_widget = CorrelationWidget()
        self.tabs.addTab(self.correlation_widget, "Correlation")
        
        right_layout.addWidget(self.tabs, 1)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 900])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready - Open an XDR file or drag & drop to begin")
        
    def setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open XDR File...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        # Recent files submenu
        self.recent_files_menu = file_menu.addMenu("Recent Files")
        self.update_recent_files_menu()
        
        file_menu.addSeparator()
        
        export_csv_action = QAction("Export to &CSV...", self)
        export_csv_action.setShortcut("Ctrl+E")
        export_csv_action.triggered.connect(self.export_csv)
        file_menu.addAction(export_csv_action)
        
        export_plot_action = QAction("Save Plot &Image...", self)
        export_plot_action.setShortcut(QKeySequence.Save)
        export_plot_action.triggered.connect(self.save_plot)
        file_menu.addAction(export_plot_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        refresh_action = QAction("&Refresh Plot", self)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.triggered.connect(self.update_plot)
        view_menu.addAction(refresh_action)
        
        clear_plot_action = QAction("&Clear Plot", self)
        clear_plot_action.setShortcut("Ctrl+L")
        clear_plot_action.triggered.connect(self.canvas.clear_plots)
        view_menu.addAction(clear_plot_action)
        
        view_menu.addSeparator()
        
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_in_plot)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_out_plot)
        view_menu.addAction(zoom_out_action)
        
        # Analysis menu
        analysis_menu = menubar.addMenu("&Analysis")
        
        stats_action = QAction("Show &Statistics", self)
        stats_action.setShortcut("Ctrl+T")
        stats_action.triggered.connect(self.show_statistics_tab)
        analysis_menu.addAction(stats_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.setShortcut(QKeySequence.HelpContents)
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        open_action = QAction(self.style().standardIcon(QStyle.SP_DialogOpenButton), "Open", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        export_action = QAction(self.style().standardIcon(QStyle.SP_DialogSaveButton), "Export CSV", self)
        export_action.triggered.connect(self.export_csv)
        toolbar.addAction(export_action)
        
    def open_file(self):
        """Open XDR file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open XDR File", "", "XDR Files (*.xdr);;All Files (*)"
        )
        
        if not filepath:
            return
        
        self.load_file(filepath)
        
    def load_file(self, filepath: str):
        """Load an XDR file with progress dialog"""
        try:
            # Show progress dialog
            progress = QProgressDialog("Loading file...", "Cancel", 0, 100, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setValue(10)
            
            self.data.read(filepath)
            progress.setValue(50)
            
            # Update time range controls
            if self.data.frames:
                max_time = self.data.frames[-1]['timestamp']
                self.spin_time_start.setMaximum(max_time)
                self.spin_time_end.setMaximum(max_time)
                self.spin_time_end.setValue(max_time)
            
            progress.setValue(70)
            
            self.file_info.update_info(self.data)
            self.param_selector.set_parameters(self.data.get_all_plottable_parameters())
            self.data_table.set_data(self.data)
            self.canvas.clear_plots()
            self.time_range = None
            
            progress.setValue(90)
            
            # Add to recent files
            self.add_recent_file(filepath)
            
            progress.setValue(100)
            progress.close()
            
            self.statusBar().showMessage(f"Loaded: {filepath} ({len(self.data.frames)} frames)")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")
    
    def add_recent_file(self, filepath: str):
        """Add file to recent files list"""
        recent = self.settings.value('recent_files', [])
        if not isinstance(recent, list):
            recent = []
        
        # Remove if already in list
        if filepath in recent:
            recent.remove(filepath)
        
        # Add to front
        recent.insert(0, filepath)
        
        # Keep only MAX_RECENT_FILES
        recent = recent[:self.MAX_RECENT_FILES]
        
        self.settings.setValue('recent_files', recent)
        self.update_recent_files_menu()
    
    def update_recent_files_menu(self):
        """Update recent files menu"""
        self.recent_files_menu.clear()
        
        recent = self.settings.value('recent_files', [])
        if not isinstance(recent, list):
            recent = []
        
        if not recent:
            action = QAction("No recent files", self)
            action.setEnabled(False)
            self.recent_files_menu.addAction(action)
            return
        
        for filepath in recent:
            if Path(filepath).exists():
                action = QAction(Path(filepath).name, self)
                action.setToolTip(filepath)
                action.triggered.connect(partial(self.load_file, filepath))
                self.recent_files_menu.addAction(action)
    
    def on_time_range_changed(self):
        """Handle time range change"""
        start = self.spin_time_start.value()
        end = self.spin_time_end.value()
        
        if start >= end:
            return
        
        if self.data.frames:
            max_time = self.data.frames[-1]['timestamp']
            if start == 0 and end >= max_time:
                self.time_range = None
            else:
                self.time_range = (start, end)
    
    def reset_time_range(self):
        """Reset time range to full range"""
        self.time_range = None
        self.spin_time_start.setValue(0)
        if self.data.frames:
            self.spin_time_end.setValue(self.data.frames[-1]['timestamp'])
        self.update_plot()
    
    def zoom_in_plot(self):
        """Zoom in on plot"""
        if self.time_range:
            start, end = self.time_range
            duration = end - start
            new_duration = duration * 0.75
            center = (start + end) / 2
            self.spin_time_start.setValue(center - new_duration / 2)
            self.spin_time_end.setValue(center + new_duration / 2)
            self.on_time_range_changed()
            self.update_plot()
    
    def zoom_out_plot(self):
        """Zoom out on plot"""
        if self.data.frames:
            if self.time_range:
                start, end = self.time_range
                duration = end - start
                new_duration = min(duration * 1.25, self.data.frames[-1]['timestamp'])
                center = (start + end) / 2
                self.spin_time_start.setValue(max(0, center - new_duration / 2))
                self.spin_time_end.setValue(min(self.data.frames[-1]['timestamp'], center + new_duration / 2))
                self.on_time_range_changed()
                self.update_plot()
    
    def show_statistics_tab(self):
        """Show statistics tab"""
        self.tabs.setCurrentIndex(2)  # Statistics tab
        selected = self.param_selector.get_selected_parameters()
        if selected:
            self.statistics_widget.set_data(self.data, selected)
            
    def update_plot(self):
        """Update the plot with selected parameters"""
        selected = self.param_selector.get_selected_parameters()
        
        if not selected:
            self.canvas.clear_plots()
            return
        
        # Update statistics if on stats tab
        if self.tabs.currentIndex() == 2:
            self.statistics_widget.set_data(self.data, selected)
        
        # Update correlation if on correlation tab
        if self.tabs.currentIndex() == 3:
            self.correlation_widget.set_data(self.data, selected)
            
        self.canvas.plot_parameters(
            self.data,
            selected,
            separate_axes=self.cb_separate_axes.isChecked(),
            show_grid=self.cb_grid.isChecked(),
            time_range=self.time_range,
            plot_derivative=self.cb_derivative.isChecked()
        )
        
        mode = "derivative" if self.cb_derivative.isChecked() else "value"
        self.statusBar().showMessage(f"Plotting {len(selected)} parameter(s) ({mode} mode)")
        
    def show_shortcuts(self):
        """Show keyboard shortcuts help"""
        shortcuts_text = """
        <h3>Keyboard Shortcuts</h3>
        <table cellpadding="5">
        <tr><td><b>Ctrl+O</b></td><td>Open File</td></tr>
        <tr><td><b>Ctrl+E</b></td><td>Export to CSV</td></tr>
        <tr><td><b>Ctrl+S</b></td><td>Save Plot Image</td></tr>
        <tr><td><b>Ctrl+Q</b></td><td>Quit Application</td></tr>
        <tr><td><b>F5</b></td><td>Refresh Plot</td></tr>
        <tr><td><b>Ctrl+L</b></td><td>Clear Plot</td></tr>
        <tr><td><b>Ctrl++</b></td><td>Zoom In</td></tr>
        <tr><td><b>Ctrl+-</b></td><td>Zoom Out</td></tr>
        <tr><td><b>Ctrl+T</b></td><td>Show Statistics</td></tr>
        <tr><td><b>F1</b></td><td>Help</td></tr>
        </table>
        """
        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts_text)
        
    def toggle_live_mode(self, state):
        """Toggle live mode on/off"""
        self.live_mode = state == 2  # Qt.Checked is 2
        
        if self.live_mode:
            if not self.data.filepath:
                QMessageBox.warning(self, "Warning", "Please open an XDR file first.")
                self.cb_live_mode.setChecked(False)
                return
            self.live_timer.start()
            self.statusBar().showMessage(f"Live mode enabled - refreshing every {self.spin_live_interval.value()}ms")
        else:
            self.live_timer.stop()
            self.statusBar().showMessage("Live mode disabled")
            
    def update_live_interval(self, value):
        """Update live mode refresh interval"""
        self.live_timer.setInterval(value)
        if self.live_mode:
            self.statusBar().showMessage(f"Live mode - refreshing every {value}ms")
            
    def on_live_timer(self):
        """Called periodically in live mode to check for new data"""
        if not self.data.filepath:
            return
            
        # Read new frames
        new_frames = self.data.read_new_frames()
        
        if new_frames > 0:
            # Update info display
            self.file_info.update_info(self.data)
            
            # Update table data range
            if self.data.frames:
                self.data_table.spin_start.setMaximum(len(self.data.frames) - 1)
                self.data_table.spin_end.setMaximum(len(self.data.frames) - 1)
            
            # Update plot
            self.update_plot()
            
            self.statusBar().showMessage(
                f"Live: {len(self.data.frames)} frames (+{new_frames})"
            )
            
        # Check if recording is complete
        if self.data.is_recording_complete():
            self.cb_live_mode.setChecked(False)
            self.file_info.update_info(self.data)
            self.statusBar().showMessage(
                f"Recording complete - {len(self.data.frames)} frames total"
            )
        
    def export_csv(self):
        """Export data to CSV"""
        if not self.data.frames:
            QMessageBox.warning(self, "Warning", "No data to export. Please open an XDR file first.")
            return
            
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if filepath:
            try:
                self.data.export_to_csv(filepath)
                self.statusBar().showMessage(f"Exported to: {filepath}")
                QMessageBox.information(self, "Success", f"Data exported to:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export:\n{str(e)}")
                
    def save_plot(self):
        """Save plot as image"""
        if not self.param_selector.get_selected_parameters():
            QMessageBox.warning(self, "Warning", "No plot to save. Please select parameters first.")
            return
            
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Plot", "", "PNG Image (*.png);;PDF Document (*.pdf);;SVG Image (*.svg)"
        )
        
        if filepath:
            try:
                self.canvas.fig.savefig(filepath, dpi=150, bbox_inches='tight',
                                        facecolor='#2b2b2b', edgecolor='none')
                self.statusBar().showMessage(f"Plot saved to: {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save plot:\n{str(e)}")
                
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About XBlackBox XDR Viewer",
            """<h3>XBlackBox XDR Viewer - Enhanced Edition</h3>
            <p>Version 2.0</p>
            <p>A tool for visualizing X-Plane flight data recordings from XBlackBox plugin.</p>
            <p><b>Features:</b></p>
            <ul>
                <li>Open and parse .xdr flight data files</li>
                <li>Plot any recorded parameter over time with auto-downsampling</li>
                <li>Live mode for real-time monitoring</li>
                <li>Time range selection and zoom controls</li>
                <li>Statistical analysis (min/max/mean/median/std)</li>
                <li>Compare multiple parameters with color coding</li>
                <li>Export data to CSV format</li>
                <li>Save plots as images (PNG/PDF/SVG)</li>
                <li>Recent files menu</li>
                <li>Drag and drop file opening</li>
                <li>Keyboard shortcuts for efficiency</li>
            </ul>
            <p><b>Performance Optimizations:</b></p>
            <ul>
                <li>Automatic data downsampling for large datasets</li>
                <li>Efficient memory usage</li>
                <li>Fast plot rendering</li>
            </ul>
            """
        )
        
    def get_stylesheet(self):
        """Get application stylesheet"""
        return """
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMenuBar {
                background-color: #1e1e1e;
            }
            QMenuBar::item:selected {
                background-color: #3d3d3d;
            }
            QMenu {
                background-color: #1e1e1e;
                border: 1px solid #3d3d3d;
            }
            QMenu::item:selected {
                background-color: #3d3d3d;
            }
            QToolBar {
                background-color: #1e1e1e;
                border: none;
                spacing: 5px;
            }
            QStatusBar {
                background-color: #1e1e1e;
            }
            QGroupBox {
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #3d3d3d;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 3px;
            }
            QScrollArea {
                border: 1px solid #3d3d3d;
                border-radius: 4px;
            }
            QTableWidget {
                background-color: #1e1e1e;
                alternate-background-color: #252525;
                gridline-color: #3d3d3d;
            }
            QHeaderView::section {
                background-color: #2b2b2b;
                border: 1px solid #3d3d3d;
                padding: 4px;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
            }
            QTabBar::tab {
                background-color: #1e1e1e;
                border: 1px solid #3d3d3d;
                padding: 8px 16px;
            }
            QTabBar::tab:selected {
                background-color: #2b2b2b;
                border-bottom-color: #2b2b2b;
            }
            QSplitter::handle {
                background-color: #3d3d3d;
            }
        """


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    # If a file was passed as argument, open it
    if len(sys.argv) > 1:
        window.data.read(sys.argv[1])
        window.file_info.update_info(window.data)
        window.param_selector.set_parameters(window.data.get_all_plottable_parameters())
        window.data_table.set_data(window.data)
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
