# Building and Installing XBlackBox

This guide covers building XBlackBox from source for all supported platforms.

## Prerequisites

### All Platforms
- CMake 3.16 or later
- C++17 compatible compiler
- Git (for cloning the repository)

### Windows
- Visual Studio 2019 or later (with C++ Desktop Development workload)
- OR MinGW-w64 (GCC 7.0 or later)

### macOS
- Xcode Command Line Tools: `xcode-select --install`
- macOS 10.13 or later

### Linux
- GCC 7.0 or later, or Clang 5.0 or later
- OpenGL development libraries:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install build-essential cmake libgl1-mesa-dev
  
  # Fedora/RHEL
  sudo dnf install gcc-c++ cmake mesa-libGL-devel
  
  # Arch Linux
  sudo pacman -S base-devel cmake mesa
  ```

## Building from Source

### 1. Clone the Repository

```bash
git clone https://github.com/CCA3370/XBlackBox.git
cd XBlackBox
```

### 2. Create Build Directory

```bash
mkdir build
cd build
```

### 3. Configure with CMake

**Windows (Visual Studio):**
```cmd
cmake .. -G "Visual Studio 17 2022" -A x64
```

**Windows (MinGW):**
```cmd
cmake .. -G "MinGW Makefiles"
```

**macOS:**
```bash
cmake ..
```

**Linux:**
```bash
cmake ..
```

### 4. Build

**Windows (Visual Studio):**
```cmd
cmake --build . --config Release
```

**Other Platforms:**
```bash
cmake --build . --config Release
```

### 5. Verify Build

After successful build, you should see:
- Windows: `build/Release/win.xpl` or `build/win.xpl`
- macOS: `build/mac.xpl`
- Linux: `build/lin.xpl`

## Installation

### Plugin Directory Structure

The plugin must be installed in X-Plane's plugin directory with the following structure:

```
X-Plane 12/
└── Resources/
    └── plugins/
        └── XBlackBox/
            ├── 64/
            │   └── [platform].xpl    (win.xpl, mac.xpl, or lin.xpl)
            └── (optional files)
```

### Installation Steps

1. **Create plugin directory:**
   ```bash
   # Navigate to X-Plane installation
   cd "X-Plane 12/Resources/plugins"
   mkdir -p XBlackBox/64
   ```

2. **Copy plugin file:**
   
   **Windows:**
   ```cmd
   copy <build-dir>\win.xpl "X-Plane 12\Resources\plugins\XBlackBox\64\"
   ```
   
   **macOS:**
   ```bash
   cp build/mac.xpl "X-Plane 12/Resources/plugins/XBlackBox/64/"
   ```
   
   **Linux:**
   ```bash
   cp build/lin.xpl "X-Plane 12/Resources/plugins/XBlackBox/64/"
   ```

3. **Set permissions (macOS/Linux):**
   ```bash
   chmod +x "X-Plane 12/Resources/plugins/XBlackBox/64/*.xpl"
   ```

### Verify Installation

1. Start X-Plane 12
2. Check the log file: `X-Plane 12/Log.txt`
3. Look for lines like:
   ```
   XBlackBox: Plugin starting...
   XBlackBox: Plugin started successfully
   ```
4. Open the Plugins menu - you should see "XBlackBox"

## Troubleshooting

### Build Issues

**CMake can't find OpenGL (Linux):**
```bash
# Install OpenGL development packages
sudo apt-get install libgl1-mesa-dev
```

**Compiler not found:**
```bash
# Specify compiler explicitly
cmake .. -DCMAKE_CXX_COMPILER=g++
```

**Wrong Visual Studio version (Windows):**
```cmd
# List available generators
cmake --help
# Use the correct generator
cmake .. -G "Visual Studio 16 2019" -A x64
```

### Plugin Loading Issues

**Plugin not visible in X-Plane:**
1. Check file permissions (must be executable on macOS/Linux)
2. Verify directory structure is correct
3. Check X-Plane Log.txt for error messages
4. Ensure you're using the 64-bit version

**"Could not load plugin" error:**
1. Check that you have the correct platform version (win/mac/lin)
2. Verify all dependencies are present
3. On macOS, check for code signing issues:
   ```bash
   xattr -cr "X-Plane 12/Resources/plugins/XBlackBox/64/mac.xpl"
   ```

**Plugin crashes on load:**
1. Check X-Plane version compatibility (requires X-Plane 12)
2. Review Log.txt for specific error messages
3. Try with a clean X-Plane installation

### Runtime Issues

**Menu not appearing:**
- Wait a few seconds after X-Plane starts
- Check that the plugin loaded successfully in Log.txt

**Recording not starting:**
- Check Output/XBlackBox/ directory exists
- Verify you have write permissions
- Check available disk space

**Files not being created:**
- Ensure Output/XBlackBox/ directory exists
- Check disk space and permissions
- Review XBlackBox messages in Log.txt

## Development Build

For development and debugging:

**Debug build:**
```bash
cmake --build . --config Debug
```

**Enable verbose output:**
```bash
cmake .. -DCMAKE_VERBOSE_MAKEFILE=ON
cmake --build . --config Release -- VERBOSE=1
```

**Clean and rebuild:**
```bash
cmake --build . --target clean
cmake --build . --config Release
```

## Cross-Compilation

### Building Windows Plugin on Linux (MinGW)

```bash
# Install MinGW
sudo apt-get install mingw-w64

# Configure for Windows
cmake .. -DCMAKE_TOOLCHAIN_FILE=../cmake/mingw-w64-x86_64.cmake

# Build
cmake --build .
```

### Building macOS Plugin on Linux (requires OSX cross toolchain)

Cross-compilation for macOS is complex and typically requires:
- OSX Cross toolchain
- macOS SDK
- Proper CMake toolchain file

It's recommended to build macOS plugins on macOS.

## Continuous Integration

This repository includes a GitHub Actions workflow that automatically builds the plugin for all platforms on push to the default branch.

### Automated Builds

The CI workflow (`.github/workflows/build.yml`) automatically:
1. Builds the plugin for Windows, macOS, and Linux
2. Creates a fat plugin package with the X-Plane standard structure:
   ```
   XBlackBox.zip/
       XBlackBox/
           win_x64/
               XBlackBox.xpl
           mac_x64/
               XBlackBox.xpl
           lin_x64/
               XBlackBox.xpl
           README.txt (bilingual English/Chinese)
           LICENSE.txt
   ```
3. Uploads the package as an artifact (available for 90 days)

### Manual CI Commands

For manual CI/CD pipelines:

```bash
# One-line build
mkdir build && cd build && cmake .. && cmake --build . --config Release

# Run with specific number of parallel jobs
cmake --build . --config Release -- -j4
```

## Performance Optimization

**Release build with optimizations:**
```bash
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS="-O3 -march=native"
cmake --build .
```

**Size-optimized build:**
```bash
cmake .. -DCMAKE_BUILD_TYPE=MinSizeRel
cmake --build .
```

## Additional Resources

- [X-Plane SDK Documentation](https://developer.x-plane.com/sdk/)
- [CMake Documentation](https://cmake.org/documentation/)
- [Project Repository](https://github.com/CCA3370/XBlackBox)

## Support

For build issues or questions:
1. Check existing GitHub Issues
2. Review X-Plane's Log.txt file
3. Create a new issue with:
   - Your platform and versions
   - Complete build output
   - Any error messages from Log.txt
