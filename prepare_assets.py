import os
import shutil
import json
from PIL import Image
import numpy as np
from collections import deque

APP_DIR = r"H:\DAIKIN\MinhPhu_Daikin_App"
WEB_ASSETS = os.path.join(APP_DIR, "web", "assets")
PROD_IMG_DIR = os.path.join(WEB_ASSETS, "products")
COMMERCIAL_IMG_DIR = os.path.join(WEB_ASSETS, "commercial")
SCRATCH_CROPS = r"C:\Users\Admin\.gemini\antigravity\brain\d9ae5685-5ee9-4db3-bc2c-8de3e0bef518\scratch\pdf_product_crops"

os.makedirs(PROD_IMG_DIR, exist_ok=True)
os.makedirs(COMMERCIAL_IMG_DIR, exist_ok=True)
os.makedirs(os.path.join(APP_DIR, "web", "js"), exist_ok=True)
os.makedirs(os.path.join(APP_DIR, "web", "css"), exist_ok=True)
os.makedirs(os.path.join(APP_DIR, "exports"), exist_ok=True)

# 1. Process Minh Phu Logo (clean PNG + Windows .ico)
logo_src = r"H:\DAIKIN\logo Minh Phu (1).png"
logo_im = Image.open(logo_src).convert("RGBA")
logo_im.thumbnail((600, 600), Image.Resampling.LANCZOS)
logo_im.save(os.path.join(WEB_ASSETS, "logo_minh_phu.png"))

# Create square icon from the top snowflake circle of Minh Phu logo
lw, lh = logo_im.size
circle_crop = logo_im.crop((int(lw*0.12), 0, int(lw*0.88), int(lh*0.72)))
ico_canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
circle_crop.thumbnail((248, 248), Image.Resampling.LANCZOS)
ico_canvas.paste(circle_crop, ((256 - circle_crop.width)//2, (256 - circle_crop.height)//2), circle_crop)
ico_canvas.save(os.path.join(WEB_ASSETS, "app_icon.png"))
ico_canvas.save(os.path.join(WEB_ASSETS, "app_icon.ico"), format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

# Copy CAD reference diagram
cad_src = r"C:\Users\Admin\.gemini\antigravity\brain\d9ae5685-5ee9-4db3-bc2c-8de3e0bef518\scratch\con_dau_diagram.jpeg"
if os.path.exists(cad_src):
    shutil.copy2(cad_src, os.path.join(WEB_ASSETS, "con_dau_cad.jpeg"))

# 2. Extract copper Refnet transparent PNGs from Minh Phu Refnet images
def extract_copper_cutout(src_path, out_name):
    im = Image.open(src_path).convert("RGBA")
    # Center area containing only copper refnet pipes (avoiding logos/text)
    crop = im.crop((145, 195, 765, 535))
    arr = np.array(crop)
    r, g, b = arr[:,:,0].astype(np.int16), arr[:,:,1].astype(np.int16), arr[:,:,2].astype(np.int16)
    # Background is pale cream/yellow (high R, high G, high luminance, low R-G difference)
    # Copper pipe is warm orange-brown/metallic with darker shadow or higher R-B & R-G contrast
    is_bg = (r > 225) & (g > 215) & (b > 165) & ((r - g) < 28)
    arr[is_bg, 3] = 0
    res = Image.fromarray(arr)
    bbox = res.getchannel("A").getbbox()
    if bbox:
        res = res.crop(bbox)
    res.save(os.path.join(PROD_IMG_DIR, out_name))

extract_copper_cutout(
    r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\BỘ CHIA GAS DÀN LẠNH.png",
    "refnet_indoor.png"
)
extract_copper_cutout(
    r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\BỘ CHIA GAS DÀN NÓNG.png",
    "refnet_outdoor.png"
)

# 3. Copy & standardize verified Daikin transparent cutout PNGs from PDF XObjects
asset_map = {
    "vrv_outdoor_single_s.png": "vrvh_p8_x706_155x268.png",      # 8-12 HP
    "vrv_outdoor_single_m.png": "vrvh_p8_x705_183x267.png",      # 14-20 HP
    "vrv_outdoor_single_l.png": "vrvh_p8_x704_242x280.png",      # 22-24 HP
    "vrv_outdoor_multi.png":    "vrvh_p8_x721_207x192.png",      # 26-60 HP multi-module
    "vrvs_outdoor_1fan.png":    "sky_p51_x10714_154x124.png",    # VRV IV-S 4-6HP / SkyAir 1 fan
    "vrvs_outdoor_2fan.png":    "sky_p51_x10730_158x247.png",    # VRV IV-S 8-9HP / SkyAir 2 fan
    "sky_outdoor_compact.png":  "sky_p51_x10736_165x138.png",    # SkyAir compact outdoor
    "multi_outdoor_3_4.png":    "multi_p6_x311_292x239.png",     # 3MXM / 4MXM
    "multi_outdoor_5.png":      "multi_p7_x351_309x348.png",     # 5MXM100
    "cassette_roundflow.png":   "vrvh_p23_x1713_392x244.png",    # FXFQ / FCQ / FCFC
    "cassette_compact.png":     "vrvh_p23_x1694_382x323.png",    # FXZQ / FFFC
    "cassette_multi_2x2.png":   "multi_p21_x1583_991x932.png",   # FFA25-60
    "cassette_2way.png":        "vrvh_p23_x1715_708x322.png",    # FXCQ
    "cassette_1way.png":        "vrvh_p23_x1712_567x315.png",    # FXKQ
    "panel_cassette.png":       "vrvth_p193_x17150_216x108.png", # BYCQ125EAF / BYFQ60
    "duct_slim_pd.png":         "vrvh_p23_x1696_628x310.png",    # FXDQ20-32PDVE
    "duct_slim_nd.png":         "vrvh_p23_x1709_543x315.png",    # FXDQ40-63NDVE
    "duct_slim_compact.png":    "vrvh_p23_x1708_704x328.png",    # FXDQ-SP / FDF
    "duct_med_fxsq.png":        "vrvh_p23_x1707_837x306.png",    # FXSQ / FBFC / FBQ / FMA
    "duct_high_fxmq.png":       "vrvh_p23_x1706_885x305.png",    # FXMQ20-140PAVE
    "duct_large_fxmq200.png":   "vrvh_p23_x1705_780x309.png",    # FXMQ200-250
    "duct_multi_cdxp.png":      "multi_p17_x1244_932x336.png",   # CDXP
    "duct_multi_cdxm.png":      "multi_p17_x1240_909x254.png",   # CDXM
    "wall_fxaq.png":            "vrvh_p23_x1701_717x321.png",    # FXAQ
    "wall_fthf.png":            "multi_p6_x289_389x216.png",     # FTHF Room Air Coanda
    "wall_ctxm.png":            "multi_p6_x303_343x220.png",     # CTXM Multi
    "ceiling_fxhq.png":         "vrvh_p23_x1703_775x310.png",    # FXHQ / FHA
    "floor_fxlq.png":           "vrvh_p23_x1700_525x319.png",    # FXLQ
    "floor_duct_fxnq.png":      "vrvh_p23_x1699_518x324.png",    # FXNQ
    "floor_standing_fva.png":   "sky_p45_x9752_141x420.png",     # FVA
    "hrv_vam.png":              "vrvh_p23_x1714_1378x624.png",   # VAM HRV
    "ctrl_wired_brc1e63.png":   "multi_p17_x1252_499x509.png",   # BRC1E63 / BRC1F61 / BRC073
    "ctrl_wired_simple.png":    "vrvth_p254_x21961_177x181.png", # BRC2E61 / BRC301B61
    "ctrl_madoka.png":          "vrvth_p252_x21768_166x196.png", # BRC1H63W
    "ctrl_wireless.png":        "multi_p17_x1256_254x801.png",   # Wireless remotes
    "ctrl_central_itm.png":     "itm_p3_x184_329x272.png",       # Central controllers DCS / DCM
}

for dest_name, src_name in asset_map.items():
    sp = os.path.join(SCRATCH_CROPS, src_name)
    if os.path.exists(sp):
        im = Image.open(sp).convert("RGBA")
        im.thumbnail((640, 640), Image.Resampling.LANCZOS)
        im.save(os.path.join(PROD_IMG_DIR, dest_name))
    else:
        print("MISSING CROP:", src_name)

# Also copy Minh Phu commercial post images (resized cleanly to 640px for fast viewing)
comm_sources = {
    "mp_vrvh_6_10.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn Nóng điều Hòa trung tâm Daikin\Dàn nóng Điều Hòa trung Tâm VRV - H 2 Chiều lạnh Sưởi\Dàn nóng điều Hòa trung tâm VRV H 6-10 HP.png",
    "mp_vrvh_12_20.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn Nóng điều Hòa trung tâm Daikin\Dàn nóng Điều Hòa trung Tâm VRV - H 2 Chiều lạnh Sưởi\Dàn nóng điều Hòa trung tâm VRV H 12-20 HP.png",
    "mp_vrvh_20_38.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn Nóng điều Hòa trung tâm Daikin\Dàn nóng Điều Hòa trung Tâm VRV - H 2 Chiều lạnh Sưởi\Dàn nóng điều Hòa trung tâm VRV H 20-38 HP.png",
    "mp_vrvh_40_60.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn Nóng điều Hòa trung tâm Daikin\Dàn nóng Điều Hòa trung Tâm VRV - H 2 Chiều lạnh Sưởi\Dàn nóng điều Hòa trung tâm VRV H 40-60 HP.png",
    "mp_vrva_6_10.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn Nóng điều Hòa trung tâm Daikin\Dàn nóng Điều Hòa trung Tâm VRV -A 1 Chiều lạnh\Dàn nóng điều Hòa trung tâm VRV A 6-10 HP.png",
    "mp_vrva_12_20.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn Nóng điều Hòa trung tâm Daikin\Dàn nóng Điều Hòa trung Tâm VRV -A 1 Chiều lạnh\Dàn nóng điều Hòa trung tâm VRV A 12-20 HP.png",
    "mp_vrva_20_38.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn Nóng điều Hòa trung tâm Daikin\Dàn nóng Điều Hòa trung Tâm VRV -A 1 Chiều lạnh\Dàn nóng điều Hòa trung tâm VRV A 20-38 HP.png",
    "mp_vrva_40_60.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn Nóng điều Hòa trung tâm Daikin\Dàn nóng Điều Hòa trung Tâm VRV -A 1 Chiều lạnh\Dàn nóng điều Hòa trung tâm VRV A 40-60 HP.png",
    "mp_vrv4s_4hp.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn Nóng điều Hòa trung tâm Daikin\Dàn nóng Điều Hòa Trung Tâm VRV 4s\Dàn nóng 2 chiều\Dàn nóng VRV 4s 4HP.png",
    "mp_vrv4s_5_6hp.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn Nóng điều Hòa trung tâm Daikin\Dàn nóng Điều Hòa Trung Tâm VRV 4s\Dàn nóng 2 chiều\Dàn nóng VRV 4s 5-6HP.png",
    "mp_vrv4s_8hp.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn Nóng điều Hòa trung tâm Daikin\Dàn nóng Điều Hòa Trung Tâm VRV 4s\Dàn nóng 2 chiều\Dàn nóng VRV 4s 8HP.png",
    "mp_fxfq.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn lạnh điều Hòa Trung tâm Daikin\Dàn lạnh điều Hòa Trung tâm Daikin Âm trần Cassette Đa Hướng thổi\Dàn lạnh âm trần Cassette đa hướng thổi FXFQ25AVM-FXFQ140AVM.png",
    "mp_fxzq.png": r"H:\DAIKIN\Dàn lạnh Loại cassette âm trần 4 hướng thổi.png",
    "mp_fxkq.png": r"H:\DAIKIN\Dàn lạnh Loại cassette âm trần một hướng thổi.png",
    "mp_fxhq.png": r"H:\DAIKIN\Dàn lạnh loại áp trần.png",
    "mp_fxnq.png": r"H:\DAIKIN\Dàn lạnh tủ đứng đặt sàn nối ống gió.png",
    "mp_vam.png": r"H:\DAIKIN\Thiết bị thu hồi nhiệt.png",
    "mp_fxdq_20_32.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn lạnh điều Hòa Trung tâm Daikin\Dàn lạnh điều Hòa Trung tâm Daikin Loại giấu trần nối ống gió dạng mỏng\Dàn lạnh trung âm trần nối gió dạng mỏng Model FXDQ20-32PDVE.png",
    "mp_fxdq_40_63.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn lạnh điều Hòa Trung tâm Daikin\Dàn lạnh điều Hòa Trung tâm Daikin Loại giấu trần nối ống gió dạng mỏng\Dàn lạnh trung âm trần nối gió dạng mỏng Model FXDQ40-63NDVE.png",
    "mp_fxsq_20_125.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn lạnh điều Hòa Trung tâm Daikin\Dàn lạnh điều Hòa Trung tâm Daikin Loại giấu trần nối ống gió dạng mỏng FXSQ\Dàn lạnh trung âm trần nối gió dạng mỏng  Model FXSQ20-125PAVE9.png",
    "mp_fxsq_140.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn lạnh điều Hòa Trung tâm Daikin\Dàn lạnh điều Hòa Trung tâm Daikin Loại giấu trần nối ống gió dạng mỏng FXSQ\Dàn lạnh trung âm trần nối gió dạng mỏng FXSQ140PAVE.png",
    "mp_fxmq_20_140.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn lạnh điều Hòa Trung tâm Daikin\Dàn lạnh điều Hòa Trung tâm Daikin Loại giấu trần nối ống gió hồi sau\Dàn lạnh trung âm trần nối gió dạng  hồi sau Model FXMQ20-140PAVE.png",
    "mp_fxmq_200_250.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn lạnh điều Hòa Trung tâm Daikin\Dàn lạnh điều Hòa Trung tâm Daikin Loại giấu trần nối ống gió hồi sau\Dàn lạnh trung âm trần nối gió dạng  hồi sau Model FXMQ200-250MVE9.png",
    "mp_fxaq.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\Dàn lạnh điều Hòa Trung tâm Daikin\Dàn lạnh điều Hòa Trung tâm Daikin Treo Tường\Dàn lạnh trung tâm treo tường 1 chiều - chiều Daikin.png",
    "mp_refnet_in.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\BỘ CHIA GAS DÀN LẠNH.png",
    "mp_refnet_out.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\BỘ CHIA GAS DÀN NÓNG.png",
    "mp_brc1e63.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\ĐIỀU KHIỂN DÂY BRC1E63.png",
    "mp_brc2e61.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\ĐIỀU KHIỂN DÂY BRC2E61.png",
    "mp_brc7m.png": r"H:\DAIKIN\ẢNH ĐĂNG BÀI ĐIỀU HÒA\Điều Hòa trung Tâm Daikin\ĐIỀU KHIỂN  Cầm tay Model BRC7M675.png",
}

for dest_name, src_path in comm_sources.items():
    if os.path.exists(src_path):
        im = Image.open(src_path).convert("RGB")
        im.thumbnail((640, 640), Image.Resampling.LANCZOS)
        im.save(os.path.join(COMMERCIAL_IMG_DIR, dest_name), quality=88, optimize=True)

print("Assets processed! Cutout PNGs:", len(os.listdir(PROD_IMG_DIR)), "Commercial:", len(os.listdir(COMMERCIAL_IMG_DIR)))
