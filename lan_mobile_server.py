# -*- coding: utf-8 -*-
"""
lan_mobile_server.py — Chạy máy chủ Wi-Fi nội bộ để mở & cài trực tiếp
ứng dụng Minh Phú HVAC lên iPhone / iPad (Safari -> Thêm vào MH chính)
và Android (Chrome -> Cài đặt ứng dụng) ngay lập tức!
"""
import socket
import bottle
import app_desktop


def get_lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    port = 8765
    ip = get_lan_ip()
    print("=" * 72)
    print("  MINH PHU HVAC — MAY CHU CAI DAT NHANH CHO IPHONE / IPAD / ANDROID")
    print("=" * 72)
    print(f"  1. Dam bao dien thoai va may tinh dung chung mang Wi-Fi.")
    print(f"  2. Mo Safari (iPhone/iPad) hoac Chrome (Android) va truy cap:")
    print(f"       http://{ip}:{port}")
    print(f"  3. Tren iPhone/iPad: Bam nut Chia se (mui ten len) -> 'Them vao MH chinh'")
    print(f"     de tao bieu tuong App Minh Phu HVAC chay toan man hinh!")
    print("=" * 72)
    bottle.run(app_desktop.http_app, host="0.0.0.0", port=port, quiet=False)
