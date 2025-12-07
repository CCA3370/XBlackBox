# XBlackBox XDR Viewer - Modern Edition UI Guide

## Quick Start Guide

Welcome to the modernized XBlackBox XDR Viewer! This guide will help you get started with the new features and UI improvements.

## 🎨 Visual Overview

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  📁 File  👁️ View  📊 Analysis  ❓ Help                         │
├─────────────────────────────────────────────────────────────────┤
│  🗁 Open  💾 Export                                             │
├──────────────────┬──────────────────────────────────────────────┤
│                  │  ⏱️ Time Range: [0.0s] → [100.0s] [🔄 Reset] │
│  📄 File Info    ├──────────────────────────────────────────────┤
│  ┌────────────┐  │  📊 Plot Options: ☑ Grid  ☐ Derivative      │
│  │Status: ✅  │  │  🔴 Live Mode [500ms]  [🔄 Update Plot]      │
│  │Level: 📊 3 │  ├──────────────────────────────────────────────┤
│  │Duration:   │  │  ┌────────────────────────────────────────┐  │
│  │  120.5s    │  │  │  Plot │ Data │ Stats │ Corr │ FFT │ 3D │  │
│  └────────────┘  │  ├────────────────────────────────────────┤  │
│                  │  │                                        │  │
│  ✓ Select All    │  │        📈 Interactive Plot Area       │  │
│  ✗ Clear All     │  │                                        │  │
│  ┌────────────┐  │  │        (Zoom, Pan, Rotate)            │  │
│  │ Filter:    │  │  │                                        │  │
│  │ [engine_]  │  │  │                                        │  │
│  ├────────────┤  │  └────────────────────────────────────────┘  │
│  │☑ Parameter1│  │                                              │
│  │☐ Parameter2│  │                                              │
│  │☑ Parameter3│  │                                              │
│  │☐ Parameter4│  │                                              │
│  └────────────┘  │                                              │
└──────────────────┴──────────────────────────────────────────────┤
│  🚀 Ready - Open an XDR file or drag & drop to begin           │
└─────────────────────────────────────────────────────────────────┘
```

## 🆕 New Features

### 1. 📡 Frequency Analysis (FFT)

**Access**: Analysis → Show Frequency Analysis (Ctrl+F)

**Purpose**: Reveals periodic patterns and oscillations in your flight data.

**How to Use**:
1. Select parameters in the left panel
2. Press Ctrl+F or click Analysis → Frequency Analysis
3. Choose a parameter from the dropdown
4. Click "🔄 Analyze"
5. View the frequency spectrum

**What You'll See**:
- Frequency (Hz) on X-axis
- Magnitude on Y-axis (logarithmic scale)
- Dominant frequency highlighted in info box
- Period calculation

**Use Cases**:
- Detect engine vibrations
- Analyze control surface oscillations
- Identify resonance frequencies
- Study stick shaker activation
- Analyze autopilot behavior

**Example Insights**:
```
🔔 Dominant Frequency: 2.5 Hz (Period: 0.400 sec)
```
This might indicate a 2.5 Hz oscillation in pitch, which could be a PIO (Pilot Induced Oscillation).

---

### 2. ✈️ 3D Flight Path Visualization

**Access**: Analysis → Show 3D Flight Path (Ctrl+3)

**Purpose**: Interactive 3D visualization of your aircraft's trajectory.

**How to Use**:
1. Load an XDR file
2. Press Ctrl+3 or click Analysis → 3D Flight Path
3. Click "🔄 Update" to render
4. Use mouse to rotate and zoom:
   - Left-click + drag: Rotate
   - Right-click + drag: Zoom
   - Middle-click + drag: Pan

**Options**:
- ☐ Show Markers: Display waypoints along the path
- ☑ Color by Altitude: Color the path from blue (low) to red (high)

**What You'll See**:
- 🔵 Start point (cyan circle)
- 🔴 End point (red square)
- Flight path colored by altitude
- Altitude range and total distance

**Use Cases**:
- Visualize complete flight trajectory
- Analyze climb and descent profiles
- Compare approach patterns
- Study traffic pattern consistency
- Present flight data to others

**Example Stats**:
```
Min Alt: 1,250 ft | Max Alt: 8,500 ft | Range: 7,250 ft | Distance: ~45.3 km
```

---

## 🎨 UI Improvements

### Color Scheme

#### Primary Colors
- **Brand Color**: Teal (#0d7377) - Used for accents, highlights, titles
- **Background**: Dark gray (#1e1e1e) - Main window background
- **Surface**: Medium gray (#252525) - Panels and cards
- **Border**: Light gray (#3d3d3d) - Borders and separators

#### Status Colors
- **Success**: Teal (#4ecdc4) - Complete recordings, positive states
- **Warning**: Yellow (#ffe66d) - In-progress, moderate states
- **Error**: Coral Red (#ff6b6b) - Recording, high priority items

#### Text Colors
- **Primary**: Light gray (#e0e0e0) - Main text
- **Secondary**: Medium gray (#b0b0b0) - Labels, less important text
- **Disabled**: Dark gray (#666666) - Disabled elements

### Icons & Visual Language

The UI uses emoji icons for quick visual recognition:

- 📁 File operations
- 📊 Statistics and data analysis
- 🔗 Correlations and relationships
- 📡 Frequency analysis
- ✈️ Flight path and navigation
- ⏱️ Time-related controls
- 🔴 Live/recording status
- ✅ Complete/success
- ⚠️ Warnings
- 🔄 Refresh/update actions
- ✓ Selection/confirmation
- ✗ Clear/cancel

### Enhanced Components

#### File Information Panel
```
┌─────────────────────────────┐
│ 📄 flight_20240101.xdr      │
│ ┌─────────────────────────┐ │
│ │ ✅ Complete              │ │
│ └─────────────────────────┘ │
│                             │
│ 📊 Level: Detailed (3)      │
│ ⏱️ Interval: 0.250s (4Hz)   │
│ 🕐 Start: 2024-01-01 10:00  │
│ 🕑 End: 2024-01-01 10:45    │
│ ⏲️ Duration: 45.0 min       │
│ 🎞️ Frames: 10,800          │
│ 📈 Parameters: 180          │
│ 💾 Size: 2.3 MB             │
└─────────────────────────────┘
```

#### Plot Options
```
📊 Plot Options: ☐ Separate Axes  ☑ Grid  ☐ Derivative
🔴 Live Mode [500ms]  [🔄 Update Plot]
```

#### Time Range Controls
```
⏱️ Time Range: [0.0s] → [100.0s] [🔄 Reset]
```

### Button Styles

#### Primary Buttons (Teal)
- Main actions: "Update Plot", "Analyze", "Calculate"
- Clear call-to-action
- High contrast

#### Secondary Buttons (Gray)
- Less frequent actions: "Reset", "Clear All"
- Subtle but accessible

### Tooltips

Hover over any control to see helpful tooltips:
```
┌─────────────────────────────────┐
│ 🔄 Update Plot                  │
│                                 │
│ Refresh plot with current      │
│ selection (F5)                  │
└─────────────────────────────────┘
```

---

## ⌨️ Keyboard Shortcuts

### File Operations
- **Ctrl+O**: Open File
- **Ctrl+E**: Export to CSV
- **Ctrl+S**: Save Plot Image
- **Ctrl+Q**: Quit

### View Operations
- **F5**: Refresh Plot
- **Ctrl+L**: Clear Plot
- **Ctrl++**: Zoom In (Time Range)
- **Ctrl+-**: Zoom Out (Time Range)

### Analysis (NEW!)
- **Ctrl+T**: Show Statistics
- **Ctrl+F**: Show Frequency Analysis ⭐ NEW
- **Ctrl+3**: Show 3D Flight Path ⭐ NEW

### Help
- **F1**: Show Keyboard Shortcuts

---

## 📊 Tab Overview

### 1. Plot Tab
- Main time-series visualization
- Multiple parameters on same or separate axes
- Zoom, pan, save capabilities
- Grid and derivative options

### 2. Data Table Tab
- Raw data view
- Frame-by-frame values
- Configurable range
- Copy/export individual values

### 3. Statistics Tab
- Automatic statistical analysis
- Min, Max, Mean, Median, Std Dev
- Count and Range
- Refreshable for selected parameters

### 4. Correlation Tab
- Parameter correlation matrix
- Color-coded correlation strength
- Positive/negative correlations
- Visual relationship mapping

### 5. Frequency Analysis Tab ⭐ NEW
- FFT visualization
- Dominant frequency detection
- Period calculation
- Oscillation analysis

### 6. 3D Flight Path Tab ⭐ NEW
- Interactive 3D trajectory
- Altitude coloring
- Start/end markers
- Flight statistics

---

## 🎯 Common Workflows

### Workflow 1: Basic Data Exploration
1. Open file (Ctrl+O or drag & drop)
2. Review file info in left panel
3. Select interesting parameters
4. View plot
5. Check statistics tab (Ctrl+T)

### Workflow 2: Oscillation Analysis
1. Open file
2. Select parameter showing oscillation (e.g., pitch angle)
3. View time-series plot
4. Switch to Frequency Analysis (Ctrl+F)
5. Identify dominant frequency
6. Correlate with other parameters

### Workflow 3: Flight Path Analysis
1. Open file
2. Go to 3D Flight Path tab (Ctrl+3)
3. Enable "Color by Altitude"
4. Rotate to view from different angles
5. Enable markers to see key waypoints
6. Note min/max altitudes and distance

### Workflow 4: Parameter Correlation Study
1. Open file
2. Select multiple related parameters
3. View plots to see relationships
4. Go to Correlation tab
5. Identify strong correlations (green/red)
6. Analyze why they correlate

### Workflow 5: Live Flight Monitoring
1. Open active recording file
2. Enable "🔴 Live Mode"
3. Set refresh interval (500-1000ms)
4. Select key parameters to monitor
5. Watch real-time updates
6. Switch between tabs as needed

---

## 💡 Pro Tips

### Tip 1: Parameter Filtering
Use the filter box to quickly find parameters:
- Type "engine" to see all engine parameters
- Type "pitch" to see pitch-related parameters
- Use category names from dropdown

### Tip 2: Color Recognition
Parameters are automatically color-coded when selected. The same colors appear in:
- Parameter list (checkbox text)
- Plot lines
- Legend

### Tip 3: Time Range Focus
Use time range controls to focus on specific flight phases:
1. Note interesting time in plot
2. Set start/end times
3. All analyses (stats, correlation, FFT) will use this range
4. Reset when done

### Tip 4: Export Workflow
For presentations or reports:
1. Configure plot as desired
2. Save plot image (Ctrl+S)
3. Choose format: PNG (raster), PDF/SVG (vector)
4. Export raw data to CSV (Ctrl+E) for further analysis

### Tip 5: FFT Best Practices
- Use longer time ranges for better frequency resolution
- Look for peaks in the frequency spectrum
- Low frequency peaks: Long-period oscillations
- High frequency peaks: Vibrations, rapid oscillations
- Compare FFT of related parameters

### Tip 6: 3D View Navigation
- Drag slowly for precise rotation
- Use middle mouse to pan if path is off-center
- Enable markers to see path density
- Color by altitude helps visualize climb/descent rates

---

## 🔍 Understanding the Interface

### Left Panel (Parameters)
- **File Info**: Recording metadata
- **Filter**: Quick parameter search
- **Bulk Actions**: Select/Clear all
- **Parameter List**: Checkboxes with color coding

### Right Panel (Analysis)
- **Controls**: Time range, plot options
- **Tabs**: Different views of data
- **Canvas**: Interactive visualization area
- **Info Bar**: Context-specific information

### Status Bar
- Shows current operation status
- Number of parameters plotted
- Plot mode (value/derivative)
- Live mode status
- File load status

---

## 🚀 Getting the Most Out of New Features

### FFT Analysis Best Practices

**For Engine Vibration Analysis**:
1. Select N1 or N2 parameter
2. Look for peaks in 10-50 Hz range
3. Compare with expected blade passage frequency

**For Flight Dynamics**:
1. Select pitch, roll, or yaw rate
2. Look for low-frequency peaks (< 5 Hz)
3. May indicate PIO or dutch roll modes

**For Control Surface Oscillation**:
1. Select elevator, aileron, or rudder position
2. Look for narrow peaks
3. High Q (sharp peaks) may indicate flutter

### 3D Visualization Tips

**For Approach Analysis**:
1. Color by altitude
2. Rotate to view from side (shows glideslope)
3. Enable markers to see fix crossings
4. Check altitude range matches expected

**For Traffic Pattern**:
1. View from above (Z-axis pointing at you)
2. Check for rectangular pattern
3. Verify consistent altitudes on downwind/base
4. Ensure smooth turn radii

**For Cross-Country**:
1. View from oblique angle
2. Enable markers to see waypoint compliance
3. Color by altitude to verify terrain clearance
4. Check distance matches planned route

---

## 📚 Additional Resources

- **VIEWER_GUIDE.md**: Complete user guide with workflows
- **UI_IMPROVEMENTS.md**: Technical documentation of all improvements
- **README.md**: Project overview and installation

---

## 🆘 Troubleshooting

### FFT shows "Not enough data points"
- Need at least 4 data points
- Use longer time range
- Check if parameter has data

### 3D Flight Path shows "Required parameters not found"
- File must contain latitude, longitude, and altitude
- Check recording level (Simple may not have all)
- Verify datarefs exist in file

### Plot is slow
- Too many parameters selected (try < 10)
- Very large file (use time range to limit)
- Disable derivative mode if not needed

### Colors look wrong
- Check display color profile
- Ensure dark mode compatible
- Try adjusting monitor brightness

---

**Happy Analyzing! ✈️📊**

**XBlackBox XDR Viewer - Modern Edition v2.5**
