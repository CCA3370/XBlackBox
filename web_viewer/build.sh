#!/bin/bash
# Build script for XBlackBox Tauri Viewer

set -e

echo "==================================="
echo "XBlackBox Tauri Viewer Build Script"
echo "==================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js v16 or later."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed. Please install npm."
    exit 1
fi

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
    echo "Error: Rust is not installed. Please install Rust from https://rustup.rs/"
    exit 1
fi

echo ""
echo "Environment:"
echo "  Node.js: $(node --version)"
echo "  npm: $(npm --version)"
echo "  Rust: $(rustc --version)"
echo "  Cargo: $(cargo --version)"
echo ""

# Install npm dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

# Determine build mode
BUILD_MODE="${1:-release}"

case "$BUILD_MODE" in
    dev|development)
        echo "Building in development mode..."
        npm run dev
        ;;
    release|prod|production)
        echo "Building in release mode..."
        npm run build
        echo ""
        echo "Build complete!"
        echo ""
        echo "Binaries can be found in:"
        echo "  src-tauri/target/release/bundle/"
        echo ""
        echo "Executable:"
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            echo "  src-tauri/target/release/xblackbox-viewer"
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            echo "  src-tauri/target/release/bundle/macos/XBlackBox Viewer.app"
        elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
            echo "  src-tauri/target/release/xblackbox-viewer.exe"
        fi
        ;;
    *)
        echo "Usage: $0 [dev|release]"
        echo "  dev     - Build and run in development mode with hot reload"
        echo "  release - Build optimized production binary (default)"
        exit 1
        ;;
esac
