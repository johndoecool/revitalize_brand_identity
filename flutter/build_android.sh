#!/bin/bash

# Android APK Build Script for Brand Intelligence Hub
# Creates distributable release APK

set -e  # Exit on any error

echo "🤖 Starting Android APK build process..."
echo "================================================="

# Check if we're in the right directory
if [ ! -f "pubspec.yaml" ]; then
    echo "❌ Error: pubspec.yaml not found. Please run this script from the Flutter project root."
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
flutter clean

# Get dependencies
echo "📦 Getting Flutter dependencies..."
flutter pub get

# Build release APK
echo "🏗️  Building release APK..."
flutter build apk --release --split-per-abi

# Create distribution directory
DIST_DIR="dist/android"
mkdir -p "$DIST_DIR"

# Copy APKs to distribution directory
echo "📋 Copying APKs to distribution directory..."
cp build/app/outputs/flutter-apk/app-arm64-v8a-release.apk "$DIST_DIR/brand-intelligence-hub-arm64.apk"
cp build/app/outputs/flutter-apk/app-armeabi-v7a-release.apk "$DIST_DIR/brand-intelligence-hub-armv7.apk"
cp build/app/outputs/flutter-apk/app-x86_64-release.apk "$DIST_DIR/brand-intelligence-hub-x64.apk"

# Also create universal APK
echo "🌍 Building universal APK..."
flutter build apk --release
cp build/app/outputs/flutter-apk/app-release.apk "$DIST_DIR/brand-intelligence-hub-universal.apk"

# Get file sizes
echo ""
echo "📊 Build Summary:"
echo "================================================="
echo "Universal APK:     $(du -h "$DIST_DIR/brand-intelligence-hub-universal.apk" | cut -f1)"
echo "ARM64 APK:         $(du -h "$DIST_DIR/brand-intelligence-hub-arm64.apk" | cut -f1)"
echo "ARMv7 APK:         $(du -h "$DIST_DIR/brand-intelligence-hub-armv7.apk" | cut -f1)"
echo "x86_64 APK:        $(du -h "$DIST_DIR/brand-intelligence-hub-x64.apk" | cut -f1)"
echo ""
echo "✅ Android APKs built successfully!"
echo "📂 Distribution files located in: $DIST_DIR"
echo ""
echo "📱 Installation Instructions:"
echo "1. Transfer APK to Android device"
echo "2. Enable 'Install from Unknown Sources' in Settings"
echo "3. Tap APK file to install"
echo "4. Use Universal APK for best compatibility"
echo ""
echo "🚀 Ready for distribution!"