/* ============================================================
   Farm Builder & Tracker — bilingual, with real video thumbnails
   ============================================================ */

const farmGrid = document.getElementById("farmGrid");

function progressFor(farm) {
  const checks = Store.getChecks(farm.id);
  const total = farm.materials.length;
  const done = checks.filter(i => i < total).length;
  return { done, total, pct: total ? Math.round((done / total) * 100) : 0 };
}

function searchURL(farm) {
  const q = (farm.name.en || tr(farm.name)) + " minecraft 26.2 tutorial";
  return "https://www.youtube.com/results?search_query=" + encodeURIComponent(q);
}
function thumbURL(farm) { return `https://img.youtube.com/vi/${farm.videoId}/hqdefault.jpg`; }

function farmCardHTML(farm) {
  const mult = Store.getMult(farm.id);
  const checks = Store.getChecks(farm.id);
  const prog = progressFor(farm);

  const matRows = farm.materials.map((m, idx) => {
    const it = getItem(m.item);
    const done = checks.includes(idx);
    return `<div class="check-row ${done ? "done" : ""}" data-check="${idx}">
      <div class="check-box">${done ? "✔" : ""}</div>
      <div class="cr-ic">${iconHTML(it)}</div>
      <div class="cr-name">${getName(it)}</div>
      <div class="cr-qty">×${m.qty * mult}</div>
    </div>`;
  }).join("");

  const steps = tr(farm.steps).map(s => `<div class="step-item">${s}</div>`).join("");
  const tips = tr(farm.tips).map(t2 => `<li>${t2}</li>`).join("");

  return `
  <div class="farm-card" data-farm="${farm.id}">
    <div class="fc-thumb-wrap" data-video title="${tr(farm.videoTitle)}">
      <img class="fc-thumb" src="${thumbURL(farm)}" alt="${tr(farm.name)}" loading="lazy"
           onerror="this.closest('.fc-thumb-wrap').classList.add('noimg')">
      <div class="fc-thumb-fallback">${farm.emoji}</div>
      <div class="fc-thumb-play">▶</div>
      <span class="pill diff ${farm.difficulty} fc-thumb-diff">${t("diff_" + farm.difficulty)}</span>
    </div>
    <div class="fc-head">
      <div class="fc-emoji">${farm.emoji}</div>
      <div style="flex:1">
        <h3>${tr(farm.name)}</h3>
        <div class="fc-tags">
          ${farm.tags.map(tg => `<span class="pill">${ftag(tg)}</span>`).join("")}
        </div>
      </div>
    </div>
    <div class="fc-body">
      <p class="fc-desc">${tr(farm.description)}</p>

      <div class="fc-metrics">
        <div class="metric"><div class="lbl">${t("efficiency")}</div><div class="val">${tr(farm.efficiency)}</div></div>
        <div class="metric"><div class="lbl">${t("footprint")}</div><div class="val">${tr(farm.dimensions)}</div></div>
      </div>

      <button class="video-btn" data-video>▶ ${t("watch")} ${tr(farm.videoTitle)}</button>

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

function renderFarms() {
  farmGrid.innerHTML = FARMS.map(farmCardHTML).join("");
  FARMS.forEach(wireFarmCard);
}

function wireFarmCard(farm) {
  const card = farmGrid.querySelector(`[data-farm="${farm.id}"]`);
  if (!card) return;

  const input = card.querySelector("[data-mult-input]");

  const refreshQtys = () => {
    const mult = Store.getMult(farm.id);
    input.value = mult;
    card.querySelectorAll("[data-check]").forEach(row => {
      const idx = +row.dataset.check;
      row.querySelector(".cr-qty").textContent = "×" + (farm.materials[idx].qty * mult);
    });
  };
  const refreshProgress = () => {
    const prog = progressFor(farm);
    card.querySelector("[data-prog-txt]").textContent = `${prog.done}/${prog.total}`;
    card.querySelector(".prog-fill").style.width = prog.pct + "%";
  };

  card.querySelector("[data-mult-up]").onclick = () => { Store.setMult(farm.id, Store.getMult(farm.id) + 1); refreshQtys(); };
  card.querySelector("[data-mult-dn]").onclick = () => { Store.setMult(farm.id, Store.getMult(farm.id) - 1); refreshQtys(); };
  input.onchange = () => { Store.setMult(farm.id, parseInt(input.value) || 1); refreshQtys(); };

  card.querySelectorAll("[data-check]").forEach(row => {
    row.addEventListener("click", () => {
      const idx = +row.dataset.check;
      Store.toggleCheck(farm.id, idx);
      const done = Store.getChecks(farm.id).includes(idx);
      row.classList.toggle("done", done);
      row.querySelector(".check-box").textContent = done ? "✔" : "";
      refreshProgress();
    });
  });
  card.querySelector("[data-reset-checks]").onclick = e => {
    e.stopPropagation();
    Store.clearChecks(farm.id);
    card.querySelectorAll("[data-check]").forEach(r => { r.classList.remove("done"); r.querySelector(".check-box").textContent = ""; });
    refreshProgress();
    toast(t("checklist_reset"), "🔄");
  };

  const collapse = card.querySelector("[data-collapse]");
  card.querySelector("[data-collapse-toggle]").onclick = () => collapse.classList.toggle("open");

  card.querySelectorAll("[data-video]").forEach(el => el.addEventListener("click", () => openVideo(farm)));
}

/* ---------- Video modal ---------- */
const backdrop = document.getElementById("modalBackdrop");
const modal = document.getElementById("modal");

function openVideo(farm) {
  modal.innerHTML = `
    <div class="modal-head">
      <div class="fc-emoji" style="width:52px;height:52px">${farm.emoji}</div>
      <div><h2>${tr(farm.name)}</h2>
        <div class="cats"><span class="mini-tag">${tr(farm.videoTitle)}</span></div></div>
      <button class="close-btn" id="closeModal">✕</button>
    </div>
    <div class="modal-body">
      <div class="video-embed">
        <iframe src="https://www.youtube-nocookie.com/embed/${farm.videoId}"
          title="${tr(farm.videoTitle)}"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen></iframe>
      </div>
      <div class="modal-actions">
        <a class="btn primary" href="https://www.youtube.com/watch?v=${farm.videoId}" target="_blank" rel="noopener">${t("open_youtube")}</a>
        <a class="btn" href="${searchURL(farm)}" target="_blank" rel="noopener">${t("more_tutorials")}</a>
      </div>
    </div>`;
  backdrop.classList.add("open");
  document.body.style.overflow = "hidden";
  document.getElementById("closeModal").onclick = closeVideo;
}
function closeVideo() {
  modal.innerHTML = "";
  backdrop.classList.remove("open");
  document.body.style.overflow = "";
}
backdrop.addEventListener("click", e => { if (e.target === backdrop) closeVideo(); });
document.addEventListener("keydown", e => { if (e.key === "Escape") closeVideo(); });

/* ---------- Init ---------- */
renderFarms();
