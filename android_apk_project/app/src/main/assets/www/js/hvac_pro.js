/* ==========================================================================
   hvac_pro.js — Minh Phú HVAC Pro Engineering Suite
   1. TCVN 5687:2024 & QCVN 09:2017/BXD Multi-Room Heat Load Calculator
   2. PDF & AutoCAD (.DXF/.DWG) + AI Vision Drawing Takeoff
   3. Daikin Duct Checker (ASHRAE Hydraulics, Velocity, Friction & ESP Check)
   4. CoolPack-Inspired R410A/R32 Superheat, Subcooling & Daikin Pipe Derating
   Works seamlessly with Python Desktop Backend AND 100% Offline JS Fallback (Android APK)!
   ========================================================================== */

const HVAC_STORAGE_KEY = "mp_hvac_pro_state_v1";
const AI_CFG_STORAGE_KEY = "mp_hvac_ai_config_v1";

/* ---------------- OFFICIAL TCVN 5687:2024 & VN MATERIALS CATALOG (JS MIRROR) ---------------- */
const HVAC_META_DEFAULT = {
  cities: {
    HANOI:       { name: "Hà Nội (Đồng bằng Bắc Bộ)",              I: { tdb: 35.4, twb: 28.0, t_win: 9.6 },  "1%": { tdb: 34.4, twb: 27.9, t_win: 10.6 }, II: { tdb: 33.4, twb: 27.5, t_win: 11.5 } },
    HCM:         { name: "TP. Hồ Chí Minh (Đông Nam Bộ)",          I: { tdb: 35.4, twb: 25.7, t_win: 20.7 }, "1%": { tdb: 34.7, twb: 25.7, t_win: 21.6 }, II: { tdb: 34.0, twb: 25.5, t_win: 22.5 } },
    DANANG:      { name: "Đà Nẵng (Nam Trung Bộ)",                 I: { tdb: 36.1, twb: 27.0, t_win: 16.6 }, "1%": { tdb: 35.1, twb: 26.8, t_win: 17.5 }, II: { tdb: 34.2, twb: 26.6, t_win: 18.4 } },
    QUANGNINH:   { name: "Quảng Ninh / Hải Phòng (Ven biển BB)",   I: { tdb: 33.1, twb: 27.5, t_win: 9.5 },  "1%": { tdb: 32.4, twb: 27.3, t_win: 10.7 }, II: { tdb: 31.8, twb: 27.2, t_win: 11.6 } },
    VINH:        { name: "Nghệ An - Vinh (Bắc Trung Bộ)",          I: { tdb: 36.6, twb: 26.9, t_win: 10.7 }, "1%": { tdb: 35.6, twb: 26.9, t_win: 11.9 }, II: { tdb: 34.6, twb: 26.6, t_win: 13.0 } },
    NHATRANG:    { name: "Nha Trang (Duyên hải Nam Trung Bộ)",     I: { tdb: 33.3, twb: 26.3, t_win: 19.5 }, "1%": { tdb: 32.7, twb: 26.3, t_win: 20.3 }, II: { tdb: 32.2, twb: 26.2, t_win: 21.1 } },
    CANTHO:      { name: "Cần Thơ (Tây Nam Bộ)",                   I: { tdb: 33.6, twb: 26.4, t_win: 20.8 }, "1%": { tdb: 33.0, twb: 26.0, t_win: 21.6 }, II: { tdb: 32.5, twb: 26.2, t_win: 22.2 } },
    CAMAU:       { name: "Cà Mau (Cực Nam)",                       I: { tdb: 34.2, twb: 25.9, t_win: 21.5 }, "1%": { tdb: 33.6, twb: 25.8, t_win: 22.2 }, II: { tdb: 33.0, twb: 25.7, t_win: 22.7 } },
    BUONMATHUOT: { name: "Buôn Ma Thuột (Tây Nguyên)",             I: { tdb: 34.3, twb: 22.0, t_win: 15.5 }, "1%": { tdb: 33.4, twb: 22.5, t_win: 16.4 }, II: { tdb: 32.4, twb: 22.4, t_win: 17.2 } },
    DALAT:       { name: "Đà Lạt (Cao nguyên ôn đới)",             I: { tdb: 25.9, twb: 16.7, t_win: 9.7 },  "1%": { tdb: 25.2, twb: 17.6, t_win: 10.7 }, II: { tdb: 24.5, twb: 17.6, t_win: 11.5 } },
    LANGSON:     { name: "Lạng Sơn (Đông Bắc Bộ)",                 I: { tdb: 33.8, twb: 26.5, t_win: 5.1 },  "1%": { tdb: 33.0, twb: 25.8, t_win: 6.5 },  II: { tdb: 32.2, twb: 25.7, t_win: 7.8 } },
    YENBAI:      { name: "Yên Bái (Trung du Bắc Bộ)",              I: { tdb: 35.2, twb: 27.9, t_win: 9.5 },  "1%": { tdb: 34.2, twb: 27.6, t_win: 10.6 }, II: { tdb: 33.3, twb: 27.3, t_win: 11.6 } },
    HAGIANG:     { name: "Hà Giang (Miền núi phía Bắc)",           I: { tdb: 34.9, twb: 27.1, t_win: 8.5 },  "1%": { tdb: 34.1, twb: 27.0, t_win: 10.1 }, II: { tdb: 33.3, twb: 26.9, t_win: 11.2 } },
    LAICHAU:     { name: "Lai Châu (Tây Bắc Bộ)",                  I: { tdb: 36.1, twb: 25.4, t_win: 9.9 },  "1%": { tdb: 34.9, twb: 25.8, t_win: 11.3 }, II: { tdb: 33.8, twb: 25.9, t_win: 12.4 } },
    SAPA:        { name: "Sa Pa - Lào Cai (Vùng núi cao)",         I: { tdb: 25.8, twb: 18.6, t_win: 1.5 },  "1%": { tdb: 24.9, twb: 18.6, t_win: 2.7 },  II: { tdb: 24.2, twb: 18.6, t_win: 3.8 } }
  },
  walls: {
    BRICK_220_SOLID:  { name: "Tường gạch đặc 220mm trát 2 mặt (U=1.85)",                   u: 1.85, r0: 0.54, cltd_adj: 0.0 },
    BRICK_220_HOLLOW: { name: "Tường gạch ống/lỗ 220mm trát 2 mặt (U=1.62 — Đạt QCVN 09)",  u: 1.62, r0: 0.62, cltd_adj: -1.0 },
    BRICK_110_SOLID:  { name: "Tường gạch đặc 110mm trát 2 mặt (U=2.65)",                   u: 2.65, r0: 0.38, cltd_adj: 2.0 },
    BRICK_110_HOLLOW: { name: "Tường gạch lỗ 110mm trát 2 mặt (U=2.40)",                    u: 2.40, r0: 0.42, cltd_adj: 1.5 },
    AAC_200:          { name: "Tường gạch nhẹ bê tông khí chưng áp AAC 200mm (U=0.72)",     u: 0.72, r0: 1.39, cltd_adj: -2.5 },
    RC_200:           { name: "Tường bê tông cốt thép 200mm trát 2 mặt (U=3.12)",           u: 3.12, r0: 0.32, cltd_adj: 1.5 },
    RC_200_STONE:     { name: "Tường bê tông 200mm ốp đá Granite / Marble (U=2.95)",        u: 2.95, r0: 0.34, cltd_adj: 1.0 },
    BRICK_220_STONE:  { name: "Tường gạch 220mm ốp đá Granite mặt tiền (U=1.78 — Đạt QCVN)",u: 1.78, r0: 0.56, cltd_adj: 0.0 },
    BRICK_220_XPS50:  { name: "Tường gạch 220mm + Cách nhiệt XPS/PU 50mm (U=0.45)",         u: 0.45, r0: 2.22, cltd_adj: -3.0 },
    GYPSUM_ROCKWOOL:  { name: "Vách thạch cao 2 mặt + Bông khoáng 50mm (U=0.62)",           u: 0.62, r0: 1.61, cltd_adj: -2.0 }
  },
  glasses: {
    CLEAR_SINGLE:    { name: "Kính đơn trong 8-10mm khung nhôm thường (SHGC=0.81)",          u: 5.80, shgc: 0.81 },
    TEMPERED_XINGFA: { name: "Kính cường lực 10-12mm hệ nhôm Xingfa (SHGC=0.78)",            u: 5.60, shgc: 0.78 },
    LAMINATED_10:    { name: "Kính dán an toàn 2 lớp 8.38-10.38mm (SHGC=0.72)",              u: 5.40, shgc: 0.72 },
    SOLAR_SINGLE:    { name: "Kính phản quang / Solar Control đơn 8-10mm (SHGC=0.48)",       u: 5.50, shgc: 0.48 },
    DOUBLE_CLEAR:    { name: "Kính hộp 2 lớp 6-12-6mm nhôm cầu cách nhiệt (SHGC=0.68)",      u: 2.80, shgc: 0.68 },
    DOUBLE_LOW_E:    { name: "Kính hộp Low-E 2 lớp 6-12-6mm (SHGC=0.36 — Chuẩn QCVN 09)",    u: 1.85, shgc: 0.36 },
    CURTAIN_LOW_E:   { name: "Vách kính mặt dựng Solar Control Low-E cao cấp (SHGC=0.28)",   u: 1.65, shgc: 0.28 }
  },
  shadings: {
    NONE:     { name: "Không rèm che nắng (SC=1.00)",                        sc: 1.00 },
    LIGHT:    { name: "Rèm vải mỏng / Rèm voan sáng màu (SC=0.68)",          sc: 0.68 },
    ROLLER:   { name: "Rèm cuốn / Rèm cầu vồng văn phòng (SC=0.55)",         sc: 0.55 },
    BLACKOUT: { name: "Rèm cản nắng 2 lớp / Chớp ngoài (SC=0.42)",           sc: 0.42 },
    OVERHANG: { name: "Mái hiên / Ban công đua sâu ≥1.2m + Rèm (SC=0.35)",   sc: 0.35 }
  },
  roofs: {
    MID_FLOOR:     { name: "Tầng giữa (Phía trên là phòng có điều hòa)",              u: 0.00, cltd: 0.0 },
    UPPER_NON_AC:  { name: "Trần bê tông giáp tầng trên KHÔNG điều hòa",              u: 1.85, cltd: 6.5 },
    ROOF_RC_PLAIN: { name: "Mái bê tông 150mm KHÔNG chống nóng + trần TC",            u: 2.15, cltd: 24.0 },
    ROOF_RC_INSUL: { name: "Mái bê tông 150mm + Chống nóng gạch bọng / PU 50mm",      u: 0.58, cltd: 18.0 },
    ROOF_TILE_INS: { name: "Mái ngói / Mái tôn + Bông thủy tinh 50mm + trần TC",      u: 0.72, cltd: 21.0 },
    ROOF_METAL:    { name: "Mái tôn 1 lớp cách nhiệt kém (nhà xưởng/tầng tum)",       u: 2.85, cltd: 28.0 }
  },
  floors: {
    GROUND:      { name: "Sàn tầng trệt (tiếp xúc nền đất)",                          u: 0.45, dt_factor: 0.35 },
    MID_AC:      { name: "Sàn tầng giữa (phía dưới có điều hòa)",                     u: 0.00, dt_factor: 0.00 },
    OVER_NON_AC: { name: "Sàn trên tầng hầm / gara / không gian không ĐHKK",          u: 1.75, dt_factor: 0.55 },
    OVER_EXT:    { name: "Sàn đua ban công / sảnh hở ngoài trời",                     u: 2.10, dt_factor: 0.85 }
  },
  doors: {
    NONE:               { name: "Không tính riêng cửa chính (đã gộp tường/lọt khí)", u: 0.00, glass_ratio: 0.00, inf_m3h_m2: 0.0 },
    WOOD_SOLID_45:      { name: "Cửa gỗ tự nhiên đặc 45mm (Lim, Gõ đỏ, Óc chó)",     u: 2.20, glass_ratio: 0.00, inf_m3h_m2: 6.5 },
    WOOD_ENG_HDF:       { name: "Cửa gỗ công nghiệp / Nhựa gỗ Composite (An Cường)", u: 2.60, glass_ratio: 0.00, inf_m3h_m2: 5.0 },
    STEEL_FIRE:         { name: "Cửa thép chống cháy / Thép vân gỗ lõi bông khoáng", u: 2.80, glass_ratio: 0.00, inf_m3h_m2: 4.5 },
    ALUM_XINGFA_GLASS:  { name: "Cửa đi nhôm kính Xingfa / PMA (75% kính)",          u: 4.80, glass_ratio: 0.75, inf_m3h_m2: 5.5 },
    TEMPERED_12_FULL:   { name: "Cửa kính cường lực thủy lực 12mm (Sảnh/VP)",        u: 5.60, glass_ratio: 0.95, inf_m3h_m2: 14.0 },
    AUTO_SLIDING_GLASS: { name: "Cửa kính trượt tự động (Bệnh viện / Sảnh)",         u: 5.40, glass_ratio: 0.90, inf_m3h_m2: 22.0 },
    HOSPITAL_HERMETIC:  { name: "Cửa kín khí Bệnh viện / Phòng sạch (Hermetic)",     u: 1.80, glass_ratio: 0.15, inf_m3h_m2: 1.2 },
    UPVC_GLASS:         { name: "Cửa nhựa lõi thép uPVC gioăng kín (70% kính)",      u: 3.20, glass_ratio: 0.70, inf_m3h_m2: 2.8 }
  },
  window_frames: {
    XINGFA_NO_TB:       { name: "Khung nhôm hệ Xingfa / Việt Pháp",                  u_factor: 1.00, inf_m3h_m2: 3.2 },
    ALUM_THERMAL_BREAK: { name: "Khung nhôm cầu cách nhiệt (Civro / Eurowindow)",    u_factor: 0.85, inf_m3h_m2: 1.8 },
    UPVC_REINF:         { name: "Khung nhựa lõi thép uPVC gioăng kép",               u_factor: 0.82, inf_m3h_m2: 1.5 },
    WOOD_FRAME:         { name: "Khung gỗ tự nhiên truyền thống",                    u_factor: 0.88, inf_m3h_m2: 4.2 },
    CURTAIN_WALL:       { name: "Vách kính mặt dựng cố định (Fix / Stick)",          u_factor: 0.92, inf_m3h_m2: 0.8 }
  },
  equipment_library: {
    TV_LED_55:       { cat: "HOME",     name: "TV LED / OLED 55\"–75\"",                         q_sens_w: 150,  q_lat_w: 0,   unit: "Chiếc" },
    FRIDGE_SIDE:     { cat: "HOME",     name: "Tủ lạnh Inverter / Side-by-Side",                 q_sens_w: 220,  q_lat_w: 0,   unit: "Chiếc" },
    INDUCTION_COOK:  { cat: "HOME",     name: "Bếp từ đôi / Bếp điện (có hút mùi)",              q_sens_w: 750,  q_lat_w: 250, unit: "Bộ" },
    RICE_KETTLE:     { cat: "HOME",     name: "Nồi cơm điện / Ấm siêu tốc / Máy pha trà",        q_sens_w: 280,  q_lat_w: 180, unit: "Bộ" },
    OVEN_MICRO:      { cat: "HOME",     name: "Lò nướng / Lò vi sóng / Nồi chiên không dầu",     q_sens_w: 550,  q_lat_w: 100, unit: "Chiếc" },
    WINE_COOLER:     { cat: "HOME",     name: "Tủ bảo quản rượu vang / Cây lọc nước nóng lạnh",  q_sens_w: 180,  q_lat_w: 0,   unit: "Chiếc" },
    PC_HOME:         { cat: "HOME",     name: "Máy tính bàn gia đình / Gaming PC",               q_sens_w: 320,  q_lat_w: 0,   unit: "Bộ" },
    WASHER_DRYER:    { cat: "HOME",     name: "Máy giặt / Máy sấy trong phòng",                  q_sens_w: 450,  q_lat_w: 250, unit: "Chiếc" },
    LAPTOP_DESK:     { cat: "OFFICE",   name: "Laptop + Màn hình rời (1 nhân viên VP)",          q_sens_w: 85,   q_lat_w: 0,   unit: "Bộ" },
    DESKTOP_PC:      { cat: "OFFICE",   name: "Máy tính Workstation + Màn hình 24\"–27\"",       q_sens_w: 220,  q_lat_w: 0,   unit: "Bộ" },
    PRINTER_MFP:     { cat: "OFFICE",   name: "Máy in Laser / Photocopy đa năng VP",             q_sens_w: 550,  q_lat_w: 0,   unit: "Chiếc" },
    PROJECTOR_LED:   { cat: "OFFICE",   name: "Máy chiếu hội nghị / Màn hình tương tác",         q_sens_w: 380,  q_lat_w: 0,   unit: "Bộ" },
    WATER_DISPENSER: { cat: "OFFICE",   name: "Cây nước uống nóng lạnh văn phòng",               q_sens_w: 260,  q_lat_w: 0,   unit: "Chiếc" },
    COFFEE_OFFICE:   { cat: "OFFICE",   name: "Máy pha cà phê Espresso Pantry",                  q_sens_w: 420,  q_lat_w: 140, unit: "Chiếc" },
    RACK_SWITCH:     { cat: "OFFICE",   name: "Tủ mạng Switch / Router / Đầu ghi Camera",        q_sens_w: 350,  q_lat_w: 0,   unit: "Tủ" },
    SERVER_RACK:     { cat: "OFFICE",   name: "Tủ Server / Máy chủ nội bộ (1/2 Rack)",           q_sens_w: 1800, q_lat_w: 0,   unit: "Tủ" },
    PATIENT_MON:     { cat: "HOSPITAL", name: "Monitor theo dõi bệnh nhân + Bơm tiêm điện",      q_sens_w: 180,  q_lat_w: 0,   unit: "Bộ" },
    ULTRASOUND:      { cat: "HOSPITAL", name: "Máy Siêu âm màu 4D / Doppler",                    q_sens_w: 650,  q_lat_w: 0,   unit: "Máy" },
    DENTAL_CHAIR:    { cat: "HOSPITAL", name: "Ghế Nha khoa + Đèn thủ thuật + Máy hút",          q_sens_w: 950,  q_lat_w: 80,  unit: "Ghế" },
    XRAY_BIOCHEM:    { cat: "HOSPITAL", name: "Máy Xét nghiệm sinh hóa / Trạm X-Quang",          q_sens_w: 1400, q_lat_w: 0,   unit: "Máy" },
    CT_MRI_SCANNER:  { cat: "HOSPITAL", name: "Máy Chụp CT Scanner / MRI (tỏa nhiệt phòng)",     q_sens_w: 4200, q_lat_w: 0,   unit: "Hệ" },
    AUTOCLAVE_STER:  { cat: "HOSPITAL", name: "Nồi hấp tiệt trùng Autoclave / Tủ sấy dụng cụ",   q_sens_w: 1200, q_lat_w: 450, unit: "Máy" },
    OT_LIGHT_ESU:    { cat: "HOSPITAL", name: "Đèn mổ LED 2 nhánh + Dao mổ điện",                q_sens_w: 780,  q_lat_w: 0,   unit: "Bộ" },
    VACCINE_FRIDGE:  { cat: "HOSPITAL", name: "Tủ bảo quản Vắc-xin / Sinh phẩm y tế",            q_sens_w: 320,  q_lat_w: 0,   unit: "Tủ" },
    ICU_VENTILATOR:  { cat: "HOSPITAL", name: "Máy thở ICU + Thiết bị hồi sức tích cực",         q_sens_w: 420,  q_lat_w: 0,   unit: "Bộ" }
  },
  room_presets: {
    BEDROOM:        { name: "Phòng ngủ (Nhà ở / Biệt thự)",             t_in: 25.0, rh_in: 60, oa_per_person: 35, oa_per_m2: 0, light_w_m2: 7,  equip_w_m2: 6,  m2_per_person: 10.0, q_pers_s: 65,  q_pers_l: 45,  ach_inf: 0.40 },
    LIVING:         { name: "Phòng khách / Sinh hoạt chung",            t_in: 25.0, rh_in: 60, oa_per_person: 30, oa_per_m2: 0, light_w_m2: 9,  equip_w_m2: 10, m2_per_person: 8.0,  q_pers_s: 70,  q_pers_l: 50,  ach_inf: 0.60 },
    DINING:         { name: "Phòng ăn / Bếp ăn gia đình",               t_in: 25.5, rh_in: 60, oa_per_person: 30, oa_per_m2: 0, light_w_m2: 9,  equip_w_m2: 22, m2_per_person: 5.0,  q_pers_s: 75,  q_pers_l: 65,  ach_inf: 0.80 },
    HOTEL_ROOM:     { name: "Phòng ngủ Khách sạn / Resort",             t_in: 24.5, rh_in: 60, oa_per_person: 35, oa_per_m2: 0, light_w_m2: 8,  equip_w_m2: 8,  m2_per_person: 10.0, q_pers_s: 65,  q_pers_l: 45,  ach_inf: 0.50 },
    OFFICE:         { name: "Văn phòng làm việc (TCVN 5687)",           t_in: 25.0, rh_in: 60, oa_per_person: 25, oa_per_m2: 0, light_w_m2: 11, equip_w_m2: 18, m2_per_person: 8.0,  q_pers_s: 70,  q_pers_l: 55,  ach_inf: 0.50 },
    MEETING:        { name: "Phòng họp / Hội thảo",                     t_in: 24.5, rh_in: 60, oa_per_person: 30, oa_per_m2: 0, light_w_m2: 12, equip_w_m2: 12, m2_per_person: 2.0,  q_pers_s: 70,  q_pers_l: 55,  ach_inf: 0.60 },
    SHOWROOM:       { name: "Showroom / Cửa hàng bán lẻ",               t_in: 25.0, rh_in: 60, oa_per_person: 25, oa_per_m2: 5, light_w_m2: 16, equip_w_m2: 12, m2_per_person: 5.0,  q_pers_s: 75,  q_pers_l: 65,  ach_inf: 0.90 },
    RESTAURANT:     { name: "Nhà hàng / Quán Café",                     t_in: 25.0, rh_in: 60, oa_per_person: 30, oa_per_m2: 0, light_w_m2: 12, equip_w_m2: 25, m2_per_person: 1.6,  q_pers_s: 80,  q_pers_l: 80,  ach_inf: 1.00 },
    CLASSROOM:      { name: "Phòng học / Trung tâm đào tạo",            t_in: 25.5, rh_in: 60, oa_per_person: 25, oa_per_m2: 0, light_w_m2: 11, equip_w_m2: 8,  m2_per_person: 2.2,  q_pers_s: 70,  q_pers_l: 55,  ach_inf: 0.60 },
    GYM:            { name: "Phòng Gym / Thể thao",                     t_in: 24.0, rh_in: 60, oa_per_person: 35, oa_per_m2: 0, light_w_m2: 10, equip_w_m2: 15, m2_per_person: 4.0,  q_pers_s: 160, q_pers_l: 265, ach_inf: 0.80 },
    LOBBY:          { name: "Tiền sảnh / Khu đón tiếp",                 t_in: 26.5, rh_in: 60, oa_per_person: 25, oa_per_m2: 0, light_w_m2: 12, equip_w_m2: 8,  m2_per_person: 4.0,  q_pers_s: 75,  q_pers_l: 65,  ach_inf: 1.20 },
    CLINIC:         { name: "Phòng khám bệnh / Nha khoa / Siêu âm",     t_in: 24.5, rh_in: 55, oa_per_person: 40, oa_per_m2: 0, light_w_m2: 14, equip_w_m2: 20, m2_per_person: 6.0,  q_pers_s: 70,  q_pers_l: 50,  ach_inf: 0.50 },
    HOSPITAL_WARD:  { name: "Phòng bệnh nhân nội trú / Hồi sức (TCVN)", t_in: 24.5, rh_in: 55, oa_per_person: 40, oa_per_m2: 0, light_w_m2: 10, equip_w_m2: 15, m2_per_person: 8.0,  q_pers_s: 65,  q_pers_l: 50,  ach_inf: 0.40 },
    OPERATING_ROOM: { name: "Phòng mổ / Thủ thuật y tế (Áp suất dương)",t_in: 22.0, rh_in: 50, oa_per_person: 60, oa_per_m2: 8, light_w_m2: 22, equip_w_m2: 35, m2_per_person: 5.0,  q_pers_s: 90,  q_pers_l: 95,  ach_inf: 0.20 },
    LAB_CLINIC:     { name: "Phòng xét nghiệm / Chẩn đoán hình ảnh",    t_in: 23.0, rh_in: 50, oa_per_person: 40, oa_per_m2: 5, light_w_m2: 16, equip_w_m2: 40, m2_per_person: 7.0,  q_pers_s: 75,  q_pers_l: 55,  ach_inf: 0.40 }
  },
  ai_providers: {
    gemini:     { name: "Google Gemini",          icon: "✨", login_url: "https://aistudio.google.com/apikey",           vision: true,  default_model: "gemini-2.5-flash",        models: ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash", "gemini-1.5-pro"], desc: "Khuyên dùng! Có gói miễn phí Google AI Studio, đọc bản vẽ Vision rất tốt." },
    openai:     { name: "OpenAI (ChatGPT)",       icon: "🚀", login_url: "https://platform.openai.com/api-keys",         vision: true,  default_model: "gpt-4o-mini",             models: ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "o3-mini"], desc: "Tài khoản OpenAI Platform, mạnh về phân tích kỹ thuật & Vision." },
    claude:     { name: "Anthropic Claude",       icon: "🧠", login_url: "https://console.anthropic.com/settings/keys",  vision: true,  default_model: "claude-3-5-sonnet-latest",models: ["claude-3-5-sonnet-latest", "claude-3-7-sonnet-latest", "claude-3-5-haiku-latest"], desc: "Viết báo cáo thẩm định kỹ thuật HVAC tiếng Việt cực sắc sảo & Vision." },
    deepseek:   { name: "DeepSeek AI",            icon: "⚡", login_url: "https://platform.deepseek.com/api_keys",       vision: false, default_model: "deepseek-chat",           models: ["deepseek-chat", "deepseek-reasoner"], desc: "Chi phí siêu rẻ, tư duy lập luận kỹ thuật tốt." },
    openrouter: { name: "OpenRouter (Đa Model)",  icon: "🌐", login_url: "https://openrouter.ai/keys",                   vision: true,  default_model: "google/gemini-2.5-flash", models: ["google/gemini-2.5-flash", "openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet", "deepseek/deepseek-chat-v3-0324"], desc: "1 tài khoản đăng nhập dùng hàng trăm Model AI khác nhau." },
    ollama:     { name: "Ollama (AI Nội Bộ)",     icon: "💻", login_url: "https://ollama.com/download",                  vision: true,  default_model: "qwen2.5:7b",              models: ["qwen2.5:7b", "llama3.2-vision", "gemma3:4b", "deepseek-r1:8b"], desc: "Chạy AI ngay trên máy tính cá nhân — bảo mật tuyệt đối 100%, không mất phí." },
    offline:    { name: "Chuyên Gia Offline",     icon: "🛡️", login_url: "",                                             vision: false, default_model: "minhphu-tcvn5687-v2",     models: ["minhphu-tcvn5687-v2"], desc: "Hệ chuyên gia TCVN 5687:2024 tích hợp sẵn, chạy 100% không cần Internet." }
  },
  orientations: {
    W:   { label: "Tây (Nắng gắt chiều)",          shgf: 640, cltd_wall: 18.5, clf: 0.78 },
    SW:  { label: "Tây Nam (Nắng chiều)",          shgf: 560, cltd_wall: 16.5, clf: 0.76 },
    NW:  { label: "Tây Bắc (Nắng chiều)",          shgf: 540, cltd_wall: 16.0, clf: 0.76 },
    E:   { label: "Đông (Nắng sáng)",              shgf: 520, cltd_wall: 15.0, clf: 0.72 },
    SE:  { label: "Đông Nam (Mát/Nắng sớm)",       shgf: 420, cltd_wall: 13.0, clf: 0.70 },
    NE:  { label: "Đông Bắc (Nắng sớm)",           shgf: 410, cltd_wall: 13.0, clf: 0.70 },
    S:   { label: "Nam (Gió mát)",                 shgf: 320, cltd_wall: 11.5, clf: 0.68 },
    N:   { label: "Bắc (Ít nắng trực tiếp)",       shgf: 210, cltd_wall: 9.5,  clf: 0.68 },
    INT: { label: "Nội bộ (Không tiếp xúc nắng)",  shgf: 0,   cltd_wall: 0.0,  clf: 0.0  }
  }
};

let HVAC_META = JSON.parse(JSON.stringify(HVAC_META_DEFAULT));

let HVAC_STATE = {
  activeTab: "heatload",
  workMode: "offline", // "offline" (default — manual detailed engineering) | "ai" (AI model login & vision)
  city: "HANOI",
  grade: "I",
  t_out_override: "",
  twb_out_override: "",
  safety_pct: 10,
  diversity_factor: 0.85,
  use_hrv: true,
  hrv_efficiency: 0.70,
  prefer_system: "VRV_DUCT",
  rooms: [],
  lastCalc: null,
  lastDuct: null,
  lastCoolpack: null,
  aiReportText: "",
  aiReportMode: "OFFLINE_EXPERT",
  takeoff: {
    filename: "",
    file_b64: "",
    file_type: "",
    page: 1,
    total_pages: 1,
    preview_data_url: "",
    note: "",
    rooms: []
  },
  ductInput: {
    model_id: "FXSQ63PAVE",
    airflow_m3h: 1260,
    esp_rated_pa: 50,
    esp_max_pa: 150,
    num_branches: 3,
    main_len_m: 6.0,
    branch_len_m: 3.5,
    flex_len_m: 2.0,
    num_elbows: 2,
    return_len_m: 3.0,
    max_h_mm: 250,
    target_dp: 1.0
  },
  coolpackInput: {
    refrigerant: "R410A",
    pressure_unit: "bar",
    p_suction: 8.6,
    p_discharge: 27.8,
    t_suction_meas: 13.0,
    t_liquid_meas: 40.5,
    pipe_length_m: 38,
    height_diff_m: 12,
    rated_kw: 40.0,
    liquid_pipe_od: "12.7",
    precharged_m: 0
  }
};

const AI_PROFILES_STORAGE_KEY = "mp_hvac_ai_profiles_v1";

let AI_CONFIG = {
  provider: "offline", // offline | gemini | openai | claude | deepseek | openrouter | ollama
  api_key: "",
  model: "minhphu-tcvn5687-v2",
  account_label: "",
  base_url: ""
};

let AI_PROFILES = {}; // provider -> { api_key, model, account_label, base_url, verified }
let _modalAiProvider = "gemini";
let _editingEquipMap = {}; // eqId -> qty inside Room Editor modal
let _editingEquipTab = "HOME";
let _editingUnitsList = []; // [{prod_id, qty}] inside Room Editor modal (Multi-Indoor per Room!)
let _editingUnitMode = "AUTO"; // "AUTO" | "MANUAL"
let _editingRoomEstBtu = 24000;
let _hvacProInitialized = false;
let _editingRoomIdx = -1;

/* ---------------- SAMPLE VIETNAMESE PROJECTS (HOME / OFFICE / HOSPITAL) ---------------- */
function getSampleVillaRooms() {
  return [
    {
      name: "Phòng Khách Chính", floor: "Tầng 1", room_type: "LIVING",
      area: 42, h_concrete: 3.9, h_ceiling: 3.2, orientation: "W",
      wall_type: "BRICK_220_STONE", ext_wall_len: 7.5,
      win_frame_type: "XINGFA_NO_TB", win_qty: 2, win_w: 2.0, win_h: 1.8, extra_glass_area: 0,
      glass_type: "TEMPERED_XINGFA", shading_type: "BLACKOUT",
      door_type: "ALUM_XINGFA_GLASS", door_qty: 1, door_w: 2.4, door_h: 2.6, door_location: "EXT",
      roof_type: "MID_FLOOR", floor_type: "GROUND",
      partition_len: 4.0, people: 8, light_w_m2: 9, equip_w_m2: "",
      equipment_items: [{ id: "TV_LED_55", qty: 1 }, { id: "WINE_COOLER", qty: 1 }], prefer_type: ""
    },
    {
      name: "Phòng Bếp & Phòng Ăn", floor: "Tầng 1", room_type: "DINING",
      area: 26, h_concrete: 3.9, h_ceiling: 3.2, orientation: "S",
      wall_type: "BRICK_220_HOLLOW", ext_wall_len: 4.5,
      win_frame_type: "XINGFA_NO_TB", win_qty: 1, win_w: 2.2, win_h: 1.6, extra_glass_area: 0,
      glass_type: "DOUBLE_CLEAR", shading_type: "ROLLER",
      door_type: "WOOD_ENG_HDF", door_qty: 1, door_w: 1.0, door_h: 2.2, door_location: "INT",
      roof_type: "MID_FLOOR", floor_type: "GROUND",
      partition_len: 3.0, people: 6, light_w_m2: 9, equip_w_m2: "",
      equipment_items: [{ id: "FRIDGE_SIDE", qty: 1 }, { id: "INDUCTION_COOK", qty: 1 }, { id: "RICE_KETTLE", qty: 1 }, { id: "OVEN_MICRO", qty: 1 }], prefer_type: ""
    },
    {
      name: "Phòng Ngủ Master", floor: "Tầng 2", room_type: "BEDROOM",
      area: 30, h_concrete: 3.6, h_ceiling: 3.0, orientation: "SW",
      wall_type: "BRICK_220_HOLLOW", ext_wall_len: 6.0,
      win_frame_type: "ALUM_THERMAL_BREAK", win_qty: 2, win_w: 1.8, win_h: 1.8, extra_glass_area: 0,
      glass_type: "DOUBLE_LOW_E", shading_type: "BLACKOUT",
      door_type: "WOOD_SOLID_45", door_qty: 1, door_w: 0.95, door_h: 2.2, door_location: "INT",
      roof_type: "MID_FLOOR", floor_type: "MID_AC",
      partition_len: 0, people: 2, light_w_m2: 7, equip_w_m2: "",
      equipment_items: [{ id: "TV_LED_55", qty: 1 }, { id: "PC_HOME", qty: 1 }], prefer_type: ""
    },
    {
      name: "Phòng Ngủ Con 1", floor: "Tầng 2", room_type: "BEDROOM",
      area: 18, h_concrete: 3.6, h_ceiling: 3.0, orientation: "E",
      wall_type: "BRICK_220_HOLLOW", ext_wall_len: 4.2,
      win_frame_type: "XINGFA_NO_TB", win_qty: 1, win_w: 1.6, win_h: 1.5, extra_glass_area: 0,
      glass_type: "DOUBLE_LOW_E", shading_type: "ROLLER",
      door_type: "WOOD_ENG_HDF", door_qty: 1, door_w: 0.9, door_h: 2.2, door_location: "INT",
      roof_type: "MID_FLOOR", floor_type: "MID_AC",
      partition_len: 0, people: 2, light_w_m2: 7, equip_w_m2: "",
      equipment_items: [{ id: "LAPTOP_DESK", qty: 1 }], prefer_type: ""
    },
    {
      name: "Phòng Làm Việc Tầng Áp Mái", floor: "Tầng 3", room_type: "OFFICE",
      area: 24, h_concrete: 3.4, h_ceiling: 2.95, orientation: "W",
      wall_type: "AAC_200", ext_wall_len: 5.0,
      win_frame_type: "ALUM_THERMAL_BREAK", win_qty: 2, win_w: 1.6, win_h: 1.6, extra_glass_area: 0,
      glass_type: "SOLAR_SINGLE", shading_type: "OVERHANG",
      door_type: "WOOD_SOLID_45", door_qty: 1, door_w: 0.95, door_h: 2.2, door_location: "INT",
      roof_type: "ROOF_RC_INSUL", floor_type: "MID_AC",
      partition_len: 0, people: 3, light_w_m2: 11, equip_w_m2: "",
      equipment_items: [{ id: "DESKTOP_PC", qty: 2 }, { id: "PRINTER_MFP", qty: 1 }], prefer_type: ""
    }
  ];
}

function getSampleOfficeRooms() {
  return [
    {
      name: "Khu Làm Việc Nhân Viên (Open Office)", floor: "Tầng 2", room_type: "OFFICE",
      area: 85, h_concrete: 3.6, h_ceiling: 2.85, orientation: "W",
      wall_type: "BRICK_220_HOLLOW", ext_wall_len: 12.0,
      win_frame_type: "CURTAIN_WALL", win_qty: 4, win_w: 2.2, win_h: 2.0, extra_glass_area: 0,
      glass_type: "DOUBLE_LOW_E", shading_type: "ROLLER",
      door_type: "TEMPERED_12_FULL", door_qty: 1, door_w: 1.8, door_h: 2.4, door_location: "INT",
      roof_type: "MID_FLOOR", floor_type: "MID_AC",
      partition_len: 0, people: 14, light_w_m2: 11, equip_w_m2: "",
      equipment_items: [{ id: "LAPTOP_DESK", qty: 12 }, { id: "DESKTOP_PC", qty: 2 }, { id: "PRINTER_MFP", qty: 1 }, { id: "WATER_DISPENSER", qty: 1 }], prefer_type: ""
    },
    {
      name: "Phòng Họp Hội Đồng", floor: "Tầng 2", room_type: "MEETING",
      area: 36, h_concrete: 3.6, h_ceiling: 2.85, orientation: "S",
      wall_type: "GYPSUM_ROCKWOOL", ext_wall_len: 6.0,
      win_frame_type: "ALUM_THERMAL_BREAK", win_qty: 2, win_w: 1.8, win_h: 1.8, extra_glass_area: 0,
      glass_type: "DOUBLE_LOW_E", shading_type: "ROLLER",
      door_type: "TEMPERED_12_FULL", door_qty: 1, door_w: 1.2, door_h: 2.2, door_location: "INT",
      roof_type: "MID_FLOOR", floor_type: "MID_AC",
      partition_len: 0, people: 14, light_w_m2: 12, equip_w_m2: "",
      equipment_items: [{ id: "PROJECTOR_LED", qty: 1 }, { id: "LAPTOP_DESK", qty: 6 }], prefer_type: ""
    },
    {
      name: "Phòng Giám Đốc", floor: "Tầng 2", room_type: "OFFICE",
      area: 28, h_concrete: 3.6, h_ceiling: 2.9, orientation: "SE",
      wall_type: "BRICK_220_HOLLOW", ext_wall_len: 5.5,
      win_frame_type: "ALUM_THERMAL_BREAK", win_qty: 2, win_w: 1.6, win_h: 1.8, extra_glass_area: 0,
      glass_type: "DOUBLE_LOW_E", shading_type: "BLACKOUT",
      door_type: "WOOD_SOLID_45", door_qty: 1, door_w: 1.0, door_h: 2.2, door_location: "INT",
      roof_type: "MID_FLOOR", floor_type: "MID_AC",
      partition_len: 0, people: 3, light_w_m2: 11, equip_w_m2: "",
      equipment_items: [{ id: "DESKTOP_PC", qty: 1 }, { id: "TV_LED_55", qty: 1 }, { id: "COFFEE_OFFICE", qty: 1 }], prefer_type: ""
    },
    {
      name: "Phòng Server / Tủ Mạng IT", floor: "Tầng 2", room_type: "OFFICE",
      area: 14, h_concrete: 3.6, h_ceiling: 2.9, orientation: "INT",
      wall_type: "BRICK_220_SOLID", ext_wall_len: 0,
      win_frame_type: "XINGFA_NO_TB", win_qty: 0, win_w: 0, win_h: 0, extra_glass_area: 0,
      glass_type: "DOUBLE_LOW_E", shading_type: "NONE",
      door_type: "STEEL_FIRE", door_qty: 1, door_w: 1.0, door_h: 2.2, door_location: "INT",
      roof_type: "MID_FLOOR", floor_type: "MID_AC",
      partition_len: 0, people: 1, light_w_m2: 10, equip_w_m2: "",
      equipment_items: [{ id: "SERVER_RACK", qty: 1 }, { id: "RACK_SWITCH", qty: 2 }], prefer_type: ""
    }
  ];
}

function getSampleHospitalRooms() {
  return [
    {
      name: "Sảnh Đón Tiếp & Cấp Cứu", floor: "Tầng 1", room_type: "LOBBY",
      area: 55, h_concrete: 3.8, h_ceiling: 3.0, orientation: "W",
      wall_type: "BRICK_220_HOLLOW", ext_wall_len: 9.0,
      win_frame_type: "ALUM_THERMAL_BREAK", win_qty: 2, win_w: 2.4, win_h: 2.2, extra_glass_area: 0,
      glass_type: "DOUBLE_LOW_E", shading_type: "OVERHANG",
      door_type: "AUTO_SLIDING_GLASS", door_qty: 1, door_w: 2.4, door_h: 2.4, door_location: "EXT",
      roof_type: "MID_FLOOR", floor_type: "GROUND",
      partition_len: 0, people: 16, light_w_m2: 14, equip_w_m2: "",
      equipment_items: [{ id: "DESKTOP_PC", qty: 2 }, { id: "WATER_DISPENSER", qty: 1 }, { id: "TV_LED_55", qty: 1 }], prefer_type: ""
    },
    {
      name: "Phòng Siêu Âm & Chẩn Đoán", floor: "Tầng 1", room_type: "CLINIC",
      area: 24, h_concrete: 3.6, h_ceiling: 2.9, orientation: "S",
      wall_type: "BRICK_220_HOLLOW", ext_wall_len: 4.5,
      win_frame_type: "UPVC_REINF", win_qty: 1, win_w: 1.6, win_h: 1.5, extra_glass_area: 0,
      glass_type: "DOUBLE_LOW_E", shading_type: "BLACKOUT",
      door_type: "HOSPITAL_HERMETIC", door_qty: 1, door_w: 1.2, door_h: 2.2, door_location: "INT",
      roof_type: "MID_FLOOR", floor_type: "GROUND",
      partition_len: 0, people: 4, light_w_m2: 14, equip_w_m2: "",
      equipment_items: [{ id: "ULTRASOUND", qty: 1 }, { id: "DESKTOP_PC", qty: 1 }, { id: "VACCINE_FRIDGE", qty: 1 }], prefer_type: ""
    },
    {
      name: "Phòng Khám Nha Khoa / Tiệt Trùng", floor: "Tầng 2", room_type: "CLINIC",
      area: 28, h_concrete: 3.6, h_ceiling: 2.9, orientation: "E",
      wall_type: "AAC_200", ext_wall_len: 5.5,
      win_frame_type: "ALUM_THERMAL_BREAK", win_qty: 2, win_w: 1.5, win_h: 1.5, extra_glass_area: 0,
      glass_type: "DOUBLE_LOW_E", shading_type: "ROLLER",
      door_type: "HOSPITAL_HERMETIC", door_qty: 1, door_w: 1.2, door_h: 2.2, door_location: "INT",
      roof_type: "MID_FLOOR", floor_type: "MID_AC",
      partition_len: 0, people: 5, light_w_m2: 14, equip_w_m2: "",
      equipment_items: [{ id: "DENTAL_CHAIR", qty: 2 }, { id: "AUTOCLAVE_STER", qty: 1 }], prefer_type: ""
    },
    {
      name: "Phòng Xét Nghiệm Sinh Hóa", floor: "Tầng 2", room_type: "LAB_CLINIC",
      area: 30, h_concrete: 3.6, h_ceiling: 2.9, orientation: "N",
      wall_type: "AAC_200", ext_wall_len: 5.0,
      win_frame_type: "UPVC_REINF", win_qty: 1, win_w: 1.8, win_h: 1.4, extra_glass_area: 0,
      glass_type: "DOUBLE_LOW_E", shading_type: "ROLLER",
      door_type: "HOSPITAL_HERMETIC", door_qty: 1, door_w: 1.2, door_h: 2.2, door_location: "INT",
      roof_type: "MID_FLOOR", floor_type: "MID_AC",
      partition_len: 0, people: 4, light_w_m2: 16, equip_w_m2: "",
      equipment_items: [{ id: "XRAY_BIOCHEM", qty: 1 }, { id: "VACCINE_FRIDGE", qty: 2 }, { id: "DESKTOP_PC", qty: 2 }], prefer_type: ""
    },
    {
      name: "Phòng Mổ / Tiểu Phẫu (Áp Suất Dương)", floor: "Tầng 3", room_type: "OPERATING_ROOM",
      area: 36, h_concrete: 3.8, h_ceiling: 2.9, orientation: "INT",
      wall_type: "GYPSUM_ROCKWOOL", ext_wall_len: 0,
      win_frame_type: "CURTAIN_WALL", win_qty: 0, win_w: 0, win_h: 0, extra_glass_area: 0,
      glass_type: "DOUBLE_LOW_E", shading_type: "NONE",
      door_type: "HOSPITAL_HERMETIC", door_qty: 1, door_w: 1.6, door_h: 2.2, door_location: "INT",
      roof_type: "ROOF_RC_INSUL", floor_type: "MID_AC",
      partition_len: 0, people: 7, light_w_m2: 22, equip_w_m2: "",
      equipment_items: [{ id: "OT_LIGHT_ESU", qty: 1 }, { id: "PATIENT_MON", qty: 2 }, { id: "ICU_VENTILATOR", qty: 1 }], prefer_type: ""
    },
    {
      name: "Phòng Bệnh Nhân Nội Trú VIP", floor: "Tầng 3", room_type: "HOSPITAL_WARD",
      area: 26, h_concrete: 3.6, h_ceiling: 3.0, orientation: "SE",
      wall_type: "BRICK_220_HOLLOW", ext_wall_len: 5.0,
      win_frame_type: "ALUM_THERMAL_BREAK", win_qty: 1, win_w: 2.0, win_h: 1.6, extra_glass_area: 0,
      glass_type: "DOUBLE_LOW_E", shading_type: "BLACKOUT",
      door_type: "WOOD_ENG_HDF", door_qty: 1, door_w: 1.2, door_h: 2.2, door_location: "INT",
      roof_type: "ROOF_RC_INSUL", floor_type: "MID_AC",
      partition_len: 0, people: 3, light_w_m2: 10, equip_w_m2: "",
      equipment_items: [{ id: "PATIENT_MON", qty: 1 }, { id: "TV_LED_55", qty: 1 }, { id: "FRIDGE_SIDE", qty: 1 }], prefer_type: ""
    }
  ];
}

function loadSamplePresetProject(domain) {
  if (domain === "OFFICE") {
    HVAC_STATE.rooms = getSampleOfficeRooms();
    showToast("🏢 Đã nạp dự án mẫu Văn Phòng (kèm Cửa kính, Cửa gỗ & Máy tính/Photocopy/Server)!");
  } else if (domain === "HOSPITAL") {
    HVAC_STATE.rooms = getSampleHospitalRooms();
    showToast("🏥 Đã nạp dự án mẫu Bệnh Viện / Phòng Khám (kèm Cửa trượt tự động, Cửa kín khí Hermetic & Thiết bị y tế)!");
  } else {
    HVAC_STATE.rooms = getSampleVillaRooms();
    showToast("🏠 Đã nạp dự án mẫu Gia Đình / Biệt Thự 3 Tầng (kèm Cửa chính, Cửa sổ & Thiết bị gia dụng)!");
  }
  recalcProjectHeatLoad();
}

/* ---------------- STATE PERSISTENCE ---------------- */
function loadHvacAndAiState() {
  try {
    const rawProfs = localStorage.getItem(AI_PROFILES_STORAGE_KEY);
    if (rawProfs) AI_PROFILES = JSON.parse(rawProfs) || {};
  } catch (e) {}
  try {
    const rawAi = localStorage.getItem(AI_CFG_STORAGE_KEY);
    if (rawAi) AI_CONFIG = Object.assign(AI_CONFIG, JSON.parse(rawAi));
  } catch (e) {}
  if (AI_CONFIG.provider && AI_CONFIG.provider !== "offline" && AI_CONFIG.api_key && !AI_PROFILES[AI_CONFIG.provider]) {
    AI_PROFILES[AI_CONFIG.provider] = {
      api_key: AI_CONFIG.api_key, model: AI_CONFIG.model, account_label: AI_CONFIG.account_label || "", base_url: AI_CONFIG.base_url || ""
    };
  }

  try {
    const raw = localStorage.getItem(HVAC_STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed && Array.isArray(parsed.rooms) && parsed.rooms.length > 0) {
        HVAC_STATE.city = parsed.city || "HANOI";
        HVAC_STATE.grade = parsed.grade || "I";
        HVAC_STATE.safety_pct = parsed.safety_pct ?? 10;
        HVAC_STATE.diversity_factor = parsed.diversity_factor ?? 0.85;
        HVAC_STATE.use_hrv = parsed.use_hrv !== undefined ? parsed.use_hrv : true;
        HVAC_STATE.prefer_system = parsed.prefer_system || "VRV_DUCT";
        HVAC_STATE.rooms = parsed.rooms;
        if (parsed.ductInput) HVAC_STATE.ductInput = Object.assign(HVAC_STATE.ductInput, parsed.ductInput);
        if (parsed.coolpackInput) HVAC_STATE.coolpackInput = Object.assign(HVAC_STATE.coolpackInput, parsed.coolpackInput);
        return;
      }
    }
  } catch (e) {}
  HVAC_STATE.rooms = getSampleVillaRooms();
}

function saveHvacState() {
  try {
    localStorage.setItem(HVAC_STORAGE_KEY, JSON.stringify({
      city: HVAC_STATE.city,
      grade: HVAC_STATE.grade,
      safety_pct: HVAC_STATE.safety_pct,
      diversity_factor: HVAC_STATE.diversity_factor,
      use_hrv: HVAC_STATE.use_hrv,
      prefer_system: HVAC_STATE.prefer_system,
      rooms: HVAC_STATE.rooms,
      ductInput: HVAC_STATE.ductInput,
      coolpackInput: HVAC_STATE.coolpackInput
    }));
  } catch (e) {}
}

function persistAiHub() {
  try {
    localStorage.setItem(AI_CFG_STORAGE_KEY, JSON.stringify(AI_CONFIG));
    localStorage.setItem(AI_PROFILES_STORAGE_KEY, JSON.stringify(AI_PROFILES));
  } catch (e) {}
  if (typeof syncBackupToDesktop === "function") syncBackupToDesktop();
  updateAiModeBadge();
  populateAiSettingsUI();
}

function saveAiSettingsFromAdmin() {
  const prov = document.getElementById("set-ai-provider")?.value || "offline";
  const key = (document.getElementById("set-ai-key")?.value || "").trim();
  const cat = HVAC_META.ai_providers[prov] || HVAC_META.ai_providers.offline;
  const model = (document.getElementById("set-ai-model")?.value || "").trim() || cat.default_model;
  AI_CONFIG = { provider: prov, api_key: key, model, account_label: AI_PROFILES[prov]?.account_label || "", base_url: AI_PROFILES[prov]?.base_url || "" };
  if (prov !== "offline" && (key || prov === "ollama")) {
    AI_PROFILES[prov] = { api_key: key, model, account_label: AI_CONFIG.account_label, base_url: AI_CONFIG.base_url };
  }
  persistAiHub();
  showToast(`🤖 Đã đăng nhập & kích hoạt ${cat.name} (${model})!`);
}

function populateAiSettingsUI() {
  const pEl = document.getElementById("set-ai-provider");
  const kEl = document.getElementById("set-ai-key");
  const mEl = document.getElementById("set-ai-model");
  if (pEl) pEl.value = AI_CONFIG.provider || "offline";
  if (kEl) kEl.value = AI_CONFIG.api_key || "";
  if (mEl) mEl.value = AI_CONFIG.model || (HVAC_META.ai_providers[AI_CONFIG.provider]?.default_model || "gemini-2.5-flash");
  onAiProviderChange(true);
}

function onAiProviderChange(keepModel) {
  const prov = document.getElementById("set-ai-provider")?.value || "offline";
  const cat = HVAC_META.ai_providers[prov] || HVAC_META.ai_providers.offline;
  const mEl = document.getElementById("set-ai-model");
  const kEl = document.getElementById("set-ai-key");
  const hint = document.getElementById("ai-provider-hint");
  if (!keepModel && mEl) {
    mEl.value = (AI_PROFILES[prov] && AI_PROFILES[prov].model) || cat.default_model;
  }
  if (!keepModel && kEl && AI_PROFILES[prov]) {
    kEl.value = AI_PROFILES[prov].api_key || "";
  }
  if (hint) {
    hint.innerHTML = `${cat.icon} <strong>${cat.name}:</strong> ${cat.desc}` +
      (cat.login_url ? ` <a href="#" style="color:#005A8D;font-weight:700;margin-left:6px;" onclick="event.preventDefault();openExternalLink('${cat.login_url}')">🌐 Đăng nhập lấy Key nhanh →</a>` : "");
  }
}

function updateAiModeBadge() {
  const cat = HVAC_META.ai_providers[AI_CONFIG.provider] || HVAC_META.ai_providers.offline;
  const isOnline = AI_CONFIG.provider !== "offline" && (Boolean(AI_CONFIG.api_key) || AI_CONFIG.provider === "ollama");
  const txt = isOnline
    ? `${cat.icon} Đã đăng nhập: ${cat.name} (${AI_CONFIG.model})${AI_CONFIG.account_label ? " • " + AI_CONFIG.account_label : ""}`
    : "🧠 Chế độ Chuyên gia Offline (TCVN 5687:2024)";
  ["hvac-ai-mode-pill", "hvac-ai-top-pill", "tk-ai-status-pill"].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = txt;
    el.style.background = isOnline ? "#EFF6FF" : "#F8FAFC";
    el.style.color = isOnline ? "#005A8D" : "#334155";
    el.style.borderColor = isOnline ? "#93C5FD" : "#CBD5E1";
  });
}

/* ---------------- MULTI-PROVIDER AI LOGIN & MODEL SELECTOR MODAL ---------------- */
function openAiLoginModal(preselectProvider) {
  _modalAiProvider = preselectProvider || (AI_CONFIG.provider !== "offline" ? AI_CONFIG.provider : "gemini");
  renderAiLoginModal();
  document.getElementById("ai-login-modal")?.classList.add("open");
}

function selectAiProviderCard(prov) {
  _modalAiProvider = prov;
  renderAiLoginModal();
}

function renderAiLoginModal() {
  renderAiLoginPanelInto("ai-login-body", false);
  renderAiLoginPanelInto("hv-ai-inline-login", true);
}

function renderAiLoginPanelInto(containerId, isInline) {
  const body = document.getElementById(containerId);
  if (!body) return;
  const pfx = isInline ? "aiin" : "ail";
  const prov = _modalAiProvider || "gemini";
  const cat = HVAC_META.ai_providers[prov] || HVAC_META.ai_providers.gemini;
  const saved = AI_PROFILES[prov] || (AI_CONFIG.provider === prov ? AI_CONFIG : {});
  const curModel = saved.model || cat.default_model;
  const modelsList = Array.from(new Set([curModel, ...(cat.models || [])]));
  const isActive = AI_CONFIG.provider === prov;

  const cardsHtml = Object.entries(HVAC_META.ai_providers).map(([k, info]) => {
    const hasLogin = k === "offline" || Boolean(AI_PROFILES[k]?.api_key) || (k === "ollama" && Boolean(AI_PROFILES[k]));
    const activeNow = AI_CONFIG.provider === k;
    return `
      <div class="ai-prov-card ${k === prov ? "selected" : ""}" onclick="selectAiProviderCard('${k}')">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:18px;">${info.icon}</span>
          ${activeNow ? `<span class="tag-pass">Đang dùng</span>` : (hasLogin && k !== "offline" ? `<span style="font-size:10px;font-weight:700;color:#005A8D;">✓ Đã lưu</span>` : "")}
        </div>
        <div style="font-weight:700;font-size:12.5px;color:#0F172A;margin-top:4px;">${info.name}</div>
        <div style="font-size:10.5px;color:#64748B;">${info.vision ? "Vision + Tạo công trình" : (k === "offline" ? "Miễn phí 100%" : "Tạo công trình + Báo cáo")}</div>
      </div>
    `;
  }).join("");

  body.innerHTML = `
    <div style="font-size:12.5px;color:#334155;margin-bottom:10px;">
      Chọn nhà cung cấp AI bạn muốn <strong>đăng nhập & sử dụng</strong> để nhận diện bản vẽ PDF/Ảnh (Vision), tự tạo bảng phòng & lập báo cáo thẩm định kỹ thuật:
    </div>
    <div class="ai-prov-grid">${cardsHtml}</div>

    <div style="background:#F8FAFC;border:1.5px solid #CBD5E1;border-left:4px solid #005A8D;border-radius:10px;padding:14px 16px;margin-top:14px;">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
        <div>
          <strong style="font-size:14.5px;color:#0F172A;">${cat.icon} ${cat.name}</strong>
          <div style="font-size:12px;color:#475569;margin-top:2px;">${cat.desc}</div>
        </div>
        ${cat.login_url ? `
          <button class="btn btn-sm btn-ice" type="button" onclick="openExternalLink('${cat.login_url}')">
            🌐 Đăng nhập tài khoản & Lấy API Key →
          </button>
        ` : ""}
      </div>

      ${prov !== "offline" ? `
        <div style="display:grid;grid-template-columns:1fr 1.5fr;gap:10px;">
          <div class="form-group">
            <label>Tên tài khoản / Email ghi nhớ (tùy chọn)</label>
            <input type="text" id="${pfx}-account" value="${saved.account_label || ""}" placeholder="VD: kythuathvac@minhphu.vn" />
          </div>
          <div class="form-group">
            <label>${prov === "ollama" ? "API Key (bỏ trống nếu dùng Ollama cục bộ)" : "API Key / Token đăng nhập (lưu bảo mật trên máy)"}</label>
            <div style="display:flex;gap:6px;">
              <input type="password" id="${pfx}-key" style="flex:1;" value="${saved.api_key || ""}" placeholder="${prov === "gemini" ? "AIzaSy..." : (prov === "openai" ? "sk-proj-..." : (prov === "claude" ? "sk-ant-..." : "Nhập API Key..."))}" />
              <button class="btn btn-sm btn-outline" type="button" onclick="const el=document.getElementById('${pfx}-key');el.type=el.type==='password'?'text':'password'">👁️</button>
            </div>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:1.4fr 1fr;gap:10px;margin-top:10px;">
          <div class="form-group">
            <label>Chọn Model AI sử dụng</label>
            <div style="display:flex;gap:6px;">
              <select id="${pfx}-model-select" style="flex:1;" onchange="document.getElementById('${pfx}-model-custom').value=this.value">
                ${modelsList.map(m => `<option value="${m}" ${m === curModel ? "selected" : ""}>${m}</option>`).join("")}
              </select>
              <button class="btn btn-sm btn-outline" type="button" onclick="fetchLiveAiModels('${pfx}')">🔄 Tải DS Model</button>
            </div>
          </div>
          <div class="form-group">
            <label>Hoặc gõ tên Model tùy chỉnh</label>
            <input type="text" id="${pfx}-model-custom" value="${curModel}" />
          </div>
        </div>

        ${(prov === "ollama" || prov === "openai" || prov === "openrouter") ? `
          <div class="form-group" style="margin-top:8px;">
            <label>Endpoint Base URL (tùy chọn — mặc định ${prov === "ollama" ? "http://127.0.0.1:11434/v1" : "Chuẩn chính hãng"})</label>
            <input type="text" id="${pfx}-baseurl" value="${saved.base_url || (prov === "ollama" ? "http://127.0.0.1:11434/v1" : "")}" placeholder="Để trống dùng máy chủ chính thức" />
          </div>
        ` : ""}
      ` : `
        <div class="hvac-badge-ok">✅ Hệ chuyên gia <strong>TCVN 5687:2024 & QCVN 09:2017/BXD</strong> của Minh Phú chạy hoàn toàn Offline, không cần API Key hay Internet.</div>
      `}

      <div id="${pfx}-test-result" style="margin-top:10px;font-size:12px;"></div>

      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-top:12px;padding-top:10px;border-top:1px solid #E2E8F0;">
        <div style="display:flex;gap:8px;">
          <button class="btn btn-sm btn-dark" type="button" onclick="testAiLoginConnection('${pfx}')">🔌 Kiểm Tra Kết Nối</button>
          ${prov !== "offline" && (saved.api_key || isActive) ? `<button class="btn btn-sm btn-outline" style="color:#991B1B;" type="button" onclick="logoutCurrentAiProvider('${prov}')">🚪 Đăng xuất ${cat.name}</button>` : ""}
        </div>
        <div style="display:flex;gap:8px;">
          ${!isInline ? `<button class="btn btn-sm btn-outline" type="button" onclick="closeModal('ai-login-modal')">Đóng</button>` : ""}
          <button class="btn btn-sm btn-primary" type="button" onclick="saveAndActivateAiProfile('${pfx}')">✅ Lưu & Sử Dụng Model Này</button>
        </div>
      </div>
    </div>
  `;
}

function _readAiModalConfig(pfx) {
  const p = pfx || "ail";
  const prov = _modalAiProvider || "offline";
  const cat = HVAC_META.ai_providers[prov] || HVAC_META.ai_providers.offline;
  return {
    provider: prov,
    api_key: (document.getElementById(`${p}-key`)?.value || "").trim(),
    model: (document.getElementById(`${p}-model-custom`)?.value || document.getElementById(`${p}-model-select`)?.value || cat.default_model).trim(),
    account_label: (document.getElementById(`${p}-account`)?.value || "").trim(),
    base_url: (document.getElementById(`${p}-baseurl`)?.value || "").trim()
  };
}

async function fetchLiveAiModels(pfx) {
  const p = pfx || "ail";
  const cfg = _readAiModalConfig(p);
  const resBox = document.getElementById(`${p}-test-result`);
  if (resBox) resBox.innerHTML = `<span style="color:#005A8D;font-weight:700;">⏳ Đang tải danh sách Model từ tài khoản ${cfg.provider.toUpperCase()}...</span>`;
  try {
    const resp = await fetch("/api/hvac/ai_list_models", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(cfg)
    });
    const data = await resp.json();
    if (data && data.ok && Array.isArray(data.models) && data.models.length) {
      const sel = document.getElementById(`${p}-model-select`);
      if (sel) {
        sel.innerHTML = data.models.map(m => `<option value="${m}" ${m === cfg.model ? "selected" : ""}>${m}</option>`).join("");
      }
      if (resBox) resBox.innerHTML = `<span style="color:#16A34A;font-weight:700;">✅ Đã tải ${data.models.length} Model ${data.live ? "trực tiếp từ tài khoản!" : "(danh sách chuẩn)."}</span>`;
      return;
    }
  } catch (e) {}
  if (resBox) resBox.innerHTML = `<span style="color:#475569;">Đang dùng danh sách Model chuẩn của nhà cung cấp.</span>`;
}

async function testAiLoginConnection(pfx) {
  const p = pfx || "ail";
  const cfg = _readAiModalConfig(p);
  const resBox = document.getElementById(`${p}-test-result`);
  if (resBox) resBox.innerHTML = `<span style="color:#005A8D;font-weight:700;">⏳ Đang kiểm tra xác thực Model ${cfg.model}...</span>`;
  try {
    const resp = await fetch("/api/hvac/ai_test", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(cfg)
    });
    const data = await resp.json();
    if (data && data.ok) {
      if (resBox) resBox.innerHTML = `<div class="hvac-badge-ok" style="padding:8px 10px;">✅ <strong>Kết nối thành công!</strong> ${data.latency_ms ? `(${data.latency_ms} ms) ` : ""}— ${data.message}</div>`;
    } else {
      if (resBox) resBox.innerHTML = `<div class="hvac-badge-warn" style="padding:8px 10px;">❌ <strong>Chưa kết nối được:</strong> ${data?.error || "Kiểm tra lại API Key & Internet."}</div>`;
    }
  } catch (e) {
    if (resBox) resBox.innerHTML = `<div class="hvac-badge-warn" style="padding:8px 10px;">⚠️ Kiểm tra kết nối AI trực tiếp cần chạy trên bản Windows Desktop (.exe). Bạn vẫn có thể lưu Key bình thường.</div>`;
  }
}

function saveAndActivateAiProfile(pfx) {
  const p = pfx || "ail";
  const cfg = _readAiModalConfig(p);
  const cat = HVAC_META.ai_providers[cfg.provider] || HVAC_META.ai_providers.offline;
  if (cfg.provider !== "offline" && cfg.provider !== "ollama" && !cfg.api_key) {
    showToast(`⚠️ Vui lòng nhập API Key cho ${cat.name} (hoặc bấm nút 'Đăng nhập tài khoản & Lấy API Key').`);
    return;
  }
  AI_CONFIG = cfg;
  if (cfg.provider !== "offline") {
    AI_PROFILES[cfg.provider] = { api_key: cfg.api_key, model: cfg.model, account_label: cfg.account_label, base_url: cfg.base_url };
  }
  persistAiHub();
  renderAiLoginModal();
  if (p === "ail") closeModal("ai-login-modal");
  showToast(`🤖 Đã đăng nhập & kích hoạt ${cat.name} (${cfg.model})!`);
}

function logoutCurrentAiProvider(prov) {
  delete AI_PROFILES[prov];
  if (AI_CONFIG.provider === prov) {
    AI_CONFIG = { provider: "offline", api_key: "", model: "minhphu-tcvn5687-v2", account_label: "", base_url: "" };
  }
  persistAiHub();
  renderAiLoginModal();
  showToast(`🚪 Đã đăng xuất khỏi ${prov.toUpperCase()}!`);
}

async function runAiGenerateRooms() {
  const desc = (document.getElementById("hv-ai-prompt")?.value || "").trim();
  const cat = document.getElementById("hv-ai-domain")?.value || "AUTO";
  if (!desc && cat === "AUTO") {
    showToast("Vui lòng nhập mô tả công trình (VD: Phòng khám 200m2 có 2 phòng siêu âm...) hoặc chọn loại công trình!");
    return;
  }
  const btn = document.getElementById("btn-ai-gen-rooms");
  if (btn) { btn.disabled = true; btn.textContent = "⏳ AI đang tạo..."; }
  let res = null;
  try {
    const resp = await fetch("/api/hvac/ai_generate_rooms", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description: desc, building_category: cat, ai_config: AI_CONFIG })
    });
    if (resp.ok) res = await resp.json();
  } catch (e) {}

  if (!res || !res.ok || !Array.isArray(res.rooms) || !res.rooms.length) {
    // Pure JS fallback
    const low = desc.toLowerCase();
    const dom = cat !== "AUTO" ? cat : (low.includes("bệnh viện") || low.includes("phòng khám") || low.includes("nha khoa") ? "HOSPITAL" : (low.includes("văn phòng") || low.includes("công ty") ? "OFFICE" : "HOME"));
    res = { ok: true, mode: "OFFLINE_SMART", rooms: dom === "HOSPITAL" ? getSampleHospitalRooms() : (dom === "OFFICE" ? getSampleOfficeRooms() : getSampleVillaRooms()) };
  }

  HVAC_STATE.rooms = res.rooms;
  if (btn) { btn.disabled = false; btn.textContent = "✨ AI Tạo Bảng Phòng & Thiết Bị"; }
  await recalcProjectHeatLoad();
  showToast(`✨ [${res.mode}] Đã tạo ${res.rooms.length} phòng đầy đủ Cửa chính, Cửa sổ & Thiết bị tỏa nhiệt!`);
}

/* ---------------- PURE-JS OFFLINE FALLBACK MATH (100% MIRROR OF hvac_engine.py) ---------------- */
function _satVP(tC) {
  return 0.61078 * Math.exp((17.27 * tC) / (tC + 237.3));
}
function _wFromTdbRh(tdb, rh) {
  const pw = _satVP(tdb) * (rh / 100.0);
  return 0.621945 * pw / Math.max(1.0, 101.325 - pw);
}
function _wFromTdbTwb(tdb, twb) {
  const pws = _satVP(twb);
  const ws = 0.621945 * pws / Math.max(1.0, 101.325 - pws);
  const num = (2501.0 - 2.326 * twb) * ws - 1.006 * (tdb - twb);
  const den = 2501.0 + 1.86 * tdb - 4.186 * twb;
  return Math.max(0.001, num / den);
}
function _enthalpy(tdb, w) { return 1.006 * tdb + w * (2501.0 + 1.86 * tdb); }
function _rhFromTdbW(tdb, w) {
  const pw = (w * 101.325) / (0.621945 + w);
  return Math.max(1, Math.min(100, (pw / Math.max(0.001, _satVP(tdb))) * 100));
}
function _qcvnMaxShgc(wwrPct, orient) {
  if (orient === "INT") return 1.0;
  const isN = orient === "N";
  if (wwrPct <= 20) return isN ? 0.90 : 0.80;
  if (wwrPct <= 30) return isN ? 0.80 : 0.64;
  if (wwrPct <= 40) return isN ? 0.67 : 0.50;
  if (wwrPct <= 50) return isN ? 0.56 : 0.40;
  if (wwrPct <= 60) return isN ? 0.47 : 0.33;
  return isN ? 0.40 : 0.27;
}

function _recommendUnitJS(reqBtu, preferType, plenumMm) {
  const prods = (typeof DB !== "undefined" && DB.products) ? DB.products : [];
  if (!prods.length) return { prod_id: "", model: "—", name: "", qty: 1, cooling_btu: 0, cooling_kw: 0, clearance_ok: true, clearance_note: "" };
  const styleOk = (p) => {
    const cid = p.category_id || "";
    if (cid.includes("_OUT") || cid === "VRV_ACC" || cid === "MULTI_ACC" || cid === "VRV_HRV") return false;
    if (!p.cooling_btu || p.cooling_btu <= 0) return false;
    if (preferType === "VRV_DUCT") return ["VRV_IN_DUCT_SLIM", "VRV_IN_DUCT_MED", "VRV_IN_DUCT_HIGH"].includes(cid);
    if (preferType === "VRV_CASSETTE") return cid === "VRV_IN_CASSETTE";
    if (preferType === "VRV_WALL") return cid === "VRV_IN_WALL";
    if (preferType === "MULTI_DUCT") return cid === "MULTI_IN_DUCT";
    if (preferType === "MULTI_WALL") return cid === "MULTI_IN_WALL";
    if (preferType === "SKY_DUCT") return cid === "SKY_DUCT";
    if (preferType === "SKY_CASSETTE") return cid === "SKY_CASSETTE";
    if (preferType === "ROOM_AIR") return cid === "ROOM_AIR";
    return true;
  };
  let cands = prods.filter(styleOk);
  if (!cands.length) cands = prods.filter(p => p.cooling_btu > 0 && !(p.category_id || "").includes("_OUT"));
  cands.sort((a, b) => a.cooling_btu - b.cooling_btu);
  let qty = 1;
  let chosen = cands.find(p => p.cooling_btu >= reqBtu * 0.94);
  if (!chosen) {
    chosen = cands[cands.length - 1];
    qty = Math.max(1, Math.ceil(reqBtu / Math.max(1, chosen.cooling_btu)));
  }
  if (plenumMm > 0 && plenumMm < 290 && preferType === "VRV_DUCT" && qty === 1) {
    const slims = prods.filter(p => p.category_id === "VRV_IN_DUCT_SLIM" && p.cooling_btu >= reqBtu * 0.94).sort((a, b) => a.cooling_btu - b.cooling_btu);
    if (slims.length) chosen = slims[0];
  }
  const mh = String(chosen.dimensions || "").match(/(\d{3})\s*[xX×]/);
  const unitH = mh ? parseInt(mh[1], 10) : 0;
  const reqPlenum = (chosen.duct || chosen.ceiling_opening) ? (unitH + 45) : 0;
  let clearance_ok = true;
  let clearance_note = "Đạt khoảng hở lắp đặt";
  if (reqPlenum > 0 && plenumMm > 0) {
    if (plenumMm < reqPlenum) {
      clearance_ok = false;
      clearance_note = `CẢNH BÁO: Khoảng trần ${Math.round(plenumMm)}mm < yêu cầu ${reqPlenum}mm (thân máy ${unitH}mm)`;
    } else {
      clearance_note = `Đạt (${Math.round(plenumMm)}mm ≥ ${reqPlenum}mm)`;
    }
  }
  return {
    prod_id: chosen.id, model: chosen.model, name: chosen.name, qty,
    cooling_btu: chosen.cooling_btu, cooling_kw: chosen.cooling_kw,
    total_btu: chosen.cooling_btu * qty, price: chosen.price || 0,
    unit_height_mm: unitH, req_plenum_mm: reqPlenum, clearance_ok, clearance_note,
    duct: chosen.duct || null, image: chosen.image || ""
  };
}

function calcHeatLoadOfflineJS(payload) {
  const city = HVAC_META.cities[payload.city] || HVAC_META.cities.HANOI;
  const clim = city[payload.grade] || city.I;
  const t_out = Number(payload.t_out_override) || clim.tdb;
  const twb_out = Number(payload.twb_out_override) || clim.twb;
  const t_out_win = clim.t_win;
  const w_out = _wFromTdbTwb(t_out, twb_out);
  const rh_out = _rhFromTdbW(t_out, w_out);
  const h_out = _enthalpy(t_out, w_out);

  const safety_pct = Number(payload.safety_pct ?? 10);
  const diversity = Number(payload.diversity_factor ?? 0.85);
  const use_hrv = Boolean(payload.use_hrv);
  const hrv_eff = use_hrv ? Number(payload.hrv_efficiency ?? 0.70) : 0.0;
  const prefer_system = payload.prefer_system || "VRV_DUCT";
  const sfMult = 1.0 + safety_pct / 100.0;

  let tot_area = 0, tot_sens = 0, tot_lat = 0, tot_q = 0, tot_heat = 0, tot_oa = 0, tot_sup = 0, tot_ppl = 0;
  const compSums = { wall: 0, glass_rad: 0, glass_cond: 0, door: 0, roof_floor: 0, partition: 0, people: 0, light_equip: 0, fresh_air: 0, infiltration: 0 };
  const qcvn_warnings = [], clearance_warnings = [], roomsOut = [];

  (payload.rooms || []).forEach((r, idx) => {
    const preset = HVAC_META.room_presets[r.room_type] || HVAC_META.room_presets.LIVING;
    const area = Math.max(1, Number(r.area) || 25);
    const h_bt = Math.max(2.2, Number(r.h_concrete) || 3.6);
    const h_tc = Math.max(2.0, Math.min(h_bt, Number(r.h_ceiling) || 3.0));
    const plenum_m = Math.max(0, h_bt - h_tc);
    const plenum_mm = Math.round(plenum_m * 1000);
    const t_in = Number(r.t_in) || preset.t_in;
    const rh_in = Number(r.rh_in) || preset.rh_in;
    const w_in = _wFromTdbRh(t_in, rh_in);
    const dt = Math.max(1, t_out - t_in);
    const dw = Math.max(0, w_out - w_in);

    const oriKey = r.orientation || "W";
    const ori = HVAC_META.orientations[oriKey] || HVAC_META.orientations.W;
    const wall = HVAC_META.walls[r.wall_type] || HVAC_META.walls.BRICK_220_SOLID;
    const glass = HVAC_META.glasses[r.glass_type] || HVAC_META.glasses.TEMPERED_XINGFA;
    const shade = HVAC_META.shadings[r.shading_type] || HVAC_META.shadings.ROLLER;
    const roof = HVAC_META.roofs[r.roof_type] || HVAC_META.roofs.MID_FLOOR;
    const floor = HVAC_META.floors[r.floor_type] || HVAC_META.floors.MID_AC;
    const wFrame = HVAC_META.window_frames[r.win_frame_type] || HVAC_META.window_frames.XINGFA_NO_TB;
    const doorMat = HVAC_META.doors[r.door_type] || HVAC_META.doors.NONE;

    const extLen = (r.ext_wall_len !== "" && r.ext_wall_len !== undefined) ? Number(r.ext_wall_len) : Math.round(Math.sqrt(area) * 11) / 10;
    let grossExt = oriKey === "INT" ? 0 : Math.max(0, extLen * h_bt);

    const winQty = Math.max(0, Number(r.win_qty) || 0);
    const winW = Math.max(0, Number(r.win_w) || 0);
    const winH = Math.max(0, Number(r.win_h) || 0);
    const winArea = (winQty > 0 && winW > 0 && winH > 0) ? (winQty * winW * winH) : 0;
    const extraGlass = Math.max(0, Number(r.extra_glass_area) || 0);
    let glassArea = winArea > 0 ? (winArea * 0.85 + extraGlass) : Math.max(0, (r.glass_area !== "" && r.glass_area !== undefined) ? Number(r.glass_area) : grossExt * 0.25);
    let winOpening = winArea > 0 ? (winArea + extraGlass) : glassArea;

    const doorQty = Math.max(0, Number(r.door_qty) || (r.door_type && r.door_type !== "NONE" ? 1 : 0));
    const doorW = Math.max(0, Number(r.door_w) || 1.0);
    const doorH = Math.max(0, Number(r.door_h) || 2.2);
    const doorArea = (r.door_type && r.door_type !== "NONE" && doorQty > 0) ? (doorQty * doorW * doorH) : 0;
    const doorIsExt = r.door_location === "EXT" && oriKey !== "INT" && doorArea > 0;

    if (oriKey === "INT") { grossExt = 0; glassArea = 0; winOpening = 0; }
    const extDoorGlass = doorIsExt ? (doorArea * doorMat.glass_ratio) : 0;
    const totGlazed = glassArea + extDoorGlass;
    const netWall = Math.max(0, grossExt - winOpening - (doorIsExt ? doorArea : 0));
    const wwrPct = grossExt > 0 ? (totGlazed / grossExt * 100) : 0;
    const partArea = Math.max(0, Number(r.partition_len) || 0) * h_tc;

    const cltdW = Math.max(dt, ori.cltd_wall + wall.cltd_adj + (25.5 - t_in) + (t_out - 35.0));
    const qWall = oriKey === "INT" ? 0 : wall.u * netWall * cltdW;
    const qGlassRad = totGlazed * ori.shgf * glass.shgc * shade.sc * ori.clf;
    const qGlassCond = (glass.u * wFrame.u_factor) * winOpening * dt;
    const qDoorCond = doorMat.u * doorArea * (doorIsExt ? dt : dt * 0.55);

    let uRoof = roof.u;
    if (uRoof > 0 && plenum_m >= 0.3) uRoof = 1.0 / (1.0 / uRoof + 0.16);
    const qRoof = uRoof > 0 ? uRoof * area * Math.max(0, roof.cltd + (25.5 - t_in) + (t_out - 35.0)) : 0;
    const qFloor = floor.u * area * (dt * floor.dt_factor);
    const qRF = qRoof + qFloor;
    const qPart = 2.2 * partArea * (dt * 0.55);

    const ppl = (r.people !== "" && r.people !== undefined) ? Number(r.people) : Math.max(1, Math.round(area / preset.m2_per_person));
    const qPplS = ppl * preset.q_pers_s, qPplL = ppl * preset.q_pers_l;
    const qLight = area * ((r.light_w_m2 !== "" && r.light_w_m2 !== undefined) ? Number(r.light_w_m2) : preset.light_w_m2);

    const eqItems = Array.isArray(r.equipment_items) ? r.equipment_items : [];
    let qEqItemS = 0, qEqItemL = 0;
    const eqLabels = [];
    eqItems.forEach(ei => {
      const q = Math.max(0, Number(ei.qty) || 0);
      if (q <= 0) return;
      const lib = HVAC_META.equipment_library[ei.id];
      if (lib) {
        qEqItemS += q * lib.q_sens_w;
        qEqItemL += q * lib.q_lat_w;
        eqLabels.push(`${q}× ${lib.name.split("(")[0].trim().slice(0, 22)}`);
      }
    });
    const eqWm2 = (eqItems.length > 0 && (r.equip_w_m2 === "" || r.equip_w_m2 === undefined))
      ? 0 : ((r.equip_w_m2 !== "" && r.equip_w_m2 !== undefined) ? Number(r.equip_w_m2) : preset.equip_w_m2);
    const qEquipS = area * eqWm2 + qEqItemS;

    const oaM3h = (r.oa_override_m3h !== "" && r.oa_override_m3h !== undefined && Number(r.oa_override_m3h) > 0)
      ? Number(r.oa_override_m3h)
      : Math.max(ppl * preset.oa_per_person, area * preset.oa_per_m2);
    const qOaS = 0.3353 * oaM3h * dt * (1 - hrv_eff);
    const qOaL = 833.67 * oaM3h * dw * (1 - hrv_eff * 0.85);

    const achVal = (r.ach_inf !== "" && r.ach_inf !== undefined) ? Number(r.ach_inf) : preset.ach_inf;
    const baseInf = area * h_tc * achVal * (oriKey === "INT" ? 0.45 : 1.0);
    const doorInf = doorArea > 0 ? (doorArea * doorMat.inf_m3h_m2 * (doorIsExt ? 1.0 : 0.45)) : 0;
    const winInf = (winArea > 0 && oriKey !== "INT") ? (winArea * wFrame.inf_m3h_m2) : 0;
    const infM3h = (doorArea > 0 || winArea > 0) ? Math.max(baseInf, doorInf + winInf + baseInf * 0.45) : baseInf;
    const qInfS = 0.3353 * infM3h * dt, qInfL = 833.67 * infM3h * dw;

    const qSens = (qWall + qGlassRad + qGlassCond + qDoorCond + qRF + qPart + qPplS + qLight + qEquipS + qOaS + qInfS) * sfMult;
    const qLat = (qPplL + qEqItemL + qOaL + qInfL) * sfMult;
    const qTot = qSens + qLat;
    const qKw = qTot / 1000.0;
    const qBtu = qKw * 3412.14;
    const supM3h = (3.6 * qSens) / 12.0;

    const wallOk = oriKey === "INT" || wall.r0 >= 0.56;
    const maxShgc = _qcvnMaxShgc(wwrPct, oriKey);
    const glassOk = totGlazed <= 0.1 || glass.shgc <= maxShgc;
    if (!wallOk) qcvn_warnings.push(`${r.name}: Tường ngoài R0=${wall.r0.toFixed(2)} < 0.56 m²K/W (QCVN 09:2017/BXD).`);
    if (!glassOk) qcvn_warnings.push(`${r.name}: Kính/Cửa kính hướng ${oriKey} (WWR=${Math.round(wwrPct)}%) SHGC=${glass.shgc.toFixed(2)} > ${maxShgc.toFixed(2)} (QCVN 09).`);

    // Resolve Multi-Indoor Units per Room (Manual selected_units OR Auto split_units)
    const prodsList = (typeof DB !== "undefined" && DB.products) ? DB.products : [];
    const manualIn = (Array.isArray(r.selected_units) ? r.selected_units : []).filter(u => u && Number(u.qty) > 0);
    const splitCnt = Math.max(1, Number(r.split_units) || 1);
    let assigned_units = [];
    let rec = null;

    if (manualIn.length) {
      let totBtuSel = 0, totKwSel = 0, allClr = true;
      const clrNotes = [];
      manualIn.forEach(mu => {
        const p = prodsList.find(x => x.id === mu.prod_id || x.model === mu.model);
        if (!p) return;
        const mq = Math.max(1, Number(mu.qty) || 1);
        const mh = String(p.dimensions || "").match(/(\d{3})\s*[xX×]/);
        const uh = mh ? parseInt(mh[1], 10) : 0;
        const reqPl = (p.duct || p.ceiling_opening) ? (uh + 45) : 0;
        let cOk = true, cNote = "Đạt";
        if (reqPl > 0 && plenum_mm > 0 && plenum_mm < reqPl) {
          cOk = false; allClr = false; cNote = `Trần ${plenum_mm}mm < ${reqPl}mm (${p.model})`; clrNotes.push(cNote);
        }
        totBtuSel += (p.cooling_btu || 0) * mq;
        totKwSel += (p.cooling_kw || 0) * mq;
        assigned_units.push({
          prod_id: p.id, model: p.model, name: p.name, qty: mq,
          cooling_btu: p.cooling_btu || 0, cooling_kw: p.cooling_kw || 0,
          total_btu: (p.cooling_btu || 0) * mq, price: p.price || 0,
          unit_height_mm: uh, req_plenum_mm: reqPl, clearance_ok: cOk, clearance_note: cNote
        });
      });
      if (assigned_units.length) {
        const covPct = Math.round((totBtuSel / Math.max(1, qBtu)) * 100);
        const lbl = assigned_units.map(u => `${u.qty}× ${u.model}`).join(" + ");
        rec = {
          prod_id: assigned_units[0].prod_id, model: lbl,
          name: `Chọn tay (${assigned_units.reduce((s, u) => s + u.qty, 0)} dàn)`,
          qty: 1, unit_count: assigned_units.reduce((s, u) => s + u.qty, 0),
          cooling_btu: Math.round(totBtuSel), cooling_kw: Math.round(totKwSel * 100) / 100,
          total_btu: Math.round(totBtuSel), coverage_pct: covPct, selection_mode: "MANUAL",
          clearance_ok: allClr, clearance_note: clrNotes.length ? clrNotes.join("; ") : `Đạt (${plenum_mm}mm)`
        };
      }
    }
    if (!rec) {
      const recSingle = _recommendUnitJS(qBtu / splitCnt, r.prefer_type || prefer_system, plenum_mm);
      const totQty = (recSingle.qty || 1) * splitCnt;
      const totBtuAuto = (recSingle.cooling_btu || 0) * totQty;
      const covPct = Math.round((totBtuAuto / Math.max(1, qBtu)) * 100);
      assigned_units = [{
        prod_id: recSingle.prod_id, model: recSingle.model, name: recSingle.name, qty: totQty,
        cooling_btu: recSingle.cooling_btu, cooling_kw: recSingle.cooling_kw,
        total_btu: totBtuAuto, price: recSingle.price || 0,
        unit_height_mm: recSingle.unit_height_mm, req_plenum_mm: recSingle.req_plenum_mm,
        clearance_ok: recSingle.clearance_ok, clearance_note: recSingle.clearance_note
      }];
      rec = Object.assign({}, recSingle, {
        qty: totQty, unit_count: totQty, total_btu: totBtuAuto,
        coverage_pct: covPct, selection_mode: splitCnt > 1 ? "AUTO_SPLIT" : "AUTO"
      });
    }
    if (!rec.clearance_ok) clearance_warnings.push(`${r.name} (${rec.model}): ${rec.clearance_note}`);

    const comps = {
      wall: Math.round(qWall * sfMult), glass_rad: Math.round(qGlassRad * sfMult),
      glass_cond: Math.round(qGlassCond * sfMult), door: Math.round(qDoorCond * sfMult),
      roof_floor: Math.round(qRF * sfMult), partition: Math.round(qPart * sfMult),
      people: Math.round((qPplS + qPplL) * sfMult), light_equip: Math.round((qLight + qEquipS + qEqItemL) * sfMult),
      fresh_air: Math.round((qOaS + qOaL) * sfMult), infiltration: Math.round((qInfS + qInfL) * sfMult)
    };
    Object.keys(compSums).forEach(k => compSums[k] += comps[k]);

    const winSum = winArea > 0 ? `${winQty} cửa sổ (${winW.toFixed(1)}×${winH.toFixed(1)}m)` : (glassArea > 0 ? `Kính ${glassArea.toFixed(1)}m²` : "Không cửa sổ");
    const doorSum = doorArea > 0 ? `${doorQty} cửa ${doorW.toFixed(1)}×${doorH.toFixed(1)}m (${doorMat.name.split("(")[0].trim()})` : "—";

    roomsOut.push({
      index: idx + 1, name: r.name || `Phòng ${idx + 1}`, floor: r.floor || "Tầng 1",
      room_type: r.room_type || "LIVING", room_type_name: preset.name,
      area: Math.round(area * 100) / 100, h_concrete: h_bt, h_ceiling: h_tc, plenum_mm,
      orientation: oriKey, orientation_label: ori.label,
      wall_name: wall.name, glass_name: glass.name, roof_name: roof.name,
      glass_area: Math.round(totGlazed * 10) / 10, window_summary: winSum, door_summary: doorSum,
      equip_items_summary: eqLabels.length ? eqLabels.join(", ") : `Định mức ${eqWm2} W/m²`,
      wwr_pct: Math.round(wwrPct * 10) / 10,
      people: ppl, t_in, rh_in, oa_m3h: Math.round(oaM3h), supply_m3h: Math.round(supM3h),
      q_sens_w: Math.round(qSens), q_lat_w: Math.round(qLat), q_total_w: Math.round(qTot),
      q_kw: Math.round(qKw * 100) / 100, q_btu: Math.round(qBtu), q_rt: Math.round((qKw / 3.517) * 100) / 100,
      w_per_m2: Math.round((qTot / area) * 10) / 10, shr: Math.round((qSens / Math.max(1, qTot)) * 100) / 100,
      qcvn_ok: wallOk && glassOk, wall_qcvn_ok: wallOk, glass_qcvn_ok: glassOk, max_shgc_allowed: maxShgc,
      components_w: comps, recommended_unit: rec, assigned_units
    });
    tot_area += area; tot_sens += qSens; tot_lat += qLat; tot_q += qTot; tot_oa += oaM3h; tot_sup += supM3h; tot_ppl += ppl;
  });

  const divKw = (tot_q / 1000.0) * diversity;
  const divBtu = divKw * 3412.14;
  const prods = (typeof DB !== "undefined" && DB.products) ? DB.products : [];
  const outCat = prefer_system.startsWith("VRV") ? "VRV_H_OUT" : (prefer_system.startsWith("MULTI") ? "MULTI_OUT" : "VRV_H_OUT");
  let outCands = prods.filter(p => p.category_id === outCat && p.cooling_btu > 0);
  if (prefer_system.startsWith("VRV") && divBtu <= 82000) {
    outCands = outCands.concat(prods.filter(p => p.category_id === "VRV_S_OUT" && p.cooling_btu > 0));
  }
  outCands.sort((a, b) => a.cooling_btu - b.cooling_btu);
  const outRec = outCands.find(p => p.cooling_btu >= divBtu * 0.90) || outCands[outCands.length - 1] || null;
  const vamCands = prods.filter(p => p.category_id === "VRV_HRV");
  const hrvRec = vamCands.find(p => (parseInt(p.hp, 10) || 0) >= tot_oa * 0.9) || vamCands[vamCands.length - 1] || null;

  return {
    ok: true,
    design_basis: {
      standard: "TCVN 5687:2024 & QCVN 09:2017/BXD (CLTD/CLF)",
      city_key: payload.city, city_name: city.name, grade: payload.grade,
      t_out, twb_out, rh_out: Math.round(rh_out * 10) / 10,
      w_out_g_kg: Math.round(w_out * 100000) / 100, h_out_kj_kg: Math.round(h_out * 10) / 10,
      t_out_win, safety_pct, diversity_factor: diversity, use_hrv, hrv_efficiency: Math.round(hrv_eff * 100)
    },
    summary: {
      room_count: roomsOut.length, total_area_m2: Math.round(tot_area * 10) / 10, total_people: tot_ppl,
      total_sens_kw: Math.round(tot_sens / 10) / 100, total_lat_kw: Math.round(tot_lat / 10) / 100,
      total_cooling_kw: Math.round(tot_q / 10) / 100, total_cooling_btu: Math.round((tot_q / 1000) * 3412.14),
      total_cooling_rt: Math.round(((tot_q / 1000) / 3.517) * 100) / 100,
      avg_w_per_m2: Math.round((tot_q / Math.max(1, tot_area)) * 10) / 10,
      shr: Math.round((tot_sens / Math.max(1, tot_q)) * 100) / 100,
      diversified_kw: Math.round(divKw * 100) / 100, diversified_btu: Math.round(divBtu),
      total_oa_m3h: Math.round(tot_oa), total_supply_m3h: Math.round(tot_sup),
      components_w: compSums,
      outdoor_rec: outRec ? { prod_id: outRec.id, model: outRec.model, name: outRec.name, cooling_btu: outRec.cooling_btu, cooling_kw: outRec.cooling_kw, price: outRec.price } : null,
      hrv_rec: hrvRec ? { prod_id: hrvRec.id, model: hrvRec.model, name: hrvRec.name, hp: hrvRec.hp } : null
    },
    rooms: roomsOut, qcvn_warnings, clearance_warnings
  };
}

function calcDuctOfflineJS(inp) {
  const prods = (typeof DB !== "undefined" && DB.products) ? DB.products : [];
  const prod = prods.find(p => p.id === inp.model_id || p.model === inp.model_id);
  const STD_RECT = [150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 900, 1000, 1100, 1200];
  const STD_RND = [100, 125, 150, 160, 200, 250, 300, 315, 350, 400, 450, 500, 560, 630];
  const hyd = (q, shape, w, h, d, rough) => {
    const qm3s = Math.max(0.001, q / 3600);
    let area, de;
    if (shape === "round") { const dm = Math.max(0.08, d / 1000); area = Math.PI * dm * dm / 4; de = dm; }
    else { const a = Math.max(0.1, w / 1000), b = Math.max(0.1, h / 1000); area = a * b; de = 1.30 * Math.pow(a * b, 0.625) / Math.pow(a + b, 0.25); }
    const v = qm3s / area, re = (v * de) / 1.51e-5;
    let f = re <= 2300 ? 64 / Math.max(100, re) : 0.11 * Math.pow((rough / 1000) / de + 68 / re, 0.25);
    if (re > 2300 && f < 0.018) f = 0.85 * f + 0.0028;
    const pd = 0.6 * v * v, dpm = f * (1 / de) * pd;
    return { area_m2: +area.toFixed(4), de_mm: +(de * 1000).toFixed(1), velocity_ms: +v.toFixed(2), pd_pa: +pd.toFixed(2), dp_pa_m: +dpm.toFixed(2) };
  };
  const autoSize = (q, tdp, mv, maxH, rough) => {
    let bestR = STD_RND[STD_RND.length - 1];
    for (const d of STD_RND) { const r = hyd(q, "round", 0, 0, d, rough); if (r.dp_pa_m <= tdp && r.velocity_ms <= mv) { bestR = d; break; } }
    let bestRect = [400, Math.min(250, maxH)], bestA = 1e9;
    for (const h of STD_RECT.filter(x => x <= maxH)) {
      for (const w of STD_RECT) {
        if (w < h || w > h * 4) continue;
        const r = hyd(q, "rect", w, h, 0, rough);
        if (r.dp_pa_m <= tdp && r.velocity_ms <= mv) { if (w * h < bestA) { bestA = w * h; bestRect = [w, h]; } break; }
      }
    }
    return { round_mm: bestR, rect_w_mm: bestRect[0], rect_h_mm: bestRect[1], rect_hyd: hyd(q, "rect", bestRect[0], bestRect[1], 0, rough) };
  };
  const qTot = Number(inp.airflow_m3h) || 1200;
  const espR = Number(inp.esp_rated_pa) || 50, espM = Number(inp.esp_max_pa) || 150;
  const nBr = Math.max(1, Number(inp.num_branches) || 3), qBr = qTot / nBr;
  const maxH = Number(inp.max_h_mm) || 250, tdp = Number(inp.target_dp) || 1.0;
  const mainA = autoSize(qTot, tdp, 6.5, maxH, 0.09);
  const brA = autoSize(qBr, tdp, 4.5, Math.min(200, maxH), 0.09);
  const flexH = hyd(qBr, "round", 0, 0, brA.round_mm, 3.0);
  const retA = autoSize(qTot, 0.8, 4.5, maxH, 0.09);
  const dpM = mainA.rect_hyd.dp_pa_m * (Number(inp.main_len_m) || 0);
  const dpB = brA.rect_hyd.dp_pa_m * (Number(inp.branch_len_m) || 0);
  const dpF = flexH.dp_pa_m * (Number(inp.flex_len_m) || 0);
  const dpR = retA.rect_hyd.dp_pa_m * (Number(inp.return_len_m) || 0);
  const dpFit = (0.5 + 0.35 * (Number(inp.num_elbows) || 0) + 0.8 + 0.45) * mainA.rect_hyd.pd_pa;
  const dpTot = dpM + dpB + dpF + dpR + dpFit + 20.0;
  const sheetM2 = 2 * ((mainA.rect_w_mm + mainA.rect_h_mm) / 1000) * (Number(inp.main_len_m) || 0) +
                  2 * ((brA.rect_w_mm + brA.rect_h_mm) / 1000) * (Number(inp.branch_len_m) || 0) * nBr +
                  2 * ((retA.rect_w_mm + retA.rect_h_mm) / 1000) * (Number(inp.return_len_m) || 0);
  const supLen = Math.max(600, Math.ceil(((qBr / (3600 * 2.5)) / 0.65 / 0.15) * 10) * 100);
  const retLen = Math.max(800, Math.ceil(((qTot / (3600 * 2.0)) / 0.70 / 0.20) * 10) * 100);
  const esp_status = dpTot <= espR ? "OK_RATED" : (dpTot <= espM ? "OK_MAX" : "EXCEED_ESP");
  return {
    ok: true, model: prod ? prod.model : "Tùy chỉnh", model_name: prod ? prod.name : "", duct_excel: prod ? prod.duct : null,
    airflow_m3h: Math.round(qTot), branch_airflow_m3h: Math.round(qBr), num_branches: nBr, esp_rated_pa: espR, esp_max_pa: espM,
    main_duct: { w_mm: mainA.rect_w_mm, h_mm: mainA.rect_h_mm, round_equiv_mm: mainA.round_mm, hyd: mainA.rect_hyd, dp_pa: +dpM.toFixed(1) },
    branch_duct: { w_mm: brA.rect_w_mm, h_mm: brA.rect_h_mm, round_mm: brA.round_mm, hyd: brA.rect_hyd, dp_pa: +dpB.toFixed(1) },
    flex_duct: { dia_mm: brA.round_mm, len_m: Number(inp.flex_len_m) || 0, hyd: flexH, dp_pa: +dpF.toFixed(1) },
    return_duct: { w_mm: retA.rect_w_mm, h_mm: retA.rect_h_mm, hyd: retA.rect_hyd, dp_pa: +dpR.toFixed(1) },
    grilles: {
      supply_rec: `${nBr} cửa cấp Linear Slot / Nan bầu dục ${supLen}×150 mm (${Math.round(qBr)} m³/h/cửa)`,
      return_rec: `1 cửa hồi có lưới lọc bụi ${retLen}×200 mm (${Math.round(qTot)} m³/h)`,
      vcd_rec: `${nBr} van chỉnh gió VCD Ø${brA.round_mm}`
    },
    pressure_breakdown: { main_straight_pa: +dpM.toFixed(1), branch_straight_pa: +dpB.toFixed(1), flex_pa: +dpF.toFixed(1), return_pa: +dpR.toFixed(1), fittings_pa: +dpFit.toFixed(1), grilles_pa: 20.0, total_pa: +dpTot.toFixed(1), esp_margin_pa: +(espM - dpTot).toFixed(1) },
    sheet_metal_m2: +sheetM2.toFixed(2), flex_total_m: +((Number(inp.flex_len_m) || 0) * nBr).toFixed(1),
    esp_status,
    esp_verdict: esp_status === "OK_RATED" ? `ĐẠT CHUẨN — Tổn thất (${dpTot.toFixed(1)} Pa) ≤ ESP ĐM (${espR} Pa).`
      : (esp_status === "OK_MAX" ? `ĐẠT KHI TĂNG CẤP ESP — Tổn thất (${dpTot.toFixed(1)} Pa) trong giới hạn Max ${espM} Pa.`
      : `CẢNH BÁO THIẾU CỘT ÁP — Tổn thất (${dpTot.toFixed(1)} Pa) > ESP Max (${espM} Pa)!`),
    noise_status: mainA.rect_hyd.velocity_ms <= 5.5 && flexH.velocity_ms <= 3.8 ? "ÊM (Đạt chuẩn phòng ngủ/VP)" : (mainA.rect_hyd.velocity_ms <= 7.0 ? "TRUNG BÌNH (Phù hợp sảnh/TM)" : "ỒN CAO (Cần tăng tiết diện)")
  };
}

function calcCoolpackOfflineJS(inp) {
  const ANT = { R410A: { A: 4.89271, B: 1162.235, C: 18.152, gwp: 2088, safety: "A1" }, R32: { A: 4.81045, B: 1099.401, C: 8.726, gwp: 675, safety: "A2L" } };
  const CHG = { "6.4": 0.022, "9.5": 0.059, "12.7": 0.120, "15.9": 0.170, "19.1": 0.250 };
  const ref = inp.refrigerant || "R410A", c = ANT[ref] || ANT.R410A;
  const pS = inp.pressure_unit === "psi" ? Number(inp.p_suction) * 0.0689476 : Number(inp.p_suction);
  const pD = inp.pressure_unit === "psi" ? Number(inp.p_discharge) * 0.0689476 : Number(inp.p_discharge);
  const tSat = (pg) => c.B / (c.A - Math.log10(Math.max(1.2, pg + 1.01325))) - c.C - 273.15;
  const te = tSat(pS), tc = tSat(pD);
  const sh = Number(inp.t_suction_meas) - te, sc = tc - Number(inp.t_liquid_meas);
  const cop = Math.min(5.8, Math.max(1.8, ((te + 273.15) / Math.max(5, tc - te)) * 0.56));
  const L = Math.max(5, Number(inp.pipe_length_m) || 35), H = Math.max(0, Number(inp.height_diff_m) || 12);
  const der = Math.max(0.75, Math.min(1.0, 1.0 - Math.max(0, (L - 7.5) * 0.00135) - H * 0.0012));
  const rKw = Number(inp.rated_kw) || 40, aKw = rKw * der;
  const rate = CHG[String(inp.liquid_pipe_od)] || 0.059;
  const exKg = Math.max(0, (L - (Number(inp.precharged_m) || 0)) * rate);
  return {
    ok: true, refrigerant: ref, gwp: c.gwp, safety_class: c.safety,
    p_suction_bar: +pS.toFixed(2), p_suction_psi: +(pS * 14.5038).toFixed(1),
    p_discharge_bar: +pD.toFixed(2), p_discharge_psi: +(pD * 14.5038).toFixed(1),
    t_evap_c: +te.toFixed(1), t_cond_c: +tc.toFixed(1), superheat_k: +sh.toFixed(1), subcooling_k: +sc.toFixed(1),
    sh_status: sh < 3 ? "LOW" : (sh <= 10 ? "OK" : "HIGH"),
    sh_diag: sh < 3 ? "NGUY HIỂM — Quá nhiệt < 3K: Nguy cơ ngập dịch máy nén!" : (sh <= 10 ? "ĐẠT CHUẨN (5–9 K): Dàn bay hơi làm việc tối ưu." : "CẢNH BÁO — Quá nhiệt > 10K: Dấu hiệu thiếu gas hoặc nghẹt EEV."),
    sc_status: sc < 2.5 ? "LOW" : (sc <= 10 ? "OK" : "HIGH"),
    sc_diag: sc < 2.5 ? "CẢNH BÁO — Quá lạnh < 3K: Thiếu gas nạp hoặc dàn nóng giải nhiệt kém." : (sc <= 10 ? "ĐẠT CHUẨN (4–8 K): Cấp lỏng ổn định vào van tiết lưu." : "LƯU Ý — Quá lạnh > 10K: Có thể dư môi chất lạnh."),
    cop_est: +cop.toFixed(2),
    piping: { eq_len_m: L, height_diff_m: H, derate_factor: +der.toFixed(3), loss_pct: +((1 - der) * 100).toFixed(1), rated_kw: rKw, actual_kw: +aKw.toFixed(2), actual_btu: Math.round(aKw * 3412.14), liquid_pipe_od: String(inp.liquid_pipe_od), charge_rate_kg_m: rate, extra_charge_kg: +exKg.toFixed(2) }
  };
}

function buildOfflineAiReportJS(calc, duct) {
  const db = calc.design_basis, sm = calc.summary, cp = sm.components_w || {};
  const tot = Math.max(1, Object.values(cp).reduce((a, b) => a + b, 0));
  const pG = ((cp.glass_rad + cp.glass_cond) / tot * 100).toFixed(1);
  const pW = ((cp.wall + cp.roof_floor + cp.partition) / tot * 100).toFixed(1);
  const pO = ((cp.fresh_air + cp.infiltration) / tot * 100).toFixed(1);
  const pI = ((cp.people + cp.light_equip) / tot * 100).toFixed(1);
  const lines = [
    `1. TỔNG QUAN TẢI NHIỆT CÔNG TRÌNH (${db.city_name} — Cấp ${db.grade} TCVN 5687:2024):`,
    `   • Tổng diện tích điều hòa: ${sm.total_area_m2} m² (${sm.room_count} phòng) — Tổng tải lạnh tức thời: ${sm.total_cooling_kw} kW (${formatNum(sm.total_cooling_btu)} Btu/h ≈ ${sm.total_cooling_rt} RT).`,
    `   • Phụ tải trung bình: ${sm.avg_w_per_m2} W/m² | SHR = ${sm.shr} | Tải chọn dàn nóng (đồng thời ${db.diversity_factor}): ${sm.diversified_kw} kW (${formatNum(sm.diversified_btu)} Btu/h).`,
    `   • Cơ cấu tải nhiệt: Kính & bức xạ ${pG}% | Tường/Mái/Sàn ${pW}% | Gió tươi & khí lọt ${pO}% | Nội sinh (người/đèn/TB) ${pI}%.`,
    "",
    "2. KIỂM TRA VẬT LIỆU BAO CHE THEO QCVN 09:2017/BXD:",
    ...(calc.qcvn_warnings.length ? calc.qcvn_warnings.map(w => `   • [Lưu ý QCVN 09] ${w}`) : ["   • Toàn bộ tường bao & kính ĐẠT chuẩn nhiệt trở R0 ≥ 0.56 m²K/W và SHGC theo QCVN 09:2017/BXD."]),
    "",
    "3. KIỂM TRA KHOẢNG TRẦN THẠCH CAO (H_BT - H_TC) & PHƯƠNG ÁN DAIKIN:",
    ...(calc.clearance_warnings.length ? calc.clearance_warnings.map(w => `   • [Cảnh báo trần] ${w}`) : ["   • Toàn bộ các phòng đạt khoảng hở trần thạch cao để lắp dàn lạnh & thoát nước ngưng."]),
    sm.outdoor_rec ? `   • Tổ hợp dàn nóng đề xuất: ${sm.outdoor_rec.model} (${sm.outdoor_rec.cooling_kw} kW) | Gió tươi: ${sm.total_oa_m3h} m³/h ${sm.hrv_rec ? "(HRV: " + sm.hrv_rec.model + ")" : ""}.` : ""
  ];
  if (duct && duct.ok) {
    lines.push("", `4. ĐÁNH GIÁ ỐNG GIÓ DAIKIN DUCT CHECKER (${duct.model}):`, `   • Ống chính ${duct.main_duct.w_mm}×${duct.main_duct.h_mm}mm (v=${duct.main_duct.hyd.velocity_ms} m/s) — ${duct.esp_verdict}`);
  }
  return lines.filter(x => x !== null).join("\n");
}

/* ---------------- INITIALIZE 4-TAB HVAC ENGINEERING SUITE ---------------- */
async function initHvacPro() {
  if (!_hvacProInitialized) {
    loadHvacAndAiState();
    populateHvacSelectOptions();
    populateDuctModelDropdown();
    populateCoolpackModelDropdown();
    syncHvacControlsFromState();
    switchHeatLoadMode(HVAC_STATE.workMode || "offline");
    updateAiModeBadge();
    renderAiLoginModal();
    _hvacProInitialized = true;
  }
  await recalcProjectHeatLoad();
  await runDuctCheckerCalc();
  await runCoolpackCalc();
}

function switchHeatLoadMode(mode) {
  HVAC_STATE.workMode = mode === "ai" ? "ai" : "offline";
  document.querySelectorAll("#hv-mode-switch .hv-mode-btn").forEach(b => {
    b.classList.toggle("active", b.getAttribute("data-hmode") === HVAC_STATE.workMode);
  });
  const offEl = document.getElementById("hv-mode-offline");
  const aiEl = document.getElementById("hv-mode-ai");
  if (offEl) offEl.style.display = HVAC_STATE.workMode === "offline" ? "block" : "none";
  if (aiEl) aiEl.style.display = HVAC_STATE.workMode === "ai" ? "block" : "none";
  if (HVAC_STATE.workMode === "ai") {
    renderAiLoginPanelInto("hv-ai-inline-login", true);
    renderTakeoffResults();
  }
}

function onCityOrGradeChange() {
  const cityKey = document.getElementById("hv-city")?.value || "HANOI";
  const grade = document.getElementById("hv-grade")?.value || "I";
  const clim = (HVAC_META.cities[cityKey] || HVAC_META.cities.HANOI)[grade] || HVAC_META.cities.HANOI.I;
  const tdbEl = document.getElementById("hv-tout");
  const twbEl = document.getElementById("hv-twbout");
  if (tdbEl) tdbEl.value = clim.tdb;
  if (twbEl) twbEl.value = clim.twb;
  HVAC_STATE.t_out_override = "";
  HVAC_STATE.twb_out_override = "";
  recalcProjectHeatLoad();
}

function onCustomOutdoorTempChange() {
  HVAC_STATE.t_out_override = document.getElementById("hv-tout")?.value || "";
  HVAC_STATE.twb_out_override = document.getElementById("hv-twbout")?.value || "";
  recalcProjectHeatLoad();
}

function switchHvacTab(tabKey) {
  HVAC_STATE.activeTab = tabKey;
  document.querySelectorAll("#hvac-subtabs .hvac-tab-btn").forEach(b => {
    b.classList.toggle("active", b.getAttribute("data-htab") === tabKey);
  });
  document.querySelectorAll(".hvac-tab-pane").forEach(p => {
    p.classList.toggle("active", p.id === "htab-" + tabKey);
  });
  if (tabKey === "ductchecker") runDuctCheckerCalc();
  if (tabKey === "coolpack") runCoolpackCalc();
}

function populateHvacSelectOptions() {
  const citySel = document.getElementById("hv-city");
  if (citySel) {
    citySel.innerHTML = Object.entries(HVAC_META.cities)
      .map(([k, v]) => `<option value="${k}">${v.name} (Cấp I: ${v.I.tdb}°C/${v.I.twb}°C)</option>`).join("");
  }
}

function syncHvacControlsFromState() {
  const setV = (id, v) => { const el = document.getElementById(id); if (el) el.value = v; };
  setV("hv-city", HVAC_STATE.city);
  setV("hv-grade", HVAC_STATE.grade);
  const clim = (HVAC_META.cities[HVAC_STATE.city] || HVAC_META.cities.HANOI)[HVAC_STATE.grade] || HVAC_META.cities.HANOI.I;
  setV("hv-tout", HVAC_STATE.t_out_override || clim.tdb);
  setV("hv-twbout", HVAC_STATE.twb_out_override || clim.twb);
  setV("hv-safety", HVAC_STATE.safety_pct);
  setV("hv-diversity", HVAC_STATE.diversity_factor);
  setV("hv-system", HVAC_STATE.prefer_system);
  const hrvEl = document.getElementById("hv-use-hrv");
  if (hrvEl) hrvEl.checked = Boolean(HVAC_STATE.use_hrv);
  setV("hv-hrv-eff", Math.round((HVAC_STATE.hrv_efficiency ?? 0.70) * 100));

  // Sync Duct Checker inputs
  const di = HVAC_STATE.ductInput;
  setV("dc-model", di.model_id);
  setV("dc-airflow", di.airflow_m3h);
  setV("dc-esp-rated", di.esp_rated_pa);
  setV("dc-esp-max", di.esp_max_pa);
  setV("dc-branches", di.num_branches);
  setV("dc-main-len", di.main_len_m);
  setV("dc-branch-len", di.branch_len_m);
  setV("dc-flex-len", di.flex_len_m);
  setV("dc-elbows", di.num_elbows);
  setV("dc-return-len", di.return_len_m);
  setV("dc-max-h", di.max_h_mm);
  setV("dc-target-dp", di.target_dp);

  // Sync CoolPack inputs
  const ci = HVAC_STATE.coolpackInput;
  setV("cp-ref", ci.refrigerant);
  setV("cp-punit", ci.pressure_unit);
  setV("cp-psuc", ci.p_suction);
  setV("cp-pdis", ci.p_discharge);
  setV("cp-tsuc", ci.t_suction_meas);
  setV("cp-tliq", ci.t_liquid_meas);
  setV("cp-len", ci.pipe_length_m);
  setV("cp-height", ci.height_diff_m);
  setV("cp-rated-kw", ci.rated_kw);
  setV("cp-liq-od", ci.liquid_pipe_od);
  setV("cp-precharge", ci.precharged_m);
}

/* ---------------- TAB 1: HEAT LOAD CALCULATION & RENDERING ---------------- */
async function recalcProjectHeatLoad() {
  HVAC_STATE.city = document.getElementById("hv-city")?.value || HVAC_STATE.city;
  HVAC_STATE.grade = document.getElementById("hv-grade")?.value || HVAC_STATE.grade;
  HVAC_STATE.safety_pct = Number(document.getElementById("hv-safety")?.value ?? 10);
  HVAC_STATE.diversity_factor = Number(document.getElementById("hv-diversity")?.value ?? 0.85);
  HVAC_STATE.prefer_system = document.getElementById("hv-system")?.value || "VRV_DUCT";
  HVAC_STATE.use_hrv = Boolean(document.getElementById("hv-use-hrv")?.checked);
  const hrvPct = Number(document.getElementById("hv-hrv-eff")?.value ?? 70);
  HVAC_STATE.hrv_efficiency = Math.max(0.3, Math.min(0.9, hrvPct / 100.0));
  saveHvacState();

  const payload = {
    city: HVAC_STATE.city,
    grade: HVAC_STATE.grade,
    t_out_override: HVAC_STATE.t_out_override ? Number(HVAC_STATE.t_out_override) : null,
    twb_out_override: HVAC_STATE.twb_out_override ? Number(HVAC_STATE.twb_out_override) : null,
    safety_pct: HVAC_STATE.safety_pct,
    diversity_factor: HVAC_STATE.diversity_factor,
    use_hrv: HVAC_STATE.use_hrv,
    hrv_efficiency: HVAC_STATE.hrv_efficiency,
    prefer_system: HVAC_STATE.prefer_system,
    rooms: HVAC_STATE.rooms
  };

  let res = null;
  try {
    const resp = await fetch("/api/hvac/calc_project", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (resp.ok) res = await resp.json();
  } catch (e) {}

  if (!res || !res.ok) {
    res = calcHeatLoadOfflineJS(payload);
  }
  HVAC_STATE.lastCalc = res;
  if (!HVAC_STATE.aiReportText || HVAC_STATE.aiReportMode === "OFFLINE_EXPERT") {
    HVAC_STATE.aiReportText = buildOfflineAiReportJS(res, HVAC_STATE.lastDuct);
    HVAC_STATE.aiReportMode = "OFFLINE_EXPERT";
  }
  renderHeatLoadDashboard(res);
}

function renderHeatLoadDashboard(res) {
  const db = res.design_basis || {};
  const sm = res.summary || {};

  // Climate strip
  const climStrip = document.getElementById("hv-climate-strip");
  if (climStrip) {
    climStrip.innerHTML = `
      <span>🌡️ <strong>${db.city_name}</strong> (TCVN 5687:2024 Cấp ${db.grade}):</span>
      <span>Nhiệt độ khô <strong>${db.t_out}°C</strong></span>
      <span>• Nhiệt độ ướt <strong>${db.twb_out}°C</strong></span>
      <span>• Độ ẩm <strong>${db.rh_out}%</strong></span>
      <span>• Entanpi <strong>${db.h_out_kj_kg} kJ/kg</strong></span>
      <span>• Mùa đông <strong>${db.t_out_win}°C</strong></span>
    `;
  }

  // 4 KPI Cards
  const kpiEl = document.getElementById("hv-kpi-grid");
  if (kpiEl) {
    const outRec = sm.outdoor_rec;
    const hrvRec = sm.hrv_rec;
    kpiEl.innerHTML = `
      <div class="hvac-kpi-card blue">
        <div class="kpi-lbl">TỔNG DIỆN TÍCH & QUY MÔ</div>
        <div class="kpi-val">${sm.total_area_m2} m²</div>
        <div class="kpi-sub">${sm.room_count} phòng • ${sm.total_people} người sử dụng</div>
      </div>
      <div class="hvac-kpi-card red">
        <div class="kpi-lbl">TỔNG TẢI LẠNH TỨC THỜI</div>
        <div class="kpi-val">${sm.total_cooling_kw} kW</div>
        <div class="kpi-sub">${formatNum(sm.total_cooling_btu)} Btu/h ≈ <strong>${sm.total_cooling_rt} RT</strong> (Hiện ${sm.total_sens_kw} / Ẩn ${sm.total_lat_kw} kW)</div>
      </div>
      <div class="hvac-kpi-card blue">
        <div class="kpi-lbl">TẢI CHỌN DÀN NÓNG (ĐỒNG THỜI ×${db.diversity_factor})</div>
        <div class="kpi-val">${sm.diversified_kw} kW</div>
        <div class="kpi-sub">${outRec ? `Đề xuất: <strong>${outRec.model}</strong> (${outRec.cooling_kw} kW)` : `${formatNum(sm.diversified_btu)} Btu/h`}</div>
      </div>
      <div class="hvac-kpi-card teal">
        <div class="kpi-lbl">CHỈ SỐ PHỤ TẢI & GIÓ TƯƠI TCVN</div>
        <div class="kpi-val">${sm.avg_w_per_m2} W/m²</div>
        <div class="kpi-sub">SHR = ${sm.shr} • Gió tươi <strong>${formatNum(sm.total_oa_m3h)} m³/h</strong>${hrvRec ? ` (${hrvRec.model})` : ""}</div>
      </div>
    `;
  }

  // Vector Component Breakdown Chart
  const chartEl = document.getElementById("hv-breakdown-chart");
  if (chartEl && sm.components_w) {
    const cp = sm.components_w;
    const rows = [
      { label: "Bức xạ & truyền nhiệt Kính / Cửa sổ", val: (cp.glass_rad || 0) + (cp.glass_cond || 0), color: "#991B1B" },
      { label: "Tường bao, Cửa chính, Mái & Sàn", val: (cp.wall || 0) + (cp.door || 0) + (cp.roof_floor || 0) + (cp.partition || 0), color: "#005A8D" },
      { label: "Gió tươi (TCVN 5687) & Khí lọt cửa", val: (cp.fresh_air || 0) + (cp.infiltration || 0), color: "#0D9488" },
      { label: "Tỏa nhiệt Người trong phòng", val: cp.people || 0, color: "#0077B6" },
      { label: "Chiếu sáng & Thiết bị trong phòng", val: cp.light_equip || 0, color: "#475569" }
    ];
    const totW = Math.max(1, rows.reduce((s, x) => s + x.val, 0));
    const maxW = Math.max(1, ...rows.map(x => x.val));
    chartEl.innerHTML = rows.map(it => {
      const pct = (it.val / totW * 100).toFixed(1);
      const wPct = Math.max(2, (it.val / maxW * 100)).toFixed(1);
      return `
        <div class="hvac-bar-row">
          <div class="hvac-bar-lbl">${it.label}</div>
          <div class="hvac-bar-track">
            <div class="hvac-bar-fill" style="width:${wPct}%;background:${it.color};"></div>
          </div>
          <div class="hvac-bar-val"><strong>${(it.val / 1000).toFixed(2)} kW</strong> (${pct}%)</div>
        </div>
      `;
    }).join("");
  }

  // QCVN 09 & Ceiling Plenum Diagnostics
  const alertEl = document.getElementById("hv-alerts-box");
  if (alertEl) {
    const qW = res.qcvn_warnings || [];
    const cW = res.clearance_warnings || [];
    if (!qW.length && !cW.length) {
      alertEl.innerHTML = `
        <div class="hvac-badge-ok">
          ✅ <strong>ĐẠT CHUẨN QCVN 09:2017/BXD & KHOẢNG HỞ TRẦN THẠCH CAO:</strong> Toàn bộ kết cấu tường bao, kính chắn nắng và khoảng hở trần (H_BT − H_TC) đều đủ tiêu chuẩn lắp đặt Daikin!
        </div>
      `;
    } else {
      alertEl.innerHTML = `
        <div class="hvac-badge-warn">
          <div style="font-weight:700;color:#991B1B;margin-bottom:4px;">⚠️ CẢNH BÁO KỸ THUẬT QCVN 09:2017/BXD & KHOẢNG TRẦN THẠCH CAO (${qW.length + cW.length} lưu ý):</div>
          <ul style="margin:0;padding-left:18px;font-size:12px;line-height:1.55;">
            ${cW.map(w => `<li><strong>[Khoảng trần]</strong> ${w}</li>`).join("")}
            ${qW.map(w => `<li><strong>[QCVN 09]</strong> ${w}</li>`).join("")}
          </ul>
        </div>
      `;
    }
  }

  // Multi-Room Table
  const tbody = document.getElementById("hv-rooms-tbody");
  if (tbody) {
    if (!res.rooms || !res.rooms.length) {
      tbody.innerHTML = `<tr><td colspan="10" style="text-align:center;padding:28px;color:#64748B;">Chưa có phòng nào. Bấm <strong>➕ Thêm phòng</strong> hoặc sang Tab <strong>📄 Bóc Tách PDF/CAD AI</strong>!</td></tr>`;
    } else {
      tbody.innerHTML = res.rooms.map((rm, idx) => {
        const rec = rm.recommended_unit || {};
        const assigned = Array.isArray(rm.assigned_units) && rm.assigned_units.length ? rm.assigned_units : [rec];
        const unitsHtml = assigned.map(u => {
          const qPfx = (u.qty > 1 || assigned.length > 1) ? `<span style="color:#991B1B;font-weight:700;">${u.qty}×</span> ` : "";
          return `<div style="font-weight:700;color:#005A8D;cursor:pointer;line-height:1.35;" onclick="if('${u.prod_id}')openProductModal('${u.prod_id}')">${qPfx}${u.model}</div>`;
        }).join("");
        const covPct = rec.coverage_pct || Math.round(((rec.total_btu || rec.cooling_btu || 0) / Math.max(1, rm.q_btu)) * 100);
        const covBadge = covPct < 94
          ? `<span class="tag-alert">Thiếu tải ${covPct}%</span>`
          : `<span class="tag-pass">${rec.selection_mode === "MANUAL" ? "Chọn tay" : "TĐ"} ${covPct}%</span>`;
        const qBadge = rm.qcvn_ok
          ? `<span class="tag-pass">QCVN Đạt</span>`
          : `<span class="tag-alert">QCVN Lưu ý</span>`;
        const cBadge = rec.clearance_ok
          ? `<span class="tag-pass">Trần ${rm.plenum_mm}mm</span>`
          : `<span class="tag-alert">Thiếu trần ${rm.plenum_mm}mm!</span>`;
        return `
          <tr>
            <td style="text-align:center;font-weight:700;">${idx + 1}</td>
            <td>
              <div style="font-weight:700;color:#0F172A;">${rm.name}</div>
              <div style="font-size:11px;color:#475569;">${rm.floor} • ${rm.room_type_name} (${rm.t_in}°C / ${rm.rh_in}%)</div>
              <div style="font-size:10.5px;color:#64748B;">🧱 ${rm.wall_name.split("(")[0].trim()} • 🪟 ${rm.window_summary || ("Kính " + rm.glass_area + "m²")}</div>
              ${rm.door_summary && rm.door_summary !== "—" ? `<div style="font-size:10.5px;color:#005A8D;">🚪 ${rm.door_summary}</div>` : ""}
              ${rm.equip_items_summary && !rm.equip_items_summary.startsWith("Định mức") ? `<div style="font-size:10.5px;color:#991B1B;font-weight:600;">⚡ TB: ${rm.equip_items_summary}</div>` : ""}
            </td>
            <td style="text-align:center;font-weight:700;">${rm.area} m²</td>
            <td style="text-align:center;font-size:11.5px;">
              <strong>${rm.h_concrete}m</strong> / ${rm.h_ceiling}m<br/>
              <span style="color:#005A8D;font-weight:700;">Hở ${rm.plenum_mm}mm</span>
            </td>
            <td style="text-align:center;font-weight:700;color:#005A8D;">${rm.orientation}</td>
            <td style="text-align:right;font-size:12px;">
              Hiện: <strong>${(rm.q_sens_w / 1000).toFixed(2)}</strong><br/>
              Ẩn: ${(rm.q_lat_w / 1000).toFixed(2)}
            </td>
            <td style="text-align:right;">
              <strong style="color:#991B1B;font-size:13px;">${rm.q_kw} kW</strong><br/>
              <span style="font-size:11px;color:#475569;">${formatNum(rm.q_btu)} Btu/h</span>
            </td>
            <td style="text-align:center;font-size:11.5px;">
              <strong>${rm.w_per_m2} W/m²</strong><br/>
              <span style="color:#0D9488;">OA: ${rm.oa_m3h} m³/h</span>
            </td>
            <td>
              ${unitsHtml}
              <div style="display:flex;gap:3px;flex-wrap:wrap;margin-top:3px;">${covBadge} ${qBadge} ${cBadge}</div>
            </td>
            <td style="text-align:center;white-space:nowrap;">
              <button class="btn btn-sm btn-ice" title="Chỉnh sửa đầy đủ thông số phòng" onclick="openRoomEditorModal(${idx}, false)">✏️ Sửa</button>
              <button class="btn btn-sm btn-primary" title="Chọn 1 hoặc nhiều dàn lạnh cho phòng này" onclick="openRoomEditorModal(${idx}, true)">❄️ Dàn</button>
              <button class="btn btn-sm btn-outline" title="Kiểm tra ống gió" onclick="jumpToDuctChecker('${assigned[0]?.prod_id || ""}')">🌀</button>
              <button class="btn btn-sm btn-outline" style="color:#991B1B;" title="Xóa phòng" onclick="deleteHvacRoom(${idx})">✕</button>
            </td>
          </tr>
        `;
      }).join("");
    }
  }

  // Update AI Report Box
  const aiOut = document.getElementById("hv-ai-report-text");
  if (aiOut) {
    aiOut.textContent = HVAC_STATE.aiReportText || "Bấm nút '🤖 AI Phân Tích & Lập Báo Cáo Chuyên Sâu' để tạo báo cáo kỹ thuật TCVN 5687:2024.";
  }
}

/* ---------------- ROOM EDITOR MODAL (FULL OFFLINE PARAMS + MULTI-INDOOR UNITS PER ROOM) ---------------- */
function openRoomEditorModal(idx, focusUnits) {
  _editingRoomIdx = idx;
  const isNew = idx < 0 || idx >= HVAC_STATE.rooms.length;
  const rm = isNew ? {
    name: `Phòng mới #${HVAC_STATE.rooms.length + 1}`, floor: "Tầng 1", room_type: "BEDROOM",
    area: 25, h_concrete: 3.6, h_ceiling: 3.0, orientation: "W",
    t_in: "", rh_in: "", oa_override_m3h: "", ach_inf: "",
    wall_type: "BRICK_220_HOLLOW", ext_wall_len: 5.0, partition_len: 0,
    win_frame_type: "XINGFA_NO_TB", win_qty: 1, win_w: 1.6, win_h: 1.5, extra_glass_area: 0,
    glass_type: "DOUBLE_LOW_E", shading_type: "ROLLER",
    door_type: "WOOD_ENG_HDF", door_qty: 1, door_w: 0.95, door_h: 2.2, door_location: "INT",
    roof_type: "MID_FLOOR", floor_type: "MID_AC",
    people: "", light_w_m2: "", equip_w_m2: "", equipment_items: [],
    prefer_type: "", split_units: 1, selected_units: []
  } : Object.assign({}, HVAC_STATE.rooms[idx]);

  const prevCalcRoom = (!isNew && HVAC_STATE.lastCalc && HVAC_STATE.lastCalc.rooms) ? HVAC_STATE.lastCalc.rooms[idx] : null;
  _editingRoomEstBtu = prevCalcRoom ? prevCalcRoom.q_btu : Math.round((rm.area || 25) * 650);

  _editingEquipMap = {};
  (rm.equipment_items || []).forEach(ei => {
    if (ei && ei.id && Number(ei.qty) > 0) _editingEquipMap[ei.id] = Number(ei.qty);
  });
  _editingEquipTab = ["CLINIC", "HOSPITAL_WARD", "OPERATING_ROOM", "LAB_CLINIC"].includes(rm.room_type)
    ? "HOSPITAL" : (["OFFICE", "MEETING", "SHOWROOM"].includes(rm.room_type) ? "OFFICE" : "HOME");

  _editingUnitsList = Array.isArray(rm.selected_units) && rm.selected_units.length
    ? rm.selected_units.map(u => ({ prod_id: u.prod_id, qty: Math.max(1, Number(u.qty) || 1) }))
    : [];
  _editingUnitMode = _editingUnitsList.length > 0 ? "MANUAL" : "AUTO";

  const optHtml = (obj, sel) => Object.entries(obj).map(([k, v]) => `<option value="${k}" ${k === sel ? "selected" : ""}>${v.name || v.label}</option>`).join("");
  const plenumMm = Math.max(0, Math.round((Number(rm.h_concrete || 3.6) - Number(rm.h_ceiling || 3.0)) * 1000));
  const preset = HVAC_META.room_presets[rm.room_type] || HVAC_META.room_presets.LIVING;

  document.getElementById("emm-title").textContent = isNew
    ? "➕ Thêm Phòng Mới — Chọn Thông Số Chi Tiết & Nhiều Dàn Lạnh (TCVN 5687:2024)"
    : `✏️ Thông Số Chi Tiết & Phân Bổ Dàn Lạnh: ${rm.name}`;

  document.getElementById("emm-body").innerHTML = `
    <div style="display:grid;grid-template-columns:1.3fr 0.7fr 1.4fr;gap:10px;">
      <div class="form-group"><label>Tên phòng / Khu vực</label><input type="text" id="rm-name" value="${rm.name || ""}" /></div>
      <div class="form-group"><label>Tầng</label><input type="text" id="rm-floor" value="${rm.floor || "Tầng 1"}" /></div>
      <div class="form-group"><label>Công năng phòng (Gia đình / VP / Bệnh viện — TCVN 5687)</label><select id="rm-type">${optHtml(HVAC_META.room_presets, rm.room_type)}</select></div>
    </div>

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:10px;background:#EFF6FF;padding:10px 12px;border-radius:8px;border:1px solid #BFDBFE;">
      <div class="form-group"><label>Diện tích sàn (m²)</label><input type="number" id="rm-area" step="0.5" min="2" value="${rm.area}" /></div>
      <div class="form-group"><label>Cao sàn Bê tông H_BT (m)</label><input type="number" id="rm-hbt" step="0.05" min="2.4" value="${rm.h_concrete}" oninput="updateRoomPlenumPreview()" /></div>
      <div class="form-group"><label>Cao trần Thạch cao H_TC (m)</label><input type="number" id="rm-htc" step="0.05" min="2.0" value="${rm.h_ceiling}" oninput="updateRoomPlenumPreview()" /></div>
      <div class="form-group">
        <label>Khoảng hở kỹ thuật trần</label>
        <div id="rm-plenum-preview" style="padding:8px 10px;background:#FFFFFF;border:1px solid #93C5FD;border-radius:7px;font-weight:700;color:#005A8D;font-size:13px;">${plenumMm} mm</div>
      </div>
    </div>

    <!-- INDOOR DESIGN PARAMETERS (CRITICAL OFFLINE SETTINGS) -->
    <div class="rm-section-box">
      <div class="rm-section-title">🌡️ Thông Số Vi Khí Hậu Trong Phòng & Gió Tươi (TCVN 5687:2024)</div>
      <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;">
        <div class="form-group"><label>Nhiệt độ phòng (°C)</label><input type="number" id="rm-tin" step="0.5" min="16" max="30" value="${rm.t_in ?? ""}" placeholder="${preset.t_in}°C" /></div>
        <div class="form-group"><label>Độ ẩm thiết kế (%)</label><input type="number" id="rm-rhin" step="1" min="35" max="75" value="${rm.rh_in ?? ""}" placeholder="${preset.rh_in}%" /></div>
        <div class="form-group"><label>Số người</label><input type="number" id="rm-people" min="0" value="${rm.people ?? ""}" placeholder="Tự động" /></div>
        <div class="form-group"><label>Gió tươi riêng (m³/h)</label><input type="number" id="rm-oa" min="0" step="10" value="${rm.oa_override_m3h ?? ""}" placeholder="Theo TCVN" /></div>
        <div class="form-group"><label>Lọt khí ACH (lần/h)</label><input type="number" id="rm-ach" min="0" step="0.1" value="${rm.ach_inf ?? ""}" placeholder="${preset.ach_inf}" /></div>
      </div>
    </div>

    <!-- WALL, PARTITION, ROOF & FLOOR -->
    <div class="rm-section-box">
      <div class="rm-section-title">🧱 1. Vật Liệu Tường Bao, Vách Ngăn Không ĐHKK, Mái & Sàn</div>
      <div style="display:grid;grid-template-columns:1fr 1.5fr 0.75fr 0.85fr;gap:8px;">
        <div class="form-group"><label>Hướng nắng chính</label><select id="rm-orient">${optHtml(HVAC_META.orientations, rm.orientation)}</select></div>
        <div class="form-group"><label>Vật liệu Tường bao ngoài</label><select id="rm-wall">${optHtml(HVAC_META.walls, rm.wall_type)}</select></div>
        <div class="form-group"><label>Dài tường ngoài (m)</label><input type="number" id="rm-extlen" step="0.1" min="0" value="${rm.ext_wall_len ?? ""}" placeholder="Tự động" /></div>
        <div class="form-group"><label>Vách ngăn hành lang (m)</label><input type="number" id="rm-partlen" step="0.5" min="0" value="${rm.partition_len ?? 0}" /></div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px;">
        <div class="form-group"><label>Kết cấu Mái / Trần trên</label><select id="rm-roof">${optHtml(HVAC_META.roofs, rm.roof_type)}</select></div>
        <div class="form-group"><label>Kết cấu Sàn dưới</label><select id="rm-floor-mat">${optHtml(HVAC_META.floors, rm.floor_type)}</select></div>
      </div>
    </div>

    <!-- WINDOWS & GLAZING -->
    <div class="rm-section-box">
      <div class="rm-section-title">🪟 2. Cửa Sổ & Vách Kính (Số Lượng, Kích Thước, Khung, Kính & Rèm)</div>
      <div style="display:grid;grid-template-columns:0.7fr 0.8fr 0.8fr 1.5fr 0.9fr;gap:8px;">
        <div class="form-group"><label>SL Cửa sổ</label><input type="number" id="rm-win-qty" min="0" max="20" value="${rm.win_qty ?? 1}" /></div>
        <div class="form-group"><label>Rộng W (m)</label><input type="number" id="rm-win-w" step="0.1" min="0" value="${rm.win_w ?? 1.6}" /></div>
        <div class="form-group"><label>Cao H (m)</label><input type="number" id="rm-win-h" step="0.1" min="0" value="${rm.win_h ?? 1.5}" /></div>
        <div class="form-group"><label>Vật liệu Khung cửa sổ</label><select id="rm-win-frame">${optHtml(HVAC_META.window_frames, rm.win_frame_type || "XINGFA_NO_TB")}</select></div>
        <div class="form-group"><label>Vách kính thêm (m²)</label><input type="number" id="rm-extra-glass" step="0.2" min="0" value="${rm.extra_glass_area ?? 0}" /></div>
      </div>
      <div style="display:grid;grid-template-columns:1.4fr 1fr;gap:8px;margin-top:8px;">
        <div class="form-group"><label>Loại Kính cửa sổ / vách kính (QCVN 09)</label><select id="rm-glass">${optHtml(HVAC_META.glasses, rm.glass_type)}</select></div>
        <div class="form-group"><label>Rèm / Che nắng ngoài</label><select id="rm-shade">${optHtml(HVAC_META.shadings, rm.shading_type)}</select></div>
      </div>
    </div>

    <!-- MAIN DOOR -->
    <div class="rm-section-box">
      <div class="rm-section-title">🚪 3. Cửa Chính / Cửa Ra Vào (Vật Liệu, Vị Trí, Kích Thước & Lọt Khí)</div>
      <div style="display:grid;grid-template-columns:1.8fr 1fr 0.6fr 0.7fr 0.7fr;gap:8px;">
        <div class="form-group"><label>Vật liệu Cửa chính / Cửa phòng</label><select id="rm-door-type">${optHtml(HVAC_META.doors, rm.door_type || "WOOD_ENG_HDF")}</select></div>
        <div class="form-group"><label>Vị trí tiếp xúc</label>
          <select id="rm-door-loc">
            <option value="EXT" ${rm.door_location === "EXT" ? "selected" : ""}>Mặt ngoài (Nắng/gió trời)</option>
            <option value="INT" ${rm.door_location !== "EXT" ? "selected" : ""}>Trong nhà / Hành lang</option>
          </select>
        </div>
        <div class="form-group"><label>SL cửa</label><input type="number" id="rm-door-qty" min="0" max="10" value="${rm.door_qty ?? 1}" /></div>
        <div class="form-group"><label>Rộng (m)</label><input type="number" id="rm-door-w" step="0.05" min="0" value="${rm.door_w ?? 1.0}" /></div>
        <div class="form-group"><label>Cao (m)</label><input type="number" id="rm-door-h" step="0.05" min="0" value="${rm.door_h ?? 2.2}" /></div>
      </div>
    </div>

    <!-- DETAILED EQUIPMENT PICKER (HOME / OFFICE / HOSPITAL) -->
    <div class="rm-section-box">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:8px;">
        <div class="rm-section-title" style="margin:0;">⚡ 4. Chiếu Sáng & Thiết Bị Tỏa Nhiệt (Gia Đình • Văn Phòng • Bệnh Viện)</div>
        <div id="rm-eq-total-badge" style="font-size:11.8px;font-weight:700;color:#991B1B;background:#FEF2F2;border:1px solid #FECACA;padding:3px 9px;border-radius:6px;">0 W</div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px;">
        <div class="form-group"><label>Công suất đèn chiếu sáng (W/m²)</label><input type="number" id="rm-light" step="1" min="0" value="${rm.light_w_m2 ?? ""}" placeholder="Mặc định ${preset.light_w_m2} W/m²" /></div>
        <div class="form-group"><label>Phụ tải thiết bị thêm (W/m² — để trống nếu chọn bên dưới)</label><input type="number" id="rm-equip" step="1" min="0" value="${rm.equip_w_m2 ?? ""}" placeholder="0 nếu đã chọn TB bên dưới" /></div>
      </div>
      <div class="eq-tab-row">
        <button type="button" class="eq-tab-btn ${_editingEquipTab === "HOME" ? "active" : ""}" data-eqcat="HOME" onclick="switchRoomEquipTab('HOME')">🏠 Thiết bị Gia đình (8)</button>
        <button type="button" class="eq-tab-btn ${_editingEquipTab === "OFFICE" ? "active" : ""}" data-eqcat="OFFICE" onclick="switchRoomEquipTab('OFFICE')">🏢 Thiết bị Văn phòng (8)</button>
        <button type="button" class="eq-tab-btn ${_editingEquipTab === "HOSPITAL" ? "active" : ""}" data-eqcat="HOSPITAL" onclick="switchRoomEquipTab('HOSPITAL')">🏥 Thiết bị Bệnh viện / Y tế (9)</button>
      </div>
      <div id="rm-eq-picker-list" class="eq-picker-grid"></div>
    </div>

    <!-- SECTION 5: MULTI-INDOOR UNIT ASSIGNMENT PER ROOM -->
    <div id="rm-units-section" class="rm-section-box" style="background:#EFF6FF;border-color:#93C5FD;">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:8px;">
        <div class="rm-section-title" style="margin:0;color:#991B1B;">❄️ 5. Chọn Dàn Lạnh Daikin Cho Phòng Này (Cho Phép 1 Phòng Nhiều Dàn Lạnh!)</div>
        <div style="display:flex;gap:6px;">
          <button type="button" class="eq-tab-btn ${_editingUnitMode === "AUTO" ? "active" : ""}" id="rm-umode-auto" onclick="switchRoomUnitMode('AUTO')">⚡ Tự động chọn & chia số dàn</button>
          <button type="button" class="eq-tab-btn ${_editingUnitMode === "MANUAL" ? "active" : ""}" id="rm-umode-manual" onclick="switchRoomUnitMode('MANUAL')">🎛️ Tự chọn từng Model dàn lạnh</button>
        </div>
      </div>

      <div id="rm-units-auto-box" style="display:${_editingUnitMode === "AUTO" ? "grid" : "none"};grid-template-columns:1.5fr 1fr;gap:10px;">
        <div class="form-group">
          <label>Kiểu dàn lạnh Daikin ưu tiên cho phòng này</label>
          <select id="rm-prefer">
            <option value="" ${!rm.prefer_type ? "selected" : ""}>Theo mặc định chung của dự án</option>
            <option value="VRV_DUCT" ${rm.prefer_type === "VRV_DUCT" ? "selected" : ""}>VRV Giấu trần nối ống gió</option>
            <option value="VRV_CASSETTE" ${rm.prefer_type === "VRV_CASSETTE" ? "selected" : ""}>VRV Cassette âm trần</option>
            <option value="VRV_WALL" ${rm.prefer_type === "VRV_WALL" ? "selected" : ""}>VRV Treo tường</option>
            <option value="MULTI_DUCT" ${rm.prefer_type === "MULTI_DUCT" ? "selected" : ""}>Multi NX Giấu trần</option>
            <option value="MULTI_WALL" ${rm.prefer_type === "MULTI_WALL" ? "selected" : ""}>Multi NX Treo tường</option>
            <option value="SKY_DUCT" ${rm.prefer_type === "SKY_DUCT" ? "selected" : ""}>SkyAir Giấu trần</option>
            <option value="SKY_CASSETTE" ${rm.prefer_type === "SKY_CASSETTE" ? "selected" : ""}>SkyAir Cassette</option>
            <option value="ROOM_AIR" ${rm.prefer_type === "ROOM_AIR" ? "selected" : ""}>Dân dụng Treo tường FTHF</option>
          </select>
        </div>
        <div class="form-group">
          <label>Chia tải thành bao nhiêu dàn lạnh trong phòng?</label>
          <select id="rm-split-units">
            <option value="1" ${(rm.split_units || 1) == 1 ? "selected" : ""}>1 dàn lạnh (Mặc định)</option>
            <option value="2" ${rm.split_units == 2 ? "selected" : ""}>2 dàn lạnh chia đều tải (Phòng rộng / L)</option>
            <option value="3" ${rm.split_units == 3 ? "selected" : ""}>3 dàn lạnh chia đều tải (Sảnh / VP mở)</option>
            <option value="4" ${rm.split_units == 4 ? "selected" : ""}>4 dàn lạnh chia đều tải (Hội trường / Sảnh lớn)</option>
          </select>
        </div>
      </div>

      <div id="rm-units-manual-box" style="display:${_editingUnitMode === "MANUAL" ? "block" : "none"};">
        <div style="display:grid;grid-template-columns:1fr 1.6fr 0.45fr auto;gap:8px;align-items:end;margin-bottom:8px;">
          <div class="form-group">
            <label>Lọc dòng dàn lạnh Daikin</label>
            <select id="rm-unit-cat-filter" onchange="populateRoomUnitDropdown()">
              <option value="ALL">Tất cả dàn lạnh Daikin</option>
              <option value="VRV_IN_DUCT">VRV Giấu trần nối ống gió</option>
              <option value="VRV_IN_CASSETTE">VRV Cassette âm trần</option>
              <option value="VRV_IN_WALL">VRV Treo tường</option>
              <option value="MULTI_IN">Super Multi NX (Giấu trần/Treo tường)</option>
              <option value="SKY">SkyAir (Giấu trần / Cassette)</option>
              <option value="ROOM_AIR">Dân dụng Treo tường FTHF</option>
            </select>
          </div>
          <div class="form-group">
            <label>Chọn Model dàn lạnh muốn gắn vào phòng</label>
            <select id="rm-unit-model-sel"></select>
          </div>
          <div class="form-group">
            <label>SL</label>
            <input type="number" id="rm-unit-add-qty" value="1" min="1" max="20" />
          </div>
          <button type="button" class="btn btn-sm btn-primary" onclick="addManualUnitToRoomEditor()">➕ Thêm dàn</button>
        </div>
        <div id="rm-selected-units-list"></div>
      </div>
    </div>

    <div style="display:flex;justify-content:flex-end;gap:10px;margin-top:16px;padding-top:12px;border-top:1px solid #E2E8F0;">
      <button class="btn btn-outline" onclick="closeModal('edit-model-modal')">Hủy bỏ</button>
      <button class="btn btn-primary" onclick="saveRoomFromEditorModal()">💾 Lưu & Tính Lại Tải Nhiệt</button>
    </div>
  `;
  renderRoomEquipmentPicker();
  populateRoomUnitDropdown();
  renderSelectedRoomUnitsList();
  document.getElementById("edit-model-modal").classList.add("open");
  if (focusUnits) {
    switchRoomUnitMode("MANUAL");
    setTimeout(() => document.getElementById("rm-units-section")?.scrollIntoView({ behavior: "smooth", block: "center" }), 60);
  }
}

function switchRoomEquipTab(cat) {
  _editingEquipTab = cat;
  document.querySelectorAll(".eq-tab-btn[data-eqcat]").forEach(b => b.classList.toggle("active", b.getAttribute("data-eqcat") === cat));
  renderRoomEquipmentPicker();
}

function stepRoomEquipQty(eqId, delta) {
  const cur = Number(_editingEquipMap[eqId] || 0) + delta;
  if (cur <= 0) delete _editingEquipMap[eqId];
  else _editingEquipMap[eqId] = Math.min(99, cur);
  renderRoomEquipmentPicker();
}

function renderRoomEquipmentPicker() {
  const box = document.getElementById("rm-eq-picker-list");
  if (!box) return;
  const items = Object.entries(HVAC_META.equipment_library).filter(([, v]) => v.cat === _editingEquipTab);
  box.innerHTML = items.map(([id, it]) => {
    const qty = Number(_editingEquipMap[id] || 0);
    return `
      <div class="eq-item-row ${qty > 0 ? "selected" : ""}">
        <div style="flex:1;min-width:0;">
          <div style="font-weight:700;font-size:11.8px;color:#0F172A;">${it.name}</div>
          <div style="font-size:10.5px;color:#475569;">Hiện: <strong>${it.q_sens_w}W</strong>${it.q_lat_w > 0 ? ` • Ẩn: <strong style="color:#005A8D;">${it.q_lat_w}W</strong>` : ""} / ${it.unit}</div>
        </div>
        <div style="display:flex;align-items:center;gap:4px;">
          <button type="button" class="btn btn-sm btn-outline" style="padding:2px 7px;" onclick="stepRoomEquipQty('${id}', -1)">−</button>
          <span style="min-width:22px;text-align:center;font-weight:700;color:${qty > 0 ? "#991B1B" : "#64748B"};">${qty}</span>
          <button type="button" class="btn btn-sm btn-ice" style="padding:2px 7px;" onclick="stepRoomEquipQty('${id}', 1)">+</button>
        </div>
      </div>
    `;
  }).join("");

  let totS = 0, totL = 0, cnt = 0;
  Object.entries(_editingEquipMap).forEach(([id, q]) => {
    const it = HVAC_META.equipment_library[id];
    if (it && q > 0) { totS += it.q_sens_w * q; totL += it.q_lat_w * q; cnt += q; }
  });
  const badge = document.getElementById("rm-eq-total-badge");
  if (badge) {
    badge.textContent = cnt > 0
      ? `Đã chọn ${cnt} TB: ${formatNum(totS)} W hiện` + (totL > 0 ? ` + ${formatNum(totL)} W ẩn` : "")
      : "Chưa chọn thiết bị riêng (dùng định mức W/m²)";
  }
}

function updateRoomPlenumPreview() {
  const hbt = Number(document.getElementById("rm-hbt")?.value) || 3.6;
  const htc = Number(document.getElementById("rm-htc")?.value) || 3.0;
  const mm = Math.max(0, Math.round((hbt - htc) * 1000));
  const el = document.getElementById("rm-plenum-preview");
  if (el) {
    el.textContent = `${mm} mm ${mm < 250 ? "(Rất thấp!)" : (mm < 300 ? "(Chọn FXDQ 200mm)" : "(Đạt chuẩn)")}`;
    el.style.color = mm < 250 ? "#991B1B" : "#005A8D";
  }
}

function switchRoomUnitMode(mode) {
  _editingUnitMode = mode === "MANUAL" ? "MANUAL" : "AUTO";
  document.getElementById("rm-umode-auto")?.classList.toggle("active", _editingUnitMode === "AUTO");
  document.getElementById("rm-umode-manual")?.classList.toggle("active", _editingUnitMode === "MANUAL");
  const ab = document.getElementById("rm-units-auto-box");
  const mb = document.getElementById("rm-units-manual-box");
  if (ab) ab.style.display = _editingUnitMode === "AUTO" ? "grid" : "none";
  if (mb) mb.style.display = _editingUnitMode === "MANUAL" ? "block" : "none";
  if (_editingUnitMode === "MANUAL") {
    populateRoomUnitDropdown();
    renderSelectedRoomUnitsList();
  }
}

function populateRoomUnitDropdown() {
  const sel = document.getElementById("rm-unit-model-sel");
  if (!sel || typeof DB === "undefined") return;
  const cat = document.getElementById("rm-unit-cat-filter")?.value || "ALL";
  const indoors = DB.products.filter(p => {
    const cid = p.category_id || "";
    if (!p.cooling_btu || p.cooling_btu <= 0) return false;
    if (cid.includes("_OUT") || cid === "VRV_ACC" || cid === "MULTI_ACC" || cid === "VRV_HRV") return false;
    if (cat === "VRV_IN_DUCT") return cid.startsWith("VRV_IN_DUCT");
    if (cat === "VRV_IN_CASSETTE") return cid === "VRV_IN_CASSETTE";
    if (cat === "VRV_IN_WALL") return cid === "VRV_IN_WALL";
    if (cat === "MULTI_IN") return cid.startsWith("MULTI_IN");
    if (cat === "SKY") return cid.startsWith("SKY_");
    if (cat === "ROOM_AIR") return cid === "ROOM_AIR";
    return true;
  }).sort((a, b) => a.cooling_btu - b.cooling_btu);
  sel.innerHTML = indoors.map(p => `<option value="${p.id}">${p.model} — ${formatNum(p.cooling_btu)} Btu/h (${p.cooling_kw} kW) | ${p.dimensions || ""}</option>`).join("");
}

function addManualUnitToRoomEditor() {
  const pid = document.getElementById("rm-unit-model-sel")?.value;
  const qty = Math.max(1, Number(document.getElementById("rm-unit-add-qty")?.value) || 1);
  if (!pid) return;
  const ex = _editingUnitsList.find(u => u.prod_id === pid);
  if (ex) ex.qty += qty;
  else _editingUnitsList.push({ prod_id: pid, qty });
  renderSelectedRoomUnitsList();
}

function stepRoomManualUnitQty(idx, delta) {
  if (!_editingUnitsList[idx]) return;
  _editingUnitsList[idx].qty += delta;
  if (_editingUnitsList[idx].qty <= 0) _editingUnitsList.splice(idx, 1);
  renderSelectedRoomUnitsList();
}

function renderSelectedRoomUnitsList() {
  const box = document.getElementById("rm-selected-units-list");
  if (!box) return;
  if (!_editingUnitsList.length) {
    box.innerHTML = `<div style="padding:10px;background:#FFFFFF;border:1px dashed #93C5FD;border-radius:7px;font-size:12px;color:#475569;text-align:center;">Chưa gắn dàn lạnh nào. Chọn Model ở trên rồi bấm <strong>➕ Thêm dàn</strong> (có thể thêm nhiều Model khác nhau trong cùng 1 phòng!).</div>`;
    return;
  }
  const prods = (typeof DB !== "undefined" && DB.products) ? DB.products : [];
  let totBtu = 0, totKw = 0, totCnt = 0;
  const rows = _editingUnitsList.map((u, idx) => {
    const p = prods.find(x => x.id === u.prod_id);
    if (!p) return "";
    totBtu += (p.cooling_btu || 0) * u.qty;
    totKw += (p.cooling_kw || 0) * u.qty;
    totCnt += u.qty;
    return `
      <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;padding:6px 10px;background:#FFFFFF;border:1px solid #BFDBFE;border-radius:7px;margin-bottom:5px;">
        <div>
          <strong style="color:#005A8D;font-size:12.5px;">${p.model}</strong>
          <span style="font-size:11.5px;color:#475569;"> — ${formatNum(p.cooling_btu)} Btu/h (${p.cooling_kw} kW) × ${u.qty} = <strong>${formatNum(p.cooling_btu * u.qty)} Btu/h</strong></span>
        </div>
        <div style="display:flex;align-items:center;gap:4px;">
          <button type="button" class="btn btn-sm btn-outline" style="padding:2px 7px;" onclick="stepRoomManualUnitQty(${idx}, -1)">−</button>
          <span style="min-width:22px;text-align:center;font-weight:700;color:#991B1B;">${u.qty}</span>
          <button type="button" class="btn btn-sm btn-ice" style="padding:2px 7px;" onclick="stepRoomManualUnitQty(${idx}, 1)">+</button>
          <button type="button" class="btn btn-sm btn-outline" style="color:#991B1B;padding:2px 7px;" onclick="stepRoomManualUnitQty(${idx}, -999)">✕</button>
        </div>
      </div>
    `;
  }).join("");
  const cov = Math.round((totBtu / Math.max(1, _editingRoomEstBtu)) * 100);
  const okCol = cov >= 94 ? "#166534" : "#991B1B";
  box.innerHTML = rows + `
    <div style="padding:7px 10px;background:#FFFFFF;border:1.5px solid ${okCol};border-radius:7px;font-size:12px;font-weight:700;color:${okCol};display:flex;justify-content:space-between;">
      <span>Tổng ${totCnt} dàn trong phòng: ${formatNum(totBtu)} Btu/h (${totKw.toFixed(1)} kW)</span>
      <span>So tải ước tính (${formatNum(_editingRoomEstBtu)} Btu/h): ${cov}% ${cov >= 94 ? "✅ ĐẠT" : "⚠️ THIẾU TẢI"}</span>
    </div>
  `;
}

function saveRoomFromEditorModal() {
  const v = (id) => document.getElementById(id)?.value;
  const numOrEmpty = (id) => { const s = v(id); return (s === "" || s === null || s === undefined) ? "" : Number(s); };
  const eqItems = Object.entries(_editingEquipMap)
    .filter(([, q]) => Number(q) > 0)
    .map(([id, q]) => ({ id, qty: Number(q) }));

  const obj = {
    name: (v("rm-name") || "Phòng").trim(),
    floor: (v("rm-floor") || "Tầng 1").trim(),
    room_type: v("rm-type") || "LIVING",
    area: Math.max(2, Number(v("rm-area")) || 20),
    h_concrete: Math.max(2.3, Number(v("rm-hbt")) || 3.6),
    h_ceiling: Math.max(2.0, Number(v("rm-htc")) || 3.0),
    t_in: numOrEmpty("rm-tin"),
    rh_in: numOrEmpty("rm-rhin"),
    oa_override_m3h: numOrEmpty("rm-oa"),
    ach_inf: numOrEmpty("rm-ach"),
    orientation: v("rm-orient") || "W",
    wall_type: v("rm-wall") || "BRICK_220_HOLLOW",
    ext_wall_len: numOrEmpty("rm-extlen"),
    partition_len: Math.max(0, Number(v("rm-partlen")) || 0),
    win_frame_type: v("rm-win-frame") || "XINGFA_NO_TB",
    win_qty: Math.max(0, Number(v("rm-win-qty")) || 0),
    win_w: Math.max(0, Number(v("rm-win-w")) || 0),
    win_h: Math.max(0, Number(v("rm-win-h")) || 0),
    extra_glass_area: Math.max(0, Number(v("rm-extra-glass")) || 0),
    glass_type: v("rm-glass") || "TEMPERED_XINGFA",
    shading_type: v("rm-shade") || "ROLLER",
    door_type: v("rm-door-type") || "NONE",
    door_location: v("rm-door-loc") || "INT",
    door_qty: Math.max(0, Number(v("rm-door-qty")) || 0),
    door_w: Math.max(0, Number(v("rm-door-w")) || 0),
    door_h: Math.max(0, Number(v("rm-door-h")) || 0),
    roof_type: v("rm-roof") || "MID_FLOOR",
    floor_type: v("rm-floor-mat") || "MID_AC",
    people: numOrEmpty("rm-people"),
    light_w_m2: numOrEmpty("rm-light"),
    equip_w_m2: numOrEmpty("rm-equip"),
    equipment_items: eqItems,
    prefer_type: v("rm-prefer") || "",
    split_units: _editingUnitMode === "AUTO" ? Math.max(1, Number(v("rm-split-units")) || 1) : 1,
    selected_units: _editingUnitMode === "MANUAL" ? _editingUnitsList.slice() : []
  };
  if (_editingRoomIdx >= 0 && _editingRoomIdx < HVAC_STATE.rooms.length) {
    HVAC_STATE.rooms[_editingRoomIdx] = obj;
  } else {
    HVAC_STATE.rooms.push(obj);
  }
  closeModal("edit-model-modal");
  recalcProjectHeatLoad();
  showToast(`✅ Đã cập nhật "${obj.name}" (${obj.selected_units.length ? obj.selected_units.reduce((s,u)=>s+u.qty,0) + " dàn lạnh chọn tay" : (obj.split_units + " dàn tự động")})!`);
}

function deleteHvacRoom(idx) {
  HVAC_STATE.rooms.splice(idx, 1);
  recalcProjectHeatLoad();
}

function loadSampleVillaToHvac() {
  HVAC_STATE.rooms = getSampleVillaRooms();
  recalcProjectHeatLoad();
  showToast("✨ Đã nạp dự án mẫu Biệt thự 3 tầng Hà Nội (5 phòng chuẩn TCVN 5687:2024)!");
}

/* ---------------- HYBRID AI THERMAL CONSULTATION REPORT ---------------- */
async function runAiThermalAnalysis() {
  if (!HVAC_STATE.lastCalc) await recalcProjectHeatLoad();
  const btn = document.getElementById("btn-run-ai-report");
  const box = document.getElementById("hv-ai-report-text");
  if (btn) btn.disabled = true;
  if (box) box.textContent = "🤖 Đang chạy động cơ AI phân tích tải nhiệt TCVN 5687:2024, thẩm định QCVN 09 & tối ưu thiết bị Daikin...";

  let res = null;
  try {
    const resp = await fetch("/api/hvac/ai_analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        calc_result: HVAC_STATE.lastCalc,
        duct_result: HVAC_STATE.lastDuct,
        ai_config: AI_CONFIG
      })
    });
    if (resp.ok) res = await resp.json();
  } catch (e) {}

  if (!res || !res.ok) {
    res = { ok: true, mode: "OFFLINE_EXPERT", report_text: buildOfflineAiReportJS(HVAC_STATE.lastCalc, HVAC_STATE.lastDuct) };
  }
  HVAC_STATE.aiReportText = res.report_text || "";
  HVAC_STATE.aiReportMode = res.mode || "OFFLINE_EXPERT";
  if (box) box.textContent = HVAC_STATE.aiReportText;
  if (btn) btn.disabled = false;
  if (res.warning) {
    showToast(`⚠️ Không gọi được AI online (${res.warning.slice(0, 80)}...) — Đã tự chuyển sang Chuyên gia Offline!`);
  } else {
    showToast(`🤖 Hoàn thành Báo cáo Thẩm định Kỹ thuật (${HVAC_STATE.aiReportMode})!`);
  }
}

/* ---------------- EXPORT SEPARATE HVAC REPORT PDF & EXCEL ---------------- */
function buildHvacReportPayload() {
  const qMeta = typeof QUOTE !== "undefined" ? QUOTE : {};
  const today = new Date();
  const code = `BC-HVAC-${today.getFullYear()}${String(today.getMonth()+1).padStart(2,"0")}${String(today.getDate()).padStart(2,"0")}`;
  return {
    company: typeof DB !== "undefined" ? DB.company : {},
    meta: {
      report_code: code,
      date_str: today.toLocaleDateString("vi-VN"),
      client_name: qMeta.client_name || "Quý Khách Hàng / Chủ Đầu Tư",
      project_name: qMeta.project_name || `Hệ Thống ĐHKK Daikin — ${HVAC_STATE.lastCalc?.design_basis?.city_name || "Việt Nam"}`,
      engineer_name: qMeta.author || "Phòng Tư Vấn Thiết Kế Minh Phú"
    },
    calc_result: HVAC_STATE.lastCalc,
    duct_result: HVAC_STATE.lastDuct,
    coolpack_result: HVAC_STATE.lastCoolpack,
    ai_report_text: HVAC_STATE.aiReportText || buildOfflineAiReportJS(HVAC_STATE.lastCalc, HVAC_STATE.lastDuct),
    ai_mode: HVAC_STATE.aiReportMode || "OFFLINE_EXPERT"
  };
}

async function exportHvacReportPDF() {
  if (!HVAC_STATE.lastCalc) await recalcProjectHeatLoad();
  const payload = buildHvacReportPayload();
  showToast("⏳ Đang xuất Báo cáo Tính Nhiệt & Ống Gió PDF riêng biệt...");
  try {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.export_hvac_report_pdf) {
      const res = await window.pywebview.api.export_hvac_report_pdf(JSON.stringify(payload));
      if (res && res.ok) showToast(`📄 Đã lưu Báo cáo PDF: ${res.path}`);
      else if (res && res.cancelled) showToast("Đã hủy lưu file PDF.");
      return;
    }
    const resp = await fetch("/api/hvac/export_report_pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (resp.ok) {
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Bao_Cao_Nhiet_Gio_Minh_Phu_${payload.meta.report_code}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      showToast("📄 Đã tải xuống Báo cáo Kỹ Thuật PDF!");
      return;
    }
  } catch (e) {}
  // Mobile / Offline Browser Fallback (Android APK / iOS IPA / Safari / Chrome)
  if (window.AndroidNative && window.AndroidNative.printQuotePdf) {
    window.AndroidNative.printQuotePdf(`Bao_Cao_Nhiet_Gio_${payload.meta.report_code}`);
    return;
  }
  if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.iosNative) {
    window.webkit.messageHandlers.iosNative.postMessage({ action: "printPdf", jobName: `Bao_Cao_Nhiet_Gio_${payload.meta.report_code}` });
    return;
  }
  window.print();
}

async function exportHvacReportExcel() {
  if (!HVAC_STATE.lastCalc) await recalcProjectHeatLoad();
  const payload = buildHvacReportPayload();
  showToast("⏳ Đang xuất Bảng tính Excel công thức sống (.xlsx)...");
  try {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.export_hvac_report_xlsx) {
      const res = await window.pywebview.api.export_hvac_report_xlsx(JSON.stringify(payload));
      if (res && res.ok) showToast(`📊 Đã lưu Bảng tính Excel: ${res.path}`);
      else if (res && res.cancelled) showToast("Đã hủy lưu file Excel.");
      return;
    }
    const resp = await fetch("/api/hvac/export_report_xlsx", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (resp.ok) {
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Bang_Tinh_Nhiet_Gio_Minh_Phu_${payload.meta.report_code}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
      showToast("📊 Đã tải xuống Bảng tính Nhiệt Excel (.xlsx)!");
      return;
    }
  } catch (e) {}
  // Offline mobile / browser UTF-8 Excel fallback (.xls)
  downloadOfflineHvacExcelXml(payload);
}

function downloadOfflineHvacExcelXml(payload) {
  const c = payload.company || {};
  const m = payload.meta || {};
  const calc = payload.calc_result || {};
  const db = calc.design_basis || {};
  const sm = calc.summary || {};
  const rooms = calc.rooms || [];
  const rowsHtml = rooms.map((rm, i) => {
    const units = (rm.assigned_units || [rm.recommended_unit]).filter(Boolean).map(u => `${u.qty > 1 ? u.qty + "x " : ""}${u.model || ""}`).join(" + ");
    return `<tr>
      <td style="text-align:center;">${i + 1}</td>
      <td>${rm.name} (${rm.floor})</td>
      <td style="text-align:right;">${rm.area}</td>
      <td style="text-align:center;">${rm.h_concrete} / ${rm.h_ceiling}</td>
      <td style="text-align:center;">${rm.orientation}</td>
      <td style="text-align:right;">${(rm.q_sens_w / 1000).toFixed(2)}</td>
      <td style="text-align:right;">${(rm.q_lat_w / 1000).toFixed(2)}</td>
      <td style="text-align:right;font-weight:bold;">${rm.q_kw}</td>
      <td style="text-align:right;">${rm.q_btu}</td>
      <td style="text-align:right;">${rm.w_per_m2}</td>
      <td style="text-align:right;">${rm.oa_m3h}</td>
      <td>${units}</td>
    </tr>`;
  }).join("");
  const html = `
    <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
    <head><meta charset="UTF-8"></head><body>
      <table border="1" style="border-collapse:collapse;font-family:Arial,sans-serif;font-size:10.5pt;">
        <tr><td colspan="12" style="background:#991B1B;color:#FFFFFF;font-weight:bold;font-size:13pt;">${c.name || "CÔNG TY TNHH PHÁT TRIỂN KỸ THUẬT THƯƠNG MẠI MINH PHÚ"}</td></tr>
        <tr><td colspan="12">BÁO CÁO TÍNH TOÁN TẢI NHIỆT TCVN 5687:2024 (${m.report_code}) — Trạm: ${db.city_name || ""} (t_khô ${db.t_out}°C / t_ướt ${db.twb_out}°C)</td></tr>
        <tr style="background:#005A8D;color:#FFFFFF;font-weight:bold;">
          <th>STT</th><th>Phòng / Tầng</th><th>Diện tích (m²)</th><th>Cao BT/TC (m)</th><th>Hướng</th>
          <th>Q hiện (kW)</th><th>Q ẩn (kW)</th><th>Tổng tải (kW)</th><th>Tổng tải (Btu/h)</th><th>W/m²</th><th>OA (m³/h)</th><th>Dàn lạnh Daikin</th>
        </tr>
        ${rowsHtml}
        <tr style="font-weight:bold;background:#EFF6FF;">
          <td colspan="2">TỔNG CỘNG (${sm.room_count || rooms.length} phòng)</td>
          <td style="text-align:right;">${sm.total_area_m2 || 0}</td>
          <td colspan="2">Đồng thời ×${db.diversity_factor || 0.85}</td>
          <td style="text-align:right;">${sm.total_sens_kw || 0}</td>
          <td style="text-align:right;">${sm.total_lat_kw || 0}</td>
          <td style="text-align:right;">${sm.total_cooling_kw || 0}</td>
          <td style="text-align:right;">${sm.total_cooling_btu || 0}</td>
          <td style="text-align:right;">${sm.avg_w_per_m2 || 0}</td>
          <td style="text-align:right;">${sm.total_oa_m3h || 0}</td>
          <td>Dàn nóng: ${sm.outdoor_rec ? sm.outdoor_rec.model : ""} (${sm.diversified_kw || 0} kW)</td>
        </tr>
      </table>
    </body></html>`;
  const blob = new Blob(["\ufeff", html], { type: "application/vnd.ms-excel;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `Bang_Tinh_Nhiet_Minh_Phu_${m.report_code || "HVAC"}.xls`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("📊 Đã xuất file Bảng tính Nhiệt Excel Offline (.xls)!");
}

function pushHvacEquipmentToCart() {
  const calc = HVAC_STATE.lastCalc;
  if (!calc || !calc.rooms || !calc.rooms.length) {
    showToast("Chưa có phòng nào để đẩy thiết bị!");
    return;
  }
  let addedCount = 0;
  // 1. Push matched outdoor unit (if VRV/Multi)
  const outRec = calc.summary?.outdoor_rec;
  if (outRec && outRec.prod_id && (HVAC_STATE.prefer_system.startsWith("VRV") || HVAC_STATE.prefer_system.startsWith("MULTI"))) {
    addToEquipCart(outRec.prod_id, 1, true);
    addedCount++;
  }
  // 2. Push ALL assigned room indoor units (supports Multi-Indoor Units per Room!)
  calc.rooms.forEach(rm => {
    const units = Array.isArray(rm.assigned_units) && rm.assigned_units.length ? rm.assigned_units : (rm.recommended_unit ? [rm.recommended_unit] : []);
    units.forEach(u => {
      if (u && u.prod_id) {
        addToEquipCart(u.prod_id, u.qty || 1, true);
        addedCount += (u.qty || 1);
      }
    });
  });
  // 3. Push HRV if enabled
  if (HVAC_STATE.use_hrv && calc.summary?.hrv_rec?.prod_id) {
    addToEquipCart(calc.summary.hrv_rec.prod_id, 1, true);
    addedCount++;
  }
  if (typeof persistQuoteState === "function") persistQuoteState();
  showToast(`🛒 Đã đẩy ${addedCount} thiết bị Daikin từ bảng tính nhiệt sang Giỏ Báo Giá!`);
  if (typeof switchView === "function") switchView("cart");
}

/* ---------------- TAB 2 + INLINE OFFLINE / AI DRAWING TAKEOFF ---------------- */
function handleDrawingFileSelect(ev, autoRunAi) {
  const file = ev.target.files && ev.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    HVAC_STATE.takeoff.filename = file.name;
    HVAC_STATE.takeoff.file_b64 = reader.result;
    HVAC_STATE.takeoff.page = 1;
    HVAC_STATE.takeoff.rooms = [];
    const lbl = `📎 Đã chọn: ${file.name} (${(file.size / 1024).toFixed(0)} KB)`;
    ["tk-file-label", "hv-off-tk-label", "hv-ai-tk-label"].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.textContent = lbl;
    });
    runDrawingTakeoff(Boolean(autoRunAi));
  };
  reader.readAsDataURL(file);
}

function renderInlineTakeoffMirror() {
  const tk = HVAC_STATE.takeoff;
  ["hv-off-tk-status", "hv-ai-tk-status"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = tk.note ? `<strong>[${tk.file_type || "FILE"}]</strong> ${tk.note}` : "";
  });
  const aiPrev = document.getElementById("hv-ai-tk-preview");
  if (aiPrev) {
    aiPrev.innerHTML = tk.preview_data_url
      ? `<img src="${tk.preview_data_url}" style="max-width:100%;max-height:280px;object-fit:contain;border-radius:8px;border:1px solid #CBD5E1;" />`
      : `<div style="padding:28px 12px;text-align:center;color:#64748B;font-size:12px;">Chưa tải bản vẽ nào. Chọn file PDF / Ảnh mặt bằng PNG-JPG hoặc CAD để AI Vision nhận diện.</div>`;
  }
  ["hv-off-tk-summary", "hv-ai-tk-summary"].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    if (!tk.rooms || !tk.rooms.length) {
      el.innerHTML = "";
      return;
    }
    el.innerHTML = `
      <div style="margin-top:8px;padding:9px 12px;background:#EFF6FF;border:1px solid #93C5FD;border-radius:8px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
        <div style="font-size:12px;color:#0F172A;">
          ✅ Đã bóc tách được <strong>${tk.rooms.length} phòng</strong>: ${tk.rooms.slice(0, 6).map(r => `${r.name} (${r.area}m²)`).join(" • ")}${tk.rooms.length > 6 ? "..." : ""}
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;">
          <button class="btn btn-sm btn-outline" onclick="switchHvacTab('takeoff')">✏️ Xem & Sửa chi tiết</button>
          <button class="btn btn-sm btn-primary" onclick="importTakeoffRoomsToHeatLoad(true);switchHeatLoadMode('offline')">📥 Nạp ${tk.rooms.length} phòng vào Bảng Tính →</button>
        </div>
      </div>
    `;
  });
}

async function runDrawingTakeoff(useAiVision) {
  const tk = HVAC_STATE.takeoff;
  if (!tk.file_b64) {
    showToast("Vui lòng chọn file bản vẽ .PDF, .DXF, .DWG hoặc ảnh mặt bằng trước!");
    return;
  }
  const statusEl = document.getElementById("tk-status-box");
  if (statusEl) {
    statusEl.innerHTML = useAiVision
      ? "🤖 <strong>AI Vision đang đọc mặt bằng kiến trúc & nhận diện các phòng...</strong> (khoảng 5–15 giây)"
      : "⏳ <strong>Đang phân tích bản vẽ PDF / AutoCAD (.DXF/.DWG) bằng bộ đọc Offline...</strong>";
  }

  try {
    const resp = await fetch("/api/hvac/parse_drawing", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        filename: tk.filename,
        file_b64: tk.file_b64,
        page: tk.page,
        run_ai: Boolean(useAiVision),
        ai_config: AI_CONFIG
      })
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const res = await resp.json();
    if (!res.ok) {
      if (statusEl) statusEl.innerHTML = `<span style="color:#991B1B;font-weight:700;">⚠️ ${res.error}</span>`;
      showToast(res.error || "Lỗi đọc bản vẽ!");
      return;
    }
    tk.file_type = res.file_type || "";
    tk.page = res.page || 1;
    tk.total_pages = res.total_pages || 1;
    tk.preview_data_url = res.preview_data_url || "";
    tk.rooms = res.rooms || [];
    tk.note = res.note || "";
    if (res.ai_error) {
      tk.note += ` | ⚠️ AI Vision: ${res.ai_error}`;
    }
    renderTakeoffResults();
  } catch (e) {
    // Pure browser fallback for Image previews
    if (tk.filename.match(/\.(png|jpg|jpeg|webp)$/i)) {
      tk.preview_data_url = tk.file_b64;
      tk.note = "Đã hiển thị ảnh mặt bằng. Chức năng bóc tách tự động PDF/CAD & AI Vision cần chạy trên bản Windows Desktop (.exe).";
      renderTakeoffResults();
    } else if (statusEl) {
      statusEl.innerHTML = `<span style="color:#991B1B;font-weight:700;">⚠️ Chức năng đọc PDF/CAD DXF-DWG cần chạy trên phiên bản Windows Desktop (.exe). (${e.message})</span>`;
    }
  }
}

function stepTakeoffPage(delta) {
  const tk = HVAC_STATE.takeoff;
  const next = tk.page + delta;
  if (next < 1 || next > tk.total_pages) return;
  tk.page = next;
  runDrawingTakeoff(false);
}

function renderTakeoffResults() {
  const tk = HVAC_STATE.takeoff;
  const statusEl = document.getElementById("tk-status-box");
  if (statusEl) statusEl.innerHTML = `<strong>[${tk.file_type || "FILE"}]</strong> ${tk.note}`;

  const pager = document.getElementById("tk-pdf-pager");
  if (pager) {
    pager.style.display = tk.total_pages > 1 ? "flex" : "none";
    const ind = document.getElementById("tk-page-ind");
    if (ind) ind.textContent = `Trang ${tk.page} / ${tk.total_pages}`;
  }

  const prevEl = document.getElementById("tk-preview-stage");
  if (prevEl) {
    if (tk.preview_data_url) {
      prevEl.innerHTML = `<img src="${tk.preview_data_url}" style="max-width:100%;max-height:460px;object-fit:contain;border-radius:8px;border:1px solid #CBD5E1;" />`;
    } else {
      prevEl.innerHTML = `<div style="padding:36px 16px;text-align:center;color:#475569;">📐 File CAD Vector <strong>${tk.filename}</strong> đã được phân tích trực tiếp hình học Polyline & Text.<br/>Kiểm tra bảng danh sách phòng đã bóc tách bên cạnh →</div>`;
    }
  }

  const tb = document.getElementById("tk-rooms-tbody");
  if (tb) {
    if (!tk.rooms.length) {
      tb.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:#64748B;">Chưa nhận diện được phòng tự động trên trang này. Hãy bấm <strong>🤖 AI Vision Quét Mặt Bằng</strong> (khi có API Key) hoặc bấm <strong>➕ Thêm dòng thủ công</strong>!</td></tr>`;
    } else {
      tb.innerHTML = tk.rooms.map((r, i) => `
        <tr>
          <td><input type="text" class="inline-inp" value="${r.name}" onchange="HVAC_STATE.takeoff.rooms[${i}].name=this.value" /></td>
          <td><input type="text" class="inline-inp" style="width:66px;" value="${r.floor || "Tầng 1"}" onchange="HVAC_STATE.takeoff.rooms[${i}].floor=this.value" /></td>
          <td><input type="number" class="inline-inp" style="width:68px;" step="0.5" value="${r.area}" onchange="HVAC_STATE.takeoff.rooms[${i}].area=Number(this.value)||10" /></td>
          <td><input type="number" class="inline-inp" style="width:58px;" step="0.1" value="${r.h_concrete || 3.6}" onchange="HVAC_STATE.takeoff.rooms[${i}].h_concrete=Number(this.value)||3.6" /></td>
          <td><input type="number" class="inline-inp" style="width:58px;" step="0.1" value="${r.h_ceiling || 3.0}" onchange="HVAC_STATE.takeoff.rooms[${i}].h_ceiling=Number(this.value)||3.0" /></td>
          <td style="font-size:11px;color:#005A8D;">${r.source || "Takeoff"}</td>
          <td><button class="btn btn-sm btn-outline" style="color:#991B1B;" onclick="HVAC_STATE.takeoff.rooms.splice(${i},1);renderTakeoffResults()">✕</button></td>
        </tr>
      `).join("");
    }
  }
  renderInlineTakeoffMirror();
}

function addManualTakeoffRow() {
  HVAC_STATE.takeoff.rooms.push({
    name: `Phòng đọc từ bản vẽ #${HVAC_STATE.takeoff.rooms.length + 1}`,
    floor: "Tầng 1", room_type: "LIVING", area: 28, h_concrete: 3.6, h_ceiling: 3.0,
    ext_wall_len: 5.5, glass_area: 4.5, orientation: "W", source: "Nhập bổ sung"
  });
  renderTakeoffResults();
}

function importTakeoffRoomsToHeatLoad(replaceAll) {
  const src = HVAC_STATE.takeoff.rooms || [];
  if (!src.length) {
    showToast("Chưa có phòng nào trong bảng bóc tách để đưa sang!");
    return;
  }
  const normalized = src.map(r => ({
    name: r.name || "Phòng",
    floor: r.floor || "Tầng 1",
    room_type: r.room_type || "LIVING",
    area: Math.max(2, Number(r.area) || 20),
    h_concrete: Number(r.h_concrete) || 3.6,
    h_ceiling: Number(r.h_ceiling) || 3.0,
    orientation: r.orientation || "W",
    wall_type: "BRICK_220_HOLLOW",
    ext_wall_len: r.ext_wall_len || "",
    glass_type: "TEMPERED_XINGFA",
    glass_area: r.glass_area || "",
    shading_type: "ROLLER",
    roof_type: "MID_FLOOR",
    floor_type: "MID_AC",
    partition_len: 0,
    people: r.people || "",
    light_w_m2: "", equip_w_m2: "", prefer_type: ""
  }));
  if (replaceAll) HVAC_STATE.rooms = normalized;
  else HVAC_STATE.rooms = HVAC_STATE.rooms.concat(normalized);
  switchHvacTab("heatload");
  recalcProjectHeatLoad();
  showToast(`📥 Đã nhập ${normalized.length} phòng từ bản vẽ sang Bảng Tính Tải Nhiệt TCVN 5687!`);
}

/* ---------------- TAB 3: DAIKIN DUCT CHECKER ---------------- */
function populateDuctModelDropdown() {
  const sel = document.getElementById("dc-model");
  if (!sel || typeof DB === "undefined") return;
  const ducted = DB.products.filter(p => p.duct || (p.category_id || "").includes("DUCT"));
  sel.innerHTML = `<option value="CUSTOM">-- Tự nhập Lưu lượng & Cột áp ESP --</option>` +
    ducted.map(p => `<option value="${p.id}">${p.model} — ${formatNum(p.cooling_btu)} Btu/h | Gió: ${p.airflow || "—"} | ESP: ${p.esp || "—"}</option>`).join("");
}

function onDuctModelSelect() {
  const id = document.getElementById("dc-model")?.value;
  HVAC_STATE.ductInput.model_id = id;
  if (id && id !== "CUSTOM" && typeof DB !== "undefined") {
    const p = DB.products.find(x => x.id === id);
    if (p) {
      // Parse airflow m3/h and ESP Pa
      const af = String(p.airflow || "");
      let m3h = 1200;
      const mh = af.match(/(\d+(?:[.,]\d+)?)\s*m³\/h/i);
      if (mh) m3h = parseFloat(mh[1].replace(",", "."));
      else {
        const mn = af.match(/(\d+(?:[.,]\d+)?)/);
        if (mn) {
          const val = parseFloat(mn[1].replace(",", "."));
          m3h = (af.includes("phút") || af.includes("min") || val < 120) ? Math.round(val * 60) : Math.round(val);
        }
      }
      const nums = (String(p.esp || "").match(/\d+/g) || []).map(Number);
      let espR = nums[0] || 50, espM = nums.length ? Math.max(...nums) : 50;
      if (String(p.esp || "").includes("ĐM") && nums.length >= 3) { espR = nums[2]; espM = Math.max(nums[0], nums[1]); }
      document.getElementById("dc-airflow").value = m3h;
      document.getElementById("dc-esp-rated").value = espR;
      document.getElementById("dc-esp-max").value = espM;
    }
  }
  runDuctCheckerCalc();
}

function jumpToDuctChecker(prodId) {
  switchHvacTab("ductchecker");
  const sel = document.getElementById("dc-model");
  if (sel && prodId && Array.from(sel.options).some(o => o.value === prodId)) {
    sel.value = prodId;
    onDuctModelSelect();
  }
}

async function runDuctCheckerCalc() {
  const gN = (id, def) => Number(document.getElementById(id)?.value) || def;
  const inp = {
    model_id: document.getElementById("dc-model")?.value || "FXSQ63PAVE",
    airflow_m3h: gN("dc-airflow", 1200),
    esp_rated_pa: gN("dc-esp-rated", 50),
    esp_max_pa: gN("dc-esp-max", 150),
    num_branches: Math.max(1, gN("dc-branches", 3)),
    main_len_m: Math.max(0, Number(document.getElementById("dc-main-len")?.value ?? 6)),
    branch_len_m: Math.max(0, Number(document.getElementById("dc-branch-len")?.value ?? 3.5)),
    flex_len_m: Math.max(0, Number(document.getElementById("dc-flex-len")?.value ?? 2.0)),
    num_elbows: Math.max(0, Number(document.getElementById("dc-elbows")?.value ?? 2)),
    return_len_m: Math.max(0, Number(document.getElementById("dc-return-len")?.value ?? 3.0)),
    max_h_mm: gN("dc-max-h", 250),
    target_dp: Number(document.getElementById("dc-target-dp")?.value ?? 1.0)
  };
  HVAC_STATE.ductInput = inp;
  saveHvacState();

  let res = null;
  try {
    const resp = await fetch("/api/hvac/duct_check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(inp)
    });
    if (resp.ok) res = await resp.json();
  } catch (e) {}

  if (!res || !res.ok) res = calcDuctOfflineJS(inp);
  HVAC_STATE.lastDuct = res;
  renderDuctCheckerUI(res);
}

function renderDuctCheckerUI(res) {
  const out = document.getElementById("dc-results-panel");
  if (!out) return;
  const pb = res.pressure_breakdown || {};
  const md = res.main_duct || {}, bd = res.branch_duct || {}, fd = res.flex_duct || {}, rd = res.return_duct || {};
  const ratio = Math.min(100, Math.round((pb.total_pa / Math.max(1, res.esp_max_pa)) * 100));
  const ratedPct = Math.min(100, Math.round((res.esp_rated_pa / Math.max(1, res.esp_max_pa)) * 100));
  const barCol = res.esp_status === "OK_RATED" ? "#16A34A" : (res.esp_status === "OK_MAX" ? "#0077B6" : "#991B1B");

  const excelBox = res.duct_excel ? `
    <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-left:4px solid #005A8D;border-radius:8px;padding:10px 12px;margin-bottom:12px;font-size:12px;">
      <strong style="color:#005A8D;">📐 Thông số Côn Đầu Máy Chuẩn Excel Daikin (${res.model}):</strong>
      Côn cấp: <strong>${res.duct_excel.supply_collar} mm</strong> &nbsp;|&nbsp;
      Côn hồi: <strong>${res.duct_excel.return_collar} mm</strong> &nbsp;|&nbsp;
      Đề xuất: <strong>${res.duct_excel.propose}</strong> &nbsp;|&nbsp;
      Hộp gió chuẩn: <strong>${res.duct_excel.std_box}</strong>
    </div>
  ` : "";

  out.innerHTML = `
    ${excelBox}
    <div class="config-card" style="margin-bottom:14px;">
      <div class="config-card-head" style="display:flex;justify-content:space-between;align-items:center;">
        <span>📊 KẾT QUẢ KIỂM TRA THỦY LỰC ỐNG GIÓ & CỘT ÁP QUẠT ESP (${res.model})</span>
        <span style="font-size:12px;font-weight:700;">${res.noise_status}</span>
      </div>
      <div class="config-card-body">
        <!-- ESP GAUGE BAR -->
        <div style="background:#F8FAFC;border:1px solid #CBD5E1;border-radius:10px;padding:12px 14px;">
          <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px;">
            <span style="font-weight:700;color:#0F172A;font-size:13px;">Tổng trở lực tuyến ống xa nhất: <strong style="color:${barCol};font-size:17px;">${pb.total_pa} Pa</strong></span>
            <span style="font-size:12px;color:#475569;">ESP Định mức: <strong>${res.esp_rated_pa} Pa</strong> • ESP Tối đa: <strong>${res.esp_max_pa} Pa</strong> (Dư ${pb.esp_margin_pa} Pa)</span>
          </div>
          <div style="position:relative;height:18px;background:#E2E8F0;border-radius:9px;overflow:hidden;">
            <div style="width:${ratio}%;height:100%;background:${barCol};border-radius:9px;transition:width 0.3s;"></div>
            <div title="Mốc ESP Định mức ${res.esp_rated_pa} Pa" style="position:absolute;top:0;bottom:0;left:${ratedPct}%;width:2.5px;background:#0F172A;"></div>
          </div>
          <div style="margin-top:8px;font-size:12.5px;font-weight:700;color:${barCol};">${res.esp_verdict}</div>
        </div>

        <!-- HYDRAULIC TABLE -->
        <div class="data-table-wrap">
          <table class="clean-table">
            <thead>
              <tr>
                <th>Đoạn ống gió</th>
                <th>Kích thước chuẩn (mm)</th>
                <th>Lưu lượng</th>
                <th>Vận tốc</th>
                <th>Ma sát đơn vị</th>
                <th>Tổn thất ΔP</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Ống gió chính (Tôn tráng kẽm)</strong></td>
                <td><strong style="color:#005A8D;">${md.w_mm} × ${md.h_mm} mm</strong> <span style="color:#64748B;">(≈ Ø${md.round_equiv_mm})</span></td>
                <td>${formatNum(res.airflow_m3h)} m³/h</td>
                <td><strong>${md.hyd?.velocity_ms} m/s</strong></td>
                <td>${md.hyd?.dp_pa_m} Pa/m</td>
                <td><strong>${md.dp_pa} Pa</strong></td>
              </tr>
              <tr>
                <td><strong>Ống gió nhánh cứng (${res.num_branches} nhánh)</strong></td>
                <td><strong style="color:#005A8D;">${bd.w_mm} × ${bd.h_mm} mm</strong> <span style="color:#64748B;">(≈ Ø${bd.round_mm})</span></td>
                <td>${formatNum(res.branch_airflow_m3h)} m³/h</td>
                <td><strong>${bd.hyd?.velocity_ms} m/s</strong></td>
                <td>${bd.hyd?.dp_pa_m} Pa/m</td>
                <td><strong>${bd.dp_pa} Pa</strong></td>
              </tr>
              <tr>
                <td><strong>Ống gió mềm bảo ôn</strong></td>
                <td><strong style="color:#991B1B;">Ø${fd.dia_mm} mm</strong> (L = ${fd.len_m}m/nhánh)</td>
                <td>${formatNum(res.branch_airflow_m3h)} m³/h</td>
                <td><strong>${fd.hyd?.velocity_ms} m/s</strong></td>
                <td>${fd.hyd?.dp_pa_m} Pa/m</td>
                <td><strong>${fd.dp_pa} Pa</strong></td>
              </tr>
              <tr>
                <td><strong>Ống gió hồi (Tôn tráng kẽm)</strong></td>
                <td><strong style="color:#005A8D;">${rd.w_mm} × ${rd.h_mm} mm</strong></td>
                <td>${formatNum(res.airflow_m3h)} m³/h</td>
                <td><strong>${rd.hyd?.velocity_ms} m/s</strong></td>
                <td>${rd.hyd?.dp_pa_m} Pa/m</td>
                <td><strong>${rd.dp_pa} Pa</strong></td>
              </tr>
              <tr>
                <td><strong>Cục bộ (Cút, Tê, VCD) + Cửa gió</strong></td>
                <td>Cút 90° + Van VCD + Cửa cấp/hồi</td>
                <td>—</td>
                <td>—</td>
                <td>—</td>
                <td><strong>${(pb.fittings_pa + pb.grilles_pa).toFixed(1)} Pa</strong></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- GRILLES & MATERIAL TAKEOFF -->
        <div style="display:grid;grid-template-columns:1.3fr 1fr;gap:12px;">
          <div style="background:#F8FAFC;border:1px solid #CBD5E1;border-radius:8px;padding:10px 12px;font-size:12px;line-height:1.6;">
            <strong style="color:#005A8D;">🎯 Đề xuất Cửa gió & Van chỉnh gió:</strong><br/>
            • ${res.grilles?.supply_rec}<br/>
            • ${res.grilles?.return_rec}<br/>
            • ${res.grilles?.vcd_rec}
          </div>
          <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;padding:10px 12px;font-size:12px;line-height:1.6;display:flex;flex-direction:column;justify-content:space-between;">
            <div>
              <strong style="color:#991B1B;">📦 Bóc tách sơ bộ vật tư ống gió:</strong><br/>
              • Ống gió tôn mạ kẽm bảo ôn: <strong>${res.sheet_metal_m2} m²</strong><br/>
              • Ống gió mềm bảo ôn Ø${fd.dia_mm}: <strong>${res.flex_total_m} md</strong>
            </div>
            <button class="btn btn-sm btn-primary" style="margin-top:8px;" onclick="pushDuctMaterialsToCart()">🛒 Đẩy Vật Tư Ống Gió Sang Giỏ Báo Giá</button>
          </div>
        </div>
      </div>
    </div>
  `;
}

function pushDuctMaterialsToCart() {
  const res = HVAC_STATE.lastDuct;
  if (!res || !res.ok || typeof QUOTE === "undefined") return;
  const pushCustom = (name, unit, qty, price) => {
    QUOTE.install_items.push({
      uid: makeUid(), mat_id: "DUCT_CHK_" + Math.random().toString(36).slice(2, 6),
      group_code: "V", group_name: "V. Côn đầu máy, Ống gió & Cửa gió",
      name, brand: "Minh Phú / VN", cost_type: "Vật tư", unit, qty: Math.round(qty * 10) / 10, base_price: price
    });
  };
  if (res.sheet_metal_m2 > 0) pushCustom(`Ống gió tôn tráng kẽm bảo ôn (${res.model} — ${res.main_duct.w_mm}×${res.main_duct.h_mm})`, "m²", res.sheet_metal_m2, 420000);
  if (res.flex_total_m > 0) pushCustom(`Ống gió mềm có bảo ôn bông thủy tinh Ø${res.flex_duct.dia_mm} (${res.model})`, "m", res.flex_total_m, 145000);
  pushCustom(`Cửa gió cấp Linear Slot / Nan bầu dục (${res.model})`, "Cái", res.num_branches, 680000);
  pushCustom(`Cửa gió hồi có lưới lọc bụi (${res.model})`, "Cái", 1, 750000);
  if (typeof persistQuoteState === "function") persistQuoteState();
  showToast(`🛒 Đã đẩy vật tư ống gió (${res.sheet_metal_m2} m² tôn + ${res.flex_total_m}m ống mềm + cửa gió) sang Phần B Giỏ Báo Giá!`);
}

/* ---------------- TAB 4: COOLPACK R410A / R32 & DAIKIN PIPING ---------------- */
function populateCoolpackModelDropdown() {
  const sel = document.getElementById("cp-model-preset");
  if (!sel || typeof DB === "undefined") return;
  const outs = DB.products.filter(p => (p.category_id || "").includes("_OUT") || p.category_id === "SKY_DUCT" || p.category_id === "SKY_CASSETTE");
  sel.innerHTML = `<option value="">-- Chọn nhanh Model Daikin để lấy Công suất & Ống lỏng --</option>` +
    outs.map(p => `<option value="${p.id}">${p.model} (${p.cooling_kw} kW | Gas: ${p.refrigerant || "R410A"} | Ống: ${p.gas_pipe || "—"})</option>`).join("");
}

function onCoolpackModelSelect() {
  const id = document.getElementById("cp-model-preset")?.value;
  if (!id || typeof DB === "undefined") return;
  const p = DB.products.find(x => x.id === id);
  if (!p) return;
  if (p.cooling_kw > 0) document.getElementById("cp-rated-kw").value = p.cooling_kw;
  if (p.refrigerant && p.refrigerant.includes("32")) document.getElementById("cp-ref").value = "R32";
  else document.getElementById("cp-ref").value = "R410A";
  const mPipe = String(p.gas_pipe || "").match(/(\d+(?:\.\d+)?)/);
  if (mPipe) {
    const od = mPipe[1];
    const selOd = document.getElementById("cp-liq-od");
    if (selOd && Array.from(selOd.options).some(o => o.value === od)) selOd.value = od;
  }
  runCoolpackCalc();
}

async function runCoolpackCalc() {
  const inp = {
    refrigerant: document.getElementById("cp-ref")?.value || "R410A",
    pressure_unit: document.getElementById("cp-punit")?.value || "bar",
    p_suction: Number(document.getElementById("cp-psuc")?.value ?? 8.6),
    p_discharge: Number(document.getElementById("cp-pdis")?.value ?? 27.8),
    t_suction_meas: Number(document.getElementById("cp-tsuc")?.value ?? 13.0),
    t_liquid_meas: Number(document.getElementById("cp-tliq")?.value ?? 40.5),
    pipe_length_m: Number(document.getElementById("cp-len")?.value ?? 38),
    height_diff_m: Number(document.getElementById("cp-height")?.value ?? 12),
    rated_kw: Number(document.getElementById("cp-rated-kw")?.value ?? 40),
    liquid_pipe_od: document.getElementById("cp-liq-od")?.value || "12.7",
    precharged_m: Number(document.getElementById("cp-precharge")?.value ?? 0)
  };
  HVAC_STATE.coolpackInput = inp;
  saveHvacState();

  let res = null;
  try {
    const resp = await fetch("/api/hvac/coolpack_check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(inp)
    });
    if (resp.ok) res = await resp.json();
  } catch (e) {}

  if (!res || !res.ok) res = calcCoolpackOfflineJS(inp);
  HVAC_STATE.lastCoolpack = res;
  renderCoolpackUI(res);
}

function renderCoolpackUI(res) {
  const out = document.getElementById("cp-results-panel");
  if (!out) return;
  const pip = res.piping || {};
  const shCol = res.sh_status === "OK" ? "#16A34A" : "#991B1B";
  const scCol = res.sc_status === "OK" ? "#16A34A" : "#991B1B";
  out.innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
      <div class="config-card">
        <div class="config-card-head">❄️ CHU TRÌNH LẠNH ${res.refrigerant} (GWP ${res.gwp} • ${res.safety_class})</div>
        <div class="config-card-body">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
            <div class="hvac-kpi-card blue" style="padding:10px 12px;">
              <div class="kpi-lbl">NHIỆT ĐỘ BAY HƠI (t_evap)</div>
              <div class="kpi-val" style="font-size:20px;">${res.t_evap_c} °C</div>
              <div class="kpi-sub">${res.p_suction_bar} bar (${res.p_suction_psi} psi)</div>
            </div>
            <div class="hvac-kpi-card red" style="padding:10px 12px;">
              <div class="kpi-lbl">NHIỆT ĐỘ NGƯNG TỤ (t_cond)</div>
              <div class="kpi-val" style="font-size:20px;">${res.t_cond_c} °C</div>
              <div class="kpi-sub">${res.p_discharge_bar} bar (${res.p_discharge_psi} psi)</div>
            </div>
          </div>

          <div style="background:#F8FAFC;border:1px solid #CBD5E1;border-left:4px solid ${shCol};border-radius:8px;padding:10px 12px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <strong>Độ quá nhiệt (Superheat ΔT_SH)</strong>
              <strong style="font-size:17px;color:${shCol};">${res.superheat_k} K</strong>
            </div>
            <div style="font-size:12px;color:#334155;margin-top:4px;">${res.sh_diag}</div>
          </div>

          <div style="background:#F8FAFC;border:1px solid #CBD5E1;border-left:4px solid ${scCol};border-radius:8px;padding:10px 12px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <strong>Độ quá lạnh (Subcooling ΔT_SC)</strong>
              <strong style="font-size:17px;color:${scCol};">${res.subcooling_k} K</strong>
            </div>
            <div style="font-size:12px;color:#334155;margin-top:4px;">${res.sc_diag}</div>
          </div>

          <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;padding:9px 12px;display:flex;justify-content:space-between;align-items:center;">
            <span style="font-weight:700;color:#005A8D;">Hiệu suất chu trình COP ước tính (Inverter):</span>
            <strong style="font-size:18px;color:#005A8D;">COP ≈ ${res.cop_est}</strong>
          </div>
        </div>
      </div>

      <div class="config-card">
        <div class="config-card-head">🔧 SUY GIẢM CÔNG SUẤT ỐNG ĐỒNG & GAS NẠP BỔ SUNG DAIKIN</div>
        <div class="config-card-body">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
            <div class="hvac-kpi-card red" style="padding:10px 12px;">
              <div class="kpi-lbl">SUY GIẢM DO CHIỀU DÀI & CHÊNH CAO</div>
              <div class="kpi-val" style="font-size:20px;">-${pip.loss_pct}%</div>
              <div class="kpi-sub">Hệ số hiệu chỉnh: ×${pip.derate_factor}</div>
            </div>
            <div class="hvac-kpi-card blue" style="padding:10px 12px;">
              <div class="kpi-lbl">CÔNG SUẤT LẠNH THỰC TẾ</div>
              <div class="kpi-val" style="font-size:20px;">${pip.actual_kw} kW</div>
              <div class="kpi-sub">${formatNum(pip.actual_btu)} Btu/h (ĐM ${pip.rated_kw} kW)</div>
            </div>
          </div>

          <div style="background:#FEF2F2;border:1.5px solid #FECACA;border-radius:10px;padding:14px;text-align:center;">
            <div style="font-size:12px;font-weight:700;color:#991B1B;text-transform:uppercase;">LƯỢNG GAS ${res.refrigerant} CẦN NẠP BỔ SUNG (CÂN ĐIỆN TỬ)</div>
            <div style="font-size:28px;font-weight:700;color:#991B1B;margin:4px 0;">+${pip.extra_charge_kg} kg</div>
            <div style="font-size:12px;color:#475569;">Ống lỏng Ø${pip.liquid_pipe_od} mm • Định mức chuẩn Daikin: <strong>${pip.charge_rate_kg_m} kg/m</strong> • Dài ${pip.eq_len_m} m</div>
          </div>

          <div style="font-size:12px;color:#475569;line-height:1.55;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:9px 12px;">
            💡 <strong>Lưu ý thi công Minh Phú:</strong> Hút chân không sâu đạt ≤ -755 mmHg (≤ 500 micron) trong tối thiểu 60 phút, giữ áp 30 phút không tụt áp trước khi nạp bổ sung gas lỏng bằng cân điện tử.
          </div>
        </div>
      </div>
    </div>
  `;
}
