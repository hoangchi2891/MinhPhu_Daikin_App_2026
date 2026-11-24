# -*- coding: utf-8 -*-
"""
pdf_exporter.py — Pure Vector Multi-Page A4 PDF Quotation Generator for Minh Phú
Theme: Formal White Letterhead (Yellow ONLY on Minh Phú Logo)
       + Minh Phú Red Title Bars with 100% Pure White Text (#991B1B / #FFFFFF)
       + Daikin Blue Table Headers (#005A8D / #FFFFFF)
       + Prominent Equipment Technical Specifications & Duct Collar Appendix right below Quotation.
"""

import io
import os
import pymupdf
from PIL import Image
from excel_exporter import make_qr_png_bytes


def make_red_bar_png(width: int = 1200, height: int = 48) -> bytes:
    """Create smooth single-hue Minh Phú Red bar PNG (pure red gradient, zero yellow, zero blue)."""
    im = Image.new("RGB", (width, height))
    px = im.load()
    c0 = (136, 22, 22)   # #881616
    c1 = (165, 28, 28)   # #A51C1C
    for x in range(width):
        u = x / max(1, width - 1)
        c = (
            int(c0[0] + (c1[0] - c0[0]) * u),
            int(c0[1] + (c1[1] - c0[1]) * u),
            int(c0[2] + (c1[2] - c0[2]) * u),
        )
        for y in range(height):
            px[x, y] = c
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return buf.getvalue()


def fmt_vn(n) -> str:
    return f"{int(round(float(n or 0))):,}".replace(",", ".")


def wrap_lines(font: pymupdf.Font, text: str, fontsize: float, max_w: float) -> list:
    out = []
    for para in (text or "").split("\n"):
        words = para.split(" ")
        if not words:
            out.append("")
            continue
        cur = words[0]
        for w in words[1:]:
            cand = cur + " " + w
            if font.text_length(cand, fontsize=fontsize) <= max_w:
                cur = cand
            else:
                out.append(cur)
                cur = w
        out.append(cur)
    return out or [""]


def generate_quote_pdf(payload: dict, web_dir: str, out_path: str = None) -> bytes:
    comp = payload.get("company", {})
    bank = comp.get("bank", {})
    q = payload.get("quote", {})
    totals = payload.get("totals", {})
    equip_rows = payload.get("equip_rows", [])
    install_rows = payload.get("install_rows", [])

    qr_bytes = make_qr_png_bytes(
        q.get("qr_url", ""),
        bank,
        q.get("code", "BG-MP"),
        totals.get("qrAmount", 0),
    )

    W, H = 595.0, 842.0  # A4 points
    ML, MR = 28.0, 28.0
    TW = W - ML - MR     # 539 pt
    BOTTOM_LIMIT = H - 36.0

    font_reg_path = r"C:\Windows\Fonts\arial.ttf"
    font_bold_path = r"C:\Windows\Fonts\arialbd.ttf"
    font_ital_path = r"C:\Windows\Fonts\arialbi.ttf"
    f_reg = pymupdf.Font(fontfile=font_reg_path)
    f_bold = pymupdf.Font(fontfile=font_bold_path)

    doc = pymupdf.open()
    red_bar_bytes = make_red_bar_png(1200, 48)
    logo_path = os.path.join(web_dir, "assets", "logo_minh_phu.png")
    show_images = bool(q.get("show_images", True))

    # Executive White-Priority Palette — ONLY Logo box has Yellow; ALL Red bars have PURE WHITE text!
    C_WHITE = (1.0, 1.0, 1.0)
    C_RED = (0.60, 0.106, 0.106)       # #991B1B
    C_RED_DARK = (0.50, 0.11, 0.11)    # #7F1D1D
    C_LOGO_GOLD = (0.98, 0.80, 0.08)   # #FACC15 (ONLY for Minh Phú Logo background)
    C_LOGO_BORDER = (0.92, 0.70, 0.03) # #EAB308 (ONLY for Minh Phú Logo border)
    C_BLUE_HEAD = (0.0, 0.353, 0.553)  # #005A8D Daikin Deep Blue
    C_DAIKIN = (0.0, 0.467, 0.714)     # #0077B6 Daikin Blue
    C_ICE_PART = (0.937, 0.965, 1.0)   # #EFF6FF Soft Ice-Blue for Part A/B
    C_ICE_SOFT = (0.941, 0.976, 1.0)   # #F0F9FF Duct Collar highlight
    C_SLATE_BG = (0.973, 0.980, 0.988) # #F8FAFC Clean Neutral Tint
    C_SLATE = (0.059, 0.090, 0.165)    # #0F172A Dark Navy Text
    C_MUTED = (0.278, 0.333, 0.412)    # #475569 Slate Muted
    C_BORDER = (0.796, 0.835, 0.882)   # #CBD5E1 Crisp Border
    C_BLUE_BORDER = (0.749, 0.859, 0.996)

    # Column widths (sum = 539 pt): STT(26), Desc(232), Origin(68), Unit(36), Qty(35), Price(68), Total(74)
    COLS = [26.0, 232.0, 68.0, 36.0, 35.0, 68.0, 74.0]
    COL_X = [ML]
    for cw in COLS:
        COL_X.append(COL_X[-1] + cw)

    def new_a4_page(is_first: bool = False):
        p = doc.new_page(width=W, height=H)
        p.insert_font(fontname="F_R", fontfile=font_reg_path)
        p.insert_font(fontname="F_B", fontfile=font_bold_path)
        p.insert_font(fontname="F_BI", fontfile=font_ital_path)
        if is_first:
            # FORMAL PURE WHITE CORPORATE LETTERHEAD (Phần thông tin tiêu đề nền trắng trang trọng)
            # Yellow is strictly ONLY inside the Minh Phú Logo badge on the left!
            if os.path.exists(logo_path):
                logo_bg = pymupdf.Rect(ML, 20, ML + 58, 78)
                p.draw_rect(logo_bg, color=C_LOGO_BORDER, fill=C_LOGO_GOLD, width=1.2, radius=0.08)
                p.insert_image(pymupdf.Rect(ML + 2, 22, ML + 56, 76), filename=logo_path)

            cx = ML + 68
            p.insert_text((cx, 32.5), comp.get("name", ""), fontname="F_B", fontsize=9.8, color=C_RED)
            p.insert_text(
                (cx, 44.5),
                f'ĐẠI LÝ & NHÀ THẦU THI CÔNG ĐHKK DAIKIN  •  "{comp.get("slogan", "HOÀN TIỀN NẾU KHÔNG HÀI LÒNG")}"',
                fontname="F_B",
                fontsize=7.0,
                color=C_BLUE_HEAD,
            )
            addr_lines = wrap_lines(f_reg, f'Địa chỉ: {comp.get("address", "")}', 7.4, 328.0)
            ay = 56.5
            for al in addr_lines[:2]:
                p.insert_text((cx, ay), al, fontname="F_R", fontsize=7.4, color=C_SLATE)
                ay += 9.5
            p.insert_text(
                (cx, max(ay + 1.0, 72.5)),
                f'Hotline: {comp.get("hotline", "0967 986 586")}   |   MST: {comp.get("tax_code", "0107709790")}   |   Web: {comp.get("website", "").replace("https://", "")}',
                fontname="F_B",
                fontsize=7.4,
                color=C_MUTED,
            )

            # Dignified Pure White Bordered Quotation Reference Card on Right
            doc_badge = pymupdf.Rect(436, 20, W - MR, 78)
            p.draw_rect(doc_badge, color=C_BORDER, fill=C_WHITE, width=1.0)
            p.draw_rect(pymupdf.Rect(436, 20, W - MR, 24.5), color=C_RED, fill=C_RED, width=0)
            p.insert_textbox(
                pymupdf.Rect(438, 28, W - MR - 2, 42),
                "BÁO GIÁ DỰ ÁN",
                fontname="F_B",
                fontsize=8.8,
                color=C_RED,
                align=pymupdf.TEXT_ALIGN_CENTER,
            )
            p.insert_textbox(
                pymupdf.Rect(438, 43, W - MR - 2, 76),
                f"Số: {q.get('code', '')}\nNgày: {q.get('date_str', '')}",
                fontname="F_B",
                fontsize=7.3,
                color=C_SLATE,
                align=pymupdf.TEXT_ALIGN_CENTER,
                lineheight=1.45,
            )

            # Crisp Corporate Double Divider Hairline (Red + Daikin Blue)
            p.draw_line((ML, 85.0), (W - MR, 85.0), color=C_RED, width=2.2)
            p.draw_line((ML, 88.2), (W - MR, 88.2), color=C_BLUE_HEAD, width=0.8)
            return p, 96.0
        return p, 30.0

    def draw_table_header(p, y: float) -> float:
        rh = 22.0
        p.draw_rect(pymupdf.Rect(ML, y, W - MR, y + rh), color=C_BLUE_HEAD, fill=C_BLUE_HEAD, width=0.6)
        labels = ["STT", "Hình ảnh, Tên thiết bị & Quy cách kỹ thuật", "Xuất xứ", "ĐVT", "SL", "Đơn giá", "Thành tiền"]
        for ci, lb in enumerate(labels):
            x0 = COL_X[ci]
            if ci > 0:
                p.draw_line((x0, y), (x0, y + rh), color=C_WHITE, width=0.4)
            tw = f_bold.text_length(lb, fontsize=8.0)
            p.insert_text((x0 + (COLS[ci] - tw) / 2, y + 14.2), lb, fontname="F_B", fontsize=8.0, color=C_WHITE)
        return y + rh

    page, y = new_a4_page(is_first=True)

    # MINH PHÚ RED DOCUMENT TITLE BAR — 100% PURE WHITE TEXT
    mode = q.get("mode", "BOTH")
    doc_title = (
        "BẢNG BÁO GIÁ CUNG CẤP THIẾT BỊ ĐIỀU HÒA KHÔNG KHÍ DAIKIN"
        if mode == "EQUIP_ONLY"
        else (
            "BẢNG BÁO GIÁ VẬT TƯ & NHÂN CÔNG LẮP ĐẶT HỆ THỐNG ĐHKK"
            if mode == "INSTALL_ONLY"
            else "BẢNG BÁO GIÁ CUNG CẤP THIẾT BỊ & THI CÔNG LẮP ĐẶT HỆ THỐNG ĐHKK"
        )
    )
    title_rect = pymupdf.Rect(ML, y, W - MR, y + 23.0)
    page.insert_image(title_rect, stream=red_bar_bytes, keep_proportion=False)
    tw_t = f_bold.text_length(doc_title, fontsize=10.5)
    page.insert_text((ML + (TW - tw_t) / 2, y + 15.0), doc_title, fontname="F_B", fontsize=10.5, color=C_WHITE)
    y += 30.0

    # Client Meta Box (Clean Pure White with crisp border + Daikin Blue left bar)
    meta_h = 47.0
    meta_rect = pymupdf.Rect(ML, y, W - MR, y + meta_h)
    page.draw_rect(meta_rect, color=C_BORDER, fill=C_WHITE, width=0.8)
    page.draw_rect(pymupdf.Rect(ML, y, ML + 3.5, y + meta_h), color=C_BLUE_HEAD, fill=C_BLUE_HEAD, width=0)

    rx = ML + 332.0
    page.insert_text((ML + 10, y + 14), f"Kính gửi (Chủ đầu tư): {q.get('client_name') or 'Quý Khách Hàng'}", fontname="F_B", fontsize=8.2, color=C_SLATE)
    page.insert_text((rx, y + 14), f"Số báo giá: {q.get('code', '')}", fontname="F_B", fontsize=8.2, color=C_RED)

    proj_str = f"Công trình / Dự án: {q.get('project_name') or 'Hệ thống ĐHKK'}"
    page.insert_text((ML + 10, y + 27.5), proj_str, fontname="F_R", fontsize=8.0, color=C_SLATE)
    page.insert_text((rx, y + 27.5), f"Ngày báo giá: {q.get('date_str', '')}", fontname="F_R", fontsize=8.0, color=C_SLATE)

    addr_str = f"Địa điểm: {q.get('project_addr') or '—'}  |  SĐT: {q.get('client_phone') or '—'}"
    page.insert_text((ML + 10, y + 41), addr_str, fontname="F_R", fontsize=8.0, color=C_SLATE)
    page.insert_text((rx, y + 41), f"Phụ trách: {q.get('author', '')}", fontname="F_R", fontsize=8.0, color=C_SLATE)
    y += meta_h + 10.0

    y = draw_table_header(page, y)

    def ensure_space(needed_h: float, repeat_tbl_header: bool = True):
        nonlocal page, y
        if y + needed_h > BOTTOM_LIMIT:
            page, y = new_a4_page(is_first=False)
            if repeat_tbl_header:
                y = draw_table_header(page, y)

    def draw_part_banner(letter: str, title: str, amount_val: float):
        nonlocal y
        rh = 20.5
        ensure_space(rh)
        page.draw_rect(pymupdf.Rect(ML, y, W - MR, y + rh), color=C_BLUE_BORDER, fill=C_ICE_PART, width=0.7)
        page.draw_rect(pymupdf.Rect(ML, y, ML + 3.0, y + rh), color=C_BLUE_HEAD, fill=C_BLUE_HEAD, width=0)
        tw_l = f_bold.text_length(letter, fontsize=8.6)
        page.insert_text((COL_X[0] + (COLS[0] - tw_l) / 2, y + 13.8), letter, fontname="F_B", fontsize=8.6, color=C_SLATE)
        page.draw_line((COL_X[1], y), (COL_X[1], y + rh), color=C_BLUE_BORDER, width=0.5)
        page.insert_text((COL_X[1] + 6, y + 13.8), title, fontname="F_B", fontsize=8.6, color=C_SLATE)
        page.draw_line((COL_X[6], y), (COL_X[6], y + rh), color=C_BLUE_BORDER, width=0.5)
        amt_s = fmt_vn(amount_val)
        tw_a = f_bold.text_length(amt_s, fontsize=8.6)
        page.insert_text((COL_X[7] - tw_a - 5, y + 13.8), amt_s, fontname="F_B", fontsize=8.6, color=C_RED)
        y += rh

    def draw_item_row(stt_s: str, name_lines: list, model_s: str, spec_lines: list, origin_s: str, unit_s: str, qty_s: str, uprice_s: str, ltotal_s: str, img_rel: str = ""):
        nonlocal y
        img_full = os.path.join(web_dir, img_rel.replace("/", os.sep)) if (show_images and img_rel) else ""
        has_img = bool(img_full and os.path.exists(img_full))

        n_lines = len(name_lines) + (1 if model_s else 0) + len(spec_lines)
        rh = max(40.0 if has_img else 20.0, 8.0 + n_lines * 10.4)
        ensure_space(rh)
        row_rect = pymupdf.Rect(ML, y, W - MR, y + rh)
        page.draw_rect(row_rect, color=C_BORDER, fill=C_WHITE, width=0.5)
        for ci in range(1, 7):
            page.draw_line((COL_X[ci], y), (COL_X[ci], y + rh), color=C_BORDER, width=0.4)

        mid_y = y + rh / 2 + 2.8
        # STT
        tw = f_reg.text_length(stt_s, fontsize=8.1)
        page.insert_text((COL_X[0] + (COLS[0] - tw) / 2, mid_y), stt_s, fontname="F_R", fontsize=8.1, color=C_SLATE)

        # Product Image thumbnail if available
        tx_start = COL_X[1] + 5
        if has_img:
            im_box = pymupdf.Rect(COL_X[1] + 4, y + (rh - 34) / 2, COL_X[1] + 46, y + (rh + 34) / 2)
            page.draw_rect(im_box, color=C_BORDER, fill=C_WHITE, width=0.5, radius=0.06)
            page.insert_image(pymupdf.Rect(im_box.x0 + 2, im_box.y0 + 2, im_box.x1 - 2, im_box.y1 - 2), filename=img_full)
            tx_start = COL_X[1] + 51

        # Description
        ty = y + 11.0
        for ln in name_lines:
            page.insert_text((tx_start, ty), ln, fontname="F_B" if model_s else "F_R", fontsize=8.0, color=C_SLATE)
            ty += 10.3
        if model_s:
            page.insert_text((tx_start, ty), model_s, fontname="F_B", fontsize=7.9, color=C_BLUE_HEAD)
            ty += 10.0
        for sln in spec_lines:
            page.insert_text((tx_start, ty), sln, fontname="F_R", fontsize=7.3, color=C_MUTED)
            ty += 9.5

        # Origin (wrap if needed)
        orig_lines = wrap_lines(f_reg, origin_s, 7.9, COLS[2] - 6)
        oy = y + (rh - len(orig_lines) * 9.8) / 2 + 7.8
        for oln in orig_lines:
            otw = f_reg.text_length(oln, fontsize=7.9)
            page.insert_text((COL_X[2] + (COLS[2] - otw) / 2, oy), oln, fontname="F_R", fontsize=7.9, color=C_SLATE)
            oy += 9.8

        # Unit
        utw = f_reg.text_length(unit_s, fontsize=8.0)
        page.insert_text((COL_X[3] + (COLS[3] - utw) / 2, mid_y), unit_s, fontname="F_R", fontsize=8.0, color=C_SLATE)

        # Qty
        qtw = f_bold.text_length(qty_s, fontsize=8.1)
        page.insert_text((COL_X[4] + (COLS[4] - qtw) / 2, mid_y), qty_s, fontname="F_B", fontsize=8.1, color=C_SLATE)

        # Unit Price
        ptw = f_reg.text_length(uprice_s, fontsize=8.1)
        page.insert_text((COL_X[6] - ptw - 5, mid_y), uprice_s, fontname="F_R", fontsize=8.1, color=C_SLATE)

        # Line Total
        ttw = f_bold.text_length(ltotal_s, fontsize=8.2)
        page.insert_text((COL_X[7] - ttw - 5, mid_y), ltotal_s, fontname="F_B", fontsize=8.2, color=C_SLATE)

        y += rh

    # PART A
    if equip_rows:
        draw_part_banner("A", "PHẦN CUNG CẤP THIẾT BỊ ĐIỀU HÒA KHÔNG KHÍ CHÍNH HÃNG DAIKIN", totals.get("sumEquip", 0))
        for r in equip_rows:
            img_rel = r.get("image", "")
            has_im = bool(show_images and img_rel and os.path.exists(os.path.join(web_dir, img_rel.replace("/", os.sep))))
            wrap_w = COLS[1] - (56 if has_im else 10)
            n_lines = wrap_lines(f_bold, r["name"], 8.0, wrap_w)
            s_lines = wrap_lines(f_reg, r["spec_note"], 7.3, wrap_w) if r.get("spec_note") else []
            draw_item_row(
                str(r["stt"]),
                n_lines,
                f"Model: {r['model']}",
                s_lines,
                r["origin"],
                r["unit"],
                fmt_vn(r["qty"]),
                fmt_vn(r["unit_price"]),
                fmt_vn(r["line_total"]),
                img_rel=img_rel,
            )

    # PART B
    if install_rows:
        p_let = "B" if equip_rows else "A"
        draw_part_banner(p_let, "PHẦN VẬT TƯ PHỤ & NHÂN CÔNG LẮP ĐẶT HỆ THỐNG", totals.get("sumInstall", 0))
        last_grp = None
        sub_stt = 1
        for r in install_rows:
            if r["group_name"] != last_grp:
                last_grp = r["group_name"]
                sub_stt = 1
                gh = 18.5
                ensure_space(gh)
                page.draw_rect(pymupdf.Rect(ML, y, W - MR, y + gh), color=C_BORDER, fill=C_SLATE_BG, width=0.5)
                tw_g = f_bold.text_length(r["group_code"], fontsize=8.2)
                page.insert_text((COL_X[0] + (COLS[0] - tw_g) / 2, y + 12.6), r["group_code"], fontname="F_B", fontsize=8.2, color=C_BLUE_HEAD)
                page.draw_line((COL_X[1], y), (COL_X[1], y + gh), color=C_BORDER, width=0.4)
                page.insert_text((COL_X[1] + 5, y + 12.6), r["group_name"], fontname="F_B", fontsize=8.2, color=C_BLUE_HEAD)
                y += gh

            n_lines = wrap_lines(f_reg, r["name"], 8.2, COLS[1] - 10)
            qty_s = f"{r['qty']:g}".replace(".", ",")
            draw_item_row(
                str(sub_stt),
                n_lines,
                "",
                [],
                r["brand"],
                r["unit"],
                qty_s,
                fmt_vn(r["unit_price"]),
                fmt_vn(r["line_total"]),
            )
            sub_stt += 1

    # SUMMARY ROWS — Grand Total Bar in Minh Phú Red with 100% Pure White Text!
    sum_items = []
    if equip_rows:
        sum_items.append(("Cộng Phần Thiết bị điều hòa:", fmt_vn(totals.get("sumEquip", 0)), False))
    if install_rows:
        sum_items.append(("Cộng Phần Vật tư & Nhân công lắp đặt:", fmt_vn(totals.get("sumInstall", 0)), False))
    sum_items.append(("Tổng cộng trước thuế:", fmt_vn(totals.get("subTotal", 0)), False))
    sum_items.append((f"Thuế GTGT (VAT {int(q.get('vat_rate', 10))}%):", fmt_vn(totals.get("vatAmount", 0)), False))
    sum_items.append(("TỔNG GIÁ TRỊ THANH TOÁN (VNĐ):", fmt_vn(totals.get("grandTotal", 0)), True))

    ensure_space(len(sum_items) * 20.0 + 30.0, repeat_tbl_header=False)
    for label, val_s, is_grand in sum_items:
        rh = 22.0 if is_grand else 18.5
        if is_grand:
            page.insert_image(pymupdf.Rect(ML, y, W - MR, y + rh), stream=red_bar_bytes, keep_proportion=False)
            page.draw_line((COL_X[6], y), (COL_X[6], y + rh), color=C_WHITE, width=0.4)
            txt_c = C_WHITE
            fsize = 9.2
        else:
            page.draw_rect(pymupdf.Rect(ML, y, W - MR, y + rh), color=C_BORDER, fill=C_SLATE_BG, width=0.5)
            page.draw_line((COL_X[6], y), (COL_X[6], y + rh), color=C_BORDER, width=0.4)
            txt_c = C_SLATE
            fsize = 8.4
        ltw = f_bold.text_length(label, fontsize=fsize)
        page.insert_text((COL_X[6] - ltw - 8, y + rh / 2 + 3.0), label, fontname="F_B", fontsize=fsize, color=txt_c)
        vtw = f_bold.text_length(val_s, fontsize=fsize)
        page.insert_text((COL_X[7] - vtw - 5, y + rh / 2 + 3.0), val_s, fontname="F_B", fontsize=fsize, color=txt_c)
        y += rh

    # Amount in words box (Clean White/Slate with Red Left Accent — ZERO Yellow)
    y += 6.0
    words_txt = f"Số tiền bằng chữ: {q.get('amount_in_words', '')}"
    w_lines = wrap_lines(f_bold, words_txt, 8.4, TW - 18)
    wh = max(21.0, 8.0 + len(w_lines) * 11.0)
    page.draw_rect(pymupdf.Rect(ML, y, W - MR, y + wh), color=C_BORDER, fill=C_SLATE_BG, width=0.7)
    page.draw_rect(pymupdf.Rect(ML, y, ML + 3.5, y + wh), color=C_RED, fill=C_RED, width=0)
    wy = y + 13.5
    for wl in w_lines:
        page.insert_text((ML + 10, wy), wl, fontname="F_BI", fontsize=8.4, color=C_RED_DARK)
        wy += 11.0
    y += wh + 14.0

    # TECHNICAL SPECIFICATION & DUCT PLENUM APPENDIX IMMEDIATELY BELOW QUOTATION!
    app_cfg = payload.get("appendix_config", {})
    app_rows = payload.get("appendix_rows", [])
    if app_cfg.get("enabled") and app_rows:
        ensure_space(74.0, repeat_tbl_header=False)
        # Minh Phú Red Title Bar with 100% Pure White Text!
        app_bar_rect = pymupdf.Rect(ML, y, W - MR, y + 22.0)
        page.insert_image(app_bar_rect, stream=red_bar_bytes, keep_proportion=False)
        page.insert_text(
            (ML + 10, y + 14.6),
            "PHỤ LỤC THÔNG SỐ KỸ THUẬT THIẾT BỊ, ỐNG ĐỒNG & KÍCH THƯỚC CÔN ĐẦU MÁY",
            fontname="F_B",
            fontsize=8.6,
            color=C_WHITE,
        )
        y += 23.0

        # Dynamic columns based on user toggles
        active_cols = [
            ("STT", "stt", 22.0),
            ("Model & Thiết bị (SL)", "model_name", 122.0),
            ("Công suất", "capacity", 66.0),
        ]
        if app_cfg.get("col_dim", True):
            active_cols.append(("KT Máy & Nặng", "dim_weight", 72.0))
        if app_cfg.get("col_pipe", True):
            active_cols.append(("Ống Đồng & Xả", "pipe_drain", 72.0))
        if app_cfg.get("col_duct", True):
            active_cols.append(("KT Côn Cấp/Hồi & Hộp Gió", "duct_plenum", 112.0))
        if app_cfg.get("col_air", True):
            active_cols.append(("Gió / Ồn / Điện", "air_power", 73.0))

        raw_sum = sum(c[2] for c in active_cols)
        ac_widths = [c[2] * (TW / raw_sum) for c in active_cols]
        ac_x = [ML]
        for w_i in ac_widths:
            ac_x.append(ac_x[-1] + w_i)

        def draw_app_header():
            nonlocal y
            rh = 20.0
            page.draw_rect(pymupdf.Rect(ML, y, W - MR, y + rh), color=C_BLUE_HEAD, fill=C_BLUE_HEAD, width=0.5)
            for ci, (cname, _, _) in enumerate(active_cols):
                if ci > 0:
                    page.draw_line((ac_x[ci], y), (ac_x[ci], y + rh), color=C_WHITE, width=0.4)
                tw_c = f_bold.text_length(cname, fontsize=7.2)
                page.insert_text((ac_x[ci] + max(2, (ac_widths[ci] - tw_c) / 2), y + 13.0), cname, fontname="F_B", fontsize=7.2, color=C_WHITE)
            y += rh

        draw_app_header()

        for idx_a, ar in enumerate(app_rows):
            img_rel = ar.get("image", "")
            img_full = os.path.join(web_dir, img_rel.replace("/", os.sep)) if (show_images and img_rel) else ""
            has_app_img = bool(img_full and os.path.exists(img_full))

            cell_lines = {}
            max_l = 1
            for ci, (_, key, _) in enumerate(active_cols):
                cw = ac_widths[ci] - 6
                if key == "stt":
                    cell_lines[key] = [str(idx_a + 1)]
                elif key == "model_name":
                    mw = cw - (28.0 if has_app_img else 0.0)
                    lns = wrap_lines(f_bold, f"{ar.get('model','')} (x{ar.get('qty',1)})", 7.3, mw) + wrap_lines(f_reg, ar.get("name", ""), 6.9, mw)
                    cell_lines[key] = lns
                else:
                    cell_lines[key] = wrap_lines(f_reg, str(ar.get(key, "")), 7.1, cw)
                max_l = max(max_l, len(cell_lines[key]))

            rh = max(28.0 if has_app_img else 18.0, 6.0 + max_l * 9.0)
            if y + rh > BOTTOM_LIMIT:
                page, y = new_a4_page(is_first=False)
                draw_app_header()

            page.draw_rect(pymupdf.Rect(ML, y, W - MR, y + rh), color=C_BORDER, fill=C_WHITE, width=0.45)
            for ci, (_, key, _) in enumerate(active_cols):
                if key == "duct_plenum":
                    page.draw_rect(pymupdf.Rect(ac_x[ci], y, ac_x[ci + 1], y + rh), color=C_BORDER, fill=C_ICE_SOFT, width=0.45)
                elif ci > 0:
                    page.draw_line((ac_x[ci], y), (ac_x[ci], y + rh), color=C_BORDER, width=0.4)

                lns = cell_lines[key]
                ty = y + 9.6
                tx_off = 3.0
                if key == "model_name" and has_app_img:
                    ib = pymupdf.Rect(ac_x[ci] + 2.5, y + (rh - 22) / 2, ac_x[ci] + 27.5, y + (rh + 22) / 2)
                    page.draw_rect(ib, color=C_BORDER, fill=C_WHITE, width=0.35, radius=0.06)
                    page.insert_image(pymupdf.Rect(ib.x0 + 1, ib.y0 + 1, ib.x1 - 1, ib.y1 - 1), filename=img_full)
                    tx_off = 30.0

                for li, ln in enumerate(lns):
                    if key == "stt":
                        tw_s = f_bold.text_length(ln, fontsize=7.4)
                        page.insert_text((ac_x[ci] + (ac_widths[ci] - tw_s) / 2, y + rh / 2 + 2.5), ln, fontname="F_B", fontsize=7.4, color=C_SLATE)
                    elif key == "model_name" and li == 0:
                        page.insert_text((ac_x[ci] + tx_off, ty), ln, fontname="F_B", fontsize=7.3, color=C_BLUE_HEAD)
                        ty += 9.0
                    elif key == "capacity":
                        page.insert_text((ac_x[ci] + 3, ty), ln, fontname="F_B", fontsize=7.0, color=C_RED)
                        ty += 8.9
                    elif key == "duct_plenum":
                        page.insert_text((ac_x[ci] + 3, ty), ln, fontname="F_B", fontsize=7.0, color=C_SLATE)
                        ty += 8.9
                    else:
                        page.insert_text((ac_x[ci] + tx_off, ty), ln, fontname="F_R", fontsize=7.0, color=C_SLATE)
                        ty += 8.9
            y += rh
        y += 14.0

    # TERMS + CLEAN WHITE VIETQR CARD (WITH RED TITLE STRIP & PURE WHITE TEXT) + SIGNATURES
    ensure_space(210.0, repeat_tbl_header=False)

    page.insert_text((ML, y + 10), "ĐIỀU KHOẢN THƯƠNG MẠI & BẢO HÀNH:", fontname="F_B", fontsize=8.6, color=C_RED)
    terms_text = "\n".join(comp.get("quote_terms", []))
    page.insert_textbox(
        pymupdf.Rect(ML, y + 16, 336, y + 128),
        terms_text,
        fontname="F_R",
        fontsize=7.6,
        color=(0.15, 0.20, 0.28),
        lineheight=1.34,
    )

    # Pure White VietQR Card with Sleek Minh Phú Red Top Title Strip (100% White Text)
    qr_card = pymupdf.Rect(344, y, W - MR, y + 114)
    page.draw_rect(qr_card, color=C_BORDER, fill=C_WHITE, width=1.0)
    qr_head = pymupdf.Rect(344, y, W - MR, y + 18)
    page.insert_image(qr_head, stream=red_bar_bytes, keep_proportion=False)
    qht = "QUÉT MÃ VIETQR THANH TOÁN"
    tw_q = f_bold.text_length(qht, fontsize=7.8)
    page.insert_text((344 + (qr_head.width - tw_q) / 2, y + 12.2), qht, fontname="F_B", fontsize=7.8, color=C_WHITE)

    qr_white = pymupdf.Rect(351, y + 23, 437, y + 109)
    page.draw_rect(qr_white, color=C_BORDER, fill=C_WHITE, width=0.8)
    page.insert_image(pymupdf.Rect(354, y + 26, 434, y + 106), stream=qr_bytes)

    qr_lines = [
        bank.get("bank_name", "Ngân hàng"),
        f"STK: {bank.get('account_no', '')}",
        f"Chủ TK: {bank.get('account_name', '')}",
    ]
    if totals.get("qrAmount", 0) > 0:
        qr_lines.append(f"Tạm ứng ({q.get('qr_percent', 50)}%): {fmt_vn(totals.get('qrAmount', 0))} đ")
    qr_lines.append(f"ND: {q.get('qr_note', '')}")
    page.insert_textbox(
        pymupdf.Rect(443, y + 24, W - MR - 4, y + 110),
        "\n".join(qr_lines),
        fontname="F_B",
        fontsize=7.2,
        color=C_SLATE,
        lineheight=1.34,
    )

    sig_y = y + 138
    page.insert_textbox(
        pymupdf.Rect(ML, sig_y, 245, sig_y + 32),
        "XÁC NHẬN CỦA KHÁCH HÀNG\n(Ký và ghi rõ họ tên)",
        fontname="F_B",
        fontsize=8.3,
        color=C_SLATE,
        align=pymupdf.TEXT_ALIGN_CENTER,
    )
    page.insert_textbox(
        pymupdf.Rect(262, sig_y, W - MR, sig_y + 34),
        f"ĐẠI DIỆN {comp.get('name', 'CÔNG TY MINH PHÚ')}\n(Ký tên, đóng dấu)",
        fontname="F_B",
        fontsize=7.8,
        color=C_RED,
        align=pymupdf.TEXT_ALIGN_CENTER,
    )
    page.insert_textbox(
        pymupdf.Rect(262, sig_y + 56, W - MR, sig_y + 76),
        comp.get("representative", ""),
        fontname="F_B",
        fontsize=8.8,
        color=C_SLATE,
        align=pymupdf.TEXT_ALIGN_CENTER,
    )

    # Clean Slate/Blue Footers on all pages (ZERO Yellow!)
    total_pages = len(doc)
    for i, pg in enumerate(doc):
        pg.draw_line((ML, H - 24), (W - MR, H - 24), color=C_BORDER, width=0.7)
        pg.insert_text(
            (ML, H - 13),
            f"{comp.get('name', 'MINH PHÚ')} — Hotline: {comp.get('hotline', '0967 986 586')} — Đại lý & Nhà thầu ĐHKK Daikin",
            fontname="F_R",
            fontsize=7.4,
            color=C_MUTED,
        )
        pg.insert_text(
            (W - MR - 60, H - 13),
            f"Trang {i + 1} / {total_pages}",
            fontname="F_B",
            fontsize=7.5,
            color=C_BLUE_HEAD,
        )

    try:
        doc.subset_fonts()
    except Exception:
        pass
    final_bytes = doc.tobytes(garbage=4, deflate=True)
    doc.close()
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(final_bytes)
    return final_bytes
