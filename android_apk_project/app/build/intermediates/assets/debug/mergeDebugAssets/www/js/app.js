/* ==========================================================================
   app.js — Core State, Model Lookup, Duct Plenum CAD SVG, PDF Viewer & Admin
   ========================================================================== */

const STORAGE_KEYS = {
  PRICE_OVERRIDES: "mp_daikin_price_overrides_v1",
  MAT_OVERRIDES: "mp_daikin_mat_overrides_v1",
  CUSTOM_MODELS: "mp_daikin_custom_models_v1",
  CUSTOM_MATS: "mp_daikin_custom_mats_v1",
  COMPANY: "mp_daikin_company_v1",
  CART: "mp_daikin_current_cart_v1",
  SAVED_PROJECTS: "mp_daikin_saved_projects_v1"
};

let DB = JSON.parse(JSON.stringify(window.DAIKIN_INITIAL_DB));
let activeSystem = "ALL";
let adminPriceTab = "equip";
let currentPdfState = { file: "", page: 1, totalPages: 1 };

function formatVND(num) {
  const n = Math.round(Number(num) || 0);
  return n.toLocaleString("vi-VN") + " đ";
}

function formatNum(num) {
  const n = Number(num) || 0;
  return n.toLocaleString("vi-VN");
}

function showToast(msg) {
  const box = document.getElementById("toast-container");
  if (!box) return;
  const el = document.createElement("div");
  el.className = "toast";
  el.textContent = msg;
  box.appendChild(el);
  setTimeout(() => {
    el.style.opacity = "0";
    el.style.transition = "opacity 0.3s";
    setTimeout(() => el.remove(), 320);
  }, 2600);
}

/* ---------------- PERSISTENCE & OVERRIDES ---------------- */
function applyStateBlobToDB(blob) {
  if (!blob || typeof blob !== "object") return;
  if (blob.company) {
    DB.company = Object.assign({}, DB.company, blob.company);
    if (blob.company.bank) {
      DB.company.bank = Object.assign({}, window.DAIKIN_INITIAL_DB.company.bank, blob.company.bank);
    }
  }
  if (Array.isArray(blob.custom_models)) {
    blob.custom_models.forEach(cm => {
      const idx = DB.products.findIndex(p => p.id === cm.id);
      if (idx >= 0) DB.products[idx] = cm;
      else DB.products.unshift(cm);
    });
  }
  if (Array.isArray(blob.custom_mats)) {
    blob.custom_mats.forEach(mm => {
      const idx = DB.materials.findIndex(m => m.id === mm.id);
      if (idx >= 0) DB.materials[idx] = mm;
      else DB.materials.unshift(mm);
    });
  }
  if (blob.prices && typeof blob.prices === "object") {
    DB.products.forEach(p => {
      const ov = blob.prices[p.id];
      if (ov !== undefined) {
        if (typeof ov === "object" && ov !== null) {
          if (ov.price !== undefined) p.price = Number(ov.price) || 0;
          if (ov.unit) p.unit = ov.unit;
          if (ov.origin) p.origin = ov.origin;
        } else {
          p.price = Number(ov) || 0;
        }
      }
    });
  }
  if (blob.mat_overrides && typeof blob.mat_overrides === "object") {
    DB.materials.forEach(m => {
      const mov = blob.mat_overrides[m.id];
      if (mov && typeof mov === "object") {
        if (mov.base_price !== undefined) m.base_price = Number(mov.base_price) || 0;
        if (mov.cost_type) m.cost_type = mov.cost_type;
        if (mov.unit) m.unit = mov.unit;
        if (mov.brand) m.brand = mov.brand;
      }
    });
  }
}

function loadOverrides() {
  try {
    const blob = {
      company: JSON.parse(localStorage.getItem(STORAGE_KEYS.COMPANY) || "null"),
      custom_models: JSON.parse(localStorage.getItem(STORAGE_KEYS.CUSTOM_MODELS) || "[]"),
      custom_mats: JSON.parse(localStorage.getItem(STORAGE_KEYS.CUSTOM_MATS) || "[]"),
      prices: JSON.parse(localStorage.getItem(STORAGE_KEYS.PRICE_OVERRIDES) || "{}"),
      mat_overrides: JSON.parse(localStorage.getItem(STORAGE_KEYS.MAT_OVERRIDES) || "{}")
    };
    applyStateBlobToDB(blob);
  } catch (e) {
    console.warn("Load overrides warning:", e);
  }
}

function syncBackupToDesktop() {
  try {
    const payload = {
      company: DB.company,
      prices: JSON.parse(localStorage.getItem(STORAGE_KEYS.PRICE_OVERRIDES) || "{}"),
      mat_overrides: JSON.parse(localStorage.getItem(STORAGE_KEYS.MAT_OVERRIDES) || "{}"),
      custom_models: JSON.parse(localStorage.getItem(STORAGE_KEYS.CUSTOM_MODELS) || "[]"),
      custom_mats: JSON.parse(localStorage.getItem(STORAGE_KEYS.CUSTOM_MATS) || "[]"),
      ai_config: JSON.parse(localStorage.getItem("mp_hvac_ai_config_v1") || "null"),
      ai_profiles: JSON.parse(localStorage.getItem("mp_hvac_ai_profiles_v1") || "null")
    };
    const jsonStr = JSON.stringify(payload);
    if (window.pywebview && window.pywebview.api && window.pywebview.api.save_user_state) {
      window.pywebview.api.save_user_state(jsonStr);
    } else {
      fetch("/api/user_state", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: jsonStr
      }).catch(() => {});
    }
  } catch (e) {}
}

async function loadDesktopBackupIfAvailable() {
  try {
    let saved = null;
    if (window.pywebview && window.pywebview.api && window.pywebview.api.load_user_state) {
      const res = await window.pywebview.api.load_user_state();
      if (res && res.ok && res.data) saved = res.data;
    } else {
      const resp = await fetch("/api/user_state");
      if (resp.ok) {
        const res = await resp.json();
        if (res && res.ok && res.data) saved = res.data;
      }
    }
    if (saved) {
      if (saved.company && !localStorage.getItem(STORAGE_KEYS.COMPANY)) {
        localStorage.setItem(STORAGE_KEYS.COMPANY, JSON.stringify(saved.company));
      }
      if (saved.prices && !localStorage.getItem(STORAGE_KEYS.PRICE_OVERRIDES)) {
        localStorage.setItem(STORAGE_KEYS.PRICE_OVERRIDES, JSON.stringify(saved.prices));
      }
      if (saved.mat_overrides && !localStorage.getItem(STORAGE_KEYS.MAT_OVERRIDES)) {
        localStorage.setItem(STORAGE_KEYS.MAT_OVERRIDES, JSON.stringify(saved.mat_overrides));
      }
      if (saved.custom_models && !localStorage.getItem(STORAGE_KEYS.CUSTOM_MODELS)) {
        localStorage.setItem(STORAGE_KEYS.CUSTOM_MODELS, JSON.stringify(saved.custom_models));
      }
      if (saved.custom_mats && !localStorage.getItem(STORAGE_KEYS.CUSTOM_MATS)) {
        localStorage.setItem(STORAGE_KEYS.CUSTOM_MATS, JSON.stringify(saved.custom_mats));
      }
      if (saved.ai_config && !localStorage.getItem("mp_hvac_ai_config_v1")) {
        localStorage.setItem("mp_hvac_ai_config_v1", JSON.stringify(saved.ai_config));
      }
      if (saved.ai_profiles && !localStorage.getItem("mp_hvac_ai_profiles_v1")) {
        localStorage.setItem("mp_hvac_ai_profiles_v1", JSON.stringify(saved.ai_profiles));
      }
      loadOverrides();
      renderCatalog();
    }
  } catch (e) {}
}

function savePriceOverride(prodId, newPrice, extraFields) {
  let pMap = {};
  try {
    pMap = JSON.parse(localStorage.getItem(STORAGE_KEYS.PRICE_OVERRIDES) || "{}");
  } catch (e) {}
  const prod = DB.products.find(p => p.id === prodId);
  const existing = typeof pMap[prodId] === "object" && pMap[prodId] !== null
    ? pMap[prodId]
    : { price: prod ? prod.price : 0 };
  if (newPrice !== null && newPrice !== undefined) {
    existing.price = Math.max(0, Number(newPrice) || 0);
    if (prod) prod.price = existing.price;
  }
  if (extraFields && typeof extraFields === "object") {
    Object.assign(existing, extraFields);
    if (prod) Object.assign(prod, extraFields);
  }
  pMap[prodId] = existing;
  localStorage.setItem(STORAGE_KEYS.PRICE_OVERRIDES, JSON.stringify(pMap));
  syncBackupToDesktop();
}

function saveMaterialOverride(matId, updates) {
  let mMap = {};
  try {
    mMap = JSON.parse(localStorage.getItem(STORAGE_KEYS.MAT_OVERRIDES) || "{}");
  } catch (e) {}
  const mat = DB.materials.find(m => m.id === matId);
  const cur = mMap[matId] || {};
  Object.assign(cur, updates);
  if (cur.base_price !== undefined) cur.base_price = Math.max(0, Number(cur.base_price) || 0);
  mMap[matId] = cur;
  if (mat) Object.assign(mat, cur);
  localStorage.setItem(STORAGE_KEYS.MAT_OVERRIDES, JSON.stringify(mMap));
  syncBackupToDesktop();
}

/* ---------------- NAVIGATION ---------------- */
const VIEW_TITLES = {
  catalog: [
    "Tra Cứu Model, Thông Số Kỹ Thuật & Côn Đầu Máy Daikin",
    "Cơ sở dữ liệu chuẩn hóa từ Báo giá VRV, Bảng Côn Đầu Dàn Lạnh & 15 Catalogue Tiếng Việt"
  ],
  cart: [
    "Giỏ Hàng Công Trình & Bóc Tách Nhân Công Vật Tư",
    "Tùy chọn báo giá Thiết bị / Nhân công Vật tư / Trọn gói với hệ số nhân linh hoạt"
  ],
  preview: [
    "Mẫu Báo Giá Chuyên Nghiệp Minh Phú & Xuất File (.XLSX / .PDF)",
    "Thiết kế Gradient hiện đại kèm thông tin pháp lý Minh Phú & mã QR thanh toán đơn hàng"
  ],
  loadcalc: [
    "Trung Tâm Tính Nhiệt TCVN 5687:2024 • Bóc Tách PDF/CAD AI • Daikin Duct Checker • CoolPack",
    "Tính tải nhiệt đa phòng chuẩn Việt Nam (QCVN 09:2017/BXD), bóc tách bản vẽ CAD/PDF, tính ống gió & kiểm tra gas"
  ],
  library: [
    "Thư Viện Catalogue Thương Mại & Kỹ Thuật Daikin Tiếng Việt",
    "Xem trực tiếp từng trang tài liệu PDF gốc trong thư mục dự án hoặc mở DaikinCatalog.com"
  ],
  admin: [
    "Quản Trị Bảng Giá, Thông Tin Công Ty Minh Phú & Cấu Hình VietQR",
    "Tùy chỉnh thông tin pháp lý, tài khoản ngân hàng nhận thanh toán QR và thêm Model mới"
  ]
};

function switchView(viewName) {
  document.querySelectorAll(".view-panel").forEach(el => el.classList.remove("active"));
  const target = document.getElementById("view-" + viewName);
  if (target) target.classList.add("active");

  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.classList.toggle("active", btn.getAttribute("data-view") === viewName);
  });

  if (VIEW_TITLES[viewName]) {
    document.getElementById("topbar-heading").textContent = VIEW_TITLES[viewName][0];
    document.getElementById("topbar-sub").textContent = VIEW_TITLES[viewName][1];
  }

  if (viewName === "cart" && typeof renderCartTables === "function") {
    renderCartTables();
    renderSavedProjectsList();
  } else if (viewName === "preview" && typeof renderQuotePreview === "function") {
    renderQuotePreview();
  } else if (viewName === "loadcalc") {
    if (typeof initHvacPro === "function") initHvacPro();
    else runLoadCalc();
  } else if (viewName === "library") {
    renderLibraryView();
  } else if (viewName === "admin") {
    populateAdminSettings();
    if (typeof populateAiSettingsUI === "function") populateAiSettingsUI();
  }
}

function openExternalLink(url) {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.open_url) {
    window.pywebview.api.open_url(url);
  } else if (window.AndroidNative && window.AndroidNative.openExternalUrl) {
    window.AndroidNative.openExternalUrl(url);
  } else if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.iosNative) {
    window.webkit.messageHandlers.iosNative.postMessage({ action: "openExternalUrl", url });
  } else {
    window.open(url, "_blank");
  }
}

/* ---------------- CATALOG FILTER & SEARCH ---------------- */
function populateCategorySelect() {
  const sel = document.getElementById("category-select");
  const currentVal = sel.value;
  sel.innerHTML = `<option value="ALL">Tất cả dòng sản phẩm (${DB.categories.length} mục lục)</option>`;
  DB.categories.forEach(c => {
    if (activeSystem !== "ALL" && c.system !== activeSystem) return;
    const count = DB.products.filter(p => p.category_id === c.id).length;
    const opt = document.createElement("option");
    opt.value = c.id;
    opt.textContent = `${c.name} (${count})`;
    sel.appendChild(opt);
  });
  if ([...sel.options].some(o => o.value === currentVal)) sel.value = currentVal;
}

function selectSystem(sys, btnEl) {
  activeSystem = sys;
  document.querySelectorAll("#system-pills .pill").forEach(b => b.classList.remove("active"));
  if (btnEl) btnEl.classList.add("active");
  document.getElementById("category-select").value = "ALL";
  populateCategorySelect();
  renderCatalog();
}

function resetCatalogFilters() {
  document.getElementById("search-input").value = "";
  document.getElementById("category-select").value = "ALL";
  document.getElementById("filter-special").value = "ALL";
  activeSystem = "ALL";
  document.querySelectorAll("#system-pills .pill").forEach(b => {
    b.classList.toggle("active", b.getAttribute("data-sys") === "ALL");
  });
  populateCategorySelect();
  renderCatalog();
}

function getFilteredProducts() {
  const q = (document.getElementById("search-input").value || "").trim().toLowerCase();
  const catId = document.getElementById("category-select").value;
  const spec = document.getElementById("filter-special").value;

  const catMap = {};
  DB.categories.forEach(c => (catMap[c.id] = c));

  return DB.products.filter(p => {
    const cat = catMap[p.category_id] || {};
    if (activeSystem !== "ALL" && cat.system !== activeSystem) return false;
    if (catId !== "ALL" && p.category_id !== catId) return false;
    if (spec === "PRICED" && (!p.price || p.price <= 0)) return false;
    if (spec === "DUCT_ONLY" && !p.duct) return false;
    if (spec === "OUTDOOR" && !(cat.group || "").toLowerCase().includes("dàn nóng")) return false;
    if (spec === "INDOOR" && !(cat.group || "").toLowerCase().includes("dàn lạnh") && !p.duct && !p.ceiling_opening) return false;

    if (q) {
      const ductStr = p.duct ? `${p.duct.supply_collar} ${p.duct.return_collar} ${p.duct.propose} ${p.duct.std_box}` : "";
      const hay = `${p.model} ${p.name} ${p.hp} ${p.cooling_btu} ${p.cooling_kw} ${p.gas_pipe} ${p.dimensions} ${p.origin} ${cat.name} ${ductStr}`.toLowerCase();
      const tokens = q.split(/\s+/);
      if (!tokens.every(t => hay.includes(t))) return false;
    }
    return true;
  });
}

function renderCatalog() {
  const list = getFilteredProducts();
  const mode = document.getElementById("view-mode-select").value;
  const container = document.getElementById("catalog-container");
  document.getElementById("badge-total-models").textContent = DB.products.length;
  document.getElementById("catalog-result-text").innerHTML =
    `Đang hiển thị <strong>${list.length}</strong> / ${DB.products.length} model sản phẩm Daikin`;

  const catMap = {};
  DB.categories.forEach(c => (catMap[c.id] = c));

  if (list.length === 0) {
    container.innerHTML = `
      <div class="filter-card" style="text-align:center;padding:42px 20px;">
        <div style="font-size:36px;margin-bottom:8px;">🔎</div>
        <h3 style="margin-bottom:6px;">Không tìm thấy Model phù hợp trong bộ lọc hiện tại</h3>
        <p style="color:#64748B;font-size:13px;margin-bottom:14px;">Bạn có thể đặt lại bộ lọc, tra cứu trên DaikinCatalog.com hoặc thêm nhanh Model mới vào kho.</p>
        <div style="display:flex;gap:10px;justify-content:center;">
          <button class="btn btn-outline" onclick="resetCatalogFilters()">Đặt lại bộ lọc</button>
          <button class="btn btn-ice" onclick="openExternalLink('https://www.daikincatalog.com/library/site/vietnam/book-lists/')">🌐 Tra trên DaikinCatalog.com</button>
          <button class="btn btn-primary" onclick="openAddModelModal()">➕ Thêm Model mới</button>
        </div>
      </div>`;
    return;
  }

  if (mode === "table") {
    container.innerHTML = `
      <div class="data-table-wrap">
        <table class="clean-table">
          <thead>
            <tr>
              <th>Ảnh</th>
              <th>Model</th>
              <th>Tên & Dòng sản phẩm</th>
              <th>Công suất</th>
              <th>KT Máy (mm) / Nặng</th>
              <th>Ống Gas</th>
              <th>KT Côn Đầu Cấp / Hồi</th>
              <th>Đơn giá gốc</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            ${list.map(p => `
              <tr>
                <td style="width:74px;cursor:pointer;" onclick="openProductModal('${p.id}')">
                  <div style="width:66px;height:52px;background:#fff;border:1px solid #E2E8F0;border-radius:8px;display:flex;align-items:center;justify-content:center;padding:3px;">
                    <img src="${p.image}" style="max-width:100%;max-height:100%;object-fit:contain;" />
                  </div>
                </td>
                <td><strong style="color:#0F172A;cursor:pointer;" onclick="openProductModal('${p.id}')">${p.model}</strong></td>
                <td>
                  <div style="font-weight:600;">${p.name}</div>
                  <div style="font-size:11px;color:#64748B;">${(catMap[p.category_id] || {}).name || ""} • ${p.origin}</div>
                </td>
                <td><strong>${p.cooling_btu ? formatNum(p.cooling_btu) + " Btu/h" : p.hp}</strong><div style="font-size:11px;color:#64748B;">${p.cooling_kw ? p.cooling_kw + " kW" : ""}</div></td>
                <td><div>${p.dimensions || "—"}</div><div style="font-size:11px;color:#64748B;">${p.weight || ""}</div></td>
                <td><strong>${p.gas_pipe || "—"}</strong></td>
                <td>
                  ${p.duct
                    ? `<span style="color:#0369A1;font-weight:700;">Cấp: ${p.duct.supply_collar}</span><br/><span style="font-size:11px;color:#475569;">Hồi: ${p.duct.return_collar}</span>`
                    : (p.ceiling_opening ? `<span style="font-size:11px;color:#475569;">Lỗ trần: ${p.ceiling_opening}</span>` : "—")}
                </td>
                <td>
                  <input type="number" class="price-edit-input" step="10000" value="${p.price || 0}" title="Sửa trực tiếp đơn giá gốc đầu vào (VNĐ)" onchange="savePriceOverride('${p.id}', this.value); showToast('Đã lưu giá gốc ' + '${p.model}: ' + formatVND(this.value));" />
                </td>
                <td style="white-space:nowrap;">
                  <button class="btn btn-sm btn-outline" onclick="openProductModal('${p.id}')">📐 Chi tiết</button>
                  <button class="btn btn-sm btn-primary" onclick="addToEquipCart('${p.id}', 1)">+ Giỏ</button>
                </td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>`;
    return;
  }

  // GRID VIEW — Crystal-clear Product Image + 6-item Technical Specs + Duct Collar + Quick Qty
  container.innerHTML = `<div class="product-grid">${list.map(p => {
    const cat = catMap[p.category_id] || {};
    return `
      <div class="prod-card">
        <div class="prod-img-stage" onclick="openProductModal('${p.id}')">
          <span class="badge-top-left">${cat.system || "DAIKIN"}</span>
          <span class="badge-top-right">${p.hp}</span>
          ${p.duct ? `<span class="badge-duct">📐 Côn cấp: ${p.duct.supply_collar} mm</span>` : ""}
          ${p.commercial_img ? `<button type="button" onclick="event.stopPropagation(); toggleCardImg(this, '${p.image}', '${p.commercial_img}')" style="position:absolute;bottom:8px;right:8px;background:#005A8D;color:#FFFFFF;border:1px solid #FFFFFF;border-radius:6px;font-size:10px;font-weight:700;padding:2px 7px;cursor:pointer;">🖼️ Đổi ảnh</button>` : ""}
          <img src="${p.image}" alt="${p.model}" loading="lazy" />
        </div>
        <div class="prod-body">
          <div style="display:flex;justify-content:space-between;align-items:baseline;gap:6px;">
            <div class="prod-model" style="cursor:pointer;" onclick="openProductModal('${p.id}')">${p.model}</div>
            <span style="font-size:10.5px;font-weight:700;color:#0369A1;background:#E0F2FE;padding:1px 6px;border-radius:4px;">${p.origin}</span>
          </div>
          <div class="prod-name">${p.name}</div>

          <div class="spec-mini-grid">
            <div class="spec-mini-item">
              <span>❄️ Công suất lạnh</span>
              <strong style="color:#0C4A6E;">${p.cooling_btu > 0 ? formatNum(p.cooling_btu) + " Btu/h" : p.hp} ${p.cooling_kw ? `(${p.cooling_kw}kW)` : ""}</strong>
            </div>
            <div class="spec-mini-item">
              <span>🔥 Sưởi ấm / Gas</span>
              <strong>${p.heating_btu > 0 ? formatNum(p.heating_btu) + " Btu" : "1 chiều"} • ${p.refrigerant || "R410A"}</strong>
            </div>
            <div class="spec-mini-item">
              <span>📏 Kích thước (C×R×S)</span>
              <strong>${(p.dimensions || "—").split("|")[0]} mm</strong>
            </div>
            <div class="spec-mini-item">
              <span>⚖️ Trọng lượng & Điện</span>
              <strong>${(p.weight || "—").split("|")[0]} • ${(p.power_supply || "").includes("3 pha") ? "3P 380V" : "1P 220V"}</strong>
            </div>
            <div class="spec-mini-item">
              <span>🔧 Ống đồng & Nước xả</span>
              <strong style="color:#991B1B;">${(p.gas_pipe || "—").replace("Cổ ống gió kết nối: ", "")}${p.drain_pipe ? " • " + p.drain_pipe : ""}</strong>
            </div>
            <div class="spec-mini-item">
              <span>💨 Lưu lượng & Độ ồn</span>
              <strong>${p.airflow || "—"} ${p.noise ? "• " + p.noise : ""}</strong>
            </div>
          </div>

          ${p.duct ? `
            <div class="duct-highlight-strip">
              🔧 Côn cấp: <strong>${p.duct.supply_collar}</strong> | Côn hồi: <strong>${p.duct.return_collar} mm</strong><br/>
              📦 ${p.duct.std_box || p.duct.propose}
            </div>
          ` : (p.ceiling_opening ? `
            <div class="duct-highlight-strip" style="background:#F8FAFC;border-color:#CBD5E1;color:#334155;">
              🔲 Lỗ mở trần: <strong>${p.ceiling_opening}</strong> ${p.panel_model ? `• Mặt nạ: <strong>${p.panel_model}</strong>` : ""}
            </div>
          ` : "")}

          <div class="prod-footer">
            <div style="cursor:pointer;" title="Bấm để sửa nhanh đơn giá gốc đầu vào" onclick="promptQuickPriceEdit('${p.id}')">
              ${p.price > 0
                ? `<div class="price-tag">${formatVND(p.price)} <span style="font-size:11px;font-weight:700;color:#005A8D;">✏️</span></div><div class="price-unit">Giá gốc / ${p.unit} (sửa nhanh)</div>`
                : `<div class="price-tag contact">✏️ Nhập giá gốc</div><div class="price-unit">ĐVT: ${p.unit}</div>`}
            </div>
            <div class="card-actions" style="align-items:center;">
              <button class="btn btn-sm btn-ice" title="Xem ảnh lớn, bản vẽ côn gió & Catalogue" onclick="openProductModal('${p.id}')">📐 Chi tiết</button>
              <input type="number" id="cqty-${p.id}" value="1" min="1" style="width:44px;padding:5px 4px;border:1px solid #CBD5E1;border-radius:6px;text-align:center;font-weight:700;font-size:12px;" title="Số lượng chọn" />
              <button class="btn btn-sm btn-primary" onclick="addToEquipCart('${p.id}', Number(document.getElementById('cqty-${p.id}').value||1))">+ Chọn</button>
            </div>
          </div>
        </div>
      </div>
    `;
  }).join("")}</div>`;
}

function toggleCardImg(btn, pngSrc, commSrc) {
  const stage = btn.parentElement;
  const img = stage ? stage.querySelector("img") : null;
  if (!img) return;
  const showingComm = img.getAttribute("data-comm") === "1";
  img.src = showingComm ? pngSrc : commSrc;
  img.setAttribute("data-comm", showingComm ? "0" : "1");
}

/* ---------------- ENGINEERING CAD SVG BLUEPRINT FOR DUCT & PLENUM ---------------- */
function parseSpigotSpec(text) {
  // Extracts count and diameter e.g. "4 cổ D200", "4D200", "5D200", "6D200", "4 cổ D250"
  let count = 2, dia = 200, boxW = 0, boxH = 220, plenDepth = 250;
  const m1 = text.match(/(\d+)\s*cổ\s*D(\d+)/i);
  const m2 = text.match(/trổ\s*đỉnh\s*(\d+)\s*D(\d+)/i);
  if (m2) {
    count = parseInt(m2[1], 10);
    dia = parseInt(m2[2], 10);
  } else if (m1) {
    count = parseInt(m1[1], 10);
    dia = parseInt(m1[2], 10);
  }
  const mb = text.match(/KT:\s*(\d+)\s*x\s*(\d+)/i);
  if (mb) {
    boxW = parseInt(mb[1], 10);
    boxH = parseInt(mb[2], 10);
  }
  const mh = text.match(/H(\d{3})/i);
  if (mh) plenDepth = parseInt(mh[1], 10);
  return { count, dia, boxW, boxH, plenDepth };
}

function buildDuctBlueprintSVG(p) {
  if (!p.duct) {
    if (p.ceiling_opening) {
      return `
      <svg viewBox="0 0 680 250" width="100%" style="background:#081224;border-radius:10px;border:1px solid #1E3A5F;">
        <defs>
          <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(56,189,248,0.08)" stroke-width="1"/>
          </pattern>
        </defs>
        <rect width="680" height="250" fill="url(#grid)" />
        <text x="18" y="26" fill="#38BDF8" font-size="12" font-weight="bold">SƠ ĐỒ KÍCH THƯỚC LỖ MỞ TRẦN & MẶT NẠ CASSETTE (${p.model})</text>
        <rect x="210" y="45" width="180" height="180" fill="rgba(56,189,248,0.08)" stroke="#38BDF8" stroke-width="2" rx="8"/>
        <rect x="228" y="63" width="144" height="144" fill="none" stroke="#FBBF24" stroke-width="1.8" stroke-dasharray="6,4"/>
        <rect x="242" y="77" width="116" height="116" fill="rgba(255,255,255,0.07)" stroke="#E2E8F0" stroke-width="1.5"/>
        <text x="300" y="138" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="bold">Thân máy</text>
        <text x="300" y="154" text-anchor="middle" fill="#93C5FD" font-size="10">${p.dimensions}</text>
        <text x="415" y="88" fill="#38BDF8" font-size="12" font-weight="bold">■ Mặt nạ ngoài: ${p.panel_dim || "950x950 mm"}</text>
        <text x="415" y="116" fill="#FBBF24" font-size="12" font-weight="bold">■ Lỗ mở trần thạch cao: ${p.ceiling_opening}</text>
        <text x="415" y="144" fill="#E2E8F0" font-size="12">■ Ống đồng kết nối: ${p.gas_pipe}</text>
        <text x="415" y="172" fill="#E2E8F0" font-size="12">■ Ống thoát nước xả: ${p.drain_pipe}</text>
      </svg>`;
    }
    return "";
  }

  const d = p.duct;
  const combinedText = `${d.propose || ""} | ${d.std_box || ""}`;
  const sp = parseSpigotSpec(combinedText);
  const mouthW = d.mouth_w || parseInt((d.supply_collar || "795x180").split(/[xX]/)[0], 10) || 795;
  const mouthH = d.mouth_h || parseInt((d.supply_collar || "795x180").split(/[xX]/)[1], 10) || 180;
  const boxW = sp.boxW || Math.max(mouthW, sp.count * (sp.dia + 60));
  const boxH = sp.boxH || Math.max(mouthH + 40, 220);

  // Compute spigot circle positions evenly inside plenum box (x from 140 to 430)
  const plenX = 110, plenW = 300, plenY = 128, plenDepthPx = 68;
  const neckW = Math.max(170, Math.round((mouthW / Math.max(boxW, mouthW)) * plenW));
  const neckX = plenX + (plenW - neckW) / 2;

  let circlesSvg = "";
  const n = Math.max(2, Math.min(6, sp.count));
  const step = plenW / n;
  for (let i = 0; i < n; i++) {
    const cx = Math.round(plenX + step * (i + 0.5));
    const cy = plenY + plenDepthPx + 18;
    circlesSvg += `
      <line x1="${cx}" y1="${plenY + plenDepthPx}" x2="${cx}" y2="${cy + 14}" stroke="#38BDF8" stroke-width="1.6"/>
      <ellipse cx="${cx}" cy="${cy + 14}" rx="18" ry="8" fill="rgba(56,189,248,0.22)" stroke="#38BDF8" stroke-width="1.8"/>
      <text x="${cx}" y="${cy + 34}" text-anchor="middle" fill="#BAE6FD" font-size="10" font-weight="bold">Ø${sp.dia}</text>
    `;
  }

  return `
  <svg viewBox="0 0 740 275" width="100%" style="background:#081224;border-radius:10px;border:1px solid #1E3A5F;">
    <defs>
      <pattern id="bpgrid" width="20" height="20" patternUnits="userSpaceOnUse">
        <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(56,189,248,0.08)" stroke-width="1"/>
      </pattern>
    </defs>
    <rect width="740" height="275" fill="url(#bpgrid)" />

    <text x="16" y="23" fill="#38BDF8" font-size="12" font-weight="bold">BẢN VẼ KỸ THUẬT CÔN ĐẦU MÁY & HỘP GIÓ GIẬT CẤP — MODEL: ${p.model}</text>

    <!-- PLAN VIEW (LEFT) -->
    <text x="260" y="44" text-anchor="middle" fill="#94A3B8" font-size="10.5" font-weight="bold">MẶT BẰNG THÂN MÁY - CỔ GIẬT - HỘP CÔN GIÓ ĐẦU CẤP</text>

    <!-- Return Collar at top of unit -->
    <rect x="${neckX - 14}" y="52" width="${neckW + 28}" height="12" fill="rgba(248,113,113,0.18)" stroke="#F87171" stroke-width="1.5"/>
    <text x="260" y="61" text-anchor="middle" fill="#FCA5A5" font-size="9.5" font-weight="bold">Côn đầu hồi: ${d.return_collar} mm</text>

    <!-- Indoor Unit Body -->
    <rect x="${neckX - 24}" y="64" width="${neckW + 48}" height="48" fill="rgba(226,232,240,0.1)" stroke="#E2E8F0" stroke-width="1.8" rx="3"/>
    <text x="260" y="87" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="bold">THÂN DÀN LẠNH (${p.dimensions} mm)</text>
    <text x="260" y="102" text-anchor="middle" fill="#94A3B8" font-size="9.8">Ống đồng: ${p.gas_pipe} • Nặng: ${p.weight}</text>

    <!-- 60mm Straight Neck CxD -->
    <rect x="${neckX}" y="112" width="${neckW}" height="16" fill="rgba(251,191,36,0.16)" stroke="#FBBF24" stroke-width="1.6"/>
    <text x="260" y="124" text-anchor="middle" fill="#FDE68A" font-size="9.5" font-weight="bold">Cổ máy (CxD): ${d.supply_collar} mm (thẳng 60mm)</text>

    <!-- Stepped Plenum Box AxB -->
    <rect x="${plenX}" y="${plenY}" width="${plenW}" height="${plenDepthPx}" fill="rgba(14,165,233,0.16)" stroke="#38BDF8" stroke-width="2"/>
    <text x="260" y="${plenY + 26}" text-anchor="middle" fill="#FFFFFF" font-size="11.5" font-weight="bold">HỘP GIÓ GIẬT CẤP (AxB): ${boxW} × ${boxH} mm</text>
    <text x="260" y="${plenY + 44}" text-anchor="middle" fill="#7DD3FC" font-size="10.5">Chiều sâu côn H = ${sp.plenDepth} mm • Trổ ${n} cổ tròn Ø${sp.dia} (kc cổ-cổ 60mm)</text>

    <!-- Round Spigots -->
    ${circlesSvg}

    <!-- SIDE PROFILE & SUMMARY (RIGHT) -->
    <rect x="452" y="42" width="272" height="214" fill="rgba(15,23,42,0.82)" stroke="#334155" rx="8"/>
    <text x="466" y="64" fill="#38BDF8" font-size="11.5" font-weight="bold">THÔNG SỐ GIA CÔNG ĐẶT HÀNG ỐNG GIÓ</text>

    <text x="466" y="88" fill="#94A3B8" font-size="10.5">1. Miệng cấp dàn lạnh (Ngang × Đứng):</text>
    <text x="466" y="104" fill="#FFFFFF" font-size="12.5" font-weight="bold">${mouthW} × ${mouthH} mm (Côn cấp: ${d.supply_collar})</text>

    <text x="466" y="128" fill="#94A3B8" font-size="10.5">2. Kích thước côn đầu hồi (Miệng hồi):</text>
    <text x="466" y="144" fill="#FCA5A5" font-size="12.5" font-weight="bold">${d.return_collar} mm</text>

    <text x="466" y="168" fill="#94A3B8" font-size="10.5">3. Diện tích bảo ôn bọc hộp tiêu chuẩn:</text>
    <text x="466" y="184" fill="#6EE7B7" font-size="12.5" font-weight="bold">${d.insul_m2 ? Number(d.insul_m2).toFixed(3) + " m²" : "Theo thực tế"}</text>

    <text x="466" y="208" fill="#94A3B8" font-size="10.5">4. Cấu hình cổ trích ống mềm:</text>
    <text x="466" y="225" fill="#FDE68A" font-size="12" font-weight="bold">Cao H${sp.plenDepth} + ${n} cổ Ø${sp.dia} (elip, trổ đứng)</text>
    <text x="466" y="243" fill="#CBD5E1" font-size="10">Tham chiếu: Bảng Côn Đầu Dàn Lạnh Daikin</text>
  </svg>`;
}

/* ---------------- PRODUCT DETAIL MODAL ---------------- */
function openProductModal(prodId) {
  const p = DB.products.find(x => x.id === prodId);
  if (!p) return;
  const cat = DB.categories.find(c => c.id === p.category_id) || {};

  document.getElementById("pm-title").textContent = `${p.model} — ${p.name}`;

  const blueprintSvg = buildDuctBlueprintSVG(p);
  const hasCommImg = Boolean(p.commercial_img);

  const html = `
    <div class="detail-layout">
      <!-- Left Media Column -->
      <div>
        <div class="media-tabs">
          <button class="media-tab active" id="mtab-png" onclick="switchModalMedia('${p.id}', 'png')">🖼️ Ảnh tách nền (.PNG)</button>
          ${hasCommImg ? `<button class="media-tab" id="mtab-comm" onclick="switchModalMedia('${p.id}', 'comm')">🏷️ Ảnh Minh Phú</button>` : ""}
          <button class="media-tab" id="mtab-cat" onclick="openCatalogPdf('${p.catalog_pdf}', ${p.catalog_page || 1})">📖 Trang Catalogue</button>
        </div>

        <div class="detail-stage" id="pm-media-stage">
          <img src="${p.image}" alt="${p.model}" />
        </div>

        <div style="margin-top:12px;padding:13px;background:#FEF2F2;border:1px solid #FECACA;border-radius:10px;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
              <div style="font-size:11px;color:#7F1D1D;font-weight:700;">ĐƠN GIÁ GỐC NIÊM YẾT (${p.unit})</div>
              <div style="font-size:20px;font-weight:700;color:#B91C1C;" id="pm-price-display">
                ${p.price > 0 ? formatVND(p.price) : "Chưa nhập giá gốc"}
              </div>
            </div>
            <button class="btn btn-sm btn-outline" onclick="promptQuickPriceEdit('${p.id}')">✏️ Sửa giá</button>
          </div>

          <div style="display:flex;gap:8px;margin-top:12px;">
            <input type="number" id="pm-add-qty" value="1" min="1" style="width:70px;padding:8px;border:1.5px solid #CBD5E1;border-radius:8px;font-weight:700;text-align:center;" />
            <button class="btn btn-primary" style="flex:1;" onclick="addToEquipCart('${p.id}', Number(document.getElementById('pm-add-qty').value||1)); closeModal('product-modal');">
              🛒 Thêm vào Giỏ Công Trình
            </button>
          </div>
        </div>

        <div style="margin-top:10px;padding:11px 13px;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;font-size:12px;">
          <div style="font-weight:700;color:#0F172A;margin-bottom:5px;">📚 TÀI LIỆU CATALOGUE THAM CHIẾU</div>
          <div style="color:#334155;margin-bottom:8px;">
            File: <strong>${p.catalog_pdf || "DAIKIN VRV TỔNG HỢP.pdf"}</strong> — <strong>Trang ${p.catalog_page || 1}</strong>
          </div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;">
            <button class="btn btn-sm btn-ice" onclick="openCatalogPdf('${p.catalog_pdf}', ${p.catalog_page || 1})">
              📖 Mở xem trang ${p.catalog_page || 1}
            </button>
            <button class="btn btn-sm btn-outline" onclick="openExternalLink('${p.web_url || DB.company.daikin_catalog_url}')">
              🌐 DaikinCatalog VN
            </button>
            <button class="btn btn-sm btn-outline" onclick="openEditModelModal('${p.id}')">
              ⚙️ Sửa thông số
            </button>
          </div>
        </div>
      </div>

      <!-- Right Specs Column -->
      <div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px;">
          <span class="pill active" style="cursor:default;">${cat.name || "Thiết bị Daikin"}</span>
          <span class="pill" style="cursor:default;">Xuất xứ: ${p.origin}</span>
          <span class="pill" style="cursor:default;">Gas: ${p.refrigerant}</span>
        </div>

        <div class="spec-section-title">⚡ Thông Số Kỹ Thuật & Đường Ống</div>
        <div class="spec-kv-grid">
          <div class="spec-kv"><span>Mã Model chuẩn</span><strong>${p.model}</strong></div>
          <div class="spec-kv"><span>Công suất danh định</span><strong>${p.hp} ${p.cooling_btu ? `(${formatNum(p.cooling_btu)} Btu/h • ${p.cooling_kw} kW)` : ""}</strong></div>
          <div class="spec-kv"><span>Công suất sưởi ấm</span><strong>${p.heating_btu > 0 ? `${formatNum(p.heating_btu)} Btu/h (${p.heating_kw} kW)` : "1 chiều / Không áp dụng"}</strong></div>
          <div class="spec-kv"><span>Nguồn điện & Điện tiêu thụ</span><strong>${p.power_supply} • ${p.power_input || "—"}</strong></div>
          <div class="spec-kv"><span>Kích thước thân máy (C×R×S)</span><strong>${p.dimensions || "—"} mm</strong></div>
          <div class="spec-kv"><span>Trọng lượng tịnh</span><strong>${p.weight || "—"}</strong></div>
          <div class="spec-kv"><span>Kích cỡ ống đồng (Lỏng / Hơi)</span><strong style="color:#B91C1C;">${p.gas_pipe || "—"}</strong></div>
          <div class="spec-kv"><span>Ống nước xả ngưng</span><strong>${p.drain_pipe || "—"}</strong></div>
          <div class="spec-kv"><span>Lưu lượng gió</span><strong>${p.airflow || "—"}</strong></div>
          <div class="spec-kv"><span>Độ ồn vận hành / Áp suất tĩnh</span><strong>${p.noise || "—"} ${p.esp ? `• ESP: ${p.esp}` : ""}</strong></div>
        </div>

        ${p.combo_detail ? `
          <div style="margin-top:10px;padding:9px 12px;background:#EFF6FF;border:1px solid #BFDBFE;border-left:4px solid #005A8D;border-radius:8px;font-size:12.5px;color:#0F172A;">
            <strong>🔗 Cấu hình ghép tổ hợp dàn nóng:</strong> ${p.combo_detail}
          </div>
        ` : ""}

        ${p.notes ? `
          <div style="margin-top:10px;padding:9px 12px;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;font-size:12.5px;color:#334155;">
            <strong>💡 Ghi chú kỹ thuật:</strong> ${p.notes}
          </div>
        ` : ""}
      </div>
    </div>

    ${p.duct ? `
      <div class="duct-blueprint-box">
        <h4>
          <span>📐 KÍCH THƯỚC CÔN MÁY, MIỆNG GIÓ & HỘP CÔN ĐẦU MÁY TIÊU CHUẨN</span>
          <span style="font-size:11px;color:#93C5FD;">Chuẩn Bảng Côn Đầu Dàn Lạnh Daikin</span>
        </h4>
        <div class="duct-metrics-row">
          <div class="duct-metric">
            <span>KT Côn Đầu Cấp (Miệng thổi)</span>
            <strong>${p.duct.supply_collar} mm</strong>
          </div>
          <div class="duct-metric">
            <span>KT Côn Đầu Hồi (Miệng hồi)</span>
            <strong>${p.duct.return_collar} mm</strong>
          </div>
          <div class="duct-metric">
            <span>Miệng cấp (Ngang × Đứng)</span>
            <strong>${p.duct.mouth_w} × ${p.duct.mouth_h} mm</strong>
          </div>
          <div class="duct-metric">
            <span>Bảo ôn cần bọc hộp</span>
            <strong>${p.duct.insul_m2 ? Number(p.duct.insul_m2).toFixed(3) + " m²" : "—"}</strong>
          </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;font-size:12.2px;">
          <div style="background:rgba(15,23,42,0.7);padding:9px 12px;border-radius:8px;border:1px solid rgba(56,189,248,0.2);">
            <span style="color:#93C5FD;display:block;font-size:11px;">Thông số côn đầu máy đề nghị:</span>
            <strong>${p.duct.propose}</strong>
          </div>
          <div style="background:rgba(15,23,42,0.7);padding:9px 12px;border-radius:8px;border:1px solid rgba(56,189,248,0.2);">
            <span style="color:#93C5FD;display:block;font-size:11px;">Kích thước hộp gió giật cấp tiêu chuẩn:</span>
            <strong>${p.duct.std_box}</strong>
          </div>
        </div>
        ${blueprintSvg}
      </div>
    ` : (blueprintSvg ? `<div style="margin-top:16px;">${blueprintSvg}</div>` : "")}
  `;

  document.getElementById("pm-body").innerHTML = html;
  document.getElementById("product-modal").classList.add("open");
}

function switchModalMedia(prodId, type) {
  const p = DB.products.find(x => x.id === prodId);
  if (!p) return;
  document.querySelectorAll("#product-modal .media-tab").forEach(b => b.classList.remove("active"));
  const stage = document.getElementById("pm-media-stage");
  if (type === "comm" && p.commercial_img) {
    document.getElementById("mtab-comm").classList.add("active");
    stage.innerHTML = `<img src="${p.commercial_img}" alt="${p.model}" style="border-radius:8px;" />`;
  } else {
    document.getElementById("mtab-png").classList.add("active");
    stage.innerHTML = `<img src="${p.image}" alt="${p.model}" />`;
  }
}

function promptQuickPriceEdit(prodId) {
  const p = DB.products.find(x => x.id === prodId);
  if (!p) return;
  const val = prompt(`Nhập đơn giá gốc mới cho Model ${p.model} (VNĐ):`, p.price || 0);
  if (val === null) return;
  const num = Number(String(val).replace(/[.,\sđ]/g, ""));
  if (isNaN(num) || num < 0) {
    alert("Giá nhập không hợp lệ!");
    return;
  }
  savePriceOverride(prodId, num);
  const disp = document.getElementById("pm-price-display");
  if (disp) disp.textContent = num > 0 ? formatVND(num) : "Chưa nhập giá gốc";
  renderCatalog();
  showToast(`Đã cập nhật giá ${p.model}: ${formatVND(num)}`);
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove("open");
}

/* ---------------- BUILT-IN PDF CATALOGUE VIEWER ---------------- */
async function openCatalogPdf(fileName, pageNum) {
  if (!fileName) return;
  currentPdfState.file = fileName;
  currentPdfState.page = Math.max(1, Number(pageNum) || 1);
  const meta = DB.catalog_files.find(f => f.file === fileName);
  currentPdfState.totalPages = meta ? meta.pages : 100;

  document.getElementById("pdfm-title").textContent = `📖 ${fileName}`;
  document.getElementById("pdf-modal").classList.add("open");
  await renderCurrentPdfPage();
}

async function renderCurrentPdfPage() {
  const body = document.getElementById("pdfm-body");
  const ind = document.getElementById("pdfm-page-indicator");
  ind.textContent = `Trang ${currentPdfState.page} / ${currentPdfState.totalPages}`;
  body.innerHTML = `<div style="color:#E2E8F0;padding:60px;">⏳ Đang trích xuất trang ${currentPdfState.page} từ Catalogue Tiếng Việt...</div>`;

  try {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.render_pdf_page) {
      const res = await window.pywebview.api.render_pdf_page(currentPdfState.file, currentPdfState.page);
      if (res && res.ok) {
        currentPdfState.totalPages = res.total_pages;
        ind.textContent = `Trang ${res.page} / ${res.total_pages}`;
        body.innerHTML = `<img src="${res.data_url}" style="max-width:100%;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,0.45);" />`;
        return;
      }
    }
    // Try local HTTP API if running in local server preview mode
    const resp = await fetch(`/api/pdf_page?file=${encodeURIComponent(currentPdfState.file)}&page=${currentPdfState.page}`);
    if (resp.ok) {
      const res = await resp.json();
      if (res.ok) {
        currentPdfState.totalPages = res.total_pages;
        ind.textContent = `Trang ${res.page} / ${res.total_pages}`;
        body.innerHTML = `<img src="${res.data_url}" style="max-width:100%;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,0.45);" />`;
        return;
      }
    }
  } catch (e) {}

  body.innerHTML = `
    <div style="color:#F8FAFC;padding:48px 24px;max-width:560px;margin:0 auto;">
      <div style="font-size:42px;margin-bottom:12px;">📑</div>
      <h3>Tài liệu tham chiếu: ${currentPdfState.file} (Trang ${currentPdfState.page})</h3>
      <p style="color:#94A3B8;margin:10px 0 18px;font-size:13.5px;">
        Trên môi trường di động / trình duyệt độc lập không gắn ổ cứng H:\\DAIKIN, bạn có thể tra cứu trực tuyến trọn bộ Catalogue Tiếng Việt trên cổng chính thức Daikin Vietnam.
      </p>
      <button class="btn btn-primary" onclick="openExternalLink('https://www.daikincatalog.com/library/site/vietnam/book-lists/')">
        🌐 Mở DaikinCatalog.com (Vietnam Book Lists)
      </button>
    </div>`;
}

function stepPdfPage(delta) {
  const next = currentPdfState.page + delta;
  if (next < 1 || next > currentPdfState.totalPages) return;
  currentPdfState.page = next;
  renderCurrentPdfPage();
}

function openCurrentPdfExternal() {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.open_local_pdf) {
    window.pywebview.api.open_local_pdf(currentPdfState.file, currentPdfState.page);
  } else {
    openExternalLink(DB.company.daikin_catalog_url);
  }
}

/* ---------------- LIBRARY VIEW ---------------- */
function renderLibraryView() {
  const grid = document.getElementById("library-grid");
  grid.innerHTML = DB.catalog_files.map(cf => `
    <div class="prod-card" style="padding:16px;">
      <div style="display:flex;align-items:flex-start;gap:12px;">
        <div style="width:46px;height:54px;border-radius:10px;background:linear-gradient(135deg,#DC2626,#7F1D1D);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;flex-shrink:0;">
          PDF
        </div>
        <div style="flex:1;">
          <div style="font-weight:700;font-size:14px;color:#0F172A;">${cf.title}</div>
          <div style="font-size:12px;color:#64748B;margin-top:3px;">Tên file: ${cf.file}</div>
          <div style="font-size:11.5px;color:#0369A1;font-weight:700;margin-top:4px;">Quy mô: ${cf.pages} trang</div>
        </div>
      </div>
      <div style="display:flex;gap:8px;margin-top:14px;">
        <button class="btn btn-sm btn-primary" style="flex:1;" onclick="openCatalogPdf('${cf.file}', 1)">📖 Xem trực tiếp trong App</button>
        <button class="btn btn-sm btn-outline" onclick="if(window.pywebview&&window.pywebview.api){window.pywebview.api.open_local_pdf('${cf.file}',1)}else{openCatalogPdf('${cf.file}',1)}">📂 Mở PDF gốc</button>
      </div>
    </div>
  `).join("");
}

/* ---------------- TCVN 5687:2024 QUICK COOLING LOAD CALCULATOR ---------------- */
function runLoadCalc() {
  const room = document.getElementById("lc-room-name").value || "Phòng công trình";
  const area = Number(document.getElementById("lc-area").value) || 25;
  const height = Number(document.getElementById("lc-height").value) || 3.0;
  const baseBtuPerM2 = Number(document.getElementById("lc-type").value) || 800;
  const sunFactor = Number(document.getElementById("lc-sun").value) || 1.0;
  const prefer = document.getElementById("lc-prefer").value;
  const people = Number(document.getElementById("lc-people").value) || 4;

  const heightFactor = height > 3.2 ? 1 + (height - 3.2) * 0.12 : 1.0;
  const reqBtu = Math.round(area * baseBtuPerM2 * sunFactor * heightFactor);
  const reqKw = (reqBtu / 3412).toFixed(2);
  const reqHp = (reqBtu / 9000).toFixed(1);
  // TCVN 5687:2024 minimum outdoor fresh air ~ 20 - 25 m3/h per person
  const freshAirM3h = Math.round(people * 25);

  const candidates = DB.products.filter(p => {
    if (!p.cooling_btu || p.cooling_btu < reqBtu * 0.82 || p.cooling_btu > reqBtu * 1.45) return false;
    if (p.category_id.includes("_OUT")) return false;
    if (prefer === "DUCT" && !p.duct) return false;
    if (prefer === "CASSETTE" && !p.category_id.includes("CASSETTE")) return false;
    if (prefer === "WALL" && !p.category_id.includes("WALL") && p.category_id !== "ROOM_AIR") return false;
    return true;
  }).sort((a, b) => Math.abs(a.cooling_btu - reqBtu) - Math.abs(b.cooling_btu - reqBtu)).slice(0, 8);

  const hrvMatch = DB.products.find(p => p.category_id === "VRV_HRV" && parseInt(p.hp, 10) >= freshAirM3h) || DB.products.find(p => p.id === "VAM150HVE");

  document.getElementById("lc-results-area").innerHTML = `
    <div class="config-card">
      <div class="config-card-head">📊 Kết Quả Tính Chọn Thiết Bị Cho "${room}" (${area} m² × cao ${height} m)</div>
      <div class="config-card-body">
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">
          <div class="spec-kv" style="background:#FEF2F2;border-color:#FECACA;">
            <span>Công suất lạnh yêu cầu</span>
            <strong style="font-size:17px;color:#B91C1C;">${formatNum(reqBtu)} Btu/h</strong>
            <span style="margin-top:2px;">~ ${reqKw} kW (${reqHp} HP)</span>
          </div>
          <div class="spec-kv" style="background:#F0F9FF;border-color:#BAE6FD;">
            <span>Lưu lượng gió tươi (TCVN 5687:2024)</span>
            <strong style="font-size:17px;color:#0369A1;">${freshAirM3h} m³/h</strong>
            <span style="margin-top:2px;">Gợi ý HRV: ${hrvMatch ? hrvMatch.model : "VAM150HVE"}</span>
          </div>
          <div class="spec-kv">
            <span>Khuyến nghị côn gió / cửa gió</span>
            <strong style="font-size:14px;color:#0F172A;">${reqBtu <= 16000 ? "H250 + 2 cổ Ø200" : (reqBtu <= 31000 ? "H250 + 3~4 cổ Ø200" : "H300 + 4 cổ Ø250")}</strong>
            <span style="margin-top:2px;">Cửa Linear Slot / Khuếch tán</span>
          </div>
        </div>

        <div class="spec-section-title">🎯 Các Model Daikin Đáp Ứng Tải Lạnh Tốt Nhất</div>
        <div class="data-table-wrap">
          <table class="clean-table">
            <thead>
              <tr>
                <th>Ảnh</th>
                <th>Model</th>
                <th>Công suất</th>
                <th>Thông số Côn / Lỗ trần</th>
                <th>Đơn giá gốc</th>
                <th>Chọn</th>
              </tr>
            </thead>
            <tbody>
              ${candidates.map(p => `
                <tr>
                  <td><img src="${p.image}" style="width:46px;height:36px;object-fit:contain;" /></td>
                  <td><strong style="cursor:pointer;color:#0F172A;" onclick="openProductModal('${p.id}')">${p.model}</strong><div style="font-size:11px;color:#64748B;">${p.name}</div></td>
                  <td><strong>${formatNum(p.cooling_btu)} Btu/h</strong></td>
                  <td>${p.duct ? `<span style="color:#0369A1;font-weight:700;">Cấp: ${p.duct.supply_collar}</span> • ${p.duct.propose}` : (p.ceiling_opening || p.dimensions)}</td>
                  <td><strong style="color:#B91C1C;">${p.price > 0 ? formatVND(p.price) : "Chờ cập nhật"}</strong></td>
                  <td><button class="btn btn-sm btn-primary" onclick="addToEquipCart('${p.id}', 1)">+ Đưa vào Giỏ</button></td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;
}

/* ---------------- VIETQR GENERATOR & ADMIN SETTINGS ---------------- */
function getVietQrUrl(amount, addInfo) {
  const b = DB.company.bank || {};
  if (b.custom_qr_data_url) return b.custom_qr_data_url;
  const bankId = encodeURIComponent((b.bank_id || "MB").trim());
  const accNo = encodeURIComponent((b.account_no || "0967986586").trim());
  const accName = encodeURIComponent((b.account_name || "CONG TY TNHH PT KT TM MINH PHU").trim());
  const info = encodeURIComponent((addInfo || b.note_prefix || "TT DON HANG MINH PHU").trim());
  const amtParam = amount && Number(amount) > 0 ? `amount=${Math.round(Number(amount))}&` : "";
  return `https://img.vietqr.io/image/${bankId}-${accNo}-compact2.png?${amtParam}addInfo=${info}&accountName=${accName}`;
}

function buildOfflineQrFallbackSvgDataUrl(label) {
  // Deterministic visual QR-styled badge used only if offline & no custom QR uploaded
  const b = DB.company.bank || {};
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="220" height="220" viewBox="0 0 220 220">
    <rect width="220" height="220" fill="#FFFFFF" rx="8"/>
    <rect x="14" y="14" width="54" height="54" fill="none" stroke="#0F172A" stroke-width="8"/>
    <rect x="28" y="28" width="26" height="26" fill="#B91C1C"/>
    <rect x="152" y="14" width="54" height="54" fill="none" stroke="#0F172A" stroke-width="8"/>
    <rect x="166" y="28" width="26" height="26" fill="#0F172A"/>
    <rect x="14" y="152" width="54" height="54" fill="none" stroke="#0F172A" stroke-width="8"/>
    <rect x="28" y="166" width="26" height="26" fill="#0F172A"/>
    <g fill="#0F172A">
      <rect x="82" y="20" width="12" height="12"/><rect x="102" y="20" width="12" height="12"/><rect x="126" y="20" width="12" height="12"/>
      <rect x="82" y="42" width="24" height="12"/><rect x="118" y="42" width="20" height="12"/>
      <rect x="20" y="84" width="16" height="12"/><rect x="48" y="84" width="28" height="12"/><rect x="92" y="84" width="36" height="12"/><rect x="142" y="84" width="24" height="12"/><rect x="180" y="84" width="24" height="12"/>
      <rect x="20" y="108" width="32" height="12"/><rect x="66" y="108" width="18" height="12"/><rect x="134" y="108" width="26" height="12"/><rect x="172" y="108" width="32" height="12"/>
      <rect x="20" y="128" width="18" height="12"/><rect x="52" y="128" width="28" height="12"/><rect x="96" y="128" width="28" height="12"/><rect x="140" y="128" width="48" height="12"/>
      <rect x="84" y="156" width="24" height="12"/><rect x="122" y="156" width="32" height="12"/><rect x="168" y="156" width="36" height="12"/>
      <rect x="84" y="180" width="40" height="14"/><rect x="138" y="180" width="24" height="14"/><rect x="176" y="180" width="28" height="14"/>
    </g>
    <text x="110" y="213" text-anchor="middle" font-family="Segoe UI, sans-serif" font-size="10.5" font-weight="bold" fill="#B91C1C">${b.bank_id || "MB"}: ${b.account_no || ""}</text>
  </svg>`;
  return "data:image/svg+xml;utf8," + encodeURIComponent(svg);
}

function populateAdminSettings() {
  const c = DB.company;
  document.getElementById("set-comp-name").value = c.name || "";
  document.getElementById("set-comp-en").value = c.english_name || "";
  document.getElementById("set-comp-tax").value = c.tax_code || "";
  document.getElementById("set-comp-hotline").value = c.hotline || "";
  document.getElementById("set-comp-rep").value = c.representative || "";
  document.getElementById("set-comp-web").value = c.website || "";
  document.getElementById("set-comp-addr").value = c.address || "";
  document.getElementById("set-comp-email").value = c.email || "";
  document.getElementById("set-comp-terms").value = (c.quote_terms || []).join("\n");

  const b = c.bank || {};
  document.getElementById("set-bank-id").value = b.bank_id || "MB";
  document.getElementById("set-bank-acc").value = b.account_no || "";
  document.getElementById("set-bank-holder").value = b.account_name || "";
  document.getElementById("set-bank-prefix").value = b.note_prefix || "";
  previewSettingsQR();
  switchAdminPriceTab(adminPriceTab || "equip");
}

function switchAdminPriceTab(tab) {
  adminPriceTab = tab;
  const bEq = document.getElementById("adm-tab-equip");
  const bMt = document.getElementById("adm-tab-mat");
  if (bEq && bMt) {
    bEq.className = tab === "equip" ? "btn btn-primary btn-sm" : "btn btn-outline btn-sm";
    bMt.className = tab === "mat" ? "btn btn-primary btn-sm" : "btn btn-outline btn-sm";
    bEq.textContent = `💎 Giá Gốc Thiết Bị Daikin (${DB.products.length} mã)`;
    bMt.textContent = `🛠️ Giá Gốc Vật Tư & Nhân Công (${DB.materials.length} mục)`;
  }
  const grpSel = document.getElementById("adm-price-group");
  if (grpSel) {
    if (tab === "equip") {
      grpSel.innerHTML = `<option value="ALL">Tất cả dòng sản phẩm (${DB.categories.length} nhóm)</option>` +
        DB.categories.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
    } else {
      grpSel.innerHTML = `
        <option value="ALL">Tất cả 5 nhóm Vật tư & Nhân công</option>
        <option value="I">Nhóm I — Lắp đặt thiết bị & Giá đỡ</option>
        <option value="II">Nhóm II — Ống đồng, bảo ôn & Trunking</option>
        <option value="III">Nhóm III — Ống nước ngưng & Bảo ôn</option>
        <option value="IV">Nhóm IV — Dây điện nguồn & Tín hiệu</option>
        <option value="V">Nhóm V — Côn đầu máy, Ống gió & Cửa gió</option>
      `;
    }
  }
  renderAdminBasePriceTable();
}

function renderAdminBasePriceTable() {
  const thead = document.getElementById("adm-price-thead");
  const tbody = document.getElementById("adm-price-tbody");
  if (!thead || !tbody) return;
  const q = (document.getElementById("adm-price-search").value || "").trim().toLowerCase();
  const grp = document.getElementById("adm-price-group").value || "ALL";

  if (adminPriceTab === "equip") {
    const catMap = {};
    DB.categories.forEach(c => (catMap[c.id] = c.name));
    const list = DB.products.filter(p => {
      if (grp !== "ALL" && p.category_id !== grp) return false;
      if (q && !`${p.model} ${p.name} ${p.hp} ${p.origin}`.toLowerCase().includes(q)) return false;
      return true;
    });
    thead.innerHTML = `
      <tr>
        <th style="width:44px;">STT</th>
        <th>Mã Model</th>
        <th>Tên thiết bị & Nhóm mục lục</th>
        <th>Công suất</th>
        <th style="width:110px;">Xuất xứ</th>
        <th style="width:72px;">ĐVT</th>
        <th style="width:165px;">Giá gốc đầu vào (VNĐ)</th>
        <th style="width:95px;">Thao tác</th>
      </tr>
    `;
    tbody.innerHTML = list.map((p, idx) => `
      <tr>
        <td style="text-align:center;">${idx + 1}</td>
        <td><strong style="color:#005A8D;cursor:pointer;" onclick="openProductModal('${p.id}')">${p.model}</strong></td>
        <td>
          <div style="font-weight:600;">${p.name}</div>
          <div style="font-size:11px;color:#64748B;">${catMap[p.category_id] || p.category_id}</div>
        </td>
        <td><strong>${p.cooling_btu > 0 ? formatNum(p.cooling_btu) + " Btu/h" : p.hp}</strong></td>
        <td><input type="text" value="${p.origin || ''}" onchange="updateMasterEquipRow('${p.id}','origin',this.value)" style="width:100px;padding:4px 6px;border:1px solid #CBD5E1;border-radius:6px;font-size:12px;" /></td>
        <td><input type="text" value="${p.unit || 'Dàn'}" onchange="updateMasterEquipRow('${p.id}','unit',this.value)" style="width:60px;padding:4px 6px;border:1px solid #CBD5E1;border-radius:6px;text-align:center;font-size:12px;" /></td>
        <td>
          <input type="number" class="price-edit-input" style="width:148px;border-color:#005A8D;background:#FFFFFF;color:#991B1B;" step="10000" value="${p.price || 0}" onchange="updateMasterEquipRow('${p.id}','price',this.value)" />
        </td>
        <td>
          <button class="btn btn-sm btn-outline" onclick="openEditModelModal('${p.id}')">⚙️ Sửa</button>
        </td>
      </tr>
    `).join("");
  } else {
    const list = DB.materials.filter(m => {
      if (grp !== "ALL" && m.group_code !== grp) return false;
      if (q && !`${m.name} ${m.brand} ${m.group_name}`.toLowerCase().includes(q)) return false;
      return true;
    });
    thead.innerHTML = `
      <tr>
        <th style="width:44px;">STT</th>
        <th style="width:74px;">Nhóm</th>
        <th>Tên hạng mục Vật tư / Nhân công đầu vào</th>
        <th style="width:115px;">Nhãn hiệu</th>
        <th style="width:115px;">Phân loại hệ số</th>
        <th style="width:70px;">ĐVT</th>
        <th style="width:165px;">Giá gốc đầu vào (VNĐ)</th>
      </tr>
    `;
    tbody.innerHTML = list.map((m, idx) => `
      <tr>
        <td style="text-align:center;">${idx + 1}</td>
        <td><strong>Phần ${m.group_code}</strong></td>
        <td style="font-weight:600;">${m.name}</td>
        <td><input type="text" value="${m.brand || ''}" onchange="updateMasterMatRow('${m.id}','brand',this.value)" style="width:105px;padding:4px 6px;border:1px solid #CBD5E1;border-radius:6px;font-size:12px;" /></td>
        <td>
          <select onchange="updateMasterMatRow('${m.id}','cost_type',this.value)" style="padding:4px 6px;border:1px solid #CBD5E1;border-radius:6px;font-size:12px;font-weight:700;color:${m.cost_type === 'labor' ? '#991B1B' : '#005A8D'};">
            <option value="material" ${m.cost_type === "material" ? "selected" : ""}>Vật tư</option>
            <option value="labor" ${m.cost_type === "labor" ? "selected" : ""}>Nhân công</option>
          </select>
        </td>
        <td><input type="text" value="${m.unit || ''}" onchange="updateMasterMatRow('${m.id}','unit',this.value)" style="width:58px;padding:4px 6px;border:1px solid #CBD5E1;border-radius:6px;text-align:center;font-size:12px;" /></td>
        <td>
          <input type="number" class="price-edit-input" style="width:148px;border-color:#005A8D;background:#FFFFFF;color:#991B1B;" step="1000" value="${m.base_price || 0}" onchange="updateMasterMatRow('${m.id}','base_price',this.value)" />
        </td>
      </tr>
    `).join("");
  }
}

function updateMasterEquipRow(prodId, field, val) {
  if (field === "price") {
    savePriceOverride(prodId, Number(val) || 0);
    const p = DB.products.find(x => x.id === prodId);
    showToast(`💾 Đã lưu giá gốc ${p ? p.model : prodId}: ${formatVND(val)}`);
  } else {
    savePriceOverride(prodId, null, { [field]: val });
    showToast("💾 Đã lưu thông tin gốc thiết bị!");
  }
}

function updateMasterMatRow(matId, field, val) {
  const upd = field === "base_price" ? { base_price: Number(val) || 0 } : { [field]: val };
  saveMaterialOverride(matId, upd);
  showToast("💾 Đã lưu giá gốc Vật tư / Nhân công!");
}

function promptAddMasterMaterial() {
  const name = prompt("Nhập tên Vật tư hoặc Nhân công mới cần thêm vào Kho giá gốc:");
  if (!name || !name.trim()) return;
  const priceStr = prompt("Nhập đơn giá gốc đầu vào (VNĐ):", "150000");
  if (priceStr === null) return;
  const unit = prompt("Đơn vị tính (VD: m, cái, bộ, dàn, m²):", "bộ") || "bộ";
  const isLabor = confirm("Bấm OK nếu đây là NHÂN CÔNG, hoặc Cancel nếu là VẬT TƯ PHỤ:");
  const newMat = {
    id: "MAT_CUSTOM_" + Date.now(),
    group_code: isLabor ? "I" : "II",
    group_name: isLabor ? "I. Phần nhân công lắp đặt thiết bị & Giá đỡ" : "II. Phần ống đồng, bảo ôn & Trunking",
    name: name.trim(),
    brand: isLabor ? "Minh Phú" : "Việt Nam",
    cost_type: isLabor ? "labor" : "material",
    unit: unit.trim(),
    base_price: Math.max(0, Number(String(priceStr).replace(/[.,\sđ]/g, "")) || 0)
  };
  DB.materials.unshift(newMat);
  let cMats = [];
  try { cMats = JSON.parse(localStorage.getItem(STORAGE_KEYS.CUSTOM_MATS) || "[]"); } catch (e) {}
  cMats.unshift(newMat);
  localStorage.setItem(STORAGE_KEYS.CUSTOM_MATS, JSON.stringify(cMats));
  syncBackupToDesktop();
  switchAdminPriceTab("mat");
  showToast(`✅ Đã thêm "${newMat.name}" vào Kho giá gốc!`);
}

function syncMasterPricesToActiveCart() {
  if (typeof QUOTE === "undefined") return;
  let updatedCount = 0;
  (QUOTE.equip_items || []).forEach(it => {
    const p = DB.products.find(x => x.id === it.prod_id);
    if (p) {
      it.base_price = Number(p.price) || 0;
      it.unit = p.unit || it.unit;
      it.origin = p.origin || it.origin;
      updatedCount++;
    }
  });
  (QUOTE.install_items || []).forEach(it => {
    const m = DB.materials.find(x => x.id === it.mat_id);
    if (m) {
      it.base_price = Number(m.base_price) || 0;
      it.cost_type = m.cost_type || it.cost_type;
      it.unit = m.unit || it.unit;
      it.brand = m.brand || it.brand;
      updatedCount++;
    }
  });
  if (typeof persistQuoteState === "function") persistQuoteState();
  if (typeof renderCartTables === "function") renderCartTables();
  showToast(`🔄 Đã cập nhật Giá gốc mới nhất cho ${updatedCount} hạng mục trong Giỏ hàng!`);
}

function resetAllBasePricesToDefault() {
  if (!confirm("Bạn có chắc muốn khôi phục toàn bộ Giá gốc Thiết bị & Vật tư/Nhân công về mức mặc định ban đầu từ file Báo giá VRV?")) return;
  localStorage.removeItem(STORAGE_KEYS.PRICE_OVERRIDES);
  localStorage.removeItem(STORAGE_KEYS.MAT_OVERRIDES);
  DB.products = JSON.parse(JSON.stringify(window.DAIKIN_INITIAL_DB.products));
  DB.materials = JSON.parse(JSON.stringify(window.DAIKIN_INITIAL_DB.materials));
  loadOverrides();
  syncBackupToDesktop();
  renderAdminBasePriceTable();
  renderCatalog();
  showToast("↩️ Đã khôi phục bảng giá gốc mặc định ban đầu!");
}

function previewSettingsQR() {
  const bankSel = document.getElementById("set-bank-id");
  const bankId = bankSel.value;
  const bankName = bankSel.options[bankSel.selectedIndex].text;
  const acc = document.getElementById("set-bank-acc").value.trim();
  const holder = document.getElementById("set-bank-holder").value.trim();
  const prefix = document.getElementById("set-bank-prefix").value.trim();

  DB.company.bank.bank_id = bankId;
  DB.company.bank.bank_name = bankName;
  DB.company.bank.account_no = acc;
  DB.company.bank.account_name = holder;
  DB.company.bank.note_prefix = prefix;

  const img = document.getElementById("settings-qr-preview");
  img.onerror = function () {
    this.onerror = null;
    this.src = buildOfflineQrFallbackSvgDataUrl();
  };
  img.src = getVietQrUrl(10000000, prefix + " BG DEMO");
  document.getElementById("settings-qr-desc").innerHTML =
    `<strong>${bankName}</strong><br/>STK: <strong style="color:#991B1B;">${acc}</strong><br/>Chủ TK: <strong>${holder}</strong><br/><span style="color:#005A8D;font-weight:700;">Tự động điền số tiền theo từng Báo giá!</span>`;
}

function handleCustomQRUpload(ev) {
  const file = ev.target.files && ev.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    DB.company.bank.custom_qr_data_url = e.target.result;
    previewSettingsQR();
    showToast("Đã nạp ảnh QR Ngân hàng tĩnh thành công!");
  };
  reader.readAsDataURL(file);
}

function clearCustomQR() {
  DB.company.bank.custom_qr_data_url = "";
  previewSettingsQR();
  showToast("Đã chuyển sang chế độ tạo VietQR tự động!");
}

function saveCompanySettings() {
  const c = DB.company;
  c.name = document.getElementById("set-comp-name").value.trim();
  c.english_name = document.getElementById("set-comp-en").value.trim();
  c.tax_code = document.getElementById("set-comp-tax").value.trim();
  c.hotline = document.getElementById("set-comp-hotline").value.trim();
  c.representative = document.getElementById("set-comp-rep").value.trim();
  c.website = document.getElementById("set-comp-web").value.trim();
  c.address = document.getElementById("set-comp-addr").value.trim();
  c.email = document.getElementById("set-comp-email").value.trim();
  c.quote_terms = document.getElementById("set-comp-terms").value
    .split("\n")
    .map(s => s.trim())
    .filter(Boolean);

  previewSettingsQR();
  localStorage.setItem(STORAGE_KEYS.COMPANY, JSON.stringify(c));
  syncBackupToDesktop();
  showToast("✅ Đã lưu thông tin Công ty Minh Phú & cấu hình VietQR!");
}

/* ---------------- ADD / EDIT MODEL MODAL ---------------- */
function openAddModelModal() {
  openEditModelModal(null);
}

function openEditModelModal(prodId) {
  const existing = prodId ? DB.products.find(x => x.id === prodId) : null;
  const p = existing || {
    id: "", model: "", category_id: "VRV_IN_DUCT_MED", name: "", hp: "2.0 HP",
    cooling_btu: 19100, cooling_kw: 5.6, heating_btu: 21500, heating_kw: 6.3,
    power_supply: "1 pha, 220-240V, 50Hz", power_input: "100 W", refrigerant: "R410A",
    dimensions: "245x1000x800", weight: "35 kg", airflow: "17 m³/phút", noise: "34 dB(A)",
    gas_pipe: "Ø6.4 / Ø12.7", drain_pipe: "VP25", price: 0, unit: "Dàn", origin: "Thái Lan",
    image: "assets/products/duct_med_fxsq.png", catalog_pdf: "DAIKIN VRV TỔNG HỢP.pdf", catalog_page: 207,
    duct: { supply_collar: "795x180", return_collar: "955x210", mouth_w: 795, mouth_h: 180, insul_m2: 0.585, propose: "Côn đầu máy H250 + 3 cổ D200", std_box: "Hộp gió KT: 795x220, H250, 3D200" }
  };

  document.getElementById("emm-title").textContent = existing ? `Sửa Model: ${p.model}` : "Thêm Mới Model Thiết Bị Vào Kho";
  document.getElementById("emm-body").innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
      <div class="form-group">
        <label>Mã Model *</label>
        <input type="text" id="em-model" value="${p.model}" ${existing ? "readonly" : ""} />
      </div>
      <div class="form-group">
        <label>Thuộc mục lục sản phẩm</label>
        <select id="em-cat">
          ${DB.categories.map(c => `<option value="${c.id}" ${c.id === p.category_id ? "selected" : ""}>${c.name}</option>`).join("")}
        </select>
      </div>
      <div class="form-group" style="grid-column:span 2;">
        <label>Tên mô tả thiết bị *</label>
        <input type="text" id="em-name" value="${p.name}" />
      </div>
      <div class="form-group">
        <label>Đơn giá gốc (VNĐ)</label>
        <input type="number" id="em-price" value="${p.price || 0}" />
      </div>
      <div class="form-group">
        <label>Đơn vị tính / Xuất xứ</label>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
          <input type="text" id="em-unit" value="${p.unit || "Dàn"}" />
          <input type="text" id="em-origin" value="${p.origin || "Thái Lan"}" />
        </div>
      </div>
      <div class="form-group">
        <label>Công suất HP & Lạnh (Btu/h)</label>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
          <input type="text" id="em-hp" value="${p.hp || ""}" placeholder="VD: 2.5 HP" />
          <input type="number" id="em-btu" value="${p.cooling_btu || 0}" />
        </div>
      </div>
      <div class="form-group">
        <label>Kích thước máy (mm) & Trọng lượng</label>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
          <input type="text" id="em-dim" value="${p.dimensions || ""}" />
          <input type="text" id="em-weight" value="${p.weight || ""}" />
        </div>
      </div>
      <div class="form-group">
        <label>Ống đồng (Lỏng / Hơi)</label>
        <input type="text" id="em-pipe" value="${p.gas_pipe || ""}" />
      </div>
      <div class="form-group">
        <label>Lưu lượng gió & Độ ồn</label>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
          <input type="text" id="em-air" value="${p.airflow || ""}" />
          <input type="text" id="em-noise" value="${p.noise || ""}" />
        </div>
      </div>
      <div class="form-group">
        <label>KT Côn đầu cấp (mm - để trống nếu không nối gió)</label>
        <input type="text" id="em-sc" value="${p.duct ? p.duct.supply_collar : ""}" placeholder="VD: 795x180" />
      </div>
      <div class="form-group">
        <label>KT Côn đầu hồi (mm)</label>
        <input type="text" id="em-rc" value="${p.duct ? p.duct.return_collar : ""}" placeholder="VD: 955x210" />
      </div>
      <div class="form-group" style="grid-column:span 2;">
        <label>Quy cách Côn đầu máy & Hộp gió tiêu chuẩn</label>
        <input type="text" id="em-sbox" value="${p.duct ? p.duct.std_box : ""}" placeholder="VD: Hộp gió giật cấp KT: 1000 x 220, H250, trổ đỉnh 4D200" />
      </div>
    </div>
    <div style="display:flex;justify-content:flex-end;gap:10px;margin-top:16px;">
      <button class="btn btn-outline" onclick="closeModal('edit-model-modal')">Hủy</button>
      <button class="btn btn-primary" onclick="saveEditedModel('${existing ? existing.id : ""}')">💾 Lưu Model vào Kho</button>
    </div>
  `;
  document.getElementById("edit-model-modal").classList.add("open");
}

function saveEditedModel(existingId) {
  const modelCode = document.getElementById("em-model").value.trim();
  const name = document.getElementById("em-name").value.trim();
  if (!modelCode || !name) {
    alert("Vui lòng nhập Mã Model và Tên thiết bị!");
    return;
  }
  const id = existingId || modelCode.replace(/[^A-Za-z0-9_-]/g, "_");
  const baseObj = (existingId && DB.products.find(x => x.id === existingId)) || {};
  const sc = document.getElementById("em-sc").value.trim();
  const rc = document.getElementById("em-rc").value.trim();
  const sbox = document.getElementById("em-sbox").value.trim();

  let ductObj = null;
  if (sc) {
    const parts = sc.split(/[xX]/);
    ductObj = {
      supply_collar: sc,
      return_collar: rc || sc,
      mouth_w: parseInt(parts[0], 10) || 700,
      mouth_h: parseInt(parts[1], 10) || 180,
      insul_m2: baseObj.duct ? baseObj.duct.insul_m2 : 0.55,
      propose: baseObj.duct ? baseObj.duct.propose : sbox,
      std_box: sbox || `Hộp gió giật cấp cổ ${sc}`
    };
  }

  const btu = Number(document.getElementById("em-btu").value) || 0;
  const updated = Object.assign({}, baseObj, {
    id,
    model: modelCode,
    category_id: document.getElementById("em-cat").value,
    name,
    price: Number(document.getElementById("em-price").value) || 0,
    unit: document.getElementById("em-unit").value.trim() || "Dàn",
    origin: document.getElementById("em-origin").value.trim() || "Thái Lan",
    hp: document.getElementById("em-hp").value.trim(),
    cooling_btu: btu,
    cooling_kw: btu ? Number((btu / 3412).toFixed(1)) : 0,
    dimensions: document.getElementById("em-dim").value.trim(),
    weight: document.getElementById("em-weight").value.trim(),
    gas_pipe: document.getElementById("em-pipe").value.trim(),
    airflow: document.getElementById("em-air").value.trim(),
    noise: document.getElementById("em-noise").value.trim(),
    image: baseObj.image || "assets/products/duct_med_fxsq.png",
    catalog_pdf: baseObj.catalog_pdf || "DAIKIN VRV TỔNG HỢP.pdf",
    catalog_page: baseObj.catalog_page || 1,
    duct: ductObj
  });

  const idx = DB.products.findIndex(x => x.id === id);
  if (idx >= 0) DB.products[idx] = updated;
  else DB.products.unshift(updated);

  let customList = [];
  try { customList = JSON.parse(localStorage.getItem(STORAGE_KEYS.CUSTOM_MODELS) || "[]"); } catch (e) {}
  const cIdx = customList.findIndex(x => x.id === id);
  if (cIdx >= 0) customList[cIdx] = updated;
  else customList.push(updated);
  localStorage.setItem(STORAGE_KEYS.CUSTOM_MODELS, JSON.stringify(customList));
  syncBackupToDesktop();

  closeModal("edit-model-modal");
  closeModal("product-modal");
  populateCategorySelect();
  renderCatalog();
  if (document.getElementById("view-admin").classList.contains("active")) renderAdminBasePriceTable();
  showToast(`✅ Đã lưu thông tin Model ${modelCode}!`);
}

/* ---------------- INIT ON DOM READY ---------------- */
document.addEventListener("DOMContentLoaded", () => {
  loadOverrides();
  populateCategorySelect();
  renderCatalog();
  if (typeof initQuoteState === "function") initQuoteState();
  loadDesktopBackupIfAvailable();
  window.addEventListener("pywebviewready", () => loadDesktopBackupIfAvailable());
});
