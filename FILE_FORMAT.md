# XBlackBox Flight Data Recorder File Format (.xdr)

This document describes the binary file format used by XBlackBox for storing flight data recordings.

## Overview

The `.xdr` (X-Plane Data Recorder) format is a binary format optimized for:
- **Compact storage**: Efficient binary encoding
- **Fast I/O**: Sequential write with minimal overhead, buffered writes (64KB buffer)
- **Self-describing**: Contains metadata about recorded parameters
- **Platform-independent**: Little-endian byte order

## File Structure

```
┌──────────────────┐
│ File Header      │
├──────────────────┤
│ Dataref Defs     │
├──────────────────┤
│ Data Frame 1     │
├──────────────────┤
│ Data Frame 2     │
├──────────────────┤
│ ...              │
├──────────────────┤
│ Data Frame N     │
├──────────────────┤
│ File Footer      │
└──────────────────┘
```

## File Header

The file header contains metadata about the recording.

### Version 2 Format (Current)

| Offset | Size | Type   | Description                          |
|--------|------|--------|--------------------------------------|
| 0      | 4    | char[] | Magic number "XFDR"                 |
| 4      | 2    | uint16 | Format version (2 for airport info) |
| 6      | 1    | uint8  | Recording level (1-3)                |
| 7      | 4    | float  | Recording interval (seconds)         |
| 11     | 8    | uint64 | Start timestamp (Unix time)          |
| 19     | 8    | char[] | Departure airport ICAO code          |
| 27     | 4    | float  | Departure airport latitude           |
| 31     | 4    | float  | Departure airport longitude          |
| 35     | 256  | char[] | Departure airport name               |
| 291    | 8    | char[] | Arrival airport ICAO code            |
| 299    | 4    | float  | Arrival airport latitude             |
| 303    | 4    | float  | Arrival airport longitude            |
| 307    | 256  | char[] | Arrival airport name                 |
| 563    | 2    | uint16 | Number of datarefs (N)               |

**Note**: Airport fields are null-padded. If no airport is detected (aircraft not within 5 nm of any airport), the ICAO field will be empty (all zeros).

### Version 1 Format (Legacy)

| Offset | Size | Type   | Description                    |
|--------|------|--------|--------------------------------|
| 0      | 4    | char[] | Magic number "XFDR"           |
| 4      | 2    | uint16 | Format version (1)             |
| 6      | 1    | uint8  | Recording level (1-3)          |
| 7      | 4    | float  | Recording interval (seconds)   |
| 11     | 8    | uint64 | Start timestamp (Unix time)    |
| 19     | 2    | uint16 | Number of datarefs (N)         |

### Recording Levels

- **1 = Simple**: Basic flight data (~25 datarefs)
- **2 = Normal**: + Controls & systems (~70 datarefs)
- **3 = Detailed**: Everything (~180+ datarefs)

## Dataref Definitions

Following the header, each dataref is defined. There are N definitions total (from header).

**For each dataref:**

| Size | Type   | Description                              |
|------|--------|------------------------------------------|
| 2    | uint16 | Name length (L)                          |
| L    | char[] | Dataref name (e.g., "sim/flightmodel/position/latitude") |
| 1    | uint8  | Data type: 0=float, 1=int, 2=string      |
| 1    | uint8  | Array size (0 for non-array, 1-255 for arrays) |

### Data Types

- **0 (float)**: IEEE 754 single-precision (4 bytes per value)
- **1 (int)**: Signed 32-bit integer (4 bytes per value)
- **2 (string)**: Variable length string (1 byte length + data)

### Example Dataref Definition

```
Name: "sim/flightmodel/position/latitude"
Name length: 37 (0x25 0x00)
Name bytes: "sim/flightmodel/position/latitude"
Type: 0 (float)
Array size: 0 (not an array)
```

## Data Frames

Each data frame contains values for all datarefs at a specific point in time.

### Frame Structure

| Size | Type   | Description                           |
|------|--------|---------------------------------------|
| 4    | char[] | Frame marker "DATA"                   |
| 4    | float  | Timestamp (seconds since recording start) |
| var  | mixed  | Values for all datarefs in order      |

### Value Encoding

Values are encoded based on their type defined in the dataref definitions:

**Float (type 0):**
- 4 bytes per value
- IEEE 754 single-precision, little-endian

**Integer (type 1):**
- 4 bytes per value
- Signed 32-bit, little-endian

**String (type 2):**
- 1 byte: string length (0-255)
- N bytes: string data (UTF-8, no null terminator)

**Arrays:**
- Array values are written sequentially
- Example: array size 8 means 8 consecutive values

### Example Frame

For datarefs:
1. latitude (float)
2. longitude (float)
3. altitude (float)
4. throttle[8] (float array, size 8)

Frame data:
```
"DATA"              # 4 bytes: Frame marker
10.5                # 4 bytes: Timestamp (10.5 seconds)
37.7749            # 4 bytes: latitude
-122.4194          # 4 bytes: longitude
500.0              # 4 bytes: altitude
0.75               # 4 bytes: throttle[0]
0.75               # 4 bytes: throttle[1]
0.0                # 4 bytes: throttle[2]
...                # throttle[3] through throttle[7]
```

## File Footer

The footer marks the end of the recording and provides summary information.

| Size | Type   | Description                    |
|------|--------|--------------------------------|
| 4    | char[] | Footer marker "ENDR"           |
| 4    | uint32 | Total number of data frames    |
| 8    | uint64 | End timestamp (Unix time)      |

## Reading Algorithm

```python
def read_xdr_file(filename):
    with open(filename, 'rb') as f:
        # Read header
        magic = f.read(4)  # Should be b'XFDR'
        version = read_uint16(f)
        level = read_uint8(f)
        interval = read_float(f)
        start_time = read_uint64(f)
        dataref_count = read_uint16(f)
        
        # Read dataref definitions
        datarefs = []
        for i in range(dataref_count):
            name_len = read_uint16(f)
            name = f.read(name_len).decode('utf-8')
            data_type = read_uint8(f)
            array_size = read_uint8(f)
            datarefs.append({
                'name': name,
                'type': data_type,
                'array_size': array_size
            })
        
        # Read data frames
        frames = []
        while True:
            marker = f.read(4)
            if marker == b'ENDR':
                break
            if marker != b'DATA':
                raise ValueError("Invalid frame marker")
            
            timestamp = read_float(f)
            values = []
            
            for dr in datarefs:
                if dr['array_size'] > 0:
                    # Read array
                    arr = []
                    for j in range(dr['array_size']):
                        arr.append(read_value(f, dr['type']))
                    values.append(arr)
                else:
                    # Read single value
                    values.append(read_value(f, dr['type']))
            
            frames.append({
                'timestamp': timestamp,
                'values': values
            })
        
        # Read footer
        total_frames = read_uint32(f)
        end_time = read_uint64(f)
        
        return {
            'header': {...},
            'datarefs': datarefs,
            'frames': frames,
            'footer': {...}
        }
```

## File Size Estimation

### Per-Frame Size

**Simple Level (~25 datarefs, mostly floats):**
- Frame marker: 4 bytes
- Timestamp: 4 bytes
- Values: ~25 × 4 = 100 bytes
- **Total: ~108 bytes per frame**

**Normal Level (~70 datarefs):**
- Frame marker: 4 bytes
- Timestamp: 4 bytes
- Values: ~70 × 4 + ~40 array values × 4 = 440 bytes
- **Total: ~448 bytes per frame**

**Detailed Level (~180 datarefs):**
- Frame marker: 4 bytes
- Timestamp: 4 bytes
- Values: ~180 × 4 + ~80 array values × 4 = 1040 bytes
- **Total: ~1048 bytes per frame**

### Storage Requirements

At 4 Hz (default, 0.25 second interval):

| Level    | Per Second | Per Minute | Per Hour |
|----------|------------|------------|----------|
| Simple   | 432 B      | 25 KB      | 1.5 MB   |
| Normal   | 1.8 KB     | 105 KB     | 6.2 MB   |
| Detailed | 4.2 KB     | 246 KB     | 14.4 MB  |

At 20 Hz (fastest, 0.05 second interval):

| Level    | Per Second | Per Minute | Per Hour |
|----------|------------|------------|----------|
| Simple   | 2.2 KB     | 127 KB     | 7.5 MB   |
| Normal   | 9.0 KB     | 526 KB     | 30.8 MB  |
| Detailed | 21 KB      | 1.2 MB     | 72 MB    |

## Performance Optimizations

The C++ implementation includes several optimizations:

1. **Buffered I/O**: 64KB write buffer with periodic flushing (every 10 records)
2. **Efficient Dataref Access**: Cached dataref references, batch reading
3. **Native Performance**: C++ provides better performance than interpreted languages
4. **Memory Efficiency**: Pre-allocated buffers, minimal allocations during recording
5. **Direct Binary Writing**: Optimized little-endian serialization

## Notes

- All multi-byte integers use little-endian byte order
- Floats use IEEE 754 single-precision format
- Strings use UTF-8 encoding
- No compression is applied (future versions may add optional compression)
- File extension is `.xdr` (X-Plane Data Recorder)
- Magic number remains "XFDR" for compatibility with existing readers

## Airport Detection (Version 2+)

Starting with version 2, the file format includes automatic airport detection:

- **Departure Airport**: Automatically detected when recording starts
- **Arrival Airport**: Automatically detected when recording stops
- **Detection Range**: Airports within 5 nautical miles of the aircraft
- **Information Stored**: ICAO code, full name, latitude, and longitude

The airport detection uses X-Plane's navigation database API to find the nearest airport. This feature helps identify:
- Where the flight originated
- Where the flight ended
- Airport information for flight analysis

**Example**: If you start recording at San Francisco International Airport, the departure fields will contain:
- ICAO: "KSFO"
- Name: "San Francisco Intl"
- Coordinates: 37.619, -122.375

If no airport is detected (e.g., recording starts in flight), the ICAO field will be empty.

## Python Reader Utility

A Python reader utility (`xdr_reader.py`) is included for reading and exporting XDR files:

```bash
# Show summary
python xdr_reader.py recording.xdr

# List all recorded parameters
python xdr_reader.py recording.xdr --datarefs

# Show first frame values
python xdr_reader.py recording.xdr --frame 0

# Export to CSV
python xdr_reader.py recording.xdr --export output.csv

# Show everything
python xdr_reader.py recording.xdr --all
```

## Version History

**Version 2** (Current)
- Added automatic airport detection (departure and arrival)
- Airport information includes ICAO code, name, and coordinates
- Detection uses X-Plane Navigation API with 5 nm search radius
- Backward compatible - version 1 files can still be read

**Version 1**
- Initial format specification
- Support for float, int, and string datatypes
- Support for arrays
- Self-describing header with dataref definitions
- Optimized C++ implementation with buffered I/O

## Future Considerations

Potential enhancements for future versions:

- Optional compression (zlib, lz4)
- Checksum/CRC for data integrity
- Event markers (touchdown, gear up/down, etc.)
- Metadata fields (aircraft model, pilot notes, etc.)
- Index for fast seeking
- Delta encoding for better compression
- Additional dataref types (double, bool)
- Runway information (departure/arrival runway used)
