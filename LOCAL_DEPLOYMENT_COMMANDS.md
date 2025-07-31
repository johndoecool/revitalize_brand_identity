# Local Deployment Commands

## Start Brand Service

```bash
cd brand-service
python start_server.py
```

## Deploy Flutter App to iOS (Release)

```bash
cd flutter
flutter clean
flutter pub get
cd ios
pod install
cd ..
flutter build ios --release
xcrun devicectl list devices
flutter install --device-id="00008110-0005556C2281801E"
```

## Start Flutter Web App

```bash
cd flutter
flutter run -d web-server --web-port 3000
```

## Verify Services

```bash
# Check brand service
curl -s -w "%{http_code}" http://10.0.0.70:8001/ -o /dev/null

# Check app on device
xcrun devicectl device info apps --device "00008110-0005556C2281801E" | grep -A 5 "brandIntelligenceHub"
```
