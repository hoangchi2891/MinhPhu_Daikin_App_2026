# Hướng Dẫn Chạy & Đóng Gói Phần Mềm Minh Phú HVAC (Windows `.exe` • Android `.apk` • iOS `.ipa` / iPhone)

## 1. Phiên Bản Windows Desktop (`.exe`) — Chạy Ngay 100% Offline
- **File chạy trực tiếp**: `H:\DAIKIN\MinhPhu_Daikin_App\dist\MinhPhu_Daikin_Quote\MinhPhu_Daikin_Quote.exe`
- **Bản đóng gói di động (.zip để gửi sang máy Windows khác)**: `H:\DAIKIN\MinhPhu_Daikin_App\dist\MinhPhu_Daikin_Quote_Windows_Portable.zip`
- **Tích hợp sẵn**:
  - Bộ font tiếng Việt chuẩn **Noto Sans Regular & Bold** (`web/assets/fonts/`) — khắc phục triệt để lỗi font/dấu tiếng Việt ở phần Tính Toán Nhiệt TCVN 5687:2024 trên mọi phiên bản Windows 10/11.
  - Đầy đủ 207 Model Daikin & Côn đầu máy từ Excel, Tính tải nhiệt TCVN 5687:2024 (Chế độ Offline chi tiết nhiều dàn lạnh/phòng & Chế độ AI đa Model), Quét bản vẽ PDF/CAD DXF/DWG, Daikin Duct Checker, CoolPack R410A/R32, Xuất Báo giá & Báo cáo Kỹ thuật PDF/Excel công thức sống.

---

## 2. Phiên Bản Android (`.apk`) — Cài Đặt Trực Tiếp Lên Điện Thoại / Máy Tính Bảng Android
- **File `.apk` sau khi biên dịch**: `H:\DAIKIN\MinhPhu_Daikin_App\dist\MinhPhu_Daikin_Quote.apk`
- **Cách cài lên điện thoại Android**:
  1. Copy file `MinhPhu_Daikin_Quote.apk` sang điện thoại Android (qua cáp USB, Zalo, Google Drive...).
  2. Chạm vào file `.apk` -> Chọn **"Cho phép cài đặt từ nguồn này"** -> bấm **Cài đặt (Install)**.
  3. Mở ứng dụng **Minh Phú HVAC** — chạy 100% offline không cần mạng (hỗ trợ xuất báo giá PDF qua trình in Android & tải Excel `.xls`).
- **Biên dịch lại `.apk` sau này khi sửa code**:
  Chạy `powershell -ExecutionPolicy Bypass -File "H:\DAIKIN\MinhPhu_Daikin_App\android_apk_project\build_apk_windows.ps1"`.

---

## 3. Phiên Bản iOS (`.ipa`) & Cài Nhanh Trên iPhone / iPad
> **Lưu ý kỹ thuật của Apple**: File `.ipa` chuẩn arm64 bắt buộc phải được biên dịch bằng **Xcode trên macOS** (không thể biên dịch trực tiếp nhân Mach-O của iOS trên Windows). Vì vậy hệ thống đã chuẩn bị sẵn **3 cách triển khai đầy đủ**:

### Cách A — Cài Ngay Lên iPhone / iPad Trong 30 Giây (Không Cần Mac / Không Cần App Store — PWA Toàn Màn Hình)
1. Trên máy tính Windows, nhấp đúp file `H:\DAIKIN\Chay_App_Tren_iPhone_Android_WiFi.bat`.
2. Đảm bảo iPhone/iPad dùng chung Wi-Fi với máy tính, mở **Safari** nhập địa chỉ `http://<IP-May-Tinh>:8765` hiển thị trên màn hình.
3. Trong Safari, bấm biểu tượng **Chia sẻ (mũi tên lên)** → chọn **"Thêm vào MH chính" (Add to Home Screen)** → bấm **Thêm**.
4. Biểu tượng **Minh Phú HVAC** sẽ xuất hiện trên màn hình chính iPhone/iPad, chạy toàn màn hình với đầy đủ font tiếng Việt Noto Sans, tính tải nhiệt TCVN 5687, ống gió, CoolPack và báo giá!

### Cách B — Tự Động Xuất File `.ipa` (Và `.apk`) Miễn Phí Trên Đám Mây macOS (GitHub Actions — Không Cần Máy Mac)
1. Tải thư mục `H:\DAIKIN\MinhPhu_Daikin_App\` lên một kho lưu trữ GitHub (Private hoặc Public đều được).
2. Vào tab **Actions** → chọn workflow **`Build Android APK & iOS IPA (Minh Phu HVAC)`** (đã cấu hình sẵn tại `.github/workflows/build_android_ios.yml`) → bấm **Run workflow**.
3. Sau ~4 phút, tải trực tiếp cả 2 file:
   - `MinhPhu_Daikin_Quote_Android_APK` (`.apk`)
   - `MinhPhu_Daikin_Quote_iOS_IPA` (`MinhPhu_Daikin_Quote_iOS.ipa`)
4. Cài file `.ipa` lên iPhone/iPad bằng **Sideloadly**, **AltStore**, hoặc ký bằng tài khoản **Apple Developer** để phát hành nội bộ / TestFlight / App Store.

### Cách C — Biên Dịch `.ipa` Trực Tiếp Trên Máy Mac (Xcode 15+)
1. Copy thư mục `H:\DAIKIN\MinhPhu_Daikin_App\` sang máy Mac.
2. Mở Terminal trong thư mục `ios_ipa_project` và chạy:
   ```bash
   chmod +x build_ipa_macos.sh
   ./build_ipa_macos.sh
   ```
3. File `MinhPhu_Daikin_Quote_iOS.ipa` sẽ được xuất ra tại `dist/MinhPhu_Daikin_Quote_iOS.ipa`.
