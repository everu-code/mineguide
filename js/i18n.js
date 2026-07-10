/* ============================================================
   Internationalisation — French primary, English toggle.
   Loaded before app/crafting/farms so getName()/t() are ready.
   ============================================================ */

let LANG = (function () {
  try { return localStorage.getItem("mcguide.lang") || "fr"; } catch (e) { return "fr"; }
})();

const STRINGS = {
  fr: {
    page_title_craft: "Guide de fabrication interactif",
    page_title_farms: "Constructeur & suivi de fermes",
    brand_sub: "MineGuide",
    nav_crafting: "Fabrication",
    nav_farms: "Fermes",
    search_placeholder: "Rechercher un objet… (pioche, redstone, trémie)",
    result_count: n => `${n} objet${n > 1 ? "s" : ""}`,
    total_count: n => `${n} objets & recettes`,
    empty_title: "Aucun objet ne correspond à vos filtres.",
    tag_all: "Tout",
    tag_fav: "★ Favoris",
    sub_craftable: "Fabricable",
    sub_smelted: "Fonderie",
    sub_gathered: "Récolté",
    stacks_to: n => `Se cumule à ${n}`,
    required_materials: "Matériaux nécessaires",
    add_fav: "☆ Ajouter aux favoris",
    faved: "★ Favori",
    fav_added: "Ajouté aux favoris",
    fav_removed: "Retiré des favoris",
    recipe_gathered: "Obtenu dans le monde",
    recipe_gathered_note: "cet objet se récupère ou se mine — il ne se fabrique pas.",
    recipe_furnace: "Fourneau",
    recipe_furnace_note: fuel => `faire fondre ${fuel} avec n'importe quel combustible.`,
    recipe_table: "Établi",
    recipe_shapeless: "Sans forme",
    makes_per: n => `donne ${n} par fabrication.`,
    fuel: "Combustible",
    /* farms */
    difficulty: "Difficulté",
    diff_Easy: "Facile", diff_Medium: "Moyen", diff_Hard: "Difficile",
    efficiency: "Rendement", footprint: "Emprise",
    build_multiplier: "Multiplicateur de construction",
    modules_to_build: "Modules à construire :",
    scales_auto: "les matériaux s'ajustent automatiquement",
    collection_progress: "Progression de la collecte",
    materials: "Matériaux", reset: "Réinitialiser",
    blueprint: "Plan étape par étape", pro_tips: "Astuces de pro",
    watch: "Voir le tuto :", open_youtube: "↗ Ouvrir sur YouTube",
    more_tutorials: "🔎 Plus de tutoriels 26.2",
    checklist_reset: "Liste réinitialisée",
    made_by: "Made by ever",
    /* category tags */
    cat_all: "Tout",
    "cat_Most Used": "Populaires", cat_Essential: "Essentiels", cat_Tools: "Outils",
    cat_Combat: "Combat", cat_Redstone: "Redstone", cat_Blocks: "Blocs",
    cat_Food: "Nourriture", cat_Transport: "Transport", cat_Decoration: "Décoration",
    cat_Nether: "Nether", cat_End: "End",
    /* farm tags */
    ftag_Resource: "Ressources", ftag_XP: "XP", ftag_AFK: "AFK", ftag_Nether: "Nether",
    ftag_End: "End", ftag_Villager: "Villageois", ftag_Combat: "Combat",
    ftag_Emeralds: "Émeraudes", ftag_Food: "Nourriture", ftag_Automatic: "Automatique",
    ftag_Fuel: "Combustible", ftag_Gunpowder: "Poudre", ftag_Copper: "Cuivre",
    ftag_Totems: "Totems", ftag_Ocean: "Océan", ftag_Paper: "Papier", ftag_Building: "Construction"
  },
  en: {
    page_title_craft: "Interactive Crafting Guide",
    page_title_farms: "Farm Builder & Tracker",
    brand_sub: "MineGuide",
    nav_crafting: "Crafting",
    nav_farms: "Farms",
    search_placeholder: "Search items… (pickaxe, redstone, hopper)",
    result_count: n => `${n} item${n > 1 ? "s" : ""}`,
    total_count: n => `${n} crafts & items`,
    empty_title: "No items match your filters.",
    tag_all: "All",
    tag_fav: "★ Favorites",
    sub_craftable: "Craftable",
    sub_smelted: "Smelted",
    sub_gathered: "Gathered",
    stacks_to: n => `Stacks to ${n}`,
    required_materials: "Required materials",
    add_fav: "☆ Add to favorites",
    faved: "★ Favorited",
    fav_added: "Added to favorites",
    fav_removed: "Removed from favorites",
    recipe_gathered: "Gathered / mined",
    recipe_gathered_note: "this item is obtained in the world, not crafted.",
    recipe_furnace: "Furnace",
    recipe_furnace_note: fuel => `smelt ${fuel} with any fuel.`,
    recipe_table: "Crafting Table",
    recipe_shapeless: "Shapeless",
    makes_per: n => `makes ${n} per craft.`,
    fuel: "Fuel",
    difficulty: "Difficulty",
    diff_Easy: "Easy", diff_Medium: "Medium", diff_Hard: "Hard",
    efficiency: "Efficiency", footprint: "Footprint",
    build_multiplier: "Build multiplier",
    modules_to_build: "Modules to build:",
    scales_auto: "materials scale automatically",
    collection_progress: "Collection progress",
    materials: "Materials", reset: "Reset",
    blueprint: "Step-by-step blueprint", pro_tips: "Pro tips",
    watch: "Watch:", open_youtube: "↗ Open on YouTube",
    more_tutorials: "🔎 More 26.2 tutorials",
    checklist_reset: "Checklist reset",
    made_by: "Made by ever",
    cat_all: "All",
    "cat_Most Used": "Most Used", cat_Essential: "Essential", cat_Tools: "Tools",
    cat_Combat: "Combat", cat_Redstone: "Redstone", cat_Blocks: "Blocks",
    cat_Food: "Food", cat_Transport: "Transport", cat_Decoration: "Decoration",
    cat_Nether: "Nether", cat_End: "End",
    ftag_Resource: "Resource", ftag_XP: "XP", ftag_AFK: "AFK", ftag_Nether: "Nether",
    ftag_End: "End", ftag_Villager: "Villager", ftag_Combat: "Combat",
    ftag_Emeralds: "Emeralds", ftag_Food: "Food", ftag_Automatic: "Automatic",
    ftag_Fuel: "Fuel", ftag_Gunpowder: "Gunpowder", ftag_Copper: "Copper",
    ftag_Totems: "Totems", ftag_Ocean: "Ocean", ftag_Paper: "Paper", ftag_Building: "Building"
  }
};

/* translate a UI key (value may be a function taking an argument) */
function t(key, arg) {
  const table = STRINGS[LANG] || STRINGS.fr;
  let v = key in table ? table[key] : STRINGS.fr[key];
  if (v == null) return key;
  return typeof v === "function" ? v(arg) : v;
}

/* translate a bilingual data field: {fr, en} or a plain string */
function tr(o) {
  if (o == null) return "";
  if (typeof o === "string") return o;
  return o[LANG] || o.fr || o.en || "";
}

/* localized item name / description (falls back to English fields) */
function getName(item) { return (LANG === "fr" && item.name_fr) ? item.name_fr : item.name; }
function getDesc(item) { return (LANG === "fr" && item.description_fr) ? item.description_fr : (item.description || ""); }

/* localized farm tag */
function ftag(tag) {
  const k = "ftag_" + tag;
  const table = STRINGS[LANG] || STRINGS.fr;
  return k in table ? table[k] : tag;
}

function setLang(l) {
  try { localStorage.setItem("mcguide.lang", l); } catch (e) {}
  location.reload();
}

/* apply static translations (elements with data-i18n / data-i18n-ph) */
function applyStaticI18n() {
  document.querySelectorAll("[data-i18n]").forEach(el => { el.textContent = t(el.dataset.i18n); });
  document.querySelectorAll("[data-i18n-ph]").forEach(el => { el.placeholder = t(el.dataset.i18nPh); });
  const lb = document.getElementById("langToggle");
  if (lb) {
    lb.textContent = LANG === "fr" ? "EN" : "FR";
    lb.title = LANG === "fr" ? "Switch to English" : "Passer en français";
    lb.onclick = () => setLang(LANG === "fr" ? "en" : "fr");
  }
  document.documentElement.lang = LANG;
}
document.addEventListener("DOMContentLoaded", applyStaticI18n);
