/* ==========================================================================
   quote.js — Project Cart, Auto-Estimator, Multipliers, Minh Phú Gradient Form,
              Vietnamese Amount-in-Words, VietQR & Excel/PDF Export Bridge
   ========================================================================== */

let QUOTE = {
  code: "BG-MP-20261124-01",
  date_str: new Date().toLocaleDateString("vi-VN"),
  client_name: "Chủ Đầu Tư Biệt Thự / Công Trình",
  project_name: "Hệ Thống Điều Hòa Trung Tâm Daikin VRV H - Biệt Thự 3 Tầng",
  project_addr: "Quận Cầu Giấy, TP. Hà Nội",
  client_phone: "",
  author: "Phòng Kinh Doanh - Kỹ Thuật Minh Phú",
  mode: "BOTH", // BOTH | EQUIP_ONLY | INSTALL_ONLY
  mult_equip: 1.0,
  mult_mat: 1.0,
  mult_labor: 1.0,
  vat_rate: 10,
  qr_percent: 50,
  custom_terms: null,
  hidden_appendix_uids: [],
  custom_appendix_rows: [],
  equip_items: [],
  install_items: []
};

function makeUid() {
  return "u_" + Math.random().toString(36).slice(2, 10);
}

/* ---------------- INIT & PERSISTENCE ---------------- */
function initQuoteState() {
  let loaded = false;
  try {
    const raw = localStorage.getItem(STORAGE_KEYS.CART);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed && Array.isArray(parsed.equip_items)) {
        QUOTE = Object.assign({}, QUOTE, parsed);
        loaded = true;
      }
    }
  } catch (e) {}

  if (!loaded) {
    loadDemoSampleProject(true);
  } else {
    syncQuoteInputsFromState();
    updateTopbarCartSummary();
  }
}

function persistQuoteState() {
  try {
    localStorage.setItem(STORAGE_KEYS.CART, JSON.stringify(QUOTE));
  } catch (e) {}
  updateTopbarCartSummary();
}

function syncQuoteInputsFromState() {
  const setVal = (id, v) => {
    const el = document.getElementById(id);
    if (el) el.value = v !== undefined && v !== null ? v : "";
  };
  setVal("q-code", QUOTE.code);
  setVal("q-client", QUOTE.client_name);
  setVal("q-project", QUOTE.project_name);
  setVal("q-address", QUOTE.project_addr);
  setVal("q-phone", QUOTE.client_phone);
  setVal("q-author", QUOTE.author);
  setVal("mult-equip", QUOTE.mult_equip.toFixed(2));
  setVal("mult-mat", QUOTE.mult_mat.toFixed(2));
  setVal("mult-labor", QUOTE.mult_labor.toFixed(2));
  setVal("q-vat", String(QUOTE.vat_rate));
  setVal("q-qr-mode", String(QUOTE.qr_percent));

  document.querySelectorAll("#quote-mode-selector .mode-option").forEach(opt => {
    opt.classList.toggle("active", opt.getAttribute("data-mode") === QUOTE.mode);
  });
}

function syncQuoteMeta() {
  QUOTE.code = document.getElementById("q-code").value.trim() || "BG-MP-01";
  QUOTE.client_name = document.getElementById("q-client").value;
  QUOTE.project_name = document.getElementById("q-project").value;
  QUOTE.project_addr = document.getElementById("q-address").value;
  QUOTE.client_phone = document.getElementById("q-phone").value;
  QUOTE.author = document.getElementById("q-author").value;
  persistQuoteState();
}

function setQuoteMode(mode) {
  QUOTE.mode = mode;
  document.querySelectorAll("#quote-mode-selector .mode-option").forEach(opt => {
    opt.classList.toggle("active", opt.getAttribute("data-mode") === mode);
  });
  persistQuoteState();
  renderCartTables();
}

function updateMultipliers() {
  QUOTE.mult_equip = Math.max(0.05, Number(document.getElementById("mult-equip").value) || 1.0);
  QUOTE.mult_mat = Math.max(0.05, Number(document.getElementById("mult-mat").value) || 1.0);
  QUOTE.mult_labor = Math.max(0.05, Number(document.getElementById("mult-labor").value) || 1.0);
  QUOTE.vat_rate = Number(document.getElementById("q-vat").value) || 0;
  QUOTE.qr_percent = Number(document.getElementById("q-qr-mode").value);
  persistQuoteState();
  renderCartTables();
}

/* ---------------- SAMPLE DEMO PROJECT ---------------- */
function loadDemoSampleProject(silent) {
  QUOTE.code = "BG-MP-20261124-01";
  QUOTE.client_name = "Quý Khách Hàng / Chủ Đầu Tư Biệt Thự";
  QUOTE.project_name = "Cung cấp & Lắp đặt ĐHKK Trung tâm Daikin VRV H - Biệt thự 3 Tầng";
  QUOTE.project_addr = "Quận Cầu Giấy, TP. Hà Nội";
  QUOTE.author = "Phòng Dự Án - Kỹ Thuật Minh Phú";
  QUOTE.mode = "BOTH";
  QUOTE.mult_equip = 1.0;
  QUOTE.mult_mat = 1.0;
  QUOTE.mult_labor = 1.0;
  QUOTE.vat_rate = 10;
  QUOTE.qr_percent = 50;
  QUOTE.equip_items = [];
  QUOTE.install_items = [];

  const sampleIds = [
    ["RXYQ14BYM", 1],
    ["FXSQ63PAVE", 2],
    ["FXSQ40PAVE", 2],
    ["FXFQ50AVM", 1],
    ["BYCQ125EAF", 1],
    ["BRC1E63", 5],
    ["KHRP26A33T8", 1],
    ["KHRP26A22T8", 3]
  ];
  sampleIds.forEach(([pid, qty]) => addToEquipCart(pid, qty, true));
  autoEstimateMaterialsFromEquip(true);
  syncQuoteInputsFromState();
  persistQuoteState();
  renderCartTables();
  if (!silent) showToast("✨ Đã nạp dự án mẫu Biệt thự VRV H 14HP kèm đầy đủ vật tư & nhân công!");
}

/* ---------------- EQUIPMENT CART OPERATIONS ---------------- */
function buildEquipSpecSummary(p) {
  const lines = [];
  if (p.cooling_btu > 0) {
    lines.push(`Công suất lạnh: ${formatNum(p.cooling_btu)} Btu/h (${p.cooling_kw} kW)`);
  }
  if (p.dimensions && p.dimensions !== "—") {
    lines.push(`KT máy: ${p.dimensions} mm • Ống gas: ${p.gas_pipe || "—"}`);
  }
  if (p.duct) {
    lines.push(`Côn cấp: ${p.duct.supply_collar} mm | Côn hồi: ${p.duct.return_collar} mm`);
  } else if (p.combo_detail && !p.combo_detail.includes("độc lập")) {
    lines.push(`Tổ hợp: ${p.combo_detail}`);
  }
  return lines.join(" | ");
}

function addToEquipCart(prodId, qty, silent) {
  const p = DB.products.find(x => x.id === prodId);
  if (!p) return;
  const nQty = Math.max(1, Number(qty) || 1);
  const existing = QUOTE.equip_items.find(it => it.prod_id === prodId);
  if (existing) {
    existing.qty += nQty;
  } else {
    QUOTE.equip_items.push({
      uid: makeUid(),
      prod_id: p.id,
      category_id: p.category_id,
      model: p.model,
      name: p.name,
      spec_note: buildEquipSpecSummary(p),
      origin: `Daikin / ${p.origin}`,
      unit: p.unit || "Dàn",
      qty: nQty,
      base_price: Number(p.price) || 0,
      image: p.image || ""
    });
  }
  persistQuoteState();
  if (!silent) showToast(`🛒 Đã thêm ${nQty} × ${p.model} vào Giỏ công trình`);
}

function removeEquipItem(uid) {
  QUOTE.equip_items = QUOTE.equip_items.filter(x => x.uid !== uid);
  persistQuoteState();
  renderCartTables();
}

function clearEquipCart() {
  if (!QUOTE.equip_items.length) return;
  QUOTE.equip_items = [];
  persistQuoteState();
  renderCartTables();
  showToast("Đã xóa danh mục thiết bị Phần A");
}

/* ---------------- SMART AUTO-ACCESSORIES & AUTO-MATERIALS ---------------- */
function autoSuggestAccessories() {
  if (!QUOTE.equip_items.length) {
    showToast("Vui lòng chọn ít nhất 1 dàn nóng/dàn lạnh ở Phần A trước!");
    return;
  }
  let fxfqCount = 0, ffaCount = 0, vrvIndoorNeedRemote = 0, totalVrvIndoors = 0;
  let needJoint2 = 0, needJoint3 = 0;

  QUOTE.equip_items.forEach(it => {
    const p = DB.products.find(x => x.id === it.prod_id);
    if (!p) return;
    if (p.model.startsWith("FXFQ")) fxfqCount += it.qty;
    if (p.model.startsWith("FFA")) ffaCount += it.qty;
    if (p.category_id.startsWith("VRV_IN_")) {
      totalVrvIndoors += it.qty;
      vrvIndoorNeedRemote += it.qty;
    }
    if (p.category_id === "VRV_H_OUT" || p.category_id === "VRV_A_OUT") {
      const hpNum = parseInt(p.hp, 10) || 0;
      if (hpNum >= 26 && hpNum <= 48) needJoint2 += it.qty;
      if (hpNum >= 50) needJoint3 += it.qty;
    }
  });

  const ensureEquipQty = (pid, targetQty) => {
    if (targetQty <= 0) return;
    const ex = QUOTE.equip_items.find(x => x.prod_id === pid);
    if (ex) ex.qty = Math.max(ex.qty, targetQty);
    else addToEquipCart(pid, targetQty, true);
  };

  if (fxfqCount > 0) ensureEquipQty("BYCQ125EAF", fxfqCount);
  if (ffaCount > 0) ensureEquipQty("BYFQ60B3W1", ffaCount);
  if (vrvIndoorNeedRemote > 0) ensureEquipQty("BRC1E63", vrvIndoorNeedRemote);
  if (needJoint2 > 0) ensureEquipQty("BFHP22R135", needJoint2);
  if (needJoint3 > 0) ensureEquipQty("BFHP22R168", needJoint3);
  if (totalVrvIndoors >= 2) {
    ensureEquipQty("KHRP26A33T8", Math.max(1, Math.floor(totalVrvIndoors / 4)));
    ensureEquipQty("KHRP26A22T8", Math.max(1, totalVrvIndoors - 1 - Math.floor(totalVrvIndoors / 4)));
  }

  persistQuoteState();
  renderCartTables();
  showToast("⚡ Đã tự động bổ sung Mặt nạ Cassette, Điều khiển dây & Bộ chia gas REFNET!");
}

function autoEstimateMaterialsFromEquip(silent) {
  if (!QUOTE.equip_items.length) {
    if (!silent) showToast("Giỏ thiết bị Phần A đang trống — hãy chọn thiết bị trước!");
    return;
  }

  const matMap = {};
  DB.materials.forEach(m => (matMap[m.id] = m));
  const newInst = [];

  const pushMat = (id, qty) => {
    const m = matMap[id];
    const rQty = Math.round(qty * 10) / 10;
    if (!m || rQty <= 0) return;
    const ex = newInst.find(x => x.mat_id === id);
    if (ex) ex.qty = Math.round((ex.qty + rQty) * 10) / 10;
    else {
      newInst.push({
        uid: makeUid(),
        mat_id: m.id,
        group_code: m.group_code,
        group_name: m.group_name,
        name: m.name,
        brand: m.brand,
        cost_type: m.cost_type,
        unit: m.unit,
        qty: rQty,
        base_price: m.base_price
      });
    }
  };

  let totalIndoors = 0;
  let totalOutdoors = 0;
  let totalDuctInsulM2 = 0;
  let totalSpigotsD200 = 0;
  let totalSpigotsD250 = 0;

  QUOTE.equip_items.forEach(it => {
    const p = DB.products.find(x => x.id === it.prod_id);
    if (!p) return;
    const q = it.qty;
    const btu = p.cooling_btu || 0;
    const hp = parseInt(p.hp, 10) || 0;

    // Outdoor units
    if (p.category_id === "VRV_H_OUT" || p.category_id === "VRV_A_OUT") {
      totalOutdoors += q;
      if (hp <= 24) { pushMat("B1_01", q); pushMat("B1_27", q); }
      else if (hp <= 48) { pushMat("B1_02", q); pushMat("B1_28", q); }
      else { pushMat("B1_03", q); pushMat("B1_29", q); }
    } else if (p.category_id === "VRV_S_OUT" || p.category_id === "MULTI_OUT") {
      totalOutdoors += q;
      if (hp <= 6) pushMat("B1_04", q);
      else pushMat("B1_05", q);
      pushMat("B1_30", q);
    }

    // Room Air & SkyAir sets
    if (p.category_id === "ROOM_AIR") {
      totalIndoors += q;
      if (btu <= 13000) { pushMat("B1_17", q); pushMat("B1_24", q); }
      else { pushMat("B1_18", q); pushMat("B1_25", q); }
    } else if (p.category_id.startsWith("SKY_")) {
      totalIndoors += q;
      if (btu <= 25000) { pushMat("B1_19", q); pushMat("B1_25", q); }
      else { pushMat("B1_20", q); pushMat("B1_26", q); }
      pushMat("B1_31", q);
    }

    // VRV & Multi Indoors
    if (p.category_id.startsWith("VRV_IN_") || p.category_id.startsWith("MULTI_IN_")) {
      if (btu > 0) {
        totalIndoors += q;
        if (p.category_id.includes("WALL")) {
          pushMat(btu <= 16000 ? "B1_06" : "B1_07", q);
        } else if (p.category_id.includes("CASSETTE")) {
          pushMat(btu <= 16000 ? "B1_08" : (btu <= 31000 ? "B1_09" : "B1_10"), q);
          pushMat("B1_31", q);
        } else if (p.duct) {
          pushMat(btu <= 16000 ? "B1_11" : (btu <= 31000 ? "B1_12" : "B1_13"), q);
          pushMat("B1_31", q);
        } else {
          pushMat("B1_09", q);
          pushMat("B1_31", q);
        }
      }
    }

    // Ducted units (VRV, SkyAir, Multi) -> Plenum box, Canvas, Grilles, Flex duct, VCD
    if (p.duct && btu > 0) {
      if (btu <= 16000) pushMat("B5_01", q);
      else if (btu <= 31000) pushMat("B5_02", q);
      else pushMat("B5_03", q);

      pushMat("B5_70", q * 2); // Cổ bạt mềm đầu cấp + hồi
      pushMat("B5_72", q);     // Nhân công lắp côn gió & cửa gió
      totalDuctInsulM2 += (p.duct.insul_m2 || 0.6) * 2.2 * q;

      const sp = parseSpigotSpec(`${p.duct.propose || ""} ${p.duct.std_box || ""}`);
      if (sp.dia >= 250) totalSpigotsD250 += sp.count * q;
      else totalSpigotsD200 += sp.count * q;

      // Supply + Return Linear Slot / Frameless Grilles + Plenum boxes
      if (btu <= 20000) {
        pushMat("B5_43", q * 2); // Cửa Slot 1000x150 (cấp + hồi)
        pushMat("B5_51", q * 2); // Hộp gió cửa
      } else {
        pushMat("B5_45", q * 2); // Cửa Slot 1200x150 (cấp + hồi)
        pushMat("B5_52", q * 2);
      }
      pushMat("B5_53", q); // Lưới lọc bụi cửa hồi
    }

    // Refnet & Remotes installation labor
    if (p.model.includes("HRP") || p.model.includes("FHP")) pushMat("B1_14", q);
    if (p.model.startsWith("BRC")) pushMat("B1_15", q);
    if (p.model.startsWith("DCS") || p.model.startsWith("DCM601")) pushMat("B1_16", q);
  });

  if (totalOutdoors > 0) pushMat("B1_32", 1);

  // Piping, Drain & Electrical estimates proportional to indoor/outdoor count
  const estUnits = Math.max(1, totalIndoors);
  const pipePerUnit = 10; // ~10m average run per indoor unit (editable by engineer!)
  pushMat("B2_06", Math.round(estUnits * pipePerUnit * 0.5)); // D6.4
  pushMat("B2_07", Math.round(estUnits * pipePerUnit * 0.5)); // D9.5
  pushMat("B2_08", Math.round(estUnits * pipePerUnit * 0.5)); // D12.7
  pushMat("B2_09", Math.round(estUnits * pipePerUnit * 0.5)); // D15.9
  if (totalOutdoors > 0) {
    pushMat("B2_14", 12 * totalOutdoors); // D28.6 trục chính
    pushMat("B2_34", 12 * totalOutdoors); // Bảo ôn D28
  }
  pushMat("B2_28", Math.round(estUnits * pipePerUnit * 0.5));
  pushMat("B2_29", Math.round(estUnits * pipePerUnit * 0.5));
  pushMat("B2_30", Math.round(estUnits * pipePerUnit * 0.5));
  pushMat("B2_31", Math.round(estUnits * pipePerUnit * 0.5));
  pushMat("B2_41", Math.max(2, Math.round(estUnits * 1.5))); // Băng cuốn
  pushMat("B2_42", Math.round(estUnits * 8));                 // Giá treo ống đồng
  pushMat("B2_43", 1);                                         // Nitơ hàn thử kín
  pushMat("B2_44", Math.max(2, Math.round(estUnits * 0.8))); // Gas bổ sung
  pushMat("B2_50", estUnits * pipePerUnit);                  // Nhân công đi ống đồng

  // Section III: Condensate PVC
  pushMat("B3_02", estUnits * 6);
  pushMat("B3_03", Math.max(8, Math.round(estUnits * 3)));
  pushMat("B3_17", estUnits * 6);
  pushMat("B3_18", Math.max(8, Math.round(estUnits * 3)));
  pushMat("B3_14", 1);
  pushMat("B3_23", estUnits * 6);
  pushMat("B3_25", estUnits * 9);

  // Section IV: Electrical & Signal
  pushMat("B4_01", estUnits * 10);
  pushMat("B4_02", estUnits * 12);
  pushMat("B4_03", estUnits * 6);
  pushMat("B4_04", estUnits * 10);
  pushMat("B4_05", estUnits * 8);
  pushMat("B4_09", estUnits * 14);

  // Section V: Ductwork extras if ducted units exist
  if (totalSpigotsD200 > 0) {
    pushMat("B5_57", totalSpigotsD200);
    pushMat("B5_63", totalSpigotsD200 * 3);
  }
  if (totalSpigotsD250 > 0) {
    pushMat("B5_58", totalSpigotsD250);
    pushMat("B5_64", totalSpigotsD250 * 3);
  }
  if (totalDuctInsulM2 > 0) {
    pushMat("B5_09", Math.ceil(totalDuctInsulM2 + (totalSpigotsD200 + totalSpigotsD250) * 0.8));
    pushMat("B5_68", Math.ceil((totalSpigotsD200 + totalSpigotsD250) * 1.5));
    pushMat("B5_69", totalIndoors * 2);
  }

  // Sort by group I -> V
  const order = { I: 1, II: 2, III: 3, IV: 4, V: 5 };
  newInst.sort((a, b) => (order[a.group_code] || 9) - (order[b.group_code] || 9));

  QUOTE.install_items = newInst;
  persistQuoteState();
  renderCartTables();
  if (!silent) showToast("⚡ Đã tự động bóc tách 5 nhóm Vật tư & Nhân công chuẩn theo Thiết bị!");
}

/* ---------------- MATERIAL PICKER & CUSTOM ROWS ---------------- */
function openMaterialPickerModal() {
  document.getElementById("mat-modal").classList.add("open");
  renderMaterialPicker();
}

function renderMaterialPicker() {
  const q = (document.getElementById("mat-search").value || "").trim().toLowerCase();
  const grp = document.getElementById("mat-group-filter").value;
  const tbody = document.getElementById("mat-picker-tbody");

  const list = DB.materials.filter(m => {
    if (grp !== "ALL" && m.group_code !== grp) return false;
    if (q && !`${m.name} ${m.brand} ${m.group_name}`.toLowerCase().includes(q)) return false;
    return true;
  });

  tbody.innerHTML = list.map(m => `
    <tr>
      <td><strong>Phần ${m.group_code}</strong></td>
      <td>${m.name}</td>
      <td>${m.brand}</td>
      <td>${m.cost_type === "labor" ? `<span style="color:#B91C1C;font-weight:700;">Nhân công</span>` : `<span style="color:#0369A1;font-weight:700;">Vật tư</span>`}</td>
      <td>${m.unit}</td>
      <td><input type="number" class="price-edit-input" step="1000" value="${m.base_price}" title="Sửa trực tiếp giá gốc đầu vào" onchange="saveMaterialOverride('${m.id}', {base_price: Number(this.value)}); showToast('Đã lưu giá gốc vật tư/NC!');" /></td>
      <td><button class="btn btn-sm btn-primary" onclick="addInstallMaterial('${m.id}')">+ Thêm</button></td>
    </tr>
  `).join("");
}

function addInstallMaterial(matId) {
  const m = DB.materials.find(x => x.id === matId);
  if (!m) return;
  const ex = QUOTE.install_items.find(x => x.mat_id === matId);
  if (ex) ex.qty += 1;
  else {
    QUOTE.install_items.push({
      uid: makeUid(),
      mat_id: m.id,
      group_code: m.group_code,
      group_name: m.group_name,
      name: m.name,
      brand: m.brand,
      cost_type: m.cost_type,
      unit: m.unit,
      qty: 1,
      base_price: m.base_price
    });
  }
  persistQuoteState();
  renderCartTables();
  showToast(`Đã thêm: ${m.name}`);
}

function addCustomInstallRow() {
  QUOTE.install_items.push({
    uid: makeUid(),
    mat_id: "CUSTOM",
    group_code: "I",
    group_name: "I. Phần nhân công lắp đặt thiết bị & Giá đỡ",
    name: "Hạng mục vật tư / nhân công bổ sung...",
    brand: "Việt Nam",
    cost_type: "material",
    unit: "bộ",
    qty: 1,
    base_price: 500000
  });
  persistQuoteState();
  renderCartTables();
}

function removeInstallItem(uid) {
  QUOTE.install_items = QUOTE.install_items.filter(x => x.uid !== uid);
  persistQuoteState();
  renderCartTables();
}

function clearInstallCart() {
  QUOTE.install_items = [];
  persistQuoteState();
  renderCartTables();
  showToast("Đã xóa Phần B Vật tư & Nhân công");
}

/* ---------------- CALCULATIONS ---------------- */
function getItemQuotedUnitPrice(item, isEquip) {
  const base = Number(item.base_price) || 0;
  if (isEquip) return Math.round(base * QUOTE.mult_equip);
  const mult = item.cost_type === "labor" ? QUOTE.mult_labor : QUOTE.mult_mat;
  return Math.round(base * mult);
}

function computeTotals() {
  let sumEquip = 0;
  let sumInstallMat = 0;
  let sumInstallLabor = 0;

  if (QUOTE.mode === "BOTH" || QUOTE.mode === "EQUIP_ONLY") {
    QUOTE.equip_items.forEach(it => {
      sumEquip += getItemQuotedUnitPrice(it, true) * (Number(it.qty) || 0);
    });
  }
  if (QUOTE.mode === "BOTH" || QUOTE.mode === "INSTALL_ONLY") {
    QUOTE.install_items.forEach(it => {
      const line = getItemQuotedUnitPrice(it, false) * (Number(it.qty) || 0);
      if (it.cost_type === "labor") sumInstallLabor += line;
      else sumInstallMat += line;
    });
  }

  const sumInstall = sumInstallMat + sumInstallLabor;
  const subTotal = sumEquip + sumInstall;
  const vatAmount = Math.round(subTotal * (QUOTE.vat_rate / 100));
  const grandTotal = subTotal + vatAmount;
  const qrAmount = QUOTE.qr_percent > 0 ? Math.round(grandTotal * (QUOTE.qr_percent / 100)) : 0;

  return { sumEquip, sumInstallMat, sumInstallLabor, sumInstall, subTotal, vatAmount, grandTotal, qrAmount };
}

function updateTopbarCartSummary() {
  const count = QUOTE.equip_items.reduce((s, x) => s + Number(x.qty || 0), 0);
  const t = computeTotals();
  const b1 = document.getElementById("badge-cart-count");
  const b2 = document.getElementById("top-cart-count");
  const b3 = document.getElementById("top-cart-sum");
  if (b1) b1.textContent = count;
  if (b2) b2.textContent = count;
  if (b3) b3.textContent = formatVND(t.grandTotal);
}

/* ---------------- RENDER CART TABLES ---------------- */
function renderCartTables() {
  const eqTbody = document.getElementById("cart-equip-tbody");
  const inTbody = document.getElementById("cart-install-tbody");
  if (!eqTbody || !inTbody) return;

  if (!QUOTE.equip_items.length) {
    eqTbody.innerHTML = `<tr><td colspan="10" style="text-align:center;padding:24px;color:#64748B;">Chưa có thiết bị nào trong Phần A. Bấm <strong>"➕ Chọn thêm Thiết bị (Xem ảnh & Thông số)"</strong> hoặc <strong>"Nạp dự án mẫu"</strong>.</td></tr>`;
  } else {
    eqTbody.innerHTML = QUOTE.equip_items.map((it, idx) => {
      const qPrice = getItemQuotedUnitPrice(it, true);
      const lineTotal = qPrice * (Number(it.qty) || 0);
      const pRef = DB.products.find(x => x.id === it.prod_id) || {};
      const imgSrc = it.image || pRef.image || "assets/logo_minh_phu.png";
      const capBadge = pRef.cooling_btu > 0 ? `${formatNum(pRef.cooling_btu)} Btu/h (${pRef.hp})` : (pRef.hp || "");
      const dimBadge = pRef.dimensions ? `KT: ${pRef.dimensions} mm${pRef.weight ? " • " + pRef.weight : ""}` : "";
      const pipeBadge = pRef.gas_pipe ? `Ống đồng: ${pRef.gas_pipe}${pRef.drain_pipe ? " • Xả " + pRef.drain_pipe : ""}` : "";
      const ductBadge = pRef.duct
        ? `Côn cấp: ${pRef.duct.supply_collar} | Hồi: ${pRef.duct.return_collar} mm • ${pRef.duct.std_box || pRef.duct.propose}`
        : (pRef.ceiling_opening ? `Lỗ trần: ${pRef.ceiling_opening}` : "");

      return `
        <tr>
          <td style="text-align:center;font-weight:700;">${idx + 1}</td>
          <td style="text-align:center;">
            <div onclick="${pRef.id ? `openProductModal('${pRef.id}')` : ""}" title="Bấm xem ảnh lớn, bản vẽ Côn đầu máy & Catalogue" style="width:82px;height:66px;margin:0 auto;background:radial-gradient(circle,#FFF 0%,#F0F9FF 100%);border:1.5px solid #BAE6FD;border-radius:8px;padding:4px;display:flex;align-items:center;justify-content:center;cursor:pointer;position:relative;">
              <img src="${imgSrc}" alt="${it.model}" style="max-width:100%;max-height:100%;object-fit:contain;" />
            </div>
          </td>
          <td>
            <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
              <strong style="color:#005A8D;font-size:13.5px;cursor:pointer;" onclick="${pRef.id ? `openProductModal('${pRef.id}')` : ""}">${it.model}</strong>
              <input type="text" value="${it.name.replace(/"/g, '&quot;')}" onchange="updateEquipField('${it.uid}','name',this.value)" style="border:none;border-bottom:1px dashed #CBD5E1;flex:1;min-width:180px;font-weight:700;color:#0F172A;background:transparent;" />
              ${pRef.id ? `<button class="btn btn-sm btn-ice" style="padding:2px 7px;font-size:11px;" onclick="openProductModal('${pRef.id}')">🔍 Ảnh & Côn</button>` : ""}
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:5px;margin-top:5px;">
              ${capBadge ? `<span style="background:#E0F2FE;color:#0C4A6E;font-size:11px;font-weight:700;padding:1px 7px;border-radius:4px;">❄️ ${capBadge}</span>` : ""}
              ${dimBadge ? `<span style="background:#F1F5F9;color:#334155;font-size:11px;font-weight:600;padding:1px 7px;border-radius:4px;">📏 ${dimBadge}</span>` : ""}
              ${pipeBadge ? `<span style="background:#FEF2F2;color:#991B1B;font-size:11px;font-weight:700;padding:1px 7px;border-radius:4px;">🔧 ${pipeBadge}</span>` : ""}
              ${ductBadge ? `<span style="background:#EFF6FF;color:#0F172A;border:1px solid #BFDBFE;font-size:11px;font-weight:700;padding:1px 7px;border-radius:4px;">📐 ${ductBadge}</span>` : ""}
            </div>
            <input type="text" value="${(it.spec_note || "").replace(/"/g, '&quot;')}" placeholder="Ghi chú thông số in kèm dưới tên máy trong báo giá..." onchange="updateEquipField('${it.uid}','spec_note',this.value)" style="border:none;border-bottom:1px dotted #E2E8F0;color:#475569;font-size:11.2px;width:99%;background:transparent;margin-top:4px;" />
          </td>
          <td><input type="text" value="${it.origin}" onchange="updateEquipField('${it.uid}','origin',this.value)" style="width:98px;border:1px solid #E2E8F0;border-radius:5px;padding:3px 6px;font-size:12px;" /></td>
          <td><input type="text" value="${it.unit}" onchange="updateEquipField('${it.uid}','unit',this.value)" style="width:46px;border:1px solid #E2E8F0;border-radius:5px;padding:3px 5px;text-align:center;font-size:12px;" /></td>
          <td><input type="number" class="qty-input" min="1" value="${it.qty}" onchange="updateEquipField('${it.uid}','qty',Number(this.value))" /></td>
          <td><input type="number" class="price-edit-input" style="border-color:#005A8D;background:#FFFFFF;color:#991B1B;" step="10000" value="${it.base_price}" title="Chỉnh sửa đơn giá gốc đầu vào (VNĐ)" onchange="updateEquipField('${it.uid}','base_price',Number(this.value))" /></td>
          <td style="text-align:right;font-weight:700;color:#0F172A;">${formatVND(qPrice)}</td>
          <td style="text-align:right;font-weight:700;color:#005A8D;">${formatVND(lineTotal)}</td>
          <td style="text-align:center;"><button class="btn btn-sm btn-outline" onclick="removeEquipItem('${it.uid}')">✕</button></td>
        </tr>
      `;
    }).join("");
  }

  if (!QUOTE.install_items.length) {
    inTbody.innerHTML = `<tr><td colspan="10" style="text-align:center;padding:24px;color:#64748B;">Chưa có mục Vật tư / Nhân công nào. Bấm <strong>"⚡ Tự động bóc tách Vật tư & Nhân công từ Thiết bị"</strong> để tạo nhanh!</td></tr>`;
  } else {
    let lastGroup = "";
    const rowsHtml = [];
    let stt = 1;
    QUOTE.install_items.forEach(it => {
      if (it.group_name !== lastGroup) {
        lastGroup = it.group_name;
        rowsHtml.push(`
          <tr style="background:#F1F5F9;">
            <td colspan="10" style="font-weight:700;color:#0F172A;padding:8px 12px;">${lastGroup}</td>
          </tr>
        `);
      }
      const qPrice = getItemQuotedUnitPrice(it, false);
      const lineTotal = qPrice * (Number(it.qty) || 0);
      rowsHtml.push(`
        <tr>
          <td style="text-align:center;">${stt++}</td>
          <td><input type="text" value="${it.name.replace(/"/g, '&quot;')}" onchange="updateInstallField('${it.uid}','name',this.value)" style="width:100%;border:none;border-bottom:1px dashed #E2E8F0;background:transparent;font-size:12.5px;" /></td>
          <td><input type="text" value="${it.brand}" onchange="updateInstallField('${it.uid}','brand',this.value)" style="width:82px;border:1px solid #E2E8F0;border-radius:5px;padding:3px 5px;font-size:12px;" /></td>
          <td>
            <select onchange="updateInstallField('${it.uid}','cost_type',this.value)" style="border:1px solid #E2E8F0;border-radius:5px;padding:3px;font-size:11.5px;font-weight:700;color:${it.cost_type === 'labor' ? '#B91C1C' : '#0369A1'};">
              <option value="material" ${it.cost_type === "material" ? "selected" : ""}>Vật tư</option>
              <option value="labor" ${it.cost_type === "labor" ? "selected" : ""}>Nhân công</option>
            </select>
          </td>
          <td><input type="text" value="${it.unit}" onchange="updateInstallField('${it.uid}','unit',this.value)" style="width:46px;border:1px solid #E2E8F0;border-radius:5px;padding:3px;text-align:center;font-size:12px;" /></td>
          <td><input type="number" class="qty-input" step="0.5" min="0" value="${it.qty}" onchange="updateInstallField('${it.uid}','qty',Number(this.value))" /></td>
          <td><input type="number" class="price-edit-input" style="border-color:#005A8D;background:#FFFFFF;color:#991B1B;" step="1000" value="${it.base_price}" title="Chỉnh sửa đơn giá gốc đầu vào (VNĐ)" onchange="updateInstallField('${it.uid}','base_price',Number(this.value))" /></td>
          <td style="text-align:right;font-weight:700;">${formatVND(qPrice)}</td>
          <td style="text-align:right;font-weight:700;color:#B91C1C;">${formatVND(lineTotal)}</td>
          <td style="text-align:center;"><button class="btn btn-sm btn-outline" onclick="removeInstallItem('${it.uid}')">✕</button></td>
        </tr>
      `);
    });
    inTbody.innerHTML = rowsHtml.join("");
  }
  updateTopbarCartSummary();
}

function updateEquipField(uid, field, val) {
  const it = QUOTE.equip_items.find(x => x.uid === uid);
  if (!it) return;
  it[field] = val;
  const syncChk = document.getElementById("chk-sync-base-price");
  if (field === "base_price" && syncChk && syncChk.checked && it.prod_id && typeof savePriceOverride === "function") {
    savePriceOverride(it.prod_id, Number(val) || 0);
    renderCatalog();
    showToast(`💾 Đã cập nhật giá gốc đầu vào ${it.model}: ${formatVND(val)}`);
  }
  persistQuoteState();
  renderCartTables();
}

function updateInstallField(uid, field, val) {
  const it = QUOTE.install_items.find(x => x.uid === uid);
  if (!it) return;
  it[field] = val;
  const syncChk = document.getElementById("chk-sync-base-price");
  if ((field === "base_price" || field === "cost_type") && syncChk && syncChk.checked && it.mat_id && it.mat_id !== "CUSTOM" && typeof saveMaterialOverride === "function") {
    saveMaterialOverride(it.mat_id, { [field]: val });
    showToast(`💾 Đã cập nhật giá gốc Vật tư / Nhân công!`);
  }
  persistQuoteState();
  renderCartTables();
}

/* ---------------- VISUAL SPLIT-VIEW EQUIPMENT PICKER MODAL ---------------- */
let currentEpmSelectedId = "";

function openQuickEquipPickerModal() {
  const catSel = document.getElementById("epm-cat");
  if (catSel && catSel.options.length <= 1) {
    catSel.innerHTML = `<option value="ALL">Tất cả dòng sản phẩm (${DB.categories.length})</option>` +
      DB.categories.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
  }
  document.getElementById("equip-picker-modal").classList.add("open");
  renderQuickEquipPickerList();
}

function renderQuickEquipPickerList() {
  const q = (document.getElementById("epm-search").value || "").trim().toLowerCase();
  const catId = document.getElementById("epm-cat").value || "ALL";
  const list = DB.products.filter(p => {
    if (catId !== "ALL" && p.category_id !== catId) return false;
    if (q) {
      const ductTxt = p.duct ? `${p.duct.supply_collar} ${p.duct.return_collar} ${p.duct.std_box}` : "";
      if (!`${p.model} ${p.name} ${p.hp} ${p.cooling_btu} ${ductTxt}`.toLowerCase().includes(q)) return false;
    }
    return true;
  });

  const wrap = document.getElementById("epm-list-wrap");
  if (!list.length) {
    wrap.innerHTML = `<div style="padding:30px;text-align:center;color:#64748B;">Không tìm thấy Model phù hợp</div>`;
    return;
  }

  if (!currentEpmSelectedId || !list.some(x => x.id === currentEpmSelectedId)) {
    currentEpmSelectedId = list[0].id;
  }

  wrap.innerHTML = `
    <table class="clean-table" style="font-size:12px;">
      <thead>
        <tr>
          <th style="width:62px;">Hình</th>
          <th>Model & Công suất</th>
          <th>Giá gốc</th>
          <th style="width:68px;">Chọn</th>
        </tr>
      </thead>
      <tbody>
        ${list.slice(0, 120).map(p => `
          <tr onclick="previewQuickEquipItem('${p.id}')" style="cursor:pointer;${p.id === currentEpmSelectedId ? 'background:#E0F2FE;' : ''}">
            <td>
              <div style="width:54px;height:42px;background:#fff;border:1px solid #CBD5E1;border-radius:6px;padding:2px;display:flex;align-items:center;justify-content:center;">
                <img src="${p.image}" style="max-width:100%;max-height:100%;object-fit:contain;" />
              </div>
            </td>
            <td>
              <strong style="color:#005A8D;font-size:13px;">${p.model}</strong>
              <div style="font-size:11px;color:#334155;">${p.name}</div>
              <div style="font-size:10.5px;color:#0369A1;font-weight:700;">${p.cooling_btu > 0 ? formatNum(p.cooling_btu) + " Btu/h" : p.hp} ${p.duct ? "• Côn: " + p.duct.supply_collar : ""}</div>
            </td>
            <td style="font-weight:700;color:#991B1B;white-space:nowrap;">${p.price > 0 ? formatVND(p.price) : "Chưa nhập"}</td>
            <td onclick="event.stopPropagation();">
              <button class="btn btn-sm btn-primary" onclick="addToEquipCart('${p.id}', 1); renderCartTables();">+ Giỏ</button>
            </td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
  previewQuickEquipItem(currentEpmSelectedId, true);
}

function previewQuickEquipItem(prodId, skipRehighlight) {
  currentEpmSelectedId = prodId;
  const p = DB.products.find(x => x.id === prodId);
  const box = document.getElementById("epm-detail-preview");
  if (!p || !box) return;
  if (!skipRehighlight) renderQuickEquipPickerList();

  box.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
      <div>
        <span style="background:#0077B6;color:#fff;font-size:10.5px;font-weight:700;padding:2px 8px;border-radius:5px;">${p.hp} • ${p.origin}</span>
        <h3 style="font-size:18px;font-weight:700;color:#0F2942;margin-top:4px;">${p.model}</h3>
      </div>
      <button class="btn btn-sm btn-ice" onclick="openProductModal('${p.id}')">📐 Mở Bản vẽ Côn & PDF</button>
    </div>
    <div style="font-size:12.5px;font-weight:600;color:#334155;margin-bottom:10px;">${p.name}</div>

    <div style="background:radial-gradient(circle,#FFFFFF 0%,#E6F6FE 85%);border:1.5px solid #BAE6FD;border-radius:10px;height:195px;display:flex;align-items:center;justify-content:center;padding:12px;position:relative;margin-bottom:12px;">
      <img id="epm-big-img" src="${p.image}" style="max-width:94%;max-height:172px;object-fit:contain;filter:drop-shadow(0 8px 14px rgba(15,23,42,0.16));" />
      ${p.commercial_img ? `<button class="btn btn-sm btn-outline" style="position:absolute;bottom:8px;right:8px;font-size:11px;padding:3px 8px;" onclick="const im=document.getElementById('epm-big-img');im.src=im.src.includes('commercial')?'${p.image}':'${p.commercial_img}';">🖼️ Đổi ảnh Thực tế / PNG</button>` : ""}
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12px;margin-bottom:10px;">
      <div style="background:#fff;border:1px solid #E2E8F0;padding:6px 9px;border-radius:7px;"><span style="color:#64748B;font-size:10.5px;display:block;">Công suất lạnh / Sưởi</span><strong style="color:#005A8D;">${p.cooling_btu > 0 ? formatNum(p.cooling_btu) + " Btu/h (" + p.cooling_kw + " kW)" : p.hp}</strong></div>
      <div style="background:#fff;border:1px solid #E2E8F0;padding:6px 9px;border-radius:7px;"><span style="color:#64748B;font-size:10.5px;display:block;">Kích thước & Trọng lượng</span><strong>${p.dimensions || "—"} mm • ${p.weight || "—"}</strong></div>
      <div style="background:#fff;border:1px solid #E2E8F0;padding:6px 9px;border-radius:7px;"><span style="color:#64748B;font-size:10.5px;display:block;">Ống đồng & Nước xả</span><strong style="color:#991B1B;">${p.gas_pipe || "—"} ${p.drain_pipe ? "• " + p.drain_pipe : ""}</strong></div>
      <div style="background:#fff;border:1px solid #E2E8F0;padding:6px 9px;border-radius:7px;"><span style="color:#64748B;font-size:10.5px;display:block;">Lưu lượng gió / Độ ồn / Điện</span><strong>${p.airflow || "—"} • ${p.noise || "—"}</strong></div>
    </div>

    ${p.duct ? `
      <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-left:4px solid #005A8D;border-radius:8px;padding:8px 11px;font-size:12px;color:#0F172A;margin-bottom:12px;">
        <strong>📐 Côn đầu cấp: ${p.duct.supply_collar} mm | Côn hồi: ${p.duct.return_collar} mm</strong>${p.duct.insul_m2 ? ` (Bảo ôn: ${Number(p.duct.insul_m2).toFixed(3)} m²)` : ""}<br/>
        <span style="color:#005A8D;font-weight:700;">📦 ${p.duct.std_box || p.duct.propose}</span>
      </div>
    ` : ""}

    <div style="display:flex;gap:8px;align-items:center;background:#fff;padding:10px;border-radius:9px;border:1.5px solid #CBD5E1;">
      <div style="flex:1;">
        <div style="font-size:10.5px;color:#64748B;font-weight:700;">Giá gốc đầu vào (${p.unit}):</div>
        <input type="number" step="10000" value="${p.price || 0}" onchange="savePriceOverride('${p.id}', this.value); renderQuickEquipPickerList();" style="width:135px;padding:4px 7px;border:1px solid #005A8D;border-radius:6px;font-weight:700;color:#991B1B;background:#FFFFFF;" />
      </div>
      <div>
        <div style="font-size:10.5px;color:#64748B;font-weight:700;">Số lượng:</div>
        <input type="number" id="epm-qty" value="1" min="1" style="width:58px;padding:5px;border:1px solid #CBD5E1;border-radius:6px;text-align:center;font-weight:700;" />
      </div>
      <button class="btn btn-primary" onclick="addToEquipCart('${p.id}', Number(document.getElementById('epm-qty').value||1)); renderCartTables();">
        🛒 Đưa vào Giỏ
      </button>
    </div>
  `;
}

/* ---------------- SAVE / LOAD PROJECT HISTORY ---------------- */
function saveProjectSnapshot() {
  syncQuoteMeta();
  let list = [];
  try { list = JSON.parse(localStorage.getItem(STORAGE_KEYS.SAVED_PROJECTS) || "[]"); } catch (e) {}
  const snap = JSON.parse(JSON.stringify(QUOTE));
  snap.saved_at = new Date().toLocaleString("vi-VN");
  const idx = list.findIndex(x => x.code === snap.code);
  if (idx >= 0) list[idx] = snap;
  else list.unshift(snap);
  localStorage.setItem(STORAGE_KEYS.SAVED_PROJECTS, JSON.stringify(list.slice(0, 30)));
  renderSavedProjectsList();
  showToast(`💾 Đã lưu hồ sơ báo giá "${snap.code}"!`);
}

function renderSavedProjectsList() {
  const box = document.getElementById("saved-projects-list");
  if (!box) return;
  let list = [];
  try { list = JSON.parse(localStorage.getItem(STORAGE_KEYS.SAVED_PROJECTS) || "[]"); } catch (e) {}
  if (!list.length) {
    box.innerHTML = `<div style="font-size:12.5px;color:#64748B;">Chưa có hồ sơ nào được lưu. Bấm <strong>"💾 Lưu hồ sơ"</strong> để lưu lại phương án báo giá theo từng khách hàng.</div>`;
    return;
  }
  box.innerHTML = list.map((s, i) => `
    <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 10px;background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;">
      <div style="font-size:12.5px;">
        <strong>${s.code}</strong> — ${s.project_name || s.client_name || "Dự án"}
        <div style="font-size:11px;color:#64748B;">Khách hàng: ${s.client_name || "—"} • Lưu lúc: ${s.saved_at}</div>
      </div>
      <div style="display:flex;gap:6px;">
        <button class="btn btn-sm btn-ice" onclick="restoreProjectSnapshot(${i})">📂 Mở lại</button>
        <button class="btn btn-sm btn-outline" onclick="deleteProjectSnapshot(${i})">✕</button>
      </div>
    </div>
  `).join("");
}

function restoreProjectSnapshot(idx) {
  let list = [];
  try { list = JSON.parse(localStorage.getItem(STORAGE_KEYS.SAVED_PROJECTS) || "[]"); } catch (e) {}
  if (!list[idx]) return;
  QUOTE = JSON.parse(JSON.stringify(list[idx]));
  syncQuoteInputsFromState();
  persistQuoteState();
  renderCartTables();
  showToast(`📂 Đã mở hồ sơ báo giá ${QUOTE.code}`);
}

function deleteProjectSnapshot(idx) {
  let list = [];
  try { list = JSON.parse(localStorage.getItem(STORAGE_KEYS.SAVED_PROJECTS) || "[]"); } catch (e) {}
  list.splice(idx, 1);
  localStorage.setItem(STORAGE_KEYS.SAVED_PROJECTS, JSON.stringify(list));
  renderSavedProjectsList();
}

/* ---------------- VIETNAMESE NUMBER TO WORDS ---------------- */
function docSoTienBangChu(soTien) {
  let n = Math.round(Number(soTien) || 0);
  if (n <= 0) return "Không đồng.";
  const chuSo = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"];
  const hang = ["", "nghìn", "triệu", "tỷ", "nghìn tỷ"];

  function doc3So(baso, dayDu) {
    let tram = Math.floor(baso / 100);
    let chuc = Math.floor((baso % 100) / 10);
    let donvi = baso % 10;
    let kq = "";
    if (dayDu || tram > 0) {
      kq += " " + chuSo[tram] + " trăm";
      if (chuc === 0 && donvi > 0) kq += " linh";
    }
    if (chuc > 1) {
      kq += " " + chuSo[chuc] + " mươi";
      if (donvi === 1) kq += " mốt";
      else if (donvi === 5) kq += " lăm";
      else if (donvi > 0) kq += " " + chuSo[donvi];
    } else if (chuc === 1) {
      kq += " mười";
      if (donvi === 5) kq += " lăm";
      else if (donvi > 0) kq += " " + chuSo[donvi];
    } else if (donvi > 0) {
      kq += " " + chuSo[donvi];
    }
    return kq;
  }

  let groups = [];
  while (n > 0) {
    groups.push(n % 1000);
    n = Math.floor(n / 1000);
  }
  let str = "";
  for (let i = groups.length - 1; i >= 0; i--) {
    if (groups[i] > 0) {
      str += doc3So(groups[i], i < groups.length - 1) + (hang[i] ? " " + hang[i] : "");
    }
  }
  str = str.trim().replace(/\s+/g, " ");
  return str.charAt(0).toUpperCase() + str.slice(1) + " đồng chẵn.";
}

/* ---------------- TECHNICAL SPEC APPENDIX HELPERS ---------------- */
function getAppendixConfig() {
  const getChk = (id, defVal) => {
    const el = document.getElementById(id);
    return el ? el.checked : defVal;
  };
  return {
    enabled: getChk("chk-show-appendix", true),
    col_dim: getChk("app-col-dim", true),
    col_pipe: getChk("app-col-pipe", true),
    col_duct: getChk("app-col-duct", true),
    col_air: getChk("app-col-air", true)
  };
}

function buildTechAppendixRows() {
  const hidden = new Set(QUOTE.hidden_appendix_uids || []);
  const rows = [];

  QUOTE.equip_items.forEach(it => {
    if (hidden.has(it.uid)) return;
    const p = DB.products.find(x => x.id === it.prod_id) || {};
    const capStr = p.cooling_btu > 0
      ? `${formatNum(p.cooling_btu)} Btu/h (${p.cooling_kw} kW)${p.heating_btu > 0 ? " / Sưởi " + formatNum(p.heating_btu) + " Btu/h" : ""}`
      : (p.hp || "Phụ kiện đồng bộ");
    const dimWeight = `${p.dimensions || "—"} mm | Nặng: ${p.weight || "—"}`;
    const pipeStr = `Gas: ${p.gas_pipe || "—"} | Xả: ${p.drain_pipe || "—"}`;
    let ductStr = "Không nối ống gió";
    if (p.duct) {
      ductStr = `Côn cấp: ${p.duct.supply_collar} mm | Côn hồi: ${p.duct.return_collar} mm | Bảo ôn hộp: ${p.duct.insul_m2 ? Number(p.duct.insul_m2).toFixed(3) + " m²" : "—"} | ${p.duct.std_box || p.duct.propose || ""}`;
    } else if (p.ceiling_opening) {
      ductStr = `Lỗ mở trần: ${p.ceiling_opening} ${p.panel_dim ? "| Mặt nạ: " + p.panel_dim : ""}`;
    }
    const airStr = `Gió: ${p.airflow || "—"} | Ồn: ${p.noise || "—"}${p.power_supply ? " | " + p.power_supply : ""}`;

    rows.push({
      uid: it.uid,
      is_custom: false,
      model: it.model,
      name: it.name,
      qty: it.qty,
      image: it.image || p.image || "",
      capacity: it.app_capacity || capStr,
      dim_weight: it.app_dim_weight || dimWeight,
      pipe_drain: it.app_pipe_drain || pipeStr,
      duct_plenum: it.app_duct_plenum || ductStr,
      air_power: it.app_air_power || airStr
    });
  });

  (QUOTE.custom_appendix_rows || []).forEach(cr => {
    rows.push(Object.assign({ is_custom: true }, cr));
  });

  return rows;
}

function hideAppendixRow(uid, isCustom) {
  if (isCustom) {
    QUOTE.custom_appendix_rows = (QUOTE.custom_appendix_rows || []).filter(r => r.uid !== uid);
  } else {
    if (!Array.isArray(QUOTE.hidden_appendix_uids)) QUOTE.hidden_appendix_uids = [];
    if (!QUOTE.hidden_appendix_uids.includes(uid)) QUOTE.hidden_appendix_uids.push(uid);
  }
  persistQuoteState();
  renderQuotePreview();
  showToast("Đã cắt dòng thông số khỏi Phụ lục Báo giá");
}

function resetHiddenAppendixRows() {
  QUOTE.hidden_appendix_uids = [];
  persistQuoteState();
  renderQuotePreview();
  showToast("🔄 Đã hiển thị đầy đủ thông số tất cả thiết bị trong đơn hàng");
}

function addCustomAppendixRow() {
  if (!Array.isArray(QUOTE.custom_appendix_rows)) QUOTE.custom_appendix_rows = [];
  QUOTE.custom_appendix_rows.push({
    uid: makeUid(),
    model: "MODEL-TUY-CHINH",
    name: "Thiết bị / Hạng mục kỹ thuật bổ sung",
    qty: 1,
    image: "assets/logo_minh_phu.png",
    capacity: "24.200 Btu/h (7.1 kW)",
    dim_weight: "245x1000x800 mm | 35 kg",
    pipe_drain: "Gas: Ø9.5 / Ø15.9 | Xả: VP25",
    duct_plenum: "Côn cấp: 795x180 mm | Côn hồi: 955x210 mm | Hộp 1000x220, H250, 4D200",
    air_power: "1260 m³/h | 36 dB(A) | 1 pha 220V"
  });
  persistQuoteState();
  renderQuotePreview();
  showToast("➕ Đã thêm dòng thông số kỹ thuật tùy chỉnh");
}

function updateAppendixCell(uid, isCustom, field, textVal) {
  if (isCustom) {
    const cr = (QUOTE.custom_appendix_rows || []).find(x => x.uid === uid);
    if (cr) cr[field] = textVal;
  } else {
    const it = QUOTE.equip_items.find(x => x.uid === uid);
    if (it) it["app_" + field] = textVal;
  }
  persistQuoteState();
}

/* ---------------- RENDER MINH PHÚ GRADIENT A4 QUOTATION ---------------- */
function renderQuotePreview() {
  const container = document.getElementById("quote-a4-container");
  if (!container) return;

  const showImg = document.getElementById("chk-show-img-in-quote").checked;
  const showDuct = document.getElementById("chk-show-duct-in-quote").checked;
  const appCfg = getAppendixConfig();
  const toggleBar = document.getElementById("appendix-col-toggles");
  if (toggleBar) toggleBar.style.display = appCfg.enabled ? "flex" : "none";

  const c = DB.company;
  const b = c.bank || {};
  const t = computeTotals();

  const includeEquip = (QUOTE.mode === "BOTH" || QUOTE.mode === "EQUIP_ONLY") && QUOTE.equip_items.length > 0;
  const includeInstall = (QUOTE.mode === "BOTH" || QUOTE.mode === "INSTALL_ONLY") && QUOTE.install_items.length > 0;

  const modeTitle = QUOTE.mode === "EQUIP_ONLY"
    ? "BẢNG BÁO GIÁ CUNG CẤP THIẾT BỊ ĐIỀU HÒA KHÔNG KHÍ DAIKIN"
    : (QUOTE.mode === "INSTALL_ONLY"
      ? "BẢNG BÁO GIÁ VẬT TƯ & NHÂN CÔNG LẮP ĐẶT HỆ THỐNG ĐHKK"
      : "BẢNG BÁO GIÁ CUNG CẤP THIẾT BỊ & THI CÔNG LẮP ĐẶT HỆ THỐNG ĐHKK");

  const qrNote = `${b.note_prefix || "TT"} ${QUOTE.code}`;
  const qrUrl = getVietQrUrl(t.qrAmount, qrNote);
  const qrFallback = buildOfflineQrFallbackSvgDataUrl();

  let tableRows = "";

  if (includeEquip) {
    tableRows += `
      <tr class="sec-part">
        <td style="text-align:center;">A</td>
        <td colspan="${showImg ? 6 : 5}">PHẦN CUNG CẤP THIẾT BỊ ĐIỀU HÒA KHÔNG KHÍ CHÍNH HÃNG DAIKIN</td>
        <td style="text-align:right;color:#991B1B;">${formatNum(t.sumEquip)}</td>
      </tr>
    `;
    QUOTE.equip_items.forEach((it, idx) => {
      const uPrice = getItemQuotedUnitPrice(it, true);
      const lTotal = uPrice * Number(it.qty || 0);
      tableRows += `
        <tr>
          <td style="text-align:center;font-weight:700;">${idx + 1}</td>
          ${showImg ? `<td style="text-align:center;width:62px;"><img src="${it.image || 'assets/logo_minh_phu.png'}" style="width:52px;height:42px;object-fit:contain;" /></td>` : ""}
          <td>
            <div contenteditable="true" style="font-weight:700;color:#0F172A;">${it.name}</div>
            <div contenteditable="true" style="font-weight:700;color:#005A8D;font-size:11.8px;">Model: ${it.model}</div>
            ${showDuct && it.spec_note ? `<div contenteditable="true" style="font-size:11.2px;color:#475569;margin-top:2px;">${it.spec_note}</div>` : ""}
          </td>
          <td contenteditable="true" style="text-align:center;">${it.origin}</td>
          <td contenteditable="true" style="text-align:center;">${it.unit}</td>
          <td style="text-align:center;font-weight:700;">${formatNum(it.qty)}</td>
          <td style="text-align:right;font-weight:600;">${formatNum(uPrice)}</td>
          <td style="text-align:right;font-weight:700;color:#0F172A;">${formatNum(lTotal)}</td>
        </tr>
      `;
    });
  }

  if (includeInstall) {
    tableRows += `
      <tr class="sec-part">
        <td style="text-align:center;">${includeEquip ? "B" : "A"}</td>
        <td colspan="${showImg ? 6 : 5}">PHẦN VẬT TƯ PHỤ & NHÂN CÔNG LẮP ĐẶT HỆ THỐNG</td>
        <td style="text-align:right;color:#991B1B;">${formatNum(t.sumInstall)}</td>
      </tr>
    `;
    let lastGrp = "";
    let subIdx = 1;
    QUOTE.install_items.forEach(it => {
      if (it.group_name !== lastGrp) {
        lastGrp = it.group_name;
        subIdx = 1;
        tableRows += `
          <tr class="sec-group">
            <td style="text-align:center;">${it.group_code}</td>
            <td colspan="${showImg ? 7 : 6}">${it.group_name.replace(/^[IVX]+\.\s*/, "")}</td>
          </tr>
        `;
      }
      const uPrice = getItemQuotedUnitPrice(it, false);
      const lTotal = uPrice * Number(it.qty || 0);
      tableRows += `
        <tr>
          <td style="text-align:center;">${subIdx++}</td>
          ${showImg ? `<td style="text-align:center;color:#64748B;font-size:11px;font-weight:700;">${it.cost_type === "labor" ? "NC" : "VT"}</td>` : ""}
          <td contenteditable="true">${it.name}</td>
          <td contenteditable="true" style="text-align:center;">${it.brand}</td>
          <td contenteditable="true" style="text-align:center;">${it.unit}</td>
          <td style="text-align:center;font-weight:700;">${formatNum(it.qty)}</td>
          <td style="text-align:right;">${formatNum(uPrice)}</td>
          <td style="text-align:right;font-weight:700;">${formatNum(lTotal)}</td>
        </tr>
      `;
    });
  }

  // Build Technical Appendix HTML — Placed IMMEDIATELY BELOW Totals & Amount-in-Words!
  let appendixHtml = "";
  const appRows = buildTechAppendixRows();
  if (appCfg.enabled && appRows.length > 0) {
    appendixHtml = `
      <div class="quote-appendix-section" id="quote-tech-appendix">
        <div class="quote-appendix-bar">
          <strong>📐 PHỤ LỤC THÔNG SỐ KỸ THUẬT THIẾT BỊ, ỐNG ĐỒNG & KÍCH THƯỚC CÔN ĐẦU MÁY</strong>
          <span class="no-print">(Bấm sửa trực tiếp nội dung hoặc bấm ✕ để cắt bớt dòng)</span>
        </div>

        <table class="quote-table" style="font-size:11.6px;margin-bottom:0;">
          <thead>
            <tr>
              <th style="width:36px;">STT</th>
              <th>Model & Thiết bị (SL)</th>
              <th>Công suất</th>
              ${appCfg.col_dim ? `<th>KT Máy (mm) & Nặng</th>` : ""}
              ${appCfg.col_pipe ? `<th>Ống Đồng & Nước Xả</th>` : ""}
              ${appCfg.col_duct ? `<th>KT Côn Cấp / Hồi & Hộp Gió</th>` : ""}
              ${appCfg.col_air ? `<th>Lưu Lượng Gió / Độ Ồn / Điện</th>` : ""}
              <th style="width:38px;" class="no-print">Cắt</th>
            </tr>
          </thead>
          <tbody>
            ${appRows.map((ar, idx) => `
              <tr>
                <td style="text-align:center;font-weight:700;">${idx + 1}</td>
                <td>
                  <div style="display:flex;align-items:center;gap:7px;">
                    ${ar.image ? `<img src="${ar.image}" style="width:42px;height:34px;object-fit:contain;background:#FFFFFF;border:1px solid #CBD5E1;border-radius:5px;padding:2px;flex-shrink:0;" />` : ""}
                    <div>
                      <strong contenteditable="true" style="color:#005A8D;">${ar.model}</strong> <span style="color:#991B1B;font-weight:700;">(×${ar.qty})</span>
                      <div contenteditable="true" style="color:#334155;font-size:11px;">${ar.name}</div>
                    </div>
                  </div>
                </td>
                <td contenteditable="true" onblur="updateAppendixCell('${ar.uid}',${ar.is_custom},'capacity',this.innerText)" style="font-weight:700;color:#991B1B;">${ar.capacity}</td>
                ${appCfg.col_dim ? `<td contenteditable="true" onblur="updateAppendixCell('${ar.uid}',${ar.is_custom},'dim_weight',this.innerText)">${ar.dim_weight}</td>` : ""}
                ${appCfg.col_pipe ? `<td contenteditable="true" onblur="updateAppendixCell('${ar.uid}',${ar.is_custom},'pipe_drain',this.innerText)" style="font-weight:600;">${ar.pipe_drain}</td>` : ""}
                ${appCfg.col_duct ? `<td contenteditable="true" onblur="updateAppendixCell('${ar.uid}',${ar.is_custom},'duct_plenum',this.innerText)" style="background:#F0F9FF;color:#0F172A;font-weight:700;">${ar.duct_plenum}</td>` : ""}
                ${appCfg.col_air ? `<td contenteditable="true" onblur="updateAppendixCell('${ar.uid}',${ar.is_custom},'air_power',this.innerText)">${ar.air_power}</td>` : ""}
                <td style="text-align:center;" class="no-print">
                  <button class="btn btn-sm btn-outline" title="Cắt dòng này khỏi báo giá" onclick="hideAppendixRow('${ar.uid}', ${ar.is_custom})">✕</button>
                </td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  }

  const terms = QUOTE.custom_terms || c.quote_terms || [];

  container.innerHTML = `
    <div class="quote-a4-paper" id="printable-quote">
      <!-- FORMAL WHITE CORPORATE LETTERHEAD (ONLY LOGO HAS YELLOW BACKGROUND) -->
      <div class="quote-hero-banner">
        <div class="quote-logo-card">
          <img src="assets/logo_minh_phu.png" alt="Minh Phú Logo" />
        </div>
        <div class="quote-comp-info">
          <h2 contenteditable="true">${c.name}</h2>
          <div class="comp-sub" contenteditable="true">
            <span>ĐẠI LÝ & NHÀ THẦU THI CÔNG HỆ THỐNG ĐHKK DAIKIN</span>
            <span style="color:#94A3B8;">•</span>
            <span style="color:#475569;font-style:italic;">"${c.slogan}"</span>
          </div>
          <div class="comp-meta" contenteditable="true">
            Địa chỉ: ${c.address}<br/>
            Hotline: <strong style="color:#991B1B;">${c.hotline}</strong> • MST: <strong style="color:#0F172A;">${c.tax_code}</strong> • Web: <strong style="color:#005A8D;">${c.website.replace("https://", "")}</strong>
          </div>
        </div>
        <div class="quote-doc-badge">
          <div class="doc-title">BÁO GIÁ DỰ ÁN</div>
          <div class="doc-no" contenteditable="true">Số: ${QUOTE.code}</div>
          <div class="doc-date" contenteditable="true">Ngày: ${QUOTE.date_str}</div>
        </div>
      </div>

      <div class="quote-body-inner">
        <!-- MINH PHÚ RED DOCUMENT TITLE BAR — 100% PURE WHITE TEXT -->
        <div class="quote-title-bar">
          <h3 contenteditable="true">${modeTitle}</h3>
        </div>
        <p class="no-print" style="text-align:center;font-size:11.8px;color:#64748B;margin:-10px 0 14px;">
          (Mọi ô chữ trên báo giá & bảng thông số kỹ thuật phía dưới đều có thể bấm sửa trực tiếp hoặc thêm/cắt trước khi xuất Excel & PDF)
        </p>

        <!-- CLIENT & PROJECT BOX -->
        <div class="quote-client-box">
          <div>
            <div><strong>Kính gửi (Chủ đầu tư):</strong> <span contenteditable="true">${QUOTE.client_name || "Quý Khách Hàng"}</span></div>
            <div style="margin-top:5px;"><strong>Công trình / Dự án:</strong> <span contenteditable="true">${QUOTE.project_name || "Hệ thống ĐHKK"}</span></div>
            <div style="margin-top:5px;"><strong>Địa điểm thi công:</strong> <span contenteditable="true">${QUOTE.project_addr || "—"}</span></div>
          </div>
          <div>
            <div><strong>Điện thoại KH:</strong> <span contenteditable="true">${QUOTE.client_phone || "—"}</span></div>
            <div style="margin-top:5px;"><strong>Phụ trách báo giá:</strong> <span contenteditable="true">${QUOTE.author}</span></div>
            <div style="margin-top:5px;"><strong>Hotline hỗ trợ 24/7:</strong> <strong style="color:#991B1B;">${c.hotline}</strong></div>
          </div>
        </div>

        <!-- QUOTATION TABLE -->
        <table class="quote-table">
          <thead>
            <tr>
              <th style="width:40px;">STT</th>
              ${showImg ? `<th style="width:64px;">Hình ảnh</th>` : ""}
              <th>Nội dung thiết bị / Quy cách kỹ thuật</th>
              <th style="width:92px;">Hãng / Xuất xứ</th>
              <th style="width:52px;">ĐVT</th>
              <th style="width:54px;">SL</th>
              <th style="width:102px;">Đơn giá (VNĐ)</th>
              <th style="width:116px;">Thành tiền (VNĐ)</th>
            </tr>
          </thead>
          <tbody>
            ${tableRows || `<tr><td colspan="8" style="text-align:center;padding:28px;">Chưa có dữ liệu báo giá</td></tr>`}
          </tbody>
        </table>

        <!-- TOTALS & AMOUNT IN WORDS -->
        <div class="quote-totals-card">
          ${includeEquip ? `<div class="tot-row"><span>Cộng Phần Thiết bị điều hòa (Phần A):</span><strong>${formatVND(t.sumEquip)}</strong></div>` : ""}
          ${includeInstall ? `<div class="tot-row"><span>Cộng Phần Vật tư & Nhân công lắp đặt (${includeEquip ? "Phần B" : "Phần A"}):</span><strong>${formatVND(t.sumInstall)}</strong></div>` : ""}
          <div class="tot-row"><span>Tổng cộng trước thuế:</span><strong>${formatVND(t.subTotal)}</strong></div>
          <div class="tot-row"><span>Thuế GTGT (VAT ${QUOTE.vat_rate}%):</span><strong>${formatVND(t.vatAmount)}</strong></div>
          <div class="tot-row grand"><span>TỔNG GIÁ TRỊ THANH TOÁN:</span><span>${formatVND(t.grandTotal)}</span></div>
        </div>

        <div style="margin-top:10px;padding:10px 14px;background:#F8FAFC;border:1px solid #CBD5E1;border-left:4px solid #991B1B;border-radius:6px;font-size:12.5px;color:#0F172A;">
          <strong style="color:#991B1B;">Số tiền bằng chữ:</strong> <em contenteditable="true" style="font-weight:700;">${docSoTienBangChu(t.grandTotal)}</em>
        </div>

        <!-- TECHNICAL SPECIFICATIONS & DUCT COLLAR APPENDIX IMMEDIATELY BELOW QUOTATION -->
        ${appendixHtml}

        <!-- TERMS & CLEAN WHITE VIETQR PAYMENT CARD -->
        <div class="quote-summary-qr-grid">
          <div style="font-size:12px;color:#334155;line-height:1.65;" contenteditable="true">
            <strong style="color:#991B1B;text-transform:uppercase;font-size:12.5px;">Điều khoản thương mại & Bảo hành:</strong><br/>
            ${terms.map(line => `${line}`).join("<br/>")}
          </div>

          <div>
            <div class="qr-payment-card">
              <div class="qr-card-head">QUÉT MÃ VIETQR THANH TOÁN ĐƠN HÀNG</div>
              <div class="qr-card-body">
                <div class="qr-img-box">
                  <img id="quote-qr-img" src="${qrUrl}" alt="VietQR Minh Phú" onerror="this.onerror=null;this.src='${qrFallback}';" />
                </div>
                <div class="qr-meta">
                  <h4>${b.bank_name || "Ngân hàng"}</h4>
                  <p>
                    STK: <strong style="font-size:13px;color:#991B1B;">${b.account_no}</strong><br/>
                    Chủ TK: <strong>${b.account_name}</strong><br/>
                    ${t.qrAmount > 0 ? `Tạm ứng (${QUOTE.qr_percent}%): <strong style="color:#005A8D;">${formatVND(t.qrAmount)}</strong><br/>` : ""}
                    ND: <strong>${qrNote}</strong>
                  </p>
                </div>
              </div>
            </div>

            <div style="margin-top:10px;padding:10px 12px;background:#F8FAFC;border:1px solid #CBD5E1;border-left:3.5px solid #005A8D;border-radius:8px;font-size:11.5px;color:#334155;text-align:center;">
              <strong style="color:#0F172A;">CAM KẾT CHẤT LƯỢNG MINH PHÚ</strong><br/>
              "${c.slogan}" — Đại lý & Nhà thầu ĐHKK Daikin chuẩn TCVN 5687:2024.
            </div>
          </div>
        </div>

        <!-- SIGNATURES -->
        <div class="quote-signatures">
          <div>
            <strong style="color:#0F172A;">XÁC NHẬN CỦA KHÁCH HÀNG / CHỦ ĐẦU TƯ</strong>
            <div style="font-size:11.5px;color:#64748B;margin-top:3px;">(Ký, ghi rõ họ tên)</div>
          </div>
          <div>
            <strong style="color:#991B1B;">ĐẠI DIỆN ${c.name}</strong>
            <div style="font-size:11.5px;color:#64748B;margin-top:3px;">(Ký tên, đóng dấu)</div>
            <div style="margin-top:58px;font-weight:700;color:#0F172A;">${c.representative}</div>
          </div>
        </div>
      </div>
    </div>
  `;
}

/* ---------------- BUILD EXPORT PAYLOAD & EXPORT EXCEL / PDF ---------------- */
function getQuoteExportPayload() {
  const totals = computeTotals();
  const includeEquip = (QUOTE.mode === "BOTH" || QUOTE.mode === "EQUIP_ONLY") && QUOTE.equip_items.length > 0;
  const includeInstall = (QUOTE.mode === "BOTH" || QUOTE.mode === "INSTALL_ONLY") && QUOTE.install_items.length > 0;

  const equipRows = includeEquip
    ? QUOTE.equip_items.map((it, idx) => {
        const uPrice = getItemQuotedUnitPrice(it, true);
        return {
          stt: idx + 1,
          model: it.model,
          name: it.name,
          spec_note: it.spec_note || "",
          origin: it.origin,
          unit: it.unit,
          qty: Number(it.qty) || 0,
          unit_price: uPrice,
          line_total: uPrice * (Number(it.qty) || 0),
          image: it.image || ""
        };
      })
    : [];

  const installRows = includeInstall
    ? QUOTE.install_items.map((it, idx) => {
        const uPrice = getItemQuotedUnitPrice(it, false);
        return {
          stt: idx + 1,
          group_code: it.group_code,
          group_name: it.group_name,
          name: it.name,
          brand: it.brand,
          cost_type: it.cost_type,
          unit: it.unit,
          qty: Number(it.qty) || 0,
          unit_price: uPrice,
          line_total: uPrice * (Number(it.qty) || 0)
        };
      })
    : [];

  const qrNote = `${DB.company.bank.note_prefix || "TT"} ${QUOTE.code}`;
  const showInlineSpec = document.getElementById("chk-show-duct-in-quote")
    ? document.getElementById("chk-show-duct-in-quote").checked
    : true;
  if (!showInlineSpec) {
    equipRows.forEach(r => { r.spec_note = ""; });
  }
  const appendixCfg = getAppendixConfig();
  const appendixRows = appendixCfg.enabled ? buildTechAppendixRows() : [];

  return {
    company: DB.company,
    quote: {
      code: QUOTE.code,
      date_str: QUOTE.date_str,
      client_name: QUOTE.client_name,
      project_name: QUOTE.project_name,
      project_addr: QUOTE.project_addr,
      client_phone: QUOTE.client_phone,
      author: QUOTE.author,
      mode: QUOTE.mode,
      show_images: document.getElementById("chk-show-img-in-quote") ? document.getElementById("chk-show-img-in-quote").checked : true,
      vat_rate: QUOTE.vat_rate,
      qr_percent: QUOTE.qr_percent,
      qr_note: qrNote,
      qr_url: getVietQrUrl(totals.qrAmount, qrNote),
      amount_in_words: docSoTienBangChu(totals.grandTotal)
    },
    totals,
    equip_rows: equipRows,
    install_rows: installRows,
    appendix_config: appendixCfg,
    appendix_rows: appendixRows
  };
}

async function exportToExcel() {
  const payload = getQuoteExportPayload();
  showToast("⏳ Đang khởi tạo file Báo giá Excel (.xlsx) chuẩn Minh Phú...");
  try {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.export_excel) {
      const res = await window.pywebview.api.export_excel(JSON.stringify(payload));
      if (res && res.ok) {
        showToast(`✅ Đã lưu file Excel: ${res.path}`);
        return;
      } else if (res && res.cancelled) {
        return;
      }
    }
    const resp = await fetch("/api/export_excel", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (resp.ok) {
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Bao_Gia_Minh_Phu_${QUOTE.code}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
      showToast("✅ Đã tải xuống file Báo giá Excel (.xlsx)!");
      return;
    }
  } catch (e) {}

  // Offline Browser / Android WebView direct Spreadsheet download fallback
  downloadOfflineExcelXml(payload);
}

async function exportToPDF() {
  const payload = getQuoteExportPayload();
  showToast("⏳ Đang kết xuất file Báo giá PDF (.pdf) chuẩn A4...");
  try {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.export_pdf) {
      const res = await window.pywebview.api.export_pdf(JSON.stringify(payload));
      if (res && res.ok) {
        showToast(`✅ Đã lưu file PDF: ${res.path}`);
        return;
      } else if (res && res.cancelled) {
        return;
      }
    }
    const resp = await fetch("/api/export_pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (resp.ok) {
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Bao_Gia_Minh_Phu_${QUOTE.code}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      showToast("✅ Đã tải xuống file Báo giá PDF (.pdf)!");
      return;
    }
  } catch (e) {}

  // Fallback to Android / iOS Native PrintManager or browser print-to-PDF
  if (window.AndroidNative && window.AndroidNative.printQuotePdf) {
    window.AndroidNative.printQuotePdf(`Bao_Gia_Minh_Phu_${QUOTE.code}`);
    return;
  }
  if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.iosNative) {
    window.webkit.messageHandlers.iosNative.postMessage({ action: "printPdf", jobName: `Bao_Gia_Minh_Phu_${QUOTE.code}` });
    return;
  }
  window.print();
}

function downloadOfflineExcelXml(payload) {
  // Clean UTF-8 Excel HTML/XML workbook fallback for pure offline Android WebView
  const c = payload.company;
  const q = payload.quote;
  const t = payload.totals;
  const html = `
    <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
    <head><meta charset="UTF-8"></head><body>
      <table border="1" style="border-collapse:collapse;font-family:Arial,sans-serif;font-size:11pt;">
        <tr><td colspan="7" style="background:#991B1B;color:#FFFFFF;font-weight:bold;font-size:14pt;">${c.name}</td></tr>
        <tr><td colspan="7">Địa chỉ: ${c.address} | Hotline: ${c.hotline} | MST: ${c.tax_code}</td></tr>
        <tr><td colspan="7" style="font-weight:bold;font-size:13pt;text-align:center;">BẢNG BÁO GIÁ HỆ THỐNG ĐIỀU HÒA KHÔNG KHÍ (${q.code})</td></tr>
        <tr><td colspan="4">Khách hàng: <b>${q.client_name}</b></td><td colspan="3">Ngày: ${q.date_str}</td></tr>
        <tr><td colspan="4">Dự án: <b>${q.project_name}</b></td><td colspan="3">Địa điểm: ${q.project_addr}</td></tr>
        <tr style="background:#0F172A;color:#FFFFFF;font-weight:bold;text-align:center;">
          <td>STT</td><td>Nội dung & Quy cách kỹ thuật</td><td>Xuất xứ</td><td>ĐVT</td><td>SL</td><td>Đơn giá</td><td>Thành tiền</td>
        </tr>
        ${payload.equip_rows.length ? `<tr style="background:#FEE2E2;font-weight:bold;"><td>A</td><td colspan="5">PHẦN THIẾT BỊ ĐIỀU HÒA DAIKIN</td><td>${t.sumEquip}</td></tr>` : ""}
        ${payload.equip_rows.map(r => `<tr><td>${r.stt}</td><td><b>${r.name} (Model: ${r.model})</b><br/>${r.spec_note}</td><td>${r.origin}</td><td>${r.unit}</td><td>${r.qty}</td><td>${r.unit_price}</td><td>${r.line_total}</td></tr>`).join("")}
        ${payload.install_rows.length ? `<tr style="background:#FEE2E2;font-weight:bold;"><td>B</td><td colspan="5">PHẦN VẬT TƯ & NHÂN CÔNG LẮP ĐẶT</td><td>${t.sumInstall}</td></tr>` : ""}
        ${payload.install_rows.map(r => `<tr><td>${r.stt}</td><td>${r.name}</td><td>${r.brand}</td><td>${r.unit}</td><td>${r.qty}</td><td>${r.unit_price}</td><td>${r.line_total}</td></tr>`).join("")}
        <tr><td colspan="6" style="text-align:right;font-weight:bold;">Cộng trước thuế:</td><td style="font-weight:bold;">${t.subTotal}</td></tr>
        <tr><td colspan="6" style="text-align:right;font-weight:bold;">Thuế VAT (${q.vat_rate}%):</td><td style="font-weight:bold;">${t.vatAmount}</td></tr>
        <tr style="background:#991B1B;color:#FFFFFF;font-weight:bold;"><td colspan="6" style="text-align:right;">TỔNG CỘNG THANH TOÁN:</td><td>${t.grandTotal}</td></tr>
        <tr><td colspan="7"><i>Bằng chữ: ${q.amount_in_words}</i></td></tr>
        <tr><td colspan="7"><b>Thanh toán chuyển khoản:</b> ${c.bank.bank_name} - STK: ${c.bank.account_no} - Chủ TK: ${c.bank.account_name}</td></tr>
      </table>
    </body></html>`;
  const blob = new Blob(["\ufeff", html], { type: "application/vnd.ms-excel;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `Bao_Gia_Minh_Phu_${q.code}.xls`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("✅ Đã xuất file Báo giá Excel thành công!");
}
