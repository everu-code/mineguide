# ⛏️ MineGuide — Guide de crafting & fermes Minecraft

A local, offline-first web app for browsing crafting recipes and planning/tracking
Minecraft farms. Pure HTML/CSS/JS with a premium Minecraft-inspired dark theme —
no build step, no framework, no internet required to run. Deploys to Vercel as a
static site straight from GitHub.

![items](https://img.shields.io/badge/items-848-5db85c) ![farms](https://img.shields.io/badge/farms-19-5db85c) ![lang](https://img.shields.io/badge/langue-FR%20%2F%20EN-5db85c) ![version](https://img.shields.io/badge/Minecraft-26.2-5db85c) ![deps](https://img.shields.io/badge/frontend%20deps-none-5db85c)

> Interface **en français par défaut** (bouton `EN`/`FR` dans l'en-tête). Noms d'items officiels tirés du fichier de langue du jeu 26.2.

## Features

### 🧱 Crafting Guide (`index.html`)
- Dense grid of **848 items** — tools & armor (all tiers), redstone, every wood set (planks → doors, signs, hanging signs, boats, buttons, plates, incl. bamboo/crimson/warped/pale oak), the full stone/deepslate/blackstone/copper (1.21) families, building blocks, food, transport, brewing, and every colour variant (wool/carpet/bed/banner/candle/stained glass + panes/shulker box/glazed terracotta/concrete/terracotta).
- Live text search **and** tag filters (`Most Used`, `Essential`, `Redstone`, `Tools`, `Combat`, `Blocks`, `Food`, `Transport`, `Decoration`, plus a `★ Favorites` view).
- Click any item for a modal showing its **3×3 crafting blueprint**, required materials, yield, stack size and description.
- Ingredient cells are **clickable** — drill into sub-recipes (e.g. Piston → Redstone Torch).
- ⭐ Favorite recipes (saved locally).

### 🏭 Farm Builder & Tracker (`farms.html`)
- **19 popular, 26.2-compatible farms**: iron, gold/piglin, raid, mob XP, enderman, guardian, wither skeleton, blaze, creeper, slime, drowned (copper/trident), honey, wool, villager crops, sugar cane, bamboo, kelp, cactus, trading hall.
- Each farm shows a **real YouTube thumbnail** (from an existing, version-matched tutorial), difficulty + efficiency + footprint, a **material checklist**, a **collection progress bar**, a **build multiplier** (materials scale live), and a collapsible step-by-step blueprint + tips.
- Clicking a farm opens the **embedded tutorial** with a working **"Open on YouTube"** link plus a **search** fallback. All 19 videos are verified to exist (checked via YouTube oEmbed).

### 🌍 Language
- **French by default**, with a one-click `EN` / `FR` toggle in the header (choice saved locally).
- Item names come from the game's official 26.2 `fr_fr` / `en_us` language files; UI, categories, farms and descriptions are fully localized.

### 💾 Smart enhancements
- **Local Storage save** — favorites, farm checkboxes, multipliers and language all persist automatically.
- **Dynamic calculation** — farm multipliers recompute all quantities instantly.

## Running it

**Option A — just open it.** Double-click `index.html`. Data is bundled as JS
(`data/items.js`, `data/farms.js`) so it works straight from `file://`.

**Option B — local server** (needed if you want `fetch`-based JSON or clean URLs):

```bash
cd "minecraft-guide"
python -m http.server 8321
# then visit http://localhost:8321
```

## Project structure

```
mineguide/
├── index.html            # Crafting Guide
├── farms.html            # Farm Builder & Tracker
├── vercel.json           # Vercel static-site config (no build step)
├── css/style.css         # Premium dark theme
├── js/
│   ├── app.js            # shared: data access, localStorage, icons, toast
│   ├── crafting.js       # crafting page + modal + 3x3 grid
│   ├── farms.js          # farm cards, checklist, multiplier, video
│   └── i18n.js           # FR/EN strings + language toggle
├── data/
│   ├── items.json        # 848 items (structured data)
│   ├── farms.json        # farm data
│   ├── items.js          # auto-generated wrapper (window.ITEMS)
│   └── farms.js          # auto-generated wrapper (window.FARMS)
├── icons/                # 848 official PNG icons (from the scraper)
└── scraper/
    ├── build_items.py    # generates items.json from recipe shapes + loops
    ├── scrape.py         # downloads official in-game icons into items.json
    └── requirements.txt
```

## Official in-game icons (already included)

Every item ships with its **official inventory icon** for the latest game
version (the 26.x line — **26.2**), downloaded from the Minecraft Wiki's
`Invicon` render files. These are exactly what you see in-game:

- **Items** (iron ingot, diamond, redstone…) → 16×16 flat game sprites.
- **Blocks** (crafting table, furnace, chest, piston…) → 32×32 isometric 3D
  inventory renders — not flat face textures.

All 848 items ship with an icon; emoji are kept only as an automatic fallback if
an icon ever fails to load.

To re-fetch or update them (e.g. after a new game version):

```bash
cd scraper
pip install -r requirements.txt
python scrape.py            # download icons for every item
python scrape.py --force    # re-download even if files already exist
python scrape.py --info     # also refresh descriptions from the wiki
python scrape.py --dry-run  # preview without downloading
```

The scraper downloads to `icons/<id>.png`, sets each item's `icon` field, and
regenerates `data/items.js`. It only *adds* data and never overwrites recipes.

## Editing data

- **Bulk-generate items:** the whole catalog is built by `scraper/build_items.py`
  from compact recipe "shapes" + colour/tier loops. Add items there and run
  `python build_items.py` (it validates that every referenced ingredient exists),
  then `python scrape.py` to fetch the new icons.
- **Add/edit a single item:** edit `data/items.json`, then regenerate the JS wrapper:
  ```bash
  cd data && printf 'window.ITEMS = ' > items.js && cat items.json >> items.js && printf ';\n' >> items.js
  ```
  (The scraper does this for you automatically.)
- **Add/edit farms:** edit `data/farms.json`, then regenerate `farms.js` the same way.
- **Swap tutorial videos:** change each farm's `videoId` (the part after `watch?v=`).

## Deploy (GitHub + Vercel)

This is a **static site** — no build step. `vercel.json` tells Vercel to serve the
repo root as-is.

**Publish the repo (GitHub CLI):**

```bash
gh auth login                       # once, choose GitHub.com + HTTPS
gh repo create mineguide --public --source=. --remote=origin --push
```

**Deploy (Vercel CLI):**

```bash
npm i -g vercel                     # once
vercel login
vercel --prod                       # deploys the current folder
```

Or, in the Vercel dashboard, **New Project → Import** `mineguide` — it auto-detects
a static site and redeploys on every `git push`.

## Notes
- Recipe data is hand-authored to match real Minecraft crafting. Farm tutorial
  `videoId`s are illustrative placeholders — swap in your favorite creators.
- Minecraft Wiki content is CC BY-NC-SA; keep scraped assets to personal use.
- Not affiliated with Mojang or Microsoft.
