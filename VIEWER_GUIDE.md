# XBlackBox XDR Viewer - Enhanced Edition User Guide

## Overview

The XBlackBox XDR Viewer Enhanced Edition is a powerful tool for visualizing and analyzing X-Plane flight data recordings. This guide covers all the enhanced features and how to use them effectively.

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [User Interface](#user-interface)
4. [Features](#features)
5. [Keyboard Shortcuts](#keyboard-shortcuts)
6. [Performance Tips](#performance-tips)
7. [Analysis Workflows](#analysis-workflows)

## Installation

### Requirements

```bash
pip install -r requirements.txt
```

Required packages:
- PySide6 >= 6.5.0
- matplotlib >= 3.7.0
- numpy >= 1.24.0

### Running the Viewer

```bash
python xdr_viewer.py [optional_file.xdr]
```

## Getting Started

### Opening Files

There are three ways to open XDR files:

1. **Menu**: File → Open XDR File... (Ctrl+O)
2. **Recent Files**: File → Recent Files → Select file
3. **Drag & Drop**: Simply drag an .xdr file onto the window

### Basic Workflow

1. Open an XDR file
2. Select parameters from the left panel
3. View plots in the main area
4. Use tabs to switch between Plot, Data Table, Statistics, and Correlation views
5. Export data or save plots as needed

## User Interface

### Main Window Layout

```
┌─────────────────────────────────────────────────────────┐
│  Menu Bar                                                │
├─────────────────────────────────────────────────────────┤
│  Toolbar                                                 │
├──────────────────┬──────────────────────────────────────┤
│                  │  Time Range Controls                  │
│  File Info       ├──────────────────────────────────────┤
│                  │  Plot Options                         │
│  ┌────────────┐  ├──────────────────────────────────────┤
│  │ Parameters │  │  ┌────────────────────────────────┐  │
│  │            │  │  │                                │  │
│  │  [✓] Param1│  │  │    Plot / Data / Stats /      │  │
│  │  [ ] Param2│  │  │         Correlation           │  │
│  │  [✓] Param3│  │  │                                │  │
│  │  [ ] Param4│  │  │                                │  │
│  │     ...    │  │  │                                │  │
│  └────────────┘  │  └────────────────────────────────┘  │
└──────────────────┴──────────────────────────────────────┘
│  Status Bar                                              │
└──────────────────────────────────────────────────────────┘
```

### Left Panel

#### File Information
- Recording status (complete or ongoing)
- Recording level and interval
- Start/end times and duration
- Total frames and parameters
- File size

#### Parameter Selection
- **Filter**: Search/filter parameters by name
- **Select All/None**: Bulk selection controls
- **Checkboxes**: Select individual parameters
- **Color Coding**: Selected parameters show their plot color

### Right Panel Tabs

#### 1. Plot Tab
Main visualization area with matplotlib toolbar for:
- Pan and zoom
- Save figure
- Configure subplots
- Home (reset view)

#### 2. Data Table Tab
Raw data view with:
- Frame range selection
- Paginated data display
- All parameter values

#### 3. Statistics Tab
Statistical analysis showing:
- Count: Number of data points
- Min: Minimum value
- Max: Maximum value
- Mean: Average value
- Median: Middle value
- Std Dev: Standard deviation
- Range: Max - Min

#### 4. Correlation Tab
Parameter correlation analysis:
- Correlation matrix between selected parameters
- Color-coded correlation strength:
  - Green: Strong positive correlation (> 0.7)
  - Yellow: Moderate correlation (0.4 - 0.7)
  - Gray: Weak correlation (< 0.4)
  - Red: Strong negative correlation (< -0.7)

## Features

### 1. Time Range Selection

Control the time window for all analyses:

- **Start Time**: Set start of time range (seconds)
- **End Time**: Set end of time range (seconds)
- **Reset Button**: Reset to full recording range
- **Automatic**: Affects plotting, statistics, and correlation

**Use Cases:**
- Focus on specific flight phases (takeoff, landing)
- Exclude taxi or ground operations
- Compare specific maneuvers

### 2. Plot Options

#### Separate Axes
Plot each parameter on its own Y-axis for better visibility when parameters have different scales.

#### Show Grid
Toggle grid lines for easier value reading.

#### Plot Derivative
Instead of plotting raw values, plot the rate of change (d/dt):
- Useful for analyzing acceleration, rate of climb/descent
- Identifies rapid changes
- Helps spot anomalies

### 3. Live Mode (实时更新)

Monitor recordings in progress:
- **Enable**: Check "Live Mode" checkbox
- **Interval**: Set refresh rate (100-5000 ms)
- **Auto-detect**: Automatically stops when recording completes
- **Real-time Updates**: File info, plots, and statistics update automatically

**Use Case:**
- Monitor active flights
- Debug recording issues
- Verify data quality in real-time

### 4. Performance Optimization

**Automatic Downsampling:**
- Datasets > 5000 points are automatically downsampled
- Maintains visual accuracy while improving responsiveness
- No configuration needed

**Progress Indicators:**
- Loading progress dialog for large files
- Status bar updates during operations

### 5. Data Export

#### CSV Export
Export all or selected data to CSV format:
- Includes all parameters
- Frame-by-frame data
- Compatible with Excel, LibreOffice, etc.

**Workflow:**
1. File → Export to CSV... (Ctrl+E)
2. Choose location
3. Open in spreadsheet software

#### Plot Export
Save plots as high-quality images:
- **PNG**: Raster format, best for viewing
- **PDF**: Vector format, best for documents
- **SVG**: Vector format, best for editing

**Workflow:**
1. Configure plot as desired
2. File → Save Plot Image... (Ctrl+S)
3. Choose format and location

### 6. Statistical Analysis

Automatically calculated for selected parameters:

**Descriptive Statistics:**
- Central tendency: Mean, Median
- Spread: Standard deviation, Range
- Extremes: Min, Max
- Sample size: Count

**Use Cases:**
- Compare flight characteristics
- Identify outliers
- Verify expected ranges
- Quality assurance

### 7. Correlation Analysis

Understand relationships between parameters:

**Correlation Coefficient (r):**
- +1.0: Perfect positive correlation
- 0.0: No correlation
- -1.0: Perfect negative correlation

**Interpretation Examples:**
- Altitude vs. Airspeed: Often negative (higher = faster TAS)
- Throttle vs. N1: Strong positive correlation
- Pitch vs. Vertical Speed: Positive correlation during climbs

**Use Cases:**
- Validate expected relationships
- Discover unexpected dependencies
- System behavior analysis
- Performance analysis

## Keyboard Shortcuts

### File Operations
- `Ctrl+O`: Open file
- `Ctrl+E`: Export to CSV
- `Ctrl+S`: Save plot image
- `Ctrl+Q`: Quit application

### View Operations
- `F5`: Refresh plot
- `Ctrl+L`: Clear plot
- `Ctrl++`: Zoom in (time range)
- `Ctrl+-`: Zoom out (time range)

### Analysis
- `Ctrl+T`: Show statistics tab
- `F1`: Show keyboard shortcuts help

### Plot Navigation
(via matplotlib toolbar)
- `Home`: Reset view
- `←/→`: Pan left/right
- `Ctrl+←/→`: Fine pan
- Mouse wheel: Zoom in/out

## Performance Tips

### Large Files (> 1 GB)

1. **Use Time Ranges**: Focus on specific periods
2. **Select Fewer Parameters**: Reduces memory usage
3. **Disable Live Mode**: Process in batch mode
4. **Close Other Applications**: Free up RAM

### Smooth Plotting

1. **Automatic Downsampling**: Enabled by default
2. **Disable Derivative Mode**: When not needed (faster)
3. **Use Separate Axes**: Only when necessary

### Quick Analysis

1. **Recent Files**: Quick access to common files
2. **Keyboard Shortcuts**: Faster than mouse
3. **Batch Operations**: Select multiple parameters at once

## Analysis Workflows

### Workflow 1: Flight Phase Analysis

**Objective**: Analyze specific flight phases

1. Open XDR file
2. Identify time ranges:
   - Check timestamps in Data Table
   - Note key events (takeoff, cruise, landing)
3. Set time range for first phase
4. Select relevant parameters
5. View statistics for that phase
6. Export data or plots
7. Repeat for other phases

### Workflow 2: Parameter Correlation Study

**Objective**: Understand parameter relationships

1. Open XDR file
2. Select parameters of interest (2 or more)
3. Switch to Correlation tab
4. Identify strong correlations
5. Plot strongly correlated parameters together
6. Analyze time-series behavior
7. Use derivative mode to see rate relationships

### Workflow 3: Performance Analysis

**Objective**: Analyze aircraft performance

**Key Parameters:**
- Airspeed (IAS, TAS)
- Altitude
- Vertical speed
- Throttle position
- Fuel flow
- Engine parameters (N1, N2)

**Steps:**
1. Select performance parameters
2. View statistics for cruise phase
3. Check correlations:
   - Throttle vs. Airspeed
   - Altitude vs. Fuel flow
   - Vertical speed vs. Pitch
4. Plot derivative of altitude (rate of climb)
5. Export data for further analysis

### Workflow 4: Anomaly Detection

**Objective**: Find unusual events or behaviors

1. Load complete flight recording
2. Select critical parameters:
   - Warnings/alerts
   - G-forces
   - Control surface positions
   - Engine parameters
3. Enable derivative mode to spot rapid changes
4. Scan statistics for outliers (extreme min/max)
5. Use time range to zoom into suspicious periods
6. Analyze detailed behavior

### Workflow 5: Training & Evaluation

**Objective**: Evaluate pilot performance

1. Record training flight
2. Select control and performance parameters
3. Identify key maneuvers using time ranges
4. For each maneuver:
   - View parameter behavior
   - Check statistics against standards
   - Note deviations
5. Generate plots for debrief
6. Export summary statistics

### Workflow 6: Real-time Monitoring

**Objective**: Monitor active recording

1. Open active recording file
2. Enable Live Mode
3. Set refresh interval (500-1000 ms)
4. Select key monitoring parameters
5. Watch real-time updates
6. Switch to statistics tab during stable phases
7. Export data post-flight

## Tips & Tricks

### Effective Parameter Selection

1. **Group by System**: Select related parameters together
   - Engine: N1, N2, EGT, fuel flow
   - Flight controls: Pitch, roll, yaw rates
   - Performance: Speeds, altitude, VS

2. **Use Filter Effectively**:
   - Type partial names: "sim/cockpit/engine"
   - Use categories from dropdown
   - Common prefixes: sim/flightmodel, sim/cockpit

3. **Color Awareness**:
   - Note assigned colors
   - Match colors in plots
   - Use separate axes for clarity

### Interpreting Correlations

**Strong Positive (> 0.7):**
- Parameters move together
- Example: Throttle and N1

**Strong Negative (< -0.7):**
- Parameters move opposite
- Example: Descent rate and altitude

**Weak (|r| < 0.4):**
- Little to no linear relationship
- May have non-linear relationship
- May be phase-dependent

### Export Best Practices

**CSV Export:**
- Export only needed parameters
- Use time range to limit data size
- Open in Excel/LibreOffice for further analysis

**Plot Export:**
- Set up plot carefully first
- Use PNG for presentations (300 DPI)
- Use PDF for documents
- Use SVG for post-processing in Illustrator/Inkscape

### Maximizing Performance

1. Start with fewer parameters
2. Use statistics tab for quick overview
3. Plot only when detailed view needed
4. Close plot before loading new file
5. Use time ranges to reduce data volume

## Troubleshooting

### File Won't Open
- Check file extension is .xdr
- Verify file is not corrupted
- Ensure file is not locked by X-Plane

### Plot is Slow
- Too many parameters selected (> 10)
- Very large file (> 100k frames)
- Solution: Use time range, select fewer parameters

### Live Mode Not Updating
- Check if recording is actually ongoing
- Verify file path hasn't changed
- Try disabling and re-enabling live mode

### Statistics Show Zero/NaN
- Check parameter is numeric (not string)
- Verify time range includes data
- Ensure frames exist in range

### Correlation Matrix Empty
- Need at least 2 parameters selected
- Verify parameters have data
- Check time range includes frames

## Advanced Topics

### Understanding Derivatives

The derivative shows rate of change per second:

**Examples:**
- Altitude derivative = Vertical speed (ft/s)
- Airspeed derivative = Acceleration (knots/s)
- Pitch derivative = Pitch rate (deg/s)

**When to Use:**
- Analyzing transient behavior
- Finding rate limits
- Identifying rapid changes
- Detecting control inputs

### Correlation vs. Causation

**Important**: Correlation ≠ Causation

Strong correlation means parameters move together, but:
- May be coincidental
- May share common cause
- May be indirectly related

**Example:**
- Ice cream sales and drowning deaths correlate
- Both caused by summer season
- Neither causes the other

**In Flight Data:**
- Altitude and OAT correlate (both affected by atmosphere)
- Throttle and airspeed correlate (throttle causes speed)
- Multiple parameters may respond to same pilot input

## Support & Feedback

For issues, suggestions, or contributions:
- GitHub Issues: Report bugs or request features
- GitHub Discussions: Ask questions, share workflows
- Pull Requests: Contribute improvements

## Version History

### Version 2.0 - Enhanced Edition
- Performance optimization with auto-downsampling
- Time range selection and zoom
- Statistics analysis tab
- Correlation analysis tab
- Derivative plotting mode
- Recent files menu
- Drag-and-drop support
- Keyboard shortcuts
- Progress indicators
- Live mode for real-time monitoring

### Version 1.0 - Initial Release
- Basic file opening and plotting
- Parameter selection
- Data table view
- CSV export
- Plot image export

---

**Happy Analyzing! 🛩️📊**
