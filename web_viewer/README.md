# XBlackBox Tauri Viewer

This is the desktop application version of the XBlackBox XDR Viewer, built with Tauri (Rust + Web Technologies).

## Overview

The XBlackBox Tauri Viewer is a cross-platform desktop application for visualizing and analyzing X-Plane flight data recordings. It combines the power of Rust for fast XDR file parsing with a modern web-based UI built using HTML, CSS, and JavaScript.

## Features

- **Native Desktop Application**: Runs as a native app on Windows, macOS, and Linux
- **Fast XDR Parsing**: Rust-based backend for efficient file reading and data processing
- **Interactive Visualizations**: Plotly-based charts for parameter analysis
- **Statistics & Correlation**: Built-in statistical analysis and parameter correlation
- **Flight Path Visualization**: 3D flight path rendering
- **Data Export**: Export to CSV format
- **Dark/Light Themes**: Multiple color schemes

## Requirements

### For Running (Pre-built)
- No additional requirements needed - the app is self-contained

### For Building

#### System Dependencies (Linux)
```bash
sudo apt-get update
sudo apt-get install -y libgtk-3-dev libwebkit2gtk-4.1-dev \
    libayatana-appindicator3-dev librsvg2-dev libssl-dev
```

#### System Dependencies (macOS)
```bash
# Xcode Command Line Tools
xcode-select --install
```

#### System Dependencies (Windows)
- Microsoft Visual Studio C++ Build Tools
- WebView2 (usually pre-installed on Windows 10/11)

#### Development Tools
- Node.js (v16 or later) and npm
- Rust toolchain (1.70 or later)
  ```bash
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  ```

## Building

1. **Install Dependencies**
   ```bash
   cd web_viewer
   npm install
   ```

2. **Build the Application**
   ```bash
   # Development build
   npm run tauri build
   
   # Or use cargo directly
   cd src-tauri
   cargo build --release
   ```

## Running

### Development Mode
```bash
cd web_viewer
npm run tauri dev
```

This will start the application in development mode with hot-reloading.

### Production Build
After building, the executable will be in:
- **Linux**: `web_viewer/src-tauri/target/release/xblackbox-viewer`
- **macOS**: `web_viewer/src-tauri/target/release/bundle/macos/XBlackBox Viewer.app`
- **Windows**: `web_viewer/src-tauri/target/release/xblackbox-viewer.exe`

## Usage

1. **Open File**: Click the "Open File" button (folder icon) or press `Ctrl+O`
   - In Tauri mode, this will open a native file dialog
   - Select an `.xdr` file from your X-Plane recordings

2. **View File Info**: File information will be displayed in the left sidebar
   - File header details
   - Recording level and interval
   - Duration and frame count

3. **Select Parameters**: Choose parameters from the list to plot
   - Click on parameter names to select/deselect
   - Multiple parameters can be plotted simultaneously

4. **Analyze Data**:
   - **Time Series**: Main plot shows parameter values over time
   - **Statistics**: View min/max/mean/std for selected parameters
   - **Correlation**: Analyze relationships between parameters
   - **FFT**: Frequency analysis (basic implementation)
   - **Flight Path**: 3D visualization of the flight trajectory
   - **Data Table**: View raw data in table format

5. **Export**: Click the download icon to export data as CSV

## Architecture

### Backend (Rust)
- **`src-tauri/src/xdr.rs`**: XDR file parser and data structures
- **`src-tauri/src/lib.rs`**: Tauri commands and application logic
- **`src-tauri/src/main.rs`**: Application entry point

### Frontend (Web Technologies)
- **`static/index.html`**: Main application UI
- **`static/js/tauri-api.js`**: Tauri API wrapper for cross-platform compatibility
- **`static/js/app.js`**: Application logic and UI handlers
- **`static/css/styles.css`**: Application styling

## Differences from Web Version

The Tauri version has several advantages over the original Flask web viewer:

1. **No Server Required**: Runs as a standalone desktop application
2. **Better Performance**: Native Rust backend is faster than Python
3. **Native File Dialogs**: Uses OS-native file pickers
4. **Smaller Footprint**: No need for Python runtime
5. **Cross-Platform**: Single codebase for Windows, macOS, and Linux
6. **Better Security**: No web server, all data stays local

## Development

### Project Structure
```
web_viewer/
├── static/              # Frontend files (HTML, CSS, JS)
├── src-tauri/           # Rust backend
│   ├── src/
│   │   ├── main.rs      # Entry point
│   │   ├── lib.rs       # Tauri commands
│   │   └── xdr.rs       # XDR file parser
│   ├── Cargo.toml       # Rust dependencies
│   └── tauri.conf.json  # Tauri configuration
├── package.json         # Node.js dependencies
└── README.md            # This file
```

### Adding New Features

1. **Backend (Rust)**: Add new Tauri commands in `src-tauri/src/lib.rs`
2. **Frontend**: Update `static/js/tauri-api.js` to call new commands
3. **UI**: Modify `static/index.html` and `static/js/app.js`

### Testing

```bash
# Run in development mode
npm run tauri dev

# Build and test release version
npm run tauri build
```

## Troubleshooting

### Linux: Missing Dependencies
If you get build errors about missing libraries:
```bash
sudo apt-get install -y libgtk-3-dev libwebkit2gtk-4.1-dev \
    libayatana-appindicator3-dev librsvg2-dev
```

### Windows: WebView2 Not Found
Install WebView2 Runtime from: https://developer.microsoft.com/microsoft-edge/webview2/

### macOS: Code Signing Issues
For development, you can skip code signing:
```bash
export TAURI_SKIP_SIGNING=true
npm run tauri build
```

## License

This project inherits the license from the parent XBlackBox project.

## Contributing

Contributions are welcome! Please follow the project's coding standards and submit pull requests.
