#!/usr/bin/env python3
"""
XBlackBox XDR File Reader
Reads and exports X-Plane Data Recorder (.xdr) binary files
"""

import struct
import sys
import argparse
import csv
from datetime import datetime
from pathlib import Path


class XDRReader:
    """Reader for XBlackBox .xdr files"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.header = {}
        self.datarefs = []
        self.frames = []
        
    def read(self):
        """Read the entire XDR file"""
        with open(self.filepath, 'rb') as f:
            self._read_header(f)
            self._read_dataref_definitions(f)
            self._read_frames(f)
            self._read_footer(f)
            
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
        """Read all data frames"""
        while True:
            marker = f.read(4)
            if marker == b'ENDR':
                # Rewind to read footer properly
                f.seek(-4, 1)
                break
            if marker != b'DATA':
                raise ValueError(f"Invalid frame marker: {marker}")
                
            timestamp = struct.unpack('<f', f.read(4))[0]
            values = self._read_frame_values(f)
            
            self.frames.append({
                'timestamp': timestamp,
                'values': values
            })
            
    def _read_frame_values(self, f):
        """Read values for one frame"""
        values = []
        for dr in self.datarefs:
            if dr['array_size'] > 0:
                # Read array
                arr = []
                for _ in range(dr['array_size']):
                    if dr['type'] == 'float':
                        arr.append(struct.unpack('<f', f.read(4))[0])
                    elif dr['type'] == 'int':
                        arr.append(struct.unpack('<i', f.read(4))[0])
                values.append(arr)
            else:
                # Read single value
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
        
    def _read_footer(self, f):
        """Read file footer"""
        marker = f.read(4)
        if marker != b'ENDR':
            raise ValueError(f"Invalid footer marker: {marker}")
            
        total_records = struct.unpack('<I', f.read(4))[0]
        end_timestamp = struct.unpack('<Q', f.read(8))[0]
        
        self.header['total_records'] = total_records
        self.header['end_timestamp'] = end_timestamp
        self.header['end_datetime'] = datetime.fromtimestamp(end_timestamp)
        self.header['duration'] = end_timestamp - self.header['start_timestamp']
        
    def print_summary(self):
        """Print file summary"""
        print(f"\n{'='*60}")
        print(f"XBlackBox XDR File Summary")
        print(f"{'='*60}")
        print(f"File: {self.filepath}")
        print(f"\nHeader Information:")
        print(f"  Format Version: {self.header['version']}")
        print(f"  Recording Level: {self.header['level']} ({self._get_level_name()})")
        print(f"  Recording Interval: {self.header['interval']:.3f} sec ({1/self.header['interval']:.1f} Hz)")
        print(f"  Start Time: {self.header['start_datetime']}")
        print(f"  End Time: {self.header['end_datetime']}")
        print(f"  Duration: {self.header['duration']} seconds")
        print(f"\nData:")
        print(f"  Total Datarefs: {self.header['dataref_count']}")
        print(f"  Total Frames: {self.header['total_records']}")
        print(f"  File Size: {Path(self.filepath).stat().st_size:,} bytes")
        print(f"{'='*60}\n")
        
    def _get_level_name(self):
        """Get recording level name"""
        levels = {1: 'Simple', 2: 'Normal', 3: 'Detailed'}
        return levels.get(self.header['level'], 'Unknown')
        
    def print_datarefs(self):
        """Print all dataref definitions"""
        print(f"\n{'='*60}")
        print(f"Recorded Datarefs ({len(self.datarefs)})")
        print(f"{'='*60}")
        for i, dr in enumerate(self.datarefs):
            array_info = f"[{dr['array_size']}]" if dr['array_size'] > 0 else ""
            print(f"{i:3d}. {dr['name']:<60} {dr['type']:>8}{array_info}")
        print(f"{'='*60}\n")
        
    def print_frame(self, frame_index):
        """Print values for a specific frame"""
        if frame_index < 0 or frame_index >= len(self.frames):
            print(f"Error: Frame index {frame_index} out of range (0-{len(self.frames)-1})")
            return
            
        frame = self.frames[frame_index]
        print(f"\n{'='*60}")
        print(f"Frame {frame_index} Values (timestamp: {frame['timestamp']:.3f}s)")
        print(f"{'='*60}")
        
        for i, dr in enumerate(self.datarefs):
            value = frame['values'][i]
            if isinstance(value, list):
                value_str = '[' + ', '.join(f"{v:.3f}" if isinstance(v, float) else str(v) for v in value) + ']'
            elif isinstance(value, float):
                value_str = f"{value:.6f}"
            else:
                value_str = str(value)
            print(f"{dr['name']:<60} = {value_str}")
        print(f"{'='*60}\n")
        
    def export_to_csv(self, output_path):
        """Export data to CSV file"""
        with open(output_path, 'w', newline='') as csvfile:
            # Build header row
            header_row = ['timestamp']
            for dr in self.datarefs:
                if dr['array_size'] > 0:
                    for i in range(dr['array_size']):
                        header_row.append(f"{dr['name']}[{i}]")
                else:
                    header_row.append(dr['name'])
                    
            writer = csv.writer(csvfile)
            writer.writerow(header_row)
            
            # Write data rows
            for frame in self.frames:
                row = [frame['timestamp']]
                for value in frame['values']:
                    if isinstance(value, list):
                        row.extend(value)
                    else:
                        row.append(value)
                writer.writerow(row)
                
        print(f"Exported {len(self.frames)} frames to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Read and export XBlackBox XDR files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show summary
  python xdr_reader.py recording.xdr
  
  # List all datarefs
  python xdr_reader.py recording.xdr --datarefs
  
  # Show first frame values
  python xdr_reader.py recording.xdr --frame 0
  
  # Export to CSV
  python xdr_reader.py recording.xdr --export output.csv
  
  # Show everything
  python xdr_reader.py recording.xdr --all
        """
    )
    
    parser.add_argument('file', help='XDR file to read')
    parser.add_argument('--datarefs', action='store_true', help='List all recorded datarefs')
    parser.add_argument('--frame', type=int, metavar='N', help='Show values for frame N')
    parser.add_argument('--export', metavar='FILE', help='Export data to CSV file')
    parser.add_argument('--all', action='store_true', help='Show all information')
    
    args = parser.parse_args()
    
    try:
        reader = XDRReader(args.file)
        reader.read()
        
        # Always show summary
        reader.print_summary()
        
        if args.all or args.datarefs:
            reader.print_datarefs()
            
        if args.all and len(reader.frames) > 0:
            reader.print_frame(0)
        elif args.frame is not None:
            reader.print_frame(args.frame)
            
        if args.export:
            reader.export_to_csv(args.export)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
        
    return 0


if __name__ == '__main__':
    sys.exit(main())
