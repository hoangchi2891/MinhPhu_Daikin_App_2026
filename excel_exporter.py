# -*- coding: utf-8 -*-
"""
excel_exporter.py — Pure-Python OpenXML (.xlsx) Generator for Minh Phú Quotations
Generates styled A4-ready .xlsx with live Excel formulas (=E*F, =SUM), borders,
Minh Phú Crimson/Slate branding, and embedded Logo + Payment QR PNG images.
"""

import io
import os
import zipfile
import urllib.request
from xml.sax.saxutils import escape
from PIL import Image, ImageDraw


def make_qr_png_bytes(qr_url: str, bank_info: dict, quote_code: str, amount: int) -> bytes:
    """Try fetching VietQR PNG if online; otherwise render a clean high-res payment QR card PNG."""
    if qr_url and qr_url.startswith("data:image/"):
        import base64
        head, b64 = qr_url.split(",", 1)
        raw = base64.b64decode(b64)
        im = Image.open(io.BytesIO(raw)).convert("RGBA")
        out = io.BytesIO()
        im.save(out, format="PNG")
        return out.getvalue()

    if qr_url and qr_url.startswith("http"):
        try:
            req = urllib.request.Request(qr_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                data = resp.read()
                im = Image.open(io.BytesIO(data)).convert("RGBA")
                out = io.BytesIO()
                im.save(out, format="PNG")
                return out.getvalue()
        except Exception:
            pass

    # Clean offline QR visual badge
    im = Image.new("RGBA", (260, 260), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([6, 6, 253, 253], outline=(185, 28, 28, 255), width=4)
    for ox, oy in [(20, 20), (176, 20), (20, 176)]:
        d.rectangle([ox, oy, ox + 64, oy + 64], outline=(15, 23, 42, 255), width=8)
        d.rectangle([ox + 18, oy + 18, ox + 46, oy + 46], fill=(185, 28, 28, 255) if ox == 20 and oy == 20 else (15, 23, 42, 255))
    # Deterministic matrix modules from account + quote_code
    seed_str = f"{bank_info.get('bank_id','MB')}|{bank_info.get('account_no','')}|{amount}|{quote_code}"
    hval = 2166136261
    for ch in seed_str:
        hval = ((hval ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    for gx in range(9):
        for gy in range(9):
            if (gx < 3 and gy < 3) or (gx > 5 and gy < 3) or (gx < 3 and gy > 5):
                continue
            bit = ((hval >> ((gx * 9 + gy) % 31)) ^ (gx * 7 + gy * 13)) & 1
            if bit:
                x0 = 24 + gx * 23
                y0 = 24 + gy * 23
                d.rectangle([x0, y0, x0 + 16, y0 + 16], fill=(15, 23, 42, 255))
    out = io.BytesIO()
    im.save(out, format="PNG")
    return out.getvalue()


def col_letter(idx_1based: int) -> str:
    s = ""
    n = idx_1based
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def generate_quote_xlsx(payload: dict, logo_path: str, out_path: str = None) -> bytes:
    comp = payload.get("company", {})
    bank = comp.get("bank", {})
    q = payload.get("quote", {})
    totals = payload.get("totals", {})
    equip_rows = payload.get("equip_rows", [])
    install_rows = payload.get("install_rows", [])

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

    # Style IDs defined in styles.xml:
    # 0: Default
    # 1: Company Name Banner (Dark Crimson/Slate, White Bold 13pt)
    # 2: Company Meta (Slate 800, White 10pt)
    # 3: Quote Title (Crimson Bold 14pt, Center)
    # 4: Client Meta Box (Soft Rose/Ice fill, Left, Wrap)
    # 5: Table Header (Dark Slate #0F172A, White Bold, Center, Border)
    # 6: Section Part A/B Header (Crimson #991B1B, White Bold, Border)
    # 7: Section Part A/B Number (Crimson #991B1B, White Bold, Right #,##0)
    # 8: Subgroup Header (Slate 100 #F1F5F9, Bold, Border)
    # 9: Cell Center Text + Border
    # 10: Cell Left Wrap Text + Border
    # 11: Cell Number #,##0 + Border
    # 12: Cell Bold Number #,##0 + Border
    # 13: Summary Label (Bold Right + Border)
    # 14: Summary Value (Bold #,##0 + Border)
    # 15: Grand Total Row (Crimson #991B1B, White Bold 12pt #,##0 + Border)
    # 16: Amount in Words (Italic Crimson on Soft Rose)
    # 17: Terms / Footer Text

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

    # Header Banner Rows 1-3 (Col A reserved for Logo, Col B-G for Company Info)
    add_row(1, [
        make_cell(1, 1, "", 1),
        make_cell(1, 2, comp.get("name", "CÔNG TY TNHH PHÁT TRIỂN KỸ THUẬT THƯƠNG MẠI MINH PHÚ"), 1),
        *[make_cell(1, c, "", 1) for c in range(3, 8)]
    ], height=26)
    merges.append("B1:G1")

    add_row(2, [
        make_cell(2, 1, "", 18),
        make_cell(2, 2, f'Địa chỉ: {comp.get("address", "")}', 18),
        *[make_cell(2, c, "", 18) for c in range(3, 8)]
    ], height=20)
    merges.append("B2:G2")

    add_row(3, [
        make_cell(3, 1, "", 2),
        make_cell(3, 2, f'Hotline: {comp.get("hotline", "0967 986 586")}  |  MST: {comp.get("tax_code", "0107709790")}  |  Website: {comp.get("website", "")}', 2),
        *[make_cell(3, c, "", 2) for c in range(3, 8)]
    ], height=21)
    merges.append("B3:G3")
    merges.append("A1:A3")

    # Row 5: Document Title
    mode = q.get("mode", "BOTH")
    doc_title = (
        "BẢNG BÁO GIÁ CUNG CẤP THIẾT BỊ ĐIỀU HÒA KHÔNG KHÍ DAIKIN" if mode == "EQUIP_ONLY"
        else ("BẢNG BÁO GIÁ VẬT TƯ & NHÂN CÔNG LẮP ĐẶT HỆ THỐNG ĐHKK" if mode == "INSTALL_ONLY"
              else "BẢNG BÁO GIÁ CUNG CẤP THIẾT BỊ & THI CÔNG LẮP ĐẶT HỆ THỐNG ĐHKK")
    )
    add_row(5, [make_cell(5, 1, doc_title, 3)] + [make_cell(5, c, "", 3) for c in range(2, 8)], height=28)
    merges.append("A5:G5")

    # Rows 6-8: Client & Project Info
    add_row(6, [
        make_cell(6, 1, f'Kính gửi: {q.get("client_name", "Quý Khách Hàng")}', 4),
        *[make_cell(6, c, "", 4) for c in range(2, 5)],
        make_cell(6, 5, f'Số báo giá: {q.get("code", "")}', 4),
        make_cell(6, 6, "", 4), make_cell(6, 7, "", 4)
    ], height=21)
    merges.append("A6:D6")
    merges.append("E6:G6")

    add_row(7, [
        make_cell(7, 1, f'Công trình / Dự án: {q.get("project_name", "")}', 4),
        *[make_cell(7, c, "", 4) for c in range(2, 5)],
        make_cell(7, 5, f'Ngày lập: {q.get("date_str", "")}', 4),
        make_cell(7, 6, "", 4), make_cell(7, 7, "", 4)
    ], height=21)
    merges.append("A7:D7")
    merges.append("E7:G7")

    add_row(8, [
        make_cell(8, 1, f'Địa điểm: {q.get("project_addr", "")}   |   SĐT KH: {q.get("client_phone", "—")}', 4),
        *[make_cell(8, c, "", 4) for c in range(2, 5)],
        make_cell(8, 5, f'Phụ trách: {q.get("author", "")}', 4),
        make_cell(8, 6, "", 4), make_cell(8, 7, "", 4)
    ], height=21)
    merges.append("A8:D8")
    merges.append("E8:G8")

    # Row 10: Table Headers
    headers = ["STT", "NỘI DUNG THIẾT BỊ & QUY CÁCH KỸ THUẬT", "HÃNG / XUẤT XỨ", "ĐVT", "SỐ LƯỢNG", "ĐƠN GIÁ (VNĐ)", "THÀNH TIỀN (VNĐ)"]
    add_row(10, [make_cell(10, idx + 1, h, 5) for idx, h in enumerate(headers)], height=28)

    cur_r = 11
    part_sum_refs = []

    # PART A: EQUIPMENT
    if equip_rows:
        part_a_row = cur_r
        cur_r += 1
        first_eq_r = cur_r
        for item in equip_rows:
            desc = f"{item['name']}\nModel: {item['model']}"
            if item.get("spec_note"):
                desc += f"\n({item['spec_note']})"
            line_cnt = desc.count("\n") + 1
            add_row(cur_r, [
                make_cell(cur_r, 1, item["stt"], 9, is_num=True),
                make_cell(cur_r, 2, desc, 10),
                make_cell(cur_r, 3, item["origin"], 9),
                make_cell(cur_r, 4, item["unit"], 9),
                make_cell(cur_r, 5, item["qty"], 11, is_num=True),
                make_cell(cur_r, 6, item["unit_price"], 11, is_num=True),
                make_cell(cur_r, 7, item["line_total"], 12, formula=f"E{cur_r}*F{cur_r}")
            ], height=max(26, line_cnt * 16 + 6))
            cur_r += 1
        last_eq_r = cur_r - 1
        # Insert Part A header row with live SUM formula
        rows_xml.insert(len(rows_xml) - len(equip_rows), f'<row r="{part_a_row}" ht="25" customHeight="1">' + "".join([
            make_cell(part_a_row, 1, "A", 6),
            make_cell(part_a_row, 2, "PHẦN CUNG CẤP THIẾT BỊ ĐIỀU HÒA KHÔNG KHÍ CHÍNH HÃNG DAIKIN", 6),
            make_cell(part_a_row, 3, "", 6),
            make_cell(part_a_row, 4, "", 6),
            make_cell(part_a_row, 5, "", 6),
            make_cell(part_a_row, 6, "", 6),
            make_cell(part_a_row, 7, totals.get("sumEquip", 0), 7, formula=f"SUM(G{first_eq_r}:G{last_eq_r})")
        ]) + '</row>')
        merges.append(f"B{part_a_row}:F{part_a_row}")
        part_sum_refs.append(f"G{part_a_row}")

    # PART B: INSTALLATION & MATERIALS
    if install_rows:
        part_b_row = cur_r
        part_letter = "B" if equip_rows else "A"
        cur_r += 1
        item_row_refs = []
        last_grp = None
        sub_stt = 1
        temp_b_rows = []
        for item in install_rows:
            if item["group_name"] != last_grp:
                last_grp = item["group_name"]
                sub_stt = 1
                temp_b_rows.append((cur_r, [
                    make_cell(cur_r, 1, item["group_code"], 8),
                    make_cell(cur_r, 2, item["group_name"], 8),
                    *[make_cell(cur_r, c, "", 8) for c in range(3, 8)]
                ], 23, f"B{cur_r}:G{cur_r}"))
                cur_r += 1
            item_row_refs.append(f"G{cur_r}")
            temp_b_rows.append((cur_r, [
                make_cell(cur_r, 1, sub_stt, 9, is_num=True),
                make_cell(cur_r, 2, item["name"], 10),
                make_cell(cur_r, 3, item["brand"], 9),
                make_cell(cur_r, 4, item["unit"], 9),
                make_cell(cur_r, 5, item["qty"], 11, is_num=True),
                make_cell(cur_r, 6, item["unit_price"], 11, is_num=True),
                make_cell(cur_r, 7, item["line_total"], 12, formula=f"E{cur_r}*F{cur_r}")
            ], 22, None))
            sub_stt += 1
            cur_r += 1

        sum_b_formula = "+".join(item_row_refs) if len(item_row_refs) <= 40 else f"SUM(G{part_b_row+1}:G{cur_r-1})"
        add_row(part_b_row, [
            make_cell(part_b_row, 1, part_letter, 6),
            make_cell(part_b_row, 2, "PHẦN VẬT TƯ PHỤ & NHÂN CÔNG LẮP ĐẶT HỆ THỐNG", 6),
            *[make_cell(part_b_row, c, "", 6) for c in range(3, 7)],
            make_cell(part_b_row, 7, totals.get("sumInstall", 0), 7, formula=sum_b_formula)
        ], height=25)
        merges.append(f"B{part_b_row}:F{part_b_row}")
        part_sum_refs.append(f"G{part_b_row}")

        for r_idx, c_list, ht, mg in temp_b_rows:
            add_row(r_idx, c_list, height=ht)
            if mg:
                merges.append(mg)

    # TOTALS SECTION
    sub_r = cur_r
    vat_r = cur_r + 1
    grand_r = cur_r + 2
    words_r = cur_r + 3

    sub_formula = "+".join(part_sum_refs) if part_sum_refs else "0"
    vat_rate = int(q.get("vat_rate", 10))

    add_row(sub_r, [
        *[make_cell(sub_r, c, "", 13) for c in range(1, 6)],
        make_cell(sub_r, 6, "TỔNG CỘNG TRƯỚC THUẾ:", 13),
        make_cell(sub_r, 7, totals.get("subTotal", 0), 14, formula=sub_formula)
    ], height=23)
    merges.append(f"A{sub_r}:F{sub_r}")
    # Put label in A{sub_r} so merged cell shows text!
    rows_xml[-1] = f'<row r="{sub_r}" ht="23" customHeight="1">' + "".join([
        make_cell(sub_r, 1, "TỔNG CỘNG TRƯỚC THUẾ:", 13),
        *[make_cell(sub_r, c, "", 13) for c in range(2, 7)],
        make_cell(sub_r, 7, totals.get("subTotal", 0), 14, formula=sub_formula)
    ]) + "</row>"

    add_row(vat_r, [
        make_cell(vat_r, 1, f"THUẾ GTGT (VAT {vat_rate}%):", 13),
        *[make_cell(vat_r, c, "", 13) for c in range(2, 7)],
        make_cell(vat_r, 7, totals.get("vatAmount", 0), 14, formula=f"ROUND(G{sub_r}*{vat_rate}/100,0)")
    ], height=23)
    merges.append(f"A{vat_r}:F{vat_r}")

    add_row(grand_r, [
        make_cell(grand_r, 1, "TỔNG GIÁ TRỊ THANH TOÁN:", 15),
        *[make_cell(grand_r, c, "", 15) for c in range(2, 7)],
        make_cell(grand_r, 7, totals.get("grandTotal", 0), 15, formula=f"G{sub_r}+G{vat_r}")
    ], height=27)
    merges.append(f"A{grand_r}:F{grand_r}")

    add_row(words_r, [
        make_cell(words_r, 1, f'Bằng chữ: {q.get("amount_in_words", "")}', 16),
        *[make_cell(words_r, c, "", 16) for c in range(2, 8)]
    ], height=24)
    merges.append(f"A{words_r}:G{words_r}")

    # TECHNICAL SPECIFICATION & DUCT APPENDIX IN EXCEL (Red Header Bar with 100% Pure White Text!)
    app_cfg = payload.get("appendix_config", {})
    app_rows = payload.get("appendix_rows", [])
    cur_r = words_r + 2
    if app_cfg.get("enabled") and app_rows:
        add_row(cur_r, [
            make_cell(cur_r, 1, "PHỤ LỤC THÔNG SỐ KỸ THUẬT THIẾT BỊ, ỐNG ĐỒNG & KÍCH THƯỚC CÔN ĐẦU MÁY", 19),
            *[make_cell(cur_r, c, "", 19) for c in range(2, 8)]
        ], height=25)
        merges.append(f"A{cur_r}:G{cur_r}")
        cur_r += 1

        app_headers = [
            "STT",
            "MODEL & TÊN MÁY (SL)",
            "CÔNG SUẤT",
            "KT MÁY & TRỌNG LƯỢNG" if app_cfg.get("col_dim", True) else "GHI CHÚ",
            "ỐNG ĐỒNG & NƯỚC XẢ" if app_cfg.get("col_pipe", True) else "—",
            "LƯU LƯỢNG / ĐỘ ỒN" if app_cfg.get("col_air", True) else "—",
            "KT CÔN ĐẦU MÁY & HỘP GIÓ" if app_cfg.get("col_duct", True) else "—",
        ]
        add_row(cur_r, [make_cell(cur_r, i + 1, h_txt, 5) for i, h_txt in enumerate(app_headers)], height=25)
        cur_r += 1

        for idx_a, ar in enumerate(app_rows):
            add_row(cur_r, [
                make_cell(cur_r, 1, idx_a + 1, 9, is_num=True),
                make_cell(cur_r, 2, f"{ar.get('model','')} (x{ar.get('qty',1)})\n{ar.get('name','')}", 10),
                make_cell(cur_r, 3, ar.get("capacity", ""), 9),
                make_cell(cur_r, 4, ar.get("dim_weight", "") if app_cfg.get("col_dim", True) else "", 9),
                make_cell(cur_r, 5, ar.get("pipe_drain", "") if app_cfg.get("col_pipe", True) else "", 9),
                make_cell(cur_r, 6, ar.get("air_power", "") if app_cfg.get("col_air", True) else "", 9),
                make_cell(cur_r, 7, ar.get("duct_plenum", "") if app_cfg.get("col_duct", True) else "", 10),
            ], height=34)
            cur_r += 1
        cur_r += 1

    # TERMS & PAYMENT QR BLOCK
    qr_anchor_row = cur_r
    add_row(cur_r, [
        make_cell(cur_r, 1, "ĐIỀU KHOẢN THƯƠNG MẠI & BẢO HÀNH:", 8),
        *[make_cell(cur_r, c, "", 8) for c in range(2, 6)],
        make_cell(cur_r, 6, "THÔNG TIN THANH TOÁN & MÃ QR:", 8),
        make_cell(cur_r, 7, "", 8)
    ], height=22)
    merges.append(f"A{cur_r}:E{cur_r}")
    merges.append(f"F{cur_r}:G{cur_r}")
    cur_r += 1

    terms = comp.get("quote_terms", [])
    bank_lines = [
        f"Ngân hàng: {bank.get('bank_name', '')}",
        f"Số tài khoản: {bank.get('account_no', '')}",
        f"Chủ tài khoản: {bank.get('account_name', '')}",
        f"Nội dung CK: {q.get('qr_note', '')}",
        "(Quét mã QR bên dưới để thanh toán nhanh)"
    ]
    max_lines = max(len(terms), len(bank_lines))
    for i in range(max_lines):
        t_txt = terms[i] if i < len(terms) else ""
        b_txt = bank_lines[i] if i < len(bank_lines) else ""
        add_row(cur_r, [
            make_cell(cur_r, 1, t_txt, 17),
            *[make_cell(cur_r, c, "", 17) for c in range(2, 6)],
            make_cell(cur_r, 6, b_txt, 17),
            make_cell(cur_r, 7, "", 17)
        ], height=20)
        merges.append(f"A{cur_r}:E{cur_r}")
        merges.append(f"F{cur_r}:G{cur_r}")
        cur_r += 1

    sig_r = cur_r + 6
    add_row(sig_r, [
        make_cell(sig_r, 1, "XÁC NHẬN CỦA KHÁCH HÀNG", 9),
        make_cell(sig_r, 2, "", 9), make_cell(sig_r, 3, "", 9),
        make_cell(sig_r, 4, "", 0),
        make_cell(sig_r, 5, f"ĐẠI DIỆN {comp.get('name', 'MINH PHÚ')}", 9),
        make_cell(sig_r, 6, "", 9), make_cell(sig_r, 7, "", 9)
    ], height=24)
    merges.append(f"A{sig_r}:C{sig_r}")
    merges.append(f"E{sig_r}:G{sig_r}")

    # Build XML parts
    cols_xml = """<cols>
      <col min="1" max="1" width="9" customWidth="1"/>
      <col min="2" max="2" width="52" customWidth="1"/>
      <col min="3" max="3" width="16" customWidth="1"/>
      <col min="4" max="4" width="9" customWidth="1"/>
      <col min="5" max="5" width="11" customWidth="1"/>
      <col min="6" max="6" width="16" customWidth="1"/>
      <col min="7" max="7" width="18" customWidth="1"/>
    </cols>"""

    merges_xml = f'<mergeCells count="{len(merges)}">' + "".join(f'<mergeCell ref="{m}"/>' for m in merges) + "</mergeCells>"

    sheet_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
           xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheetPr><pageSetUpPr fitToPage="1"/></sheetPr>
  <sheetViews><sheetView tabSelected="1" workbookViewId="0"/></sheetViews>
  {cols_xml}
  <sheetData>{"".join(rows_xml)}</sheetData>
  {merges_xml}
  <pageMargins left="0.4" right="0.4" top="0.5" bottom="0.5" header="0.2" footer="0.2"/>
  <pageSetup paperSize="9" orientation="portrait" fitToWidth="1" fitToHeight="0"/>
  <drawing r:id="rId1"/>
</worksheet>"""

    ss_xml = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="{len(shared_strings)}" uniqueCount="{len(shared_strings)}">'
        + "".join(f'<si><t xml:space="preserve">{escape(s)}</t></si>' for s in shared_strings)
        + "</sst>"
    )

    styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <numFmts count="1">
    <numFmt numFmtId="164" formatCode="#,##0"/>
  </numFmts>
  <fonts count="8">
    <font><sz val="10.5"/><color rgb="FF0F172A"/><name val="Arial"/></font>
    <font><b/><sz val="13"/><color rgb="FF991B1B"/><name val="Arial"/></font>
    <font><sz val="10"/><color rgb="FF334155"/><name val="Arial"/></font>
    <font><b/><sz val="12.5"/><color rgb="FFFFFFFF"/><name val="Arial"/></font>
    <font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Arial"/></font>
    <font><b/><sz val="10.5"/><color rgb="FF0F172A"/><name val="Arial"/></font>
    <font><b/><sz val="11.5"/><color rgb="FFFFFFFF"/><name val="Arial"/></font>
    <font><b/><i/><sz val="10.5"/><color rgb="FF991B1B"/><name val="Arial"/></font>
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
  <cellXfs count="20">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>
    <xf numFmtId="0" fontId="1" fillId="3" borderId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment vertical="center"/></xf>
    <xf numFmtId="0" fontId="2" fillId="3" borderId="2" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center"/></xf>
    <xf numFmtId="0" fontId="3" fillId="2" borderId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
    <xf numFmtId="0" fontId="5" fillId="4" borderId="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="4" fillId="5" borderId="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="5" fillId="6" borderId="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center"/></xf>
    <xf numFmtId="164" fontId="7" fillId="6" borderId="1" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <xf numFmtId="0" fontId="5" fillId="4" borderId="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center"/></xf>
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" applyBorder="1" applyAlignment="1"><alignment horizontal="left" vertical="center" wrapText="1"/></xf>
    <xf numFmtId="164" fontId="0" fillId="0" borderId="1" applyNumberFormat="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <xf numFmtId="164" fontId="5" fillId="0" borderId="1" applyNumberFormat="1" applyFont="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <xf numFmtId="0" fontId="5" fillId="4" borderId="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <xf numFmtId="164" fontId="5" fillId="4" borderId="1" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <xf numFmtId="164" fontId="6" fillId="2" borderId="1" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <xf numFmtId="0" fontId="7" fillId="4" borderId="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="left" vertical="center"/></xf>
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" applyAlignment="1"><alignment horizontal="left" vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="2" fillId="3" borderId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment vertical="center"/></xf>
    <xf numFmtId="0" fontId="6" fillId="2" borderId="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="left" vertical="center"/></xf>
  </cellXfs>
</styleSheet>"""

    # Prepare Logo + QR images
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as lf:
            logo_bytes = lf.read()
    else:
        im_tmp = Image.new("RGBA", (120, 120), (185, 28, 28, 255))
        buf_tmp = io.BytesIO()
        im_tmp.save(buf_tmp, format="PNG")
        logo_bytes = buf_tmp.getvalue()

    qr_bytes = make_qr_png_bytes(
        q.get("qr_url", ""),
        bank,
        q.get("code", "BG-MP"),
        totals.get("qrAmount", 0)
    )

    qr_r0 = qr_anchor_row + max_lines
    drawing_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<xdr:wsDr xmlns:xdr="http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"
          xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <xdr:twoCellAnchor editAs="oneCell">
    <xdr:from><xdr:col>0</xdr:col><xdr:colOff>38100</xdr:colOff><xdr:row>0</xdr:row><xdr:rowOff>28575</xdr:rowOff></xdr:from>
    <xdr:to><xdr:col>1</xdr:col><xdr:colOff>-38100</xdr:colOff><xdr:row>3</xdr:row><xdr:rowOff>-28575</xdr:rowOff></xdr:to>
    <xdr:pic>
      <xdr:nvPicPr><xdr:cNvPr id="2" name="MinhPhuLogo"/><xdr:cNvPicPr/></xdr:nvPicPr>
      <xdr:blipFill><a:blip r:embed="rId1"/><a:stretch><a:fillRect/></a:stretch></xdr:blipFill>
      <xdr:spPr><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></xdr:spPr>
    </xdr:pic>
    <xdr:clientData/>
  </xdr:twoCellAnchor>
  <xdr:twoCellAnchor editAs="oneCell">
    <xdr:from><xdr:col>5</xdr:col><xdr:colOff>150000</xdr:colOff><xdr:row>{qr_r0}</xdr:row><xdr:rowOff>40000</xdr:rowOff></xdr:from>
    <xdr:to><xdr:col>6</xdr:col><xdr:colOff>900000</xdr:colOff><xdr:row>{qr_r0 + 5}</xdr:row><xdr:rowOff>180000</xdr:rowOff></xdr:to>
    <xdr:pic>
      <xdr:nvPicPr><xdr:cNvPr id="3" name="PaymentQR"/><xdr:cNvPicPr/></xdr:nvPicPr>
      <xdr:blipFill><a:blip r:embed="rId2"/><a:stretch><a:fillRect/></a:stretch></xdr:blipFill>
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
  <sheets><sheet name="Bao Gia Minh Phu" sheetId="1" r:id="rId1"/></sheets>
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
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/qr.png"/>
</Relationships>""")
        z.writestr("xl/styles.xml", styles_xml)
        z.writestr("xl/sharedStrings.xml", ss_xml)
        z.writestr("xl/worksheets/sheet1.xml", sheet_xml)
        z.writestr("xl/drawings/drawing1.xml", drawing_xml)
        z.writestr("xl/media/logo.png", logo_bytes)
        z.writestr("xl/media/qr.png", qr_bytes)

    raw_xlsx = out_buf.getvalue()
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as f:
            f.write(raw_xlsx)
    return raw_xlsx
