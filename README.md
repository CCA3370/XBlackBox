# XBlackBox - Flight Data Recorder for X-Plane 12

XBlackBox is a high-performance C++ plugin for X-Plane 12 that records comprehensive flight data in real-time, similar to a real aircraft's flight data recorder (black box).

## Features

- **Real-time Recording**: Continuously records flight data at configurable intervals (20Hz to 0.2Hz)
- **Three Recording Levels**:
  - **Simple**: Basic flight data (position, attitude, velocities) - ~25 parameters
  - **Normal**: + flight controls, engines, systems - ~70 parameters  
  - **Detailed**: Everything including autopilot, weather, warnings, etc. - ~180+ parameters
- **Efficient Binary Format**: Compact .xdr files for minimal disk usage and fast I/O
- **Optimized Performance**: Buffered binary I/O, efficient dataref caching
- **Auto Recording Mode**: Automatically starts/stops recording based on:
  - Ground speed threshold
  - Engine running state
  - Weight on wheels (takeoff/landing detection)
- **Menu Integration**: Full X-Plane plugins menu integration
- **Persistent Settings**: All configuration is saved and restored

## Installation

1. Build the plugin (see Building section below)
2. Copy the built plugin to your X-Plane 12 `Resources/plugins/XBlackBox/` directory
3. The final structure should be:
   ```
   X-Plane 12/
   └── Resources/
       └── plugins/
           └── XBlackBox/
               ├── 64/
               │   └── lin.xpl (or mac.xpl or win.xpl)
               └── ...
   ```
4. Start X-Plane 12

## Building

### Requirements

- CMake 3.16 or later
- C++17 compatible compiler (GCC, Clang, MSVC)
- X-Plane SDK (included in `SDK/` directory)
- ImGui (included in `SDK/imgui-1.92.5/` directory)

### Build Steps

```bash
# Create build directory
mkdir build
cd build

# Configure
cmake ..

# Build
cmake --build . --config Release

# Install (copies to project root)
cmake --install .
```

### Platform-Specific Notes

**Windows**: Requires MSVC or MinGW. The plugin will be named `win.xpl`.

**macOS**: Requires Xcode command-line tools. The plugin will be named `mac.xpl`.

**Linux**: Requires GCC or Clang. The plugin will be named `lin.xpl`.

## Usage

### Menu Access

Access XBlackBox from the X-Plane menu bar:
**Plugins → XBlackBox**

### Menu Options

- **Auto Mode**: Toggle automatic recording on/off
- **Start/Stop Recording**: Manually control recording
- **Recording Level**: Choose Simple, Normal, or Detailed
- **Recording Interval**: Set data capture frequency (0.05s to 5.0s)
- **Show Status**: Display current recording status
- **Open Output Folder**: Open the folder containing recorded files

### Recording Files

Recorded files are saved in:
```
X-Plane 12/Output/XBlackBox/flightdata_YYYYMMDD_HHMMSS.xdr
```

Files use the efficient `.xdr` (X-Plane Data Recorder) binary format.

## Configuration

Settings are automatically saved in:
```
X-Plane 12/Output/XBlackBox/config.ini
```

### Configurable Parameters

- **recordingLevel**: 1=Simple, 2=Normal, 3=Detailed (default: 3)
- **recordingInterval**: 0.05 to 5.0 seconds (default: 0.25)
- **autoMode**: true/false (default: false)
- **autoStartCondition**: "ground_speed", "engine_running", "weight_on_wheels"
- **autoStartThreshold**: threshold value (default: 5 knots for ground speed)
- **autoStopCondition**: same options as start
- **autoStopThreshold**: threshold value (default: 5 knots)
- **autoStopDelay**: delay in seconds before stopping (default: 30)

## Recorded Parameters

### Level 1: Simple (Basic Flight Data)

**Time & Aircraft Info**
- Total running time, Zulu time, Date
- Aircraft description, ICAO code

**Position**
- Latitude, Longitude
- Elevation MSL, Height AGL

**Attitude**
- Pitch, Roll, Heading (true & magnetic)
- Ground track, Sideslip angle, Angle of attack

**Velocities**
- IAS, TAS, Ground speed
- Vertical speed (fpm)
- Angular rates (P, Q, R)

**Forces**
- G-forces (normal, axial, side)

### Level 2: Normal (+ Controls & Systems)

**Flight Controls**
- Yoke pitch, roll, rudder pedals
- Parking brake, landing brake

**Control Surfaces**
- Aileron positions (left/right)
- Elevator, Rudder
- Flaps (request & actual)
- Speedbrake (request & actual)

**Landing Gear**
- Gear request & deployment status
- Tire rotation speeds
- Weight on wheels

**Engine Controls & Data**
- Throttle, Mixture, Prop pitch (up to 8 engines)
- Engine running status
- N1, N2 percentages
- Fuel flow, EGT, ITT, CHT, Torque

**Weight & Fuel**
- Total weight, Fuel weight
- Fuel quantity

### Level 3: Detailed (Everything)

**Autopilot**
- State, Mode
- Altitude, Heading, Airspeed, VS targets
- Flight director (mode, pitch, roll)

**Navigation & Radios**
- NAV1/2 frequencies & DME distance
- COM1/2 frequencies
- GPS distance

**Environment**
- Cabin altitude & vertical speed
- Outside air temperature
- Wind speed & direction (multiple layers)
- Barometric pressure

**Electrical System**
- Battery voltage & current (up to 8 batteries)
- Generator status

**Hydraulics**
- Hydraulic pressure (systems 1 & 2)

**Engine Details**
- Manifold pressure
- Oil pressure & temperature
- Cowl flap positions

**Warnings & Annunciators**
- Master warning/caution
- Stall warning
- Low vacuum, Low voltage
- Fuel quantity warning

**Ice & Anti-Ice**
- Frame anti-ice, Inlet heat, Pitot heat
- Ice accumulation levels

**Additional Forces & Moments**
- Aerodynamic forces (side, normal, axial)
- Roll, Pitch, Yaw moments

## File Format

The `.xdr` format is a binary format optimized for:
- **Compact storage**: Efficient binary encoding
- **Fast I/O**: Sequential write with minimal overhead, buffered writes
- **Self-describing**: Contains metadata about recorded parameters
- **Platform-independent**: Little-endian byte order

### File Structure

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

See the [XBlackBox-SASL repository](https://github.com/CCA3370/XBlackBox-SASL) for detailed file format specification and Python reader utility.

## Performance Optimizations

This C++ implementation includes several optimizations over the SASL version:

1. **Buffered I/O**: 64KB write buffer with periodic flushing
2. **Efficient Dataref Access**: Cached dataref references, batch reading
3. **Native Performance**: C++ provides better performance than Lua
4. **Memory Efficiency**: Pre-allocated buffers, minimal allocations during recording
5. **Direct Binary Writing**: Optimized little-endian serialization

At default settings (4Hz, Detailed level):
- ~2KB per second of flight time
- ~7MB per hour of recording
- Negligible FPS impact (<0.1%)

## Development

Built with:
- X-Plane SDK (XPLM420)
- ImGui 1.92.5 for UI
- CMake build system
- C++17

## License

This project is licensed under the GPLv3 License - see the LICENSE file for details.

## Credits

- Developed for X-Plane 12
- Based on functionality from XBlackBox-SASL
- Uses X-Plane SDK by Laminar Research
- Uses Dear ImGui by Omar Cornut

## Support

For issues, questions, or contributions, please visit the project repository on GitHub.