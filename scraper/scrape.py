#!/usr/bin/env python3
"""
Minecraft Companion — official icon downloader
==============================================

Downloads the **official in-game inventory icons** for every item in
`data/items.json` from the Minecraft Wiki (https://minecraft.wiki), using its
`Invicon` render files. These are the exact icons shown in the game's inventory
— proper isometric 3D renders for blocks (crafting table, furnace, chest,
piston…) and flat sprites for items (iron ingot, diamond, redstone…).

The wiki's Invicon renders track the current game version (the 26.x line, latest
stable 26.2). Item/flat textures are pixel-identical to the game files; block
renders match the in-game inventory look.

The script only *adds* an "icon" field to items.json and never deletes your
curated recipe data. Items whose icon can't be resolved keep their emoji.

USAGE
-----
    pip install -r requirements.txt

    python scrape.py                 # download every item's icon
    python scrape.py --info          # also refresh descriptions from the wiki
    python scrape.py --only iron_ingot,piston
    python scrape.py --force         # re-download icons that already exist
    python scrape.py --dry-run       # resolve URLs but download nothing

After running, `data/items.js` is regenerated so the app shows the new icons on
reload. Minecraft Wiki content is CC BY-NC-SA — keep assets to personal use.
This project is not affiliated with Mojang or Microsoft.
"""

import argparse
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("Missing dependency. Run:  pip install -r requirements.txt")

# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "items.json"
ICONS = ROOT / "icons"
API = "https://minecraft.wiki/api.php"
HEADERS = {"User-Agent": "MinecraftCompanion/1.0 (local personal project)"}
SLEEP = 0.5  # be polite to the wiki


# Windows consoles default to cp1252 and choke on ✓/•/– — force UTF-8.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def log(msg):
    print(msg, flush=True)


def api_get(params):
    params = {**params, "format": "json"}
    r = requests.get(API, params=params, headers=HEADERS, timeout=25)
    r.raise_for_status()
    return r.json()


def candidate_titles(item):
    """Wiki File: titles to try, most-accurate first. `Invicon <Name>` is the
    official inventory render used across the wiki."""
    name = item["name"]
    ident = " ".join(w.capitalize() for w in item["id"].split("_"))
    names = [name, ident]
    titles = []
    for n in names:
        titles += [f"File:Invicon {n}.png", f"File:{n} JE4 BE3.png", f"File:{n}.png"]
    seen, out = set(), []
    for t in titles:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def resolve_urls(items):
    """Batch-resolve an icon URL for each item. Returns {id: url}."""
    # Build ordered candidate list per item, keep the mapping title->item
    per_item = {i["id"]: candidate_titles(i) for i in items}
    all_titles = []
    for lst in per_item.values():
        all_titles += lst
    all_titles = list(dict.fromkeys(all_titles))  # de-dupe, keep order

    found = {}  # title -> url
    for k in range(0, len(all_titles), 45):
        batch = all_titles[k:k + 45]
        try:
            d = api_get({"action": "query", "titles": "|".join(batch),
                         "prop": "imageinfo", "iiprop": "url"})
        except Exception as e:
            log(f"    ! query failed: {e}")
            continue
        q = d.get("query", {})
        norm = {n["from"]: n["to"] for n in q.get("normalized", [])}
        by_title = {p.get("title"): p for p in q.get("pages", {}).values()}
        for t in batch:
            p = by_title.get(norm.get(t, t))
            if p and "imageinfo" in p:
                found[t] = p["imageinfo"][0]["url"]
        time.sleep(SLEEP)

    result = {}
    for iid, titles in per_item.items():
        for t in titles:
            if t in found:
                result[iid] = found[t]
                break
    return result


def download(url, dest):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    dest.write_bytes(r.content)


def fetch_description(item):
    try:
        d = api_get({"action": "query", "prop": "extracts", "exintro": 1,
                     "explaintext": 1, "redirects": 1, "titles": item["name"]})
    except Exception:
        return None
    for p in d.get("query", {}).get("pages", {}).values():
        text = (p.get("extract") or "").strip()
        if text:
            return re.split(r"(?<=[.!?])\s+", text)[0][:240]
    return None


def regenerate_js(items):
    js = ROOT / "data" / "items.js"
    js.write_text("window.ITEMS = " + json.dumps(items, indent=2) + ";\n", encoding="utf-8")
    log(f"  -> regenerated {js.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser(description="Download official Minecraft icons into items.json.")
    ap.add_argument("--info", action="store_true", help="also refresh descriptions")
    ap.add_argument("--only", help="comma-separated item ids to limit to")
    ap.add_argument("--dry-run", action="store_true", help="resolve but don't download/write")
    ap.add_argument("--force", action="store_true", help="re-download icons that already exist")
    args = ap.parse_args()

    if not DATA.exists():
        sys.exit(f"Cannot find {DATA}. Run from the scraper/ folder of the project.")

    items = json.loads(DATA.read_text(encoding="utf-8"))
    ICONS.mkdir(exist_ok=True)

    only = set(args.only.split(",")) if args.only else None
    targeted = [i for i in items if not only or i["id"] in only]

    log(f"Resolving official icons for {len(targeted)} item(s) from minecraft.wiki…")
    urls = resolve_urls(targeted)
    log(f"  {len(urls)}/{len(targeted)} resolved.\n")

    got = 0
    for item in targeted:
        iid = item["id"]
        dest = ICONS / f"{iid}.png"
        if dest.exists() and not args.force:
            item["icon"] = f"icons/{iid}.png"
            log(f"• {item['name']:22} ✓ already present")
        elif iid in urls:
            if args.dry_run:
                log(f"• {item['name']:22} (dry-run) {urls[iid]}")
            else:
                try:
                    download(urls[iid], dest)
                    item["icon"] = f"icons/{iid}.png"
                    got += 1
                    log(f"• {item['name']:22} ✓ downloaded")
                except Exception as e:
                    log(f"• {item['name']:22} ! download failed: {e}")
                time.sleep(SLEEP)
        else:
            log(f"• {item['name']:22} – no icon found (keeps emoji)")

        if args.info and not args.dry_run:
            desc = fetch_description(item)
            time.sleep(SLEEP)
            if desc:
                item["description"] = desc

    if args.dry_run:
        log("\nDry run complete — nothing written.")
        return

    DATA.write_text(json.dumps(items, indent=2) + "\n", encoding="utf-8")
    log(f"\nWrote {DATA.relative_to(ROOT)}")
    regenerate_js(items)
    log(f"Done. {got} new icon(s) downloaded. Reload the app to see them.")


if __name__ == "__main__":
    main()
