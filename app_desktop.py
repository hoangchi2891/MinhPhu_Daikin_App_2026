# -*- coding: utf-8 -*-
"""
app_desktop.py — Windows Desktop Application (.exe) & Local Server Host
Powered by PyWebView + Bottle + PyMuPDF + TCVN 5687:2024 HVAC/CAD/AI Suite
For CÔNG TY TNHH PHÁT TRIỂN KỸ THUẬT THƯƠNG MẠI MINH PHÚ
"""

import os
import sys
import json
import base64
import webbrowser
import threading
import pymupdf
import bottle

# Allow up to 32 MB JSON uploads for PDF / AutoCAD DXF / DWG architectural drawings
bottle.BaseRequest.MEMFILE_MAX = 32 * 1024 * 1024

from excel_exporter import generate_quote_xlsx
from pdf_exporter import generate_quote_pdf
import hvac_engine
from hvac_report_exporter import generate_hvac_report_pdf, generate_hvac_report_xlsx


def get_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def get_app_data_dir() -> str:
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        return exe_dir
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()
WEB_DIR = os.path.join(BASE_DIR, "web")
EXPORTS_DIR = os.path.join(get_app_data_dir(), "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

_CACHED_PRODUCTS = None


def load_db_products() -> list:
    global _CACHED_PRODUCTS
    if _CACHED_PRODUCTS is not None:
        return _CACHED_PRODUCTS
    db_path = os.path.join(WEB_DIR, "database.json")
    try:
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                _CACHED_PRODUCTS = data.get("products", [])
                return _CACHED_PRODUCTS
    except Exception:
        pass
    return []


def find_daikin_catalog_dir() -> str:
    """Locate folder containing the 15 Daikin Vietnamese PDF catalogues."""
    candidates = []
    cur = get_app_data_dir()
    for _ in range(5):
        if cur:
            candidates.append(cur)
            cur = os.path.dirname(cur)
    candidates.append(r"H:\DAIKIN")
    for c in candidates:
        if c and os.path.exists(os.path.join(c, "DAIKIN VRV TỔNG HỢP.pdf")):
            return c
    return r"H:\DAIKIN"


def render_pdf_page_to_data_url(file_name: str, page_num: int, dpi: int = 150) -> dict:
    cat_dir = find_daikin_catalog_dir()
    pdf_path = os.path.join(cat_dir, file_name)
    if not os.path.exists(pdf_path):
        return {"ok": False, "error": f"Không tìm thấy file {file_name}"}
    doc = pymupdf.open(pdf_path)
    total = len(doc)
    p = max(1, min(total, int(page_num or 1)))
    pix = doc[p - 1].get_pixmap(dpi=dpi)
    png_bytes = pix.tobytes("png")
    doc.close()
    b64 = base64.b64encode(png_bytes).decode("ascii")
    return {
        "ok": True,
        "page": p,
        "total_pages": total,
        "data_url": f"data:image/png;base64,{b64}",
    }


def handle_parse_drawing(body: dict) -> dict:
    """Parse uploaded PDF, AutoCAD DXF/DWG, or Floor Plan Image (Offline + Optional AI Vision)."""
    filename = str(body.get("filename") or "drawing.pdf")
    file_b64 = str(body.get("file_b64") or "")
    page_no = int(body.get("page") or 1)
    run_ai = bool(body.get("run_ai", False))
    ai_cfg = body.get("ai_config") or {}

    if "," in file_b64 and file_b64.startswith("data:"):
        file_b64 = file_b64.split(",", 1)[1]
    if not file_b64:
        return {"ok": False, "error": "Chưa nhận được dữ liệu file bản vẽ."}

    try:
        raw_bytes = base64.b64decode(file_b64)
    except Exception as e:
        return {"ok": False, "error": f"Dữ liệu base64 không hợp lệ: {e}"}

    ext = os.path.splitext(filename.lower())[1]

    if ext == ".dxf":
        return hvac_engine.parse_dxf_bytes(raw_bytes, filename)

    if ext == ".dwg":
        dxf_bytes, err_msg = hvac_engine.try_convert_dwg_to_dxf(raw_bytes)
        if not dxf_bytes:
            return {"ok": False, "error": err_msg}
        res = hvac_engine.parse_dxf_bytes(dxf_bytes, filename)
        if res.get("ok"):
            res["file_type"] = "DWG->DXF"
        return res

    if ext == ".pdf":
        res = hvac_engine.parse_pdf_drawing_offline(raw_bytes, page_no, filename)
        if res.get("ok") and run_ai:
            ai_res = hvac_engine.ai_vision_takeoff_drawing(
                res.get("preview_b64", ""),
                ai_cfg,
                mime_type="image/png",
                extra_text=res.get("raw_text_sample", ""),
            )
            if ai_res.get("ok"):
                res["rooms"] = ai_res.get("rooms", [])
                res["ai_used"] = ai_res.get("provider", "").upper()
                res["note"] = f"AI Vision ({res['ai_used']}) đã quét mặt bằng PDF trang {res['page']}/{res['total_pages']} và bóc tách được {len(res['rooms'])} phòng!"
            else:
                res["ai_error"] = ai_res.get("error", "")
        res.pop("preview_b64", None)
        return res

    if ext in (".png", ".jpg", ".jpeg", ".webp"):
        mime = "image/jpeg" if ext in (".jpg", ".jpeg") else ("image/webp" if ext == ".webp" else "image/png")
        res = {
            "ok": True,
            "file_type": "IMAGE",
            "filename": filename,
            "page": 1,
            "total_pages": 1,
            "preview_data_url": f"data:{mime};base64,{file_b64}",
            "rooms": [],
            "note": "Đã tải ảnh bản vẽ mặt bằng. Bấm '🤖 AI Vision Quét Mặt Bằng' (khi đã cấu hình Gemini/OpenAI API Key) để AI tự nhận diện các phòng & diện tích.",
        }
        if run_ai:
            ai_res = hvac_engine.ai_vision_takeoff_drawing(file_b64, ai_cfg, mime_type=mime)
            if ai_res.get("ok"):
                res["rooms"] = ai_res.get("rooms", [])
                res["ai_used"] = ai_res.get("provider", "").upper()
                res["note"] = f"AI Vision ({res['ai_used']}) đã phân tích ảnh mặt bằng và bóc tách được {len(res['rooms'])} phòng!"
            else:
                res["ai_error"] = ai_res.get("error", "")
        return res

    return {"ok": False, "error": f"Định dạng file '{ext}' chưa hỗ trợ. Vui lòng chọn .PDF, .DXF, .DWG, .PNG hoặc .JPG."}


class DesktopBridgeAPI:
    def __init__(self):
        self._window = None

    def open_url(self, url: str):
        webbrowser.open(url)
        return {"ok": True}

    def render_pdf_page(self, file_name: str, page_num: int):
        try:
            return render_pdf_page_to_data_url(file_name, page_num)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def open_local_pdf(self, file_name: str, page_num: int = 1):
        cat_dir = find_daikin_catalog_dir()
        pdf_path = os.path.join(cat_dir, file_name)
        if os.path.exists(pdf_path):
            os.startfile(pdf_path)
            return {"ok": True}
        return {"ok": False}

    def save_user_state(self, state_json: str):
        try:
            state_path = os.path.join(get_app_data_dir(), "user_settings_backup.json")
            with open(state_path, "w", encoding="utf-8") as f:
                f.write(state_json)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def load_user_state(self):
        try:
            state_path = os.path.join(get_app_data_dir(), "user_settings_backup.json")
            if os.path.exists(state_path):
                with open(state_path, "r", encoding="utf-8") as f:
                    return {"ok": True, "data": json.load(f)}
            return {"ok": True, "data": None}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _ask_save_path(self, default_name: str, file_types: tuple):
        import webview
        save_mode = getattr(getattr(webview, "FileDialog", None), "SAVE", getattr(webview, "SAVE_DIALOG", 10))
        if self._window:
            res = self._window.create_file_dialog(
                save_mode,
                directory=EXPORTS_DIR,
                save_filename=default_name,
                file_types=file_types,
            )
            if not res:
                return None
            return res[0] if isinstance(res, (list, tuple)) else res
        return os.path.join(EXPORTS_DIR, default_name)

    def export_excel(self, payload_json: str):
        payload = json.loads(payload_json)
        code = payload.get("quote", {}).get("code", "BG-MP").replace("/", "-")
        save_path = self._ask_save_path(f"Bao_Gia_Minh_Phu_{code}.xlsx", ("Excel Workbook (*.xlsx)", "All files (*.*)"))
        if not save_path:
            return {"ok": False, "cancelled": True}
        logo_path = os.path.join(WEB_DIR, "assets", "logo_minh_phu.png")
        generate_quote_xlsx(payload, logo_path=logo_path, out_path=save_path)
        try:
            os.startfile(save_path)
        except Exception:
            pass
        return {"ok": True, "path": save_path}

    def export_pdf(self, payload_json: str):
        payload = json.loads(payload_json)
        code = payload.get("quote", {}).get("code", "BG-MP").replace("/", "-")
        save_path = self._ask_save_path(f"Bao_Gia_Minh_Phu_{code}.pdf", ("PDF Document (*.pdf)", "All files (*.*)"))
        if not save_path:
            return {"ok": False, "cancelled": True}
        generate_quote_pdf(payload, web_dir=WEB_DIR, out_path=save_path)
        try:
            os.startfile(save_path)
        except Exception:
            pass
        return {"ok": True, "path": save_path}

    def export_hvac_report_pdf(self, payload_json: str):
        payload = json.loads(payload_json)
        code = (payload.get("meta", {}).get("report_code") or "BC-HVAC").replace("/", "-")
        save_path = self._ask_save_path(f"Bao_Cao_Nhiet_Gio_Minh_Phu_{code}.pdf", ("PDF Document (*.pdf)", "All files (*.*)"))
        if not save_path:
            return {"ok": False, "cancelled": True}
        generate_hvac_report_pdf(payload, web_dir=WEB_DIR, out_path=save_path)
        try:
            os.startfile(save_path)
        except Exception:
            pass
        return {"ok": True, "path": save_path}

    def export_hvac_report_xlsx(self, payload_json: str):
        payload = json.loads(payload_json)
        code = (payload.get("meta", {}).get("report_code") or "BC-HVAC").replace("/", "-")
        save_path = self._ask_save_path(f"Bang_Tinh_Nhiet_Gio_Minh_Phu_{code}.xlsx", ("Excel Workbook (*.xlsx)", "All files (*.*)"))
        if not save_path:
            return {"ok": False, "cancelled": True}
        logo_path = os.path.join(WEB_DIR, "assets", "logo_minh_phu.png")
        generate_hvac_report_xlsx(payload, logo_path=logo_path, out_path=save_path)
        try:
            os.startfile(save_path)
        except Exception:
            pass
        return {"ok": True, "path": save_path}


# Local Bottle HTTP App (used both inside PyWebView & for local browser demo)
http_app = bottle.Bottle()


_STATIC_MIME_MAP = {
    ".html": "text/html; charset=utf-8",
    ".htm": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml; charset=utf-8",
    ".ttf": "font/ttf",
    ".otf": "font/otf",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".webmanifest": "application/manifest+json; charset=utf-8",
}


def _serve_web_file(filepath: str):
    ext = os.path.splitext(filepath.lower())[1]
    mimetype = _STATIC_MIME_MAP.get(ext, "auto")
    resp = bottle.static_file(filepath, root=WEB_DIR, mimetype=mimetype)
    resp.set_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
    resp.set_header("Pragma", "no-cache")
    return resp


@http_app.route("/")
def serve_index():
    return _serve_web_file("index.html")


@http_app.route("/api/pdf_page")
def api_pdf_page():
    fn = bottle.request.query.get("file", "")
    pg = int(bottle.request.query.get("page", "1") or 1)
    bottle.response.content_type = "application/json; charset=utf-8"
    return json.dumps(render_pdf_page_to_data_url(fn, pg), ensure_ascii=False)


@http_app.post("/api/export_excel")
def api_export_excel():
    payload = bottle.request.json
    logo_path = os.path.join(WEB_DIR, "assets", "logo_minh_phu.png")
    code = payload.get("quote", {}).get("code", "BG-MP").replace("/", "-")
    out_file = os.path.join(EXPORTS_DIR, f"Bao_Gia_Minh_Phu_{code}.xlsx")
    raw = generate_quote_xlsx(payload, logo_path=logo_path, out_path=out_file)
    bottle.response.content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    bottle.response.headers["Content-Disposition"] = f'attachment; filename="Bao_Gia_Minh_Phu_{code}.xlsx"'
    return raw


@http_app.post("/api/export_pdf")
def api_export_pdf():
    payload = bottle.request.json
    code = payload.get("quote", {}).get("code", "BG-MP").replace("/", "-")
    out_file = os.path.join(EXPORTS_DIR, f"Bao_Gia_Minh_Phu_{code}.pdf")
    raw = generate_quote_pdf(payload, web_dir=WEB_DIR, out_path=out_file)
    bottle.response.content_type = "application/pdf"
    bottle.response.headers["Content-Disposition"] = f'attachment; filename="Bao_Gia_Minh_Phu_{code}.pdf"'
    return raw


@http_app.get("/api/user_state")
def api_get_user_state():
    bottle.response.content_type = "application/json; charset=utf-8"
    state_path = os.path.join(get_app_data_dir(), "user_settings_backup.json")
    if os.path.exists(state_path):
        with open(state_path, "r", encoding="utf-8") as f:
            return json.dumps({"ok": True, "data": json.load(f)}, ensure_ascii=False)
    return json.dumps({"ok": True, "data": None})


@http_app.post("/api/user_state")
def api_save_user_state():
    bottle.response.content_type = "application/json; charset=utf-8"
    payload = bottle.request.json
    state_path = os.path.join(get_app_data_dir(), "user_settings_backup.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return json.dumps({"ok": True})


# ==============================================================================
# NEW HVAC ENGINEERING, CAD/PDF TAKEOFF, DUCT CHECKER, COOLPACK & AI API ROUTES
# ==============================================================================
@http_app.get("/api/hvac/meta")
def api_hvac_meta():
    bottle.response.content_type = "application/json; charset=utf-8"
    return json.dumps({"ok": True, "data": hvac_engine.get_reference_catalog_metadata()}, ensure_ascii=False)


@http_app.post("/api/hvac/calc_project")
def api_hvac_calc_project():
    bottle.response.content_type = "application/json; charset=utf-8"
    body = bottle.request.json or {}
    res = hvac_engine.calculate_project_heat_load(body, load_db_products())
    return json.dumps(res, ensure_ascii=False)


@http_app.post("/api/hvac/parse_drawing")
def api_hvac_parse_drawing():
    bottle.response.content_type = "application/json; charset=utf-8"
    body = bottle.request.json or {}
    res = handle_parse_drawing(body)
    return json.dumps(res, ensure_ascii=False)


@http_app.post("/api/hvac/ai_analyze")
def api_hvac_ai_analyze():
    bottle.response.content_type = "application/json; charset=utf-8"
    body = bottle.request.json or {}
    res = hvac_engine.run_ai_thermal_report(
        body.get("calc_result") or {},
        body.get("ai_config") or {},
        body.get("duct_result"),
    )
    return json.dumps(res, ensure_ascii=False)


@http_app.post("/api/hvac/ai_test")
def api_hvac_ai_test():
    bottle.response.content_type = "application/json; charset=utf-8"
    body = bottle.request.json or {}
    res = hvac_engine.ai_test_connection(body)
    return json.dumps(res, ensure_ascii=False)


@http_app.post("/api/hvac/ai_list_models")
def api_hvac_ai_list_models():
    bottle.response.content_type = "application/json; charset=utf-8"
    body = bottle.request.json or {}
    res = hvac_engine.ai_list_models(body)
    return json.dumps(res, ensure_ascii=False)


@http_app.post("/api/hvac/ai_generate_rooms")
def api_hvac_ai_generate_rooms():
    bottle.response.content_type = "application/json; charset=utf-8"
    body = bottle.request.json or {}
    res = hvac_engine.ai_generate_rooms(
        body.get("description", ""),
        body.get("building_category", "AUTO"),
        body.get("ai_config") or {},
    )
    return json.dumps(res, ensure_ascii=False)


@http_app.post("/api/hvac/duct_check")
def api_hvac_duct_check():
    bottle.response.content_type = "application/json; charset=utf-8"
    body = bottle.request.json or {}
    res = hvac_engine.calc_duct_checker(body, load_db_products())
    return json.dumps(res, ensure_ascii=False)


@http_app.post("/api/hvac/coolpack_check")
def api_hvac_coolpack_check():
    bottle.response.content_type = "application/json; charset=utf-8"
    body = bottle.request.json or {}
    res = hvac_engine.calc_coolpack_cycle(body)
    return json.dumps(res, ensure_ascii=False)


@http_app.post("/api/hvac/export_report_pdf")
def api_hvac_export_report_pdf():
    payload = bottle.request.json or {}
    code = (payload.get("meta", {}).get("report_code") or "BC-HVAC").replace("/", "-")
    out_file = os.path.join(EXPORTS_DIR, f"Bao_Cao_Nhiet_Gio_Minh_Phu_{code}.pdf")
    raw = generate_hvac_report_pdf(payload, web_dir=WEB_DIR, out_path=out_file)
    bottle.response.content_type = "application/pdf"
    bottle.response.headers["Content-Disposition"] = f'attachment; filename="Bao_Cao_Nhiet_Gio_Minh_Phu_{code}.pdf"'
    return raw


@http_app.post("/api/hvac/export_report_xlsx")
def api_hvac_export_report_xlsx():
    payload = bottle.request.json or {}
    logo_path = os.path.join(WEB_DIR, "assets", "logo_minh_phu.png")
    code = (payload.get("meta", {}).get("report_code") or "BC-HVAC").replace("/", "-")
    out_file = os.path.join(EXPORTS_DIR, f"Bang_Tinh_Nhiet_Gio_Minh_Phu_{code}.xlsx")
    raw = generate_hvac_report_xlsx(payload, logo_path=logo_path, out_path=out_file)
    bottle.response.content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    bottle.response.headers["Content-Disposition"] = f'attachment; filename="Bang_Tinh_Nhiet_Gio_Minh_Phu_{code}.xlsx"'
    return raw


@http_app.route("/<filepath:path>")
def serve_static(filepath):
    return _serve_web_file(filepath)


def run_desktop_gui():
    import webview
    bridge = DesktopBridgeAPI()
    window = webview.create_window(
        title="Minh Phú HVAC — Tính Nhiệt TCVN 5687, Ống Gió AI & Báo Giá Daikin",
        url=http_app,
        js_api=bridge,
        width=1420,
        height=900,
        min_size=(1024, 680),
    )
    bridge._window = window
    webview.start(debug=False)


if __name__ == "__main__":
    if "--server" in sys.argv:
        port = 8765
        print(f"Minh Phu Daikin Demo Server running at http://127.0.0.1:{port}")
        bottle.run(http_app, host="127.0.0.1", port=port, quiet=False)
    else:
        run_desktop_gui()
