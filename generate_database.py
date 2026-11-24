# -*- coding: utf-8 -*-
import json
import os

APP_DIR = r"H:\DAIKIN\MinhPhu_Daikin_App"

COMPANY_DEFAULT = {
    "name": "CÔNG TY TNHH PHÁT TRIỂN KỸ THUẬT THƯƠNG MẠI MINH PHÚ",
    "short_name": "ĐIỀU HÒA MINH PHÚ",
    "english_name": "MINH PHU COMMERCIAL AND TECHNICAL DEVELOPMENT CO., LTD",
    "slogan": "HOÀN TIỀN NẾU KHÔNG HÀI LÒNG",
    "tax_code": "0107709790",
    "representative": "Nguyễn Đình Can",
    "position": "Giám đốc",
    "address": "Số 05 ngõ 89 đường Lạc Long Quân, Phường Nghĩa Đô, Quận Cầu Giấy, TP. Hà Nội",
    "hotline": "0967 986 586",
    "email": "lienhe@nhathaudieuhoatrungtam.com",
    "website": "https://nhathaudieuhoatrungtam.com",
    "daikin_catalog_url": "https://www.daikincatalog.com/library/site/vietnam/book-lists/",
    "daikin_home_url": "https://www.daikin.com.vn/",
    "bank": {
        "bank_id": "MB",
        "bank_name": "Ngân hàng TMCP Quân Đội (MBBank)",
        "account_no": "0967986586",
        "account_name": "CONG TY TNHH PT KT TM MINH PHU",
        "template": "compact2",
        "note_prefix": "TT BAO GIA MINH PHU",
        "deposit_percent": 50,
        "custom_qr_data_url": ""
    },
    "quote_terms": [
        "1. Báo giá chưa bao gồm thuế GTGT (VAT) nếu không ghi chú khác ở phần tổng hợp.",
        "2. Thiết bị mới 100%, chính hãng Daikin, đầy đủ chứng nhận xuất xứ và chất lượng (CO, CQ).",
        "3. Bảo hành chính hãng Daikin: 01 năm cho toàn bộ thiết bị, 05 năm cho máy nén khí; Bảo hành phần thi công lắp đặt Minh Phú: 12 tháng.",
        "4. Tiến độ giao hàng & thi công: Trong vòng 03 - 07 ngày kể từ ngày ký hợp đồng và nhận tạm ứng.",
        "5. Phương thức thanh toán: Tạm ứng 50% ngay sau khi xác nhận đơn hàng, thanh toán 50% còn lại sau khi bàn giao nghiệm thu.",
        "6. Hiệu lực báo giá: 15 ngày kể từ ngày lập báo giá."
    ]
}

CATEGORIES = [
    {"id": "VRV_H_OUT", "system": "VRV", "group": "Dàn nóng", "name": "Dàn nóng VRV H (2 chiều lạnh/sưởi)"},
    {"id": "VRV_A_OUT", "system": "VRV", "group": "Dàn nóng", "name": "Dàn nóng VRV A / VRV 6 (1 chiều lạnh)"},
    {"id": "VRV_S_OUT", "system": "VRV", "group": "Dàn nóng", "name": "Dàn nóng VRV IV-S (Nhỏ gọn 4HP - 9HP)"},
    {"id": "VRV_IN_WALL", "system": "VRV", "group": "Dàn lạnh", "name": "Dàn lạnh VRV - Treo tường (FXAQ)"},
    {"id": "VRV_IN_CASSETTE", "system": "VRV", "group": "Dàn lạnh", "name": "Dàn lạnh VRV - Cassette âm trần (FXFQ / FXZQ / FXCQ / FXKQ)"},
    {"id": "VRV_IN_DUCT_SLIM", "system": "VRV", "group": "Dàn lạnh", "name": "Dàn lạnh VRV - Giấu trần nối ống gió mỏng (FXDQ)"},
    {"id": "VRV_IN_DUCT_MED", "system": "VRV", "group": "Dàn lạnh", "name": "Dàn lạnh VRV - Giấu trần nối ống gió ASTB (FXSQ)"},
    {"id": "VRV_IN_DUCT_HIGH", "system": "VRV", "group": "Dàn lạnh", "name": "Dàn lạnh VRV - Giấu trần nối ống gió ASTC (FXMQ)"},
    {"id": "VRV_IN_OTHER", "system": "VRV", "group": "Dàn lạnh", "name": "Dàn lạnh VRV - Áp trần & Đặt sàn (FXHQ / FXLQ / FXNQ)"},
    {"id": "VRV_HRV", "system": "VRV", "group": "Thông gió HRV", "name": "Thiết bị thông gió thu hồi nhiệt HRV (VAM-HVE)"},
    {"id": "VRV_ACC", "system": "VRV", "group": "Bộ chia gas & Điều khiển", "name": "Bộ chia gas REFNET & Điều khiển trung tâm VRV"},
    {"id": "ROOM_AIR", "system": "ROOM_AIR", "group": "Máy cục bộ treo tường", "name": "Điều hòa dân dụng 2 chiều Inverter (FTHF Series)"},
    {"id": "SKY_CASSETTE", "system": "SKYAIR", "group": "Cassette thương mại", "name": "Điều hòa SkyAir Cassette âm trần (FCQ / FCFC)"},
    {"id": "SKY_DUCT", "system": "SKYAIR", "group": "Giấu trần nối ống gió", "name": "Điều hòa SkyAir Giấu trần nối ống gió (FBQ / FBFC / FDF)"},
    {"id": "SKY_OTHER", "system": "SKYAIR", "group": "Áp trần & Tủ đứng", "name": "Điều hòa SkyAir Áp trần & Tủ đứng (FHA / FVA)"},
    {"id": "MULTI_OUT", "system": "MULTI", "group": "Dàn nóng Multi", "name": "Dàn nóng Super Multi NX R32 2 chiều (3MXM / 4MXM / 5MXM)"},
    {"id": "MULTI_IN_WALL", "system": "MULTI", "group": "Dàn lạnh Multi", "name": "Dàn lạnh Multi - Treo tường (CTXM)"},
    {"id": "MULTI_IN_CASSETTE", "system": "MULTI", "group": "Dàn lạnh Multi", "name": "Dàn lạnh Multi - Cassette âm trần (FFA)"},
    {"id": "MULTI_IN_DUCT", "system": "MULTI", "group": "Dàn lạnh Multi", "name": "Dàn lạnh Multi - Giấu trần nối ống gió (CDXP / CDXM / FMA)"},
    {"id": "MULTI_ACC", "system": "MULTI", "group": "Điều khiển Multi", "name": "Điều khiển có dây & không dây hệ Multi"}
]

products = []

def add_prod(p):
    p.setdefault("brand", "Daikin")
    p.setdefault("origin", "Thái Lan")
    p.setdefault("unit", "Dàn")
    p.setdefault("price", 0)
    p.setdefault("refrigerant", "R410A")
    p.setdefault("power_supply", "1 pha, 220-240V, 50Hz")
    p.setdefault("duct", None)
    p.setdefault("ceiling_opening", "")
    p.setdefault("panel_model", "")
    p.setdefault("panel_dim", "")
    p.setdefault("combo_detail", "")
    p.setdefault("commercial_img", "")
    p.setdefault("web_url", "https://www.daikincatalog.com/library/site/vietnam/book-lists/")
    products.append(p)

# ==============================================================================
# 1. VRV H OUTDOOR UNITS (RXYQ8BYM -> RXYQ60BYM) - Prices from BÁO GIÁ VRV.xlsx
# ==============================================================================
vrvh_list = [
    # model, hp, btu_c, kw_c, btu_h, kw_h, p_cool, dim, weight, airflow, noise, pipe_l_g, price, unit, combo
    ("RXYQ8BYM", 8, 76400, 22.4, 85300, 25.0, "5.17 kW", "1660x930x765", "215 kg", "155 m³/phút", "56/56 dB(A)", "Ø9.5 / Ø19.1 (Hàn)", 82868000, "Dàn", "Dàn nóng đơn độc lập"),
    ("RXYQ10BYM", 10, 95500, 28.0, 107000, 31.5, "6.81 kW", "1660x930x765", "215 kg", "169 m³/phút", "57/58 dB(A)", "Ø9.5 / Ø22.2 (Hàn)", 91998000, "Dàn", "Dàn nóng đơn độc lập"),
    ("RXYQ12BYM", 12, 114000, 33.5, 128000, 37.5, "8.70 kW", "1660x930x765", "225 kg", "181 m³/phút", "60/62 dB(A)", "Ø12.7 / Ø28.6 (Hàn)", 109555000, "Dàn", "Dàn nóng đơn độc lập"),
    ("RXYQ14BYM", 14, 136000, 40.0, 154000, 45.0, "10.7 kW", "1660x1240x765", "310 kg", "260 m³/phút", "61/61 dB(A)", "Ø12.7 / Ø28.6 (Hàn)", 127111000, "Dàn", "Dàn nóng đơn độc lập"),
    ("RXYQ16BYM", 16, 154000, 45.0, 171000, 50.0, "13.3 kW", "1660x1240x765", "310 kg", "266 m³/phút", "61/61 dB(A)", "Ø12.7 / Ø28.6 (Hàn)", 144668000, "Dàn", "Dàn nóng đơn độc lập"),
    ("RXYQ18BYM", 18, 171000, 50.0, 191000, 56.0, "14.3 kW", "1660x1240x765", "340 kg", "258 m³/phút", "65/66 dB(A)", "Ø15.9 / Ø28.6 (Hàn)", 155904000, "Dàn", "Dàn nóng đơn độc lập"),
    ("RXYQ20BYM", 20, 191000, 56.0, 215000, 63.0, "16.9 kW", "1660x1240x765", "340 kg", "306 m³/phút", "65/66 dB(A)", "Ø15.9 / Ø28.6 (Hàn)", 172759000, "Dàn", "Dàn nóng đơn độc lập"),
    ("RXYQ22BYM", 22, 210000, 61.5, 235000, 69.0, "18.6 kW", "1660x1750x765", "385 kg", "430 m³/phút", "67/67 dB(A)", "Ø15.9 / Ø28.6 (Hàn)", 201552000, "Dàn", "Dàn nóng đơn độc lập"),
    ("RXYQ24BYM", 24, 229000, 67.0, 256000, 75.0, "21.6 kW", "1660x1750x765", "385 kg", "430 m³/phút", "68/68 dB(A)", "Ø15.9 / Ø34.9 (Hàn)", 219109000, "Dàn", "Dàn nóng đơn độc lập"),
    ("RXYQ26BYM", 26, 250000, 73.5, 282000, 82.5, "19.4 kW", "(1660x930x765)+(1660x1240x765)", "225+310 (535 kg)", "181+260 m³/phút", "64/65 dB(A)", "Ø19.1 / Ø34.9 (Hàn)", 236666000, "Bộ", "01 dàn RXYQ14BYM + 01 dàn RXYQ12BYM (cần bộ nối BHFP22R135)"),
    ("RXYQ28BYM", 28, 268000, 78.5, 299000, 87.5, "22.0 kW", "(1660x930x765)+(1660x1240x765)", "225+310 (535 kg)", "181+266 m³/phút", "64/65 dB(A)", "Ø19.1 / Ø34.9 (Hàn)", 254224000, "Bộ", "01 dàn RXYQ16BYM + 01 dàn RXYQ12BYM (cần bộ nối BHFP22R135)"),
    ("RXYQ30BYM", 30, 285000, 83.5, 319000, 93.5, "23.0 kW", "(1660x930x765)+(1660x1240x765)", "225+340 (565 kg)", "181+258 m³/phút", "66/67 dB(A)", "Ø19.1 / Ø34.9 (Hàn)", 265459000, "Bộ", "01 dàn RXYQ18BYM + 01 dàn RXYQ12BYM (cần bộ nối BHFP22R135)"),
    ("RXYQ32BYM", 32, 305000, 89.5, 343000, 100.0, "25.6 kW", "(1660x930x765)+(1660x1240x765)", "225+340 (565 kg)", "181+306 m³/phút", "66/67 dB(A)", "Ø19.1 / Ø34.9 (Hàn)", 289337000, "Bộ", "01 dàn RXYQ20BYM + 01 dàn RXYQ12BYM (cần bộ nối BHFP22R135)"),
    ("RXYQ34BYM", 34, 327000, 96.0, 369000, 108.0, "27.6 kW", "(1660x1240x765)+(1660x1240x765)", "310+340 (650 kg)", "260+306 m³/phút", "66/67 dB(A)", "Ø19.1 / Ø34.9 (Hàn)", 300573000, "Bộ", "01 dàn RXYQ20BYM + 01 dàn RXYQ14BYM (cần bộ nối BHFP22R135)"),
    ("RXYQ36BYM", 36, 345000, 101.0, 386000, 113.0, "30.2 kW", "(1660x1240x765)+(1660x1240x765)", "310+340 (650 kg)", "266+306 m³/phút", "66/67 dB(A)", "Ø19.1 / Ø41.3 (Hàn)", 317427000, "Bộ", "01 dàn RXYQ20BYM + 01 dàn RXYQ16BYM (cần bộ nối BHFP22R135)"),
    ("RXYQ38BYM", 38, 362000, 106.0, 406000, 119.0, "31.2 kW", "(1660x1240x765)+(1660x1240x765)", "340+340 (680 kg)", "258+306 m³/phút", "68/69 dB(A)", "Ø19.1 / Ø41.3 (Hàn)", 328664000, "Bộ", "01 dàn RXYQ20BYM + 01 dàn RXYQ18BYM (cần bộ nối BHFP22R135)"),
    ("RXYQ40BYM", 40, 382000, 112.0, 430000, 126.0, "33.8 kW", "(1660x1240x765) x 2", "340+340 (680 kg)", "306+306 m³/phút", "68/69 dB(A)", "Ø19.1 / Ø41.3 (Hàn)", 345518000, "Bộ", "02 dàn RXYQ20BYM (cần bộ nối BHFP22R135)"),
    ("RXYQ42BYM", 42, 401000, 117.0, 450000, 132.0, "35.5 kW", "(1660x1240x765)+(1660x1750x765)", "340+385 (725 kg)", "306+430 m³/phút", "69/70 dB(A)", "Ø19.1 / Ø41.3 (Hàn)", 375015000, "Bộ", "01 dàn RXYQ22BYM + 01 dàn RXYQ20BYM (cần bộ nối BHFP22R135)"),
    ("RXYQ44BYM", 44, 420000, 123.0, 471000, 138.0, "38.5 kW", "(1660x1240x765)+(1660x1750x765)", "340+385 (725 kg)", "306+430 m³/phút", "70/70 dB(A)", "Ø19.1 / Ø41.3 (Hàn)", 391868000, "Bộ", "01 dàn RXYQ24BYM + 01 dàn RXYQ20BYM (cần bộ nối BHFP22R135)"),
    ("RXYQ46BYM", 46, 439000, 128.0, 491000, 144.0, "40.2 kW", "(1660x1750x765) x 2", "385+385 (770 kg)", "430+430 m³/phút", "70/70 dB(A)", "Ø19.1 / Ø41.3 (Hàn)", 416448000, "Bộ", "01 dàn RXYQ24BYM + 01 dàn RXYQ22BYM (cần bộ nối BHFP22R135)"),
    ("RXYQ48BYM", 48, 458000, 134.0, 512000, 150.0, "43.2 kW", "(1660x1750x765) x 2", "385+385 (770 kg)", "430+430 m³/phút", "71/71 dB(A)", "Ø19.1 / Ø41.3 (Hàn)", 434005000, "Bộ", "02 dàn RXYQ24BYM (cần bộ nối BHFP22R135)"),
    ("RXYQ50BYM", 50, 476000, 139.0, 534000, 156.0, "39.9 kW", "(1660x930x765)+(1660x1240x765)x2", "225+340+340 (905 kg)", "181+258+306 m³/phút", "67/68 dB(A)", "Ø19.1 / Ø41.3 (Hàn)", 445242000, "Bộ", "01 dàn RXYQ20BYM + 01 dàn RXYQ18BYM + 01 dàn RXYQ12BYM (bộ nối BHFP22R168)"),
    ("RXYQ52BYM", 52, 496000, 145.0, 558000, 163.0, "42.5 kW", "(1660x930x765)+(1660x1240x765)x2", "225+340+340 (905 kg)", "181+306+306 m³/phút", "68/69 dB(A)", "Ø19.1 / Ø41.3 (Hàn)", 456478000, "Bộ", "02 dàn RXYQ20BYM + 01 dàn RXYQ12BYM (bộ nối BHFP22R168)"),
    ("RXYQ54BYM", 54, 518000, 152.0, 584000, 171.0, "44.5 kW", "(1660x1240x765) x 3", "310+340+340 (990 kg)", "260+306+306 m³/phút", "69/70 dB(A)", "Ø19.1 / Ø41.3 (Hàn)", 467714000, "Bộ", "02 dàn RXYQ20BYM + 01 dàn RXYQ14BYM (bộ nối BHFP22R168)"),
    ("RXYQ56BYM", 56, 536000, 157.0, 601000, 176.0, "47.1 kW", "(1660x1240x765) x 3", "310+340+340 (990 kg)", "266+306+306 m³/phút", "69/70 dB(A)", "Ø19.1 / Ø41.3 (Hàn)", 484569000, "Bộ", "02 dàn RXYQ20BYM + 01 dàn RXYQ16BYM (bộ nối BHFP22R168)"),
    ("RXYQ58BYM", 58, 553000, 162.0, 621000, 182.0, "48.1 kW", "(1660x1240x765) x 3", "340+340+340 (1020 kg)", "258+306+306 m³/phút", "70/71 dB(A)", "Ø19.1 / Ø41.3 (Hàn)", 501424000, "Bộ", "02 dàn RXYQ20BYM + 01 dàn RXYQ18BYM (bộ nối BHFP22R168)"),
    ("RXYQ60BYM", 60, 573000, 168.0, 645000, 189.0, "50.7 kW", "(1660x1240x765) x 3", "340+340+340 (1020 kg)", "306+306+306 m³/phút", "70/71 dB(A)", "Ø19.1 / Ø41.3 (Hàn)", 518279000, "Bộ", "03 dàn RXYQ20BYM (bộ nối BHFP22R168)"),
]

for m, hp, bc, kc, bh, kh, pc, dim, wt, af, ns, pipe, pr, un, cb in vrvh_list:
    img = "vrv_outdoor_single_s.png" if hp <= 12 else ("vrv_outdoor_single_m.png" if hp <= 20 else ("vrv_outdoor_single_l.png" if hp <= 24 else "vrv_outdoor_multi.png"))
    cimg = "mp_vrvh_6_10.png" if hp <= 10 else ("mp_vrvh_12_20.png" if hp <= 20 else ("mp_vrvh_20_38.png" if hp <= 38 else "mp_vrvh_40_60.png"))
    pg = 24 if (hp <= 20 or (36 <= hp <= 48)) else 25
    add_prod({
        "id": m, "model": m, "category_id": "VRV_H_OUT",
        "name": f"Dàn nóng trung tâm VRV H 2 chiều {hp}HP ({bc:,} Btu/h)".replace(",", "."),
        "hp": f"{hp} HP", "cooling_btu": bc, "cooling_kw": kc, "heating_btu": bh, "heating_kw": kh,
        "power_input": pc, "power_supply": "3 pha 4 dây, 380-415V, 50Hz", "refrigerant": "R410A",
        "dimensions": dim, "weight": wt, "airflow": af, "noise": ns, "gas_pipe": pipe, "drain_pipe": "Thoát đáy dàn nóng",
        "price": pr, "unit": un, "origin": "Thái Lan", "combo_detail": cb,
        "image": f"assets/products/{img}", "commercial_img": f"assets/commercial/{cimg}",
        "catalog_pdf": "Catalogue Điều Hòa Trung tâm VRV H Daikin 2025.pdf", "catalog_page": pg,
        "tech_pdf": "Dàn nóng VRV 6 trung tâm.pdf", "tech_page": 21 + (hp - 8)//6,
        "notes": f"Kết nối tối đa {min(64, int(hp*1.6))} dàn lạnh. Tổng công suất kết nối 50% - 200%."
    })

# ==============================================================================
# 1B. VRV 6 A OUTDOOR UNITS (1 chiều lạnh - từ DAIKIN VRV TỔNG HỢP.pdf tr.94-95)
# ==============================================================================
vrva_list = [
    ("RXQ8BYM", 8, 76400, 22.4, "5.00 kW", "1660x930x765", "206 kg", "158 m³/phút", "56 dB(A)", "Ø9.5 / Ø19.1 (Hàn)", 0, "Dàn", "Dàn nóng đơn 1 chiều VRV 6 A"),
    ("RXQ10BYM", 10, 95500, 28.0, "6.41 kW", "1660x930x765", "210 kg", "174 m³/phút", "57 dB(A)", "Ø9.5 / Ø22.2 (Hàn)", 0, "Dàn", "Dàn nóng đơn 1 chiều VRV 6 A"),
    ("RXQ12BYM", 12, 114000, 33.5, "8.38 kW", "1660x930x765", "210 kg", "185 m³/phút", "59 dB(A)", "Ø12.7 / Ø28.6 (Hàn)", 0, "Dàn", "Dàn nóng đơn 1 chiều VRV 6 A"),
    ("RXQ14BYM", 14, 136000, 40.0, "9.88 kW", "1660x1240x765", "247 kg", "237 m³/phút", "61 dB(A)", "Ø12.7 / Ø28.6 (Hàn)", 0, "Dàn", "Dàn nóng đơn 1 chiều VRV 6 A"),
    ("RXQ16BYM", 16, 154000, 45.0, "12.6 kW", "1660x1240x765", "270 kg", "266 m³/phút", "61 dB(A)", "Ø12.7 / Ø28.6 (Hàn)", 0, "Dàn", "Dàn nóng đơn 1 chiều VRV 6 A"),
    ("RXQ18BYM", 18, 171000, 50.0, "13.8 kW", "1660x1240x765", "285 kg", "258 m³/phút", "63 dB(A)", "Ø15.9 / Ø28.6 (Hàn)", 0, "Dàn", "Dàn nóng đơn 1 chiều VRV 6 A"),
    ("RXQ20BYM", 20, 191000, 56.0, "15.9 kW", "1660x1240x765", "293 kg", "306 m³/phút", "65 dB(A)", "Ø15.9 / Ø28.6 (Hàn)", 0, "Dàn", "Dàn nóng đơn 1 chiều VRV 6 A"),
    ("RXQ24BYM", 24, 229000, 67.0, "22.2 kW", "1660x1750x765", "354 kg", "390 m³/phút", "67 dB(A)", "Ø15.9 / Ø34.9 (Hàn)", 0, "Dàn", "Dàn nóng đơn 1 chiều VRV 6 A"),
    ("RXQ30BYM", 30, 285000, 83.5, "20.2 kW", "(1660x930x765)+(1660x1240x765)", "210+285 kg", "185+258 m³/phút", "66 dB(A)", "Ø19.1 / Ø34.9 (Hàn)", 0, "Bộ", "RXQ12BYM + RXQ18BYM"),
    ("RXQ40BYM", 40, 382000, 112.0, "31.8 kW", "(1660x1240x765) x 2", "293+293 kg", "306+306 m³/phút", "68 dB(A)", "Ø19.1 / Ø41.3 (Hàn)", 0, "Bộ", "02 dàn RXQ20BYM"),
    ("RXQ50BYM", 50, 478000, 140.0, "43.7 kW", "(1660x1750x765) x 2", "354+354 kg", "390+411 m³/phút", "72 dB(A)", "Ø19.1 / Ø41.3 (Hàn)", 0, "Bộ", "RXQ24BYM + RXQ26BYM"),
    ("RXQ60BYM", 60, 573000, 168.0, "47.7 kW", "(1660x1240x765) x 3", "293x3 (879 kg)", "306x3 m³/phút", "70 dB(A)", "Ø19.1 / Ø41.3 (Hàn)", 0, "Bộ", "03 dàn RXQ20BYM"),
]
for m, hp, bc, kc, pc, dim, wt, af, ns, pipe, pr, un, cb in vrva_list:
    img = "vrv_outdoor_single_s.png" if hp <= 12 else ("vrv_outdoor_single_m.png" if hp <= 20 else ("vrv_outdoor_single_l.png" if hp <= 24 else "vrv_outdoor_multi.png"))
    cimg = "mp_vrva_6_10.png" if hp <= 10 else ("mp_vrva_12_20.png" if hp <= 20 else ("mp_vrva_20_38.png" if hp <= 38 else "mp_vrva_40_60.png"))
    add_prod({
        "id": m, "model": m, "category_id": "VRV_A_OUT",
        "name": f"Dàn nóng trung tâm VRV 6 A 1 chiều {hp}HP ({bc:,} Btu/h)".replace(",", "."),
        "hp": f"{hp} HP", "cooling_btu": bc, "cooling_kw": kc, "heating_btu": 0, "heating_kw": 0,
        "power_input": pc, "power_supply": "3 pha 4 dây, 380-415V, 50Hz", "refrigerant": "R410A",
        "dimensions": dim, "weight": wt, "airflow": af, "noise": ns, "gas_pipe": pipe, "drain_pipe": "Thoát đáy dàn nóng",
        "price": pr, "unit": un, "origin": "Thái Lan", "combo_detail": cb,
        "image": f"assets/products/{img}", "commercial_img": f"assets/commercial/{cimg}",
        "catalog_pdf": "DAIKIN VRV TỔNG HỢP.pdf", "catalog_page": 94 if hp <= 20 else 95,
        "notes": "Dòng VRV 6 A 1 chiều lạnh hiệu suất EER cao (Cập nhật giá theo dự án)."
    })

# ==============================================================================
# 2. VRV IV-S OUTDOOR UNITS (RXYMQ4AVE -> RXYMQ9AY1) - Prices from BÁO GIÁ VRV.xlsx
# ==============================================================================
vrvs_list = [
    ("RXYMQ4AVE", 4, 38200, 11.2, 42700, 12.5, "2.88 kW", "990x940x320", "71 kg", "76 m³/phút", "52/54 dB(A)", "Ø9.5 / Ø15.9 (Loe)", "1 pha, 220-240V, 50Hz", 46350000, "mp_vrv4s_4hp.png", "vrvs_outdoor_1fan.png"),
    ("RXYMQ5AVE", 5, 47800, 14.0, 47800, 14.0, "3.83 kW", "990x940x320", "78 kg", "80 m³/phút", "53/54 dB(A)", "Ø9.5 / Ø15.9 (Loe)", "1 pha, 220-240V, 50Hz", 52670000, "mp_vrv4s_5_6hp.png", "vrvs_outdoor_1fan.png"),
    ("RXYMQ6AVE", 6, 54600, 16.0, 54600, 16.0, "4.51 kW", "990x940x320", "80 kg", "81 m³/phút", "55/56 dB(A)", "Ø9.5 / Ø19.1 (Hàn)", "1 pha, 220-240V, 50Hz", 58800000, "mp_vrv4s_5_6hp.png", "vrvs_outdoor_1fan.png"),
    ("RXYMQ8AY1", 8, 76400, 22.4, 85300, 25.0, "5.94 kW", "1430x940x320", "138 kg", "140 m³/phút", "57/58 dB(A)", "Ø9.5 / Ø19.1 (Hàn)", "3 pha, 380-415V, 50Hz", 74569000, "mp_vrv4s_8hp.png", "vrvs_outdoor_2fan.png"),
    ("RXYMQ9AY1", 9, 81900, 24.0, 88700, 26.0, "6.88 kW", "1430x940x320", "140 kg", "140 m³/phút", "58/59 dB(A)", "Ø9.5 / Ø22.2 (Hàn)", "3 pha, 380-415V, 50Hz", 80251000, "mp_vrv4s_8hp.png", "vrvs_outdoor_2fan.png"),
]
for m, hp, bc, kc, bh, kh, pc, dim, wt, af, ns, pipe, pwr, pr, cimg, img in vrvs_list:
    add_prod({
        "id": m, "model": m, "category_id": "VRV_S_OUT",
        "name": f"Dàn nóng VRV IV-S 2 chiều nhỏ gọn {hp}HP ({bc:,} Btu/h)".replace(",", "."),
        "hp": f"{hp} HP", "cooling_btu": bc, "cooling_kw": kc, "heating_btu": bh, "heating_kw": kh,
        "power_input": pc, "power_supply": pwr, "refrigerant": "R410A",
        "dimensions": dim, "weight": wt, "airflow": af, "noise": ns, "gas_pipe": pipe, "drain_pipe": "Thoát đáy dàn nóng",
        "price": pr, "unit": "Dàn", "origin": "Thái Lan",
        "image": f"assets/products/{img}", "commercial_img": f"assets/commercial/{cimg}",
        "catalog_pdf": "DAIKIN VRV TỔNG HỢP.pdf", "catalog_page": 135,
        "tech_pdf": "CATALOGUE KỸ THUẬT VRV 4S.pdf", "tech_page": 3,
        "notes": "Thiết kế mỏng 320mm tiết kiệm diện tích ban công biệt thự, chung cư cao cấp."
    })

# ==============================================================================
# 3. VRV INDOOR - WALL MOUNTED (FXAQ20PVE -> FXAQ63PVE)
# ==============================================================================
fxaq_list = [
    ("FXAQ20PVE", "0.8 HP", 7500, 2.2, 8500, 2.5, "19 W", "290x795x238", "11 kg", "7.5/6.0/4.5 m³/phút", "35/31/28 dB(A)", "Ø6.4 / Ø12.7", 9576000),
    ("FXAQ25PVE", "1.0 HP", 9600, 2.8, 10900, 3.2, "28 W", "290x795x238", "11 kg", "8.0/6.5/5.0 m³/phút", "36/32/28 dB(A)", "Ø6.4 / Ø12.7", 9704000),
    ("FXAQ32PVE", "1.25 HP", 12300, 3.6, 13600, 4.0, "30 W", "290x795x238", "11 kg", "8.5/7.0/5.5 m³/phút", "37/33/28 dB(A)", "Ø6.4 / Ø12.7", 9960000),
    ("FXAQ40PVE", "1.6 HP", 15400, 4.5, 17100, 5.0, "20 W", "290x1050x238", "14 kg", "12.0/10.5/9.0 m³/phút", "39/35/32 dB(A)", "Ø6.4 / Ø12.7", 10343000),
    ("FXAQ50PVE", "2.0 HP", 19100, 5.6, 21500, 6.3, "33 W", "290x1050x238", "14 kg", "15.0/12.5/10.5 m³/phút", "42/38/34 dB(A)", "Ø6.4 / Ø12.7", 11364000),
    ("FXAQ63PVE", "2.5 HP", 24200, 7.1, 27300, 8.0, "50 W", "290x1050x238", "14 kg", "19.0/16.5/13.5 m³/phút", "46/42/38 dB(A)", "Ø9.5 / Ø15.9", 12066000),
]
for m, hp, bc, kc, bh, kh, pw, dim, wt, af, ns, pipe, pr in fxaq_list:
    add_prod({
        "id": m, "model": m, "category_id": "VRV_IN_WALL",
        "name": f"Dàn lạnh treo tường VRV {bc:,} Btu/h ({m})".replace(",", "."),
        "hp": hp, "cooling_btu": bc, "cooling_kw": kc, "heating_btu": bh, "heating_kw": kh,
        "power_input": pw, "dimensions": dim, "weight": wt, "airflow": af, "noise": ns,
        "gas_pipe": pipe, "drain_pipe": "VP13 (Ngoài Ø18 / Trong Ø13)",
        "price": pr, "unit": "Dàn", "origin": "Thái Lan",
        "image": "assets/products/wall_fxaq.png", "commercial_img": "assets/commercial/mp_fxaq.png",
        "catalog_pdf": "DAIKIN VRV TỔNG HỢP.pdf", "catalog_page": 217,
        "notes": "Loại treo tường mặt phẳng trang nhã, không kèm bơm nước ngưng."
    })

# ==============================================================================
# 4. VRV INDOOR - CASSETTE (FXFQ + BYCQ125EAF + FXZQ / FXCQ / FXKQ)
# ==============================================================================
fxfq_list = [
    ("FXFQ25AVM", "1.0 HP", 9600, 2.8, 10900, 3.2, "29 W", "256x840x840", "19 kg", "13/12.5/11.5 m³/phút", "30/28.5/27 dB(A)", "Ø6.4 / Ø12.7", 11428000),
    ("FXFQ32AVM", "1.25 HP", 12300, 3.6, 13600, 4.0, "29 W", "256x840x840", "19 kg", "13/12.5/11.5 m³/phút", "30/28.5/27 dB(A)", "Ø6.4 / Ø12.7", 11683000),
    ("FXFQ40AVM", "1.6 HP", 15400, 4.5, 17100, 5.0, "36 W", "256x840x840", "19 kg", "17/13.5/11 m³/phút", "35/29/27 dB(A)", "Ø6.4 / Ø12.7", 12130000),
    ("FXFQ50AVM", "2.0 HP", 19100, 5.6, 21500, 6.3, "40 W", "256x840x840", "19 kg", "18/13.5/11 m³/phút", "35/29.5/27 dB(A)", "Ø6.4 / Ø12.7", 13344000),
    ("FXFQ63AVM", "2.5 HP", 24200, 7.1, 27300, 8.0, "63 W", "256x840x840", "22 kg", "21/16/13.5 m³/phút", "36/31.5/28 dB(A)", "Ø9.5 / Ø15.9", 14173000),
    ("FXFQ80AVM", "3.2 HP", 30700, 9.0, 34100, 10.0, "96 W", "256x840x840", "22 kg", "22.5/21/15 m³/phút", "37/36/29.5 dB(A)", "Ø9.5 / Ø15.9", 16855000),
    ("FXFQ100AVM", "4.0 HP", 38200, 11.2, 42700, 12.5, "158 W", "298x840x840", "25 kg", "32/26/21 m³/phút", "43/37.5/33 dB(A)", "Ø9.5 / Ø15.9", 18068000),
    ("FXFQ125AVM", "5.0 HP", 47800, 14.0, 47800, 14.0, "178 W", "298x840x840", "25 kg", "33/28/21 m³/phút", "44/39/33 dB(A)", "Ø9.5 / Ø15.9", 20493000),
    ("FXFQ140AVM", "6.0 HP", 54600, 16.0, 54600, 16.0, "203 W", "298x840x840", "26 kg", "35.5/29.5/23 m³/phút", "46/40.5/35 dB(A)", "Ø9.5 / Ø15.9", 22989000),
]
for m, hp, bc, kc, bh, kh, pw, dim, wt, af, ns, pipe, pr in fxfq_list:
    add_prod({
        "id": m, "model": m, "category_id": "VRV_IN_CASSETTE",
        "name": f"Dàn lạnh Cassette âm trần đa hướng thổi VRV {bc:,} Btu/h".replace(",", "."),
        "hp": hp, "cooling_btu": bc, "cooling_kw": kc, "heating_btu": bh, "heating_kw": kh,
        "power_input": pw, "dimensions": dim, "weight": wt, "airflow": af, "noise": ns,
        "gas_pipe": pipe, "drain_pipe": "VP25 (Ngoài Ø32 / Trong Ø25) - Có bơm nâng 850mm",
        "ceiling_opening": "860x860 đến 910x910 mm",
        "panel_model": "BYCQ125EAF", "panel_dim": "50x950x950 mm (5.5 kg)",
        "price": pr, "unit": "Dàn", "origin": "Thái Lan",
        "image": "assets/products/cassette_roundflow.png", "commercial_img": "assets/commercial/mp_fxfq.png",
        "catalog_pdf": "DAIKIN VRV TỔNG HỢP.pdf", "catalog_page": 193,
        "notes": "Luồng gió 360° Round Flow phân bổ nhiệt đồng đều. Giá thân máy chưa gồm mặt nạ BYCQ125EAF."
    })

add_prod({
    "id": "BYCQ125EAF", "model": "BYCQ125EAF", "category_id": "VRV_IN_CASSETTE",
    "name": "Mặt nạ tiêu chuẩn Cassette âm trần đa hướng thổi (Trắng sáng)",
    "hp": "Phụ kiện", "cooling_btu": 0, "cooling_kw": 0, "heating_btu": 0, "heating_kw": 0,
    "power_input": "—", "dimensions": "50x950x950", "weight": "5.5 kg", "airflow": "360° đa hướng", "noise": "—",
    "gas_pipe": "—", "drain_pipe": "—", "ceiling_opening": "Lắp cho FXFQ25-140AVM / FCFC40-140DVM",
    "price": 2147000, "unit": "Cái", "origin": "Thái Lan",
    "image": "assets/products/panel_cassette.png", "commercial_img": "assets/commercial/mp_fxfq.png",
    "catalog_pdf": "DAIKIN VRV TỔNG HỢP.pdf", "catalog_page": 193,
    "notes": "Mặt nạ trang trí tiêu chuẩn màu trắng sáng Fresh White dùng cho Cassette Round Flow."
})

# Additional VRV Cassettes from Catalogue (FXZQ compact 4-way, FXCQ 2-way, FXKQ 1-way)
extra_cassettes = [
    ("FXZQ25BVM", "1.0 HP", 9600, 2.8, 10900, 3.2, "43 W", "260x575x575", "15.5 kg", "9.0/8.0/6.5 m³/phút", "33/30/25.5 dB(A)", "Ø6.4 / Ø12.7", "585x585 mm", "BYFQ60CAW (46x620x620, 2.8 kg)", "cassette_compact.png", "mp_fxzq.png", 195, "Cassette 4 hướng thổi nhỏ gọn vừa ô trần 600x600"),
    ("FXZQ32BVM", "1.25 HP", 12300, 3.6, 13600, 4.0, "45 W", "260x575x575", "16.5 kg", "10.0/8.5/7.0 m³/phút", "33.5/30/26 dB(A)", "Ø6.4 / Ø12.7", "585x585 mm", "BYFQ60CAW (46x620x620, 2.8 kg)", "cassette_compact.png", "mp_fxzq.png", 195, "Cassette 4 hướng thổi nhỏ gọn vừa ô trần 600x600"),
    ("FXZQ40BVM", "1.6 HP", 15400, 4.5, 17100, 5.0, "59 W", "260x575x575", "16.5 kg", "11.5/9.5/8.0 m³/phút", "37/32/28 dB(A)", "Ø6.4 / Ø12.7", "585x585 mm", "BYFQ60CAW (46x620x620, 2.8 kg)", "cassette_compact.png", "mp_fxzq.png", 195, "Cassette 4 hướng thổi nhỏ gọn vừa ô trần 600x600"),
    ("FXZQ50BVM", "2.0 HP", 19100, 5.6, 21500, 6.3, "92 W", "260x575x575", "18.5 kg", "14.5/12.5/10.0 m³/phút", "43/40/33 dB(A)", "Ø6.4 / Ø12.7", "585x585 mm", "BYFQ60CAW (46x620x620, 2.8 kg)", "cassette_compact.png", "mp_fxzq.png", 195, "Cassette 4 hướng thổi nhỏ gọn vừa ô trần 600x600"),
    ("FXCQ32BVM", "1.25 HP", 12300, 3.6, 13600, 4.0, "39 W", "305x775x620", "19 kg", "11.5/10.5/9.5/8.5/8.0 m³/phút", "34/33/31/30/29 dB(A)", "Ø6.4 / Ø12.7", "815x660 mm", "BYBCQ40CF (55x1070x700)", "cassette_2way.png", "", 197, "Cassette âm trần 2 hướng thổi mỏng gọn"),
    ("FXCQ63BVM", "2.5 HP", 24200, 7.1, 27300, 8.0, "63 W", "305x990x620", "25 kg", "16/15/14/12.5/11.5 m³/phút", "39/38/37/34/32 dB(A)", "Ø9.5 / Ø15.9", "1030x660 mm", "BYBCQ63CF (55x1285x700)", "cassette_2way.png", "", 197, "Cassette âm trần 2 hướng thổi mỏng gọn"),
    ("FXKQ32AVM", "1.25 HP", 12300, 3.6, 13600, 4.0, "45 W", "215x1110x710", "29 kg", "11/9.5 m³/phút", "37/32 dB(A)", "Ø6.4 / Ø12.7", "1140x740 mm", "BYK45F (70x1240x800)", "cassette_1way.png", "mp_fxkq.png", 198, "Cassette âm trần 1 hướng thổi chuyên cho sảnh/phòng ngủ"),
    ("FXKQ63AVM", "2.5 HP", 24200, 7.1, 27300, 8.0, "75 W", "215x1310x710", "33 kg", "18/15 m³/phút", "40/35 dB(A)", "Ø9.5 / Ø15.9", "1340x740 mm", "BYK71F (70x1440x800)", "cassette_1way.png", "mp_fxkq.png", 198, "Cassette âm trần 1 hướng thổi chuyên cho sảnh/phòng ngủ"),
]
for m, hp, bc, kc, bh, kh, pw, dim, wt, af, ns, pipe, ceil, pan, img, cimg, pg, nt in extra_cassettes:
    add_prod({
        "id": m, "model": m, "category_id": "VRV_IN_CASSETTE",
        "name": f"Dàn lạnh {nt.split(' chuyên')[0].split(' vừa')[0]} ({m})",
        "hp": hp, "cooling_btu": bc, "cooling_kw": kc, "heating_btu": bh, "heating_kw": kh,
        "power_input": pw, "dimensions": dim, "weight": wt, "airflow": af, "noise": ns,
        "gas_pipe": pipe, "drain_pipe": "VP20/VP25 - Có bơm nước xả",
        "ceiling_opening": ceil, "panel_model": pan.split(" ")[0], "panel_dim": pan,
        "price": 0, "unit": "Dàn", "origin": "Thái Lan",
        "image": f"assets/products/{img}", "commercial_img": f"assets/commercial/{cimg}" if cimg else "",
        "catalog_pdf": "DAIKIN VRV TỔNG HỢP.pdf", "catalog_page": pg, "notes": nt
    })

# ==============================================================================
# 5. VRV INDOOR - SLIM DUCT (FXDQ20PDVE -> FXDQ63NDVE)
# Specs from DAIKIN VRV TỔNG HỢP.pdf p.204; Air outlet flange from Daikin UK.SAF5-7 / Drawing 3D049799
# (Model không nằm trong Bảng côn Excel - KHÔNG bịa kích thước hộp gió)
# ==============================================================================
fxdq_list = [
    ("FXDQ20PDVE", "0.8 HP", 7500, 2.2, 8500, 2.5, "86 W", "200x700x620", "23 kg", "8.0/7.2/6.4 m³/phút (480 m³/h)", "28/26/23 dB(A)", "10 - 30 Pa", "Ø6.4 / Ø12.7", 9066000,
     {"supply_collar": "660x152", "return_collar": "Theo bản vẽ hãng (thân 200x700)", "mouth_w": 660, "mouth_h": 152, "insul_m2": 0, "plenum_height": 0, "spigots": "Theo thiết kế công trình", "propose": "Mặt bích miệng cấp chuẩn hãng Daikin 660x152mm (Model ngoài Bảng côn Excel)", "std_box": "Không có trong Bảng côn Excel — kiểm tra bản vẽ hãng Daikin 3D049799 trước khi gia công hộp gió"}),
    ("FXDQ25PDVE", "1.0 HP", 9600, 2.8, 10900, 3.2, "86 W", "200x700x620", "23 kg", "8.0/7.2/6.4 m³/phút (480 m³/h)", "28/26/23 dB(A)", "10 - 30 Pa", "Ø6.4 / Ø12.7", 9129000,
     {"supply_collar": "660x152", "return_collar": "Theo bản vẽ hãng (thân 200x700)", "mouth_w": 660, "mouth_h": 152, "insul_m2": 0, "plenum_height": 0, "spigots": "Theo thiết kế công trình", "propose": "Mặt bích miệng cấp chuẩn hãng Daikin 660x152mm (Model ngoài Bảng côn Excel)", "std_box": "Không có trong Bảng côn Excel — kiểm tra bản vẽ hãng Daikin 3D049799 trước khi gia công hộp gió"}),
    ("FXDQ32PDVE", "1.25 HP", 12300, 3.6, 13600, 4.0, "89 W", "200x700x620", "23 kg", "8.0/7.2/6.4 m³/phút (480 m³/h)", "28/26/24 dB(A)", "10 - 30 Pa", "Ø6.4 / Ø12.7", 9321000,
     {"supply_collar": "660x152", "return_collar": "Theo bản vẽ hãng (thân 200x700)", "mouth_w": 660, "mouth_h": 152, "insul_m2": 0, "plenum_height": 0, "spigots": "Theo thiết kế công trình", "propose": "Mặt bích miệng cấp chuẩn hãng Daikin 660x152mm (Model ngoài Bảng côn Excel)", "std_box": "Không có trong Bảng côn Excel — kiểm tra bản vẽ hãng Daikin 3D049799 trước khi gia công hộp gió"}),
    ("FXDQ40NDVE", "1.6 HP", 15400, 4.5, 17100, 5.0, "160 W", "200x900x620", "27 kg", "10.5/9.5/8.5 m³/phút (630 m³/h)", "30/28/26 dB(A)", "15 - 44 Pa", "Ø6.4 / Ø12.7", 9704000,
     {"supply_collar": "860x152", "return_collar": "Theo bản vẽ hãng (thân 200x900)", "mouth_w": 860, "mouth_h": 152, "insul_m2": 0, "plenum_height": 0, "spigots": "Theo thiết kế công trình", "propose": "Mặt bích miệng cấp chuẩn hãng Daikin 860x152mm (Model ngoài Bảng côn Excel)", "std_box": "Không có trong Bảng côn Excel — kiểm tra bản vẽ hãng Daikin 3D049799 trước khi gia công hộp gió"}),
    ("FXDQ50NDVE", "2.0 HP", 19100, 5.6, 21500, 6.3, "165 W", "200x900x620", "28 kg", "12.5/11.0/10.0 m³/phút (750 m³/h)", "33/30/27 dB(A)", "15 - 44 Pa", "Ø6.4 / Ø12.7", 10662000,
     {"supply_collar": "860x152", "return_collar": "Theo bản vẽ hãng (thân 200x900)", "mouth_w": 860, "mouth_h": 152, "insul_m2": 0, "plenum_height": 0, "spigots": "Theo thiết kế công trình", "propose": "Mặt bích miệng cấp chuẩn hãng Daikin 860x152mm (Model ngoài Bảng côn Excel)", "std_box": "Không có trong Bảng côn Excel — kiểm tra bản vẽ hãng Daikin 3D049799 trước khi gia công hộp gió"}),
    ("FXDQ63NDVE", "2.5 HP", 24200, 7.1, 27300, 8.0, "181 W", "200x1100x620", "31 kg", "16.5/14.5/13.0 m³/phút (990 m³/h)", "33/31/29 dB(A)", "15 - 44 Pa", "Ø9.5 / Ø15.9", 11364000,
     {"supply_collar": "1060x152", "return_collar": "Theo bản vẽ hãng (thân 200x1100)", "mouth_w": 1060, "mouth_h": 152, "insul_m2": 0, "plenum_height": 0, "spigots": "Theo thiết kế công trình", "propose": "Mặt bích miệng cấp chuẩn hãng Daikin 1060x152mm (Model ngoài Bảng côn Excel)", "std_box": "Không có trong Bảng côn Excel — kiểm tra bản vẽ hãng Daikin 3D049799 trước khi gia công hộp gió"}),
]
for m, hp, bc, kc, bh, kh, pw, dim, wt, af, ns, esp, pipe, pr, dct in fxdq_list:
    is_pd = "PDVE" in m
    add_prod({
        "id": m, "model": m, "category_id": "VRV_IN_DUCT_SLIM",
        "name": f"Dàn lạnh giấu trần nối ống gió dạng mỏng VRV {bc:,} Btu/h".replace(",", "."),
        "hp": hp, "cooling_btu": bc, "cooling_kw": kc, "heating_btu": bh, "heating_kw": kh,
        "power_input": pw, "dimensions": dim, "weight": wt, "airflow": af, "noise": ns, "esp": esp,
        "gas_pipe": pipe, "drain_pipe": "VP20 (Ngoài Ø26 / Trong Ø20) - Bơm nâng 750mm",
        "price": pr, "unit": "Dàn", "origin": "Thái Lan", "duct": dct,
        "image": f"assets/products/{'duct_slim_pd.png' if is_pd else 'duct_slim_nd.png'}",
        "commercial_img": f"assets/commercial/{'mp_fxdq_20_32.png' if is_pd else 'mp_fxdq_40_63.png'}",
        "catalog_pdf": "DAIKIN VRV TỔNG HỢP.pdf", "catalog_page": 204,
        "notes": "Chiều cao máy siêu mỏng chỉ 200mm, lý tưởng cho trần khách sạn & căn hộ có trần thạch cao hẹp (từ 240mm)."
    })

# ==============================================================================
# 6. VRV INDOOR - MEDIUM STATIC DUCT (FXSQ20PAVE -> FXSQ140PAVE)
# 100% Exact Duct & Plenum data from BẢNG CÔN ĐẦU DÀN LẠNH DAIKIN - E HOAN.xlsx!
# ==============================================================================
fxsq_list = [
    ("FXSQ20PAVE", "0.8 HP", 7500, 2.2, 8500, 2.5, "58 W", "245x550x800", "25 kg", "540 m³/h - 150 l/s (9 m³/phút)", "33/30/28 dB(A)", "30-150 Pa (ĐM 50Pa)", "Ø6.4 / Ø12.7", 11875000,
     "340x180", "505x210", 340, 180, 0.312, "Côn đầu máy (a.b), H250 + 2 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 480 x 220, giật cổ 340x180 để thẳng 60/480 x 220/ H250, trổ đỉnh 2D200"),
    ("FXSQ25PAVE", "1.0 HP", 9600, 2.8, 10900, 3.2, "58 W", "245x550x800", "25 kg", "540 m³/h - 150 l/s (9 m³/phút)", "33/30/28 dB(A)", "30-150 Pa (ĐM 50Pa)", "Ø6.4 / Ø12.7", 12003000,
     "340x180", "505x210", 340, 180, 0.312, "Côn đầu máy, H250 + 2 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 480 x 220, giật cổ 340x180 để thẳng 60/480 x 220/ H250, trổ đỉnh 2D200"),
    ("FXSQ32PAVE", "1.25 HP", 12300, 3.6, 13600, 4.0, "66 W", "245x550x800", "25 kg", "568.8 m³/h - 158 l/s (9.5 m³/phút)", "34/32/29 dB(A)", "30-150 Pa (ĐM 50Pa)", "Ø6.4 / Ø12.7", 12258000,
     "340x180", "505x210", 340, 180, 0.312, "Côn đầu máy, H250 + 2 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 480 x 220, giật cổ 340x180 để thẳng 60/480 x 220/ H250, trổ đỉnh 2D200"),
    ("FXSQ40PAVE", "1.6 HP", 15400, 4.5, 17100, 5.0, "101 W", "245x700x800", "27 kg", "900 m³/h - 250 l/s (15 m³/phút)", "36/33/30 dB(A)", "30-150 Pa (ĐM 50Pa)", "Ø6.4 / Ø12.7", 12769000,
     "495x180", "655x210", 495, 180, 0.405, "Côn đầu máy, H250 + 2 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 495 x 220, giật cổ 495 x 180 để thẳng 60/495 x 220/ H250, trổ đỉnh 2D200"),
    ("FXSQ50PAVE", "2.0 HP", 19100, 5.6, 21500, 6.3, "75 W", "245x1000x800", "35 kg", "1018.8 m³/h - 283 l/s (17 m³/phút)", "34/32/30 dB(A)", "50-150 Pa (ĐM 50Pa)", "Ø6.4 / Ø12.7", 13981000,
     "795x180", "955x210", 795, 180, 0.585, "Côn đầu máy, H250 + 3 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 795 x 220, Giật cổ 795 x 180 để thẳng 60/795 x 220/ H250, trổ đỉnh 3D200"),
    ("FXSQ63PAVE", "2.5 HP", 24200, 7.1, 27300, 8.0, "106 W", "245x1000x800", "35 kg", "1260 m³/h - 350 l/s (21 m³/phút)", "36/32/29 dB(A)", "50-150 Pa (ĐM 50Pa)", "Ø9.5 / Ø15.9", 14875000,
     "795x180", "955x210", 795, 180, 0.585, "Côn đầu máy, H250 + 4 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1000 x 220, Giật cổ 795 x 180 để thẳng 60/1000 x 220/ H250, trổ đỉnh 4D200"),
    ("FXSQ80PAVE", "3.2 HP", 30700, 9.0, 34100, 10.0, "126 W", "245x1000x800", "37 kg", "1378.8 m³/h - 383 l/s (23 m³/phút)", "37.5/34/30 dB(A)", "50-150 Pa (ĐM 50Pa)", "Ø9.5 / Ø15.9", 17684000,
     "795x180", "955x210", 795, 180, 0.585, "Côn đầu máy, H250 + 4 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1000 x 220, Giật cổ 795 x 180 để thẳng 60/1000 x 220/ H250, trổ đỉnh 4D200"),
    ("FXSQ100PAVE", "4.0 HP", 38200, 11.2, 42700, 12.5, "151 W", "245x1400x800", "46 kg", "1918.8 m³/h - 533 l/s (32 m³/phút)", "39/35/32 dB(A)", "50-150 Pa (ĐM 50Pa)", "Ø9.5 / Ø15.9", 18962000,
     "1195x180", "1355x210", 1195, 180, 0.990, "Côn đầu máy, H300 + 4 cổ D250 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1260 x 220, Giật cổ 1195 x 180 để thẳng 60/1260 x 220/ H300, trổ đỉnh 5D200"),
    ("FXSQ125PAVE", "5.0 HP", 47800, 14.0, 54600, 16.0, "206 W", "245x1400x800", "47 kg", "2221.2 m³/h - 617 l/s (37 m³/phút)", "42/38.5/35 dB(A)", "50-150 Pa (ĐM 50Pa)", "Ø9.5 / Ø15.9", 21515000,
     "1195x180", "1355x210", 1195, 180, 0.990, "Côn đầu máy, H300 + 4 cổ D250 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1520 x 220, Giật cổ 1195 x 180 để thẳng 60/1520 x 220/ H300, trổ đỉnh 6D200"),
    ("FXSQ140PAVE", "6.0 HP", 54600, 16.0, 61400, 18.0, "222 W", "245x1550x800", "52 kg", "2340 m³/h - 650 l/s (39 m³/phút)", "43/40/36 dB(A)", "50-140 Pa (ĐM 50Pa)", "Ø9.5 / Ø15.9", 24133000,
     "1340x180", "1505x210", 1340, 180, 1.094, "Côn đầu máy, H300 + 4 cổ D250 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1520 x 220, Giật cổ 1340 x 180 để thẳng 60/1520 x 220/ H300, trổ đỉnh 6D200"),
]
for m, hp, bc, kc, bh, kh, pw, dim, wt, af, ns, esp, pipe, pr, sc, rc, mw, mh, ins, prop, sbox in fxsq_list:
    add_prod({
        "id": m, "model": m, "category_id": "VRV_IN_DUCT_MED",
        "name": f"Dàn lạnh giấu trần nối ống gió ASTB VRV {bc:,} Btu/h".replace(",", "."),
        "hp": hp, "cooling_btu": bc, "cooling_kw": kc, "heating_btu": bh, "heating_kw": kh,
        "power_input": pw, "dimensions": dim, "weight": wt, "airflow": af, "noise": ns, "esp": esp,
        "gas_pipe": pipe, "drain_pipe": "VP25 (Ngoài Ø32 / Trong Ø25) - Có bơm nước ngưng",
        "price": pr, "unit": "Dàn", "origin": "Việt Nam",
        "duct": {"supply_collar": sc, "return_collar": rc, "mouth_w": mw, "mouth_h": mh, "insul_m2": ins, "propose": prop, "std_box": sbox},
        "image": "assets/products/duct_med_fxsq.png",
        "commercial_img": "assets/commercial/mp_fxsq_140.png" if "140" in m else "assets/commercial/mp_fxsq_20_125.png",
        "catalog_pdf": "DAIKIN VRV TỔNG HỢP.pdf", "catalog_page": 207,
        "notes": "Áp suất tĩnh trung bình 30-150Pa, chiều cao chỉ 245mm, tích hợp sẵn bơm nước xả."
    })

# ==============================================================================
# 7. VRV INDOOR - HIGH/MED-HIGH STATIC DUCT (FXMQ20PAVE -> FXMQ250MVE9)
# 100% Exact Duct & Plenum data from BẢNG CÔN ĐẦU DÀN LẠNH DAIKIN - E HOAN.xlsx!
# ==============================================================================
fxmq_list = [
    ("FXMQ20PAVE", "0.8 HP", 7500, 2.2, 8500, 2.5, "56 W", "300x550x700", "25 kg", "540 m³/h - 150 l/s (9 m³/phút)", "33/31/29 dB(A)", "30-100 Pa (ĐM 50Pa)", "Ø6.4 / Ø12.7", 11301000,
     "315x220", "480x250", 315, 220, 0.321, "Côn đầu máy (a.b), H250 + 2 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 480 x 220, Giật cổ 315 x 220 để thẳng 60/480 x 220/ H250, trổ đỉnh 2D200"),
    ("FXMQ25PAVE", "1.0 HP", 9600, 2.8, 10900, 3.2, "56 W", "300x550x700", "25 kg", "540 m³/h - 150 l/s (9 m³/phút)", "33/31/29 dB(A)", "30-100 Pa (ĐM 50Pa)", "Ø6.4 / Ø12.7", 11428000,
     "315x220", "480x250", 315, 220, 0.321, "Côn đầu máy, H250 + 2 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 480 x 220, Giật cổ 315 x 220 để thẳng 60/480 x 220/ H250, trổ đỉnh 2D200"),
    ("FXMQ32PAVE", "1.25 HP", 12300, 3.6, 13600, 4.0, "60 W", "300x550x700", "25 kg", "568.8 m³/h - 158 l/s (9.5 m³/phút)", "34/32/30 dB(A)", "30-100 Pa (ĐM 50Pa)", "Ø6.4 / Ø12.7", 11683000,
     "315x220", "480x250", 315, 220, 0.321, "Côn đầu máy, H250 + 2 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 480 x 220, Giật cổ 315 x 220 để thẳng 60/480 x 220/ H250, trổ đỉnh 2D200"),
    ("FXMQ40PAVE", "1.6 HP", 15400, 4.5, 17100, 5.0, "151 W", "300x700x700", "27 kg", "961.2 m³/h - 267 l/s (16 m³/phút)", "39/37/35 dB(A)", "30-160 Pa (ĐM 100Pa)", "Ø6.4 / Ø12.7", 12130000,
     "465x220", "630x250", 465, 220, 0.411, "Côn đầu máy, H250 + 2 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 465 x 220, Giật cổ 465x220 để thẳng 60/465 x 220/ H250, trổ đỉnh 2D200"),
    ("FXMQ50PAVE", "2.0 HP", 19100, 5.6, 21500, 6.3, "128 W", "300x1000x700", "35 kg", "1080 m³/h - 300 l/s (18 m³/phút)", "41/39/37 dB(A)", "50-200 Pa (ĐM 100Pa)", "Ø6.4 / Ø12.7", 13344000,
     "765x220", "930x250", 765, 220, 0.591, "Côn đầu máy, H250 + 3 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1000 x 220, Giật cổ 765x220 để thẳng 60/1000 x 220/ H250, trổ đỉnh 4D200"),
    ("FXMQ63PAVE", "2.5 HP", 24200, 7.1, 27300, 8.0, "138 W", "300x1000x700", "35 kg", "1170 m³/h - 325 l/s (19.5 m³/phút)", "42/40/38 dB(A)", "50-200 Pa (ĐM 100Pa)", "Ø9.5 / Ø15.9", 14173000,
     "765x220", "930x250", 765, 220, 0.591, "Côn đầu máy, H250 + 4 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1000 x 220, Giật cổ 765x220 để thẳng 60/1000 x 220/ H250, trổ đỉnh 4D200"),
    ("FXMQ80PAVE", "3.2 HP", 30700, 9.0, 34100, 10.0, "185 W", "300x1000x700", "35 kg", "1501.2 m³/h - 417 l/s (25 m³/phút)", "43/41/39 dB(A)", "50-200 Pa (ĐM 100Pa)", "Ø9.5 / Ø15.9", 16855000,
     "765x220", "930x250", 765, 220, 0.591, "Côn đầu máy, H250 + 4 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1000 x 220, Giật cổ 765x220 để thẳng 60/1000 x 220/ H250, trổ đỉnh 4D200"),
    ("FXMQ100PAVE", "4.0 HP", 38200, 11.2, 42700, 12.5, "215 W", "300x1400x700", "45 kg", "1918.8 m³/h - 533 l/s (32 m³/phút)", "43/41/39 dB(A)", "50-200 Pa (ĐM 100Pa)", "Ø9.5 / Ø15.9", 18068000,
     "1185x220", "1350x250", 1165, 220, 0.997, "Côn đầu máy, H300 + 4 cổ D250 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1260 x 220, Giật cổ 1165x220 để thẳng 60/1260 x 220/ H300, trổ đỉnh 5D200"),
    ("FXMQ125PAVE", "5.0 HP", 47800, 14.0, 54600, 16.0, "284 W", "300x1400x700", "45 kg", "2340 m³/h - 650 l/s (39 m³/phút)", "44/42/40 dB(A)", "50-200 Pa (ĐM 100Pa)", "Ø9.5 / Ø15.9", 20493000,
     "1185x220", "1330x250", 1165, 220, 0.997, "Côn đầu máy, H300 + 4 cổ D250 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1520 x 220, Giật cổ 1165x220 để thẳng 60/1520 x 220/ H300, trổ đỉnh 6D200"),
    ("FXMQ140PAVE", "6.0 HP", 54600, 16.0, 61400, 18.0, "405 W", "300x1400x700", "46 kg", "2761.2 m³/h - 767 l/s (46 m³/phút)", "46/45/43 dB(A)", "50-140 Pa (ĐM 100Pa)", "Ø9.5 / Ø15.9", 22983000,
     "1185x220", "1330x250", 1165, 220, 0.997, "Côn đầu máy, H300 + 4 cổ D250 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1520 x 220, Giật cổ 1165x220 để thẳng 60/1520 x 220/ H300, trổ đỉnh 6D200"),
    ("FXMQ200MVE9", "8.0 HP", 76400, 22.4, 85300, 25.0, "1.294 kW", "470x1380x1100", "137 kg", "58/50 m³/phút (3480 m³/h)", "48/45 dB(A) (220V)", "132 - 221 Pa", "Ø9.5 / Ø19.1", 37923000,
     "Theo mặt bích chuẩn hãng (Drawing 3D038851)", "Theo mặt bích chuẩn hãng (thân 470x1380x1100)", 0, 0, 0, "Dùng mặt bích chuẩn đi kèm máy + cổ bạt chống rung nối ống gió chính (Model ngoài Bảng côn Excel)", "Không có trong Bảng côn Excel — kiểm tra bản vẽ Daikin 3D038851 khi gia công côn chuyển tiếp"),
    ("FXMQ250MVE9", "10.0 HP", 95500, 28.0, 107500, 31.5, "1.465 kW", "470x1380x1100", "137 kg", "72/62 m³/phút (4320 m³/h)", "48/45 dB(A) (220V)", "191 - 270 Pa", "Ø9.5 / Ø22.2", 38242000,
     "Theo mặt bích chuẩn hãng (Drawing 3D038851)", "Theo mặt bích chuẩn hãng (thân 470x1380x1100)", 0, 0, 0, "Dùng mặt bích chuẩn đi kèm máy + cổ bạt chống rung nối ống gió chính (Model ngoài Bảng côn Excel)", "Không có trong Bảng côn Excel — kiểm tra bản vẽ Daikin 3D038851 khi gia công côn chuyển tiếp"),
]
for m, hp, bc, kc, bh, kh, pw, dim, wt, af, ns, esp, pipe, pr, sc, rc, mw, mh, ins, prop, sbox in fxmq_list:
    is_large = "200" in m or "250" in m
    add_prod({
        "id": m, "model": m, "category_id": "VRV_IN_DUCT_HIGH",
        "name": f"Dàn lạnh giấu trần nối ống gió {'ASTC cỡ lớn' if is_large else 'dạng dày ASTC'} VRV {bc:,} Btu/h".replace(",", "."),
        "hp": hp, "cooling_btu": bc, "cooling_kw": kc, "heating_btu": bh, "heating_kw": kh,
        "power_input": pw, "dimensions": dim, "weight": wt, "airflow": af, "noise": ns, "esp": esp,
        "gas_pipe": pipe,
        "drain_pipe": "BSP 1 inch (Không kèm bơm nước xả)" if is_large else "VP25 (Ngoài Ø32 / Trong Ø25) - Có bơm nước ngưng",
        "price": pr, "unit": "Dàn", "origin": "Thái Lan",
        "duct": {"supply_collar": sc, "return_collar": rc, "mouth_w": mw, "mouth_h": mh, "insul_m2": ins, "propose": prop, "std_box": sbox},
        "image": f"assets/products/{'duct_large_fxmq200.png' if is_large else 'duct_high_fxmq.png'}",
        "commercial_img": f"assets/commercial/{'mp_fxmq_200_250.png' if is_large else 'mp_fxmq_20_140.png'}",
        "catalog_pdf": "DAIKIN VRV TỔNG HỢP.pdf", "catalog_page": 211 if is_large else 209,
        "notes": "Áp suất tĩnh cao lên tới 200-250Pa, phù hợp tuyến ống gió dài và sảnh lớn."
    })

# ==============================================================================
# 7B. VRV INDOOR OTHER (FXHQ, FXLQ, FXNQ) & HRV (VAM150 -> VAM2000)
# ==============================================================================
vrv_other = [
    ("FXHQ32MAVE", "1.25 HP", 12300, 3.6, 13600, 4.0, "111 W", "195x960x680", "24 kg", "12/-/10 m³/phút", "36/-/31 dB(A)", "Ø6.4 / Ø12.7", "VP20 (Ngoài Ø26 / Trong Ø20)", "ceiling_fxhq.png", "mp_fxhq.png", 215, "Dàn lạnh áp trần VRV 12.300 Btu/h"),
    ("FXHQ63MAVE", "2.5 HP", 24200, 7.1, 27300, 8.0, "115 W", "195x1160x680", "28 kg", "17.5/-/14 m³/phút", "39/-/34 dB(A)", "Ø9.5 / Ø15.9", "VP20 (Ngoài Ø26 / Trong Ø20)", "ceiling_fxhq.png", "mp_fxhq.png", 215, "Dàn lạnh áp trần VRV 24.200 Btu/h"),
    ("FXHQ100MAVE", "4.0 HP", 38200, 11.2, 42700, 12.5, "135 W", "195x1400x680", "33 kg", "25/-/19.5 m³/phút", "45/-/37 dB(A)", "Ø9.5 / Ø15.9", "VP20 (Ngoài Ø26 / Trong Ø20)", "ceiling_fxhq.png", "mp_fxhq.png", 215, "Dàn lạnh áp trần VRV 38.200 Btu/h"),
    ("FXLQ32MAVE", "1.25 HP", 12300, 3.6, 13600, 4.0, "49 W", "600x1000x222", "25 kg", "8/6 m³/phút", "35/32 dB(A)", "Ø6.4 / Ø12.7", "Đường kính ngoài Ø21", "floor_fxlq.png", "", 218, "Dàn lạnh đặt sàn có vỏ VRV 12.300 Btu/h"),
    ("FXLQ50MAVE", "2.0 HP", 19100, 5.6, 21500, 6.3, "90 W", "600x1140x222", "30 kg", "14/11 m³/phút", "39/34 dB(A)", "Ø6.4 / Ø12.7", "Đường kính ngoài Ø21", "floor_fxlq.png", "", 218, "Dàn lạnh đặt sàn có vỏ VRV 19.100 Btu/h"),
    ("FXNQ32MAVE", "1.25 HP", 12300, 3.6, 13600, 4.0, "49 W", "610x1070x220", "23 kg", "8/6 m³/phút", "35/32 dB(A)", "Ø6.4 / Ø12.7", "Đường kính ngoài Ø21", "floor_duct_fxnq.png", "mp_fxnq.png", 219, "Dàn lạnh đặt sàn giấu tường VRV 12.300 Btu/h"),
    ("FXNQ50MAVE", "2.0 HP", 19100, 5.6, 21500, 6.3, "90 W", "610x1350x220", "27 kg", "14/11 m³/phút", "39/34 dB(A)", "Ø6.4 / Ø12.7", "Đường kính ngoài Ø21", "floor_duct_fxnq.png", "mp_fxnq.png", 219, "Dàn lạnh đặt sàn giấu tường VRV 19.100 Btu/h"),
]
for m, hp, bc, kc, bh, kh, pw, dim, wt, af, ns, pipe, drn, img, cimg, pg, nm in vrv_other:
    add_prod({
        "id": m, "model": m, "category_id": "VRV_IN_OTHER", "name": nm,
        "hp": hp, "cooling_btu": bc, "cooling_kw": kc, "heating_btu": bh, "heating_kw": kh,
        "power_input": pw, "dimensions": dim, "weight": wt, "airflow": af, "noise": ns,
        "gas_pipe": pipe, "drain_pipe": drn, "price": 0, "unit": "Dàn", "origin": "Thái Lan",
        "image": f"assets/products/{img}", "commercial_img": f"assets/commercial/{cimg}" if cimg else "",
        "catalog_pdf": "DAIKIN VRV TỔNG HỢP.pdf", "catalog_page": pg,
        "notes": "Tham chiếu chính xác Catalogue VRV Tổng Hợp Daikin Việt Nam."
    })

vam_list = [
    ("VAM150HVE", "150 m³/h", "96-103 W", "278x551x810", "22 kg", "150 / 100 m³/h", "33.0-34.0 / 23.0-25.5 dB(A)", "Ø100 mm", 10),
    ("VAM250HVE", "250 m³/h", "126-141 W", "278x551x810", "22 kg", "250 / 165 m³/h", "33.0-34.0 / 23.0-25.5 dB(A)", "Ø150 mm", 10),
    ("VAM350HVE", "350 m³/h", "178-193 W", "306x800x879", "31 kg", "350 / 275 m³/h", "32.0-33.0 / 26.5-28.5 dB(A)", "Ø150 mm", 10),
    ("VAM500HVE", "500 m³/h", "296-326 W", "306x800x879", "41 kg", "500 / 470 m³/h", "36.0-37.0 / 32.0-34.0 dB(A)", "Ø200 mm", 10),
    ("VAM650HVE", "650 m³/h", "381-426 W", "338x832x973", "43 kg", "650 / 570 m³/h", "37.5-38.0 / 34.0-35.0 dB(A)", "Ø200 mm", 10),
    ("VAM800HVE", "800 m³/h", "539-569 W", "387x1012x1110", "63 kg", "800 / 720 m³/h", "38.0-40.5 / 36.0-38.5 dB(A)", "Ø250 mm", 11),
    ("VAM1000HVE", "1000 m³/h", "683-736 W", "387x1012x1110", "63 kg", "1000 / 880 m³/h", "41.5-42.5 / 38.0-39.5 dB(A)", "Ø250 mm", 11),
    ("VAM1500HVE", "1500 m³/h", "1274-1353 W", "785x1012x1110", "133 kg", "1500 / 1350 m³/h", "43.0-44.0 / 38.0-40.5 dB(A)", "Ø250 x 4 (trong) | Hộp 680x290 x 2 (ngoài)", 11),
    ("VAM2000HVE", "2000 m³/h", "1365-1471 W", "785x1012x1110", "133 kg", "2000 / 1650 m³/h", "43.5-44.0 / 39.0-41.0 dB(A)", "Ø250 x 4 (trong) | Hộp 680x290 x 2 (ngoài)", 11),
]
for m, cap, pw, dim, wt, af, ns, collar, pg in vam_list:
    add_prod({
        "id": m, "model": m, "category_id": "VRV_HRV",
        "name": f"Thiết bị thông gió thu hồi nhiệt HRV Daikin {cap} ({m})",
        "hp": cap, "cooling_btu": 0, "cooling_kw": 0, "heating_btu": 0, "heating_kw": 0,
        "power_input": pw, "refrigerant": "Trao đổi nhiệt Enthalpy",
        "dimensions": dim, "weight": wt, "airflow": af, "noise": ns,
        "gas_pipe": f"Cổ ống gió kết nối: {collar}", "drain_pipe": "Không cần thoát nước ngưng",
        "duct": {"supply_collar": collar, "return_collar": collar, "mouth_w": 250, "mouth_h": 250, "insul_m2": 0,
                 "propose": f"Kết nối 4 cổ ống gió tròn {collar} (OA, EA, SA, RA)", "std_box": f"Cổ nối tiêu chuẩn {collar} bọc bảo ôn chống đọng sương nhánh OA/EA"},
        "price": 0, "unit": "Bộ", "origin": "Nhật Bản / TQ",
        "image": "assets/products/hrv_vam.png", "commercial_img": "assets/commercial/mp_vam.png",
        "catalog_pdf": "THIẾT BỊ THU HỒI NHIỆT HRV.pdf", "catalog_page": pg,
        "notes": "Cấp khí tươi giàu Oxy và thu hồi nhiệt năng (tiết kiệm tới 28% tải điều hòa)."
    })

# ==============================================================================
# 8. VRV CONTROLLERS & REFNET JOINTS (Exact from BÁO GIÁ VRV.xlsx rows 94-113)
# ==============================================================================
vrv_acc_list = [
    ("BRC1E63", "Điều khiển có dây tiêu chuẩn BRC1E63 (LCD điều hướng)", "Cái", 696000, "120x120x19", "0.2 kg", "ctrl_wired_brc1e63.png", "mp_brc1e63.png", "DAIKIN VRV TỔNG HỢP.pdf", 253, "Điều khiển dây phổ biến nhất cho dàn lạnh VRV & SkyAir."),
    ("BRC1H63W", "Điều khiển có dây cảm ứng cao cấp Madoka BRC1H63W (Bluetooth)", "Cái", 1350000, "85x85x19", "0.15 kg", "ctrl_madoka.png", "", "DAIKIN VRV TỔNG HỢP.pdf", 252, "Thiết kế đạt giải Red Dot, kết nối Bluetooth qua app Madoka Assistant."),
    ("BRC2E61", "Điều khiển có dây đơn giản nhỏ gọn BRC2E61", "Cái", 696000, "85x85x19", "0.14 kg", "ctrl_wired_simple.png", "mp_brc2e61.png", "DAIKIN VRV TỔNG HỢP.pdf", 254, "Thiết kế 85x85mm nhỏ gọn chuyên dùng cho khách sạn."),
    ("BRC1F61-9", "Điều khiển có dây cho dàn lạnh Cassette 1 hướng thổi (BRC1F61-9)", "Cái", 1213000, "120x120x19", "0.2 kg", "ctrl_wired_brc1e63.png", "", "DAIKIN VRV TỔNG HỢP.pdf", 253, "Dùng cho dàn lạnh Cassette 1 hướng thổi."),
    ("BRC7EA618-9", "Điều khiển không dây từ xa cho dàn lạnh Treo tường (BRC7EA618-9)", "Cái", 1404000, "155x52x18", "0.18 kg", "ctrl_wireless.png", "mp_brc7m.png", "DAIKIN VRV TỔNG HỢP.pdf", 254, "Bao gồm tay cầm từ xa + bộ nhận hồng ngoại cho FXAQ."),
    ("BRC4M61", "Điều khiển không dây từ xa cho dàn lạnh Cassette 1 hướng thổi (BRC4M61)", "Cái", 1404000, "155x52x18", "0.18 kg", "ctrl_wireless.png", "mp_brc7m.png", "DAIKIN VRV TỔNG HỢP.pdf", 254, "Bao gồm tay cầm từ xa + mắt nhận hồng ngoại."),
    ("BRC7M65", "Điều khiển không dây từ xa cho dàn lạnh Cassette 2 hướng thổi (BRC7M65)", "Cái", 2079000, "155x52x18", "0.2 kg", "ctrl_wireless.png", "mp_brc7m.png", "DAIKIN VRV TỔNG HỢP.pdf", 254, "Dành cho dòng FXCQ."),
    ("BRC7M634F", "Điều khiển không dây từ xa cho dàn lạnh Cassette đa hướng thổi (BRC7M634F)", "Cái", 1247000, "155x52x18", "0.2 kg", "ctrl_wireless.png", "mp_brc7m.png", "DAIKIN VRV TỔNG HỢP.pdf", 193, "Lắp tích hợp góc mặt nạ BYCQ125EAF cho dòng FXFQ."),
    ("BRC4C65", "Điều khiển không dây từ xa cho dàn lạnh Giấu trần nối ống gió (BRC4C65)", "Cái", 1247000, "155x52x18", "0.22 kg", "ctrl_wireless.png", "mp_brc7m.png", "DAIKIN VRV TỔNG HỢP.pdf", 254, "Gồm tay điều khiển + mắt nhận gắn tường/trần cho FXDQ, FXSQ, FXMQ."),
    ("BRC301B61", "Điều khiển có dây chuyên dụng cho thiết bị HRV (BRC301B61)", "Cái", 830000, "120x120x19", "0.2 kg", "ctrl_wired_simple.png", "", "THIẾT BỊ THU HỒI NHIỆT HRV.pdf", 8, "Điều khiển độc lập cho thiết bị thu hồi nhiệt VAM-HVE."),
    ("DCS301BA61", "Điều khiển trung tâm loại ON/OFF thống nhất (DCS301BA61)", "Cái", 4850000, "120x120x55", "0.4 kg", "ctrl_central_itm.png", "", "ĐIỀU KHIỂN TRUNG TÂM DAIKIN.pdf", 6, "Điều khiển Bật/Tắt đồng loạt tối đa 16 nhóm (128 dàn lạnh)."),
    ("DCS302CA61", "Điều khiển trung tâm tiêu chuẩn Central Remote (DCS302CA61)", "Cái", 11900000, "180x240x55", "0.8 kg", "ctrl_central_itm.png", "", "ĐIỀU KHIỂN TRUNG TÂM DAIKIN.pdf", 6, "Quản lý tối đa 64 nhóm dàn lạnh độc lập qua DIII-NET."),
    ("DCS303A51", "Điều khiển trung tâm cho biệt thự / nhà riêng (DCS303A51)", "Cái", 9500000, "180x120x50", "0.5 kg", "ctrl_central_itm.png", "", "ĐIỀU KHIỂN TRUNG TÂM DAIKIN.pdf", 8, "Lập lịch và giám sát tập trung cho biệt thự."),
    ("DCM601A51", "Bộ điều khiển trung tâm thông minh cảm ứng iTM (DCM601A51)", "Cái", 46500000, "290x208x55", "2.4 kg", "ctrl_central_itm.png", "", "Intelligent touch Manager.pdf", 14, "Màn hình cảm ứng màu quản lý 64 nhóm (mở rộng tới 512 nhóm với iTM Plus)."),
    ("DCM601A52", "Adaptor mở rộng iTM Plus cho điều khiển trung tâm (DCM601A52)", "Cái", 19800000, "160x195x45", "0.9 kg", "ctrl_central_itm.png", "", "Intelligent touch Manager.pdf", 15, "Mở rộng thêm 64 nhóm dàn lạnh cho hệ thống iTM."),
    ("DCM002A51", "Phần mềm tính tiền điện năng tiêu thụ PPD cho iTM (DCM002A51)", "Code", 28500000, "License Key", "—", "ctrl_central_itm.png", "", "Intelligent touch Manager.pdf", 14, "Phân bổ chi phí điện năng từng phòng/khu thuê cho tòa nhà."),
    ("BFHP22R135", "Bộ chia gas kết nối 2 dàn nóng VRV (Model: BHFP22R135 / BFHP22R135)", "Bộ", 2043000, "Bộ ống đồng chữ Y", "2.2 kg", "refnet_outdoor.png", "mp_refnet_out.png", "Catalogue Điều Hòa Trung tâm VRV H Daikin 2025.pdf", 26, "Dùng ghép đôi 02 dàn nóng từ RXYQ26BYM đến RXYQ48BYM."),
    ("BFHP22R168", "Bộ chia gas kết nối 3 dàn nóng VRV (Model: BHFP22R168 / BFHP22R168)", "Bộ", 3958000, "Bộ ống đồng 3 nhánh", "4.1 kg", "refnet_outdoor.png", "mp_refnet_out.png", "Catalogue Điều Hòa Trung tâm VRV H Daikin 2025.pdf", 26, "Dùng ghép tổ hợp 03 dàn nóng từ RXYQ50BYM đến RXYQ60BYM."),
    ("KHRP26A22T8", "Bộ chia gas dàn lạnh REFNET Joint (Model: KHRP26A22T8)", "Bộ", 1277000, "Bộ Y đồng + bảo ôn", "1.1 kg", "refnet_indoor.png", "mp_refnet_in.png", "Catalogue Điều Hòa Trung tâm VRV H Daikin 2025.pdf", 26, "Tổng chỉ số công suất dàn lạnh sau bộ chia < 200 (< 8HP)."),
    ("KHRP26A33T8", "Bộ chia gas dàn lạnh REFNET Joint (Model: KHRP26A33T8)", "Bộ", 1468000, "Bộ Y đồng + bảo ôn", "1.4 kg", "refnet_indoor.png", "mp_refnet_in.png", "Catalogue Điều Hòa Trung tâm VRV H Daikin 2025.pdf", 26, "Tổng chỉ số công suất dàn lạnh sau bộ chia từ 200 đến < 290."),
    ("KHRP26A72T8", "Bộ chia gas dàn lạnh REFNET Joint (Model: KHRP26A72T8)", "Bộ", 1915000, "Bộ Y đồng + bảo ôn", "2.1 kg", "refnet_indoor.png", "mp_refnet_in.png", "Catalogue Điều Hòa Trung tâm VRV H Daikin 2025.pdf", 26, "Tổng chỉ số công suất dàn lạnh sau bộ chia từ 290 đến < 640."),
    ("KHRP26A73T8", "Bộ chia gas dàn lạnh cỡ lớn (Model: KHRP26A73T8 + KHRP26M73TP8)", "Bộ", 3001000, "Bộ Y đồng lớn + bảo ôn", "3.2 kg", "refnet_indoor.png", "mp_refnet_in.png", "Catalogue Điều Hòa Trung tâm VRV H Daikin 2025.pdf", 26, "Tổng chỉ số công suất dàn lạnh sau bộ chia >= 640."),
]
for m, nm, un, pr, dim, wt, img, cimg, pdf, pg, nt in vrv_acc_list:
    add_prod({
        "id": m, "model": m, "category_id": "VRV_ACC", "name": nm,
        "hp": "Phụ kiện VRV", "cooling_btu": 0, "cooling_kw": 0, "heating_btu": 0, "heating_kw": 0,
        "power_input": "—", "dimensions": dim, "weight": wt, "airflow": "—", "noise": "—",
        "gas_pipe": "Đồng nguyên chất chuẩn Daikin" if "HRP" in m or "FHP" in m else "Cáp tín hiệu F1-F2 (2x0.75-1.5mm²)",
        "drain_pipe": "—", "price": pr, "unit": un, "origin": "Thái Lan / Nhật Bản",
        "image": f"assets/products/{img}", "commercial_img": f"assets/commercial/{cimg}" if cimg else "",
        "catalog_pdf": pdf, "catalog_page": pg, "notes": nt
    })

# ==============================================================================
# 9. ROOM AIR WALL SPLIT (FTHF25 -> FTHF71) - Prices from BÁO GIÁ VRV.xlsx
# ==============================================================================
fthf_list = [
    ("FTHF25RAVMV/RHF25RAVMV", "1.0 HP", 9000, 2.6, 11600, 3.4, "0.70 kW", "DL: 283x770x226 | DN: 550x658x275", "DL: 8 kg | DN: 27 kg", "10.2 m³/phút", "25-38 dB(A)", "Ø6.4 / Ø9.5", "Việt Nam", 9412000),
    ("FTHF35RAVMV/RHF35RAVMV", "1.5 HP", 12000, 3.5, 13600, 4.0, "0.98 kW", "DL: 283x770x226 | DN: 550x658x275", "DL: 8 kg | DN: 27 kg", "10.8 m³/phút", "26-39 dB(A)", "Ø6.4 / Ø9.5", "Việt Nam", 11474000),
    ("FTHF50RVMV/RHF50RVMV", "2.0 HP", 18000, 5.2, 20500, 6.0, "1.38 kW", "DL: 295x990x266 | DN: 595x845x300", "DL: 13 kg | DN: 36 kg", "16.5 m³/phút", "31-44 dB(A)", "Ø6.4 / Ø12.7", "Thái Lan", 17454000),
    ("FTHF60RVMV/RHF60RVMV", "2.5 HP", 20500, 6.0, 22200, 6.5, "1.78 kW", "DL: 295x990x266 | DN: 595x845x300", "DL: 13 kg | DN: 36 kg", "18.8 m³/phút", "33-45 dB(A)", "Ø6.4 / Ø12.7", "Thái Lan", 24064000),
    ("FTHF71RVMV/RHF71RVMV", "3.0 HP", 24000, 7.1, 25600, 7.5, "2.35 kW", "DL: 295x990x266 | DN: 595x845x300", "DL: 13 kg | DN: 39 kg", "19.8 m³/phút", "34-46 dB(A)", "Ø6.4 / Ø15.9", "Thái Lan", 27126000),
]
for m, hp, bc, kc, bh, kh, pw, dim, wt, af, ns, pipe, orig, pr in fthf_list:
    add_prod({
        "id": m.replace("/", "_"), "model": m, "category_id": "ROOM_AIR",
        "name": f"Điều hòa cục bộ treo tường 2 chiều Inverter {bc:,} Btu/h".replace(",", "."),
        "hp": hp, "cooling_btu": bc, "cooling_kw": kc, "heating_btu": bh, "heating_kw": kh,
        "power_input": pw, "refrigerant": "R32", "dimensions": dim, "weight": wt, "airflow": af, "noise": ns,
        "gas_pipe": pipe, "drain_pipe": "Ø16 mm mềm", "price": pr, "unit": "Bộ", "origin": orig,
        "image": "assets/products/wall_fthf.png",
        "catalog_pdf": "Catalogue kỹ thuật máy cục bộ Daikin ( đặt cửa gió).pdf", "catalog_page": 3,
        "web_url": "https://www.daikin.com.vn/san-pham/dieu-hoa-dan-dung",
        "notes": "Luồng gió Coanda dễ chịu, Mắt thần thông minh tiết kiệm điện, Gas R32."
    })

# ==============================================================================
# 10. SKYAIR CASSETTE (FCQ50KAVEA..FCQ140KAVEA + R32 FCFC40..140DVM)
# ==============================================================================
fcq_list = [
    ("FCQ50KAVEA/RZQS50AV1", "2.0 HP", 18000, 5.0, "1 pha, 220V", "DL: 256x840x840 | DN: 595x845x300", "DL: 21 kg | DN: 43 kg", "16/13.5/11 m³/phút", "Ø6.4 / Ø12.7", 26969000),
    ("FCQ60KAVEA/RZQS60AV1", "2.5 HP", 20500, 6.0, "1 pha, 220V", "DL: 256x840x840 | DN: 770x900x320", "DL: 21 kg | DN: 64 kg", "19/16/13 m³/phút", "Ø6.4 / Ø12.7", 33388000),
    ("FCQ71KAVEA/RZQ71LV1", "3.0 HP", 24000, 7.1, "1 pha, 220V", "DL: 256x840x840 | DN: 770x900x320", "DL: 21 kg | DN: 64 kg", "21/17/13.5 m³/phút", "Ø9.5 / Ø15.9", 34231000),
    ("FCQ100KAVEA/RZQ100LV1", "4.0 HP (1P)", 34000, 10.0, "1 pha, 220V", "DL: 298x840x840 | DN: 990x940x320", "DL: 24 kg | DN: 75 kg", "32/26/20 m³/phút", "Ø9.5 / Ø15.9", 39733000),
    ("FCQ100KAVEA/RZQ100HAY4A", "4.0 HP (3P)", 34000, 10.0, "3 pha, 380V", "DL: 298x840x840 | DN: 990x940x320", "DL: 24 kg | DN: 95 kg", "32/26/20 m³/phút", "Ø9.5 / Ø15.9", 40789000),
    ("FCQ125KAVEA/RZQ125LV1", "5.0 HP (1P)", 42000, 12.5, "1 pha, 220V", "DL: 298x840x840 | DN: 1170x900x320", "DL: 24 kg | DN: 98 kg", "33/28/22.5 m³/phút", "Ø9.5 / Ø15.9", 43300000),
    ("FCQ125KAVEA/RZQ125HAY4A", "5.0 HP (3P)", 42000, 12.5, "3 pha, 380V", "DL: 298x840x840 | DN: 1345x900x320", "DL: 24 kg | DN: 103 kg", "33/28/22.5 m³/phút", "Ø9.5 / Ø15.9", 44450000),
    ("FCQ140KAVEA/RZQ140LV1", "5.5 HP (1P)", 45000, 14.0, "1 pha, 220V", "DL: 298x840x840 | DN: 1430x940x320", "DL: 24 kg | DN: 101 kg", "33.5/28.5/23 m³/phút", "Ø9.5 / Ø15.9", 47094000),
    ("FCQ140KAVEA/RZQ140HAY4A", "5.5 HP (3P)", 45000, 14.0, "3 pha, 380V", "DL: 298x840x840 | DN: 1430x940x320", "DL: 24 kg | DN: 108 kg", "33.5/28.5/23 m³/phút", "Ø9.5 / Ø15.9", 48267000),
]
for m, hp, bc, kc, pwr, dim, wt, af, pipe, pr in fcq_list:
    add_prod({
        "id": m.replace("/", "_"), "model": m, "category_id": "SKY_CASSETTE",
        "name": f"Điều hòa SkyAir Cassette âm trần Inverter {bc:,} Btu/h ({hp})".replace(",", "."),
        "hp": hp, "cooling_btu": bc, "cooling_kw": kc, "heating_btu": int(bc*1.1), "heating_kw": round(kc*1.1, 1),
        "power_input": f"{round(kc/3.3, 2)} kW", "power_supply": pwr, "refrigerant": "R410A / Inverter",
        "dimensions": dim, "weight": wt, "airflow": af, "noise": "32 - 44 dB(A)",
        "gas_pipe": pipe, "drain_pipe": "VP25 (Có bơm nâng 850mm)",
        "ceiling_opening": "860x860 - 910x910 mm", "panel_model": "BYCP125K-W18 / BYCQ125EAF", "panel_dim": "50x950x950 mm",
        "price": pr, "unit": "Bộ", "origin": "Thái Lan",
        "image": "assets/products/cassette_roundflow.png", "commercial_img": "assets/commercial/mp_fxfq.png",
        "catalog_pdf": "SKY TỔNG HỢP 2023.pdf", "catalog_page": 96,
        "notes": "Bộ máy thương mại SkyAir Cassette đa hướng thổi chính hãng Daikin."
    })

# ==============================================================================
# 11. SKYAIR DUCTED (FBQ50..140EVE with prices + FBFC40..140DVM & FDF50..60BV1 from BẢNG CÔN ĐẦU)
# ==============================================================================
fbq_list = [
    ("FBQ50EVE/RZQS50AV1", "2.0 HP", 18000, 5.0, "1 pha, 220V", "DL: 245x1000x800 | DN: 595x845x300", "DL: 37 kg | DN: 43 kg", "18.0/15.0/12.5 m³/phút", "Ø6.4 / Ø12.7", 25897000, "795x180", "955x210", 795, 180, 0.585, "Côn đầu máy H250 + 3 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 795 x 220, Giật cổ 795x180 để thẳng 60/795x220/ H250, trổ đỉnh 3D200"),
    ("FBQ60EVE/RZQS60AV1", "2.5 HP", 20500, 6.0, "1 pha, 220V", "DL: 245x1000x800 | DN: 770x900x320", "DL: 37 kg | DN: 64 kg", "21.0/17.5/13.5 m³/phút", "Ø6.4 / Ø12.7", 32137000, "795x180", "955x210", 795, 180, 0.585, "Côn đầu máy H250 + 3 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 795 x 220, Giật cổ 795x180 để thẳng 60/795x220/ H250, trổ đỉnh 3D200"),
    ("FBQ71EVE/RZQ71LV1", "3.0 HP", 24000, 7.1, "1 pha, 220V", "DL: 245x1000x800 | DN: 770x900x320", "DL: 37 kg | DN: 64 kg", "23.0/19.5/16.0 m³/phút", "Ø9.5 / Ø15.9", 32805000, "795x180", "955x210", 795, 180, 0.585, "Côn đầu máy H250 + 4 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1000 x 220, Giật cổ 795x180 để thẳng 60/1000x220/ H250, trổ đỉnh 4D200"),
    ("FBQ100EVE/RZQ100LV1", "4.0 HP (1P)", 34000, 10.0, "1 pha, 220V", "DL: 245x1400x800 | DN: 990x940x320", "DL: 47 kg | DN: 75 kg", "32.0/27.0/22.5 m³/phút", "Ø9.5 / Ø15.9", 38192000, "1195x180", "1355x210", 1195, 180, 0.990, "Côn đầu máy H300 + 4 cổ D250 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1260 x 220, Giật cổ 1195x180 để thẳng 60/1260x220/ H300, trổ đỉnh 5D200"),
    ("FBQ100EVE/RZQ100HAY4A", "4.0 HP (3P)", 34000, 10.0, "3 pha, 380V", "DL: 245x1400x800 | DN: 990x940x320", "DL: 47 kg | DN: 95 kg", "32.0/27.0/22.5 m³/phút", "Ø9.5 / Ø15.9", 39248000, "1195x180", "1355x210", 1195, 180, 0.990, "Côn đầu máy H300 + 4 cổ D250 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1260 x 220, Giật cổ 1195x180 để thẳng 60/1260x220/ H300, trổ đỉnh 5D200"),
    ("FBQ125EVE/RZQ125LV1", "5.0 HP (1P)", 42000, 12.5, "1 pha, 220V", "DL: 245x1400x800 | DN: 1170x900x320", "DL: 47 kg | DN: 98 kg", "33.0/28.0/22.5 m³/phút", "Ø9.5 / Ø15.9", 41612000, "1195x180", "1355x210", 1195, 180, 0.990, "Côn đầu máy H300 + 4 cổ D250 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1520 x 220, Giật cổ 1195x180 để thẳng 60/1520x220/ H300, trổ đỉnh 6D200"),
    ("FBQ125EVE/RZQ125HAY4A", "5.0 HP (3P)", 42000, 12.5, "3 pha, 380V", "DL: 245x1400x800 | DN: 1345x900x320", "DL: 47 kg | DN: 103 kg", "33.0/28.0/22.5 m³/phút", "Ø9.5 / Ø15.9", 42763000, "1195x180", "1355x210", 1195, 180, 0.990, "Côn đầu máy H300 + 4 cổ D250 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1520 x 220, Giật cổ 1195x180 để thẳng 60/1520x220/ H300, trổ đỉnh 6D200"),
    ("FBQ140EVE/RZQ140LV1", "5.5 HP (1P)", 45000, 14.0, "1 pha, 220V", "DL: 245x1400x800 | DN: 1430x940x320", "DL: 47 kg | DN: 101 kg", "36.0/30.5/25.0 m³/phút", "Ø9.5 / Ø15.9", 45321000, "1195x180", "1355x210", 1195, 180, 0.990, "Côn đầu máy H300 + 4 cổ D250 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1520 x 220, Giật cổ 1195x180 để thẳng 60/1520x220/ H300, trổ đỉnh 6D200"),
    ("FBQ140EVE/RZQ140HAY4A", "5.5 HP (3P)", 45000, 14.0, "3 pha, 380V", "DL: 245x1400x800 | DN: 1430x940x320", "DL: 47 kg | DN: 108 kg", "36.0/30.5/25.0 m³/phút", "Ø9.5 / Ø15.9", 46493000, "1195x180", "1355x210", 1195, 180, 0.990, "Côn đầu máy H300 + 4 cổ D250 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1520 x 220, Giật cổ 1195x180 để thẳng 60/1520x220/ H300, trổ đỉnh 6D200"),
]
for m, hp, bc, kc, pwr, dim, wt, af, pipe, pr, sc, rc, mw, mh, ins, prop, sbox in fbq_list:
    add_prod({
        "id": m.replace("/", "_"), "model": m, "category_id": "SKY_DUCT",
        "name": f"Điều hòa SkyAir Giấu trần nối ống gió {bc:,} Btu/h ({hp})".replace(",", "."),
        "hp": hp, "cooling_btu": bc, "cooling_kw": kc, "heating_btu": int(bc*1.1), "heating_kw": round(kc*1.1, 1),
        "power_input": f"{round(kc/3.2, 2)} kW", "power_supply": pwr, "refrigerant": "R410A / Inverter",
        "dimensions": dim, "weight": wt, "airflow": af, "noise": "33 - 40 dB(A)", "esp": "50 - 150 Pa",
        "gas_pipe": pipe, "drain_pipe": "VP25 (Có bơm nước xả)",
        "duct": {"supply_collar": sc, "return_collar": rc, "mouth_w": mw, "mouth_h": mh, "insul_m2": ins, "propose": prop, "std_box": sbox},
        "price": pr, "unit": "Bộ", "origin": "Thái Lan",
        "image": "assets/products/duct_med_fxsq.png",
        "catalog_pdf": "SKY TỔNG HỢP 2023.pdf", "catalog_page": 89,
        "notes": "Máy cục bộ thương mại giấu trần nối ống gió áp suất tĩnh trung bình."
    })

# Exact SkyAir R32 models from BẢNG CÔN ĐẦU DÀN LẠNH DAIKIN - E HOAN.xlsx (rows 27-41) + SKY TỔNG HỢP 2023.pdf p.98 & Engineering Data p.23
sky_r32_duct = [
    ("FDF50BV1/RZF50CV2V", "2.0 HP (1P)", 17100, 5.0, "1.51 kW", "1 pha, 220V", "DL: 200x1100x620 | DN: 595x845x300", "DL: 30 kg | DN: 41 kg", "16/13.5 m³/phút (960 m³/h)", "38/34 dB(A)", "40 Pa", "Ø9.5 / Ø15.9", "1065x175", "1005x175", 1065, 175, 0.744, "Côn đầu máy, H250 + 3 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1065 x 220, Giật cổ 1065x175 để thẳng 60/1065 x 220/ H250, trổ đỉnh 3D200", "duct_slim_compact.png", "Catalogue kỹ thuật máy cục bộ Daikin ( đặt cửa gió).pdf", 23),
    ("FDF60BV1/RZF60CV2V", "2.5 HP (1P)", 20500, 6.0, "1.98 kW", "1 pha, 220V", "DL: 200x1100x620 | DN: 595x845x300", "DL: 30 kg | DN: 41 kg", "16/13.5 m³/phút (960 m³/h)", "38/34 dB(A)", "40 Pa", "Ø9.5 / Ø15.9", "1065x175", "1005x175", 1065, 175, 0.744, "Côn đầu máy, H250 + 4 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1065 x 220, Giật cổ 1065x175 để thẳng 60/1065 x 220/ H250, trổ đỉnh 3D200", "duct_slim_compact.png", "Catalogue kỹ thuật máy cục bộ Daikin ( đặt cửa gió).pdf", 23),
    ("FBFC40DVM/RZFC40DVM", "1.5 HP (1P)", 13600, 4.0, "1.19 kW", "1 pha, 220V", "DL: 245x700x800 | DN: 595x845x300", "DL: 26 kg | DN: 34 kg", "15.5/12/9 m³/phút (TB 720 m³/h)", "37/35/30 dB(A)", "30-130 Pa (ĐM 30Pa)", "Ø6.4 / Ø12.7", "495x180", "660x210", 495, 180, 0.405, "Côn đầu máy (a.b), H250 + 2 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 495 x 220, Giật cổ 495 x 180 để thẳng 60/480 x 220/ H250, trổ đỉnh 2D200", "duct_med_fxsq.png", "SKY TỔNG HỢP 2023.pdf", 98),
    ("FBFC50DVM/RZFC50DVM", "2.0 HP (1P)", 17000, 5.0, "1.56 kW", "1 pha, 220V", "DL: 245x700x800 | DN: 595x845x300", "DL: 26 kg | DN: 37 kg", "15.5/12/9 m³/phút (TB 720 m³/h)", "37/35/30 dB(A)", "30-130 Pa (ĐM 30Pa)", "Ø6.4 / Ø12.7", "495x180", "660x210", 495, 180, 0.405, "Côn đầu máy (a.b), H250 + 2 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 495 x 220, Giật cổ 495 x 180 để thẳng 60/480 x 220/ H250, trổ đỉnh 2D200", "duct_med_fxsq.png", "SKY TỔNG HỢP 2023.pdf", 98),
    ("FBFC60DVM/RZFC60DVM", "2.5 HP (1P)", 20500, 6.0, "2.07 kW", "1 pha, 220V", "DL: 245x700x800 | DN: 595x845x300", "DL: 26 kg | DN: 44 kg", "15.5/12/9 m³/phút (TB 720 m³/h)", "37/35/30 dB(A)", "30-130 Pa (ĐM 30Pa)", "Ø6.4 / Ø12.7", "495x180", "660x210", 495, 180, 0.405, "Côn đầu máy (a.b), H250 + 2 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 495 x 220, Giật cổ 495 x 180 để thẳng 60/480 x 220/ H250, trổ đỉnh 2D200", "duct_med_fxsq.png", "SKY TỔNG HỢP 2023.pdf", 98),
    ("FBFC71DVM/RZFC71DVM", "3.0 HP (1P)", 24200, 7.1, "2.37 kW", "1 pha, 220V", "DL: 245x1000x800 | DN: 695x930x350", "DL: 36 kg | DN: 44 kg", "25/20/16.5 m³/phút (TB 1200 m³/h)", "39/37/34 dB(A)", "40-140 Pa (ĐM 40Pa)", "Ø9.5 / Ø15.9", "795x180", "955x210", 795, 180, 0.585, "Côn đầu máy (a.b), H250 + 3 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1000 x 220, Giật cổ 795 x 180 để thẳng 60/1000 x 220/ H250, trổ đỉnh 4D200", "duct_med_fxsq.png", "SKY TỔNG HỢP 2023.pdf", 98),
    ("FBFC71DVM/RZFC71DY1", "3.0 HP (3P)", 24200, 7.1, "2.37 kW", "3 pha, 380V", "DL: 245x1000x800 | DN: 695x930x350", "DL: 36 kg | DN: 46 kg", "25/20/16.5 m³/phút (TB 1200 m³/h)", "39/37/34 dB(A)", "40-140 Pa (ĐM 40Pa)", "Ø9.5 / Ø15.9", "795x180", "955x210", 795, 180, 0.585, "Côn đầu máy (a.b), H250 + 4 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1000 x 220, Giật cổ 795 x 180 để thẳng 60/1000 x 220/ H250, trổ đỉnh 4D200", "duct_med_fxsq.png", "SKY TỔNG HỢP 2023.pdf", 98),
    ("FBFC85DVM/RZFC85DVM", "3.5 HP (1P)", 29000, 8.5, "2.74 kW", "1 pha, 220V", "DL: 245x1000x800 | DN: 695x930x350", "DL: 36 kg | DN: 46 kg", "25/20/16.5 m³/phút (TB 1200 m³/h)", "39/37/34 dB(A)", "40-140 Pa (ĐM 40Pa)", "Ø9.5 / Ø15.9", "795x180", "955x210", 795, 180, 0.702, "Côn đầu máy (a.b), H250 + 4 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1000 x 220, Giật cổ 795 x 180 để thẳng 60/1000 x 220/ H250, trổ đỉnh 4D200", "duct_med_fxsq.png", "SKY TỔNG HỢP 2023.pdf", 98),
    ("FBFC85DVM/RZFC85DY1", "3.5 HP (3P)", 29000, 8.5, "2.74 kW", "3 pha, 380V", "DL: 245x1000x800 | DN: 695x930x350", "DL: 36 kg | DN: 46 kg", "25/20/16.5 m³/phút (TB 1200 m³/h)", "39/37/34 dB(A)", "40-140 Pa (ĐM 40Pa)", "Ø9.5 / Ø15.9", "795x180", "955x210", 795, 180, 0.585, "Côn đầu máy (a.b), H250 + 4 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1000 x 220, Giật cổ 795 x 180 để thẳng 60/1000 x 220/ H250, trổ đỉnh 4D200", "duct_med_fxsq.png", "SKY TỔNG HỢP 2023.pdf", 98),
    ("FBFC100DVM/RZFC100DVM", "4.0 HP (1P)", 34100, 10.0, "3.17 kW", "1 pha, 220V", "DL: 245x1400x800 | DN: 695x930x350", "DL: 46 kg | DN: 62 kg", "36/30.5/25 m³/phút (TB 1830 m³/h)", "40/37.5/35 dB(A)", "50-150 Pa (ĐM 50Pa)", "Ø9.5 / Ø15.9", "1195x180", "1355x210", 1195, 180, 0.990, "Côn đầu máy (a.b), H300 + 4 cổ D250 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1260 x 220, Giật cổ 1195 x 180 để thẳng 60/1260 x 220/ H300, trổ đỉnh 5D200", "duct_med_fxsq.png", "SKY TỔNG HỢP 2023.pdf", 98),
    ("FBFC100DVM/RZFC100DY1", "4.0 HP (3P)", 34100, 10.0, "3.17 kW", "3 pha, 380V", "DL: 245x1400x800 | DN: 990x940x320", "DL: 46 kg | DN: 62 kg", "36/30.5/25 m³/phút (TB 1830 m³/h)", "40/37.5/35 dB(A)", "50-150 Pa (ĐM 50Pa)", "Ø9.5 / Ø15.9", "1195x180", "1355x210", 1195, 180, 0.990, "Côn đầu máy (a.b), H300 + 4 cổ D250 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1520 x 220, Giật cổ 1195x180 để thẳng 60/1520 x 220/ H300, trổ đỉnh 6D200", "duct_med_fxsq.png", "SKY TỔNG HỢP 2023.pdf", 98),
    ("FBFC125DVM/RZFC125DY1", "5.0 HP (3P)", 42700, 12.5, "5.21 kW", "3 pha, 380V", "DL: 245x1400x800 | DN: 990x940x320", "DL: 46 kg | DN: 62 kg", "36/30.5/25 m³/phút (TB 1830 m³/h)", "40/37.5/35 dB(A)", "50-150 Pa (ĐM 50Pa)", "Ø9.5 / Ø15.9", "1195x180", "1355x210", 1195, 180, 0.990, "Côn đầu máy (a.b), H300 + 4 cổ D250 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1520 x 220, Giật cổ 1195x180 để thẳng 60/1520 x 220/ H300, trổ đỉnh 6D200", "duct_med_fxsq.png", "SKY TỔNG HỢP 2023.pdf", 98),
    ("FBFC140DVM/RZFC140DY1", "5.5 HP (3P)", 47800, 14.0, "6.22 kW", "3 pha, 380V", "DL: 245x1400x800 | DN: 990x940x320", "DL: 46 kg | DN: 62 kg", "36/30.5/25 m³/phút (TB 1830 m³/h)", "40/37.5/35 dB(A)", "50-150 Pa (ĐM 50Pa)", "Ø9.5 / Ø15.9", "1195x180", "1355x210", 1195, 180, 0.990, "Côn đầu máy (a.b), H300 + 4 cổ D250 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1520 x 220, Giật cổ 1195x180 để thẳng 60/1520 x 220/ H300, trổ đỉnh 6D200", "duct_med_fxsq.png", "SKY TỔNG HỢP 2023.pdf", 98),
]
for m, hp, bc, kc, pw, pwr, dim, wt, af, ns, esp, pipe, sc, rc, mw, mh, ins, prop, sbox, img, pdf, pg in sky_r32_duct:
    add_prod({
        "id": m.replace("/", "_"), "model": m, "category_id": "SKY_DUCT",
        "name": f"Điều hòa SkyAir R32 Giấu trần nối ống gió {bc:,} Btu/h ({hp})".replace(",", "."),
        "hp": hp, "cooling_btu": bc, "cooling_kw": kc, "heating_btu": 0, "heating_kw": 0,
        "power_input": pw, "power_supply": pwr, "refrigerant": "R32 Inverter",
        "dimensions": dim, "weight": wt, "airflow": af, "noise": ns, "esp": esp,
        "gas_pipe": pipe, "drain_pipe": "VP20 (Ngoài Ø26 / Trong Ø20)" if "FDF" in m else "VP25 (Có bơm nước xả)",
        "duct": {"supply_collar": sc, "return_collar": rc, "mouth_w": mw, "mouth_h": mh, "insul_m2": ins, "propose": prop, "std_box": sbox},
        "price": 0, "unit": "Bộ", "origin": "Thái Lan",
        "image": f"assets/products/{img}",
        "catalog_pdf": pdf, "catalog_page": pg,
        "notes": "Thông số côn đầu máy & hộp gió khớp tuyệt đối 100% theo BẢNG CÔN ĐẦU DÀN LẠNH DAIKIN."
    })

# SkyAir Floor Standing FVA & Ceiling FHA (Exact from SKY TỔNG HỢP 2023.pdf pp. 90-91)
sky_other = [
    ("FVA50AMVM/RZF50CV2V", "2.0 HP", 17100, 5.0, "1.23 kW", "1 pha, 220V", "DL: 1850x600x270 | DN: 595x845x300", "DL: 42 kg | DN: 41 kg", "18/16/14 m³/phút", "43/41/38 dB(A)", "Ø9.5 / Ø15.9", "floor_standing_fva.png", 90, "Tủ đứng đặt sàn SkyAir Inverter R32 17.100 Btu/h"),
    ("FVA71AMVM/RZF71CV2V", "3.0 HP", 24200, 7.1, "2.51 kW", "1 pha, 220V", "DL: 1850x600x270 | DN: 695x930x350", "DL: 42 kg | DN: 48 kg", "18/16/14 m³/phút", "43/41/38 dB(A)", "Ø9.5 / Ø15.9", "floor_standing_fva.png", 90, "Tủ đứng đặt sàn SkyAir Inverter R32 24.200 Btu/h"),
    ("FVA100AMVM/RZF100CVM", "4.0 HP", 34100, 10.0, "3.48 kW", "1 pha, 220V", "DL: 1850x600x350 | DN: 990x940x320", "DL: 50 kg | DN: 64 kg", "28/25/22 m³/phút", "50/47/44 dB(A)", "Ø9.5 / Ø15.9", "floor_standing_fva.png", 90, "Tủ đứng đặt sàn SkyAir Inverter R32 34.100 Btu/h"),
    ("FVA125AMVM/RZF125CYM", "5.0 HP (3P)", 42700, 12.5, "4.48 kW", "3 pha, 380V", "DL: 1850x600x350 | DN: 990x940x320", "DL: 50 kg | DN: 64 kg", "28/26/24 m³/phút", "51/48/46 dB(A)", "Ø9.5 / Ø15.9", "floor_standing_fva.png", 90, "Tủ đứng đặt sàn SkyAir Inverter R32 42.700 Btu/h"),
    ("FVA140AMVM/RZF140CYM", "5.5 HP (3P)", 47800, 14.0, "5.71 kW", "3 pha, 380V", "DL: 1850x600x350 | DN: 990x940x320", "DL: 50 kg | DN: 64 kg", "30/28/26 m³/phút", "53/51/48 dB(A)", "Ø9.5 / Ø15.9", "floor_standing_fva.png", 90, "Tủ đứng đặt sàn SkyAir Inverter R32 47.800 Btu/h"),
    ("FHA60CVMV/RZF60CV2V", "2.5 HP", 20500, 6.0, "1.53 kW", "1 pha, 220V", "DL: 235x1270x690 | DN: 595x845x300", "DL: 32 kg | DN: 41 kg", "20.5/18.8/17/15.5/14 m³/phút", "38/37/36/35/34 dB(A)", "Ø9.5 / Ø15.9", "ceiling_fxhq.png", 91, "Áp trần SkyAir Inverter R32 20.500 Btu/h"),
    ("FHA100CVMV/RZF100CVM", "4.0 HP", 34100, 10.0, "3.24 kW", "1 pha, 220V", "DL: 235x1590x690 | DN: 990x940x320", "DL: 38 kg | DN: 64 kg", "28/26/24/22/20 m³/phút", "42/40/38/36/34 dB(A)", "Ø9.5 / Ø15.9", "ceiling_fxhq.png", 91, "Áp trần SkyAir Inverter R32 34.100 Btu/h"),
]
for m, hp, bc, kc, pw, pwr, dim, wt, af, ns, pipe, img, pg, nm in sky_other:
    add_prod({
        "id": m.replace("/", "_"), "model": m, "category_id": "SKY_OTHER", "name": nm,
        "hp": hp, "cooling_btu": bc, "cooling_kw": kc, "heating_btu": 0, "heating_kw": 0,
        "power_input": pw, "power_supply": pwr, "refrigerant": "R32 Inverter",
        "dimensions": dim, "weight": wt, "airflow": af, "noise": ns,
        "gas_pipe": pipe, "drain_pipe": "VP25 (Ngoài Ø32 / Trong Ø25)", "price": 0, "unit": "Bộ", "origin": "Thái Lan",
        "image": f"assets/products/{img}",
        "catalog_pdf": "SKY TỔNG HỢP 2023.pdf", "catalog_page": pg,
        "notes": "Tham chiếu chính xác Catalogue SkyAir Daikin 2023."
    })

# ==============================================================================
# 12. MULTI NX R32 (Outdoor, Wall, Cassette, Ducted, Remotes)
# ==============================================================================
multi_out = [
    ("3MXM52RVMV", "2.0 HP (Tối đa 3 dàn)", 18000, 5.2, 23200, 6.8, "1.15 kW", "695x930x350", "53 kg", "53.2 m³/phút", "Lạnh 45/43 | Sưởi 47/45 dB(A)", "Lỏng Ø6.4x3 | Hơi Ø9.5x1 + Ø12.7x2", 21906000, "multi_outdoor_3_4.png"),
    ("4MXM68RVMV", "2.5 HP (Tối đa 4 dàn)", 24000, 6.8, 29300, 8.6, "1.67 kW", "695x930x350", "56 kg", "57.4 m³/phút", "Lạnh 47/44 | Sưởi 48/46 dB(A)", "Lỏng Ø6.4x4 | Hơi Ø9.5x2 + Ø12.7x2", 26847000, "multi_outdoor_3_4.png"),
    ("4MXM80RVMV", "3.0 HP (Tối đa 4 dàn)", 28000, 8.0, 32700, 9.6, "2.05 kW", "695x930x350", "61 kg", "59.1 m³/phút", "Lạnh 48/45 | Sưởi 49/47 dB(A)", "Lỏng Ø6.4x4 | Hơi Ø9.5x1 + Ø12.7x1 + Ø15.9x2", 31301000, "multi_outdoor_3_4.png"),
    ("5MXM100RVMV", "4.0 HP (Tối đa 5 dàn)", 34000, 10.0, 37500, 11.0, "2.55 kW", "990x940x320", "83 kg", "59.6 m³/phút", "Lạnh 48/46 | Sưởi 49/47 dB(A)", "Lỏng Ø6.4x5 | Hơi Ø9.5x2 + Ø12.7x1 + Ø15.9x2", 38376000, "multi_outdoor_5.png"),
]
for m, hp, bc, kc, bh, kh, pw, dim, wt, af, ns, pipe, pr, img in multi_out:
    add_prod({
        "id": m, "model": m, "category_id": "MULTI_OUT",
        "name": f"Dàn nóng Super Multi NX 2 chiều {bc:,} Btu/h ({hp})".replace(",", "."),
        "hp": hp, "cooling_btu": bc, "cooling_kw": kc, "heating_btu": bh, "heating_kw": kh,
        "power_input": pw, "refrigerant": "R32", "dimensions": dim, "weight": wt, "airflow": af, "noise": ns,
        "gas_pipe": pipe, "drain_pipe": "Thoát đáy dàn nóng", "price": pr, "unit": "Dàn", "origin": "Thái Lan",
        "image": f"assets/products/{img}",
        "catalog_pdf": "MULTI DAIKIN.pdf", "catalog_page": 46,
        "tech_pdf": "Catalogue kỹ thuật Multi-R32.pdf", "tech_page": 23,
        "notes": "1 dàn nóng duy nhất kết nối tối đa 3-5 dàn lạnh độc lập (Treo tường, Cassette, Nối ống gió)."
    })

multi_wall = [
    ("CTXM25RVMV", "1.0 HP", 9000, 2.5, "285x770x223", "9 kg", "10.4 m³/phút", "40/32/25/19 dB(A)", "Ø6.4 / Ø9.5", 3755000),
    ("CTXM35RVMV", "1.5 HP", 12000, 3.5, "285x770x223", "9 kg", "11.3 m³/phút", "42/34/26/19 dB(A)", "Ø6.4 / Ø9.5", 4103000),
    ("CTXM50RVMV", "2.0 HP", 18000, 5.0, "295x990x263", "13 kg", "16.9 m³/phút", "45/40/35/28 dB(A)", "Ø6.4 / Ø12.7", 6445000),
    ("CTXM60RVMV", "2.5 HP", 20500, 6.0, "295x990x263", "13 kg", "19.5 m³/phút", "48/41/33/29 dB(A)", "Ø6.4 / Ø12.7", 8103000),
    ("CTXM71RVMV", "3.0 HP", 24000, 7.1, "295x990x263", "13 kg", "20.0 m³/phút", "49/43/35/30 dB(A)", "Ø6.4 / Ø15.9", 8227000),
]
for m, hp, bc, kc, dim, wt, af, ns, pipe, pr in multi_wall:
    add_prod({
        "id": m, "model": m, "category_id": "MULTI_IN_WALL",
        "name": f"Dàn lạnh treo tường Multi 2 chiều {bc:,} Btu/h ({m})".replace(",", "."),
        "hp": hp, "cooling_btu": bc, "cooling_kw": kc, "heating_btu": int(bc*1.12), "heating_kw": round(kc*1.12, 1),
        "power_input": "35 W", "refrigerant": "R32", "dimensions": dim, "weight": wt, "airflow": af, "noise": ns,
        "gas_pipe": pipe, "drain_pipe": "Ø16 mm (Kèm điều khiển không dây)", "price": pr, "unit": "Dàn", "origin": "Thái Lan",
        "image": "assets/products/wall_ctxm.png",
        "catalog_pdf": "MULTI DAIKIN.pdf", "catalog_page": 45,
        "notes": "Tích hợp mắt thần thông minh & phin lọc Apatit Titan, đã kèm điều khiển từ xa."
    })

multi_cas = [
    ("FFA25RV1V", "1.0 HP", 9000, 2.5, "260x575x575", "17.5 kg", "9.0 m³/phút", "33/27 dB(A)", "Ø6.4 / Ø9.5", 7182000),
    ("FFA35RV1V", "1.5 HP", 12000, 3.5, "260x575x575", "17.5 kg", "10.0 m³/phút", "36/29 dB(A)", "Ø6.4 / Ø9.5", 8006000),
    ("FFA50RV1V", "2.0 HP", 18000, 5.0, "260x575x575", "17.5 kg", "12.0 m³/phút", "38/30 dB(A)", "Ø6.4 / Ø12.7", 9410000),
    ("FFA60RV1V", "2.5 HP", 20500, 6.0, "260x575x575", "17.5 kg", "15.0 m³/phút", "42/34 dB(A)", "Ø6.4 / Ø12.7", 10986000),
]
for m, hp, bc, kc, dim, wt, af, ns, pipe, pr in multi_cas:
    add_prod({
        "id": m, "model": m, "category_id": "MULTI_IN_CASSETTE",
        "name": f"Dàn lạnh Cassette âm trần 4 hướng Multi {bc:,} Btu/h ({m})".replace(",", "."),
        "hp": hp, "cooling_btu": bc, "cooling_kw": kc, "heating_btu": int(bc*1.12), "heating_kw": round(kc*1.12, 1),
        "power_input": "50 W", "refrigerant": "R32", "dimensions": dim, "weight": wt, "airflow": af, "noise": ns,
        "gas_pipe": pipe, "drain_pipe": "VP20 (Có bơm nước xả)",
        "ceiling_opening": "585x585 mm", "panel_model": "BYFQ60B3W1", "panel_dim": "55x700x700 mm (2.7 kg)",
        "price": pr, "unit": "Dàn", "origin": "Thái Lan",
        "image": "assets/products/cassette_multi_2x2.png",
        "catalog_pdf": "MULTI DAIKIN.pdf", "catalog_page": 43,
        "notes": "Thiết kế Châu Âu vừa khít ô trần 600x600mm (Giá chưa gồm mặt nạ BYFQ60B3W1 & điều khiển)."
    })

add_prod({
    "id": "BYFQ60B3W1", "model": "BYFQ60B3W1", "category_id": "MULTI_IN_CASSETTE",
    "name": "Mặt nạ trang trí Cassette Multi 4 hướng thổi (Model: BYFQ60B3W1)",
    "hp": "Phụ kiện", "cooling_btu": 0, "cooling_kw": 0, "heating_btu": 0, "heating_kw": 0,
    "power_input": "—", "refrigerant": "—", "dimensions": "55x700x700", "weight": "2.7 kg", "airflow": "4 hướng thổi", "noise": "—",
    "gas_pipe": "—", "drain_pipe": "—", "ceiling_opening": "Dùng cho FFA25-60RV1V",
    "price": 3271000, "unit": "Cái", "origin": "CH Czech",
    "image": "assets/products/panel_cassette.png",
    "catalog_pdf": "MULTI DAIKIN.pdf", "catalog_page": 43,
    "notes": "Mặt nạ thiết kế Châu Âu nhập khẩu CH Czech cho dàn lạnh FFA."
})

# Multi Ducted (Exact from BÁO GIÁ VRV.xlsx + BẢNG CÔN ĐẦU DÀN LẠNH DAIKIN - E HOAN.xlsx rows 44-54)
multi_duct = [
    ("CDXM25RVMV", "1.0 HP", 9000, 2.5, "200x900x620", "25 kg", "9.5 m³/phút (570 m³/h)", "35/33/31/29 dB(A)", "40 Pa", "Ø6.4 / Ø9.5", 6318000,
     "860x180", "780x180", 880, 180, 0.636, "Côn đầu máy, H250 + 2 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 880 x 220, Giật cổ 880 x 180 để thẳng 60/880 x 220/ H250, trổ đỉnh 2D200", "duct_multi_cdxm.png", 41),
    ("CDXM35RVMV", "1.5 HP", 12000, 3.5, "200x900x620", "25 kg", "10.0 m³/phút (600 m³/h)", "35/33/31/29 dB(A)", "40 Pa", "Ø6.4 / Ø9.5", 6694000,
     "860x180", "780x180", 880, 180, 0.636, "Côn đầu máy, H250 + 2 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 880 x 220, Giật cổ 880 x 180 để thẳng 60/880 x 220/ H250, trổ đỉnh 2D200", "duct_multi_cdxm.png", 41),
    ("CDXM50RVMV", "2.0 HP", 17100, 5.0, "200x900x620", "27 kg", "12.0 m³/phút (720 m³/h)", "37/35/33/31 dB(A)", "40 Pa", "Ø6.4 / Ø12.7", 8405000,
     "860x180", "780x180", 880, 180, 0.636, "Côn đầu máy, H250 + 2 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 880 x 220, Giật cổ 880 x 180 để thẳng 60/880 x 220/ H250, trổ đỉnh 2D200", "duct_multi_cdxm.png", 41),
    ("CDXM60RVMV", "2.5 HP", 21000, 6.0, "200x1100x620", "30 kg", "16.0 m³/phút (960 m³/h)", "38/36/34/32 dB(A)", "40 Pa", "Ø6.4 / Ø12.7", 8950000,
     "1080x180", "1080x180", 1080, 180, 0.756, "Côn đầu máy, H250 + 3 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1080 x 220, Giật cổ 1080 x 180 để thẳng 60/740 x 220/ H250, trổ đỉnh 3D200", "duct_multi_cdxm.png", 41),
    ("CDXM71RVMV", "3.0 HP", 24200, 7.1, "200x1100x620", "30 kg", "16.0 m³/phút (960 m³/h)", "38/36/34/32 dB(A)", "40 Pa", "Ø6.4 / Ø15.9", 9351000,
     "1080x180", "1080x180", 1080, 180, 0.756, "Côn đầu máy, H250 + 3 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1080 x 220, Giật cổ 1080 x 180 để thẳng 60/740 x 220/ H250, trổ đỉnh 3D200", "duct_multi_cdxm.png", 41),
    ("CDXP25RVMV", "1.0 HP", 9000, 2.5, "200x700x620", "21 kg", "8.7 m³/phút (522 m³/h)", "35/33/31/29 dB(A)", "30 Pa", "Ø6.4 / Ø9.5", 6250000,
     "680x180", "680x180", 680, 180, 0.516, "Côn đầu máy, H250 + 2 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 680 x 220, Giật cổ 680 x 180 để thẳng 60/480 x 220/ H250, trổ đỉnh 2D200", "duct_multi_cdxp.png", 40),
    ("CDXP35RVMV", "1.5 HP", 12000, 3.5, "200x700x620", "21 kg", "8.7 m³/phút (522 m³/h)", "35/33/31/29 dB(A)", "30 Pa", "Ø6.4 / Ø9.5", 6620000,
     "680x180", "680x180", 680, 180, 0.516, "Côn đầu máy, H250 + 2 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 680 x 220, Giật cổ 680 x 180 để thẳng 60/480 x 220/ H250, trổ đỉnh 2D200", "duct_multi_cdxp.png", 40),
    ("CDXP60RVMV", "2.5 HP", 21000, 6.0, "200x1100x620", "30 kg", "16.0 m³/phút (960 m³/h)", "38/36/34/32 dB(A)", "40 Pa", "Ø6.4 / Ø12.7", 8950000,
     "1080x180", "1080x180", 1080, 180, 0.756, "Côn đầu máy, H250 + 3 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1080 x 220, Giật cổ 1080 x 180 để thẳng 60/740 x 220/ H250, trổ đỉnh 3D200", "duct_multi_cdxp.png", 41),
    ("CDXP71RVMV", "3.0 HP", 24200, 7.1, "200x1100x620", "30 kg", "16.0 m³/phút (960 m³/h)", "38/36/34/32 dB(A)", "40 Pa", "Ø6.4 / Ø15.9", 9351000,
     "1080x180", "1080x180", 1080, 180, 0.756, "Côn đầu máy, H250 + 3 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1080 x 220, Giật cổ 1080 x 180 để thẳng 60/740 x 220/ H250, trổ đỉnh 3D200", "duct_multi_cdxp.png", 41),
    ("FMA50RVMV", "2.0 HP", 17100, 5.0, "245x1000x800", "37 kg", "18.0 m³/phút (1080 m³/h)", "35/33/31 dB(A)", "50-150 Pa", "Ø6.4 / Ø12.7", 9200000,
     "980x225", "980x225", 980, 225, 0.723, "Côn đầu máy, H250 + 3 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 980 x 225, Giật cổ 980 x 225 để thẳng 60/980 x 225/ H250, trổ đỉnh 3D200", "duct_med_fxsq.png", 42),
    ("FMA60RVMV", "2.5 HP", 21000, 6.0, "245x1000x800", "37 kg", "18.0 m³/phút (1080 m³/h)", "35/33/31 dB(A)", "50-150 Pa", "Ø6.4 / Ø12.7", 9850000,
     "980x225", "980x225", 980, 225, 0.723, "Côn đầu máy, H250 + 3 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 980 x 225, Giật cổ 980 x 225 để thẳng 60/980 x 225/ H250, trổ đỉnh 3D200", "duct_med_fxsq.png", 42),
    ("FMA71RVMV", "3.0 HP", 24200, 7.1, "245x1000x800", "37 kg", "23.0 m³/phút (1380 m³/h)", "38/35/33 dB(A)", "50-150 Pa", "Ø6.4 / Ø15.9", 10450000,
     "980x225", "980x225", 980, 225, 0.723, "Côn đầu máy, H250 + 4 cổ D200 (elip, trổ đứng), 1 đầu để thẳng", "Hộp gió giật cấp KT: 1000 x 225, Giật cổ 980 x 225 để thẳng 60/1000 x 225/ H250, trổ đỉnh 4D200", "duct_med_fxsq.png", 42),
]
for m, hp, bc, kc, dim, wt, af, ns, esp, pipe, pr, sc, rc, mw, mh, ins, prop, sbox, img, pg in multi_duct:
    add_prod({
        "id": m, "model": m, "category_id": "MULTI_IN_DUCT",
        "name": f"Dàn lạnh giấu trần nối ống gió Multi {bc:,} Btu/h ({m})".replace(",", "."),
        "hp": hp, "cooling_btu": bc, "cooling_kw": kc, "heating_btu": int(bc*1.12), "heating_kw": round(kc*1.12, 1),
        "power_input": "75 - 120 W", "refrigerant": "R32", "dimensions": dim, "weight": wt, "airflow": af, "noise": ns, "esp": esp,
        "gas_pipe": pipe, "drain_pipe": "VP20 / VP25",
        "duct": {"supply_collar": sc, "return_collar": rc, "mouth_w": mw, "mouth_h": mh, "insul_m2": ins, "propose": prop, "std_box": sbox},
        "price": pr, "unit": "Dàn", "origin": "Thái Lan",
        "image": f"assets/products/{img}",
        "catalog_pdf": "MULTI DAIKIN.pdf", "catalog_page": pg,
        "tech_pdf": "Catalogue kỹ thuật Multi-R32.pdf", "tech_page": 19,
        "notes": "Thông số côn đầu máy & hộp gió giật cấp chuẩn BẢNG CÔN ĐẦU DÀN LẠNH DAIKIN."
    })

multi_acc = [
    ("BRC1E63_M", "BRC1E63", "Điều khiển có dây cho dàn lạnh Cassette Multi (BRC1E63)", 882000, "ctrl_wired_brc1e63.png", 21),
    ("BRC073A4", "BRC073A4", "Điều khiển có dây cho dàn lạnh giấu trần nối ống gió Multi (BRC073A4)", 1617000, "ctrl_wired_brc1e63.png", 17),
    ("BRC086A21", "BRC086A21/BRC086A2R2", "Điều khiển không dây từ xa cho dàn lạnh Cassette Multi (BRC086A21)", 1912000, "ctrl_wireless.png", 21),
    ("BRC086A11", "BRC086A11", "Điều khiển không dây từ xa cho dàn lạnh giấu trần nối ống gió Multi (BRC086A11)", 955000, "ctrl_wireless.png", 17),
]
for pid, m, nm, pr, img, pg in multi_acc:
    add_prod({
        "id": pid, "model": m, "category_id": "MULTI_ACC", "name": nm,
        "hp": "Phụ kiện Multi", "cooling_btu": 0, "cooling_kw": 0, "heating_btu": 0, "heating_kw": 0,
        "power_input": "—", "refrigerant": "—", "dimensions": "120x120x19" if "073" in m or "1E" in m else "155x52x18",
        "weight": "0.2 kg", "airflow": "—", "noise": "—", "gas_pipe": "Cáp điều khiển", "drain_pipe": "—",
        "price": pr, "unit": "Cái", "origin": "Thái Lan",
        "image": f"assets/products/{img}",
        "catalog_pdf": "MULTI DAIKIN.pdf", "catalog_page": pg,
        "notes": "Phụ kiện điều khiển chính hãng cho dàn lạnh hệ Super Multi NX."
    })

# ==============================================================================
# PART B: INSTALLATION LABOR & MATERIALS (Exact from BÁO GIÁ VRV.xlsx rows 169-360)
# Each item has cost_type: "labor" or "material" so multipliers work cleanly!
# ==============================================================================
MATERIALS = [
    # Group B.I - Phần lắp đặt thiết bị & Giá đỡ
    {"id": "B1_01", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt dàn nóng điều hòa trung tâm VRV (VRF) công suất (8HP - 24HP)", "brand": "Minh Phú", "unit": "dàn", "base_price": 3500000, "cost_type": "labor"},
    {"id": "B1_02", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt dàn nóng điều hòa trung tâm VRV công suất (26HP - 48HP)", "brand": "Minh Phú", "unit": "bộ", "base_price": 6500000, "cost_type": "labor"},
    {"id": "B1_03", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt dàn nóng điều hòa trung tâm VRV công suất (50HP - 60HP)", "brand": "Minh Phú", "unit": "bộ", "base_price": 9000000, "cost_type": "labor"},
    {"id": "B1_04", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt dàn nóng điều hòa VRV S / Multi công suất (4HP - 6HP)", "brand": "Minh Phú", "unit": "dàn", "base_price": 1500000, "cost_type": "labor"},
    {"id": "B1_05", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt dàn nóng điều hòa trung tâm VRV S công suất (8HP - 9HP)", "brand": "Minh Phú", "unit": "dàn", "base_price": 2200000, "cost_type": "labor"},
    {"id": "B1_06", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt dàn lạnh loại treo tường, CSL: 7.500 - 15.400 Btu/h", "brand": "Minh Phú", "unit": "dàn", "base_price": 350000, "cost_type": "labor"},
    {"id": "B1_07", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt dàn lạnh loại treo tường, CSL: 18.000 - 24.200 Btu/h", "brand": "Minh Phú", "unit": "dàn", "base_price": 450000, "cost_type": "labor"},
    {"id": "B1_08", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt dàn lạnh loại Cassette, CSL: 7.500 - 15.400 Btu/h", "brand": "Minh Phú", "unit": "dàn", "base_price": 650000, "cost_type": "labor"},
    {"id": "B1_09", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt dàn lạnh loại Cassette, CSL: 18.000 - 30.700 Btu/h", "brand": "Minh Phú", "unit": "dàn", "base_price": 800000, "cost_type": "labor"},
    {"id": "B1_10", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt dàn lạnh loại Cassette, CSL: 34.000 - 54.600 Btu/h", "brand": "Minh Phú", "unit": "dàn", "base_price": 950000, "cost_type": "labor"},
    {"id": "B1_11", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt dàn lạnh Giấu trần nối ống gió, CSL: 7.500 - 15.400 Btu/h", "brand": "Minh Phú", "unit": "dàn", "base_price": 750000, "cost_type": "labor"},
    {"id": "B1_12", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt dàn lạnh Giấu trần nối ống gió, CSL: 18.000 - 30.700 Btu/h", "brand": "Minh Phú", "unit": "dàn", "base_price": 900000, "cost_type": "labor"},
    {"id": "B1_13", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt dàn lạnh Giấu trần nối ống gió, CSL: 34.000 - 54.600 Btu/h", "brand": "Minh Phú", "unit": "dàn", "base_price": 1150000, "cost_type": "labor"},
    {"id": "B1_14", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt bộ chia gas REFNET (hàn đồng có thổi khí Nitơ)", "brand": "Minh Phú", "unit": "bộ", "base_price": 350000, "cost_type": "labor"},
    {"id": "B1_15", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt điều khiển có dây / không dây cho dàn lạnh", "brand": "Minh Phú", "unit": "cái", "base_price": 120000, "cost_type": "labor"},
    {"id": "B1_16", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt, cài đặt điều khiển trung tâm", "brand": "Minh Phú", "unit": "cái", "base_price": 1500000, "cost_type": "labor"},
    {"id": "B1_17", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt điều hòa cục bộ treo tường, CSL: 9.000 - 12.000 Btu/h", "brand": "Minh Phú", "unit": "bộ", "base_price": 450000, "cost_type": "labor"},
    {"id": "B1_18", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt điều hòa cục bộ treo tường, CSL: 18.000 - 24.000 Btu/h", "brand": "Minh Phú", "unit": "bộ", "base_price": 600000, "cost_type": "labor"},
    {"id": "B1_19", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt điều hòa cục bộ SkyAir (Cassette/Nối ống gió), CSL: 18.000 - 24.000 Btu/h", "brand": "Minh Phú", "unit": "bộ", "base_price": 1200000, "cost_type": "labor"},
    {"id": "B1_20", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Lắp đặt điều hòa cục bộ SkyAir (Cassette/Nối ống gió), CSL: 34.000 - 48.000 Btu/h", "brand": "Minh Phú", "unit": "bộ", "base_price": 1600000, "cost_type": "labor"},
    {"id": "B1_23", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Chi phí cẩu dàn nóng lên mái", "brand": "Việt Nam", "unit": "Ca", "base_price": 5400000, "cost_type": "labor"},
    {"id": "B1_24", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Giá đỡ dàn nóng điều hòa cục bộ, CSL: 9.000 - 12.000 Btu/h", "brand": "Việt Nam", "unit": "bộ", "base_price": 135000, "cost_type": "material"},
    {"id": "B1_25", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Giá đỡ dàn nóng điều hòa cục bộ, CSL: 18.000 - 24.000 Btu/h", "brand": "Việt Nam", "unit": "bộ", "base_price": 203000, "cost_type": "material"},
    {"id": "B1_26", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Giá đỡ dàn nóng điều hòa cục bộ, CSL: 34.000 - 48.000 Btu/h", "brand": "Việt Nam", "unit": "bộ", "base_price": 270000, "cost_type": "material"},
    {"id": "B1_27", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Giá đỡ dàn nóng VRV công suất 8HP-24HP (sắt U100 sơn 2 lớp, hàn cao 200mm)", "brand": "Việt Nam", "unit": "hệ", "base_price": 2025000, "cost_type": "material"},
    {"id": "B1_28", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Giá đỡ dàn nóng VRV công suất 26HP-48HP (sắt U100 sơn 2 lớp, hàn cao 200mm)", "brand": "Việt Nam", "unit": "hệ", "base_price": 2970000, "cost_type": "material"},
    {"id": "B1_29", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Giá đỡ dàn nóng VRV công suất 50HP-60HP (sắt U100 sơn 2 lớp, hàn cao 200mm)", "brand": "Việt Nam", "unit": "hệ", "base_price": 4050000, "cost_type": "material"},
    {"id": "B1_30", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Giá đỡ dàn nóng điều hòa trung tâm VRV-S / Multi", "brand": "Việt Nam", "unit": "bộ", "base_price": 270000, "cost_type": "material"},
    {"id": "B1_31", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Giá treo ty ren dàn lạnh (áp trần, cassette, nối ống gió)", "brand": "Việt Nam", "unit": "dàn", "base_price": 81000, "cost_type": "material"},
    {"id": "B1_32", "group_code": "I", "group_name": "I. Phần nhân công lắp đặt thiết bị & Giá đỡ", "name": "Vật tư phụ phần lắp đặt thiết bị (5% vật tư chính)", "brand": "Việt Nam", "unit": "lô", "base_price": 770000, "cost_type": "material"},

    # Group B.II - Phần ống đồng, bảo ôn & Trunking
    {"id": "B2_01", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Ống đồng D6.4 dày 0.7 mm", "brand": "Toàn Phát", "unit": "m", "base_price": 40000, "cost_type": "material"},
    {"id": "B2_02", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Ống đồng D9.5 dày 0.7 mm", "brand": "Toàn Phát", "unit": "m", "base_price": 63000, "cost_type": "material"},
    {"id": "B2_03", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Ống đồng D12.7 dày 0.7 mm", "brand": "Toàn Phát", "unit": "m", "base_price": 80000, "cost_type": "material"},
    {"id": "B2_04", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Ống đồng D15.9 dày 0.7 mm", "brand": "Toàn Phát", "unit": "m", "base_price": 108000, "cost_type": "material"},
    {"id": "B2_05", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Ống đồng D19.1 dày 0.7 mm", "brand": "Toàn Phát", "unit": "m", "base_price": 130000, "cost_type": "material"},
    {"id": "B2_06", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Ống đồng D6.4 dày 0.8 mm", "brand": "Toàn Phát", "unit": "m", "base_price": 42000, "cost_type": "material"},
    {"id": "B2_07", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Ống đồng D9.5 dày 0.8 mm", "brand": "Toàn Phát", "unit": "m", "base_price": 66000, "cost_type": "material"},
    {"id": "B2_08", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Ống đồng D12.7 dày 0.8 mm", "brand": "Toàn Phát", "unit": "m", "base_price": 90000, "cost_type": "material"},
    {"id": "B2_09", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Ống đồng D15.9 dày 0.8 mm", "brand": "Toàn Phát", "unit": "m", "base_price": 114000, "cost_type": "material"},
    {"id": "B2_10", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Ống đồng D19.1 dày 0.8 mm", "brand": "Toàn Phát", "unit": "m", "base_price": 138000, "cost_type": "material"},
    {"id": "B2_13", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Ống đồng D22.2 dày 1.0 mm", "brand": "Toàn Phát", "unit": "m", "base_price": 199000, "cost_type": "material"},
    {"id": "B2_14", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Ống đồng D28.6 dày 1.0 mm", "brand": "Toàn Phát", "unit": "m", "base_price": 257000, "cost_type": "material"},
    {"id": "B2_17", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Ống đồng D34.9 dày 1.2 mm", "brand": "Toàn Phát", "unit": "m", "base_price": 380000, "cost_type": "material"},
    {"id": "B2_18", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Ống đồng D38.1 dày 1.2 mm", "brand": "Toàn Phát", "unit": "m", "base_price": 416000, "cost_type": "material"},
    {"id": "B2_19", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Ống đồng D41.9 dày 1.2 mm", "brand": "Toàn Phát", "unit": "m", "base_price": 452000, "cost_type": "material"},
    {"id": "B2_23", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Phụ kiện ống đồng: Côn, cút, tê, nối... (15% ống cây)", "brand": "Toàn Phát", "unit": "lô", "base_price": 324000, "cost_type": "material"},
    {"id": "B2_28", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Bảo ôn D6 dày 19mm", "brand": "Superlon", "unit": "m", "base_price": 13000, "cost_type": "material"},
    {"id": "B2_29", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Bảo ôn D10 dày 19mm", "brand": "Superlon", "unit": "m", "base_price": 14000, "cost_type": "material"},
    {"id": "B2_30", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Bảo ôn D13 dày 19mm", "brand": "Superlon", "unit": "m", "base_price": 17000, "cost_type": "material"},
    {"id": "B2_31", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Bảo ôn D16 dày 19mm", "brand": "Superlon", "unit": "m", "base_price": 19000, "cost_type": "material"},
    {"id": "B2_32", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Bảo ôn D19 dày 19mm", "brand": "Superlon", "unit": "m", "base_price": 21000, "cost_type": "material"},
    {"id": "B2_33", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Bảo ôn D22 dày 19mm", "brand": "Superlon", "unit": "m", "base_price": 39000, "cost_type": "material"},
    {"id": "B2_34", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Bảo ôn D28 dày 19mm", "brand": "Superlon", "unit": "m", "base_price": 41000, "cost_type": "material"},
    {"id": "B2_35", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Bảo ôn D35 dày 19mm", "brand": "Superlon", "unit": "m", "base_price": 50000, "cost_type": "material"},
    {"id": "B2_36", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Bảo ôn D42 dày 19mm", "brand": "Superlon", "unit": "m", "base_price": 56000, "cost_type": "material"},
    {"id": "B2_41", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Băng quấn cách ẩm", "brand": "Việt Nam", "unit": "kg", "base_price": 27000, "cost_type": "material"},
    {"id": "B2_42", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Giá treo ống đồng", "brand": "Việt Nam", "unit": "cái", "base_price": 20000, "cost_type": "material"},
    {"id": "B2_43", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Nitơ hàn thổi khí, nén thử kín, Oxy, gas hàn", "brand": "Việt Nam", "unit": "lô", "base_price": 227000, "cost_type": "material"},
    {"id": "B2_44", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Gas sạc bổ sung (R410A / R32)", "brand": "Ấn Độ", "unit": "kg", "base_price": 300000, "cost_type": "material"},
    {"id": "B2_45", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Trunking ống đồng 300x200 tôn sơn tĩnh điện dày 0.75 (đã có nắp)", "brand": "Việt Nam", "unit": "m", "base_price": 450000, "cost_type": "material"},
    {"id": "B2_46", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Trunking ống đồng 500x200 tôn sơn tĩnh điện dày 0.75 (đã có nắp)", "brand": "Việt Nam", "unit": "m", "base_price": 645000, "cost_type": "material"},
    {"id": "B2_50", "group_code": "II", "group_name": "II. Phần ống đồng, bảo ôn & Trunking", "name": "Nhân công đi ống đồng + bảo ôn trung bình", "brand": "Minh Phú", "unit": "m", "base_price": 65000, "cost_type": "labor"},

    # Group B.III - Phần nước ngưng, bảo ôn
    {"id": "B3_01", "group_code": "III", "group_name": "III. Phần ống nước ngưng & Bảo ôn", "name": "Ống PVC D=21 Class 2", "brand": "Tiền Phong", "unit": "m", "base_price": 11000, "cost_type": "material"},
    {"id": "B3_02", "group_code": "III", "group_name": "III. Phần ống nước ngưng & Bảo ôn", "name": "Ống PVC D=27 Class 2", "brand": "Tiền Phong", "unit": "m", "base_price": 15000, "cost_type": "material"},
    {"id": "B3_03", "group_code": "III", "group_name": "III. Phần ống nước ngưng & Bảo ôn", "name": "Ống PVC D=34 Class 2", "brand": "Tiền Phong", "unit": "m", "base_price": 18000, "cost_type": "material"},
    {"id": "B3_04", "group_code": "III", "group_name": "III. Phần ống nước ngưng & Bảo ôn", "name": "Ống PVC D=42 Class 2", "brand": "Tiền Phong", "unit": "m", "base_price": 25000, "cost_type": "material"},
    {"id": "B3_05", "group_code": "III", "group_name": "III. Phần ống nước ngưng & Bảo ôn", "name": "Ống PVC D=48 Class 2", "brand": "Tiền Phong", "unit": "m", "base_price": 30000, "cost_type": "material"},
    {"id": "B3_14", "group_code": "III", "group_name": "III. Phần ống nước ngưng & Bảo ôn", "name": "Phụ kiện ống PVC: Cút, tê, keo... (20% ống)", "brand": "Tiền Phong", "unit": "lô", "base_price": 57000, "cost_type": "material"},
    {"id": "B3_16", "group_code": "III", "group_name": "III. Phần ống nước ngưng & Bảo ôn", "name": "Bảo ôn ống nước D21 dày 13mm", "brand": "Superlon", "unit": "m", "base_price": 14000, "cost_type": "material"},
    {"id": "B3_17", "group_code": "III", "group_name": "III. Phần ống nước ngưng & Bảo ôn", "name": "Bảo ôn ống nước D27 dày 13mm", "brand": "Superlon", "unit": "m", "base_price": 16000, "cost_type": "material"},
    {"id": "B3_18", "group_code": "III", "group_name": "III. Phần ống nước ngưng & Bảo ôn", "name": "Bảo ôn ống nước D34 dày 13mm", "brand": "Superlon", "unit": "m", "base_price": 18000, "cost_type": "material"},
    {"id": "B3_23", "group_code": "III", "group_name": "III. Phần ống nước ngưng & Bảo ôn", "name": "Giá treo ống nước ngưng", "brand": "Việt Nam", "unit": "bộ", "base_price": 20000, "cost_type": "material"},
    {"id": "B3_25", "group_code": "III", "group_name": "III. Phần ống nước ngưng & Bảo ôn", "name": "Nhân công lắp đặt ống thoát nước ngưng bọc bảo ôn", "brand": "Minh Phú", "unit": "m", "base_price": 35000, "cost_type": "labor"},

    # Group B.IV - Phần điện tín hiệu, điều khiển
    {"id": "B4_01", "group_code": "IV", "group_name": "IV. Phần điện nguồn & Tín hiệu điều khiển", "name": "Dây điện 2x2.5mm² (Điện nguồn nối dàn lạnh)", "brand": "Cadisun", "unit": "m", "base_price": 24000, "cost_type": "material"},
    {"id": "B4_02", "group_code": "IV", "group_name": "IV. Phần điện nguồn & Tín hiệu điều khiển", "name": "Dây điện 2x1.5mm² chống nhiễu (Dây tín hiệu truyền thông F1-F2)", "brand": "Cadisun", "unit": "m", "base_price": 16500, "cost_type": "material"},
    {"id": "B4_03", "group_code": "IV", "group_name": "IV. Phần điện nguồn & Tín hiệu điều khiển", "name": "Dây điện 2x0.75mm² (Dây điều khiển gắn tường)", "brand": "Cadisun", "unit": "m", "base_price": 11000, "cost_type": "material"},
    {"id": "B4_04", "group_code": "IV", "group_name": "IV. Phần điện nguồn & Tín hiệu điều khiển", "name": "Ống ruột gà đi dây điện D16 / D20", "brand": "Sino / VN", "unit": "m", "base_price": 7500, "cost_type": "material"},
    {"id": "B4_05", "group_code": "IV", "group_name": "IV. Phần điện nguồn & Tín hiệu điều khiển", "name": "Ống gen cứng luồn dây điện D20", "brand": "Sino / VN", "unit": "m", "base_price": 12500, "cost_type": "material"},
    {"id": "B4_09", "group_code": "IV", "group_name": "IV. Phần điện nguồn & Tín hiệu điều khiển", "name": "Nhân công kéo rải dây nguồn & dây tín hiệu điều khiển", "brand": "Minh Phú", "unit": "m", "base_price": 18000, "cost_type": "labor"},

    # Group B.V - Phần gió lạnh (Côn đầu máy, ống gió, cửa gió)
    {"id": "B5_01", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Côn đầu dàn lạnh công suất 7.500 - 15.400 Btu/h, tôn dày 0.58mm", "brand": "Hoa Sen", "unit": "cái", "base_price": 448000, "cost_type": "material"},
    {"id": "B5_02", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Côn đầu dàn lạnh công suất 19.100 - 30.700 Btu/h, tôn dày 0.58mm", "brand": "Hoa Sen", "unit": "cái", "base_price": 576000, "cost_type": "material"},
    {"id": "B5_03", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Côn đầu dàn lạnh công suất 38.200 - 54.600 Btu/h, tôn dày 0.58mm", "brand": "Hoa Sen", "unit": "cái", "base_price": 832000, "cost_type": "material"},
    {"id": "B5_04", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Côn đầu dàn lạnh 38.200 - 54.600 Btu/h, tôn 0.75mm, bông thủy tinh 80kg/m³, tôn soi lỗ", "brand": "Hoa Sen", "unit": "cái", "base_price": 832000, "cost_type": "material"},
    {"id": "B5_07", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Ống gió vuông bằng tôn mạ kẽm dày 0.58mm", "brand": "Hoa Sen", "unit": "m²", "base_price": 480000, "cost_type": "material"},
    {"id": "B5_08", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Ống gió vuông bằng tôn mạ kẽm dày 0.75mm", "brand": "Hoa Sen", "unit": "m²", "base_price": 520000, "cost_type": "material"},
    {"id": "B5_09", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Bảo ôn cách nhiệt PE dày 20mm bọc ống gió/hộp gió", "brand": "Việt Nam", "unit": "m²", "base_price": 82000, "cost_type": "material"},
    {"id": "B5_11", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Bảo ôn cao su lưu hóa 1 mặt bạc, 1 mặt keo dày 19mm", "brand": "Tplex", "unit": "m²", "base_price": 382000, "cost_type": "material"},
    {"id": "B5_13", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Cửa gió khuếch tán 600x600 sơn tĩnh điện", "brand": "Việt Nam", "unit": "cái", "base_price": 416000, "cost_type": "material"},
    {"id": "B5_20", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Cửa gió không viền thẩm mỹ KT 800x150", "brand": "Amiv", "unit": "cái", "base_price": 352000, "cost_type": "material"},
    {"id": "B5_24", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Cửa gió không viền thẩm mỹ KT 1000x150", "brand": "Amiv", "unit": "cái", "base_price": 448000, "cost_type": "material"},
    {"id": "B5_26", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Cửa gió không viền thẩm mỹ KT 1200x150", "brand": "Amiv", "unit": "cái", "base_price": 512000, "cost_type": "material"},
    {"id": "B5_33", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Cửa gió nan bầu dục 1 lớp KT 1000x150", "brand": "Việt Nam", "unit": "cái", "base_price": 400000, "cost_type": "material"},
    {"id": "B5_43", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Cửa cấp gió Linear SLOT KT 1000x150 (2 nan slot)", "brand": "Việt Nam", "unit": "cái", "base_price": 448000, "cost_type": "material"},
    {"id": "B5_45", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Cửa cấp gió Linear SLOT KT 1200x150 (2 nan slot)", "brand": "Việt Nam", "unit": "cái", "base_price": 544000, "cost_type": "material"},
    {"id": "B5_51", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Hộp gió cho cửa (800x150 - 1000x150), tôn dày 0.58mm", "brand": "Hoa Sen", "unit": "cái", "base_price": 348000, "cost_type": "material"},
    {"id": "B5_52", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Hộp gió cho cửa (1200x150 - 1500x150), tôn dày 0.58mm", "brand": "Hoa Sen", "unit": "cái", "base_price": 531000, "cost_type": "material"},
    {"id": "B5_53", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Lưới lọc bụi cho cửa hồi", "brand": "Việt Nam", "unit": "cái", "base_price": 128000, "cost_type": "material"},
    {"id": "B5_57", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Van điều chỉnh lưu lượng gió VCD D200", "brand": "Hoa Sen", "unit": "cái", "base_price": 45000, "cost_type": "material"},
    {"id": "B5_58", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Van điều chỉnh lưu lượng gió VCD D250", "brand": "Hoa Sen", "unit": "cái", "base_price": 58000, "cost_type": "material"},
    {"id": "B5_63", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Ống gió mềm có bảo ôn D200", "brand": "VN/TQ", "unit": "m", "base_price": 45000, "cost_type": "material"},
    {"id": "B5_64", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Ống gió mềm có bảo ôn D250", "brand": "VN/TQ", "unit": "m", "base_price": 58000, "cost_type": "material"},
    {"id": "B5_68", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Đai treo cố định ống gió mềm", "brand": "Việt Nam", "unit": "bộ", "base_price": 8000, "cost_type": "material"},
    {"id": "B5_69", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Ty treo & giá đỡ cố định hộp gió, cửa gió", "brand": "Việt Nam", "unit": "bộ", "base_price": 32000, "cost_type": "material"},
    {"id": "B5_70", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Cổ bạt mềm nối đầu (đuôi) máy chống rung", "brand": "Việt Nam", "unit": "bộ", "base_price": 256000, "cost_type": "material"},
    {"id": "B5_72", "group_code": "V", "group_name": "V. Phần côn đầu máy, ống gió & cửa gió", "name": "Nhân công gia công lắp đặt côn gió, hộp gió & cửa gió", "brand": "Minh Phú", "unit": "bộ", "base_price": 320000, "cost_type": "labor"},
]

CATALOG_FILES = [
    {"file": "Catalogue Điều Hòa Trung tâm VRV H Daikin 2025.pdf", "title": "Catalogue Thương Mại VRV H Daikin 2025 (Tiếng Việt)", "pages": 28},
    {"file": "DAIKIN VRV TỔNG HỢP.pdf", "title": "Catalogue Tổng Hợp Hệ Thống VRV Daikin (Tiếng Việt)", "pages": 324},
    {"file": "Dàn nóng VRV 6 trung tâm.pdf", "title": "Tài Liệu Kỹ Thuật Dàn Nóng VRV 6 RXYQ8-60BYM (Tiếng Việt)", "pages": 108},
    {"file": "CATALOGUE KỸ THUẬT VRV 4S.pdf", "title": "Catalogue Kỹ Thuật VRV IV-S", "pages": 76},
    {"file": "SKY TỔNG HỢP 2023.pdf", "title": "Catalogue Tổng Hợp SkyAir Daikin (Tiếng Việt)", "pages": 148},
    {"file": "Skyair Daikin Tổng hợp.pdf", "title": "Catalogue SkyAir Daikin Thương Mại (Tiếng Việt)", "pages": 174},
    {"file": "Catalogue kỹ thuật máy cục bộ Daikin ( đặt cửa gió).pdf", "title": "Engineering Data Máy Cục Bộ & Đặt Cửa Gió Daikin", "pages": 372},
    {"file": "MULTI DAIKIN.pdf", "title": "Catalogue Thương Mại Super Multi NX R32 (Tiếng Việt)", "pages": 60},
    {"file": "mULTI S.pdf", "title": "Catalogue Multi S Daikin (Tiếng Việt)", "pages": 28},
    {"file": "Catalogue kỹ thuật Multi-R32.pdf", "title": "Engineering Data Super Multi NX R32", "pages": 920},
    {"file": "THIẾT BỊ THU HỒI NHIỆT HRV.pdf", "title": "Catalogue Thiết Bị Thông Gió Thu Hồi Nhiệt VAM-HVE (Tiếng Việt)", "pages": 14},
    {"file": "ĐIỀU KHIỂN TRUNG TÂM DAIKIN.pdf", "title": "Catalogue Hệ Thống Điều Khiển Trung Tâm Daikin (Tiếng Việt)", "pages": 20},
    {"file": "Intelligent touch Manager.pdf", "title": "Catalogue Bộ Điều Khiển Trung Tâm iTM (Tiếng Việt)", "pages": 16},
    {"file": "Cassette âm trần có streamer.pdf", "title": "Brochure Cassette Đa Hướng Thổi Streamer (Tiếng Việt)", "pages": 4},
    {"file": "TCVN Điều Hòa Không Khí _5687_2024.pdf", "title": "Tiêu Chuẩn Quốc Gia TCVN 5687:2024 - Thông Gió & ĐHKK", "pages": 89},
]

db = {
    "version": "1.0.0",
    "company": COMPANY_DEFAULT,
    "categories": CATEGORIES,
    "products": products,
    "materials": MATERIALS,
    "catalog_files": CATALOG_FILES
}

json_path = os.path.join(APP_DIR, "web", "database.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

js_path = os.path.join(APP_DIR, "web", "js", "data.js")
with open(js_path, "w", encoding="utf-8") as f:
    f.write("window.DAIKIN_INITIAL_DB = ")
    json.dump(db, f, ensure_ascii=False)
    f.write(";\n")

print(f"Database generated! Categories: {len(CATEGORIES)}, Products: {len(products)}, Materials/Labor: {len(MATERIALS)}")
