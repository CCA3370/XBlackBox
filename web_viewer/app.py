#!/usr/bin/env python3
"""
XBlackBox Web-based XDR Viewer
Flask backend server for the web interface
"""

import sys
import struct
import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Global data storage
current_data = None


class XDRData:
    """Container for XDR file data"""
    
    def __init__(self):
        self.filepath = ""
        self.header = {}
        self.datarefs = []
        self.frames = []
        self._is_complete = False
        
    def clear(self):
        self.filepath = ""
        self.header = {}
        self.datarefs = []
        self.frames = []
        self._is_complete = False
        
    def read(self, filepath: str):
        """Read the entire XDR file"""
        self.clear()
        self.filepath = filepath
        
        with open(filepath, 'rb') as f:
            self._read_header(f)
            self._read_dataref_definitions(f)
            self._read_frames(f)
            self._try_read_footer(f)
            
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
            'start_datetime': datetime.fromtimestamp(start_timestamp).isoformat(),
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
        """Read all data frames"""
        while True:
            marker = f.read(4)
            if len(marker) < 4:
                break
            if marker == b'ENDR':
                f.seek(-4, 1)
                break
            if marker != b'DATA':
                f.seek(-4, 1)
                break
                
            ts_data = f.read(4)
            if len(ts_data) < 4:
                break
                
            timestamp = struct.unpack('<f', ts_data)[0]
            
            try:
                values = self._read_frame_values(f)
                self.frames.append({
                    'timestamp': timestamp,
                    'values': values
                })
            except:
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
        
    def _try_read_footer(self, f):
        """Try to read file footer"""
        try:
            marker = f.read(4)
            if marker == b'ENDR':
                self._is_complete = True
                total_records = struct.unpack('<I', f.read(4))[0]
                end_timestamp = struct.unpack('<Q', f.read(8))[0]
                
                self.header['total_records'] = total_records
                self.header['end_timestamp'] = end_timestamp
                self.header['end_datetime'] = datetime.fromtimestamp(end_timestamp).isoformat()
                self.header['duration'] = end_timestamp - self.header['start_timestamp']
        except:
            pass
            
    def get_parameter_data(self, dataref_index: int, array_index: int = 0, 
                          time_range: Optional[tuple] = None, 
                          downsample_factor: int = 1) -> tuple:
        """Get timestamps and values for a specific parameter"""
        timestamps = []
        values = []
        
        dr = self.datarefs[dataref_index]
        
        for i, frame in enumerate(self.frames):
            if i % downsample_factor != 0:
                continue
                
            timestamp = frame['timestamp']
            
            if time_range:
                if timestamp < time_range[0] or timestamp > time_range[1]:
                    continue
            
            timestamps.append(timestamp)
            value = frame['values'][dataref_index]
            
            if dr['array_size'] > 0:
                values.append(value[array_index])
            else:
                if dr['type'] == 'string':
                    values.append(0)
                else:
                    values.append(value)
                    
        return timestamps, values
        
    def get_parameter_statistics(self, dataref_index: int, array_index: int = 0) -> Dict:
        """Calculate statistics for a parameter"""
        timestamps, values = self.get_parameter_data(dataref_index, array_index)
        
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
    
    def get_parameter_fft(self, dataref_index: int, array_index: int = 0) -> tuple:
        """Calculate FFT of a parameter"""
        timestamps, values = self.get_parameter_data(dataref_index, array_index)
        
        if len(timestamps) < 4:
            return [], []
        
        values_array = np.array(values)
        n = len(values_array)
        values_array = values_array - np.mean(values_array)
        window = np.hanning(n)
        values_windowed = values_array * window
        fft = np.fft.rfft(values_windowed)
        
        timestamps_array = np.array(timestamps)
        sample_rate = 1.0 / np.mean(np.diff(timestamps_array))
        frequencies = np.fft.rfftfreq(n, d=1.0/sample_rate)
        magnitude = np.abs(fft) / n
        
        return frequencies[1:].tolist(), magnitude[1:].tolist()
    
    def calculate_correlation(self, param1_index: int, param1_array_idx: int,
                             param2_index: int, param2_array_idx: int) -> float:
        """Calculate correlation between two parameters"""
        _, values1 = self.get_parameter_data(param1_index, param1_array_idx)
        _, values2 = self.get_parameter_data(param2_index, param2_array_idx)
        
        if len(values1) != len(values2) or len(values1) < 2:
            return 0.0
        
        return float(np.corrcoef(values1, values2)[0, 1])


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/load', methods=['POST'])
def load_file():
    global current_data
    
    data = request.get_json()
    filepath = data.get('filepath')
    
    if not filepath:
        return jsonify({'error': 'No file path provided'}), 400
    
    if not os.path.exists(filepath):
        return jsonify({'error': f'File not found: {filepath}'}), 404
    
    try:
        current_data = XDRData()
        current_data.read(filepath)
        
        return jsonify({
            'success': True,
            'header': current_data.header,
            'parameters': current_data.get_all_plottable_parameters(),
            'frame_count': len(current_data.frames)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    global current_data
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save uploaded file temporarily
    upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, file.filename)
    file.save(filepath)
    
    try:
        current_data = XDRData()
        current_data.read(filepath)
        
        return jsonify({
            'success': True,
            'header': current_data.header,
            'parameters': current_data.get_all_plottable_parameters(),
            'frame_count': len(current_data.frames)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/data', methods=['POST'])
def get_data():
    global current_data
    
    if current_data is None:
        return jsonify({'error': 'No file loaded'}), 400
    
    data = request.get_json()
    params = data.get('parameters', [])
    downsample = data.get('downsample', 1)
    time_range = data.get('time_range')
    
    result = {}
    
    for param in params:
        idx = param['index']
        arr_idx = param.get('array_index', 0)
        
        tr = None
        if time_range:
            tr = (time_range[0], time_range[1])
        
        timestamps, values = current_data.get_parameter_data(idx, arr_idx, tr, downsample)
        
        result[param['name']] = {
            'timestamps': timestamps,
            'values': values
        }
    
    return jsonify(result)


@app.route('/api/statistics', methods=['POST'])
def get_statistics():
    global current_data
    
    if current_data is None:
        return jsonify({'error': 'No file loaded'}), 400
    
    data = request.get_json()
    params = data.get('parameters', [])
    
    result = []
    
    for param in params:
        idx = param['index']
        arr_idx = param.get('array_index', 0)
        
        stats = current_data.get_parameter_statistics(idx, arr_idx)
        stats['name'] = param['name']
        result.append(stats)
    
    return jsonify(result)


@app.route('/api/fft', methods=['POST'])
def get_fft():
    global current_data
    
    if current_data is None:
        return jsonify({'error': 'No file loaded'}), 400
    
    data = request.get_json()
    idx = data.get('index', 0)
    arr_idx = data.get('array_index', 0)
    
    frequencies, magnitudes = current_data.get_parameter_fft(idx, arr_idx)
    
    return jsonify({
        'frequencies': frequencies,
        'magnitudes': magnitudes
    })


@app.route('/api/correlation', methods=['POST'])
def get_correlation():
    global current_data
    
    if current_data is None:
        return jsonify({'error': 'No file loaded'}), 400
    
    data = request.get_json()
    params = data.get('parameters', [])
    
    n = len(params)
    matrix = []
    
    for i, p1 in enumerate(params):
        row = []
        for j, p2 in enumerate(params):
            if i == j:
                row.append(1.0)
            else:
                corr = current_data.calculate_correlation(
                    p1['index'], p1.get('array_index', 0),
                    p2['index'], p2.get('array_index', 0)
                )
                row.append(corr)
        matrix.append(row)
    
    return jsonify({
        'matrix': matrix,
        'names': [p['name'] for p in params]
    })


@app.route('/api/table', methods=['POST'])
def get_table_data():
    global current_data
    
    if current_data is None:
        return jsonify({'error': 'No file loaded'}), 400
    
    data = request.get_json()
    start = data.get('start', 0)
    count = data.get('count', 100)
    
    end = min(start + count, len(current_data.frames))
    
    rows = []
    for i in range(start, end):
        frame = current_data.frames[i]
        row = {
            'index': i,
            'timestamp': frame['timestamp'],
            'values': []
        }
        for value in frame['values']:
            if isinstance(value, list):
                row['values'].extend(value)
            else:
                row['values'].append(value)
        rows.append(row)
    
    # Build headers
    headers = ['Index', 'Timestamp']
    for dr in current_data.datarefs:
        if dr['array_size'] > 0:
            for j in range(dr['array_size']):
                headers.append(f"{dr['name']}[{j}]")
        else:
            headers.append(dr['name'])
    
    return jsonify({
        'headers': headers,
        'rows': rows,
        'total': len(current_data.frames)
    })


@app.route('/api/flight-path', methods=['GET'])
def get_flight_path():
    global current_data
    
    if current_data is None:
        return jsonify({'error': 'No file loaded'}), 400
    
    # Find latitude, longitude, altitude
    lat_idx = lon_idx = alt_idx = None
    
    for i, dr in enumerate(current_data.datarefs):
        name = dr['name'].lower()
        if 'latitude' in name:
            lat_idx = i
        elif 'longitude' in name:
            lon_idx = i
        elif ('elevation' in name or 'altitude' in name) and 'agl' not in name:
            alt_idx = i
    
    if lat_idx is None or lon_idx is None or alt_idx is None:
        return jsonify({'error': 'Position data not found'}), 404
    
    # Extract data with downsampling
    downsample = max(1, len(current_data.frames) // 1000)
    
    lats = []
    lons = []
    alts = []
    times = []
    
    for i, frame in enumerate(current_data.frames):
        if i % downsample != 0:
            continue
        times.append(frame['timestamp'])
        lats.append(frame['values'][lat_idx])
        lons.append(frame['values'][lon_idx])
        alts.append(frame['values'][alt_idx])
    
    return jsonify({
        'latitudes': lats,
        'longitudes': lons,
        'altitudes': alts,
        'timestamps': times
    })


@app.route('/api/export-csv', methods=['GET'])
def export_csv():
    global current_data
    
    if current_data is None:
        return jsonify({'error': 'No file loaded'}), 400
    
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    header_row = ['timestamp']
    for dr in current_data.datarefs:
        if dr['array_size'] > 0:
            for i in range(dr['array_size']):
                header_row.append(f"{dr['name']}[{i}]")
        else:
            header_row.append(dr['name'])
    writer.writerow(header_row)
    
    # Data
    for frame in current_data.frames:
        row = [frame['timestamp']]
        for value in frame['values']:
            if isinstance(value, list):
                row.extend(value)
            else:
                row.append(value)
        writer.writerow(row)
    
    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=export.csv'}
    )


if __name__ == '__main__':
    print("Starting XBlackBox Web Viewer...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
