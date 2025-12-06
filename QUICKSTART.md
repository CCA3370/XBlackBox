# XBlackBox Quick Start Guide

Get started with XBlackBox flight data recording in 5 minutes!

## Installation

### 1. Download or Build the Plugin

**Option A: Download Pre-built** (when available)
- Download the appropriate .xpl file for your platform from releases

**Option B: Build from Source**
- See [BUILD.md](BUILD.md) for detailed instructions
- Quick Linux build:
  ```bash
  mkdir build && cd build
  cmake .. && cmake --build . --config Release
  ```

### 2. Install to X-Plane

Copy the plugin file to your X-Plane plugins directory:

```
X-Plane 12/
└── Resources/
    └── plugins/
        └── XBlackBox/
            └── 64/
                └── lin.xpl (or mac.xpl or win.xpl)
```

**Quick Copy Commands:**

**Linux:**
```bash
mkdir -p "$HOME/X-Plane 12/Resources/plugins/XBlackBox/64"
cp build/lin.xpl "$HOME/X-Plane 12/Resources/plugins/XBlackBox/64/"
```

**macOS:**
```bash
mkdir -p "$HOME/X-Plane 12/Resources/plugins/XBlackBox/64"
cp build/mac.xpl "$HOME/X-Plane 12/Resources/plugins/XBlackBox/64/"
```

**Windows:**
```cmd
mkdir "%USERPROFILE%\X-Plane 12\Resources\plugins\XBlackBox\64"
copy build\win.xpl "%USERPROFILE%\X-Plane 12\Resources\plugins\XBlackBox\64\"
```

### 3. Verify Installation

1. Start X-Plane 12
2. Check `X-Plane 12/Log.txt` for:
   ```
   XBlackBox: Plugin starting...
   XBlackBox: Plugin started successfully
   ```
3. Look for **Plugins → XBlackBox** in the menu bar

---

## Basic Usage

### Manual Recording

1. **Start Recording**
   - Go to: **Plugins → XBlackBox → Start Recording**
   - Begin your flight
   - Files saved to: `X-Plane 12/Output/XBlackBox/`

2. **Stop Recording**
   - Go to: **Plugins → XBlackBox → Stop Recording**
   - File is automatically closed and finalized

3. **View Recorded Files**
   - **Plugins → XBlackBox → Open Output Folder**
   - Files named: `flightdata_YYYYMMDD_HHMMSS.xdr`

### Auto Recording

**Enable Auto Mode:**
- **Plugins → XBlackBox → Auto Mode**
- Recording starts/stops automatically based on configured conditions

**Default Behavior:**
- Starts when ground speed > 5 knots
- Stops when ground speed < 5 knots (after 30 second delay)
- Perfect for capturing entire flights automatically!

---

## Recording Levels

Choose your recording detail level:

### Simple (~25 parameters)
- Position, attitude, velocities
- G-forces, angular rates
- ~1.5 MB per hour at 4 Hz
- **Best for**: Basic flight tracking

### Normal (~70 parameters)
- Everything in Simple, plus:
- Flight controls, engines, fuel
- Landing gear, control surfaces
- ~6.2 MB per hour at 4 Hz
- **Best for**: General flight analysis

### Detailed (~180 parameters) - **Default**
- Everything in Normal, plus:
- Autopilot, navigation, radios
- Environment, weather, electrical
- Warnings, ice, forces/moments
- ~14.4 MB per hour at 4 Hz
- **Best for**: Complete flight data

**Change Level:**
- **Plugins → XBlackBox → Recording Level → [Choose Level]**

---

## Recording Intervals

Balance between data detail and file size:

| Interval | Frequency | Use Case |
|----------|-----------|----------|
| 0.05s | 20 Hz | Aerobatic maneuvers, high-g flights |
| 0.10s | 10 Hz | Fast-paced flying, detailed analysis |
| **0.25s** | **4 Hz** | **Standard recording (default)** |
| 1.0s | 1 Hz | Long cruise flights, fuel economy |

**Change Interval:**
- **Plugins → XBlackBox → Recording Interval → [Choose Frequency]**

---

## Reading Your Data

### Python Reader (Recommended)

**View Summary:**
```bash
python xdr_reader.py recording.xdr
```

**Export to CSV:**
```bash
python xdr_reader.py recording.xdr --export output.csv
```

**See All Recorded Parameters:**
```bash
python xdr_reader.py recording.xdr --datarefs
```

**View Specific Frame:**
```bash
python xdr_reader.py recording.xdr --frame 0
```

**See Everything:**
```bash
python xdr_reader.py recording.xdr --all
```

### Import into Spreadsheet

1. Export to CSV: `python xdr_reader.py recording.xdr --export data.csv`
2. Open in Excel, LibreOffice, Google Sheets
3. Create charts and analyze your flight!

---

## Configuration

Settings are saved in: `X-Plane 12/Output/XBlackBox/config.ini`

### Example config.ini:
```ini
# XBlackBox Configuration File
# Recording Settings
recordingLevel=3
recordingInterval=0.25

# Auto Recording Mode
autoMode=false
autoStartCondition=ground_speed
autoStartThreshold=5
autoStopCondition=ground_speed
autoStopThreshold=5
autoStopDelay=30

# File Settings
filePrefix="flightdata_"
```

**Edit manually** or use the menu to change settings.

---

## Common Workflows

### Workflow 1: Record a Training Flight
1. Start X-Plane, load aircraft
2. **Plugins → XBlackBox → Start Recording**
3. Fly your training session
4. **Plugins → XBlackBox → Stop Recording**
5. Export to CSV and review maneuvers

### Workflow 2: Auto-Record All Flights
1. **Plugins → XBlackBox → Auto Mode** (enable once)
2. Fly normally - recording starts automatically at takeoff
3. Stops automatically after landing
4. No intervention needed!

### Workflow 3: High-Frequency Aerobatics
1. **Plugins → XBlackBox → Recording Interval → 20 Hz**
2. **Plugins → XBlackBox → Recording Level → Detailed**
3. Record aerobatic sequence
4. Analyze frame-by-frame for perfection

### Workflow 4: Long Cruise Flight
1. **Plugins → XBlackBox → Recording Interval → 1 Hz**
2. **Plugins → XBlackBox → Recording Level → Simple**
3. Fly your long cruise
4. Minimal file size, captures the essentials

---

## Troubleshooting

### Plugin Not Loading
- Check X-Plane 12 version (requires X-Plane 12)
- Verify file is in correct directory
- Check Log.txt for error messages
- Ensure file is executable (macOS/Linux): `chmod +x *.xpl`

### No Files Created
- Check: `X-Plane 12/Output/XBlackBox/` exists
- Verify disk space available
- Check write permissions
- Look for errors in Log.txt

### Recording Not Starting
- Check menu shows "Start Recording" (not already recording)
- Verify output directory is writable
- Review Log.txt for error messages

### Auto Mode Not Working
- Check condition settings in config.ini
- Verify threshold values are appropriate
- Watch ground speed/engine status during test
- Enable/disable auto mode to refresh settings

---

## Performance Tips

1. **Use appropriate recording level**
   - Simple for basic tracking
   - Detailed only when needed

2. **Adjust interval for flight type**
   - 1 Hz for cruise
   - 4 Hz for general (default)
   - 20 Hz for aerobatics

3. **Monitor file sizes**
   - Check Output/XBlackBox/ directory size
   - Archive old recordings
   - Use CSV export selectively

4. **Test before important flights**
   - Do a quick test recording
   - Verify file creation works
   - Confirm data looks correct

---

## Need More Help?

- **Full Documentation**: See [README.md](README.md)
- **Build Instructions**: See [BUILD.md](BUILD.md)
- **File Format Details**: See [FILE_FORMAT.md](FILE_FORMAT.md)
- **Issues**: Check GitHub Issues
- **X-Plane Forums**: Search for XBlackBox discussions

---

## Tips for Best Results

✅ **DO:**
- Test recording before important flights
- Use auto mode for convenience
- Export to CSV for analysis
- Archive old recordings regularly
- Choose appropriate level and interval

❌ **DON'T:**
- Record with insufficient disk space
- Use 20 Hz for long flights (huge files!)
- Delete recordings without backing up
- Modify config.ini while X-Plane is running
- Ignore error messages in Log.txt

---

## Quick Reference

| Action | Menu Path |
|--------|-----------|
| Start/Stop | Plugins → XBlackBox → Start/Stop Recording |
| Auto Mode | Plugins → XBlackBox → Auto Mode |
| Change Level | Plugins → XBlackBox → Recording Level |
| Change Interval | Plugins → XBlackBox → Recording Interval |
| View Status | Plugins → XBlackBox → Show Status |
| Open Folder | Plugins → XBlackBox → Open Output Folder |

**Happy Flying! 🛩️**

---

*XBlackBox - Professional Flight Data Recording for X-Plane 12*
