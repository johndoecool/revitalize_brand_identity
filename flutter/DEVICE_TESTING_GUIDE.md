# 📱 Device Testing & Simulation Guide

## 🔧 Build Commands (Already Completed)

### Set Environment Variables (Required for each terminal session)
```bash
export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home
export ANDROID_HOME=/opt/homebrew/share/android-commandlinetools
export PATH=$ANDROID_HOME/platform-tools:$PATH
```

### Build APKs
```bash
# Debug APK (for testing)
flutter build apk --debug

# Release APK (for distribution)
flutter build apk --release

# Build for multiple architectures
flutter build apk --release --split-per-abi
```

## 📱 Testing on Physical Android Device

### Step 1: Prepare Android Device
1. **Enable Developer Options**:
   - Go to `Settings` → `About Phone`
   - Tap `Build Number` 7 times
   - Developer options will appear in Settings

2. **Enable USB Debugging**:
   - Go to `Settings` → `Developer Options`
   - Turn on `USB Debugging`
   - Turn on `Install via USB` (if available)

3. **Connect Device**:
   - Connect Android device to Mac via USB cable
   - Allow USB debugging when prompted on device

### Step 2: Verify Device Connection
```bash
# Check if device is detected
adb devices

# Expected output:
# List of devices attached
# ABC123XYZ    device
```

### Step 3: Install and Test APK
```bash
# Option A: Install debug APK directly
flutter install

# Option B: Install specific APK file
adb install build/app/outputs/flutter-apk/app-debug.apk

# Option C: Install release APK
adb install build/app/outputs/flutter-apk/app-release.apk

# Uninstall if needed
adb uninstall com.example.revitalize_brand_identity
```

### Step 4: Run Development Mode (Live Testing)
```bash
# Run app with hot reload on connected device
flutter run

# Run in release mode
flutter run --release

# Run with verbose logging
flutter run -v
```

## 💻 Simulation on Mac (Android Emulator)

### Step 1: Install Android Emulator
```bash
# Install emulator package
sdkmanager "emulator"
sdkmanager "system-images;android-34;google_apis;arm64-v8a"

# Create virtual device
avdmanager create avd -n Pixel_7_API_34 -k "system-images;android-34;google_apis;arm64-v8a" -d "pixel_7"
```

### Step 2: Start Emulator
```bash
# List available virtual devices
emulator -list-avds

# Start emulator (background)
emulator -avd Pixel_7_API_34 &

# Or start with specific settings
emulator -avd Pixel_7_API_34 -gpu host -skin 1080x2400 &
```

### Step 3: Run App on Emulator
```bash
# Once emulator is running, deploy app
flutter run

# Or install APK on emulator
flutter install build/app/outputs/flutter-apk/app-debug.apk
```

## 🌐 Web Simulation (Easiest for Mac)

### Step 1: Start Web Development Server
```bash
# Start Flutter web server
flutter run -d web-server --web-port 8080

# Or use Python server for built version
python3 serve.py
```

### Step 2: Test Mobile Simulation in Browser
1. **Chrome DevTools Mobile Simulation**:
   - Open Chrome → `http://localhost:8080`
   - Press `F12` to open DevTools
   - Click device icon (📱) in toolbar
   - Select device: iPhone, Pixel, iPad, etc.
   - Test touch interactions and responsive design

2. **Safari Responsive Design**:
   - Open Safari → `http://localhost:8080`
   - Go to `Develop` → `Enter Responsive Design Mode`
   - Test different screen sizes

## 📊 Testing Checklist

### ✅ Functionality Tests
- [ ] **Setup Tab**: Brand input, area selection, competitor
- [ ] **Launch Analysis**: Loading animation (2-4 seconds)
- [ ] **Analysis Tab**: Charts and data visualization
- [ ] **Insights Tab**: Actionable insights display
- [ ] **Roadmap Tab**: Quarterly timeline
- [ ] **Report Tab**: PDF generation and export

### ✅ Mobile-Specific Tests
- [ ] **Touch Navigation**: Tab switching works smoothly
- [ ] **Responsive Layout**: Elements resize properly
- [ ] **Scroll Performance**: Smooth scrolling in all tabs
- [ ] **Form Inputs**: Text fields work with on-screen keyboard
- [ ] **Loading States**: Progress indicators display correctly
- [ ] **PDF Export**: Downloads work on mobile browser

### ✅ Performance Tests
- [ ] **App Launch Time**: < 3 seconds on device
- [ ] **Tab Switching**: Instant transitions
- [ ] **Chart Rendering**: Smooth animations
- [ ] **Memory Usage**: Stable during extended use

## 🛠️ Troubleshooting

### Device Not Detected
```bash
# Restart ADB server
adb kill-server
adb start-server

# Check USB connection mode on device
# Switch to "File Transfer" or "PTP" mode
```

### Build Errors
```bash
# Clean build cache
flutter clean
flutter pub get
flutter build apk --debug

# Force dependency update
flutter pub upgrade --major-versions
```

### Emulator Issues
```bash
# Delete and recreate AVD
avdmanager delete avd -n Pixel_7_API_34
avdmanager create avd -n Pixel_7_API_34 -k "system-images;android-34;google_apis;arm64-v8a"

# Start with more memory
emulator -avd Pixel_7_API_34 -memory 4096 &
```

## 🚀 Quick Testing Commands

### For Physical Device Testing:
```bash
# All-in-one setup and run
export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home
export ANDROID_HOME=/opt/homebrew/share/android-commandlinetools
flutter run --debug
```

### For Web Mobile Testing:
```bash
# Start web server and open in browser
flutter run -d web-server --web-port 8080
# Open: http://localhost:8080
# Use Chrome DevTools for mobile simulation
```

### For APK Distribution Testing:
```bash
# Build release APK
flutter build apk --release

# Share APK file from:
# build/app/outputs/flutter-apk/app-release.apk
```

## 📈 Performance Monitoring

### During Testing, Monitor:
```bash
# Real-time logs while app runs
flutter logs

# Performance profiling
flutter run --profile

# Memory usage monitoring
adb shell dumpsys meminfo com.example.revitalize_brand_identity
```

## 🎯 Demo Scenarios

### Scenario 1: Live Demo on Physical Device
1. Connect Android phone to Mac
2. Run `flutter run` for live demo with hot reload
3. Show real-time development capabilities

### Scenario 2: APK Installation Demo
1. Transfer `app-release.apk` to device
2. Install via file manager
3. Show production app experience

### Scenario 3: Cross-Platform Demo
1. Web version on Mac browser
2. Mobile simulation in Chrome DevTools
3. Native Android app on device
4. Show identical functionality across platforms

**Ready for comprehensive device testing and simulation!** 🚀