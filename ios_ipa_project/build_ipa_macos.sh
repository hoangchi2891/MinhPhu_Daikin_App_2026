#!/usr/bin/env bash
# Build Minh Phú HVAC iOS .ipa on macOS (Xcode 15+ & XcodeGen)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$SCRIPT_DIR"

echo "1. Syncing latest web/ assets (207 Daikin models, Noto Sans VN fonts, TCVN 5687 Heat Load)..."
rm -rf "$SCRIPT_DIR/www"
cp -R "$APP_ROOT/web" "$SCRIPT_DIR/www"

if ! command -v xcodegen >/dev/null 2>&1; then
  echo "Installing XcodeGen via Homebrew..."
  brew install xcodegen
fi

echo "2. Generating MinhPhuHVAC.xcodeproj..."
xcodegen generate --spec project.yml

echo "3. Compiling arm64 iOS Release binary..."
rm -rf build_ios Payload MinhPhu_Daikin_Quote_iOS.ipa
xcodebuild \
  -project MinhPhuHVAC.xcodeproj \
  -scheme MinhPhuHVAC \
  -configuration Release \
  -sdk iphoneos \
  -derivedDataPath build_ios \
  CODE_SIGN_IDENTITY="" \
  CODE_SIGNING_REQUIRED=NO \
  CODE_SIGNING_ALLOWED=NO \
  clean build

APP_PATH="build_ios/Build/Products/Release-iphoneos/MinhPhuHVAC.app"
mkdir -p Payload
cp -R "$APP_PATH" Payload/
zip -qry MinhPhu_Daikin_Quote_iOS.ipa Payload
rm -rf Payload

mkdir -p "$APP_ROOT/dist"
cp MinhPhu_Daikin_Quote_iOS.ipa "$APP_ROOT/dist/MinhPhu_Daikin_Quote_iOS.ipa"
echo "DONE! IPA exported to: $APP_ROOT/dist/MinhPhu_Daikin_Quote_iOS.ipa"
echo "Install on iPhone/iPad via Sideloadly / AltStore / Xcode (or re-sign with Apple Developer profile)."
