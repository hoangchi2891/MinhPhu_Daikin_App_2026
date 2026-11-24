# -*- coding: utf-8 -*-
"""
hvac_report_exporter.py — Standalone A4 PDF & Live-Formula Excel (.xlsx) Engineering Report Exporter
For CÔNG TY TNHH PHÁT TRIỂN KỸ THUẬT THƯƠNG MẠI MINH PHÚ
Standards: TCVN 5687:2024 & QCVN 09:2017/BXD, Daikin Duct Checker, CoolPack R410A/R32 & Hybrid AI Report.
Theme: Formal Pure White Letterhead (Yellow ONLY on Minh Phú Logo)
       + Minh Phú Red Title Bars with 100% Pure White Text (#991B1B / #FFFFFF)
       + Daikin Deep Blue Table Headers (#005A8D / #FFFFFF)
       + Zero stray yellow anywhere.
"""

import io
import os
import zipfile
from datetime import datetime
from xml.sax.saxutils import escape
import pymupdf
from PIL import Image

from pdf_exporter import make_red_bar_png, wrap_lines, fmt_vn
from excel_exporter import col_letter


def _fmt_f(val, dec: int = 1) -> str:
    try:
        return f"{float(val):.{dec}f}"
    except Exception:
        return "0"


def _fmt_int(val) -> str:
    try:
        return f"{int(round(float(val or 0))):,}".replace(",", ".")
    except Exception:
        return "0"


# ==============================================================================
# 1. PURE VECTOR MULTI-PAGE A4 PDF REPORT GENERATOR
# ==============================================================================
def generate_hvac_report_pdf(payload: dict, web_dir: str, out_path: str = None) -> bytes:
    comp = payload.get("company", {})
    meta = payload.get("meta", {})
    calc = payload.get("calc_result", {}) or {}
    duct = payload.get("duct_result")
    coolpack = payload.get("coolpack_result")
    ai_report = payload.get("ai_report_text", "") or ""
    ai_mode = payload.get("ai_mode", "OFFLINE_EXPERT")

    db = calc.get("design_basis", {})
    sm = calc.get("summary", {})
    rooms = calc.get("rooms", [])

    W, H = 595.0, 842.0  # A4 Portrait
    ML, MR = 26.0, 26.0
    TW = W - ML - MR     # 543 pt
    BOTTOM_LIMIT = H - 36.0

    font_reg_path = r"C:\Windows\Fonts\arial.ttf"
    font_bold_path = r"C:\Windows\Fonts\arialbd.ttf"
    font_ital_path = r"C:\Windows\Fonts\arialbi.ttf"
    f_reg = pymupdf.Font(fontfile=font_reg_path)
    f_bold = pymupdf.Font(fontfile=font_bold_path)

    doc = pymupdf.open()
    red_bar_bytes = make_red_bar_png(1200, 48)
    logo_path = os.path.join(web_dir, "assets", "logo_minh_phu.png")

    # Executive White-Priority Palette — Yellow ONLY inside Logo badge; ALL Red bars have PURE WHITE text!
    C_WHITE = (1.0, 1.0, 1.0)
    C_RED = (0.60, 0.106, 0.106)       # #991B1B
    C_LOGO_GOLD = (0.98, 0.80, 0.08)   # #FACC15 ONLY for Minh Phú Logo
    C_LOGO_BORDER = (0.92, 0.70, 0.03) # #EAB308 ONLY for Minh Phú Logo
    C_BLUE_HEAD = (0.0, 0.353, 0.553)  # #005A8D Daikin Deep Blue
    C_DAIKIN = (0.0, 0.467, 0.714)     # #0077B6 Daikin Mid Blue
    C_TEAL = (0.051, 0.580, 0.533)     # #0D9488 Engineering Teal
    C_GREEN = (0.086, 0.639, 0.290)    # #16A34A Pass Green
    C_ICE = (0.937, 0.965, 1.0)        # #EFF6FF Ice Blue Highlight
    C_SLATE_BG = (0.973, 0.980, 0.988) # #F8FAFC Clean Light Neutral
    C_ROSE_BG = (0.996, 0.949, 0.949)  # #FEF2F2 Soft Alert Rose
    C_SLATE = (0.059, 0.090, 0.165)    # #0F172A Dark Navy Text
    C_MUTED = (0.278, 0.333, 0.412)    # #475569 Slate Muted
    C_BORDER = (0.796, 0.835, 0.882)   # #CBD5E1 Crisp Border

    now_str = meta.get("date_str") or datetime.now().strftime("%d/%m/%Y")
    rep_code = meta.get("report_code") or f"BC-HVAC-{datetime.now().strftime('%Y%m%d')}"

    def new_page(is_first: bool = False):
        p = doc.new_page(width=W, height=H)
        p.insert_font(fontname="F_R", fontfile=font_reg_path)
        p.insert_font(fontname="F_B", fontfile=font_bold_path)
        p.insert_font(fontname="F_BI", fontfile=font_ital_path)
        if is_first:
            # Pure White Corporate Letterhead — Yellow strictly ONLY inside Logo badge
            if os.path.exists(logo_path):
                p.draw_rect(pymupdf.Rect(ML, 18, ML + 56, 74), color=C_LOGO_BORDER, fill=C_LOGO_GOLD, width=1.1, radius=0.08)
                p.insert_image(pymupdf.Rect(ML + 2, 20, ML + 54, 72), filename=logo_path)

            cx = ML + 66
            p.insert_text(
                (cx, 30.5),
                comp.get("name", "CÔNG TY TNHH PHÁT TRIỂN KỸ THUẬT THƯƠNG MẠI MINH PHÚ"),
                fontname="F_B", fontsize=9.6, color=C_RED
            )
            p.insert_text(
                (cx, 42.0),
                f'PHÒNG TƯ VẤN THIẾT KẾ HVAC DAIKIN  •  "{comp.get("slogan", "HOÀN TIỀN NẾU KHÔNG HÀI LÒNG")}"',
                fontname="F_B", fontsize=6.6, color=C_BLUE_HEAD
            )
            addr_lines = wrap_lines(f_reg, f'Địa chỉ: {comp.get("address", "")}', 7.2, 330.0)
            ay = 53.5
            for al in addr_lines[:2]:
                p.insert_text((cx, ay), al, fontname="F_R", fontsize=7.2, color=C_SLATE)
                ay += 9.2
            p.insert_text(
                (cx, max(ay + 0.5, 69.5)),
                f'Hotline: {comp.get("hotline", "0967 986 586")}   |   MST: {comp.get("tax_code", "0107709790")}   |   Web: {comp.get("website", "").replace("https://", "")}',
                fontname="F_B", fontsize=7.2, color=C_MUTED
            )

            # Right Formal White Reference Card
            p.draw_rect(pymupdf.Rect(436, 18, W - MR, 74), color=C_BORDER, fill=C_WHITE, width=1.0)
            p.draw_rect(pymupdf.Rect(436, 18, W - MR, 22.5), color=C_RED, fill=C_RED, width=0)
            p.insert_textbox(
                pymupdf.Rect(438, 25, W - MR - 2, 39),
                "HỒ SƠ KỸ THUẬT HVAC",
                fontname="F_B", fontsize=8.0, color=C_RED, align=pymupdf.TEXT_ALIGN_CENTER
            )
            p.insert_textbox(
                pymupdf.Rect(438, 40, W - MR - 2, 72),
                f"Mã: {rep_code}\nNgày: {now_str}",
                fontname="F_B", fontsize=7.1, color=C_SLATE, align=pymupdf.TEXT_ALIGN_CENTER, lineheight=1.45
            )
            p.draw_line((ML, 81.0), (W - MR, 81.0), color=C_RED, width=2.0)
            p.draw_line((ML, 84.0), (W - MR, 84.0), color=C_BLUE_HEAD, width=0.8)
            return p, 92.0
        else:
            # Clean running header on continuation pages (clamped so it never overlaps report code)
            hdr_left = f"HỒ SƠ TÍNH TOÁN NHIỆT TCVN 5687:2024 & ỐNG GIÓ — {meta.get('project_name') or 'DỰ ÁN ĐHKK DAIKIN'}"
            while len(hdr_left) > 20 and f_bold.text_length(hdr_left, fontsize=7.0) > (TW - 118.0):
                hdr_left = hdr_left[:-4] + "..."
            p.insert_text((ML, 20), hdr_left, fontname="F_B", fontsize=7.0, color=C_BLUE_HEAD)
            code_txt = f"Mã: {rep_code}"
            tw_c = f_reg.text_length(code_txt, fontsize=7.0)
            p.insert_text((W - MR - tw_c, 20), code_txt, fontname="F_R", fontsize=7.0, color=C_MUTED)
            p.draw_line((ML, 24.5), (W - MR, 24.5), color=C_BORDER, width=0.6)
            return p, 34.0

    def draw_section_bar(p, y: float, title: str) -> tuple:
        if y + 26.0 > BOTTOM_LIMIT:
            p, y = new_page(False)
        p.draw_rect(pymupdf.Rect(ML, y, W - MR, y + 18.0), color=C_RED, fill=C_RED, width=0)
        p.insert_text((ML + 8, y + 12.2), title, fontname="F_B", fontsize=8.5, color=C_WHITE)
        return p, y + 23.0

    page, y = new_page(is_first=True)

    # MAIN RED DOCUMENT TITLE BAR (100% Pure White Text)
    doc_title = "BÁO CÁO TÍNH TOÁN TẢI NHIỆT (TCVN 5687:2024), ỐNG GIÓ & PHÂN TÍCH KỸ THUẬT AI"
    page.insert_image(pymupdf.Rect(ML, y, W - MR, y + 22.0), stream=red_bar_bytes, keep_proportion=False)
    tw_t = f_bold.text_length(doc_title, fontsize=9.8)
    page.insert_text((ML + (TW - tw_t) / 2, y + 14.5), doc_title, fontname="F_B", fontsize=9.8, color=C_WHITE)
    y += 28.0

    # PROJECT META BOX (Clean Pure White with Daikin Blue accent strip — wrapped cleanly)
    rx = ML + 312.0
    left_max_w = 294.0
    client_lines = wrap_lines(f_bold, f"Chủ đầu tư: {meta.get('client_name') or 'Quý Khách Hàng'}", 7.8, left_max_w)[:1]
    proj_lines = wrap_lines(f_reg, f"Công trình: {meta.get('project_name') or 'Hệ thống Điều hòa Không khí Daikin'}", 7.6, left_max_w)[:2]
    eng_lines = wrap_lines(f_reg, f"Kỹ sư thực hiện: {meta.get('engineer_name') or 'Phòng Kỹ Thuật Minh Phú'}", 7.4, left_max_w)[:1]
    meta_h = 46.0 + (10.5 if len(proj_lines) > 1 else 0.0)
    page.draw_rect(pymupdf.Rect(ML, y, W - MR, y + meta_h), color=C_BORDER, fill=C_WHITE, width=0.8)
    page.draw_rect(pymupdf.Rect(ML, y, ML + 3.5, y + meta_h), color=C_BLUE_HEAD, fill=C_BLUE_HEAD, width=0)
    page.insert_text((ML + 10, y + 13.5), client_lines[0], fontname="F_B", fontsize=7.8, color=C_SLATE)
    py_m = y + 25.5
    for pl in proj_lines:
        page.insert_text((ML + 10, py_m), pl, fontname="F_R", fontsize=7.6, color=C_SLATE)
        py_m += 10.5
    page.insert_text((ML + 10, py_m + 1.5), eng_lines[0], fontname="F_R", fontsize=7.4, color=C_MUTED)

    page.insert_text((rx, y + 13.5), "Tiêu chuẩn: TCVN 5687:2024 & QCVN 09:2017/BXD", fontname="F_B", fontsize=7.4, color=C_BLUE_HEAD)
    page.insert_text((rx, y + 26.0), f"Khu vực: {db.get('city_name', 'Hà Nội')} — Cấp {db.get('grade', 'I')}", fontname="F_R", fontsize=7.5, color=C_SLATE)
    page.insert_text((rx, y + 38.5), f"Ngoài trời: t_khô={db.get('t_out', 35.4)}°C | t_ướt={db.get('twb_out', 28.0)}°C | h={db.get('h_out_kj_kg', 89.0)} kJ/kg", fontname="F_R", fontsize=7.2, color=C_MUTED)
    y += meta_h + 10.0

    # ==========================================================================
    # SECTION 1: KPI SUMMARY CARDS (4 clean cards across TW=543pt)
    # ==========================================================================
    page, y = draw_section_bar(page, y, "1. TỔNG HỢP THÔNG SỐ THIẾT KẾ & CÔNG SUẤT TẢI LẠNH")
    card_w = (TW - 18.0) / 4.0
    card_h = 48.0
    kpis = [
        ("TỔNG DIỆN TÍCH / SỐ PHÒNG", f"{_fmt_f(sm.get('total_area_m2', 0), 1)} m²", f"{sm.get('room_count', 0)} phòng • {sm.get('total_people', 0)} người", C_BLUE_HEAD),
        ("TỔNG TẢI LẠNH TỨC THỜI", f"{_fmt_f(sm.get('total_cooling_kw', 0), 2)} kW", f"{_fmt_int(sm.get('total_cooling_btu', 0))} Btu/h ({_fmt_f(sm.get('total_cooling_rt', 0), 2)} RT)", C_RED),
        ("TẢI CHỌN DÀN NÓNG (ĐỒNG THỜI)", f"{_fmt_f(sm.get('diversified_kw', 0), 2)} kW", f"Hệ số {db.get('diversity_factor', 0.85)} • Dự phòng +{db.get('safety_pct', 10)}%", C_BLUE_HEAD),
        ("CHỈ SỐ PHỤ TẢI & GIÓ TƯƠI", f"{_fmt_f(sm.get('avg_w_per_m2', 0), 0)} W/m²", f"SHR {sm.get('shr', 0.78)} • OA {_fmt_int(sm.get('total_oa_m3h', 0))} m³/h", C_TEAL),
    ]
    for ci, (lbl, big, sub, accent) in enumerate(kpis):
        cx = ML + ci * (card_w + 6.0)
        page.draw_rect(pymupdf.Rect(cx, y, cx + card_w, y + card_h), color=C_BORDER, fill=C_SLATE_BG, width=0.7)
        page.draw_rect(pymupdf.Rect(cx, y, cx + card_w, y + 3.0), color=accent, fill=accent, width=0)
        page.insert_text((cx + 6, y + 13.5), lbl, fontname="F_B", fontsize=6.1, color=C_MUTED)
        page.insert_text((cx + 6, y + 29.5), big, fontname="F_B", fontsize=11.5, color=accent)
        page.insert_text((cx + 6, y + 42.0), sub, fontname="F_R", fontsize=6.6, color=C_SLATE)
    y += card_h + 8.0

    # Recommended Outdoor & HRV Banner (if matched)
    out_rec = sm.get("outdoor_rec")
    hrv_rec = sm.get("hrv_rec")
    if out_rec or hrv_rec:
        banner_h = 26.0
        page.draw_rect(pymupdf.Rect(ML, y, W - MR, y + banner_h), color=C_BLUE_HEAD, fill=C_ICE, width=0.7)
        b_txt = []
        if out_rec:
            b_txt.append(f"Tổ hợp dàn nóng Daikin đề xuất: {out_rec['model']} ({out_rec['cooling_kw']} kW / {_fmt_int(out_rec['cooling_btu'])} Btu/h)")
        if hrv_rec:
            b_txt.append(f"Cấp gió tươi HRV: {hrv_rec['model']} ({hrv_rec.get('hp', '')})")
        page.insert_text((ML + 8, y + 16.0), "   |   ".join(b_txt), fontname="F_B", fontsize=7.6, color=C_BLUE_HEAD)
        y += banner_h + 10.0

    # ==========================================================================
    # SECTION 2: PURE VECTOR HEAT LOAD COMPONENT BREAKDOWN BAR CHART
    # ==========================================================================
    comps = sm.get("components_w", {})
    if comps:
        page, y = draw_section_bar(page, y, "2. BIỂU ĐỒ PHÂN TÍCH CƠ CẤU NGUỒN NHIỆT CÔNG TRÌNH (W & %)")
        chart_items = [
            ("Bức xạ & truyền nhiệt Kính / Cửa sổ", comps.get("glass_rad", 0) + comps.get("glass_cond", 0), C_RED),
            ("Tường bao, Cửa chính, Mái & Sàn", comps.get("wall", 0) + comps.get("door", 0) + comps.get("roof_floor", 0) + comps.get("partition", 0), C_BLUE_HEAD),
            ("Gió tươi (TCVN 5687) & Khí lọt cửa", comps.get("fresh_air", 0) + comps.get("infiltration", 0), C_TEAL),
            ("Tỏa nhiệt Người trong phòng", comps.get("people", 0), C_DAIKIN),
            ("Chiếu sáng & Thiết bị trong phòng", comps.get("light_equip", 0), C_MUTED),
        ]
        tot_cw = max(1.0, sum(v for _, v, _ in chart_items))
        max_cw = max(1.0, max(v for _, v, _ in chart_items))

        box_h = len(chart_items) * 18.0 + 12.0
        page.draw_rect(pymupdf.Rect(ML, y, W - MR, y + box_h), color=C_BORDER, fill=C_WHITE, width=0.7)
        cy = y + 8.0
        label_w = 165.0
        bar_max_w = TW - label_w - 115.0
        for cname, cval, ccol in chart_items:
            pct = cval / tot_cw * 100.0
            bw = max(2.0, (cval / max_cw) * bar_max_w)
            page.insert_text((ML + 8, cy + 10.5), cname, fontname="F_B", fontsize=7.4, color=C_SLATE)
            bx0 = ML + label_w
            page.draw_rect(pymupdf.Rect(bx0, cy + 2.5, bx0 + bar_max_w, cy + 12.5), color=None, fill=C_SLATE_BG, width=0)
            page.draw_rect(pymupdf.Rect(bx0, cy + 2.5, bx0 + bw, cy + 12.5), color=None, fill=ccol, width=0)
            val_str = f"{cval/1000.0:.2f} kW ({pct:.1f}%)"
            page.insert_text((bx0 + bar_max_w + 8, cy + 10.5), val_str, fontname="F_B", fontsize=7.4, color=C_SLATE)
            cy += 18.0
        y += box_h + 10.0

    # ==========================================================================
    # SECTION 3: MULTI-ROOM HEAT LOAD & EQUIPMENT SELECTION TABLE
    # ==========================================================================
    page, y = draw_section_bar(page, y, "3. BẢNG TÍNH TẢI NHIỆT CHI TIẾT TỪNG PHÒNG & CHỌN THIẾT BỊ DAIKIN")

    # Column widths summing to 543 pt
    RCOLS = [22.0, 128.0, 32.0, 42.0, 34.0, 40.0, 38.0, 62.0, 50.0, 95.0]
    RX = [ML]
    for cw in RCOLS:
        RX.append(RX[-1] + cw)

    def draw_room_table_header(p, yy: float) -> float:
        rh = 24.0
        p.draw_rect(pymupdf.Rect(ML, yy, W - MR, yy + rh), color=C_BLUE_HEAD, fill=C_BLUE_HEAD, width=0.5)
        hdrs = [
            "STT", "Phòng / Tầng / Vật liệu", "DT\n(m²)", "H_BT/TC\n(m)", "Hướng",
            "Q_hiện\n(kW)", "Q_ẩn\n(kW)", "Tổng tải\n(kW / Btu)", "W/m² &\nOA m³/h", "Model Daikin &\nKiểm tra QCVN/Trần"
        ]
        for ci, htxt in enumerate(hdrs):
            if ci > 0:
                p.draw_line((RX[ci], yy), (RX[ci], yy + rh), color=C_WHITE, width=0.4)
            p.insert_textbox(
                pymupdf.Rect(RX[ci] + 1, yy + 3.0, RX[ci + 1] - 1, yy + rh - 1),
                htxt, fontname="F_B", fontsize=6.7, color=C_WHITE, align=pymupdf.TEXT_ALIGN_CENTER, lineheight=1.15
            )
        return yy + rh

    y = draw_room_table_header(page, y)

    for idx, r in enumerate(rooms):
        rec = r.get("recommended_unit", {}) or {}
        name_lines = wrap_lines(f_bold, f"{r.get('name', '')} ({r.get('floor', '')})", 7.0, RCOLS[1] - 6)
        win_txt = r.get("window_summary") or f"Kính {r.get('glass_area', 0)}m²"
        door_txt = r.get("door_summary")
        eq_txt = r.get("equip_items_summary") or ""
        mat_parts = [f"{r.get('wall_name', '').split('(')[0].strip()[:22]} | {win_txt[:26]}"]
        if door_txt and door_txt != "—":
            mat_parts.append(f"Cửa: {door_txt[:34]}")
        if eq_txt and not eq_txt.startswith("Định mức"):
            mat_parts.append(f"TB: {eq_txt[:36]}")
        mat_lines = []
        for mp in mat_parts[:3]:
            mat_lines.extend(wrap_lines(f_reg, mp, 5.8, RCOLS[1] - 6)[:1])
        assigned = r.get("assigned_units") or []
        if assigned:
            model_str = " + ".join((f"{u.get('qty',1)}× {u.get('model','')}" if u.get("qty", 1) > 1 or len(assigned) > 1 else u.get("model", "")) for u in assigned)
        else:
            qty_str = f"{rec.get('qty', 1)}× " if rec.get("qty", 1) > 1 else ""
            model_str = f"{qty_str}{rec.get('model', '—')}"
        cov_s = f" ({rec.get('coverage_pct')}%)" if rec.get("coverage_pct") else ""
        qcvn_tag = "QCVN09: Đạt" if r.get("qcvn_ok", True) else "QCVN09: Lưu ý"
        clr_tag = "Trần: Đạt" if rec.get("clearance_ok", True) else "Trần: THIẾU!"
        mod_lines = wrap_lines(f_bold, model_str + cov_s, 6.7, RCOLS[9] - 6)
        tag_lines = wrap_lines(f_reg, f"{qcvn_tag} | {clr_tag}", 6.0, RCOLS[9] - 6)

        row_h = max(28.0, len(name_lines) * 8.4 + len(mat_lines) * 7.4 + 6.0, (len(mod_lines) + len(tag_lines)) * 8.4 + 6.0)
        if y + row_h > BOTTOM_LIMIT:
            page, y = new_page(False)
            y = draw_room_table_header(page, y)

        bg = C_SLATE_BG if idx % 2 == 1 else C_WHITE
        page.draw_rect(pymupdf.Rect(ML, y, W - MR, y + row_h), color=C_BORDER, fill=bg, width=0.45)
        for ci in range(1, len(RCOLS)):
            page.draw_line((RX[ci], y), (RX[ci], y + row_h), color=C_BORDER, width=0.4)

        # STT
        page.insert_textbox(pymupdf.Rect(RX[0], y + 6, RX[1], y + row_h), str(idx + 1), fontname="F_B", fontsize=7.2, color=C_SLATE, align=pymupdf.TEXT_ALIGN_CENTER)
        # Name & materials
        ty = y + 9.2
        for nl in name_lines:
            page.insert_text((RX[1] + 3, ty), nl, fontname="F_B", fontsize=7.0, color=C_SLATE)
            ty += 8.4
        for ml in mat_lines:
            page.insert_text((RX[1] + 3, ty), ml, fontname="F_R", fontsize=5.8, color=C_MUTED)
            ty += 7.4

        # Area
        page.insert_textbox(pymupdf.Rect(RX[2], y + 6, RX[3], y + row_h), f"{r.get('area', 0):.1f}", fontname="F_B", fontsize=7.2, color=C_SLATE, align=pymupdf.TEXT_ALIGN_CENTER)
        # H_BT/TC
        page.insert_textbox(pymupdf.Rect(RX[3], y + 4, RX[4], y + row_h), f"{r.get('h_concrete', 3.6):.1f}/{r.get('h_ceiling', 3.0):.1f}\n({int(r.get('plenum_mm', 600))}mm)", fontname="F_R", fontsize=6.3, color=C_SLATE, align=pymupdf.TEXT_ALIGN_CENTER, lineheight=1.2)
        # Orientation
        page.insert_textbox(pymupdf.Rect(RX[4], y + 6, RX[5], y + row_h), str(r.get("orientation", "")), fontname="F_B", fontsize=7.2, color=C_BLUE_HEAD, align=pymupdf.TEXT_ALIGN_CENTER)
        # Q_sens kW
        page.insert_textbox(pymupdf.Rect(RX[5], y + 6, RX[6], y + row_h), f"{r.get('q_sens_w', 0)/1000.0:.2f}", fontname="F_R", fontsize=7.1, color=C_SLATE, align=pymupdf.TEXT_ALIGN_CENTER)
        # Q_lat kW
        page.insert_textbox(pymupdf.Rect(RX[6], y + 6, RX[7], y + row_h), f"{r.get('q_lat_w', 0)/1000.0:.2f}", fontname="F_R", fontsize=7.1, color=C_SLATE, align=pymupdf.TEXT_ALIGN_CENTER)
        # Total kW / Btu
        page.insert_textbox(pymupdf.Rect(RX[7], y + 4, RX[8], y + row_h), f"{r.get('q_kw', 0):.2f} kW\n{_fmt_int(r.get('q_btu', 0))} Btu", fontname="F_B", fontsize=6.8, color=C_RED, align=pymupdf.TEXT_ALIGN_CENTER, lineheight=1.25)
        # W/m2 & OA
        page.insert_textbox(pymupdf.Rect(RX[8], y + 4, RX[9], y + row_h), f"{r.get('w_per_m2', 0):.0f} W/m²\nOA {int(r.get('oa_m3h', 0))}", fontname="F_R", fontsize=6.6, color=C_SLATE, align=pymupdf.TEXT_ALIGN_CENTER, lineheight=1.25)
        # Model + QCVN/Clearance
        my = y + 9.5
        for ml in mod_lines:
            page.insert_text((RX[9] + 3, my), ml, fontname="F_B", fontsize=7.0, color=C_BLUE_HEAD)
            my += 8.4
        tag_col = C_GREEN if (r.get("qcvn_ok", True) and rec.get("clearance_ok", True)) else C_RED
        for tl in tag_lines:
            page.insert_text((RX[9] + 3, my), tl, fontname="F_B", fontsize=6.0, color=tag_col)
            my += 7.5

        y += row_h

    # Total Summary Row
    if y + 24.0 > BOTTOM_LIMIT:
        page, y = new_page(False)
    tot_h = 22.0
    page.draw_rect(pymupdf.Rect(ML, y, W - MR, y + tot_h), color=C_RED, fill=C_ICE, width=0.8)
    page.insert_text((RX[1] + 3, y + 14.0), f"TỔNG CỘNG ({len(rooms)} PHÒNG)", fontname="F_B", fontsize=7.6, color=C_RED)
    page.insert_textbox(pymupdf.Rect(RX[2], y + 5, RX[3], y + tot_h), f"{sm.get('total_area_m2', 0):.1f}", fontname="F_B", fontsize=7.4, color=C_SLATE, align=pymupdf.TEXT_ALIGN_CENTER)
    page.insert_textbox(pymupdf.Rect(RX[5], y + 5, RX[6], y + tot_h), f"{sm.get('total_sens_kw', 0):.2f}", fontname="F_B", fontsize=7.4, color=C_SLATE, align=pymupdf.TEXT_ALIGN_CENTER)
    page.insert_textbox(pymupdf.Rect(RX[6], y + 5, RX[7], y + tot_h), f"{sm.get('total_lat_kw', 0):.2f}", fontname="F_B", fontsize=7.4, color=C_SLATE, align=pymupdf.TEXT_ALIGN_CENTER)
    page.insert_textbox(pymupdf.Rect(RX[7], y + 2.5, RX[8], y + tot_h), f"{sm.get('total_cooling_kw', 0):.2f} kW\n{_fmt_int(sm.get('total_cooling_btu', 0))} Btu", fontname="F_B", fontsize=6.9, color=C_RED, align=pymupdf.TEXT_ALIGN_CENTER, lineheight=1.18)
    page.insert_textbox(pymupdf.Rect(RX[8], y + 2.5, RX[9], y + tot_h), f"{sm.get('avg_w_per_m2', 0):.0f} W/m²\nOA {_fmt_int(sm.get('total_oa_m3h', 0))}", fontname="F_B", fontsize=6.6, color=C_BLUE_HEAD, align=pymupdf.TEXT_ALIGN_CENTER, lineheight=1.18)
    page.insert_textbox(pymupdf.Rect(RX[9], y + 2.5, RX[10], y + tot_h), f"Đồng thời: {sm.get('diversified_kw', 0):.2f} kW\n≈ {sm.get('total_cooling_rt', 0):.2f} RT", fontname="F_B", fontsize=6.8, color=C_BLUE_HEAD, align=pymupdf.TEXT_ALIGN_CENTER, lineheight=1.18)
    y += tot_h + 12.0

    # ==========================================================================
    # SECTION 4: DAIKIN DUCT CHECKER SUMMARY (If provided)
    # ==========================================================================
    if duct and duct.get("ok"):
        if y + 218.0 > BOTTOM_LIMIT:
            page, y = new_page(False)
        page, y = draw_section_bar(page, y, f"4. KIỂM TRA ỐNG GIÓ & CỘT ÁP QUẠT — DAIKIN DUCT CHECKER ({duct.get('model', '')})")

        # Summary header strip
        pb = duct.get("pressure_breakdown", {})
        esp_max = max(1.0, float(duct.get("esp_max_pa", 150)))
        dp_tot = float(pb.get("total_pa", 0))
        esp_ok = duct.get("esp_status") != "EXCEED_ESP"

        page.draw_rect(pymupdf.Rect(ML, y, W - MR, y + 26.0), color=C_BORDER, fill=C_SLATE_BG, width=0.6)
        page.insert_text(
            (ML + 8, y + 11.0),
            f"Model: {duct.get('model')}   |   Lưu lượng gió: {_fmt_int(duct.get('airflow_m3h'))} m³/h ({duct.get('num_branches')} nhánh)   |   ESP ĐM/Max: {duct.get('esp_rated_pa'):.0f} / {esp_max:.0f} Pa",
            fontname="F_B", fontsize=7.6, color=C_BLUE_HEAD
        )
        page.insert_text(
            (ML + 8, y + 21.5),
            f"Tổng trở lực tuyến xa nhất ΔP = {dp_tot:.1f} Pa  |  Độ ồn: {duct.get('noise_status')}  |  Diện tích tôn ước tính: {duct.get('sheet_metal_m2')} m²  |  Ống mềm: {duct.get('flex_total_m')} m",
            fontname="F_R", fontsize=7.2, color=C_SLATE
        )
        y += 30.0

        # Duct sizing 4-row table
        DCOLS = [135.0, 95.0, 70.0, 68.0, 68.0, 107.0]
        DX = [ML]
        for cw in DCOLS:
            DX.append(DX[-1] + cw)

        page.draw_rect(pymupdf.Rect(ML, y, W - MR, y + 19.0), color=C_BLUE_HEAD, fill=C_BLUE_HEAD, width=0.5)
        for ci, htxt in enumerate(["Đoạn ống gió", "Kích thước (mm)", "Lưu lượng", "Vận tốc", "Ma sát", "Tổn thất ΔP (Pa)"]):
            if ci > 0:
                page.draw_line((DX[ci], y), (DX[ci], y + 19.0), color=C_WHITE, width=0.4)
            page.insert_textbox(pymupdf.Rect(DX[ci], y + 4.5, DX[ci + 1], y + 19.0), htxt, fontname="F_B", fontsize=7.2, color=C_WHITE, align=pymupdf.TEXT_ALIGN_CENTER)
        y += 19.0

        md = duct.get("main_duct", {})
        bd = duct.get("branch_duct", {})
        fd = duct.get("flex_duct", {})
        rd = duct.get("return_duct", {})
        d_rows = [
            ("Ống gió chính (Tôn tráng kẽm)", f"{md.get('w_mm')} × {md.get('h_mm')} (≈ Ø{md.get('round_equiv_mm')})", f"{_fmt_int(duct.get('airflow_m3h'))} m³/h", f"{md.get('hyd',{}).get('velocity_ms')} m/s", f"{md.get('hyd',{}).get('dp_pa_m')} Pa/m", f"{md.get('dp_pa')} Pa"),
            ("Ống gió nhánh cứng (Mỗi nhánh)", f"{bd.get('w_mm')} × {bd.get('h_mm')} (≈ Ø{bd.get('round_mm')})", f"{_fmt_int(duct.get('branch_airflow_m3h'))} m³/h", f"{bd.get('hyd',{}).get('velocity_ms')} m/s", f"{bd.get('hyd',{}).get('dp_pa_m')} Pa/m", f"{bd.get('dp_pa')} Pa"),
            ("Ống gió mềm bảo ôn", f"Ø{fd.get('dia_mm')} mm (L={fd.get('len_m')}m)", f"{_fmt_int(duct.get('branch_airflow_m3h'))} m³/h", f"{fd.get('hyd',{}).get('velocity_ms')} m/s", f"{fd.get('hyd',{}).get('dp_pa_m')} Pa/m", f"{fd.get('dp_pa')} Pa"),
            ("Ống gió hồi (Hồi trần / Box)", f"{rd.get('w_mm')} × {rd.get('h_mm')}", f"{_fmt_int(duct.get('airflow_m3h'))} m³/h", f"{rd.get('hyd',{}).get('velocity_ms')} m/s", f"{rd.get('hyd',{}).get('dp_pa_m')} Pa/m", f"{rd.get('dp_pa')} Pa"),
            ("Phụ kiện (Cút/Tê/VCD) + Cửa gió", "Cục bộ & Lưới lọc", "—", "—", "—", f"{pb.get('fittings_pa', 0) + pb.get('grilles_pa', 0):.1f} Pa"),
        ]
        for ri, drow in enumerate(d_rows):
            bg = C_SLATE_BG if ri % 2 == 1 else C_WHITE
            drh = 18.5
            page.draw_rect(pymupdf.Rect(ML, y, W - MR, y + drh), color=C_BORDER, fill=bg, width=0.45)
            for ci, val in enumerate(drow):
                if ci > 0:
                    page.draw_line((DX[ci], y), (DX[ci], y + drh), color=C_BORDER, width=0.4)
                al = pymupdf.TEXT_ALIGN_LEFT if ci == 0 else pymupdf.TEXT_ALIGN_CENTER
                page.insert_textbox(pymupdf.Rect(DX[ci] + 4, y + 4.2, DX[ci + 1] - 4, y + drh), val, fontname="F_B" if ci in (0, 5) else "F_R", fontsize=6.8, color=C_SLATE, align=al)
            y += drh

        # Verdict & Grille Recommendation
        verdict_col = C_GREEN if esp_ok else C_RED
        verdict_bg = C_ICE if esp_ok else C_ROSE_BG
        grilles = duct.get("grilles", {})
        v_lines = wrap_lines(f_bold, f"KẾT LUẬN ESP: {duct.get('esp_verdict', '')}", 7.2, TW - 16)
        g_lines = wrap_lines(f_reg, f"Cửa gió đề xuất: {grilles.get('supply_rec', '')}  |  {grilles.get('return_rec', '')}  |  {grilles.get('vcd_rec', '')}", 6.9, TW - 16)
        vh = (len(v_lines) + len(g_lines)) * 10.0 + 10.0
        if y + vh + 12.0 > BOTTOM_LIMIT:
            page, y = new_page(False)
        page.draw_rect(pymupdf.Rect(ML, y + 3, W - MR, y + 3 + vh), color=verdict_col, fill=verdict_bg, width=0.7)
        vy = y + 13.0
        for vl in v_lines:
            page.insert_text((ML + 8, vy), vl, fontname="F_B", fontsize=7.2, color=verdict_col)
            vy += 10.0
        for gl in g_lines:
            page.insert_text((ML + 8, vy), gl, fontname="F_R", fontsize=6.9, color=C_SLATE)
            vy += 10.0
        y += vh + 14.0

    # ==========================================================================
    # SECTION 5: COOLPACK SUPERHEAT / SUBCOOLING & PIPING (If provided)
    # ==========================================================================
    if coolpack and coolpack.get("ok"):
        if y + 95.0 > BOTTOM_LIMIT:
            page, y = new_page(False)
        page, y = draw_section_bar(page, y, f"5. KIỂM TRA CHU TRÌNH LẠNH (COOLPACK — {coolpack.get('refrigerant')}) & ĐƯỜNG ỐNG ĐỒNG")
        pip = coolpack.get("piping", {})
        c_h = 56.0
        page.draw_rect(pymupdf.Rect(ML, y, W - MR, y + c_h), color=C_BORDER, fill=C_SLATE_BG, width=0.7)
        page.insert_text((ML + 8, y + 13.5), f"Môi chất: {coolpack.get('refrigerant')} (GWP {coolpack.get('gwp')}, Nhóm {coolpack.get('safety_class')})  |  Bay hơi t_e = {coolpack.get('t_evap_c')}°C ({coolpack.get('p_suction_bar')} bar)  |  Ngưng tụ t_c = {coolpack.get('t_cond_c')}°C ({coolpack.get('p_discharge_bar')} bar)", fontname="F_B", fontsize=7.3, color=C_BLUE_HEAD)
        page.insert_text((ML + 8, y + 26.5), f"Độ quá nhiệt Superheat ΔT_SH = {coolpack.get('superheat_k')} K ({coolpack.get('sh_status')})   |   Độ quá lạnh Subcooling ΔT_SC = {coolpack.get('subcooling_k')} K ({coolpack.get('sc_status')})   |   COP ước tính ≈ {coolpack.get('cop_est')}", fontname="F_B", fontsize=7.3, color=C_SLATE)
        page.insert_text((ML + 8, y + 39.5), f"Tổn hao ống đồng (L_tđ = {pip.get('eq_len_m')}m, ΔH = {pip.get('height_diff_m')}m): Suy giảm -{pip.get('loss_pct')}% -> Công suất thực tế {pip.get('actual_kw')} kW (từ {pip.get('rated_kw')} kW)", fontname="F_R", fontsize=7.2, color=C_SLATE)
        page.insert_text((ML + 8, y + 51.0), f"Lượng gas nạp bổ sung (ống lỏng Ø{pip.get('liquid_pipe_od')}mm, hệ số {pip.get('charge_rate_kg_m')} kg/m): +{pip.get('extra_charge_kg')} kg {coolpack.get('refrigerant')}", fontname="F_B", fontsize=7.3, color=C_RED)
        y += c_h + 12.0

    # ==========================================================================
    # SECTION 6: AI ENGINEERING CONSULTATION & SIGNATURE
    # ==========================================================================
    if ai_report.strip():
        mode_lbl = f"MODEL AI ({ai_mode})" if ai_mode not in ("OFFLINE_EXPERT", "OFFLINE_FALLBACK", "") else "HỆ CHUYÊN GIA KỸ THUẬT MINH PHÚ (TCVN 5687:2024)"
        page, y = draw_section_bar(page, y, f"6. BÁO CÁO THẨM ĐỊNH & TƯ VẤN KỸ THUẬT CHUYÊN SÂU — {mode_lbl}")
        ai_lines = []
        for raw_ln in ai_report.replace("\r\n", "\n").split("\n"):
            if not raw_ln.strip():
                ai_lines.append(("BLANK", ""))
            else:
                is_head = bool(raw_ln.strip()[0].isdigit() and "." in raw_ln[:4])
                fnt = f_bold if is_head else f_reg
                wrapped = wrap_lines(fnt, raw_ln.strip(), 7.8 if is_head else 7.5, TW - 16)
                for wl in wrapped:
                    ai_lines.append(("HEAD" if is_head else "BODY", wl))

        for kind, txt in ai_lines:
            lh = 6.0 if kind == "BLANK" else (11.5 if kind == "HEAD" else 10.6)
            if y + lh > BOTTOM_LIMIT:
                page, y = new_page(False)
            if kind == "HEAD":
                page.insert_text((ML + 6, y + 9.0), txt, fontname="F_B", fontsize=7.8, color=C_BLUE_HEAD)
            elif kind == "BODY":
                page.insert_text((ML + 8, y + 8.5), txt, fontname="F_R", fontsize=7.5, color=C_SLATE)
            y += lh
        y += 10.0

    # Formal Signature Block
    if y + 72.0 > BOTTOM_LIMIT:
        page, y = new_page(False)
    page.draw_line((ML, y), (W - MR, y), color=C_BORDER, width=0.6)
    y += 12.0
    page.insert_textbox(pymupdf.Rect(ML, y, ML + 240, y + 26), "KỸ SƯ THIẾT KẾ LẬP BÁO CÁO\n(Ký, ghi rõ họ tên)", fontname="F_B", fontsize=7.8, color=C_SLATE, align=pymupdf.TEXT_ALIGN_CENTER, lineheight=1.35)
    page.insert_textbox(pymupdf.Rect(W - MR - 250, y, W - MR, y + 26), f"ĐẠI DIỆN {comp.get('short_name', 'CÔNG TY MINH PHÚ').upper()}\n(Xác nhận hồ sơ kỹ thuật)", fontname="F_B", fontsize=7.8, color=C_RED, align=pymupdf.TEXT_ALIGN_CENTER, lineheight=1.35)

    # Page Footers across all pages
    total_pgs = len(doc)
    for pi, p in enumerate(doc):
        p.draw_line((ML, H - 24), (W - MR, H - 24), color=C_BORDER, width=0.5)
        p.insert_text((ML, H - 14), f"{comp.get('name', 'MINH PHÚ HVAC')} — Hotline: {comp.get('hotline', '0967 986 586')} — Chuẩn TCVN 5687:2024 & QCVN 09:2017/BXD", fontname="F_R", fontsize=6.6, color=C_MUTED)
        pg_txt = f"Trang {pi + 1} / {total_pgs}"
        tw_p = f_bold.text_length(pg_txt, fontsize=6.8)
        p.insert_text((W - MR - tw_p, H - 14), pg_txt, fontname="F_B", fontsize=6.8, color=C_BLUE_HEAD)

    raw_pdf = doc.tobytes(deflate=True, garbage=3)
    doc.close()
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(raw_pdf)
    return raw_pdf


# ==============================================================================
# 2. LIVE-FORMULA OPENXML EXCEL (.XLSX) REPORT GENERATOR
# ==============================================================================
def generate_hvac_report_xlsx(payload: dict, logo_path: str, out_path: str = None) -> bytes:
    comp = payload.get("company", {})
    meta = payload.get("meta", {})
    calc = payload.get("calc_result", {}) or {}
    duct = payload.get("duct_result")
    coolpack = payload.get("coolpack_result")
    ai_report = payload.get("ai_report_text", "") or ""

    db = calc.get("design_basis", {})
    sm = calc.get("summary", {})
    rooms = calc.get("rooms", [])

    shared_strings = []
    ss_index = {}

    def get_ss(text: str) -> int:
        t = str(text if text is not None else "")
        if t not in ss_index:
            ss_index[t] = len(shared_strings)
            shared_strings.append(t)
        return ss_index[t]

    rows_xml = []
    merges = []

    def make_cell(r: int, c: int, val=None, style: int = 0, formula: str = None, is_num: bool = False) -> str:
        ref = f"{col_letter(c)}{r}"
        s_attr = f' s="{style}"' if style else ""
        if formula is not None:
            cached = val if val is not None else 0
            return f'<c r="{ref}"{s_attr}><f>{escape(formula)}</f><v>{cached}</v></c>'
        if val is None or val == "":
            return f'<c r="{ref}"{s_attr}/>'
        if is_num:
            return f'<c r="{ref}"{s_attr}><v>{val}</v></c>'
        idx = get_ss(str(val))
        return f'<c r="{ref}" t="s"{s_attr}><v>{idx}</v></c>'

    def add_row(r: int, cells: list, height: float = None):
        ht = f' ht="{height}" customHeight="1"' if height else ""
        rows_xml.append(f'<row r="{r}"{ht}>{"".join(cells)}</row>')

    NCOLS = 14  # A..N (A4 Landscape fitToWidth=1)

    # Rows 1-3: Formal White Letterhead (Col A reserved for Minh Phú Logo)
    add_row(1, [make_cell(1, 1, "", 1), make_cell(1, 2, comp.get("name", "CÔNG TY TNHH PHÁT TRIỂN KỸ THUẬT THƯƠNG MẠI MINH PHÚ"), 1)] + [make_cell(1, c, "", 1) for c in range(3, NCOLS + 1)], height=24)
    merges.append("B1:N1")
    add_row(2, [make_cell(2, 1, "", 13), make_cell(2, 2, f'Địa chỉ: {comp.get("address", "")}', 13)] + [make_cell(2, c, "", 13) for c in range(3, NCOLS + 1)], height=18)
    merges.append("B2:N2")
    add_row(3, [make_cell(3, 1, "", 2), make_cell(3, 2, f'Hotline: {comp.get("hotline", "0967 986 586")}  |  MST: {comp.get("tax_code", "0107709790")}  |  Tiêu chuẩn: TCVN 5687:2024 & QCVN 09:2017/BXD', 2)] + [make_cell(3, c, "", 2) for c in range(3, NCOLS + 1)], height=20)
    merges.append("B3:N3")
    merges.append("A1:A3")

    # Row 5: Minh Phú Red Title Bar (100% Pure White Text)
    add_row(5, [make_cell(5, 1, "BẢNG TÍNH TOÁN TẢI NHIỆT (TCVN 5687:2024), ỐNG GIÓ DAIKIN & THẨM ĐỊNH KỸ THUẬT AI", 3)] + [make_cell(5, c, "", 3) for c in range(2, NCOLS + 1)], height=28)
    merges.append("A5:N5")

    # Rows 6-7: Project & Climate Basis
    now_str = meta.get("date_str") or datetime.now().strftime("%d/%m/%Y")
    add_row(6, [
        make_cell(6, 1, f"Công trình / Dự án: {meta.get('project_name') or 'Hệ thống ĐHKK Daikin'}", 4),
        *[make_cell(6, c, "", 4) for c in range(2, 8)],
        make_cell(6, 8, f"Khu vực khí hậu: {db.get('city_name', 'Hà Nội')} (Cấp {db.get('grade', 'I')}) — t_N={db.get('t_out', 35.4)}°C / t_uN={db.get('twb_out', 28.0)}°C", 4),
        *[make_cell(6, c, "", 4) for c in range(9, NCOLS + 1)],
    ], height=20)
    merges.append("A6:G6")
    merges.append("H6:N6")

    add_row(7, [
        make_cell(7, 1, f"Chủ đầu tư: {meta.get('client_name') or 'Quý Khách Hàng'}   |   Ngày lập: {now_str}", 4),
        *[make_cell(7, c, "", 4) for c in range(2, 8)],
        make_cell(7, 8, f"Hệ số đồng thời: {db.get('diversity_factor', 0.85)}   |   Dự phòng: +{db.get('safety_pct', 10)}%   |   Thu hồi nhiệt HRV: {'Có (' + str(db.get('hrv_efficiency', 70)) + '%)' if db.get('use_hrv') else 'Không'}", 4),
        *[make_cell(7, c, "", 4) for c in range(9, NCOLS + 1)],
    ], height=20)
    merges.append("A7:G7")
    merges.append("H7:N7")

    # Row 9: Table Header (Daikin Deep Blue)
    hdrs = [
        "STT", "Tên phòng", "Tầng", "Diện tích\n(m²)", "Cao BT\n(m)", "Cao TC\n(m)",
        "Khoảng trần\n(m)", "Hướng & Vật liệu", "Nhiệt hiện\n(kW)", "Nhiệt ẩn\n(kW)",
        "Tổng tải\n(kW)", "Tổng tải\n(Btu/h)", "Phụ tải\n(W/m²)", "Gió tươi & Model Daikin đề xuất"
    ]
    add_row(9, [make_cell(9, ci + 1, h, 5) for ci, h in enumerate(hdrs)], height=30)

    r_start = 10
    cur_r = r_start
    for idx, rm in enumerate(rooms):
        rec = rm.get("recommended_unit", {}) or {}
        q_sens_kw = round(rm.get("q_sens_w", 0) / 1000.0, 2)
        q_lat_kw = round(rm.get("q_lat_w", 0) / 1000.0, 2)
        q_tot_kw = round(q_sens_kw + q_lat_kw, 2)
        q_btu_val = int(round(q_tot_kw * 3412.14))
        area = float(rm.get("area", 1.0))
        w_m2_val = round(q_tot_kw * 1000.0 / max(1.0, area), 1)
        h_bt = float(rm.get("h_concrete", 3.6))
        h_tc = float(rm.get("h_ceiling", 3.0))
        plenum_m = round(h_bt - h_tc, 2)
        win_d = rm.get("window_summary") or f"Kính {rm.get('glass_area',0)}m²"
        door_d = f" | Cửa: {rm.get('door_summary')}" if rm.get("door_summary") and rm.get("door_summary") != "—" else ""
        eq_d = f" | TB: {rm.get('equip_items_summary')}" if rm.get("equip_items_summary") else ""
        mat_desc = f"Hướng {rm.get('orientation','')} | {rm.get('wall_name','').split('(')[0].strip()[:22]} | {win_d}{door_d}{eq_d}"
        assigned = rm.get("assigned_units") or []
        if assigned:
            mod_lbl = " + ".join(f"{u.get('qty',1)}× {u.get('model','')}" for u in assigned)
        else:
            qty_s = f"{rec.get('qty',1)}× " if rec.get("qty", 1) > 1 else ""
            mod_lbl = f"{qty_s}{rec.get('model','—')}"
        q_tag = "Đạt QCVN" if rm.get("qcvn_ok", True) else "Lưu ý QCVN"
        model_info = f"OA {int(rm.get('oa_m3h',0))} m³/h | {mod_lbl} ({q_tag})"

        add_row(cur_r, [
            make_cell(cur_r, 1, idx + 1, 7, is_num=True),
            make_cell(cur_r, 2, rm.get("name", ""), 8),
            make_cell(cur_r, 3, rm.get("floor", ""), 7),
            make_cell(cur_r, 4, area, 9, is_num=True),
            make_cell(cur_r, 5, h_bt, 9, is_num=True),
            make_cell(cur_r, 6, h_tc, 9, is_num=True),
            make_cell(cur_r, 7, plenum_m, 9, formula=f"E{cur_r}-F{cur_r}"),
            make_cell(cur_r, 8, mat_desc, 8),
            make_cell(cur_r, 9, q_sens_kw, 9, is_num=True),
            make_cell(cur_r, 10, q_lat_kw, 9, is_num=True),
            make_cell(cur_r, 11, q_tot_kw, 10, formula=f"I{cur_r}+J{cur_r}"),
            make_cell(cur_r, 12, q_btu_val, 11, formula=f"ROUND(K{cur_r}*3412.14,0)"),
            make_cell(cur_r, 13, w_m2_val, 9, formula=f"ROUND(K{cur_r}*1000/D{cur_r},1)"),
            make_cell(cur_r, 14, model_info, 8),
        ], height=22)
        cur_r += 1

    r_end = max(r_start, cur_r - 1)
    tot_r = cur_r
    # Live SUM Total Row
    add_row(tot_r, [
        make_cell(tot_r, 1, "", 6),
        make_cell(tot_r, 2, f"TỔNG CỘNG TỨC THỜI ({len(rooms)} PHÒNG)", 6),
        make_cell(tot_r, 3, "", 6),
        make_cell(tot_r, 4, sm.get("total_area_m2", 0), 12, formula=f"SUM(D{r_start}:D{r_end})"),
        make_cell(tot_r, 5, "", 6),
        make_cell(tot_r, 6, "", 6),
        make_cell(tot_r, 7, "", 6),
        make_cell(tot_r, 8, f"SHR = {sm.get('shr', 0.78)} | Tổng gió tươi = {int(sm.get('total_oa_m3h',0))} m³/h", 6),
        make_cell(tot_r, 9, sm.get("total_sens_kw", 0), 12, formula=f"SUM(I{r_start}:I{r_end})"),
        make_cell(tot_r, 10, sm.get("total_lat_kw", 0), 12, formula=f"SUM(J{r_start}:J{r_end})"),
        make_cell(tot_r, 11, sm.get("total_cooling_kw", 0), 12, formula=f"SUM(K{r_start}:K{r_end})"),
        make_cell(tot_r, 12, int(sm.get("total_cooling_btu", 0)), 14, formula=f"SUM(L{r_start}:L{r_end})"),
        make_cell(tot_r, 13, sm.get("avg_w_per_m2", 0), 12, formula=f"IF(D{tot_r}>0,ROUND(K{tot_r}*1000/D{tot_r},1),0)"),
        make_cell(tot_r, 14, f"≈ {sm.get('total_cooling_rt', 0)} RT", 6),
    ], height=24)

    # Diversified Outdoor Unit Row (with live formula!)
    div_r = tot_r + 1
    div_f = float(db.get("diversity_factor", 0.85))
    out_rec = sm.get("outdoor_rec")
    out_txt = f"Dàn nóng đề xuất: {out_rec['model']} ({out_rec['cooling_kw']} kW)" if out_rec else "Chọn theo tải đồng thời"
    add_row(div_r, [
        make_cell(div_r, 1, "", 15),
        make_cell(div_r, 2, f"TẢI CHỌN DÀN NÓNG SAU HỆ SỐ ĐỒNG THỜI ({div_f})", 15),
        *[make_cell(div_r, c, "", 15) for c in range(3, 11)],
        make_cell(div_r, 11, sm.get("diversified_kw", 0), 16, formula=f"ROUND(K{tot_r}*{div_f},2)"),
        make_cell(div_r, 12, int(sm.get("diversified_btu", 0)), 17, formula=f"ROUND(L{tot_r}*{div_f},0)"),
        make_cell(div_r, 13, round(sm.get("diversified_kw", 0) / 3.517, 2), 16, formula=f"ROUND(K{div_r}/3.517,2)"),
        make_cell(div_r, 14, out_txt, 15),
    ], height=24)
    merges.append(f"B{div_r}:J{div_r}")

    cur_r = div_r + 2

    # Duct Checker Section (if present)
    if duct and duct.get("ok"):
        add_row(cur_r, [make_cell(cur_r, 1, f"PHẦN II. KIỂM TRA ỐNG GIÓ & CỘT ÁP QUẠT — DAIKIN DUCT CHECKER ({duct.get('model')})", 3)] + [make_cell(cur_r, c, "", 3) for c in range(2, NCOLS + 1)], height=24)
        merges.append(f"A{cur_r}:N{cur_r}")
        cur_r += 1
        md = duct.get("main_duct", {})
        bd = duct.get("branch_duct", {})
        fd = duct.get("flex_duct", {})
        rd = duct.get("return_duct", {})
        pb = duct.get("pressure_breakdown", {})
        add_row(cur_r, [
            make_cell(cur_r, 1, "Đoạn ống gió", 5), *[make_cell(cur_r, c, "", 5) for c in range(2, 5)],
            make_cell(cur_r, 5, "Kích thước (mm)", 5), *[make_cell(cur_r, c, "", 5) for c in range(6, 8)],
            make_cell(cur_r, 8, "Lưu lượng (m³/h)", 5),
            make_cell(cur_r, 9, "Vận tốc (m/s)", 5),
            make_cell(cur_r, 10, "Ma sát (Pa/m)", 5),
            make_cell(cur_r, 11, "Tổn thất (Pa)", 5),
            make_cell(cur_r, 12, "Ghi chú & Đánh giá", 5), *[make_cell(cur_r, c, "", 5) for c in range(13, NCOLS + 1)],
        ], height=22)
        merges.extend([f"A{cur_r}:D{cur_r}", f"E{cur_r}:G{cur_r}", f"L{cur_r}:N{cur_r}"])
        cur_r += 1
        d_start = cur_r
        d_items = [
            ("Ống gió chính (Tôn kẽm)", f"{md.get('w_mm')} × {md.get('h_mm')}", duct.get("airflow_m3h", 0), md.get("hyd",{}).get("velocity_ms", 0), md.get("hyd",{}).get("dp_pa_m", 0), md.get("dp_pa", 0), duct.get("noise_status", "")),
            ("Ống nhánh cứng (Mỗi nhánh)", f"{bd.get('w_mm')} × {bd.get('h_mm')}", duct.get("branch_airflow_m3h", 0), bd.get("hyd",{}).get("velocity_ms", 0), bd.get("hyd",{}).get("dp_pa_m", 0), bd.get("dp_pa", 0), f"{duct.get('num_branches')} nhánh"),
            ("Ống gió mềm bảo ôn", f"Ø{fd.get('dia_mm')} (L={fd.get('len_m')}m)", duct.get("branch_airflow_m3h", 0), fd.get("hyd",{}).get("velocity_ms", 0), fd.get("hyd",{}).get("dp_pa_m", 0), fd.get("dp_pa", 0), f"Tổng {duct.get('flex_total_m')} m"),
            ("Ống gió hồi", f"{rd.get('w_mm')} × {rd.get('h_mm')}", duct.get("airflow_m3h", 0), rd.get("hyd",{}).get("velocity_ms", 0), rd.get("hyd",{}).get("dp_pa_m", 0), rd.get("dp_pa", 0), f"Tổng tôn ≈ {duct.get('sheet_metal_m2')} m²"),
            ("Phụ kiện (Cút/Tê/VCD) + Cửa gió", "Cục bộ + Lưới lọc", 0, 0, 0, round(pb.get("fittings_pa", 0) + pb.get("grilles_pa", 0), 1), duct.get("grilles",{}).get("supply_rec", "")),
        ]
        for nm, sz, qv, vv, mv, dpv, note in d_items:
            add_row(cur_r, [
                make_cell(cur_r, 1, nm, 8), *[make_cell(cur_r, c, "", 8) for c in range(2, 5)],
                make_cell(cur_r, 5, sz, 7), *[make_cell(cur_r, c, "", 7) for c in range(6, 8)],
                make_cell(cur_r, 8, qv, 11, is_num=True),
                make_cell(cur_r, 9, vv, 9, is_num=True),
                make_cell(cur_r, 10, mv, 9, is_num=True),
                make_cell(cur_r, 11, dpv, 9, is_num=True),
                make_cell(cur_r, 12, note, 8), *[make_cell(cur_r, c, "", 8) for c in range(13, NCOLS + 1)],
            ], height=20)
            merges.extend([f"A{cur_r}:D{cur_r}", f"E{cur_r}:G{cur_r}", f"L{cur_r}:N{cur_r}"])
            cur_r += 1
        d_end = cur_r - 1
        add_row(cur_r, [
            make_cell(cur_r, 1, f"TỔNG TỔN THẤT CỘT ÁP ΔP (ESP ĐM {duct.get('esp_rated_pa'):.0f} Pa / Max {duct.get('esp_max_pa'):.0f} Pa)", 6),
            *[make_cell(cur_r, c, "", 6) for c in range(2, 11)],
            make_cell(cur_r, 11, pb.get("total_pa", 0), 12, formula=f"SUM(K{d_start}:K{d_end})"),
            make_cell(cur_r, 12, duct.get("esp_verdict", ""), 6),
            *[make_cell(cur_r, c, "", 6) for c in range(13, NCOLS + 1)],
        ], height=24)
        merges.extend([f"A{cur_r}:J{cur_r}", f"L{cur_r}:N{cur_r}"])
        cur_r += 2

    # AI Consultation Summary Section
    if ai_report.strip():
        add_row(cur_r, [make_cell(cur_r, 1, "PHẦN III. THẨM ĐỊNH & TƯ VẤN KỸ THUẬT CHUYÊN SÂU (AI ENGINEER — TCVN 5687:2024)", 3)] + [make_cell(cur_r, c, "", 3) for c in range(2, NCOLS + 1)], height=24)
        merges.append(f"A{cur_r}:N{cur_r}")
        cur_r += 1
        for ln in ai_report.replace("\r\n", "\n").split("\n"):
            if not ln.strip():
                continue
            add_row(cur_r, [make_cell(cur_r, 1, ln.strip(), 8)] + [make_cell(cur_r, c, "", 8) for c in range(2, NCOLS + 1)], height=20)
            merges.append(f"A{cur_r}:N{cur_r}")
            cur_r += 1

    # Column widths for A..N
    col_widths = [6, 22, 10, 10, 9, 9, 11, 28, 10, 10, 11, 13, 10, 34]
    cols_xml = "<cols>" + "".join(
        f'<col min="{i+1}" max="{i+1}" width="{w}" customWidth="1"/>' for i, w in enumerate(col_widths)
    ) + "</cols>"
    merges_xml = f'<mergeCells count="{len(merges)}">' + "".join(f'<mergeCell ref="{m}"/>' for m in merges) + "</mergeCells>"

    sheet_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
           xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheetPr><pageSetUpPr fitToPage="1"/></sheetPr>
  <sheetViews><sheetView tabSelected="1" workbookViewId="0"/></sheetViews>
  {cols_xml}
  <sheetData>{"".join(rows_xml)}</sheetData>
  {merges_xml}
  <pageMargins left="0.35" right="0.35" top="0.4" bottom="0.4" header="0.2" footer="0.2"/>
  <pageSetup paperSize="9" orientation="landscape" fitToWidth="1" fitToHeight="0"/>
  <drawing r:id="rId1"/>
</worksheet>"""

    ss_xml = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="{len(shared_strings)}" uniqueCount="{len(shared_strings)}">'
        + "".join(f'<si><t xml:space="preserve">{escape(s)}</t></si>' for s in shared_strings)
        + "</sst>"
    )

    # Pure White Letterhead + Red Title Bars (Pure White text) + Daikin Blue Table Headers (Zero stray yellow!)
    styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <numFmts count="2">
    <numFmt numFmtId="164" formatCode="#,##0"/>
    <numFmt numFmtId="165" formatCode="#,##0.00"/>
  </numFmts>
  <fonts count="7">
    <font><sz val="10"/><color rgb="FF0F172A"/><name val="Arial"/></font>
    <font><b/><sz val="13"/><color rgb="FF991B1B"/><name val="Arial"/></font>
    <font><sz val="9.5"/><color rgb="FF334155"/><name val="Arial"/></font>
    <font><b/><sz val="11.5"/><color rgb="FFFFFFFF"/><name val="Arial"/></font>
    <font><b/><sz val="9.5"/><color rgb="FFFFFFFF"/><name val="Arial"/></font>
    <font><b/><sz val="10"/><color rgb="FF0F172A"/><name val="Arial"/></font>
    <font><b/><sz val="10"/><color rgb="FF991B1B"/><name val="Arial"/></font>
  </fonts>
  <fills count="7">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF991B1B"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFFFFFFF"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFF8FAFC"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF005A8D"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFEFF6FF"/></patternFill></fill>
  </fills>
  <borders count="3">
    <border><left/><right/><top/><bottom/><diagonal/></border>
    <border>
      <left style="thin"><color rgb="FFCBD5E1"/></left>
      <right style="thin"><color rgb="FFCBD5E1"/></right>
      <top style="thin"><color rgb="FFCBD5E1"/></top>
      <bottom style="thin"><color rgb="FFCBD5E1"/></bottom>
      <diagonal/>
    </border>
    <border>
      <left/><right/><top/>
      <bottom style="medium"><color rgb="FF991B1B"/></bottom>
      <diagonal/>
    </border>
  </borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="18">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>
    <xf numFmtId="0" fontId="1" fillId="3" borderId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment vertical="center"/></xf>
    <xf numFmtId="0" fontId="2" fillId="3" borderId="2" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center"/></xf>
    <xf numFmtId="0" fontId="3" fillId="2" borderId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
    <xf numFmtId="0" fontId="5" fillId="4" borderId="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="4" fillId="5" borderId="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="6" fillId="6" borderId="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" applyBorder="1" applyAlignment="1"><alignment horizontal="left" vertical="center" wrapText="1"/></xf>
    <xf numFmtId="165" fontId="0" fillId="0" borderId="1" applyNumberFormat="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <xf numFmtId="165" fontId="6" fillId="0" borderId="1" applyNumberFormat="1" applyFont="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <xf numFmtId="164" fontId="0" fillId="0" borderId="1" applyNumberFormat="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <xf numFmtId="165" fontId="6" fillId="6" borderId="1" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <xf numFmtId="0" fontId="2" fillId="3" borderId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment vertical="center"/></xf>
    <xf numFmtId="164" fontId="6" fillId="6" borderId="1" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <xf numFmtId="0" fontId="4" fillId="2" borderId="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center"/></xf>
    <xf numFmtId="165" fontId="4" fillId="2" borderId="1" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <xf numFmtId="164" fontId="4" fillId="2" borderId="1" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
  </cellXfs>
</styleSheet>"""

    if os.path.exists(logo_path):
        with open(logo_path, "rb") as lf:
            logo_bytes = lf.read()
    else:
        im_tmp = Image.new("RGBA", (120, 120), (153, 27, 27, 255))
        buf_tmp = io.BytesIO()
        im_tmp.save(buf_tmp, format="PNG")
        logo_bytes = buf_tmp.getvalue()

    drawing_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<xdr:wsDr xmlns:xdr="http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"
          xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <xdr:twoCellAnchor editAs="oneCell">
    <xdr:from><xdr:col>0</xdr:col><xdr:colOff>19050</xdr:colOff><xdr:row>0</xdr:row><xdr:rowOff>19050</xdr:rowOff></xdr:from>
    <xdr:to><xdr:col>1</xdr:col><xdr:colOff>-19050</xdr:colOff><xdr:row>3</xdr:row><xdr:rowOff>-19050</xdr:rowOff></xdr:to>
    <xdr:pic>
      <xdr:nvPicPr><xdr:cNvPr id="2" name="MinhPhuLogo"/><xdr:cNvPicPr/></xdr:nvPicPr>
      <xdr:blipFill><a:blip r:embed="rId1"/><a:stretch><a:fillRect/></a:stretch></xdr:blipFill>
      <xdr:spPr><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></xdr:spPr>
    </xdr:pic>
    <xdr:clientData/>
  </xdr:twoCellAnchor>
</xdr:wsDr>"""

    out_buf = io.BytesIO()
    with zipfile.ZipFile(out_buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  <Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>
  <Override PartName="/xl/drawings/drawing1.xml" ContentType="application/vnd.openxmlformats-officedocument.drawing+xml"/>
</Types>""")
        z.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>""")
        z.writestr("xl/workbook.xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets><sheet name="Tinh Nhiet TCVN 5687" sheetId="1" r:id="rId1"/></sheets>
</workbook>""")
        z.writestr("xl/_rels/workbook.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>
</Relationships>""")
        z.writestr("xl/worksheets/_rels/sheet1.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing" Target="../drawings/drawing1.xml"/>
</Relationships>""")
        z.writestr("xl/drawings/_rels/drawing1.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/logo.png"/>
</Relationships>""")
        z.writestr("xl/styles.xml", styles_xml)
        z.writestr("xl/sharedStrings.xml", ss_xml)
        z.writestr("xl/worksheets/sheet1.xml", sheet_xml)
        z.writestr("xl/drawings/drawing1.xml", drawing_xml)
        z.writestr("xl/media/logo.png", logo_bytes)

    raw_xlsx = out_buf.getvalue()
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(raw_xlsx)
    return raw_xlsx
