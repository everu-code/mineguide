/* ============================================================
   Crafting Guide page logic
   ============================================================ */

const TAGS = ["Most Used", "Essential", "Tools", "Combat", "Redstone", "Blocks", "Food", "Transport"];

let activeTag = "All";
let searchTerm = "";
let showFavsOnly = false;

const grid = document.getElementById("itemGrid");
const searchInput = document.getElementById("search");
const tagRow = document.getElementById("tagRow");
const resultCount = document.getElementById("resultCount");

/* ---------- Build tag filter row ---------- */
function buildTags() {
  const entries = [
    { val: "All", label: t("tag_all") },
    ...TAGS.map(tag => ({ val: tag, label: t("cat_" + tag) })),
    { val: "__fav", label: t("tag_fav") }
  ];
  tagRow.innerHTML = entries.map(e =>
    `<div class="tag${e.val === "All" ? " active" : ""}" data-tag="${e.val}">${e.label}</div>`
  ).join("");
  tagRow.querySelectorAll(".tag").forEach(el => {
    el.addEventListener("click", () => {
      tagRow.querySelectorAll(".tag").forEach(x => x.classList.remove("active"));
      el.classList.add("active");
      const v = el.dataset.tag;
      if (v === "__fav") { showFavsOnly = true; activeTag = "All"; }
      else { showFavsOnly = false; activeTag = v; }
      render();
    });
  });
}

/* ---------- Filtering ---------- */
function filtered() {
  const q = searchTerm.trim().toLowerCase();
  return ITEMS.filter(it => {
    if (showFavsOnly && !Store.isFav(it.id)) return false;
    if (activeTag !== "All" && !(it.category || []).includes(activeTag)) return false;
    if (q) {
      const hay = (it.name + " " + (it.name_fr || "") + " " + it.id).toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
}

/* ---------- Render grid ---------- */
function render() {
  const list = filtered();
  resultCount.textContent = t("result_count", list.length);

  if (!list.length) {
    grid.innerHTML = `<div class="empty-state">
      <div class="big">🔍</div>
      <div>${t("empty_title")}</div>
    </div>`;
    return;
  }

  grid.innerHTML = list.map(it => {
    const type = it.recipe && it.recipe.type;
    const sub = type === "furnace" ? t("sub_smelted") : (type === "gathered" ? t("sub_gathered") : t("sub_craftable"));
    return `
      <div class="item-card" data-id="${it.id}">
        <button class="fav-star ${Store.isFav(it.id) ? "on" : ""}" data-fav="${it.id}"
                title="Favorite">${Store.isFav(it.id) ? "★" : "☆"}</button>
        <div class="item-icon">${iconHTML(it)}</div>
        <div class="item-name">${getName(it)}</div>
        <div class="item-sub">${sub}</div>
      </div>`;
  }).join("");

  grid.querySelectorAll(".item-card").forEach(card => {
    card.addEventListener("click", e => {
      if (e.target.closest("[data-fav]")) return;
      openModal(card.dataset.id);
    });
  });
  grid.querySelectorAll("[data-fav]").forEach(btn => {
    btn.addEventListener("click", e => {
      e.stopPropagation();
      const on = Store.toggleFav(btn.dataset.fav);
      btn.classList.toggle("on", on);
      btn.textContent = on ? "★" : "☆";
      toast(on ? t("fav_added") : t("fav_removed"), on ? "⭐" : "☆");
      if (showFavsOnly) render();
    });
  });
}

/* ---------- Modal ---------- */
const backdrop = document.getElementById("modalBackdrop");
const modal = document.getElementById("modal");

function craftGridHTML(item) {
  const r = item.recipe;
  if (!r || r.type === "gathered") {
    return `<div class="recipe-note">🌍 <span class="recipe-type-badge">${t("recipe_gathered")}</span>
             — ${t("recipe_gathered_note")}</div>`;
  }
  if (r.type === "furnace") {
    const ingId = Object.keys(r.ingredients)[0];
    const ing = getItem(ingId);
    return `
      <div class="craft-layout">
        <div class="craft-grid" style="grid-template-columns:repeat(1,56px);grid-template-rows:repeat(2,56px)">
          <div class="craft-cell clickable" data-jump="${ing.recipe && ing.recipe.type !== "gathered" ? ingId : ""}" title="${getName(ing)}">${iconHTML(ing)}</div>
          <div class="craft-cell empty" title="${t("fuel")}">🔥</div>
        </div>
        <div class="craft-arrow">➜</div>
        <div class="craft-result" title="${getName(item)}">${iconHTML(item)}
          ${r.yields > 1 ? `<span class="qty">${r.yields}</span>` : ""}</div>
      </div>
      <div class="recipe-note">🔥 <span class="recipe-type-badge">${t("recipe_furnace")}</span> — ${t("recipe_furnace_note", getName(ing))}</div>`;
  }

  // crafting table (shaped/shapeless) 3x3
  const cells = [];
  for (let row = 0; row < 3; row++) {
    for (let col = 0; col < 3; col++) {
      const id = (r.grid[row] && r.grid[row][col]) || null;
      if (!id) { cells.push(`<div class="craft-cell empty"></div>`); continue; }
      const ci = getItem(id);
      const clickable = ci.recipe && ci.recipe.type !== "gathered";
      cells.push(`<div class="craft-cell ${clickable ? "clickable" : ""}"
        data-jump="${clickable ? id : ""}" title="${getName(ci)}">${iconHTML(ci)}</div>`);
    }
  }
  return `
    <div class="craft-layout">
      <div class="craft-grid">${cells.join("")}</div>
      <div class="craft-arrow">➜</div>
      <div class="craft-result" title="${getName(item)}">${iconHTML(item)}
        ${r.yields > 1 ? `<span class="qty">${r.yields}</span>` : ""}</div>
    </div>
    <div class="recipe-note">
      ${r.type === "shapeless" ? "🎲" : "🧱"}
      <span class="recipe-type-badge">${r.type === "shapeless" ? t("recipe_shapeless") : t("recipe_table")}</span>
      — ${t("makes_per", r.yields)}
    </div>`;
}

function matListHTML(item) {
  const ing = (item.recipe && item.recipe.ingredients) || {};
  const keys = Object.keys(ing);
  if (!keys.length) return "";
  return `
    <div class="mats-title">${t("required_materials")}</div>
    <div class="mat-list">
      ${keys.map(id => {
        const mi = getItem(id);
        return `<div class="mat-row">
          <div class="ic">${iconHTML(mi)}</div>
          <div class="nm">${getName(mi)}</div>
          <div class="ct">×${ing[id]}</div>
        </div>`;
      }).join("")}
    </div>`;
}

function openModal(id) {
  const item = getItem(id);
  const cats = (item.category || []);
  modal.innerHTML = `
    <div class="modal-head">
      <div class="item-icon">${iconHTML(item)}</div>
      <div>
        <h2>${getName(item)}</h2>
        <div class="cats">${cats.map(c => `<span class="mini-tag">${t("cat_" + c)}</span>`).join("")}
          <span class="mini-tag">${t("stacks_to", item.stackSize || 64)}</span></div>
      </div>
      <button class="close-btn" id="closeModal">✕</button>
    </div>
    <div class="modal-body">
      <p class="desc">${getDesc(item)}</p>
      ${craftGridHTML(item)}
      ${matListHTML(item)}
      <div class="modal-actions">
        <button class="btn primary" id="favBtn">
          ${Store.isFav(id) ? t("faved") : t("add_fav")}</button>
      </div>
    </div>`;

  backdrop.classList.add("open");
  document.body.style.overflow = "hidden";

  document.getElementById("closeModal").onclick = closeModal;
  document.getElementById("favBtn").onclick = () => {
    const on = Store.toggleFav(id);
    document.getElementById("favBtn").textContent = on ? t("faved") : t("add_fav");
    toast(on ? t("fav_added") : t("fav_removed"), on ? "⭐" : "☆");
    render();
  };
  // jump to ingredient recipes
  modal.querySelectorAll("[data-jump]").forEach(c => {
    if (!c.dataset.jump) return;
    c.addEventListener("click", () => openModal(c.dataset.jump));
  });
}

function closeModal() {
  backdrop.classList.remove("open");
  document.body.style.overflow = "";
}
backdrop.addEventListener("click", e => { if (e.target === backdrop) closeModal(); });
document.addEventListener("keydown", e => { if (e.key === "Escape") closeModal(); });

/* ---------- Search ---------- */
searchInput.addEventListener("input", () => {
  searchTerm = searchInput.value;
  document.getElementById("clearSearch").style.display = searchTerm ? "block" : "none";
  render();
});
document.getElementById("clearSearch").addEventListener("click", () => {
  searchInput.value = ""; searchTerm = "";
  document.getElementById("clearSearch").style.display = "none";
  render(); searchInput.focus();
});

/* ---------- Deep link (?item=id) ---------- */
function checkDeepLink() {
  const params = new URLSearchParams(location.search);
  const id = params.get("item");
  if (id && ITEM_BY_ID[id]) openModal(id);
}

/* ---------- Init ---------- */
buildTags();
render();
checkDeepLink();
const totalEl = document.getElementById("totalCount");
if (totalEl) totalEl.textContent = t("total_count", ITEMS.length);
