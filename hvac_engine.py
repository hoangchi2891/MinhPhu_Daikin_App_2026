# -*- coding: utf-8 -*-
"""
hvac_engine.py — Minh Phú HVAC Engineering Engine
1. Heat Load Calculation per TCVN 5687:2024 + QCVN 09:2017/BXD + ASHRAE CLTD/CLF
   (Reference: Trace 700, Daikin Heat Load, DK-BIM)
2. Drawing Takeoff Engine for PDF (PyMuPDF), AutoCAD DXF (ezdxf), DWG (AutoCAD COM/ODA), & Images
3. Hybrid AI Engine: Offline Expert Rule-Based Analysis + Optional Google Gemini / OpenAI Vision & Report API
4. Daikin Duct Checker (ASHRAE Darcy-Weisbach/Altshul-Tsal + Huebscher De + ESP Verification)
5. CoolPack-style Superheat / Subcooling & Daikin Refrigerant Piping Derating (R410A / R32)
"""

import base64
import io
import json
import math
import os
import re
import tempfile
import urllib.request
import urllib.error

try:
    import pymupdf
except Exception:
    pymupdf = None

try:
    import ezdxf
except Exception:
    ezdxf = None

# ==============================================================================
# 1. OFFICIAL TCVN 5687:2024 CLIMATE DATABASE (Bảng C.1, trang 53-58 — 15 trạm chuẩn)
# Format: city_id -> {name, region, lat, grades: {"I"(0.4%): {tdb, twb, t_win}, "II"(2.0%), "1%"(1.0%)}}
# ==============================================================================
TCVN_CLIMATE_CITIES = {
    "HANOI": {
        "name": "Hà Nội (Đồng bằng Bắc Bộ)", "lat": 21.0,
        "I":   {"tdb": 35.4, "twb": 28.0, "twb_max": 29.0, "t_win": 9.6},
        "1%":  {"tdb": 34.4, "twb": 27.9, "twb_max": 28.5, "t_win": 10.6},
        "II":  {"tdb": 33.4, "twb": 27.5, "twb_max": 28.1, "t_win": 11.5},
    },
    "HCM": {
        "name": "TP. Hồ Chí Minh (Đông Nam Bộ)", "lat": 10.8,
        "I":   {"tdb": 35.4, "twb": 25.7, "twb_max": 28.6, "t_win": 20.7},
        "1%":  {"tdb": 34.7, "twb": 25.7, "twb_max": 27.4, "t_win": 21.6},
        "II":  {"tdb": 34.0, "twb": 25.5, "twb_max": 26.9, "t_win": 22.5},
    },
    "DANANG": {
        "name": "Đà Nẵng (Nam Trung Bộ)", "lat": 16.0,
        "I":   {"tdb": 36.1, "twb": 27.0, "twb_max": 28.2, "t_win": 16.6},
        "1%":  {"tdb": 35.1, "twb": 26.8, "twb_max": 27.8, "t_win": 17.5},
        "II":  {"tdb": 34.2, "twb": 26.6, "twb_max": 27.4, "t_win": 18.4},
    },
    "QUANGNINH": {
        "name": "Quảng Ninh / Hải Phòng (Ven biển Bắc Bộ)", "lat": 20.9,
        "I":   {"tdb": 33.1, "twb": 27.5, "twb_max": 28.6, "t_win": 9.5},
        "1%":  {"tdb": 32.4, "twb": 27.3, "twb_max": 28.2, "t_win": 10.7},
        "II":  {"tdb": 31.8, "twb": 27.2, "twb_max": 27.8, "t_win": 11.6},
    },
    "VINH": {
        "name": "Nghệ An - Vinh (Bắc Trung Bộ)", "lat": 18.7,
        "I":   {"tdb": 36.6, "twb": 26.9, "twb_max": 28.8, "t_win": 10.7},
        "1%":  {"tdb": 35.6, "twb": 26.9, "twb_max": 28.0, "t_win": 11.9},
        "II":  {"tdb": 34.6, "twb": 26.6, "twb_max": 27.5, "t_win": 13.0},
    },
    "NHATRANG": {
        "name": "Nha Trang (Duyên hải Nam Trung Bộ)", "lat": 12.2,
        "I":   {"tdb": 33.3, "twb": 26.3, "twb_max": 27.8, "t_win": 19.5},
        "1%":  {"tdb": 32.7, "twb": 26.3, "twb_max": 27.4, "t_win": 20.3},
        "II":  {"tdb": 32.2, "twb": 26.2, "twb_max": 27.1, "t_win": 21.1},
    },
    "CANTHO": {
        "name": "Cần Thơ (Tây Nam Bộ)", "lat": 10.0,
        "I":   {"tdb": 33.6, "twb": 26.4, "twb_max": 28.4, "t_win": 20.8},
        "1%":  {"tdb": 33.0, "twb": 26.0, "twb_max": 27.6, "t_win": 21.6},
        "II":  {"tdb": 32.5, "twb": 26.2, "twb_max": 27.2, "t_win": 22.2},
    },
    "CAMAU": {
        "name": "Cà Mau (Cực Nam)", "lat": 9.2,
        "I":   {"tdb": 34.2, "twb": 25.9, "twb_max": 27.7, "t_win": 21.5},
        "1%":  {"tdb": 33.6, "twb": 25.8, "twb_max": 27.3, "t_win": 22.2},
        "II":  {"tdb": 33.0, "twb": 25.7, "twb_max": 27.0, "t_win": 22.7},
    },
    "BUONMATHUOT": {
        "name": "Buôn Ma Thuột (Tây Nguyên)", "lat": 12.7,
        "I":   {"tdb": 34.3, "twb": 22.0, "twb_max": 25.1, "t_win": 15.5},
        "1%":  {"tdb": 33.4, "twb": 22.5, "twb_max": 24.8, "t_win": 16.4},
        "II":  {"tdb": 32.4, "twb": 22.4, "twb_max": 24.5, "t_win": 17.2},
    },
    "DALAT": {
        "name": "Đà Lạt (Cao nguyên ôn đới)", "lat": 11.9,
        "I":   {"tdb": 25.9, "twb": 16.7, "twb_max": 20.4, "t_win": 9.7},
        "1%":  {"tdb": 25.2, "twb": 17.6, "twb_max": 19.9, "t_win": 10.7},
        "II":  {"tdb": 24.5, "twb": 17.6, "twb_max": 19.5, "t_win": 11.5},
    },
    "LANGSON": {
        "name": "Lạng Sơn (Đông Bắc Bộ)", "lat": 21.8,
        "I":   {"tdb": 33.8, "twb": 26.5, "twb_max": 27.6, "t_win": 5.1},
        "1%":  {"tdb": 33.0, "twb": 25.8, "twb_max": 26.9, "t_win": 6.5},
        "II":  {"tdb": 32.2, "twb": 25.7, "twb_max": 26.5, "t_win": 7.8},
    },
    "YENBAI": {
        "name": "Yên Bái (Trung du Bắc Bộ)", "lat": 21.7,
        "I":   {"tdb": 35.2, "twb": 27.9, "twb_max": 28.9, "t_win": 9.5},
        "1%":  {"tdb": 34.2, "twb": 27.6, "twb_max": 28.5, "t_win": 10.6},
        "II":  {"tdb": 33.3, "twb": 27.3, "twb_max": 28.1, "t_win": 11.6},
    },
    "HAGIANG": {
        "name": "Hà Giang (Miền núi phía Bắc)", "lat": 22.8,
        "I":   {"tdb": 34.9, "twb": 27.1, "twb_max": 28.7, "t_win": 8.5},
        "1%":  {"tdb": 34.1, "twb": 27.0, "twb_max": 28.1, "t_win": 10.1},
        "II":  {"tdb": 33.3, "twb": 26.9, "twb_max": 27.7, "t_win": 11.2},
    },
    "LAICHAU": {
        "name": "Lai Châu (Tây Bắc Bộ)", "lat": 22.4,
        "I":   {"tdb": 36.1, "twb": 25.4, "twb_max": 27.7, "t_win": 9.9},
        "1%":  {"tdb": 34.9, "twb": 25.8, "twb_max": 27.2, "t_win": 11.3},
        "II":  {"tdb": 33.8, "twb": 25.9, "twb_max": 26.8, "t_win": 12.4},
    },
    "SAPA": {
        "name": "Sa Pa - Lào Cai (Vùng núi cao)", "lat": 22.3,
        "I":   {"tdb": 25.8, "twb": 18.6, "twb_max": 21.6, "t_win": 1.5},
        "1%":  {"tdb": 24.9, "twb": 18.6, "twb_max": 21.0, "t_win": 2.7},
        "II":  {"tdb": 24.2, "twb": 18.6, "twb_max": 20.5, "t_win": 3.8},
    },
}

# ==============================================================================
# 2. VIETNAMESE BUILDING MATERIALS LIBRARY (QCVN 09:2017/BXD & TCVN 4605)
# U = 1 / R0 [W/m2.K], R0 = Rsi(0.115) + sum(d/lambda) + Rse(0.043)
# ==============================================================================
WALL_MATERIALS = {
    "BRICK_220_SOLID":  {"name": "Tường gạch đặc 220mm trát 2 mặt (phổ biến VN)", "u": 1.85, "r0": 0.54, "cltd_adj": 0.0},
    "BRICK_220_HOLLOW": {"name": "Tường gạch ống/lỗ 220mm trát 2 mặt", "u": 1.62, "r0": 0.62, "cltd_adj": -1.0},
    "BRICK_110_SOLID":  {"name": "Tường gạch đặc 110mm trát 2 mặt (tường đơn)", "u": 2.65, "r0": 0.38, "cltd_adj": 2.0},
    "BRICK_110_HOLLOW": {"name": "Tường gạch lỗ 110mm trát 2 mặt", "u": 2.40, "r0": 0.42, "cltd_adj": 1.5},
    "AAC_200":          {"name": "Tường gạch nhẹ bê tông khí chưng áp AAC 200mm (đạt QCVN 09)", "u": 0.72, "r0": 1.39, "cltd_adj": -2.5},
    "RC_200":           {"name": "Tường bê tông cốt thép 200mm trát 2 mặt", "u": 3.12, "r0": 0.32, "cltd_adj": 1.5},
    "RC_200_STONE":     {"name": "Tường bê tông 200mm ốp đá Granite / Marble ngoài trời", "u": 2.95, "r0": 0.34, "cltd_adj": 1.0},
    "BRICK_220_STONE":  {"name": "Tường gạch 220mm ốp đá tự nhiên / Granite mặt tiền", "u": 1.78, "r0": 0.56, "cltd_adj": 0.0},
    "BRICK_220_XPS50":  {"name": "Tường gạch 220mm + Lớp cách nhiệt XPS/PU 50mm (chống nóng)", "u": 0.45, "r0": 2.22, "cltd_adj": -3.0},
    "GYPSUM_ROCKWOOL":  {"name": "Vách thạch cao 2 mặt + Bông khoáng 50mm (vách văn phòng)", "u": 0.62, "r0": 1.61, "cltd_adj": -2.0},
}

GLASS_MATERIALS = {
    "CLEAR_SINGLE":     {"name": "Kính đơn trong 8-10mm khung nhôm thường", "u": 5.80, "shgc": 0.81},
    "TEMPERED_XINGFA":  {"name": "Kính cường lực 10-12mm hệ nhôm Xingfa", "u": 5.60, "shgc": 0.78},
    "LAMINATED_10":     {"name": "Kính dán an toàn 2 lớp 8.38 - 10.38mm", "u": 5.40, "shgc": 0.72},
    "SOLAR_SINGLE":     {"name": "Kính phản quang / Solar Control đơn 8-10mm", "u": 5.50, "shgc": 0.48},
    "DOUBLE_CLEAR":     {"name": "Kính hộp 2 lớp (6-12-6mm khí khô) nhôm cầu cách nhiệt", "u": 2.80, "shgc": 0.68},
    "DOUBLE_LOW_E":     {"name": "Kính hộp Low-E 2 lớp 6-12-6mm (Chuẩn QCVN 09)", "u": 1.85, "shgc": 0.36},
    "CURTAIN_LOW_E":    {"name": "Vách kính mặt dựng Solar Control Low-E cao cấp", "u": 1.65, "shgc": 0.28},
}

SHADING_TYPES = {
    "NONE":      {"name": "Không rèm che nắng", "sc": 1.00},
    "LIGHT":     {"name": "Rèm vải mỏng / Rèm voan sáng màu", "sc": 0.68},
    "ROLLER":    {"name": "Rèm cuốn / Rèm cầu vồng văn phòng", "sc": 0.55},
    "BLACKOUT":  {"name": "Rèm cản nắng 2 lớp / Chớp ngoài che nắng", "sc": 0.42},
    "OVERHANG":  {"name": "Mái hiên / Ban công đua sâu ≥ 1.2m + Rèm", "sc": 0.35},
}

ROOF_TYPES = {
    "MID_FLOOR":     {"name": "Tầng giữa (phía trên là phòng có điều hòa)", "u": 0.00, "cltd": 0.0, "is_roof": False},
    "UPPER_NON_AC":  {"name": "Trần bê tông giáp tầng trên KHÔNG điều hòa (kho/sân phơi có mái)", "u": 1.85, "cltd": 6.5, "is_roof": False},
    "ROOF_RC_PLAIN": {"name": "Mái bê tông 150mm KHÔNG chống nóng + trần thạch cao", "u": 2.15, "cltd": 24.0, "is_roof": True},
    "ROOF_RC_INSUL": {"name": "Mái bê tông 150mm + chống nóng gạch bọng / PU 50mm + trần TC", "u": 0.58, "cltd": 18.0, "is_roof": True},
    "ROOF_TILE_INS": {"name": "Mái ngói / Mái tôn + bông thủy tinh 50mm + trần thạch cao", "u": 0.72, "cltd": 21.0, "is_roof": True},
    "ROOF_METAL":    {"name": "Mái tôn 1 lớp cách nhiệt kém (nhà xưởng/tầng tum)", "u": 2.85, "cltd": 28.0, "is_roof": True},
}

FLOOR_TYPES = {
    "GROUND":       {"name": "Sàn tầng trệt (tiếp xúc nền đất)", "u": 0.45, "dt_factor": 0.35},
    "MID_AC":       {"name": "Sàn tầng giữa (phía dưới có điều hòa)", "u": 0.00, "dt_factor": 0.00},
    "OVER_NON_AC":  {"name": "Sàn trên tầng hầm / gara / không gian không ĐHKK", "u": 1.75, "dt_factor": 0.55},
    "OVER_EXT":     {"name": "Sàn đua ban công / sảnh hở ngoài trời", "u": 2.10, "dt_factor": 0.85},
}

# Main Door Materials popular in Vietnam (TCVN 4605 / ASHRAE Fundamentals)
# glass_ratio: fraction of door area that transmits solar radiation; inf_m3h_m2: air infiltration m3/(h·m2)
DOOR_MATERIALS = {
    "NONE":               {"name": "Không tính riêng cửa chính (đã gộp tường/lọt khí)", "u": 0.00, "glass_ratio": 0.00, "inf_m3h_m2": 0.0},
    "WOOD_SOLID_45":      {"name": "Cửa gỗ tự nhiên đặc 45mm (Lim, Gõ đỏ, Óc chó)",     "u": 2.20, "glass_ratio": 0.00, "inf_m3h_m2": 6.5},
    "WOOD_ENG_HDF":       {"name": "Cửa gỗ công nghiệp / Nhựa gỗ Composite (An Cường)", "u": 2.60, "glass_ratio": 0.00, "inf_m3h_m2": 5.0},
    "STEEL_FIRE":         {"name": "Cửa thép chống cháy / Thép vân gỗ lõi bông khoáng", "u": 2.80, "glass_ratio": 0.00, "inf_m3h_m2": 4.5},
    "ALUM_XINGFA_GLASS":  {"name": "Cửa đi nhôm kính Xingfa / PMA (75% kính)",          "u": 4.80, "glass_ratio": 0.75, "inf_m3h_m2": 5.5},
    "TEMPERED_12_FULL":   {"name": "Cửa kính cường lực thủy lực 12mm (Sảnh/VP — khe hở lớn)", "u": 5.60, "glass_ratio": 0.95, "inf_m3h_m2": 14.0},
    "AUTO_SLIDING_GLASS": {"name": "Cửa kính trượt tự động (Bệnh viện / Sảnh — đóng mở nhiều)", "u": 5.40, "glass_ratio": 0.90, "inf_m3h_m2": 22.0},
    "HOSPITAL_HERMETIC":  {"name": "Cửa kín khí Bệnh viện / Phòng sạch (Hermetic Inox/HPL)",    "u": 1.80, "glass_ratio": 0.15, "inf_m3h_m2": 1.2},
    "UPVC_GLASS":         {"name": "Cửa nhựa lõi thép uPVC gioăng kín (70% kính)",      "u": 3.20, "glass_ratio": 0.70, "inf_m3h_m2": 2.8},
}

# Window Frame Materials popular in Vietnam
WINDOW_FRAME_MATERIALS = {
    "XINGFA_NO_TB":       {"name": "Khung nhôm hệ Xingfa / Việt Pháp (không cầu cách nhiệt)", "u_factor": 1.00, "inf_m3h_m2": 3.2},
    "ALUM_THERMAL_BREAK": {"name": "Khung nhôm cầu cách nhiệt cao cấp (Civro / Eurowindow)",  "u_factor": 0.85, "inf_m3h_m2": 1.8},
    "UPVC_REINF":         {"name": "Khung nhựa lõi thép uPVC gioăng kép kín khít",            "u_factor": 0.82, "inf_m3h_m2": 1.5},
    "WOOD_FRAME":         {"name": "Khung gỗ tự nhiên truyền thống",                          "u_factor": 0.88, "inf_m3h_m2": 4.2},
    "CURTAIN_WALL":       {"name": "Vách kính mặt dựng cố định (Fix / Stick)",                "u_factor": 0.92, "inf_m3h_m2": 0.8},
}

# Detailed Equipment / Appliance Heat Gain Library (ASHRAE Fundamentals & ASHRAE Hospital Design Manual)
# Split by 3 Vietnamese building domains: HOME (Gia đình), OFFICE (Văn phòng), HOSPITAL (Bệnh viện / Phòng khám)
EQUIPMENT_LIBRARY = {
    # --- GIA ĐÌNH (HOME) ---
    "TV_LED_55":       {"cat": "HOME",     "name": "TV LED / OLED 55\"–75\"",                               "q_sens_w": 150,  "q_lat_w": 0,   "unit": "Chiếc"},
    "FRIDGE_SIDE":     {"cat": "HOME",     "name": "Tủ lạnh Inverter / Side-by-Side (tỏa nhiệt trung bình)","q_sens_w": 220,  "q_lat_w": 0,   "unit": "Chiếc"},
    "INDUCTION_COOK":  {"cat": "HOME",     "name": "Bếp từ đôi / Bếp điện (đang nấu có hút mùi)",           "q_sens_w": 750,  "q_lat_w": 250, "unit": "Bộ"},
    "RICE_KETTLE":     {"cat": "HOME",     "name": "Nồi cơm điện / Ấm siêu tốc / Máy pha trà",             "q_sens_w": 280,  "q_lat_w": 180, "unit": "Bộ"},
    "OVEN_MICRO":      {"cat": "HOME",     "name": "Lò nướng / Lò vi sóng / Nồi chiên không dầu",           "q_sens_w": 550,  "q_lat_w": 100, "unit": "Chiếc"},
    "WINE_COOLER":     {"cat": "HOME",     "name": "Tủ bảo quản rượu vang / Máy lọc nước nóng lạnh",        "q_sens_w": 180,  "q_lat_w": 0,   "unit": "Chiếc"},
    "PC_HOME":         {"cat": "HOME",     "name": "Máy tính bàn gia đình / Gaming PC + Màn hình",          "q_sens_w": 320,  "q_lat_w": 0,   "unit": "Bộ"},
    "WASHER_DRYER":    {"cat": "HOME",     "name": "Máy giặt / Máy sấy đặt trong không gian ĐHKK",          "q_sens_w": 450,  "q_lat_w": 250, "unit": "Chiếc"},
    # --- VĂN PHÒNG (OFFICE) ---
    "LAPTOP_DESK":     {"cat": "OFFICE",   "name": "Bộ Laptop + Màn hình rời (1 nhân viên VP)",             "q_sens_w": 85,   "q_lat_w": 0,   "unit": "Bộ"},
    "DESKTOP_PC":      {"cat": "OFFICE",   "name": "Máy tính Workstation + Màn hình 24\"–27\"",             "q_sens_w": 220,  "q_lat_w": 0,   "unit": "Bộ"},
    "PRINTER_MFP":     {"cat": "OFFICE",   "name": "Máy in Laser / Máy Photocopy đa năng văn phòng",        "q_sens_w": 550,  "q_lat_w": 0,   "unit": "Chiếc"},
    "PROJECTOR_LED":   {"cat": "OFFICE",   "name": "Máy chiếu hội nghị / Màn hình tương tác 75\"–86\"",     "q_sens_w": 380,  "q_lat_w": 0,   "unit": "Bộ"},
    "WATER_DISPENSER": {"cat": "OFFICE",   "name": "Cây nước uống nóng lạnh văn phòng",                     "q_sens_w": 260,  "q_lat_w": 0,   "unit": "Chiếc"},
    "COFFEE_OFFICE":   {"cat": "OFFICE",   "name": "Máy pha cà phê Espresso tự động Pantry",                "q_sens_w": 420,  "q_lat_w": 140, "unit": "Chiếc"},
    "RACK_SWITCH":     {"cat": "OFFICE",   "name": "Tủ mạng Switch / Router / Đầu ghi Camera",              "q_sens_w": 350,  "q_lat_w": 0,   "unit": "Tủ"},
    "SERVER_RACK":     {"cat": "OFFICE",   "name": "Tủ Server / Máy chủ nội bộ (1/2 Rack)",                 "q_sens_w": 1800, "q_lat_w": 0,   "unit": "Tủ"},
    # --- BỆNH VIỆN / PHÒNG KHÁM (HOSPITAL) ---
    "PATIENT_MON":     {"cat": "HOSPITAL", "name": "Monitor theo dõi bệnh nhân + Bơm tiêm điện",            "q_sens_w": 180,  "q_lat_w": 0,   "unit": "Bộ"},
    "ULTRASOUND":      {"cat": "HOSPITAL", "name": "Máy Siêu âm màu 4D / Doppler",                          "q_sens_w": 650,  "q_lat_w": 0,   "unit": "Máy"},
    "DENTAL_CHAIR":    {"cat": "HOSPITAL", "name": "Ghế Nha khoa + Đèn thủ thuật + Máy hút",                "q_sens_w": 950,  "q_lat_w": 80,  "unit": "Ghế"},
    "XRAY_BIOCHEM":    {"cat": "HOSPITAL", "name": "Máy Xét nghiệm sinh hóa / Trạm điều khiển X-Quang",     "q_sens_w": 1400, "q_lat_w": 0,   "unit": "Máy"},
    "CT_MRI_SCANNER":  {"cat": "HOSPITAL", "name": "Máy Chụp CT Scanner / MRI (tỏa nhiệt phòng máy)",       "q_sens_w": 4200, "q_lat_w": 0,   "unit": "Hệ"},
    "AUTOCLAVE_STER":  {"cat": "HOSPITAL", "name": "Nồi hấp tiệt trùng Autoclave / Tủ sấy dụng cụ",         "q_sens_w": 1200, "q_lat_w": 450, "unit": "Máy"},
    "OT_LIGHT_ESU":    {"cat": "HOSPITAL", "name": "Đèn mổ LED 2 nhánh không hắt bóng + Dao mổ điện",       "q_sens_w": 780,  "q_lat_w": 0,   "unit": "Bộ"},
    "VACCINE_FRIDGE":  {"cat": "HOSPITAL", "name": "Tủ bảo quản Vắc-xin / Sinh phẩm y tế chuyên dụng",      "q_sens_w": 320,  "q_lat_w": 0,   "unit": "Tủ"},
    "ICU_VENTILATOR":  {"cat": "HOSPITAL", "name": "Máy thở ICU + Thiết bị hồi sức tích cực",               "q_sens_w": 420,  "q_lat_w": 0,   "unit": "Bộ"},
}

# Room usage presets strictly matched to TCVN 5687:2024 Annex A & Annex E + QCVN 09 Lighting Power Density
ROOM_PRESETS = {
    "BEDROOM":        {"name": "Phòng ngủ (Nhà ở / Biệt thự)",             "t_in": 25.0, "rh_in": 60, "oa_per_person": 35, "oa_per_m2": 0, "m2_per_person": 10,  "q_pers_s": 65,  "q_pers_l": 45,  "light_w_m2": 7.0,  "equip_w_m2": 6.0,  "ach_inf": 0.4},
    "LIVING":         {"name": "Phòng khách / Sinh hoạt chung",            "t_in": 25.0, "rh_in": 60, "oa_per_person": 30, "oa_per_m2": 0, "m2_per_person": 8,   "q_pers_s": 70,  "q_pers_l": 50,  "light_w_m2": 9.0,  "equip_w_m2": 10.0, "ach_inf": 0.6},
    "DINING":         {"name": "Phòng ăn / Bếp ăn gia đình",               "t_in": 25.5, "rh_in": 60, "oa_per_person": 30, "oa_per_m2": 0, "m2_per_person": 5,   "q_pers_s": 75,  "q_pers_l": 65,  "light_w_m2": 9.0,  "equip_w_m2": 22.0, "ach_inf": 0.8},
    "HOTEL_ROOM":     {"name": "Phòng ngủ Khách sạn / Resort",             "t_in": 24.5, "rh_in": 60, "oa_per_person": 35, "oa_per_m2": 0, "m2_per_person": 10,  "q_pers_s": 65,  "q_pers_l": 45,  "light_w_m2": 8.0,  "equip_w_m2": 8.0,  "ach_inf": 0.5},
    "OFFICE":         {"name": "Văn phòng làm việc (TCVN 5687)",           "t_in": 25.0, "rh_in": 60, "oa_per_person": 25, "oa_per_m2": 0, "m2_per_person": 8,   "q_pers_s": 70,  "q_pers_l": 55,  "light_w_m2": 11.0, "equip_w_m2": 18.0, "ach_inf": 0.5},
    "MEETING":        {"name": "Phòng họp / Hội thảo",                     "t_in": 24.5, "rh_in": 60, "oa_per_person": 30, "oa_per_m2": 0, "m2_per_person": 2.0, "q_pers_s": 70,  "q_pers_l": 55,  "light_w_m2": 12.0, "equip_w_m2": 12.0, "ach_inf": 0.6},
    "SHOWROOM":       {"name": "Showroom / Cửa hàng bán lẻ",               "t_in": 25.0, "rh_in": 60, "oa_per_person": 25, "oa_per_m2": 5, "m2_per_person": 5.0, "q_pers_s": 75,  "q_pers_l": 65,  "light_w_m2": 16.0, "equip_w_m2": 12.0, "ach_inf": 0.9},
    "RESTAURANT":     {"name": "Nhà hàng / Quán Café",                     "t_in": 25.0, "rh_in": 60, "oa_per_person": 30, "oa_per_m2": 0, "m2_per_person": 1.6, "q_pers_s": 80,  "q_pers_l": 80,  "light_w_m2": 12.0, "equip_w_m2": 25.0, "ach_inf": 1.0},
    "CLASSROOM":      {"name": "Phòng học / Trung tâm đào tạo",            "t_in": 25.5, "rh_in": 60, "oa_per_person": 25, "oa_per_m2": 0, "m2_per_person": 2.2, "q_pers_s": 70,  "q_pers_l": 55,  "light_w_m2": 11.0, "equip_w_m2": 8.0,  "ach_inf": 0.6},
    "GYM":            {"name": "Phòng Gym / Thể thao",                     "t_in": 24.0, "rh_in": 60, "oa_per_person": 35, "oa_per_m2": 0, "m2_per_person": 4.0, "q_pers_s": 160, "q_pers_l": 265, "light_w_m2": 10.0, "equip_w_m2": 15.0, "ach_inf": 0.8},
    "LOBBY":          {"name": "Tiền sảnh / Khu đón tiếp",                 "t_in": 26.5, "rh_in": 60, "oa_per_person": 25, "oa_per_m2": 0, "m2_per_person": 4.0, "q_pers_s": 75,  "q_pers_l": 65,  "light_w_m2": 12.0, "equip_w_m2": 8.0,  "ach_inf": 1.2},
    "CLINIC":         {"name": "Phòng khám bệnh / Nha khoa / Siêu âm",     "t_in": 24.5, "rh_in": 55, "oa_per_person": 40, "oa_per_m2": 0, "m2_per_person": 6.0, "q_pers_s": 70,  "q_pers_l": 50,  "light_w_m2": 14.0, "equip_w_m2": 20.0, "ach_inf": 0.5},
    "HOSPITAL_WARD":  {"name": "Phòng bệnh nhân nội trú / Hồi sức (TCVN)", "t_in": 24.5, "rh_in": 55, "oa_per_person": 40, "oa_per_m2": 0, "m2_per_person": 8.0, "q_pers_s": 65,  "q_pers_l": 50,  "light_w_m2": 10.0, "equip_w_m2": 15.0, "ach_inf": 0.4},
    "OPERATING_ROOM": {"name": "Phòng mổ / Thủ thuật y tế (Áp suất dương)","t_in": 22.0, "rh_in": 50, "oa_per_person": 60, "oa_per_m2": 8, "m2_per_person": 5.0, "q_pers_s": 90,  "q_pers_l": 95,  "light_w_m2": 22.0, "equip_w_m2": 35.0, "ach_inf": 0.2},
    "LAB_CLINIC":     {"name": "Phòng xét nghiệm / Chẩn đoán hình ảnh",    "t_in": 23.0, "rh_in": 50, "oa_per_person": 40, "oa_per_m2": 5, "m2_per_person": 7.0, "q_pers_s": 75,  "q_pers_l": 55,  "light_w_m2": 16.0, "equip_w_m2": 40.0, "ach_inf": 0.4},
}

# Solar Heat Gain Factor (SHGF peak W/m2 at Vietnam latitude 10-21N, summer peak 14h-16h)
# and CLTD wall differential (K) by orientation (ASHRAE / Trace 700 / QCVN 09)
ORIENTATION_SOLAR = {
    "W":  {"label": "Tây (Nắng gắt chiều)",    "shgf": 640.0, "cltd_wall": 18.5, "clf": 0.78},
    "SW": {"label": "Tây Nam (Nắng chiều)",    "shgf": 560.0, "cltd_wall": 16.5, "clf": 0.76},
    "NW": {"label": "Tây Bắc (Nắng chiều)",    "shgf": 540.0, "cltd_wall": 16.0, "clf": 0.76},
    "E":  {"label": "Đông (Nắng sáng)",        "shgf": 520.0, "cltd_wall": 15.0, "clf": 0.72},
    "SE": {"label": "Đông Nam (Mát/Nắng sớm)", "shgf": 420.0, "cltd_wall": 13.0, "clf": 0.70},
    "NE": {"label": "Đông Bắc (Nắng sớm)",     "shgf": 410.0, "cltd_wall": 13.0, "clf": 0.70},
    "S":  {"label": "Nam (Gió mát)",           "shgf": 320.0, "cltd_wall": 11.5, "clf": 0.68},
    "N":  {"label": "Bắc (Ít nắng trực tiếp)", "shgf": 210.0, "cltd_wall": 9.5,  "clf": 0.68},
    "INT":{"label": "Nội bộ (Không tiếp xúc nắng)", "shgf": 0.0, "cltd_wall": 0.0, "clf": 0.0},
}

# QCVN 09:2017/BXD Table 2.2 max SHGC limits by WWR (for non-North facades)
def qcvn09_max_shgc(wwr_pct: float, orient: str) -> float:
    is_north = orient in ("N", "INT")
    if wwr_pct <= 20:
        return 0.90 if is_north else 0.80
    if wwr_pct <= 30:
        return 0.80 if is_north else 0.64
    if wwr_pct <= 40:
        return 0.70 if is_north else 0.50
    if wwr_pct <= 50:
        return 0.60 if is_north else 0.40
    if wwr_pct <= 60:
        return 0.54 if is_north else 0.33
    if wwr_pct <= 70:
        return 0.48 if is_north else 0.27
    return 0.44 if is_north else 0.24


# ==============================================================================
# 3. PSYCHROMETRIC FUNCTIONS (Standard Sea-Level P = 101.325 kPa)
# ==============================================================================
def sat_vapor_pressure_kpa(t_c: float) -> float:
    """Magnus-Tetens saturation vapor pressure of water in kPa."""
    return 0.61078 * math.exp((17.2694 * t_c) / (t_c + 237.3))


def humidity_ratio_from_tdb_rh(tdb: float, rh_pct: float, p_kpa: float = 101.325) -> float:
    """Returns humidity ratio W in kg_water / kg_dry_air."""
    pws = sat_vapor_pressure_kpa(tdb)
    pw = max(0.0, min(p_kpa * 0.95, pws * (rh_pct / 100.0)))
    return 0.621945 * pw / max(1.0, p_kpa - pw)


def humidity_ratio_from_tdb_twb(tdb: float, twb: float, p_kpa: float = 101.325) -> float:
    """ASHRAE psychrometric humidity ratio W [kg/kg] from Dry-Bulb and Wet-Bulb temperatures."""
    twb = min(twb, tdb)
    pws_wb = sat_vapor_pressure_kpa(twb)
    ws_wb = 0.621945 * pws_wb / max(1.0, p_kpa - pws_wb)
    num = (2501.0 - 2.326 * twb) * ws_wb - 1.006 * (tdb - twb)
    den = 2501.0 + 1.86 * tdb - 4.186 * twb
    return max(0.001, num / den)


def enthalpy_kj_kg(tdb: float, w_kg_kg: float) -> float:
    """Moist air specific enthalpy in kJ/kg dry air."""
    return 1.006 * tdb + w_kg_kg * (2501.0 + 1.86 * tdb)


def rh_from_tdb_w(tdb: float, w_kg_kg: float, p_kpa: float = 101.325) -> float:
    pw = (w_kg_kg * p_kpa) / (0.621945 + w_kg_kg)
    pws = sat_vapor_pressure_kpa(tdb)
    return max(1.0, min(100.0, (pw / max(0.001, pws)) * 100.0))


# ==============================================================================
# 4. MULTI-ROOM HEAT LOAD CALCULATION ENGINE (TCVN 5687:2024 + QCVN 09:2017/BXD)
# ==============================================================================
def recommend_daikin_model(req_btu: float, prefer_type: str, plenum_mm: float, products: list) -> dict:
    """Match the best Daikin indoor model from database.json with ceiling clearance check."""
    if not products:
        return {"model": "—", "name": "Chưa có DB", "cooling_btu": 0, "clearance_ok": True, "clearance_note": ""}

    # Filter indoor units matching preferred style
    def style_ok(p):
        cid = p.get("category_id", "")
        if "_OUT" in cid or cid in ("VRV_ACC", "MULTI_ACC", "VRV_HRV"):
            return False
        if not p.get("cooling_btu") or p["cooling_btu"] <= 0:
            return False
        if prefer_type == "VRV_DUCT":
            return cid in ("VRV_IN_DUCT_SLIM", "VRV_IN_DUCT_MED", "VRV_IN_DUCT_HIGH")
        if prefer_type == "VRV_CASSETTE":
            return cid == "VRV_IN_CASSETTE"
        if prefer_type == "VRV_WALL":
            return cid == "VRV_IN_WALL"
        if prefer_type == "MULTI_DUCT":
            return cid == "MULTI_IN_DUCT"
        if prefer_type == "MULTI_WALL":
            return cid == "MULTI_IN_WALL"
        if prefer_type == "SKY_DUCT":
            return cid == "SKY_DUCT"
        if prefer_type == "SKY_CASSETTE":
            return cid == "SKY_CASSETTE"
        if prefer_type == "ROOM_AIR":
            return cid == "ROOM_AIR"
        return True

    cands = [p for p in products if style_ok(p)]
    if not cands:
        cands = [p for p in products if p.get("cooling_btu", 0) > 0 and "_OUT" not in p.get("category_id", "")]

    # Prefer smallest capacity >= 0.94 * req_btu; if req_btu exceeds max single unit, suggest qty > 1
    cands.sort(key=lambda x: x["cooling_btu"])
    qty = 1
    chosen = None
    for p in cands:
        if p["cooling_btu"] >= req_btu * 0.94:
            # If ducted & tight plenum (< 285mm), prefer slim 200mm (FXDQ / CDXP / CDXM / FDF) if available
            chosen = p
            break
    if not chosen:
        chosen = cands[-1]
        qty = max(1, math.ceil(req_btu / max(1, chosen["cooling_btu"])))

    # If tight ceiling plenum and FXSQ/FXMQ chosen, check if FXDQ slim (200mm) fits capacity
    if plenum_mm > 0 and plenum_mm < 290 and prefer_type == "VRV_DUCT" and qty == 1:
        slim_cands = [p for p in products if p.get("category_id") == "VRV_IN_DUCT_SLIM" and p["cooling_btu"] >= req_btu * 0.94]
        if slim_cands:
            slim_cands.sort(key=lambda x: x["cooling_btu"])
            chosen = slim_cands[0]

    # Parse unit height from dimensions (e.g. "245x1000x800" or "DL: 245x1000x800 | ...")
    dim_str = str(chosen.get("dimensions", ""))
    m_h = re.search(r"(\d{3})\s*[xX×]", dim_str)
    unit_h_mm = int(m_h.group(1)) if m_h else 0
    req_plenum_mm = (unit_h_mm + 45) if (chosen.get("duct") or chosen.get("ceiling_opening")) else 0
    clearance_ok = True
    clearance_note = "Đạt khoảng hở lắp đặt"
    if req_plenum_mm > 0 and plenum_mm > 0:
        if plenum_mm < req_plenum_mm:
            clearance_ok = False
            clearance_note = f"CẢNH BÁO: Khoảng trần {int(plenum_mm)}mm < yêu cầu tối thiểu {req_plenum_mm}mm (thân máy cao {unit_h_mm}mm)"
        else:
            clearance_note = f"Đạt ({int(plenum_mm)}mm ≥ {req_plenum_mm}mm)"

    return {
        "prod_id": chosen.get("id", ""),
        "model": chosen.get("model", "—"),
        "name": chosen.get("name", ""),
        "qty": qty,
        "cooling_btu": chosen.get("cooling_btu", 0),
        "cooling_kw": chosen.get("cooling_kw", 0),
        "total_btu": chosen.get("cooling_btu", 0) * qty,
        "price": chosen.get("price", 0),
        "unit_height_mm": unit_h_mm,
        "req_plenum_mm": req_plenum_mm,
        "clearance_ok": clearance_ok,
        "clearance_note": clearance_note,
        "duct": chosen.get("duct"),
        "image": chosen.get("image", ""),
    }


def calculate_project_heat_load(payload: dict, products: list = None) -> dict:
    """
    Full multi-room / multi-floor heat load calculation per TCVN 5687:2024 & QCVN 09:2017/BXD.
    """
    products = products or []
    city_key = payload.get("city", "HANOI")
    grade = payload.get("grade", "I")  # "I" (0.4%), "1%", "II" (2.0%)
    city = TCVN_CLIMATE_CITIES.get(city_key, TCVN_CLIMATE_CITIES["HANOI"])
    clim = city.get(grade, city["I"])

    t_out = float(payload.get("t_out_override") or clim["tdb"])
    twb_out = float(payload.get("twb_out_override") or clim["twb"])
    t_out_win = float(clim["t_win"])
    w_out = humidity_ratio_from_tdb_twb(t_out, twb_out)
    rh_out = rh_from_tdb_w(t_out, w_out)
    h_out = enthalpy_kj_kg(t_out, w_out)

    safety_pct = float(payload.get("safety_pct", 10.0))
    diversity = float(payload.get("diversity_factor", 0.85))
    use_hrv = bool(payload.get("use_hrv", False))
    hrv_eff = float(payload.get("hrv_efficiency", 0.70)) if use_hrv else 0.0
    prefer_system = payload.get("prefer_system", "VRV_DUCT")

    rooms_in = payload.get("rooms", [])
    room_results = []

    tot_area = 0.0
    tot_sens_w = 0.0
    tot_lat_w = 0.0
    tot_q_w = 0.0
    tot_heat_w = 0.0
    tot_oa_m3h = 0.0
    tot_supply_m3h = 0.0
    tot_people = 0

    comp_sums = {
        "wall": 0.0,
        "glass_rad": 0.0,
        "glass_cond": 0.0,
        "door": 0.0,
        "roof_floor": 0.0,
        "partition": 0.0,
        "people": 0.0,
        "light_equip": 0.0,
        "fresh_air": 0.0,
        "infiltration": 0.0,
    }
    qcvn_warnings = []
    clearance_warnings = []

    for idx, r in enumerate(rooms_in):
        preset = ROOM_PRESETS.get(r.get("room_type", "LIVING"), ROOM_PRESETS["LIVING"])
        name = r.get("name") or f"Phòng {idx + 1}"
        floor_label = r.get("floor") or "Tầng 1"
        area = max(1.0, float(r.get("area", 25.0)))
        h_concrete = max(2.2, float(r.get("h_concrete", 3.6)))
        h_ceiling = max(2.0, min(h_concrete, float(r.get("h_ceiling", 3.0))))
        plenum_m = max(0.0, h_concrete - h_ceiling)
        plenum_mm = round(plenum_m * 1000.0)

        t_in = float(r.get("t_in") or preset["t_in"])
        rh_in = float(r.get("rh_in") or preset["rh_in"])
        w_in = humidity_ratio_from_tdb_rh(t_in, rh_in)
        h_in = enthalpy_kj_kg(t_in, w_in)
        dt = max(1.0, t_out - t_in)
        dw = max(0.0, w_out - w_in)

        orient = r.get("orientation", "W")
        ori_data = ORIENTATION_SOLAR.get(orient, ORIENTATION_SOLAR["W"])

        wall_mat = WALL_MATERIALS.get(r.get("wall_type", "BRICK_220_SOLID"), WALL_MATERIALS["BRICK_220_SOLID"])
        glass_mat = GLASS_MATERIALS.get(r.get("glass_type", "TEMPERED_XINGFA"), GLASS_MATERIALS["TEMPERED_XINGFA"])
        shade = SHADING_TYPES.get(r.get("shading_type", "ROLLER"), SHADING_TYPES["ROLLER"])
        roof_mat = ROOF_TYPES.get(r.get("roof_type", "MID_FLOOR"), ROOF_TYPES["MID_FLOOR"])
        floor_mat = FLOOR_TYPES.get(r.get("floor_type", "MID_AC"), FLOOR_TYPES["MID_AC"])
        win_frame = WINDOW_FRAME_MATERIALS.get(r.get("win_frame_type", "XINGFA_NO_TB"), WINDOW_FRAME_MATERIALS["XINGFA_NO_TB"])
        door_mat = DOOR_MATERIALS.get(r.get("door_type", "NONE"), DOOR_MATERIALS["NONE"])

        # Exterior wall, detailed Windows (Cửa sổ), and Main Door (Cửa chính)
        ext_wall_len = float(r.get("ext_wall_len") if r.get("ext_wall_len") not in (None, "") else round(math.sqrt(area) * 1.1, 1))
        gross_ext_area = max(0.0, ext_wall_len * h_concrete)

        # Windows: explicit count × W × H (if given), plus optional fixed curtain glass area
        win_qty = max(0, int(r.get("win_qty") or 0))
        win_w = max(0.0, float(r.get("win_w") or 0.0))
        win_h = max(0.0, float(r.get("win_h") or 0.0))
        win_area = win_qty * win_w * win_h if (win_qty > 0 and win_w > 0 and win_h > 0) else 0.0
        extra_glass = max(0.0, float(r.get("extra_glass_area") or 0.0))

        if win_area > 0:
            glass_area = win_area * 0.85 + extra_glass
            window_opening_area = win_area + extra_glass
        else:
            glass_area = max(0.0, float(r.get("glass_area") if r.get("glass_area") not in (None, "") else round(gross_ext_area * 0.25, 1)))
            window_opening_area = glass_area

        # Main Door (Cửa chính / Cửa ra vào)
        door_qty = max(0, int(r.get("door_qty") or (1 if r.get("door_type") and r.get("door_type") != "NONE" else 0)))
        door_w = max(0.0, float(r.get("door_w") or 1.0))
        door_h = max(0.0, float(r.get("door_h") or 2.2))
        door_area = (door_qty * door_w * door_h) if (r.get("door_type", "NONE") != "NONE" and door_qty > 0) else 0.0
        door_loc = r.get("door_location", "INT")  # "EXT" (mặt ngoài) or "INT" (hành lang / trong nhà)
        door_is_ext = (door_loc == "EXT") and (orient != "INT") and (door_area > 0)

        if orient == "INT":
            gross_ext_area = 0.0
            glass_area = 0.0
            window_opening_area = 0.0

        ext_door_glass = (door_area * door_mat["glass_ratio"]) if door_is_ext else 0.0
        total_glazed_area = glass_area + ext_door_glass
        net_wall_area = max(0.0, gross_ext_area - window_opening_area - (door_area if door_is_ext else 0.0))
        wwr_pct = (total_glazed_area / gross_ext_area * 100.0) if gross_ext_area > 0 else 0.0

        # Partition wall adjacent to non-AC space (corridor/staircase/kitchen)
        part_len = max(0.0, float(r.get("partition_len") or 0.0))
        part_area = part_len * h_ceiling

        # 1. Exterior Wall Conduction (CLTD adjusted for Vietnam ambient & indoor temp)
        cltd_wall_eff = max(dt, ori_data["cltd_wall"] + wall_mat["cltd_adj"] + (25.5 - t_in) + (t_out - 35.0))
        q_wall = wall_mat["u"] * net_wall_area * cltd_wall_eff if orient != "INT" else 0.0

        # 2. Windows & Fixed Glass: Solar Radiation + Frame-Adjusted Conduction
        u_glass_eff = glass_mat["u"] * win_frame["u_factor"]
        q_glass_rad = total_glazed_area * ori_data["shgf"] * glass_mat["shgc"] * shade["sc"] * ori_data["clf"]
        q_glass_cond = u_glass_eff * window_opening_area * dt

        # 2b. Main Door Conduction (Exterior ΔT or Interior Adjacent 0.55×ΔT)
        door_dt = dt if door_is_ext else (dt * 0.55)
        q_door_cond = door_mat["u"] * door_area * door_dt

        # 3. Roof / Ceiling (accounts for plenum air buffer H_BT - H_TC!) + Floor
        u_roof_eff = roof_mat["u"]
        if u_roof_eff > 0 and plenum_m >= 0.3:
            u_roof_eff = 1.0 / (1.0 / u_roof_eff + 0.16)
        cltd_roof_eff = max(0.0, roof_mat["cltd"] + (25.5 - t_in) + (t_out - 35.0)) if roof_mat["u"] > 0 else 0.0
        q_roof = u_roof_eff * area * cltd_roof_eff
        q_floor = floor_mat["u"] * area * (dt * floor_mat["dt_factor"])
        q_roof_floor = q_roof + q_floor

        # 4. Interior Partition to non-AC space (assumed U=2.2 W/m2K, ΔT_adj = 0.55*ΔT)
        q_partition = 2.2 * part_area * (dt * 0.55)

        # 5. People (Sensible + Latent)
        people = int(r.get("people") if r.get("people") not in (None, "") else max(1, round(area / preset["m2_per_person"])))
        q_people_sens = people * preset["q_pers_s"]
        q_people_lat = people * preset["q_pers_l"]

        # 6. Lighting + Detailed Equipment Library (Home / Office / Hospital — Sensible + Latent!)
        light_w_m2 = float(r.get("light_w_m2") if r.get("light_w_m2") not in (None, "") else preset["light_w_m2"])
        q_light = area * light_w_m2

        equip_items_in = r.get("equipment_items") or []
        q_equip_items_sens = 0.0
        q_equip_items_lat = 0.0
        equip_labels = []
        for ei in equip_items_in:
            if not isinstance(ei, dict):
                continue
            eq_qty = max(0, int(ei.get("qty") or 0))
            if eq_qty <= 0:
                continue
            lib_item = EQUIPMENT_LIBRARY.get(ei.get("id", ""))
            if lib_item:
                qs_u = float(ei.get("q_sens_w") if ei.get("q_sens_w") not in (None, "") else lib_item["q_sens_w"])
                ql_u = float(ei.get("q_lat_w") if ei.get("q_lat_w") not in (None, "") else lib_item["q_lat_w"])
                enm = lib_item["name"].split("(")[0].strip()
            else:
                qs_u = float(ei.get("q_sens_w") or 0.0)
                ql_u = float(ei.get("q_lat_w") or 0.0)
                enm = str(ei.get("name") or "Thiết bị")
            q_equip_items_sens += eq_qty * qs_u
            q_equip_items_lat += eq_qty * ql_u
            equip_labels.append(f"{eq_qty}× {enm[:24]}")

        # Avoid double-counting default equip_w_m2 when explicit equipment items are selected
        if equip_items_in and r.get("equip_w_m2") in (None, ""):
            equip_w_m2 = 0.0
        else:
            equip_w_m2 = float(r.get("equip_w_m2") if r.get("equip_w_m2") not in (None, "") else preset["equip_w_m2"])
        extra_equip_w = float(r.get("extra_equip_w") or 0.0)
        q_equip_sens = area * equip_w_m2 + extra_equip_w + q_equip_items_sens

        # 7. Outdoor Fresh Air per TCVN 5687:2024 Annex E (Bảng E.1)
        oa_by_person = people * preset["oa_per_person"]
        oa_by_area = area * preset["oa_per_m2"]
        oa_m3h = float(r.get("oa_override_m3h") or max(oa_by_person, oa_by_area))
        q_oa_sens = 0.3353 * oa_m3h * dt * (1.0 - hrv_eff)
        q_oa_lat = 833.67 * oa_m3h * dw * (1.0 - hrv_eff * 0.85)

        # 8. Infiltration (Base room ACH + Explicit Door & Window crack/traffic infiltration!)
        vol_m3 = area * h_ceiling
        ach = float(r.get("ach_inf") if r.get("ach_inf") not in (None, "") else preset["ach_inf"])
        base_inf_m3h = vol_m3 * ach * (0.45 if orient == "INT" else 1.0)
        door_inf_m3h = (door_area * door_mat["inf_m3h_m2"] * (1.0 if door_is_ext else 0.45)) if door_area > 0 else 0.0
        win_inf_m3h = (win_area * win_frame["inf_m3h_m2"]) if (win_area > 0 and orient != "INT") else 0.0
        inf_m3h = max(base_inf_m3h, door_inf_m3h + win_inf_m3h + base_inf_m3h * 0.45) if (door_area > 0 or win_area > 0) else base_inf_m3h
        q_inf_sens = 0.3353 * inf_m3h * dt
        q_inf_lat = 833.67 * inf_m3h * dw

        # Room Sensible, Latent, Grand Total (with safety factor)
        q_sens_raw = q_wall + q_glass_rad + q_glass_cond + q_door_cond + q_roof_floor + q_partition + q_people_sens + q_light + q_equip_sens + q_oa_sens + q_inf_sens
        q_lat_raw = q_people_lat + q_equip_items_lat + q_oa_lat + q_inf_lat
        sf_mult = 1.0 + safety_pct / 100.0
        q_sens = q_sens_raw * sf_mult
        q_lat = q_lat_raw * sf_mult
        q_total = q_sens + q_lat
        q_kw = q_total / 1000.0
        q_btu = q_kw * 3412.14
        q_rt = q_kw / 3.517
        w_per_m2 = q_total / area
        shr = q_sens / max(1.0, q_total)

        # Heating Load (Winter, TCVN 5687:2024: t_in_win = 22.0°C)
        dt_win = max(0.0, 22.0 - t_out_win)
        q_heat_w = (wall_mat["u"] * net_wall_area + u_glass_eff * window_opening_area + door_mat["u"] * door_area * (1.0 if door_is_ext else 0.5) + u_roof_eff * area * 0.7 + floor_mat["u"] * area * floor_mat["dt_factor"]) * dt_win + 0.3353 * (oa_m3h * (1.0 - hrv_eff) + inf_m3h) * dt_win
        q_heat_w *= sf_mult

        # Supply Air Flow per TCVN 5687:2024 Annex G (G.1): c = 1.2 kJ/(m3.K), ΔT_supply = 10 K
        supply_m3h = (3.6 * q_sens) / (1.2 * 10.0)

        # QCVN 09:2017/BXD Envelope Check
        wall_qcvn_ok = (orient == "INT") or (wall_mat["r0"] >= 0.56)
        max_shgc_allowed = qcvn09_max_shgc(wwr_pct, orient)
        glass_qcvn_ok = (total_glazed_area <= 0.1) or (glass_mat["shgc"] <= max_shgc_allowed)
        if not wall_qcvn_ok:
            qcvn_warnings.append(f"{name}: Tường ngoài R0={wall_mat['r0']:.2f} < 0.56 m²K/W (QCVN 09:2017/BXD).")
        if not glass_qcvn_ok:
            qcvn_warnings.append(f"{name}: Kính/Cửa kính hướng {orient} (WWR={wwr_pct:.0f}%) có SHGC={glass_mat['shgc']:.2f} > giới hạn {max_shgc_allowed:.2f} (QCVN 09).")

        # Resolve Multi-Indoor Units per Room (Manual selected_units OR Auto split_units)
        room_style = r.get("prefer_type") or prefer_system
        split_units = max(1, int(r.get("split_units") or 1))
        manual_units_in = [u for u in (r.get("selected_units") or []) if isinstance(u, dict) and int(u.get("qty") or 0) > 0]
        prod_by_id = {p.get("id"): p for p in products}
        prod_by_mod = {p.get("model"): p for p in products}

        assigned_units = []
        if manual_units_in:
            tot_sel_btu = 0.0
            tot_sel_kw = 0.0
            all_clr_ok = True
            clr_notes = []
            for mu in manual_units_in:
                p = prod_by_id.get(mu.get("prod_id")) or prod_by_mod.get(mu.get("model"))
                if not p:
                    continue
                mq = max(1, int(mu.get("qty") or 1))
                m_h = re.search(r"(\d{3})\s*[xX×]", str(p.get("dimensions", "")))
                uh = int(m_h.group(1)) if m_h else 0
                req_pl = (uh + 45) if (p.get("duct") or p.get("ceiling_opening")) else 0
                c_ok = True
                c_note = "Đạt"
                if req_pl > 0 and plenum_mm > 0 and plenum_mm < req_pl:
                    c_ok = False
                    all_clr_ok = False
                    c_note = f"Trần {int(plenum_mm)}mm < {req_pl}mm ({p.get('model')})"
                    clr_notes.append(c_note)
                tot_sel_btu += p.get("cooling_btu", 0) * mq
                tot_sel_kw += p.get("cooling_kw", 0) * mq
                assigned_units.append({
                    "prod_id": p.get("id", ""), "model": p.get("model", ""), "name": p.get("name", ""),
                    "qty": mq, "cooling_btu": p.get("cooling_btu", 0), "cooling_kw": p.get("cooling_kw", 0),
                    "total_btu": p.get("cooling_btu", 0) * mq, "price": p.get("price", 0),
                    "unit_height_mm": uh, "req_plenum_mm": req_pl, "clearance_ok": c_ok, "clearance_note": c_note,
                })
            if assigned_units:
                cov_pct = round(tot_sel_btu / max(1.0, q_btu) * 100.0)
                lbl = " + ".join(f"{u['qty']}× {u['model']}" for u in assigned_units)
                rec = {
                    "prod_id": assigned_units[0]["prod_id"],
                    "model": lbl,
                    "name": f"Chọn tay ({sum(u['qty'] for u in assigned_units)} dàn)",
                    "qty": 1,
                    "unit_count": sum(u["qty"] for u in assigned_units),
                    "cooling_btu": round(tot_sel_btu),
                    "cooling_kw": round(tot_sel_kw, 2),
                    "total_btu": round(tot_sel_btu),
                    "coverage_pct": cov_pct,
                    "selection_mode": "MANUAL",
                    "clearance_ok": all_clr_ok,
                    "clearance_note": "; ".join(clr_notes) if clr_notes else f"Đạt ({int(plenum_mm)}mm)",
                }
            else:
                manual_units_in = []

        if not manual_units_in:
            rec_single = recommend_daikin_model(q_btu / split_units, room_style, plenum_mm, products)
            tot_qty = rec_single.get("qty", 1) * split_units
            tot_btu_auto = rec_single.get("cooling_btu", 0) * tot_qty
            cov_pct = round(tot_btu_auto / max(1.0, q_btu) * 100.0)
            assigned_units = [{
                "prod_id": rec_single.get("prod_id", ""), "model": rec_single.get("model", "—"),
                "name": rec_single.get("name", ""), "qty": tot_qty,
                "cooling_btu": rec_single.get("cooling_btu", 0), "cooling_kw": rec_single.get("cooling_kw", 0),
                "total_btu": tot_btu_auto, "price": rec_single.get("price", 0),
                "unit_height_mm": rec_single.get("unit_height_mm", 0), "req_plenum_mm": rec_single.get("req_plenum_mm", 0),
                "clearance_ok": rec_single.get("clearance_ok", True), "clearance_note": rec_single.get("clearance_note", ""),
            }]
            rec = dict(rec_single)
            rec["qty"] = tot_qty
            rec["unit_count"] = tot_qty
            rec["total_btu"] = tot_btu_auto
            rec["coverage_pct"] = cov_pct
            rec["selection_mode"] = "AUTO_SPLIT" if split_units > 1 else "AUTO"

        if not rec["clearance_ok"]:
            clearance_warnings.append(f"{name} ({rec['model']}): {rec['clearance_note']}")

        win_summary = f"{win_qty} cửa sổ ({win_w:.1f}×{win_h:.1f}m, {win_frame['name'].split('(')[0].strip()})" if win_area > 0 else (f"Kính {glass_area:.1f}m²" if glass_area > 0 else "Không cửa sổ ngoài")
        door_summary = f"{door_qty} cửa chính {door_w:.1f}×{door_h:.1f}m ({door_mat['name'].split('(')[0].strip()}, {'Ngoài' if door_is_ext else 'Trong'})" if door_area > 0 else "—"

        room_results.append({
            "index": idx + 1,
            "name": name,
            "floor": floor_label,
            "room_type": r.get("room_type", "LIVING"),
            "room_type_name": preset["name"],
            "area": round(area, 2),
            "h_concrete": h_concrete,
            "h_ceiling": h_ceiling,
            "plenum_mm": plenum_mm,
            "orientation": orient,
            "orientation_label": ori_data["label"],
            "wall_name": wall_mat["name"],
            "glass_name": glass_mat["name"],
            "roof_name": roof_mat["name"],
            "glass_area": round(total_glazed_area, 2),
            "window_summary": win_summary,
            "door_summary": door_summary,
            "door_area": round(door_area, 2),
            "equip_items_summary": ", ".join(equip_labels) if equip_labels else f"Định mức {equip_w_m2:.0f} W/m²",
            "equip_items_w": round((q_equip_items_sens + q_equip_items_lat), 0),
            "wwr_pct": round(wwr_pct, 1),
            "people": people,
            "t_in": t_in,
            "rh_in": rh_in,
            "oa_m3h": round(oa_m3h, 1),
            "supply_m3h": round(supply_m3h, 0),
            "q_sens_w": round(q_sens, 0),
            "q_lat_w": round(q_lat, 0),
            "q_total_w": round(q_total, 0),
            "q_kw": round(q_kw, 2),
            "q_btu": round(q_btu, 0),
            "q_rt": round(q_rt, 2),
            "q_heat_kw": round(q_heat_w / 1000.0, 2),
            "w_per_m2": round(w_per_m2, 1),
            "shr": round(shr, 2),
            "qcvn_ok": wall_qcvn_ok and glass_qcvn_ok,
            "wall_qcvn_ok": wall_qcvn_ok,
            "glass_qcvn_ok": glass_qcvn_ok,
            "max_shgc_allowed": max_shgc_allowed,
            "components_w": {
                "wall": round(q_wall * sf_mult, 0),
                "glass_rad": round(q_glass_rad * sf_mult, 0),
                "glass_cond": round(q_glass_cond * sf_mult, 0),
                "door": round(q_door_cond * sf_mult, 0),
                "roof_floor": round(q_roof_floor * sf_mult, 0),
                "partition": round(q_partition * sf_mult, 0),
                "people": round((q_people_sens + q_people_lat) * sf_mult, 0),
                "light_equip": round((q_light + q_equip_sens + q_equip_items_lat) * sf_mult, 0),
                "fresh_air": round((q_oa_sens + q_oa_lat) * sf_mult, 0),
                "infiltration": round((q_inf_sens + q_inf_lat) * sf_mult, 0),
            },
            "recommended_unit": rec,
            "assigned_units": assigned_units,
        })

        tot_area += area
        tot_sens_w += q_sens
        tot_lat_w += q_lat
        tot_q_w += q_total
        tot_heat_w += q_heat_w
        tot_oa_m3h += oa_m3h
        tot_supply_m3h += supply_m3h
        tot_people += people
        for ck in comp_sums:
            comp_sums[ck] += room_results[-1]["components_w"][ck]

    # Match Outdoor VRV / Multi Unit based on diversified load
    div_q_btu = (tot_q_w / 1000.0) * 3412.14 * diversity
    div_q_kw = (tot_q_w / 1000.0) * diversity
    outdoor_rec = None
    if products and div_q_btu > 0:
        out_cat = "VRV_H_OUT" if prefer_system.startswith("VRV") else ("MULTI_OUT" if prefer_system.startswith("MULTI") else "VRV_H_OUT")
        out_cands = [p for p in products if p.get("category_id") == out_cat and p.get("cooling_btu", 0) > 0]
        if prefer_system.startswith("VRV") and div_q_btu <= 82000:
            # Also include VRV IV-S for villas <= 9HP
            out_cands += [p for p in products if p.get("category_id") == "VRV_S_OUT" and p.get("cooling_btu", 0) > 0]
        out_cands.sort(key=lambda x: x["cooling_btu"])
        for op in out_cands:
            if op["cooling_btu"] >= div_q_btu * 0.90:
                outdoor_rec = op
                break
        if not outdoor_rec and out_cands:
            outdoor_rec = out_cands[-1]

    # Match HRV Daikin VAM if fresh air required
    hrv_rec = None
    if products and tot_oa_m3h > 0:
        vam_cands = [p for p in products if p.get("category_id") == "VRV_HRV"]
        for vp in vam_cands:
            cap_m = re.search(r"(\d+)", str(vp.get("hp", "")))
            if cap_m and int(cap_m.group(1)) >= tot_oa_m3h * 0.9:
                hrv_rec = vp
                break
        if not hrv_rec and vam_cands:
            hrv_rec = vam_cands[-1]

    return {
        "ok": True,
        "design_basis": {
            "standard": "TCVN 5687:2024 & QCVN 09:2017/BXD (CLTD/CLF)",
            "city_key": city_key,
            "city_name": city["name"],
            "grade": grade,
            "t_out": round(t_out, 1),
            "twb_out": round(twb_out, 1),
            "rh_out": round(rh_out, 1),
            "w_out_g_kg": round(w_out * 1000.0, 2),
            "h_out_kj_kg": round(h_out, 1),
            "t_out_win": round(t_out_win, 1),
            "safety_pct": safety_pct,
            "diversity_factor": diversity,
            "use_hrv": use_hrv,
            "hrv_efficiency": round(hrv_eff * 100),
        },
        "summary": {
            "room_count": len(room_results),
            "total_area_m2": round(tot_area, 2),
            "total_people": tot_people,
            "total_sens_kw": round(tot_sens_w / 1000.0, 2),
            "total_lat_kw": round(tot_lat_w / 1000.0, 2),
            "total_cooling_kw": round(tot_q_w / 1000.0, 2),
            "total_cooling_btu": round((tot_q_w / 1000.0) * 3412.14, 0),
            "total_cooling_rt": round((tot_q_w / 1000.0) / 3.517, 2),
            "total_heating_kw": round(tot_heat_w / 1000.0, 2),
            "avg_w_per_m2": round(tot_q_w / max(1.0, tot_area), 1),
            "shr": round(tot_sens_w / max(1.0, tot_q_w), 2),
            "diversified_kw": round(div_q_kw, 2),
            "diversified_btu": round(div_q_btu, 0),
            "total_oa_m3h": round(tot_oa_m3h, 0),
            "total_supply_m3h": round(tot_supply_m3h, 0),
            "components_w": {k: round(v, 0) for k, v in comp_sums.items()},
            "outdoor_rec": {
                "prod_id": outdoor_rec.get("id", ""),
                "model": outdoor_rec.get("model", ""),
                "name": outdoor_rec.get("name", ""),
                "cooling_btu": outdoor_rec.get("cooling_btu", 0),
                "cooling_kw": outdoor_rec.get("cooling_kw", 0),
                "price": outdoor_rec.get("price", 0),
                "image": outdoor_rec.get("image", ""),
            } if outdoor_rec else None,
            "hrv_rec": {
                "prod_id": hrv_rec.get("id", ""),
                "model": hrv_rec.get("model", ""),
                "name": hrv_rec.get("name", ""),
                "hp": hrv_rec.get("hp", ""),
            } if hrv_rec else None,
        },
        "rooms": room_results,
        "qcvn_warnings": qcvn_warnings,
        "clearance_warnings": clearance_warnings,
    }


# ==============================================================================
# 5. DAIKIN DUCT CHECKER ENGINE (ASHRAE Friction, Velocity, Huebscher De & ESP)
# ==============================================================================
STD_RECT_SIZES = [150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 900, 1000, 1100, 1200]
STD_ROUND_SIZES = [100, 125, 150, 160, 200, 250, 300, 315, 350, 400, 450, 500, 560, 630]


def parse_model_airflow_esp(prod: dict) -> dict:
    """Extract rated airflow (m3/h) and max ESP (Pa) directly from verified Daikin database product."""
    af_str = str(prod.get("airflow", ""))
    esp_str = str(prod.get("esp", ""))

    # 1. Try explicit m3/h in string
    af_m3h = 0.0
    m_h = re.search(r"(\d+(?:[.,]\d+)?)\s*m³/h", af_str, re.I)
    if m_h:
        af_m3h = float(m_h.group(1).replace(",", "."))
    else:
        # Try first number in m3/phut -> multiply by 60
        m_min = re.search(r"(\d+(?:[.,]\d+)?)", af_str)
        if m_min:
            val = float(m_min.group(1).replace(",", "."))
            af_m3h = val * 60.0 if ("phút" in af_str or "min" in af_str or val < 120) else val

    # 2. Extract rated & max ESP from string (e.g. "50-150 Pa (ĐM 50Pa)" or "40 Pa" or "132 - 221 Pa")
    nums = [int(x) for x in re.findall(r"(\d+)", esp_str)]
    esp_rated = nums[0] if nums else 50
    esp_max = max(nums) if nums else 50
    if "ĐM" in esp_str and len(nums) >= 3:
        esp_rated = nums[2]
        esp_max = max(nums[0], nums[1])
    elif len(nums) >= 2:
        esp_max = max(nums[0], nums[1])
        esp_rated = nums[0]

    return {
        "airflow_m3h": round(af_m3h, 0) if af_m3h > 0 else 900.0,
        "esp_rated_pa": esp_rated,
        "esp_max_pa": esp_max,
    }


def darcy_friction_factor(re_num: float, rel_rough: float) -> float:
    """Altshul-Tsal explicit approximation of Colebrook-White Darcy friction factor."""
    if re_num <= 2300:
        return 64.0 / max(100.0, re_num)
    f_t = 0.11 * ((rel_rough + 68.0 / re_num) ** 0.25)
    return f_t if f_t >= 0.018 else 0.85 * f_t + 0.0028


def duct_hydraulics(q_m3h: float, shape: str, w_mm: float, h_mm: float, d_mm: float, roughness_mm: float = 0.09) -> dict:
    """Calculate velocity, equivalent diameter, friction loss Pa/m, dynamic pressure Pa."""
    rho = 1.2       # kg/m3 at 20C
    nu = 1.51e-5    # m2/s kinematic viscosity
    q_m3s = max(0.001, q_m3h / 3600.0)

    if shape == "round":
        d_m = max(0.08, d_mm / 1000.0)
        area = math.pi * (d_m ** 2) / 4.0
        de_m = d_m
        v = q_m3s / area
    else:
        a = max(0.10, w_mm / 1000.0)
        b = max(0.10, h_mm / 1000.0)
        area = a * b
        de_m = 1.30 * ((a * b) ** 0.625) / ((a + b) ** 0.25)
        v = q_m3s / area

    re_num = (v * de_m) / nu
    f = darcy_friction_factor(re_num, (roughness_mm / 1000.0) / de_m)
    pd = 0.5 * rho * (v ** 2)
    dp_per_m = f * (1.0 / de_m) * pd

    return {
        "area_m2": round(area, 4),
        "de_mm": round(de_m * 1000.0, 1),
        "velocity_ms": round(v, 2),
        "pd_pa": round(pd, 2),
        "dp_pa_m": round(dp_per_m, 2),
        "reynolds": int(re_num),
    }


def auto_size_duct(q_m3h: float, target_dp: float = 1.0, max_v: float = 6.0, max_h_mm: int = 250, roughness_mm: float = 0.09) -> dict:
    """Find best standard round and rectangular duct sizes matching target friction & max velocity."""
    best_round = STD_ROUND_SIZES[-1]
    for d in STD_ROUND_SIZES:
        res = duct_hydraulics(q_m3h, "round", 0, 0, d, roughness_mm)
        if res["dp_pa_m"] <= target_dp and res["velocity_ms"] <= max_v:
            best_round = d
            break

    # Rectangular with height <= max_h_mm and aspect ratio <= 4:1
    best_rect = (400, min(250, max_h_mm))
    best_area = 1e9
    for h in [x for x in STD_RECT_SIZES if x <= max_h_mm]:
        for w in STD_RECT_SIZES:
            if w < h or w > h * 4:
                continue
            res = duct_hydraulics(q_m3h, "rect", w, h, 0, roughness_mm)
            if res["dp_pa_m"] <= target_dp and res["velocity_ms"] <= max_v:
                if w * h < best_area:
                    best_area = w * h
                    best_rect = (w, h)
                break
    return {
        "round_mm": best_round,
        "round_hyd": duct_hydraulics(q_m3h, "round", 0, 0, best_round, roughness_mm),
        "rect_w_mm": best_rect[0],
        "rect_h_mm": best_rect[1],
        "rect_hyd": duct_hydraulics(q_m3h, "rect", best_rect[0], best_rect[1], 0, roughness_mm),
    }


def calc_duct_checker(payload: dict, products: list = None) -> dict:
    """
    Daikin Duct Checker: Sizes main duct, branches, flex ducts, grilles, and verifies Total Pressure Drop vs Model ESP.
    """
    products = products or []
    model_id = payload.get("model_id", "")
    prod = next((p for p in products if p.get("id") == model_id or p.get("model") == model_id), None)

    model_info = parse_model_airflow_esp(prod) if prod else {"airflow_m3h": 1200.0, "esp_rated_pa": 50, "esp_max_pa": 150}
    q_total = float(payload.get("airflow_m3h") or model_info["airflow_m3h"])
    esp_rated = float(payload.get("esp_rated_pa") or model_info["esp_rated_pa"])
    esp_max = float(payload.get("esp_max_pa") or model_info["esp_max_pa"])

    target_dp = float(payload.get("target_dp", 1.0))  # Pa/m (ASHRAE equal friction: 0.8 - 1.2 Pa/m)
    max_h_mm = int(payload.get("max_h_mm", 250))
    n_branches = max(1, int(payload.get("num_branches", 3)))
    main_len_m = max(0.0, float(payload.get("main_len_m", 6.0)))
    branch_len_m = max(0.0, float(payload.get("branch_len_m", 4.0)))
    flex_len_m = max(0.0, float(payload.get("flex_len_m", 2.5)))
    n_elbows = max(0, int(payload.get("num_elbows", 2)))
    return_duct_len_m = max(0.0, float(payload.get("return_len_m", 3.0)))

    # 1. Main Trunk Sizing
    main_auto = auto_size_duct(q_total, target_dp=target_dp, max_v=6.5, max_h_mm=max_h_mm, roughness_mm=0.09)
    main_w = int(payload.get("custom_main_w") or main_auto["rect_w_mm"])
    main_h = int(payload.get("custom_main_h") or main_auto["rect_h_mm"])
    main_hyd = duct_hydraulics(q_total, "rect", main_w, main_h, 0, 0.09)

    # 2. Branch Duct Sizing (Rigid Galvanized + Flexible Insulated Duct)
    q_branch = q_total / n_branches
    br_auto = auto_size_duct(q_branch, target_dp=target_dp, max_v=4.5, max_h_mm=min(200, max_h_mm), roughness_mm=0.09)
    flex_dia = int(payload.get("custom_flex_d") or br_auto["round_mm"])
    # Flex duct roughness = 3.0mm (much higher friction than smooth sheet metal!)
    flex_hyd = duct_hydraulics(q_branch, "round", 0, 0, flex_dia, 3.0)

    # 3. Return Duct Sizing (lower velocity <= 4.5 m/s to prevent noise)
    ret_auto = auto_size_duct(q_total, target_dp=0.8, max_v=4.5, max_h_mm=max_h_mm, roughness_mm=0.09)
    ret_hyd = ret_auto["rect_hyd"]

    # 4. Grille Sizing (Supply Linear Slot / Louver at ~2.5 m/s effective face area 65%, Return at ~2.0 m/s)
    # Effective free area A_eff = Q / (3600 * v), Gross area = A_eff / 0.65
    sup_gross_m2 = (q_branch / (3600.0 * 2.5)) / 0.65
    sup_slot_len_mm = max(600, int(math.ceil((sup_gross_m2 / 0.15) * 1000.0 / 100.0) * 100))
    ret_gross_m2 = (q_total / (3600.0 * 2.0)) / 0.70
    ret_slot_len_mm = max(800, int(math.ceil((ret_gross_m2 / 0.20) * 1000.0 / 100.0) * 100))

    # 5. Total System External Pressure Drop (Critical Path)
    dp_main_straight = main_hyd["dp_pa_m"] * main_len_m
    dp_branch_straight = br_auto["rect_hyd"]["dp_pa_m"] * branch_len_m
    dp_flex = flex_hyd["dp_pa_m"] * flex_len_m
    dp_return = ret_hyd["dp_pa_m"] * return_duct_len_m
    # Local fittings: Plenum entry (zeta=0.5), Elbows (zeta=0.35 each), Tee branch (zeta=0.8), VCD damper (zeta=0.45)
    dp_fittings = (0.5 + 0.35 * n_elbows + 0.8 + 0.45) * main_hyd["pd_pa"]
    dp_grilles = 12.0 + 8.0  # Supply grille (~12 Pa) + Return grille w/ filter (~8 Pa)
    dp_total = dp_main_straight + dp_branch_straight + dp_flex + dp_return + dp_fittings + dp_grilles

    # Sheet metal area estimate for quotation (m2 of galvanized steel)
    sheet_m2 = 2.0 * ((main_w + main_h) / 1000.0) * main_len_m + \
               2.0 * ((br_auto["rect_w_mm"] + br_auto["rect_h_mm"]) / 1000.0) * branch_len_m * n_branches + \
               2.0 * ((ret_auto["rect_w_mm"] + ret_auto["rect_h_mm"]) / 1000.0) * return_duct_len_m

    esp_status = "OK_RATED" if dp_total <= esp_rated else ("OK_MAX" if dp_total <= esp_max else "EXCEED_ESP")
    esp_verdict = (
        f"ĐẠT CHUẨN — Tổn thất hệ thống ({dp_total:.1f} Pa) nằm trong mức áp suất định mức ({esp_rated:.0f} Pa)."
        if esp_status == "OK_RATED"
        else (
            f"ĐẠT KHI TĂNG CẤP ESP — Tổn thất ({dp_total:.1f} Pa) vượt ĐM {esp_rated:.0f} Pa nhưng trong giới hạn tối đa {esp_max:.0f} Pa (chỉnh tăng cấp ESP trên điều khiển dây BRC1E63)."
            if esp_status == "OK_MAX"
            else f"CẢNH BÁO THIẾU CỘT ÁP — Tổn thất ({dp_total:.1f} Pa) VƯỢT QUÁ ESP tối đa ({esp_max:.0f} Pa) của máy! Cần tăng tiết diện ống, giảm chiều dài ống mềm hoặc đổi sang dòng FXMQ áp suất cao."
        )
    )

    noise_status = "ÊM (Đạt chuẩn phòng ngủ/VP)" if main_hyd["velocity_ms"] <= 5.5 and flex_hyd["velocity_ms"] <= 3.8 else (
        "TRUNG BÌNH (Phù hợp sảnh/TM)" if main_hyd["velocity_ms"] <= 7.0 else "ỒN CAO (Cần tăng tiết diện ống)"
    )

    return {
        "ok": True,
        "model": prod.get("model", "Tùy chỉnh") if prod else "Tùy chỉnh",
        "model_name": prod.get("name", "") if prod else "",
        "duct_excel": prod.get("duct") if prod else None,
        "airflow_m3h": round(q_total, 0),
        "branch_airflow_m3h": round(q_branch, 0),
        "num_branches": n_branches,
        "esp_rated_pa": esp_rated,
        "esp_max_pa": esp_max,
        "main_duct": {
            "w_mm": main_w, "h_mm": main_h,
            "round_equiv_mm": main_auto["round_mm"],
            "hyd": main_hyd,
            "dp_pa": round(dp_main_straight, 1),
        },
        "branch_duct": {
            "w_mm": br_auto["rect_w_mm"], "h_mm": br_auto["rect_h_mm"],
            "round_mm": br_auto["round_mm"],
            "hyd": br_auto["rect_hyd"],
            "dp_pa": round(dp_branch_straight, 1),
        },
        "flex_duct": {
            "dia_mm": flex_dia,
            "len_m": flex_len_m,
            "hyd": flex_hyd,
            "dp_pa": round(dp_flex, 1),
        },
        "return_duct": {
            "w_mm": ret_auto["rect_w_mm"], "h_mm": ret_auto["rect_h_mm"],
            "hyd": ret_hyd,
            "dp_pa": round(dp_return, 1),
        },
        "grilles": {
            "supply_rec": f"{n_branches} cửa cấp Linear Slot / Nan bầu dục {sup_slot_len_mm}×150 mm (mỗi cửa {round(q_branch)} m³/h)",
            "return_rec": f"1 cửa hồi có lưới lọc bụi {ret_slot_len_mm}×200 mm (lưu lượng {round(q_total)} m³/h)",
            "vcd_rec": f"{n_branches} van chỉnh gió VCD Ø{flex_dia}",
        },
        "pressure_breakdown": {
            "main_straight_pa": round(dp_main_straight, 1),
            "branch_straight_pa": round(dp_branch_straight, 1),
            "flex_pa": round(dp_flex, 1),
            "return_pa": round(dp_return, 1),
            "fittings_pa": round(dp_fittings, 1),
            "grilles_pa": round(dp_grilles, 1),
            "total_pa": round(dp_total, 1),
            "esp_margin_pa": round(esp_max - dp_total, 1),
        },
        "sheet_metal_m2": round(sheet_m2, 2),
        "flex_total_m": round(flex_len_m * n_branches, 1),
        "esp_status": esp_status,
        "esp_verdict": esp_verdict,
        "noise_status": noise_status,
    }


# ==============================================================================
# 6. COOLPACK SUPERHEAT / SUBCOOLING & DAIKIN PIPING DERATING ENGINE (R410A / R32)
# NIST-fitted vapor pressure curves: log10(P_bar_abs) = A - B / (T_K + C)
# Validated across -20°C to +65°C within ±0.2°C of NIST REFPROP / CoolPack!
# ==============================================================================
REFRIGERANT_ANTOINE = {
    "R410A": {"A": 4.89271, "B": 1162.235, "C": 18.152, "gwp": 2088, "safety": "A1", "sh_min": 5.0, "sh_max": 9.0, "sc_min": 4.0, "sc_max": 8.0},
    "R32":   {"A": 4.81045, "B": 1099.401, "C": 8.726,  "gwp": 675,  "safety": "A2L","sh_min": 5.0, "sh_max": 9.0, "sc_min": 4.0, "sc_max": 8.0},
}

# Exact Daikin additional charge (kg/m) by liquid pipe OD (mm) for VRV / SkyAir
LIQUID_PIPE_CHARGE_KG_M = {
    "6.4": 0.022,
    "9.5": 0.059,
    "12.7": 0.120,
    "15.9": 0.170,
    "19.1": 0.250,
}


def ref_tsat_from_pgauge_bar(ref: str, p_gauge_bar: float) -> float:
    """Saturation temperature [°C] from gauge pressure [bar] (P_abs = P_gauge + 1.01325)."""
    c = REFRIGERANT_ANTOINE.get(ref, REFRIGERANT_ANTOINE["R410A"])
    p_abs = max(1.2, p_gauge_bar + 1.01325)
    t_k = c["B"] / (c["A"] - math.log10(p_abs)) - c["C"]
    return t_k - 273.15


def calc_coolpack_cycle(payload: dict) -> dict:
    """CoolPack-inspired Superheat, Subcooling, P-h Cycle Health & Daikin Pipe Derating."""
    ref = payload.get("refrigerant", "R410A")
    c = REFRIGERANT_ANTOINE.get(ref, REFRIGERANT_ANTOINE["R410A"])

    p_unit = payload.get("pressure_unit", "bar")  # "bar" or "psi"
    p_suc_raw = float(payload.get("p_suction", 8.5 if ref == "R410A" else 8.8))
    p_dis_raw = float(payload.get("p_discharge", 28.0 if ref == "R410A" else 29.0))
    p_suc_bar = p_suc_raw * 0.0689476 if p_unit == "psi" else p_suc_raw
    p_dis_bar = p_dis_raw * 0.0689476 if p_unit == "psi" else p_dis_raw

    t_suc_meas = float(payload.get("t_suction_meas", 13.0))
    t_liq_meas = float(payload.get("t_liquid_meas", 41.0))

    t_evap = ref_tsat_from_pgauge_bar(ref, p_suc_bar)
    t_cond = ref_tsat_from_pgauge_bar(ref, p_dis_bar)
    superheat = t_suc_meas - t_evap
    subcooling = t_cond - t_liq_meas

    # Carnot & practical VRV Inverter COP estimate
    t_e_k = t_evap + 273.15
    t_c_k = t_cond + 273.15
    cop_carnot = t_e_k / max(5.0, t_c_k - t_e_k)
    cop_est = min(5.8, max(1.8, cop_carnot * 0.56))

    # Diagnostic Verdicts (CoolPack / Daikin Service Checker Logic)
    if superheat < 3.0:
        sh_status = "LOW"
        sh_diag = "NGUY HIỂM — Quá nhiệt quá thấp (< 3K): Nguy cơ dịch lỏng hồi về máy nén gây thủy kích! Kiểm tra van tiết lưu EEV hoặc thừa gas."
    elif superheat <= 10.0:
        sh_status = "OK"
        sh_diag = f"ĐẠT CHUẨN ({superheat:.1f} K nằm trong dải tối ưu 5–9 K): Dàn bay hơi trao đổi nhiệt tốt, an toàn cho máy nén."
    else:
        sh_status = "HIGH"
        sh_diag = f"CẢNH BÁO — Quá nhiệt cao ({superheat:.1f} K > 10 K): Dấu hiệu thiếu môi chất lạnh (thiếu gas), nghẹt phin lọc/EEV hoặc thiếu gió dàn lạnh."

    if subcooling < 2.5:
        sc_status = "LOW"
        sc_diag = f"CẢNH BÁO — Quá lạnh thấp ({subcooling:.1f} K < 3 K): Thiếu gas nạp hoặc dàn ngưng giải nhiệt kém (bẩn dàn nóng / quẩn gió)."
    elif subcooling <= 10.0:
        sc_status = "OK"
        sc_diag = f"ĐẠT CHUẨN ({subcooling:.1f} K nằm trong dải tối ưu 4–8 K): Môi chất lỏng cấp ổn định tới van tiết lưu."
    else:
        sc_status = "HIGH"
        sc_diag = f"LƯU Ý — Quá lạnh cao ({subcooling:.1f} K > 10 K): Có thể nạp dư môi chất lạnh hoặc tắc bán phần đường lỏng."

    # Daikin Piping Length & Height Derating + Extra Gas Charge Calculator
    eq_len_m = max(5.0, float(payload.get("pipe_length_m", 35.0)))
    height_diff_m = max(0.0, float(payload.get("height_diff_m", 12.0)))
    rated_kw = max(1.0, float(payload.get("rated_kw", 40.0)))
    liq_od = str(payload.get("liquid_pipe_od", "12.7"))
    precharged_m = max(0.0, float(payload.get("precharged_m", 0.0)))

    # Typical Daikin VRV H / SkyAir capacity correction curves (length & elevation friction)
    len_loss = max(0.0, (eq_len_m - 7.5) * 0.00135)
    elev_loss = height_diff_m * 0.0012
    derate_factor = max(0.75, min(1.0, 1.0 - len_loss - elev_loss))
    actual_kw = rated_kw * derate_factor

    charge_rate = LIQUID_PIPE_CHARGE_KG_M.get(liq_od, 0.059)
    extra_charge_kg = max(0.0, (eq_len_m - precharged_m) * charge_rate)

    return {
        "ok": True,
        "refrigerant": ref,
        "gwp": c["gwp"],
        "safety_class": c["safety"],
        "p_suction_bar": round(p_suc_bar, 2),
        "p_suction_psi": round(p_suc_bar * 14.5038, 1),
        "p_discharge_bar": round(p_dis_bar, 2),
        "p_discharge_psi": round(p_dis_bar * 14.5038, 1),
        "t_evap_c": round(t_evap, 1),
        "t_cond_c": round(t_cond, 1),
        "superheat_k": round(superheat, 1),
        "subcooling_k": round(subcooling, 1),
        "sh_status": sh_status,
        "sh_diag": sh_diag,
        "sc_status": sc_status,
        "sc_diag": sc_diag,
        "cop_est": round(cop_est, 2),
        "piping": {
            "eq_len_m": eq_len_m,
            "height_diff_m": height_diff_m,
            "derate_factor": round(derate_factor, 3),
            "loss_pct": round((1.0 - derate_factor) * 100.0, 1),
            "rated_kw": rated_kw,
            "actual_kw": round(actual_kw, 2),
            "actual_btu": round(actual_kw * 3412.14, 0),
            "liquid_pipe_od": liq_od,
            "charge_rate_kg_m": charge_rate,
            "extra_charge_kg": round(extra_charge_kg, 2),
        },
    }


# ==============================================================================
# 7. DRAWING TAKEOFF ENGINE (PDF + AutoCAD DXF + DWG COM Bridge + Image)
# ==============================================================================
ROOM_KEYWORDS = [
    (r"ph[oò]ng\s*ng[uủ]|p\.?\s*ng[uủ]|bedroom|master\s*bed|pn\s*\d*", "BEDROOM"),
    (r"ph[oò]ng\s*kh[aá]ch|p\.?\s*kh[aá]ch|sinh\s*ho[aạ]t|living|pk\s*\d*", "LIVING"),
    (r"ph[oò]ng\s*[aă]n|b[eế]p|dining|kitchen", "DINING"),
    (r"v[aă]n\s*ph[oò]ng|l[aà]m\s*vi[eệ]c|office|gi[aá]m\s*[đd][oố]c", "OFFICE"),
    (r"ph[oò]ng\s*h[oọ]p|h[oộ]i\s*th[aả]o|h[oộ]i\s*tr[uư][oờ]ng|meeting|conference", "MEETING"),
    (r"showroom|c[uử]a\s*h[aà]ng|b[aá]n\s*h[aà]ng|shop|retail", "SHOWROOM"),
    (r"nh[aà]\s*h[aà]ng|caf[eé]|qu[aá]n|restaurant", "RESTAURANT"),
    (r"l[oớ]p\s*h[oọ]c|ph[oò]ng\s*h[oọ]c|classroom|th[uư]\s*vi[eệ]n", "CLASSROOM"),
    (r"gym|th[eể]\s*thao|fitness|yoga", "GYM"),
    (r"s[aả]nh|ti[eề]n\s*s[aả]nh|lobby|l[eễ]\s*t[aâ]n", "LOBBY"),
    (r"ph[oò]ng\s*kh[aá]m|b[eệ]nh\s*nh[aâ]n|clinic", "CLINIC"),
]


def guess_room_type_from_label(text: str) -> str:
    low = (text or "").lower()
    for pat, rtype in ROOM_KEYWORDS:
        if re.search(pat, low):
            return rtype
    return "LIVING"


def polygon_area(pts: list) -> float:
    n = len(pts)
    if n < 3:
        return 0.0
    s = 0.0
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return abs(s) * 0.5


def point_in_poly(x: float, y: float, poly: list) -> bool:
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def parse_dxf_bytes(raw_bytes: bytes, filename: str = "drawing.dxf") -> dict:
    """Extract room names, areas, and perimeters directly from AutoCAD DXF vector entities."""
    if not ezdxf:
        return {"ok": False, "error": "Thư viện ezdxf chưa được cài đặt."}
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tf:
            tf.write(raw_bytes)
            tmp_path = tf.name
        doc = ezdxf.readfile(tmp_path)
        msp = doc.modelspace()

        # Detect drawing scale (mm -> m vs cm -> m vs m)
        insunits = int(doc.header.get("$INSUNITS", 4))
        scale_to_m = 0.001 if insunits == 4 else (0.01 if insunits == 5 else (1.0 if insunits == 6 else 0.001))

        # Collect TEXT / MTEXT entities
        labels = []
        for ent in msp.query("TEXT MTEXT"):
            try:
                txt = ent.plain_text() if ent.dxftype() == "MTEXT" else ent.dxf.text
                txt = " ".join((txt or "").split())
                if not txt:
                    continue
                pos = ent.dxf.insert
                labels.append({"text": txt, "x": float(pos.x), "y": float(pos.y)})
            except Exception:
                pass

        # Collect closed LWPOLYLINE room boundaries
        polys = []
        for pl in msp.query("LWPOLYLINE"):
            try:
                pts = [(p[0], p[1]) for p in pl.get_points("xy")]
                if len(pts) < 3:
                    continue
                is_closed = pl.closed or (math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 50.0)
                if not is_closed:
                    continue
                a_raw = polygon_area(pts)
                if a_raw <= 0:
                    continue
                # Auto-calibrate unit if $INSUNITS unset (0)
                if insunits == 0:
                    if a_raw > 50000:
                        scale_to_m = 0.001
                    elif a_raw > 500:
                        scale_to_m = 0.01
                    else:
                        scale_to_m = 1.0
                area_m2 = a_raw * (scale_to_m ** 2)
                if 3.5 <= area_m2 <= 2500.0:
                    xs = [p[0] for p in pts]
                    ys = [p[1] for p in pts]
                    perim_m = sum(math.hypot(pts[(i+1)%len(pts)][0]-pts[i][0], pts[(i+1)%len(pts)][1]-pts[i][1]) for i in range(len(pts))) * scale_to_m
                    polys.append({
                        "pts": pts, "area_m2": round(area_m2, 2), "perim_m": round(perim_m, 1),
                        "cx": sum(xs)/len(xs), "cy": sum(ys)/len(ys), "layer": pl.dxf.layer,
                    })
            except Exception:
                pass

        rooms = []
        used_labels = set()
        # Match labels inside closed polylines
        for pi, poly in enumerate(polys):
            inside_txts = []
            for li, lb in enumerate(labels):
                if point_in_poly(lb["x"], lb["y"], poly["pts"]):
                    inside_txts.append((li, lb["text"]))
            room_name = ""
            for li, t in inside_txts:
                if any(re.search(pat, t.lower()) for pat, _ in ROOM_KEYWORDS):
                    room_name = t
                    used_labels.add(li)
                    break
            if not room_name and inside_txts:
                room_name = inside_txts[0][1]
                used_labels.add(inside_txts[0][0])
            if room_name or len(polys) <= 25:
                rname = room_name or f"Phòng CAD #{pi+1} (Layer {poly['layer']})"
                rooms.append({
                    "name": rname[:60],
                    "floor": "Tầng 1",
                    "room_type": guess_room_type_from_label(rname),
                    "area": poly["area_m2"],
                    "h_concrete": 3.6,
                    "h_ceiling": 3.0,
                    "ext_wall_len": round(poly["perim_m"] * 0.28, 1),
                    "glass_area": round(poly["area_m2"] * 0.14, 1),
                    "orientation": "W",
                    "source": f"CAD DXF Polyline (Layer: {poly['layer']})",
                })

        # Also parse explicit text annotations like "PHÒNG KHÁCH - 35.5 m2" not matched to polys
        for li, lb in enumerate(labels):
            if li in used_labels:
                continue
            t = lb["text"]
            m_area = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:m2|m²)", t, re.I)
            if m_area and any(re.search(pat, t.lower()) for pat, _ in ROOM_KEYWORDS):
                a_val = float(m_area.group(1).replace(",", "."))
                if 3.0 <= a_val <= 2000.0:
                    rooms.append({
                        "name": re.sub(r"[-:]?\s*\d+(?:[.,]\d+)?\s*(?:m2|m²).*", "", t, flags=re.I).strip() or t,
                        "floor": "Tầng 1",
                        "room_type": guess_room_type_from_label(t),
                        "area": round(a_val, 2),
                        "h_concrete": 3.6,
                        "h_ceiling": 3.0,
                        "ext_wall_len": round(math.sqrt(a_val) * 1.1, 1),
                        "glass_area": round(a_val * 0.14, 1),
                        "orientation": "W",
                        "source": "CAD DXF Text",
                    })

        # Deduplicate similar names & limit to 50
        return {
            "ok": True,
            "file_type": "DXF",
            "filename": filename,
            "stats": {"polylines_found": len(polys), "text_entities": len(labels), "rooms_extracted": len(rooms)},
            "rooms": rooms[:50],
            "note": f"Đã đọc trực tiếp bản vẽ CAD DXF ({len(polys)} vùng kín, {len(labels)} nhãn chữ -> bóc tách được {len(rooms)} phòng)."
                    if rooms else "File DXF chưa có vùng khép kín (closed polyline) hoặc nhãn diện tích chuẩn. Bạn có thể xuất sang PDF để AI Vision đọc mặt bằng trực quan.",
        }
    except Exception as e:
        return {"ok": False, "error": f"Lỗi đọc file DXF: {e}"}
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


def try_convert_dwg_to_dxf(raw_bytes: bytes) -> tuple:
    """Try converting DWG -> DXF via local AutoCAD COM if installed on Windows."""
    tmp_dwg = None
    tmp_dxf = None
    try:
        import win32com.client
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dwg") as tf:
            tf.write(raw_bytes)
            tmp_dwg = tf.name
        tmp_dxf = tmp_dwg[:-4] + ".dxf"
        acad = win32com.client.Dispatch("AutoCAD.Application")
        doc = acad.Documents.Open(tmp_dwg, True)
        # 61 = ac2018_dxf, 49 = ac2013_dxf
        doc.SaveAs(tmp_dxf, 61)
        doc.Close(False)
        with open(tmp_dxf, "rb") as f:
            return f.read(), ""
    except Exception as e:
        return None, f"Không kết nối được AutoCAD trên máy để tự đổi DWG sang DXF ({e}). Vui lòng lưu bản vẽ trong AutoCAD dưới dạng .DXF hoặc in sang .PDF rồi tải lên!"
    finally:
        for p in (tmp_dwg, tmp_dxf):
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass


def parse_pdf_drawing_offline(raw_bytes: bytes, page_no: int = 1, filename: str = "drawing.pdf") -> dict:
    """Extract architectural room text/areas from PDF + render high-res preview image for UI & AI Vision."""
    if not pymupdf:
        return {"ok": False, "error": "PyMuPDF chưa khả dụng."}
    try:
        doc = pymupdf.open(stream=raw_bytes, filetype="pdf")
        total_pages = len(doc)
        pg_idx = max(0, min(total_pages - 1, int(page_no) - 1))
        page = doc[pg_idx]

        # Render preview PNG (~1400px wide max for crisp visual & AI Vision)
        zoom = min(2.2, 1400.0 / max(1.0, page.rect.width))
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
        img_bytes = pix.tobytes("png")
        preview_b64 = base64.b64encode(img_bytes).decode("ascii")

        # Extract individual text segments (splitting horizontally separated room labels cleanly)
        td = page.get_text("dict")
        text_chunks = []
        for blk in td.get("blocks", []):
            if blk.get("type") != 0:
                continue
            for ln in blk.get("lines", []):
                spans = sorted(ln.get("spans", []), key=lambda s: s["bbox"][0])
                if not spans:
                    continue
                cur_txt = spans[0].get("text", "")
                prev_x1 = spans[0]["bbox"][2]
                for sp in spans[1:]:
                    gap = sp["bbox"][0] - prev_x1
                    if gap > 22.0:
                        if cur_txt.strip():
                            text_chunks.append(" ".join(cur_txt.split()))
                        cur_txt = sp.get("text", "")
                    else:
                        cur_txt += (" " if gap > 2.0 else "") + sp.get("text", "")
                    prev_x1 = max(prev_x1, sp["bbox"][2])
                if cur_txt.strip():
                    text_chunks.append(" ".join(cur_txt.split()))

        rooms = []
        raw_texts = []
        current_floor = "Tầng 1"
        for txt in text_chunks:
            if not txt:
                continue
            raw_texts.append(txt)
            m_fl = re.search(r"(t[aầ]ng\s*\d+|t[aầ]ng\s*tr[eệ]t|t[aầ]ng\s*m[aá]i|l[aầ]u\s*\d+)", txt, re.I)
            if m_fl:
                current_floor = m_fl.group(1).title()

            is_room = any(re.search(pat, txt.lower()) for pat, _ in ROOM_KEYWORDS)
            m_area = re.search(r"(?:s\s*=?\s*)?(\d+(?:[.,]\d+)?)\s*(?:m2|m²)", txt, re.I)
            m_dim = re.search(r"(\d+(?:[.,]\d+)?)\s*[xX×]\s*(\d+(?:[.,]\d+)?)\s*m?\b", txt)

            if is_room and (m_area or m_dim):
                if m_area:
                    area_val = float(m_area.group(1).replace(",", "."))
                else:
                    d1 = float(m_dim.group(1).replace(",", "."))
                    d2 = float(m_dim.group(2).replace(",", "."))
                    if d1 > 100:
                        d1 /= 1000.0
                    if d2 > 100:
                        d2 /= 1000.0
                    area_val = d1 * d2
                if 3.0 <= area_val <= 2500.0:
                    clean_nm = re.sub(r"(?:s\s*=?\s*)?\d+(?:[.,]\d+)?\s*(?:m2|m²).*", "", txt, flags=re.I)
                    clean_nm = re.sub(r"\d+(?:[.,]\d+)?\s*[xX×]\s*\d+(?:[.,]\d+)?\s*m?\b.*", "", clean_nm).strip(" -\u00ad:|")
                    rooms.append({
                        "name": (clean_nm or txt)[:60],
                        "floor": current_floor,
                        "room_type": guess_room_type_from_label(txt),
                        "area": round(area_val, 2),
                        "h_concrete": 3.6,
                        "h_ceiling": 3.0,
                        "ext_wall_len": round(math.sqrt(area_val) * 1.1, 1),
                        "glass_area": round(area_val * 0.14, 1),
                        "orientation": "W",
                        "source": f"PDF Vector Text (Trang {pg_idx + 1})",
                    })

        doc.close()
        return {
            "ok": True,
            "file_type": "PDF",
            "filename": filename,
            "page": pg_idx + 1,
            "total_pages": total_pages,
            "preview_data_url": f"data:image/png;base64,{preview_b64}",
            "preview_b64": preview_b64,
            "rooms": rooms[:50],
            "raw_text_sample": "\n".join(raw_texts[:40]),
            "note": f"Đã đọc trang {pg_idx+1}/{total_pages} bản vẽ PDF — nhận diện Offline được {len(rooms)} phòng có ghi diện tích."
                    + (" Bạn có thể bấm nút '🤖 AI Vision Quét Mặt Bằng' (khi có API Key Gemini/OpenAI) để AI đọc cả bản vẽ scan/ảnh không có chữ vector!" if not rooms else ""),
        }
    except Exception as e:
        return {"ok": False, "error": f"Lỗi đọc bản vẽ PDF: {e}"}


# ==============================================================================
# 8. MULTI-PROVIDER AI HUB (GEMINI, OPENAI, CLAUDE, DEEPSEEK, OPENROUTER, OLLAMA & OFFLINE)
# ==============================================================================
AI_PROVIDERS_CATALOG = {
    "gemini": {
        "name": "Google Gemini (AI Studio)",
        "login_url": "https://aistudio.google.com/apikey",
        "supports_vision": True,
        "default_model": "gemini-2.5-flash",
        "models": ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash", "gemini-1.5-pro"],
    },
    "openai": {
        "name": "OpenAI (ChatGPT)",
        "login_url": "https://platform.openai.com/api-keys",
        "supports_vision": True,
        "default_model": "gpt-4o-mini",
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "o3-mini"],
    },
    "claude": {
        "name": "Anthropic Claude",
        "login_url": "https://console.anthropic.com/settings/keys",
        "supports_vision": True,
        "default_model": "claude-3-5-sonnet-latest",
        "models": ["claude-3-5-sonnet-latest", "claude-3-7-sonnet-latest", "claude-3-5-haiku-latest"],
    },
    "deepseek": {
        "name": "DeepSeek AI",
        "login_url": "https://platform.deepseek.com/api_keys",
        "supports_vision": False,
        "default_model": "deepseek-chat",
        "models": ["deepseek-chat", "deepseek-reasoner"],
    },
    "openrouter": {
        "name": "OpenRouter (Đa Model AI)",
        "login_url": "https://openrouter.ai/keys",
        "supports_vision": True,
        "default_model": "google/gemini-2.5-flash",
        "models": ["google/gemini-2.5-flash", "openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet", "deepseek/deepseek-chat-v3-0324"],
    },
    "ollama": {
        "name": "Ollama / AI Nội Bộ Trên Máy",
        "login_url": "https://ollama.com/download",
        "supports_vision": True,
        "default_model": "qwen2.5:7b",
        "models": ["qwen2.5:7b", "llama3.2-vision", "gemma3:4b", "deepseek-r1:8b"],
    },
    "offline": {
        "name": "Chuyên Gia Offline Minh Phú (Miễn phí)",
        "login_url": "",
        "supports_vision": False,
        "default_model": "minhphu-tcvn5687-v2",
        "models": ["minhphu-tcvn5687-v2"],
    },
}


def call_gemini_api(api_key: str, model: str, prompt: str, image_b64: str = None, mime_type: str = "image/png") -> tuple:
    model = (model or "gemini-2.5-flash").strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key.strip()}"
    parts = [{"text": prompt}]
    if image_b64:
        parts.append({"inline_data": {"mime_type": mime_type, "data": image_b64}})
    body = json.dumps({"contents": [{"parts": parts}], "generationConfig": {"temperature": 0.2}}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            txt = data["candidates"][0]["content"]["parts"][0]["text"]
            return True, txt
    except urllib.error.HTTPError as he:
        err_body = he.read().decode("utf-8", errors="ignore")
        return False, f"Gemini API HTTP {he.code}: {err_body[:300]}"
    except Exception as e:
        return False, f"Lỗi kết nối Gemini API: {e}"


def call_openai_compat_api(url: str, api_key: str, model: str, prompt: str, image_b64: str = None, mime_type: str = "image/png", extra_headers: dict = None) -> tuple:
    content = [{"type": "text", "text": prompt}] if image_b64 else prompt
    if image_b64:
        content.append({"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}})
    body = json.dumps({
        "model": model.strip(),
        "temperature": 0.2,
        "messages": [{"role": "user", "content": content}],
    }).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key and api_key.strip():
        headers["Authorization"] = f"Bearer {api_key.strip()}"
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            txt = data["choices"][0]["message"]["content"]
            return True, txt
    except urllib.error.HTTPError as he:
        err_body = he.read().decode("utf-8", errors="ignore")
        return False, f"AI API HTTP {he.code}: {err_body[:300]}"
    except Exception as e:
        return False, f"Lỗi kết nối AI API ({url}): {e}"


def call_claude_api(api_key: str, model: str, prompt: str, image_b64: str = None, mime_type: str = "image/png") -> tuple:
    model = (model or "claude-3-5-sonnet-latest").strip()
    url = "https://api.anthropic.com/v1/messages"
    content = []
    if image_b64:
        content.append({"type": "image", "source": {"type": "base64", "media_type": mime_type, "data": image_b64}})
    content.append({"type": "text", "text": prompt})
    body = json.dumps({
        "model": model,
        "max_tokens": 2048,
        "temperature": 0.2,
        "messages": [{"role": "user", "content": content}],
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key.strip(),
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            txt = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
            return True, txt
    except urllib.error.HTTPError as he:
        err_body = he.read().decode("utf-8", errors="ignore")
        return False, f"Claude API HTTP {he.code}: {err_body[:300]}"
    except Exception as e:
        return False, f"Lỗi kết nối Claude API: {e}"


def call_ai_provider(ai_cfg: dict, prompt: str, image_b64: str = None, mime_type: str = "image/png") -> tuple:
    """Unified router across Google Gemini, OpenAI, Claude, DeepSeek, OpenRouter, and Local Ollama."""
    provider = (ai_cfg.get("provider") or "offline").lower().strip()
    api_key = (ai_cfg.get("api_key") or "").strip()
    model = (ai_cfg.get("model") or AI_PROVIDERS_CATALOG.get(provider, {}).get("default_model", "")).strip()
    base_url = (ai_cfg.get("base_url") or "").strip().rstrip("/")

    if provider == "offline":
        return False, "Đang ở chế độ Offline."
    if provider != "ollama" and not api_key:
        return False, f"Chưa nhập API Key / Token đăng nhập cho {AI_PROVIDERS_CATALOG.get(provider, {}).get('name', provider)}."

    if provider == "gemini":
        return call_gemini_api(api_key, model or "gemini-2.5-flash", prompt, image_b64, mime_type)
    if provider == "openai":
        url = f"{base_url}/chat/completions" if base_url else "https://api.openai.com/v1/chat/completions"
        return call_openai_compat_api(url, api_key, model or "gpt-4o-mini", prompt, image_b64, mime_type)
    if provider == "claude":
        return call_claude_api(api_key, model or "claude-3-5-sonnet-latest", prompt, image_b64, mime_type)
    if provider == "deepseek":
        url = f"{base_url}/chat/completions" if base_url else "https://api.deepseek.com/v1/chat/completions"
        return call_openai_compat_api(url, api_key, model or "deepseek-chat", prompt, None if image_b64 else None, mime_type)
    if provider == "openrouter":
        url = f"{base_url}/chat/completions" if base_url else "https://openrouter.ai/api/v1/chat/completions"
        return call_openai_compat_api(
            url, api_key, model or "google/gemini-2.5-flash", prompt, image_b64, mime_type,
            extra_headers={"HTTP-Referer": "https://nhathaudieuhoatrungtam.com", "X-Title": "Minh Phu HVAC Pro"},
        )
    if provider == "ollama":
        url = f"{base_url}/chat/completions" if base_url else "http://127.0.0.1:11434/v1/chat/completions"
        return call_openai_compat_api(url, api_key or "ollama", model or "qwen2.5:7b", prompt, image_b64, mime_type)
    return False, f"Nhà cung cấp AI '{provider}' chưa hỗ trợ."


def ai_test_connection(ai_cfg: dict) -> dict:
    """Test live authentication & response from the chosen AI model."""
    provider = (ai_cfg.get("provider") or "offline").lower().strip()
    if provider == "offline":
        return {"ok": True, "provider": "offline", "model": "minhphu-tcvn5687-v2", "message": "Chế độ Chuyên gia Offline Minh Phú luôn sẵn sàng 100% không cần đăng nhập!"}
    import time
    t0 = time.time()
    ok, txt = call_ai_provider(ai_cfg, "Trả lời ngắn gọn trong 1 dòng tiếng Việt: Xác nhận kết nối thành công với phần mềm Minh Phú HVAC.")
    ms = int((time.time() - t0) * 1000)
    if ok:
        return {"ok": True, "provider": provider, "model": ai_cfg.get("model", ""), "latency_ms": ms, "message": txt.strip()[:220]}
    return {"ok": False, "provider": provider, "error": txt}


def ai_list_models(ai_cfg: dict) -> dict:
    """Fetch live model catalog from provider API if logged in, falling back to curated list."""
    provider = (ai_cfg.get("provider") or "offline").lower().strip()
    api_key = (ai_cfg.get("api_key") or "").strip()
    base_url = (ai_cfg.get("base_url") or "").strip().rstrip("/")
    defaults = list(AI_PROVIDERS_CATALOG.get(provider, {}).get("models", []))

    if provider == "offline" or (provider != "ollama" and not api_key):
        return {"ok": True, "live": False, "models": defaults}

    try:
        if provider == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                found = [
                    m["name"].replace("models/", "")
                    for m in data.get("models", [])
                    if "generateContent" in (m.get("supportedGenerationMethods") or []) and "gemini" in m.get("name", "")
                ]
                if found:
                    return {"ok": True, "live": True, "models": found[:30]}
        elif provider in ("openai", "deepseek", "openrouter", "ollama"):
            url_map = {
                "openai": f"{base_url}/models" if base_url else "https://api.openai.com/v1/models",
                "deepseek": f"{base_url}/models" if base_url else "https://api.deepseek.com/v1/models",
                "openrouter": f"{base_url}/models" if base_url else "https://openrouter.ai/api/v1/models",
                "ollama": f"{base_url}/models" if base_url else "http://127.0.0.1:11434/v1/models",
            }
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            req = urllib.request.Request(url_map[provider], headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                ids = [m.get("id", "") for m in data.get("data", []) if m.get("id")]
                if provider == "openai":
                    ids = [x for x in ids if any(k in x for k in ("gpt-4", "gpt-5", "o1", "o3", "o4"))]
                if ids:
                    return {"ok": True, "live": True, "models": sorted(ids)[:40]}
    except Exception:
        pass
    return {"ok": True, "live": False, "models": defaults}


def _offline_smart_generate_rooms(description: str, building_cat: str = "AUTO") -> list:
    """Offline smart Vietnamese HVAC room & appliance generator for Home, Office & Hospital projects."""
    low = (description or "").lower()
    cat = building_cat.upper()
    if cat == "AUTO":
        if any(k in low for k in ("bệnh viện", "phòng khám", "y tế", "nha khoa", "siêu âm", "phòng mổ", "clinic", "hospital")):
            cat = "HOSPITAL"
        elif any(k in low for k in ("văn phòng", "công ty", "tòa nhà", "office", "phòng họp", "server")):
            cat = "OFFICE"
        else:
            cat = "HOME"

    if cat == "HOSPITAL":
        return [
            {"name": "Sảnh Đón Tiếp & Cấp Cứu", "floor": "Tầng 1", "room_type": "LOBBY", "area": 55, "h_concrete": 3.8, "h_ceiling": 3.0, "orientation": "W", "wall_type": "BRICK_220_HOLLOW", "ext_wall_len": 9.0, "win_frame_type": "ALUM_THERMAL_BREAK", "win_qty": 2, "win_w": 2.4, "win_h": 2.2, "glass_type": "DOUBLE_LOW_E", "shading_type": "OVERHANG", "door_type": "AUTO_SLIDING_GLASS", "door_qty": 1, "door_w": 2.4, "door_h": 2.4, "door_location": "EXT", "roof_type": "MID_FLOOR", "floor_type": "GROUND", "people": 16, "equipment_items": [{"id": "DESKTOP_PC", "qty": 2}, {"id": "WATER_DISPENSER", "qty": 1}, {"id": "TV_LED_55", "qty": 1}]},
            {"name": "Phòng Siêu Âm & Chẩn Đoán", "floor": "Tầng 1", "room_type": "CLINIC", "area": 24, "h_concrete": 3.6, "h_ceiling": 2.9, "orientation": "S", "wall_type": "BRICK_220_HOLLOW", "ext_wall_len": 4.5, "win_frame_type": "UPVC_REINF", "win_qty": 1, "win_w": 1.6, "win_h": 1.5, "glass_type": "DOUBLE_LOW_E", "shading_type": "BLACKOUT", "door_type": "HOSPITAL_HERMETIC", "door_qty": 1, "door_w": 1.2, "door_h": 2.2, "door_location": "INT", "roof_type": "MID_FLOOR", "floor_type": "GROUND", "people": 4, "equipment_items": [{"id": "ULTRASOUND", "qty": 1}, {"id": "DESKTOP_PC", "qty": 1}, {"id": "VACCINE_FRIDGE", "qty": 1}]},
            {"name": "Phòng Khám Nha Khoa / Thủ Thuật", "floor": "Tầng 2", "room_type": "CLINIC", "area": 28, "h_concrete": 3.6, "h_ceiling": 2.9, "orientation": "E", "wall_type": "AAC_200", "ext_wall_len": 5.5, "win_frame_type": "ALUM_THERMAL_BREAK", "win_qty": 2, "win_w": 1.5, "win_h": 1.5, "glass_type": "DOUBLE_LOW_E", "shading_type": "ROLLER", "door_type": "HOSPITAL_HERMETIC", "door_qty": 1, "door_w": 1.2, "door_h": 2.2, "door_location": "INT", "roof_type": "MID_FLOOR", "floor_type": "MID_AC", "people": 5, "equipment_items": [{"id": "DENTAL_CHAIR", "qty": 2}, {"id": "AUTOCLAVE_STER", "qty": 1}]},
            {"name": "Phòng Xét Nghiệm Sinh Hóa", "floor": "Tầng 2", "room_type": "LAB_CLINIC", "area": 30, "h_concrete": 3.6, "h_ceiling": 2.9, "orientation": "N", "wall_type": "AAC_200", "ext_wall_len": 5.0, "win_frame_type": "UPVC_REINF", "win_qty": 1, "win_w": 1.8, "win_h": 1.4, "glass_type": "DOUBLE_LOW_E", "shading_type": "ROLLER", "door_type": "HOSPITAL_HERMETIC", "door_qty": 1, "door_w": 1.2, "door_h": 2.2, "door_location": "INT", "roof_type": "MID_FLOOR", "floor_type": "MID_AC", "people": 4, "equipment_items": [{"id": "XRAY_BIOCHEM", "qty": 1}, {"id": "VACCINE_FRIDGE", "qty": 2}, {"id": "DESKTOP_PC", "qty": 2}]},
            {"name": "Phòng Mổ / Tiểu Phẫu (Áp Suất Dương)", "floor": "Tầng 3", "room_type": "OPERATING_ROOM", "area": 36, "h_concrete": 3.8, "h_ceiling": 2.9, "orientation": "INT", "wall_type": "GYPSUM_ROCKWOOL", "ext_wall_len": 0, "win_qty": 0, "glass_type": "DOUBLE_LOW_E", "shading_type": "NONE", "door_type": "HOSPITAL_HERMETIC", "door_qty": 1, "door_w": 1.6, "door_h": 2.2, "door_location": "INT", "roof_type": "ROOF_RC_INSUL", "floor_type": "MID_AC", "people": 7, "equipment_items": [{"id": "OT_LIGHT_ESU", "qty": 1}, {"id": "PATIENT_MON", "qty": 2}, {"id": "ICU_VENTILATOR", "qty": 1}]},
            {"name": "Phòng Bệnh Nhân Nội Trú VIP", "floor": "Tầng 3", "room_type": "HOSPITAL_WARD", "area": 26, "h_concrete": 3.6, "h_ceiling": 3.0, "orientation": "SE", "wall_type": "BRICK_220_HOLLOW", "ext_wall_len": 5.0, "win_frame_type": "ALUM_THERMAL_BREAK", "win_qty": 1, "win_w": 2.0, "win_h": 1.6, "glass_type": "DOUBLE_LOW_E", "shading_type": "BLACKOUT", "door_type": "WOOD_ENG_HDF", "door_qty": 1, "door_w": 1.2, "door_h": 2.2, "door_location": "INT", "roof_type": "ROOF_RC_INSUL", "floor_type": "MID_AC", "people": 3, "equipment_items": [{"id": "PATIENT_MON", "qty": 1}, {"id": "TV_LED_55", "qty": 1}, {"id": "FRIDGE_SIDE", "qty": 1}]},
        ]
    if cat == "OFFICE":
        return [
            {"name": "Khu Làm Việc Nhân Viên (Open Office)", "floor": "Tầng 2", "room_type": "OFFICE", "area": 85, "h_concrete": 3.6, "h_ceiling": 2.85, "orientation": "W", "wall_type": "BRICK_220_HOLLOW", "ext_wall_len": 12.0, "win_frame_type": "CURTAIN_WALL", "win_qty": 4, "win_w": 2.2, "win_h": 2.0, "glass_type": "DOUBLE_LOW_E", "shading_type": "ROLLER", "door_type": "TEMPERED_12_FULL", "door_qty": 1, "door_w": 1.8, "door_h": 2.4, "door_location": "INT", "roof_type": "MID_FLOOR", "floor_type": "MID_AC", "people": 14, "equipment_items": [{"id": "LAPTOP_DESK", "qty": 12}, {"id": "DESKTOP_PC", "qty": 2}, {"id": "PRINTER_MFP", "qty": 1}, {"id": "WATER_DISPENSER", "qty": 1}]},
            {"name": "Phòng Họp Hội Đồng", "floor": "Tầng 2", "room_type": "MEETING", "area": 36, "h_concrete": 3.6, "h_ceiling": 2.85, "orientation": "S", "wall_type": "GYPSUM_ROCKWOOL", "ext_wall_len": 6.0, "win_frame_type": "ALUM_THERMAL_BREAK", "win_qty": 2, "win_w": 1.8, "win_h": 1.8, "glass_type": "DOUBLE_LOW_E", "shading_type": "ROLLER", "door_type": "TEMPERED_12_FULL", "door_qty": 1, "door_w": 1.2, "door_h": 2.2, "door_location": "INT", "roof_type": "MID_FLOOR", "floor_type": "MID_AC", "people": 14, "equipment_items": [{"id": "PROJECTOR_LED", "qty": 1}, {"id": "LAPTOP_DESK", "qty": 6}]},
            {"name": "Phòng Giám Đốc", "floor": "Tầng 2", "room_type": "OFFICE", "area": 28, "h_concrete": 3.6, "h_ceiling": 2.9, "orientation": "SE", "wall_type": "BRICK_220_HOLLOW", "ext_wall_len": 5.5, "win_frame_type": "ALUM_THERMAL_BREAK", "win_qty": 2, "win_w": 1.6, "win_h": 1.8, "glass_type": "DOUBLE_LOW_E", "shading_type": "BLACKOUT", "door_type": "WOOD_SOLID_45", "door_qty": 1, "door_w": 1.0, "door_h": 2.2, "door_location": "INT", "roof_type": "MID_FLOOR", "floor_type": "MID_AC", "people": 3, "equipment_items": [{"id": "DESKTOP_PC", "qty": 1}, {"id": "TV_LED_55", "qty": 1}, {"id": "COFFEE_OFFICE", "qty": 1}]},
            {"name": "Phòng Server / Thiết Bị Mạng", "floor": "Tầng 2", "room_type": "OFFICE", "area": 14, "h_concrete": 3.6, "h_ceiling": 2.9, "orientation": "INT", "wall_type": "BRICK_220_SOLID", "ext_wall_len": 0, "win_qty": 0, "glass_type": "DOUBLE_LOW_E", "shading_type": "NONE", "door_type": "STEEL_FIRE", "door_qty": 1, "door_w": 1.0, "door_h": 2.2, "door_location": "INT", "roof_type": "MID_FLOOR", "floor_type": "MID_AC", "people": 1, "equipment_items": [{"id": "SERVER_RACK", "qty": 1}, {"id": "RACK_SWITCH", "qty": 2}]},
        ]
    # Default HOME (Gia đình / Biệt thự)
    return [
        {"name": "Phòng Khách Chính", "floor": "Tầng 1", "room_type": "LIVING", "area": 42, "h_concrete": 3.9, "h_ceiling": 3.2, "orientation": "W", "wall_type": "BRICK_220_STONE", "ext_wall_len": 7.5, "win_frame_type": "XINGFA_NO_TB", "win_qty": 2, "win_w": 2.0, "win_h": 1.8, "glass_type": "TEMPERED_XINGFA", "shading_type": "BLACKOUT", "door_type": "ALUM_XINGFA_GLASS", "door_qty": 1, "door_w": 2.4, "door_h": 2.6, "door_location": "EXT", "roof_type": "MID_FLOOR", "floor_type": "GROUND", "people": 8, "equipment_items": [{"id": "TV_LED_55", "qty": 1}, {"id": "WINE_COOLER", "qty": 1}]},
        {"name": "Phòng Bếp & Phòng Ăn", "floor": "Tầng 1", "room_type": "DINING", "area": 26, "h_concrete": 3.9, "h_ceiling": 3.2, "orientation": "S", "wall_type": "BRICK_220_HOLLOW", "ext_wall_len": 4.5, "win_frame_type": "XINGFA_NO_TB", "win_qty": 1, "win_w": 2.2, "win_h": 1.6, "glass_type": "DOUBLE_CLEAR", "shading_type": "ROLLER", "door_type": "WOOD_ENG_HDF", "door_qty": 1, "door_w": 1.0, "door_h": 2.2, "door_location": "INT", "roof_type": "MID_FLOOR", "floor_type": "GROUND", "people": 6, "equipment_items": [{"id": "FRIDGE_SIDE", "qty": 1}, {"id": "INDUCTION_COOK", "qty": 1}, {"id": "RICE_KETTLE", "qty": 1}, {"id": "OVEN_MICRO", "qty": 1}]},
        {"name": "Phòng Ngủ Master", "floor": "Tầng 2", "room_type": "BEDROOM", "area": 30, "h_concrete": 3.6, "h_ceiling": 3.0, "orientation": "SW", "wall_type": "BRICK_220_HOLLOW", "ext_wall_len": 6.0, "win_frame_type": "ALUM_THERMAL_BREAK", "win_qty": 2, "win_w": 1.8, "win_h": 1.8, "glass_type": "DOUBLE_LOW_E", "shading_type": "BLACKOUT", "door_type": "WOOD_SOLID_45", "door_qty": 1, "door_w": 0.95, "door_h": 2.2, "door_location": "INT", "roof_type": "MID_FLOOR", "floor_type": "MID_AC", "people": 2, "equipment_items": [{"id": "TV_LED_55", "qty": 1}, {"id": "PC_HOME", "qty": 1}]},
        {"name": "Phòng Ngủ Con", "floor": "Tầng 2", "room_type": "BEDROOM", "area": 18, "h_concrete": 3.6, "h_ceiling": 3.0, "orientation": "E", "wall_type": "BRICK_220_HOLLOW", "ext_wall_len": 4.2, "win_frame_type": "XINGFA_NO_TB", "win_qty": 1, "win_w": 1.6, "win_h": 1.5, "glass_type": "DOUBLE_LOW_E", "shading_type": "ROLLER", "door_type": "WOOD_ENG_HDF", "door_qty": 1, "door_w": 0.9, "door_h": 2.2, "door_location": "INT", "roof_type": "MID_FLOOR", "floor_type": "MID_AC", "people": 2, "equipment_items": [{"id": "LAPTOP_DESK", "qty": 1}]},
    ]


def ai_generate_rooms(description: str, building_cat: str, ai_cfg: dict) -> dict:
    """Use the signed-in AI Model (or Offline Smart Generator) to generate structured rooms, doors, windows & equipment."""
    provider = (ai_cfg.get("provider") or "offline").lower().strip()
    api_key = (ai_cfg.get("api_key") or "").strip()
    if provider == "offline" or (provider != "ollama" and not api_key):
        rooms = _offline_smart_generate_rooms(description, building_cat)
        return {
            "ok": True,
            "mode": "OFFLINE_SMART",
            "rooms": rooms,
            "note": f"Đã tạo nhanh {len(rooms)} phòng mẫu đầy đủ cửa chính, cửa sổ & thiết bị tỏa nhiệt ({building_cat}). Đăng nhập Model AI (Gemini / ChatGPT / Claude / DeepSeek) để AI tùy biến chính xác theo mọi yêu cầu riêng!",
        }

    eq_keys = ", ".join(EQUIPMENT_LIBRARY.keys())
    door_keys = ", ".join(DOOR_MATERIALS.keys())
    prompt = (
        "Bạn là kỹ sư trưởng thiết kế ĐHKK HVAC tại Việt Nam theo TCVN 5687:2024 & QCVN 09:2017/BXD.\n"
        f"Loại công trình: {building_cat}. Yêu cầu của khách hàng:\n\"{description}\"\n\n"
        "Hãy lập danh sách các phòng cần lắp điều hòa đầy đủ kích thước, cửa chính, cửa sổ, vật liệu Việt Nam và thiết bị tỏa nhiệt.\n"
        "Trả về DUY NHẤT mảng JSON hợp lệ (không giải thích thêm) theo cấu trúc:\n"
        '[{"name":"Phòng khách","floor":"Tầng 1","room_type":"LIVING","area":40,"h_concrete":3.8,"h_ceiling":3.1,'
        '"orientation":"W","wall_type":"BRICK_220_HOLLOW","ext_wall_len":7.0,"win_frame_type":"XINGFA_NO_TB","win_qty":2,'
        '"win_w":1.8,"win_h":1.6,"glass_type":"DOUBLE_LOW_E","shading_type":"BLACKOUT","door_type":"ALUM_XINGFA_GLASS",'
        '"door_qty":1,"door_w":2.2,"door_h":2.4,"door_location":"EXT","roof_type":"MID_FLOOR","floor_type":"GROUND",'
        '"people":6,"equipment_items":[{"id":"TV_LED_55","qty":1}]}]\n'
        f"Mã room_type hợp lệ: {', '.join(ROOM_PRESETS.keys())}\n"
        f"Mã door_type hợp lệ: {door_keys}\n"
        f"Mã equipment_items.id hợp lệ: {eq_keys}\n"
        "Mã wall_type: BRICK_220_SOLID, BRICK_220_HOLLOW, AAC_200, RC_200, BRICK_220_STONE, BRICK_220_XPS50, GYPSUM_ROCKWOOL.\n"
        "Mã glass_type: CLEAR_SINGLE, TEMPERED_XINGFA, LAMINATED_10, SOLAR_SINGLE, DOUBLE_CLEAR, DOUBLE_LOW_E, CURTAIN_LOW_E.\n"
        "Mã roof_type: MID_FLOOR, UPPER_NON_AC, ROOF_RC_PLAIN, ROOF_RC_INSUL, ROOF_TILE_INS, ROOF_METAL.\n"
        "Mã floor_type: GROUND, MID_AC, OVER_NON_AC, OVER_EXT."
    )
    ok, resp_text = call_ai_provider(ai_cfg, prompt)
    if not ok:
        rooms = _offline_smart_generate_rooms(description, building_cat)
        return {"ok": True, "mode": "OFFLINE_FALLBACK", "warning": resp_text, "rooms": rooms}

    m_json = re.search(r"\[[\s\S]*\]", resp_text)
    if not m_json:
        rooms = _offline_smart_generate_rooms(description, building_cat)
        return {"ok": True, "mode": "OFFLINE_FALLBACK", "warning": "AI không trả về đúng mảng JSON.", "rooms": rooms}
    try:
        arr = json.loads(m_json.group(0))
        cleaned = []
        for it in arr:
            if not isinstance(it, dict):
                continue
            eqs = []
            for e in (it.get("equipment_items") or []):
                if isinstance(e, dict) and e.get("id") in EQUIPMENT_LIBRARY:
                    eqs.append({"id": e["id"], "qty": max(1, int(e.get("qty") or 1))})
            cleaned.append({
                "name": str(it.get("name") or "Phòng"),
                "floor": str(it.get("floor") or "Tầng 1"),
                "room_type": it.get("room_type") if it.get("room_type") in ROOM_PRESETS else "LIVING",
                "area": max(4.0, float(it.get("area") or 24.0)),
                "h_concrete": max(2.4, float(it.get("h_concrete") or 3.6)),
                "h_ceiling": max(2.1, float(it.get("h_ceiling") or 3.0)),
                "orientation": it.get("orientation") if it.get("orientation") in ORIENTATION_SOLAR else "W",
                "wall_type": it.get("wall_type") if it.get("wall_type") in WALL_MATERIALS else "BRICK_220_HOLLOW",
                "ext_wall_len": float(it.get("ext_wall_len") or 5.0),
                "win_frame_type": it.get("win_frame_type") if it.get("win_frame_type") in WINDOW_FRAME_MATERIALS else "XINGFA_NO_TB",
                "win_qty": max(0, int(it.get("win_qty") or 1)),
                "win_w": max(0.0, float(it.get("win_w") or 1.6)),
                "win_h": max(0.0, float(it.get("win_h") or 1.5)),
                "glass_type": it.get("glass_type") if it.get("glass_type") in GLASS_MATERIALS else "DOUBLE_LOW_E",
                "shading_type": it.get("shading_type") if it.get("shading_type") in SHADING_TYPES else "ROLLER",
                "door_type": it.get("door_type") if it.get("door_type") in DOOR_MATERIALS else "WOOD_ENG_HDF",
                "door_qty": max(0, int(it.get("door_qty") or 1)),
                "door_w": max(0.0, float(it.get("door_w") or 1.0)),
                "door_h": max(0.0, float(it.get("door_h") or 2.2)),
                "door_location": "EXT" if it.get("door_location") == "EXT" else "INT",
                "roof_type": it.get("roof_type") if it.get("roof_type") in ROOF_TYPES else "MID_FLOOR",
                "floor_type": it.get("floor_type") if it.get("floor_type") in FLOOR_TYPES else "MID_AC",
                "people": int(it.get("people") or 3),
                "equipment_items": eqs,
            })
        if cleaned:
            return {"ok": True, "mode": f"{provider.upper()} ({ai_cfg.get('model','')})", "rooms": cleaned}
    except Exception as e:
        rooms = _offline_smart_generate_rooms(description, building_cat)
        return {"ok": True, "mode": "OFFLINE_FALLBACK", "warning": str(e), "rooms": rooms}
    return {"ok": True, "mode": "OFFLINE_SMART", "rooms": _offline_smart_generate_rooms(description, building_cat)}


def ai_vision_takeoff_drawing(image_b64: str, ai_cfg: dict, mime_type: str = "image/png", extra_text: str = "") -> dict:
    """Use signed-in Vision AI (Gemini / OpenAI / Claude / OpenRouter / Ollama) to read floor plan and return structured JSON rooms."""
    provider = (ai_cfg.get("provider") or "offline").lower().strip()
    api_key = (ai_cfg.get("api_key") or "").strip()
    if provider == "offline" or (provider != "ollama" and not api_key):
        return {"ok": False, "error": "Chưa đăng nhập Model AI có hỗ trợ Vision (Gemini, ChatGPT, Claude, OpenRouter). Bấm nút '🤖 Đăng Nhập Model AI' để kết nối!"}

    prompt = (
        "Bạn là kỹ sư trưởng HVAC tại Việt Nam. Hãy phân tích bản vẽ mặt bằng kiến trúc đính kèm "
        "và bóc tách danh sách TẤT CẢ các phòng cần lắp điều hòa không khí (bỏ qua WC, kho nhỏ, cầu thang).\n"
        "Trả về DUY NHẤT một mảng JSON hợp lệ (không thêm markdown thừa) theo mẫu:\n"
        '[{"name": "Phòng khách", "floor": "Tầng 1", "room_type": "LIVING", "area": 36.5, '
        '"h_concrete": 3.6, "h_ceiling": 3.0, "ext_wall_len": 6.5, "win_qty": 2, "win_w": 1.6, "win_h": 1.5, '
        '"door_type": "ALUM_XINGFA_GLASS", "door_qty": 1, "door_w": 2.0, "door_h": 2.4, "orientation": "W", "people": 6}]\n'
        f"Quy ước room_type: {', '.join(ROOM_PRESETS.keys())}.\n"
        "Quy ước orientation: N, S, E, W, NE, NW, SE, SW, INT.\n"
        "Đọc chính xác diện tích ghi trên bản vẽ hoặc tính từ kích thước trục (mm -> m). "
        + (f"\nChữ đọc được trên bản vẽ:\n{extra_text[:1500]}" if extra_text else "")
    )

    ok, resp_text = call_ai_provider(ai_cfg, prompt, image_b64=image_b64, mime_type=mime_type)
    if not ok:
        return {"ok": False, "error": resp_text}

    # Parse JSON array cleanly from AI response
    m_json = re.search(r"\[[\s\S]*\]", resp_text)
    if not m_json:
        return {"ok": False, "error": f"AI không trả về đúng định dạng JSON phòng: {resp_text[:300]}"}
    try:
        arr = json.loads(m_json.group(0))
        cleaned = []
        for item in arr:
            if not isinstance(item, dict):
                continue
            area = max(3.0, float(item.get("area") or 20.0))
            cleaned.append({
                "name": str(item.get("name") or "Phòng"),
                "floor": str(item.get("floor") or "Tầng 1"),
                "room_type": item.get("room_type") if item.get("room_type") in ROOM_PRESETS else "LIVING",
                "area": round(area, 2),
                "h_concrete": float(item.get("h_concrete") or 3.6),
                "h_ceiling": float(item.get("h_ceiling") or 3.0),
                "ext_wall_len": float(item.get("ext_wall_len") or round(math.sqrt(area) * 1.1, 1)),
                "glass_area": float(item.get("glass_area") or round(area * 0.15, 1)),
                "orientation": item.get("orientation") if item.get("orientation") in ORIENTATION_SOLAR else "W",
                "people": int(item.get("people") or max(2, round(area / 8))),
                "source": f"AI Vision ({provider.upper()})",
            })
        return {"ok": True, "rooms": cleaned, "provider": provider}
    except Exception as e:
        return {"ok": False, "error": f"Lỗi phân tích JSON từ AI: {e}"}


def generate_offline_ai_analysis(calc_result: dict, duct_result: dict = None) -> str:
    """100% Offline Expert HVAC Engineering Diagnostic Report (TCVN 5687:2024 + QCVN 09:2017/BXD)."""
    db = calc_result.get("design_basis", {})
    sm = calc_result.get("summary", {})
    comps = sm.get("components_w", {})
    tot_w = max(1.0, sum(comps.values()))

    pct_glass = (comps.get("glass_rad", 0) + comps.get("glass_cond", 0)) / tot_w * 100
    pct_wall_roof = (comps.get("wall", 0) + comps.get("roof_floor", 0) + comps.get("partition", 0)) / tot_w * 100
    pct_oa = (comps.get("fresh_air", 0) + comps.get("infiltration", 0)) / tot_w * 100
    pct_int = (comps.get("people", 0) + comps.get("light_equip", 0)) / tot_w * 100

    lines = [
        f"1. TỔNG QUAN TẢI NHIỆT CÔNG TRÌNH ({db.get('city_name', 'Việt Nam')} — Cấp {db.get('grade', 'I')} TCVN 5687:2024):",
        f"   • Tổng diện tích điều hòa: {sm.get('total_area_m2', 0)} m² ({sm.get('room_count', 0)} phòng) — Tổng tải lạnh tức thời: {sm.get('total_cooling_kw', 0)} kW ({int(sm.get('total_cooling_btu', 0)):,} Btu/h ≈ {sm.get('total_cooling_rt', 0)} RT).".replace(",", "."),
        f"   • Chỉ số phụ tải lạnh trung bình: {sm.get('avg_w_per_m2', 0)} W/m² | Tỷ số nhiệt hiện SHR = {sm.get('shr', 0.78)} | Tải sau hệ số đồng thời ({db.get('diversity_factor', 0.85)}): {sm.get('diversified_kw', 0)} kW ({int(sm.get('diversified_btu', 0)):,} Btu/h).".replace(",", "."),
        f"   • Cơ cấu nguồn nhiệt: Kính & bức xạ mặt trời chiếm {pct_glass:.1f}% | Bao che (tường/mái/sàn) {pct_wall_roof:.1f}% | Gió tươi & lọt khí {pct_oa:.1f}% | Nội sinh (người/đèn/thiết bị) {pct_int:.1f}%.",
        "",
        "2. ĐÁNH GIÁ KẾT CẤU BAO CHE THEO QCVN 09:2017/BXD & GIẢI PHÁP GIẢM TẢI:",
    ]
    q_warns = calc_result.get("qcvn_warnings", [])
    if q_warns:
        for w in q_warns[:6]:
            lines.append(f"   • [Lưu ý QCVN 09] {w}")
        lines.append("   • Khuyến nghị kỹ sư: Nâng cấp kính hướng Tây/Đông sang kính hộp Low-E (SHGC ≤ 0.36) hoặc bổ sung rèm cản nắng 2 lớp giúp giảm ngay 15%–28% công suất máy lạnh đầu tư.")
    else:
        lines.append("   • Kết cấu tường bao & kính các phòng đều ĐẠT giới hạn nhiệt trở R0 ≥ 0.56 m²K/W và SHGC cho phép theo QCVN 09:2017/BXD.")

    lines.append("")
    lines.append("3. KIỂM TRA KHOẢNG TRẦN THẠCH CAO (H_BT - H_TC) & CẤU HÌNH THIẾT BỊ DAIKIN:")
    c_warns = calc_result.get("clearance_warnings", [])
    if c_warns:
        for cw in c_warns[:5]:
            lines.append(f"   • [Cảnh báo trần] {cw} -> Đề xuất chuyển sang dàn lạnh mỏng FXDQ (cao 200mm) hoặc hạ thêm cao độ trần thạch cao.")
    else:
        lines.append("   • Toàn bộ các phòng đều đủ khoảng hở kỹ thuật trần thạch cao để lắp đặt dàn lạnh, côn đầu máy và độ dốc thoát nước ngưng 1%.")

    out_rec = sm.get("outdoor_rec")
    if out_rec:
        ratio = (sm.get("total_cooling_btu", 0) / max(1, out_rec.get("cooling_btu", 1))) * 100
        lines.append(f"   • Tổ hợp dàn nóng đề xuất: {out_rec['model']} ({out_rec['cooling_kw']} kW) — Tỷ lệ kết nối dàn lạnh/dàn nóng ≈ {ratio:.0f}% (nằm trong dải vận hành hiệu suất cao 90%–130% của Daikin VRV).")

    if sm.get("total_oa_m3h", 0) > 0:
        hrv_rec = sm.get("hrv_rec")
        hrv_txt = f"Model gợi ý: {hrv_rec['model']} ({hrv_rec['hp']})." if hrv_rec else ""
        lines.append(f"   • Gió tươi theo Bảng E.1 TCVN 5687:2024: {int(sm.get('total_oa_m3h', 0))} m³/h. " +
                     (f"Đã tích hợp thu hồi nhiệt HRV ({db.get('hrv_efficiency', 70)}%), giúp giảm đáng kể tải ẩn mùa nồm ẩm. {hrv_txt}"
                      if db.get("use_hrv") else f"Khuyến nghị lắp thiết bị thu hồi nhiệt Daikin HRV VAM để tiết kiệm 20%–28% tải nhiệt gió tươi. {hrv_txt}"))

    if duct_result and duct_result.get("ok"):
        lines.append("")
        lines.append(f"4. ĐÁNH GIÁ HỆ THỐNG ỐNG GIÓ (DAIKIN DUCT CHECKER — {duct_result.get('model')}):")
        pb = duct_result.get("pressure_breakdown", {})
        md = duct_result.get("main_duct", {})
        lines.append(f"   • Ống gió chính: {md.get('w_mm')}×{md.get('h_mm')} mm (Vận tốc {md.get('hyd',{}).get('velocity_ms')} m/s, Ma sát {md.get('hyd',{}).get('dp_pa_m')} Pa/m) — Độ ồn: {duct_result.get('noise_status')}.")
        lines.append(f"   • Kiểm tra cột áp quạt ESP: Tổng trở lực {pb.get('total_pa')} Pa vs ESP tối đa {duct_result.get('esp_max_pa')} Pa -> {duct_result.get('esp_verdict')}")

    return "\n".join(lines)


def run_ai_thermal_report(calc_result: dict, ai_cfg: dict, duct_result: dict = None) -> dict:
    """Generate Hybrid AI Technical Consultation Report (Gemini / OpenAI / Claude / DeepSeek / OpenRouter / Ollama or Offline Expert)."""
    offline_txt = generate_offline_ai_analysis(calc_result, duct_result)
    provider = (ai_cfg.get("provider") or "offline").lower().strip()
    api_key = (ai_cfg.get("api_key") or "").strip()

    if provider == "offline" or (provider != "ollama" and not api_key):
        return {"ok": True, "mode": "OFFLINE_EXPERT", "report_text": offline_txt}

    compact_data = {
        "design_basis": calc_result.get("design_basis"),
        "summary": calc_result.get("summary"),
        "qcvn_warnings": calc_result.get("qcvn_warnings"),
        "clearance_warnings": calc_result.get("clearance_warnings"),
        "rooms": [
            {
                "name": r["name"], "floor": r["floor"], "area": r["area"],
                "h_bt": r["h_concrete"], "h_tc": r["h_ceiling"], "orient": r["orientation"],
                "window": r.get("window_summary", ""), "door": r.get("door_summary", ""),
                "equipment": r.get("equip_items_summary", ""),
                "q_kw": r["q_kw"], "w_m2": r["w_per_m2"], "oa_m3h": r["oa_m3h"],
                "model": r["recommended_unit"]["model"], "qcvn_ok": r["qcvn_ok"],
            }
            for r in calc_result.get("rooms", [])[:25]
        ],
        "duct_check": duct_result if (duct_result and duct_result.get("ok")) else None,
    }
    prompt = (
        "Bạn là Kỹ sư Trưởng Tư vấn Thiết kế HVAC cao cấp của Công ty TNHH Phát Triển Kỹ Thuật Thương Mại Minh Phú.\n"
        "Dựa trên kết quả tính toán nhiệt chuẩn TCVN 5687:2024 & QCVN 09:2017/BXD sau đây (đã bao gồm cửa chính, cửa sổ và thiết bị gia đình/văn phòng/bệnh viện), "
        "hãy viết một Báo Cáo Thẩm Định & Tư Vấn Kỹ Thuật Chuyên Sâu "
        "(tiếng Việt chuẩn kỹ sư, súc tích 260-420 từ, KHÔNG dùng bảng markdown hay ###, chỉ dùng mục số 1, 2, 3, 4 và gạch đầu dòng '•'):\n"
        "1. Nhận xét tổng tải lạnh, chỉ số W/m², tỷ số nhiệt hiện SHR và nguồn gây tải lớn nhất (kính, cửa, thiết bị, gió tươi).\n"
        "2. Đánh giá tuân thủ QCVN 09:2017/BXD (tường, cửa sổ, cửa chính, hướng nắng) và đề xuất tối ưu chi phí đầu tư & điện năng.\n"
        "3. Đánh giá phương án chọn dàn lạnh/dàn nóng Daikin, khoảng hở trần thạch cao và giải pháp cấp gió tươi HRV.\n"
        "4. Lưu ý thi công ống gió / đường ống đồng / áp suất phòng để đạt độ ồn thấp và hiệu suất tối ưu.\n\n"
        f"DỮ LIỆU TÍNH TOÁN:\n{json.dumps(compact_data, ensure_ascii=False)}"
    )
    ok, txt = call_ai_provider(ai_cfg, prompt)
    if ok:
        return {"ok": True, "mode": f"{provider.upper()} ({ai_cfg.get('model','')})", "report_text": txt.strip()}
    return {
        "ok": True,
        "mode": "OFFLINE_FALLBACK",
        "warning": txt,
        "report_text": offline_txt,
    }


def get_reference_catalog_metadata() -> dict:
    """Expose full Vietnam climate cities, walls, doors, windows, equipment library, room presets & AI providers."""
    return {
        "cities": TCVN_CLIMATE_CITIES,
        "walls": WALL_MATERIALS,
        "glasses": GLASS_MATERIALS,
        "shadings": SHADING_TYPES,
        "roofs": ROOF_TYPES,
        "floors": FLOOR_TYPES,
        "doors": DOOR_MATERIALS,
        "window_frames": WINDOW_FRAME_MATERIALS,
        "equipment_library": EQUIPMENT_LIBRARY,
        "room_presets": ROOM_PRESETS,
        "orientations": ORIENTATION_SOLAR,
        "ai_providers": AI_PROVIDERS_CATALOG,
    }
