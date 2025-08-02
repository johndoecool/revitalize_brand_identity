# Brand Intelligence Hub - iOS Deployment Guide

## 📱 One-Click iOS Deployment

This guide covers the automated iOS deployment script that handles everything from device detection to app installation.

## 🚀 Quick Start

### Prerequisites
- ✅ iOS device connected via USB
- ✅ Device trusted and unlocked
- ✅ Xcode installed with iOS development setup
- ✅ Flutter environment configured

### Deploy to Connected iOS Device

```bash
# Deploy release build (default)
./deploy_ios.sh

# Deploy debug build
./deploy_ios.sh --debug

# Deploy release build (explicit)
./deploy_ios.sh --release
```

## 📋 What the Script Does

### 1. **Pre-Flight Checks**
- ✅ Verifies Flutter directory exists
- ✅ Checks backend services status (ports 8001, 8002, 8003)
- ✅ Automatically detects connected iOS devices

### 2. **Device Detection**
- 🔍 Scans for connected iOS devices
- 📱 Auto-selects first iOS device if multiple found
- ⚠️ Warns if multiple devices detected
- ❌ Fails gracefully if no devices found

### 3. **Build Process**
- 🧹 Cleans Flutter project
- 📦 Gets Flutter dependencies (`flutter pub get`)
- 🍎 Installs iOS dependencies (`pod install`)
- 🏗️ Builds iOS app (release or debug mode)
- 📊 Reports build size and status

### 4. **Deployment**
- 📲 Installs app on detected device
- ✅ Verifies successful installation
- 📱 Provides launch instructions

## 🎯 Example Output

```bash
$ ./deploy_ios.sh

📱 Brand Intelligence Hub - iOS Deployment
===========================================
Build Mode: release

✅ Flutter directory found
[19:41:47] Checking backend services...
✅ brand-service: Running on port 8001
✅ data-collection: Running on port 8002
✅ analysis-engine: Running on port 8003
✅ All backend services are running
[19:41:47] Detecting connected iOS devices...
✅ Selected device: Avishek's iPhone
ℹ️  Device ID: 00008110-0005556C2281801E

[19:41:47] Starting deployment process...
✅ Flutter project cleaned
✅ Flutter dependencies updated
✅ CocoaPods dependencies installed
✅ iOS build completed (29.6MB)
ℹ️  Build location: build/ios/iphoneos/Runner.app
✅ App installed successfully
✅ App verification successful
ℹ️  Bundle ID: com.avishekdas.brandIntelligenceHub
ℹ️  Version: 1.0.0

🎉 iOS Deployment Completed Successfully!
============================================

📱 Device: Avishek's iPhone
📦 Build Mode: release
🆔 Device ID: 00008110-0005556C2281801E
📋 App Name: Brand Intelligence Hub

📲 Next Steps:
1. Look for 'Brand Intelligence Hub' on your device
2. Tap the app icon to launch it
3. Test the app functionality

🔧 Backend Services:
Make sure backend services are running for full functionality:
  ./start_all_services.sh

🔄 To redeploy:
  ./deploy_ios.sh                    # Release build
  ./deploy_ios.sh --debug            # Debug build
```

## 🔧 Command Options

| Command | Description | Build Type |
|---------|-------------|------------|
| `./deploy_ios.sh` | Default deployment | Release (optimized) |
| `./deploy_ios.sh --release` | Explicit release build | Release (optimized) |
| `./deploy_ios.sh --debug` | Debug deployment | Debug (with debugging) |
| `./deploy_ios.sh --help` | Show help | N/A |

## 🔍 Backend Service Integration

The script automatically checks if backend services are running:

### ✅ All Services Running
```
✅ brand-service: Running on port 8001
✅ data-collection: Running on port 8002
✅ analysis-engine: Running on port 8003
✅ All backend services are running
```

### ⚠️ Services Not Running
```
⚠️  brand-service: Not responding on port 8001
⚠️  data-collection: Not responding on port 8002
⚠️  Some backend services are not running:
ℹ️    • brand-service (port 8001)
ℹ️    • data-collection (port 8002)
ℹ️  To start all services: ./start_all_services.sh
ℹ️  Continuing with deployment...
```

## 📱 Device Management

### Single Device
```
✅ Selected device: Avishek's iPhone
ℹ️  Device ID: 00008110-0005556C2281801E
```

### Multiple Devices
```
⚠️  Multiple iOS devices detected (2 devices)
ℹ️  Using the first device found:
✅ Selected device: Avishek's iPhone
ℹ️  Device ID: 00008110-0005556C2281801E
```

### No Devices
```
❌ No iOS devices found
ℹ️  Please connect an iOS device and ensure it's trusted
ℹ️  You can check connected devices with: flutter devices
```

## 🚨 Troubleshooting

### Common Issues

#### 1. **No Devices Found**
```bash
# Check connected devices
flutter devices

# Ensure device is trusted
# Unlock device and tap "Trust" when prompted
```

#### 2. **Build Failures**
```bash
# Check Flutter doctor
flutter doctor

# Clean and retry
flutter clean
./deploy_ios.sh
```

#### 3. **Installation Failures**
- **Code Signing**: Check Xcode project settings
- **Device Space**: Ensure device has enough storage
- **Trust**: Make sure device trusts the developer certificate

#### 4. **Backend Services Warning**
```bash
# Start all backend services
./start_all_services.sh

# Check service status
./start_all_services.sh status
```

### Debug Mode vs Release Mode

| Mode | Build Time | App Size | Performance | Debugging |
|------|-----------|----------|-------------|-----------|
| **Debug** | Faster | Larger | Slower | Full debugging |
| **Release** | Slower | Smaller | Optimized | No debugging |

**Recommendations:**
- Use **debug** for development and testing
- Use **release** for demonstrations and production

## 🔗 Integration with Other Scripts

### Workflow Integration
```bash
# 1. Start backend services
./start_all_services.sh

# 2. Deploy to iOS
./deploy_ios.sh

# 3. Test integration
cd tests/integration
python test_consumer.py --test-type health
```

### Continuous Development
```bash
# Quick redeploy during development
./deploy_ios.sh --debug

# Production deployment
./deploy_ios.sh --release
```

## 📝 Script Features

### ✅ **Automated Features**
- Device auto-detection
- Backend service health checks
- Dependency management
- Build optimization
- Installation verification
- Error handling with recovery suggestions

### 🎨 **User Experience**
- Color-coded output
- Progress indicators
- Clear status messages
- Comprehensive completion summary
- Helpful error messages

### 🛡️ **Error Handling**
- Graceful failure handling
- Recovery suggestions
- Warning vs critical error distinction
- Detailed error reporting

## 🔄 Related Commands

```bash
# Backend management
./start_all_services.sh          # Start all services
./start_all_services.sh status   # Check service status
./start_all_services.sh stop     # Stop all services

# iOS deployment
./deploy_ios.sh                  # Deploy release build
./deploy_ios.sh --debug          # Deploy debug build

# Testing
cd tests/integration && python test_consumer.py --test-type health

# Flutter commands
flutter devices                  # List connected devices
flutter clean                   # Clean project
flutter doctor                  # Check Flutter setup
```

The iOS deployment script provides a seamless, one-click solution for deploying the Brand Intelligence Hub to connected iOS devices with comprehensive error handling and user guidance.