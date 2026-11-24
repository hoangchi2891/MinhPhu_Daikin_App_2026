# ==============================================================================
# Script Tu Dong Dong Goi File .APK (Android) tren Windows — Minh Phu HVAC
# Ho tro: Tu dong dong bo web\ + Tai Portable OpenJDK 17, Gradle 8.9 & Android SDK 34
#         neu may tinh chua cai dat san, sau do bien dich ra file .apk cai dat ngay!
# ==============================================================================
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = $PSScriptRoot
$AppRoot    = Split-Path -Parent $ProjectDir
$WebSrc     = Join-Path $AppRoot "web"
$AssetsDst  = Join-Path $ProjectDir "app\src\main\assets\www"
$ToolsDir   = Join-Path $ProjectDir ".android_toolchain"
$DistDir    = Join-Path $AppRoot "dist"
New-Item -ItemType Directory -Force -Path $ToolsDir, $DistDir | Out-Null

Write-Host "[1/5] Dong bo 207 Model Daikin, Font Tieng Viet Noto Sans & Bo Tinh Nhiet TCVN 5687..." -ForegroundColor Cyan
if (Test-Path $AssetsDst) { Remove-Item -Recurse -Force $AssetsDst }
New-Item -ItemType Directory -Force -Path $AssetsDst | Out-Null
Copy-Item -Path "$WebSrc\*" -Destination $AssetsDst -Recurse -Force

# 2. Ensure Portable OpenJDK 17
$JdkRoot = Join-Path $ToolsDir "jdk17"
$JavaExe = Get-ChildItem -Path $JdkRoot -Filter "java.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $JavaExe) {
    Write-Host "[2/5] Dang tai Portable OpenJDK 17 (Adoptium Temurin ~185 MB)..." -ForegroundColor Yellow
    $JdkZip = Join-Path $ToolsDir "jdk17.zip"
    $JdkUrl = "https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse"
    Invoke-WebRequest -Uri $JdkUrl -OutFile $JdkZip -UseBasicParsing
    New-Item -ItemType Directory -Force -Path $JdkRoot | Out-Null
    Expand-Archive -Path $JdkZip -DestinationPath $JdkRoot -Force
    Remove-Item $JdkZip -Force
    $JavaExe = Get-ChildItem -Path $JdkRoot -Filter "java.exe" -Recurse | Select-Object -First 1
}
$env:JAVA_HOME = Split-Path -Parent (Split-Path -Parent $JavaExe.FullName)
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"
Write-Host "      JAVA_HOME = $env:JAVA_HOME" -ForegroundColor Green

# 3. Ensure Portable Gradle 8.9
$GradleRoot = Join-Path $ToolsDir "gradle"
$GradleBat = Get-ChildItem -Path $GradleRoot -Filter "gradle.bat" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $GradleBat) {
    Write-Host "[3/5] Dang tai Portable Gradle 8.9 (~130 MB)..." -ForegroundColor Yellow
    $GradleZip = Join-Path $ToolsDir "gradle-8.9-bin.zip"
    Invoke-WebRequest -Uri "https://services.gradle.org/distributions/gradle-8.9-bin.zip" -OutFile $GradleZip -UseBasicParsing
    New-Item -ItemType Directory -Force -Path $GradleRoot | Out-Null
    Expand-Archive -Path $GradleZip -DestinationPath $GradleRoot -Force
    Remove-Item $GradleZip -Force
    $GradleBat = Get-ChildItem -Path $GradleRoot -Filter "gradle.bat" -Recurse | Select-Object -First 1
}
Write-Host "      GRADLE = $($GradleBat.FullName)" -ForegroundColor Green

# 4. Ensure Android Command-Line Tools & SDK 34
$AndroidSdk = if ($env:ANDROID_HOME -and (Test-Path $env:ANDROID_HOME)) { $env:ANDROID_HOME } else { Join-Path $ToolsDir "android_sdk" }
$SdkMgr = Join-Path $AndroidSdk "cmdline-tools\latest\bin\sdkmanager.bat"
if (-not (Test-Path $SdkMgr)) {
    Write-Host "[4/5] Dang tai Android Command-Line Tools & SDK API 34..." -ForegroundColor Yellow
    $CmdZip = Join-Path $ToolsDir "cmdline-tools.zip"
    Invoke-WebRequest -Uri "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip" -OutFile $CmdZip -UseBasicParsing
    $TmpCmd = Join-Path $ToolsDir "tmp_cmd"
    if (Test-Path $TmpCmd) { Remove-Item -Recurse -Force $TmpCmd }
    Expand-Archive -Path $CmdZip -DestinationPath $TmpCmd -Force
    New-Item -ItemType Directory -Force -Path (Join-Path $AndroidSdk "cmdline-tools") | Out-Null
    $LatestDir = Join-Path $AndroidSdk "cmdline-tools\latest"
    if (Test-Path $LatestDir) { Remove-Item -Recurse -Force $LatestDir }
    Move-Item -Path (Join-Path $TmpCmd "cmdline-tools") -Destination $LatestDir
    Remove-Item -Recurse -Force $TmpCmd, $CmdZip
}
$env:ANDROID_HOME = $AndroidSdk
$env:ANDROID_SDK_ROOT = $AndroidSdk

$PlatformJar = Join-Path $AndroidSdk "platforms\android-34\android.jar"
$BuildToolsDir = Join-Path $AndroidSdk "build-tools\34.0.0"
if ((-not (Test-Path $PlatformJar)) -or (-not (Test-Path $BuildToolsDir))) {
    Write-Host "      Dang cai dat platform-tools, platforms;android-34 va build-tools;34.0.0..." -ForegroundColor Yellow
    1..30 | ForEach-Object { "y" } | & $SdkMgr "--sdk_root=$AndroidSdk" --licenses | Out-Null
    1..30 | ForEach-Object { "y" } | & $SdkMgr "--sdk_root=$AndroidSdk" "platform-tools" "platforms;android-34" "build-tools;34.0.0"
}

# Write local.properties for Gradle
$EscSdk = $AndroidSdk -replace "\\", "\\\\"
Set-Content -Path (Join-Path $ProjectDir "local.properties") -Value "sdk.dir=$EscSdk" -Encoding ASCII

# 5. Compile APK
Write-Host "[5/5] Dang bien dich file MinhPhu_Daikin_Quote.apk..." -ForegroundColor Cyan
Push-Location $ProjectDir
try {
    & $GradleBat.FullName --no-daemon assembleDebug
} finally {
    Pop-Location
}

$ApkBuilt = Join-Path $ProjectDir "app\build\outputs\apk\debug\app-debug.apk"
if (-not (Test-Path $ApkBuilt)) {
    throw "Khong tim thay file APK sau khi bien dich: $ApkBuilt"
}
$ApkFinal = Join-Path $DistDir "MinhPhu_Daikin_Quote.apk"
Copy-Item -Path $ApkBuilt -Destination $ApkFinal -Force
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "THANH CONG! File Android APK da san sang tai:" -ForegroundColor Green
Write-Host "  $ApkFinal" -ForegroundColor White
Write-Host "=================================================================" -ForegroundColor Green
