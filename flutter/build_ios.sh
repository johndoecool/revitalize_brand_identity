#!/bin/bash

# iOS App Build Script for Brand Intelligence Hub
# Creates distributable iOS app for development/ad-hoc distribution

set -e  # Exit on any error

echo "🍎 Starting iOS app build process..."
echo "================================================="

# Check if we're in the right directory
if [ ! -f "pubspec.yaml" ]; then
    echo "❌ Error: pubspec.yaml not found. Please run this script from the Flutter project root."
    exit 1
fi

# Check if Xcode is available
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Error: Xcode command line tools not found. Please install Xcode."
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
flutter clean

# Get dependencies
echo "📦 Getting Flutter dependencies..."
flutter pub get

# Install iOS dependencies
echo "🔧 Installing iOS dependencies..."
cd ios
pod install --repo-update
cd ..

# Build iOS app
echo "🏗️  Building iOS app..."
flutter build ios --release --no-codesign

# Create distribution directory
DIST_DIR="dist/ios"
mkdir -p "$DIST_DIR"

# Archive the app for distribution
echo "📦 Creating iOS app archive..."
WORKSPACE_PATH="ios/Runner.xcworkspace"
SCHEME="Runner"
ARCHIVE_PATH="$DIST_DIR/BrandIntelligenceHub.xcarchive"

xcodebuild archive \
    -workspace "$WORKSPACE_PATH" \
    -scheme "$SCHEME" \
    -archivePath "$ARCHIVE_PATH" \
    -configuration Release \
    CODE_SIGN_IDENTITY="" \
    CODE_SIGNING_REQUIRED=NO \
    CODE_SIGNING_ALLOWED=NO

# Export the app
echo "📱 Exporting iOS app..."
APP_PATH="$DIST_DIR/BrandIntelligenceHub.app"
cp -R "$ARCHIVE_PATH/Products/Applications/Runner.app" "$APP_PATH"

# Create IPA (optional, for easier distribution)
echo "📦 Creating IPA file..."
IPA_PATH="$DIST_DIR/BrandIntelligenceHub.ipa"
cd "$DIST_DIR"
zip -r "BrandIntelligenceHub.ipa" "BrandIntelligenceHub.app"
cd - > /dev/null

# Get build info
echo ""
echo "📊 Build Summary:"
echo "================================================="
if [ -d "$APP_PATH" ]; then
    echo "App Bundle Size:   $(du -sh "$APP_PATH" | cut -f1)"
fi
if [ -f "$IPA_PATH" ]; then
    echo "IPA Size:          $(du -h "$IPA_PATH" | cut -f1)"
fi
echo ""
echo "✅ iOS app built successfully!"
echo "📂 Distribution files located in: $DIST_DIR"
echo ""
echo "📱 Installation Instructions:"
echo ""
echo "Method 1 - iOS Simulator:"
echo "1. Open iOS Simulator"
echo "2. Drag and drop BrandIntelligenceHub.app to simulator"
echo ""
echo "Method 2 - Physical Device (Development):"
echo "1. Connect device to Mac"
echo "2. Open Xcode"
echo "3. Window > Devices and Simulators"
echo "4. Select your device"
echo "5. Click '+' and select BrandIntelligenceHub.app"
echo ""
echo "Method 3 - TestFlight (Enterprise/App Store):"
echo "1. Use BrandIntelligenceHub.ipa"
echo "2. Upload to App Store Connect"
echo "3. Distribute via TestFlight"
echo ""
echo "⚠️  Note: For physical device installation, you may need:"
echo "   - Valid Apple Developer account"
echo "   - Device UDID registered"
echo "   - Proper code signing certificates"
echo ""
echo "🚀 Ready for distribution!"