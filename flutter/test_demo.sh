#!/bin/bash

# 🚀 Brand Intelligence Hub - Quick Demo Script

echo "🎯 Brand Intelligence Hub Demo Setup"
echo "======================================"

# Set environment variables
export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home
export ANDROID_HOME=/opt/homebrew/share/android-commandlinetools
export PATH=$ANDROID_HOME/platform-tools:$PATH

echo "✅ Environment configured"
echo "   JAVA_HOME: $JAVA_HOME"
echo "   ANDROID_HOME: $ANDROID_HOME"

# Check if web server is running
if lsof -i :8080 > /dev/null 2>&1; then
    echo "✅ Web server is already running on port 8080"
    echo "   URL: http://localhost:8080"
else
    echo "🚀 Starting Flutter web server..."
    flutter run -d web-server --web-port 8080 &
    sleep 5
    echo "✅ Web server started on port 8080"
fi

# Check for connected Android devices
echo ""
echo "📱 Checking for Android devices..."
devices=$(adb devices | grep -v "List of devices" | grep "device" | wc -l)
if [ $devices -gt 0 ]; then
    echo "✅ Found $devices Android device(s) connected"
    adb devices
    echo ""
    echo "🎯 To run on Android device:"
    echo "   flutter run"
else
    echo "⚠️  No Android devices connected"
    echo "   Connect device via USB and enable USB debugging"
fi

echo ""
echo "🌐 Demo Options:"
echo "=================="
echo "1. WEB DEMO (Recommended for Mac):"
echo "   • Open: http://localhost:8080"
echo "   • Press F12 → Click 📱 icon → Select iPhone/Pixel"
echo ""
echo "2. ANDROID DEVICE DEMO:"
echo "   • Connect Android device via USB"
echo "   • Run: flutter run"
echo ""
echo "3. APK INSTALLATION:"
echo "   • File: build/app/outputs/flutter-apk/app-release.apk"
echo "   • Size: 24.9MB (production ready)"
echo ""
echo "🎯 Test Sequence:"
echo "=================="
echo "1. Setup Tab → Enter: 'Oriental Bank', 'Customer Experience', 'First National Bank'"
echo "2. Click 'Launch Analysis' → Watch 8-step loading animation (2-4 seconds)"
echo "3. Analysis Tab → Check interactive charts and metrics"
echo "4. Insights Tab → Review AI-generated actionable insights"
echo "5. Roadmap Tab → Explore quarterly timeline"
echo "6. Report Tab → Test PDF generation and export"
echo ""
echo "🎉 Demo Ready! Open http://localhost:8080 to start"