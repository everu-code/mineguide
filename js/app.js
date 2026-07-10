/* ============================================================
   Shared app core: data access, storage, icons, toast, nav
   Data is loaded from data/items.js & data/farms.js
   (window.ITEMS / window.FARMS) so the app runs on file://.
   ============================================================ */

const ITEMS = window.ITEMS || [];
const FARMS = window.FARMS || [];

/* Fast lookup maps */
const ITEM_BY_ID = Object.fromEntries(ITEMS.map(i => [i.id, i]));
const FARM_BY_ID = Object.fromEntries(FARMS.map(f => [f.id, f]));

/* ---------- Item helpers ---------- */
function getItem(id) {
  return ITEM_BY_ID[id] || {
    id, name: prettify(id), emoji: "❔", category: [], recipe: { type: "gathered", grid: [], ingredients: {} }
  };
}
function prettify(id) {
  return String(id).split("_").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
}

/* Renders an item icon: real PNG if available (icons/<id>.png from the
   scraper), otherwise the emoji fallback. */
function iconHTML(item, cls = "") {
  if (!item) return "";
  if (item.icon) {
    return `<img class="${cls}" src="${item.icon}" alt="${item.name}"
              onerror="this.replaceWith(document.createTextNode('${item.emoji || "❔"}'))">`;
  }
  return `<span class="${cls}">${item.emoji || "❔"}</span>`;
}

/* ---------- localStorage store ---------- */
const Store = {
  KEY: "mcguide.v1",
  data: null,
  _defaults() {
    return {
      favorites: [],          // item ids
      farmChecks: {},         // { farmId: [checkedIndexes] }
      farmMultipliers: {}     // { farmId: number }
    };
  },
  load() {
    if (this.data) return this.data;
    try {
      const raw = localStorage.getItem(this.KEY);
      this.data = raw ? Object.assign(this._defaults(), JSON.parse(raw)) : this._defaults();
    } catch (e) {
      this.data = this._defaults();
    }
    return this.data;
  },
  save() {
    try { localStorage.setItem(this.KEY, JSON.stringify(this.data)); } catch (e) {}
  },

  /* favorites */
  isFav(id) { return this.load().favorites.includes(id); },
  toggleFav(id) {
    const d = this.load();
    const i = d.favorites.indexOf(id);
    if (i >= 0) d.favorites.splice(i, 1); else d.favorites.push(id);
    this.save();
    return this.isFav(id);
  },

  /* farm checklist */
  getChecks(farmId) { return this.load().farmChecks[farmId] || []; },
  toggleCheck(farmId, idx) {
    const d = this.load();
    const arr = d.farmChecks[farmId] || (d.farmChecks[farmId] = []);
    const p = arr.indexOf(idx);
    if (p >= 0) arr.splice(p, 1); else arr.push(idx);
    this.save();
  },
  clearChecks(farmId) { const d = this.load(); d.farmChecks[farmId] = []; this.save(); },

  /* farm multiplier */
  getMult(farmId) { return this.load().farmMultipliers[farmId] || 1; },
  setMult(farmId, n) { const d = this.load(); d.farmMultipliers[farmId] = Math.max(1, n | 0); this.save(); }
};

/* ---------- Toast ---------- */
let _toastTimer = null;
function toast(msg, emoji = "✅") {
  let el = document.querySelector(".toast");
  if (!el) {
    el = document.createElement("div");
    el.className = "toast";
    document.body.appendChild(el);
  }
  el.innerHTML = `<span>${emoji}</span><span>${msg}</span>`;
  el.classList.add("show");
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => el.classList.remove("show"), 2200);
}

