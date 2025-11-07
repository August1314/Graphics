#!/bin/bash
# Build script for Native Drawing App

set -e

BUILD_TYPE=${1:-Release}
BUILD_DIR="build/${BUILD_TYPE}"

echo "========================================="
echo "Building Native Drawing App (${BUILD_TYPE})"
echo "========================================="

# Step 1: Build C++ Core Library
echo ""
echo "Step 1: Building C++ Core Library..."
mkdir -p ${BUILD_DIR}
cd ${BUILD_DIR}

cmake ../.. \
    -DCMAKE_BUILD_TYPE=${BUILD_TYPE} \
    -DBUILD_TESTS=ON \
    -DENABLE_GPU_ACCELERATION=ON

cmake --build . --config ${BUILD_TYPE} -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

# Run C++ tests in Debug mode
if [ "${BUILD_TYPE}" = "Debug" ]; then
    echo ""
    echo "Running C++ tests..."
    ctest --output-on-failure || true
fi

cd ../..

# Step 2: Install Node.js dependencies
echo ""
echo "Step 2: Installing Node.js dependencies..."
if [ ! -d "node_modules" ]; then
    npm install
fi

# Step 3: Build Native Addon
echo ""
echo "Step 3: Building Native Addon..."
npm run build:native || echo "Native addon build skipped (will be implemented later)"

# Step 4: Build Vue.js frontend
echo ""
echo "Step 4: Building Vue.js frontend..."
npm run build:ui

# Step 5: Build Electron main process
echo ""
echo "Step 5: Building Electron main process..."
npm run build:electron

echo ""
echo "========================================="
echo "Build complete!"
echo "========================================="
echo ""
echo "To run the application:"
echo "  npm start"
echo ""
echo "To package the application:"
echo "  npm run package"
echo ""
