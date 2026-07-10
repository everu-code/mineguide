/* ============================================================
   Building Guide — bilingual, farm-style cards + category filters
   Reuses the farm-card layout, checklist, multiplier & progress.
   ============================================================ */

const BUILDINGS = window.BUILDINGS || [];
const buildGrid = document.getElementById("buildGrid");
const bTagRow = document.getElementById("buildTagRow");
const bCount = document.getElementById("buildCount");

const BCATS = ["living", "farmstead", "utility", "passage", "relax"];
let activeBCat = "All";

function bSearchURL(b) {
  const q = (b.name.en || tr(b.name)) + " minecraft build tutorial 1.21";
  return "https://www.youtube.com/results?search_query=" + encodeURIComponent(q);
}

function bProgress(b) {
  const checks = Store.getChecks(b.id);
  const total = b.materials.length;
  const done = checks.filter(i => i < total).length;
  return { done, total, pct: total ? Math.round((done / total) * 100) : 0 };
}

function buildingCardHTML(b) {
  const mult = Store.getMult(b.id);
  const checks = Store.getChecks(b.id);
  const prog = bProgress(b);

  const matRows = b.materials.map((m, idx) => {
    const it = getItem(m.item);
    const done = checks.includes(idx);
    return `<div class="check-row ${done ? "done" : ""}" data-check="${idx}">
      <div class="check-box">${done ? "✔" : ""}</div>
      <div class="cr-ic">${iconHTML(it)}</div>
      <div class="cr-name">${getName(it)}</div>
      <div class="cr-qty">×${m.qty * mult}</div>
    </div>`;
  }).join("");

  const steps = tr(b.steps).map(s => `<div class="step-item">${s}</div>`).join("");
  const tips = tr(b.tips).map(t2 => `<li>${t2}</li>`).join("");

  return `
  <div class="farm-card" data-build="${b.id}">
    <div class="fc-thumb-wrap noimg bcat-${b.category}" data-bsearch title="${tr(b.name)}">
      <div class="fc-thumb-fallback">${b.emoji}</div>
      <div class="fc-thumb-play">▶</div>
      <span class="pill diff ${b.difficulty} fc-thumb-diff">${t("diff_" + b.difficulty)}</span>
      <span class="pill fc-thumb-cat">${t("bcat_" + b.category)}</span>
    </div>
    <div class="fc-head">
      <div class="fc-emoji">${b.emoji}</div>
      <div style="flex:1">
        <h3>${tr(b.name)}</h3>
        <div class="fc-tags">
          ${b.tags.map(tg => `<span class="pill">${tg}</span>`).join("")}
        </div>
      </div>
    </div>
    <div class="fc-body">
      <p class="fc-desc">${tr(b.description)}</p>

      <div class="fc-metrics">
        <div class="metric"><div class="lbl">${t("build_style")}</div><div class="val">${tr(b.style)}</div></div>
        <div class="metric"><div class="lbl">${t("build_size")}</div><div class="val">${tr(b.size)}</div></div>
      </div>

      <button class="video-btn" data-bsearch>${b.videoId ? "▶" : "🔎"} ${t("watch_builds")}</button>

      <div class="section-label" style="margin-top:20px">⚙️ ${t("build_multiplier")}</div>
      <div class="mult-row">
        <label>${t("modules_to_build")}</label>
        <div class="stepper">
          <button data-mult-dn>−</button>
          <input type="number" min="1" value="${mult}" data-mult-input>
          <button data-mult-up>+</button>
        </div>
        <span style="font-size:.78rem;color:var(--text-faint)">${t("scales_auto")}</span>
      </div>

      <div class="prog-wrap">
        <div class="prog-top"><span>${t("collection_progress")}</span><span data-prog-txt>${prog.done}/${prog.total}</span></div>
        <div class="prog-bar"><div class="prog-fill" style="width:${prog.pct}%"></div></div>
      </div>

      <div class="section-label">📦 ${t("materials")}
        <button class="btn ghost sm" style="margin-left:auto" data-reset-checks>${t("reset")}</button>
      </div>
      <div class="checklist" data-checklist>${matRows}</div>

      <div class="collapse" data-collapse>
        <div class="section-label collapse-head" data-collapse-toggle>
          🧭 ${t("blueprint")} <span class="chev">▶</span>
        </div>
        <div class="collapse-body">
          <div class="steps-list" style="margin-bottom:16px">${steps}</div>
          <div class="section-label" style="margin-top:0">${t("pro_tips")}</div>
          <ul class="tips-list">${tips}</ul>
        </div>
      </div>
    </div>
  </div>`;
}

function filteredBuilds() {
  return activeBCat === "All" ? BUILDINGS : BUILDINGS.filter(b => b.category === activeBCat);
}

function renderBuildings() {
  const list = filteredBuilds();
  if (bCount) bCount.textContent = t("builds_count", list.length);
  buildGrid.innerHTML = list.map(buildingCardHTML).join("");
  list.forEach(wireBuildingCard);
}

function buildBTags() {
  const entries = [{ val: "All", label: t("builds_all") },
    ...BCATS.map(c => ({ val: c, label: t("bcat_" + c) }))];
  bTagRow.innerHTML = entries.map(e =>
    `<div class="tag${e.val === "All" ? " active" : ""}" data-bcat="${e.val}">${e.label}</div>`).join("");
  bTagRow.querySelectorAll(".tag").forEach(el => {
    el.addEventListener("click", () => {
      bTagRow.querySelectorAll(".tag").forEach(x => x.classList.remove("active"));
      el.classList.add("active");
      activeBCat = el.dataset.bcat;
      renderBuildings();
    });
  });
}

function wireBuildingCard(b) {
  const card = buildGrid.querySelector(`[data-build="${b.id}"]`);
  if (!card) return;
  const input = card.querySelector("[data-mult-input]");

  const refreshQtys = () => {
    const mult = Store.getMult(b.id);
    input.value = mult;
    card.querySelectorAll("[data-check]").forEach(row => {
      const idx = +row.dataset.check;
      row.querySelector(".cr-qty").textContent = "×" + (b.materials[idx].qty * mult);
    });
  };
  const refreshProgress = () => {
    const prog = bProgress(b);
    card.querySelector("[data-prog-txt]").textContent = `${prog.done}/${prog.total}`;
    card.querySelector(".prog-fill").style.width = prog.pct + "%";
  };

  card.querySelector("[data-mult-up]").onclick = () => { Store.setMult(b.id, Store.getMult(b.id) + 1); refreshQtys(); };
  card.querySelector("[data-mult-dn]").onclick = () => { Store.setMult(b.id, Store.getMult(b.id) - 1); refreshQtys(); };
  input.onchange = () => { Store.setMult(b.id, parseInt(input.value) || 1); refreshQtys(); };

  card.querySelectorAll("[data-check]").forEach(row => {
    row.addEventListener("click", () => {
      const idx = +row.dataset.check;
      Store.toggleCheck(b.id, idx);
      const done = Store.getChecks(b.id).includes(idx);
      row.classList.toggle("done", done);
      row.querySelector(".check-box").textContent = done ? "✔" : "";
      refreshProgress();
    });
  });
  card.querySelector("[data-reset-checks]").onclick = e => {
    e.stopPropagation();
    Store.clearChecks(b.id);
    card.querySelectorAll("[data-check]").forEach(r => { r.classList.remove("done"); r.querySelector(".check-box").textContent = ""; });
    refreshProgress();
    toast(t("checklist_reset"), "🔄");
  };

  const collapse = card.querySelector("[data-collapse]");
  card.querySelector("[data-collapse-toggle]").onclick = () => collapse.classList.toggle("open");

  card.querySelectorAll("[data-bsearch]").forEach(el =>
    el.addEventListener("click", () => {
      if (b.videoId) openBuildVideo(b);
      else window.open(bSearchURL(b), "_blank", "noopener");
    }));
}

/* ---------- Video modal ---------- */
const backdrop = document.getElementById("modalBackdrop");
const modal = document.getElementById("modal");

function openBuildVideo(b) {
  modal.innerHTML = `
    <div class="modal-head">
      <div class="fc-emoji" style="width:52px;height:52px">${b.emoji}</div>
      <div><h2>${tr(b.name)}</h2>
        <div class="cats"><span class="mini-tag">${t("bcat_" + b.category)}</span>
          <span class="mini-tag">${tr(b.style)}</span></div></div>
      <button class="close-btn" id="closeModal">✕</button>
    </div>
    <div class="modal-body">
      <div class="video-embed">
        <iframe src="https://www.youtube-nocookie.com/embed/${b.videoId}"
          title="${tr(b.name)}"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen></iframe>
      </div>
      <div class="modal-actions">
        <a class="btn primary" href="https://www.youtube.com/watch?v=${b.videoId}" target="_blank" rel="noopener">${t("open_youtube")}</a>
        <a class="btn" href="${bSearchURL(b)}" target="_blank" rel="noopener">${t("more_tutorials")}</a>
      </div>
    </div>`;
  backdrop.classList.add("open");
  document.body.style.overflow = "hidden";
  document.getElementById("closeModal").onclick = closeBuildVideo;
}
function closeBuildVideo() {
  modal.innerHTML = "";
  backdrop.classList.remove("open");
  document.body.style.overflow = "";
}
backdrop.addEventListener("click", e => { if (e.target === backdrop) closeBuildVideo(); });
document.addEventListener("keydown", e => { if (e.key === "Escape") closeBuildVideo(); });

/* ---------- Init ---------- */
buildBTags();
renderBuildings();
