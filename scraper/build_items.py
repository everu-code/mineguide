#!/usr/bin/env python3
"""
Item catalog generator for Minecraft Companion (game version 26.2).

Builds ../data/items.json from compact recipe "shapes" + colour/tier loops, so
we can ship a huge, accurate crafting catalog without hand-writing every grid.

Run:  python build_items.py       (then run scrape.py to fetch icons)

It validates that every id referenced inside a recipe is also a defined item,
and preserves already-downloaded icons (icons/<id>.png).
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "icons"
OUT = ROOT / "data" / "items.json"

items = []
_seen = set()


def add(id, name, cats, desc, recipe, emoji="🧱", stack=64):
    if id in _seen:
        return
    _seen.add(id)
    items.append({"id": id, "name": name, "emoji": emoji, "category": cats,
                  "stackSize": stack, "description": desc, "recipe": recipe})


# ---------------- recipe helpers ----------------
def _ing(grid):
    d = {}
    for row in grid:
        for c in row:
            if c:
                d[c] = d.get(c, 0) + 1
    return d


def craft(grid, out=1, t="crafting_table"):
    g = [((row + [None, None, None])[:3]) for row in grid]
    while len(g) < 3:
        g.append([None, None, None])
    return {"type": t, "grid": g, "yields": out, "ingredients": _ing(g)}


def shapeless(parts, out=1):
    grid = [[None] * 3 for _ in range(3)]
    for i, p in enumerate(parts):
        grid[i // 3][i % 3] = p
    d = {}
    for p in parts:
        d[p] = d.get(p, 0) + 1
    return {"type": "shapeless", "grid": grid, "yields": out, "ingredients": d}


def furnace(src):
    return {"type": "furnace", "grid": [], "yields": 1, "ingredients": {src: 1}}


def gathered():
    return {"type": "gathered", "grid": [], "yields": 1, "ingredients": {}}


# shape helpers (material id -> recipe)
def pickaxe(m): return craft([[m, m, m], [None, "stick", None], [None, "stick", None]])
def axe(m): return craft([[m, m, None], [m, "stick", None], [None, "stick", None]])
def shovel(m): return craft([[None, m, None], [None, "stick", None], [None, "stick", None]])
def hoe(m): return craft([[m, m, None], [None, "stick", None], [None, "stick", None]])
def sword(m): return craft([[None, m, None], [None, m, None], [None, "stick", None]])
def helmet(m): return craft([[m, m, m], [m, None, m]], 1)
def chestplate(m): return craft([[m, None, m], [m, m, m], [m, m, m]], 1)
def leggings(m): return craft([[m, m, m], [m, None, m], [m, None, m]], 1)
def boots(m): return craft([[m, None, m], [m, None, m]], 1)
def stairs(m): return craft([[m, None, None], [m, m, None], [m, m, m]], 4)
def slab(m): return craft([[m, m, m]], 6)
def wall(m): return craft([[m, m, m], [m, m, m]], 6)
def door(m): return craft([[m, m], [m, m], [m, m]], 3)
def trapdoor(m): return craft([[m, m, m], [m, m, m]], 2)
def fence(m): return craft([[m, "stick", m], [m, "stick", m]], 3)
def fence_gate(m): return craft([["stick", m, "stick"], ["stick", m, "stick"]], 1)
def sign(m): return craft([[m, m, m], [m, m, m], [None, "stick", None]], 3)
def boat(m): return craft([[m, None, m], [m, m, m]], 1)
def block9(m): return craft([[m, m, m], [m, m, m], [m, m, m]], 1)
def square4(m, out=1): return craft([[m, m], [m, m]], out)


# ---------------- gathered raw materials ----------------
GATH = [
    ("oak_log", "Oak Log", ["Blocks", "Most Used"], "🪵"),
    ("cobblestone", "Cobblestone", ["Blocks", "Essential", "Most Used"], "🪨"),
    ("coal", "Coal", ["Most Used"], "⚫"),
    ("charcoal", "Charcoal", [], "⚫"),
    ("raw_iron", "Raw Iron", ["Most Used"], "🟤"),
    ("raw_gold", "Raw Gold", [], "🟠"),
    ("raw_copper", "Raw Copper", [], "🟠"),
    ("diamond", "Diamond", ["Essential"], "💎"),
    ("redstone", "Redstone Dust", ["Redstone", "Most Used"], "🔴"),
    ("lapis_lazuli", "Lapis Lazuli", [], "🔵"),
    ("emerald", "Emerald", [], "💚"),
    ("quartz", "Nether Quartz", ["Redstone"], "◽"),
    ("obsidian", "Obsidian", ["Blocks"], "⬛"),
    ("sand", "Sand", ["Blocks"], "🟨"),
    ("gravel", "Gravel", ["Blocks"], "🪨"),
    ("flint", "Flint", [], "🪨"),
    ("string", "String", [], "🧵"),
    ("gunpowder", "Gunpowder", ["Redstone"], "💥"),
    ("feather", "Feather", [], "🪶"),
    ("leather", "Leather", [], "🟫"),
    ("bone", "Bone", [], "🦴"),
    ("slime_ball", "Slimeball", [], "🟢"),
    ("ender_pearl", "Ender Pearl", ["End"], "🟣"),
    ("blaze_rod", "Blaze Rod", ["Nether"], "🟡"),
    ("glowstone_dust", "Glowstone Dust", ["Nether"], "✨"),
    ("nether_star", "Nether Star", [], "🌟"),
    ("ancient_debris", "Ancient Debris", ["Nether"], "🟤"),
    ("wheat", "Wheat", ["Food"], "🌾"),
    ("sugar_cane", "Sugar Cane", ["Food"], "🎋"),
    ("bamboo", "Bamboo", [], "🎍"),
    ("carrot", "Carrot", ["Food"], "🥕"),
    ("potato", "Potato", ["Food"], "🥔"),
    ("beetroot", "Beetroot", ["Food"], "🫜"),
    ("apple", "Apple", ["Food"], "🍎"),
    ("egg", "Egg", ["Food"], "🥚"),
    ("cocoa_beans", "Cocoa Beans", ["Food"], "🫘"),
    ("melon_slice", "Melon Slice", ["Food"], "🍈"),
    ("pumpkin", "Pumpkin", ["Blocks"], "🎃"),
    ("honeycomb", "Honeycomb", [], "🍯"),
    ("milk_bucket", "Milk Bucket", ["Food"], "🥛"),
    ("clay_ball", "Clay Ball", [], "🟫"),
    ("amethyst_shard", "Amethyst Shard", [], "🟪"),
    ("shulker_shell", "Shulker Shell", ["End"], "🐚"),
    ("nautilus_shell", "Nautilus Shell", [], "🐚"),
    ("heart_of_the_sea", "Heart of the Sea", [], "💙"),
    ("turtle_scute", "Turtle Scute", [], "🐢"),
    ("kelp", "Kelp", ["Food"], "🌿"),
    ("ink_sac", "Ink Sac", [], "⚫"),
    ("glow_ink_sac", "Glow Ink Sac", [], "🔵"),
    ("prismarine_shard", "Prismarine Shard", [], "🔷"),
    ("prismarine_crystals", "Prismarine Crystals", [], "🔷"),
    ("poppy", "Poppy", [], "🌺"),
    ("dandelion", "Dandelion", [], "🌼"),
    ("cactus", "Cactus", [], "🌵"),
    ("red_mushroom", "Red Mushroom", ["Food"], "🍄"),
    ("brown_mushroom", "Brown Mushroom", ["Food"], "🍄"),
    ("spider_eye", "Spider Eye", [], "👁️"),
    ("beef", "Raw Beef", ["Food"], "🥩"),
    ("porkchop", "Raw Porkchop", ["Food"], "🥩"),
    ("chicken", "Raw Chicken", ["Food"], "🍗"),
    ("mutton", "Raw Mutton", ["Food"], "🍖"),
    ("cod", "Raw Cod", ["Food"], "🐟"),
    ("salmon", "Raw Salmon", ["Food"], "🐟"),
]
for id, name, cats, emo in GATH:
    add(id, name, cats, f"{name} — gathered or mined in the world.", gathered(), emo)


# ---------------- core basics ----------------
add("oak_planks", "Oak Planks", ["Blocks", "Essential", "Most Used"],
    "Basic building block and ingredient. One log yields four planks.",
    shapeless(["oak_log"], 4), "🟫")
add("stick", "Stick", ["Essential", "Most Used"],
    "Used in tools, torches and more. Two planks make four sticks.",
    craft([["oak_planks"], ["oak_planks"]], 4), "🥢")
add("crafting_table", "Crafting Table", ["Blocks", "Essential", "Most Used"],
    "Opens the 3x3 crafting grid. The most important early block.",
    craft([["oak_planks", "oak_planks"], ["oak_planks", "oak_planks"]], 1), "🛠️")
add("furnace", "Furnace", ["Blocks", "Essential", "Most Used"],
    "Smelts ores, cooks food and burns fuel.",
    craft([["cobblestone", "cobblestone", "cobblestone"], ["cobblestone", None, "cobblestone"],
           ["cobblestone", "cobblestone", "cobblestone"]]), "🔥")
add("chest", "Chest", ["Blocks", "Essential", "Most Used"],
    "27 slots of storage. Place two side by side for a double chest.",
    craft([["oak_planks", "oak_planks", "oak_planks"], ["oak_planks", None, "oak_planks"],
           ["oak_planks", "oak_planks", "oak_planks"]]), "🧰")

# smelting outputs
add("iron_ingot", "Iron Ingot", ["Essential", "Most Used"],
    "Smelted from raw iron. Core material for tools, armor and redstone.", furnace("raw_iron"), "⬜")
add("gold_ingot", "Gold Ingot", ["Essential"],
    "Smelted from raw gold. Used in rails, clocks and brewing.", furnace("raw_gold"), "🟨")
add("copper_ingot", "Copper Ingot", [],
    "Smelted from raw copper. Used in spyglasses and lightning rods.", furnace("raw_copper"), "🟧")
add("netherite_scrap", "Netherite Scrap", ["Nether"],
    "Smelted from ancient debris found deep in the Nether.", furnace("ancient_debris"), "🟤")
add("stone", "Stone", ["Blocks"], "Smelted from cobblestone.", furnace("cobblestone"), "🪨")
add("smooth_stone", "Smooth Stone", ["Blocks"], "Smelted from stone.", furnace("stone"), "⬜")
add("glass", "Glass", ["Blocks"], "Smelted from sand.", furnace("sand"), "🔲")
add("terracotta", "Terracotta", ["Blocks"], "Smelted from a block of clay.", furnace("clay"), "🟧")
add("brick", "Brick", [], "Smelted from a clay ball.", furnace("clay_ball"), "🧱")
add("charcoal_note", "Dried Kelp", ["Food"], "Smelted from kelp; a renewable food and fuel base.",
    furnace("kelp"), "🌿")  # placeholder id fix below
# fix dried_kelp id
items[-1]["id"] = "dried_kelp"
_seen.discard("charcoal_note"); _seen.add("dried_kelp")

for raw, ing, label, emo in [("beef", "cooked_beef", "Steak", "🥩"),
                             ("porkchop", "cooked_porkchop", "Cooked Porkchop", "🍖"),
                             ("chicken", "cooked_chicken", "Cooked Chicken", "🍗"),
                             ("mutton", "cooked_mutton", "Cooked Mutton", "🍖"),
                             ("cod", "cooked_cod", "Cooked Cod", "🐟"),
                             ("salmon", "cooked_salmon", "Cooked Salmon", "🐟"),
                             ("potato", "baked_potato", "Baked Potato", "🥔")]:
    add(ing, label, ["Food"], f"{label} — smelted/cooked in a furnace or smoker.", furnace(raw), emo)

# metal nuggets & compressed blocks
add("iron_nugget", "Iron Nugget", [], "Nine make an ingot; used for chains and lanterns.",
    shapeless(["iron_ingot"], 9), "▫️")
add("gold_nugget", "Gold Nugget", [], "Nine make an ingot; used for golden carrots and clocks.",
    shapeless(["gold_ingot"], 9), "▫️")
add("netherite_ingot", "Netherite Ingot", ["Nether"],
    "Four netherite scrap + four gold ingots. Used to upgrade diamond gear.",
    shapeless(["netherite_scrap", "netherite_scrap", "netherite_scrap", "netherite_scrap",
               "gold_ingot", "gold_ingot", "gold_ingot", "gold_ingot"]), "🟫")

for bid, mat, label, emo, cats in [
    ("iron_block", "iron_ingot", "Block of Iron", "⬜", ["Blocks"]),
    ("gold_block", "gold_ingot", "Block of Gold", "🟨", ["Blocks"]),
    ("diamond_block", "diamond", "Block of Diamond", "💎", ["Blocks"]),
    ("emerald_block", "emerald", "Block of Emerald", "💚", ["Blocks"]),
    ("coal_block", "coal", "Block of Coal", "⬛", ["Blocks"]),
    ("redstone_block", "redstone", "Block of Redstone", "🟥", ["Redstone", "Blocks"]),
    ("copper_block", "copper_ingot", "Block of Copper", "🟧", ["Blocks"]),
    ("netherite_block", "netherite_ingot", "Block of Netherite", "🟫", ["Blocks"]),
    ("lapis_block", "lapis_lazuli", "Lapis Lazuli Block", "🔵", ["Blocks"]),
    ("slime_block", "slime_ball", "Slime Block", "🟩", ["Redstone", "Blocks"]),
    ("bone_block", "bone_meal", "Bone Block", "🦴", ["Blocks"]),
    ("hay_block", "wheat", "Hay Bale", "🌾", ["Blocks", "Food"]),
    ("dried_kelp_block", "dried_kelp", "Dried Kelp Block", "🟩", ["Blocks"]),
]:
    add(bid, label, cats, f"Compact storage: nine {mat.replace('_', ' ')}.", block9(mat), emo)

add("clay", "Clay", ["Blocks"], "Four clay balls. Smelt into terracotta.", square4("clay_ball"), "🟫")
add("quartz_block", "Block of Quartz", ["Blocks"], "Four nether quartz.", square4("quartz"), "◻️")
add("sandstone", "Sandstone", ["Blocks"], "Four sand blocks.", square4("sand"), "🟨")
add("prismarine", "Prismarine", ["Blocks"], "Four prismarine shards.", square4("prismarine_shard"), "🔷")
add("glowstone", "Glowstone", ["Blocks", "Nether"], "Four glowstone dust.", square4("glowstone_dust"), "✨")
add("bone_meal", "Bone Meal", ["Food"], "Fertilizer and white dye. One bone makes three.",
    shapeless(["bone"], 3), "⚪")
add("magma_cream", "Magma Cream", ["Nether"], "Blaze powder + slimeball. Brewing & magma blocks.",
    shapeless(["blaze_powder", "slime_ball"]), "🟠")
add("magma_block", "Magma Block", ["Blocks", "Nether"], "Four magma cream.", square4("magma_cream"), "🟥")

# ---------------- tools ----------------
TOOL_TIERS = [("wooden", "oak_planks", "Wooden"), ("stone", "cobblestone", "Stone"),
              ("iron", "iron_ingot", "Iron"), ("golden", "gold_ingot", "Golden"),
              ("diamond", "diamond", "Diamond")]
for tid, mat, label in TOOL_TIERS:
    add(f"{tid}_sword", f"{label} Sword", ["Combat", "Tools"], f"{label} melee weapon.", sword(mat), "🗡️", 1)
    add(f"{tid}_pickaxe", f"{label} Pickaxe", ["Tools"], f"{label} pickaxe for mining.", pickaxe(mat), "⛏️", 1)
    add(f"{tid}_axe", f"{label} Axe", ["Tools"], f"{label} axe for chopping wood.", axe(mat), "🪓", 1)
    add(f"{tid}_shovel", f"{label} Shovel", ["Tools"], f"{label} shovel for digging.", shovel(mat), "🥄", 1)
    add(f"{tid}_hoe", f"{label} Hoe", ["Tools"], f"{label} hoe for farming.", hoe(mat), "🧑‍🌾", 1)

# ---------------- armor ----------------
ARMOR = [("leather", "leather", {"helmet": "Leather Cap", "chestplate": "Leather Tunic",
                                 "leggings": "Leather Pants", "boots": "Leather Boots"}),
         ("iron", "iron_ingot", {"helmet": "Iron Helmet", "chestplate": "Iron Chestplate",
                                 "leggings": "Iron Leggings", "boots": "Iron Boots"}),
         ("golden", "gold_ingot", {"helmet": "Golden Helmet", "chestplate": "Golden Chestplate",
                                   "leggings": "Golden Leggings", "boots": "Golden Boots"}),
         ("diamond", "diamond", {"helmet": "Diamond Helmet", "chestplate": "Diamond Chestplate",
                                 "leggings": "Diamond Leggings", "boots": "Diamond Boots"})]
_shape = {"helmet": helmet, "chestplate": chestplate, "leggings": leggings, "boots": boots}
_emo = {"helmet": "🪖", "chestplate": "🦺", "leggings": "👖", "boots": "🥾"}
for tid, mat, names in ARMOR:
    for piece, nm in names.items():
        add(f"{tid}_{piece}", nm, ["Combat"], f"{nm} — wearable armor.", _shape[piece](mat), _emo[piece], 1)
add("turtle_helmet", "Turtle Shell", ["Combat"], "Helmet that grants Water Breathing. Five turtle scutes.",
    helmet("turtle_scute"), "🐢", 1)

# ---------------- misc tools & utility items ----------------
add("torch", "Torch", ["Essential", "Most Used"], "Light source. Coal + stick makes four.",
    craft([["coal"], ["stick"]], 4), "🕯️")
add("soul_torch", "Soul Torch", ["Nether"], "Blue torch; torch + soul soil/sand.",
    shapeless(["coal", "stick", "soul_soil"]), "🔵")
add("soul_soil", "Soul Soil", ["Nether"], "Found in soul sand valleys.", gathered(), "🟫")
add("lantern", "Lantern", ["Blocks"], "Eight iron nuggets around a torch.",
    craft([["iron_nugget", "iron_nugget", "iron_nugget"], ["iron_nugget", "torch", "iron_nugget"],
           ["iron_nugget", "iron_nugget", "iron_nugget"]]), "🏮")
add("chain", "Chain", ["Blocks"], "Iron nugget + ingot + nugget.",
    craft([["iron_nugget"], ["iron_ingot"], ["iron_nugget"]]), "⛓️")
add("bucket", "Bucket", ["Tools", "Essential"], "Holds water, lava or milk. Three iron.",
    craft([["iron_ingot", None, "iron_ingot"], [None, "iron_ingot", None]]), "🪣", 16)
add("water_bucket", "Water Bucket", ["Tools", "Essential", "Most Used"],
    "A bucket filled with water — vital for farms, mining and travel.", gathered(), "🪣", 1)
add("flint_and_steel", "Flint and Steel", ["Tools"], "Lights fires and TNT.",
    shapeless(["iron_ingot", "flint"]), "🔥", 1)
add("shears", "Shears", ["Tools"], "Two iron ingots. Shears sheep and leaves.",
    craft([[None, "iron_ingot"], ["iron_ingot", None]]), "✂️", 1)
add("fishing_rod", "Fishing Rod", ["Tools"], "Three sticks + two string.",
    craft([[None, None, "stick"], [None, "stick", "string"], ["stick", None, "string"]]), "🎣", 1)
add("compass", "Compass", ["Tools"], "Points to your world spawn. Four iron + redstone.",
    craft([[None, "iron_ingot", None], ["iron_ingot", "redstone", "iron_ingot"],
           [None, "iron_ingot", None]]), "🧭", 1)
add("clock", "Clock", ["Tools"], "Shows the in-game time. Four gold + redstone.",
    craft([[None, "gold_ingot", None], ["gold_ingot", "redstone", "gold_ingot"],
           [None, "gold_ingot", None]]), "🕐", 1)
add("spyglass", "Spyglass", ["Tools"], "Zoom in. Two copper + one amethyst shard.",
    craft([["amethyst_shard"], ["copper_ingot"], ["copper_ingot"]]), "🔭", 1)
add("brush", "Brush", ["Tools"], "Feather + copper + stick. For archaeology.",
    craft([["feather"], ["copper_ingot"], ["stick"]]), "🖌️", 1)
add("lead", "Lead", ["Tools"], "Four string + one slimeball. Leash mobs.",
    craft([["string", "string", None], ["string", "slime_ball", None], [None, None, "string"]], 2), "🪢")
add("shield", "Shield", ["Combat", "Essential"], "Blocks damage. Six planks + one iron.",
    craft([["oak_planks", "iron_ingot", "oak_planks"], ["oak_planks", "oak_planks", "oak_planks"],
           [None, "oak_planks", None]]), "🛡️", 1)
add("bow", "Bow", ["Combat"], "Three sticks + three string.",
    craft([[None, "stick", "string"], ["stick", None, "string"], [None, "stick", "string"]]), "🏹", 1)
add("crossbow", "Crossbow", ["Combat"], "Sticks, iron, string and a tripwire hook.",
    craft([["stick", "iron_ingot", "stick"], ["string", "tripwire_hook", "string"],
           [None, "stick", None]]), "🏹", 1)
add("arrow", "Arrow", ["Combat"], "Flint + stick + feather makes four.",
    craft([["flint"], ["stick"], ["feather"]], 4), "🎯")

# ---------------- redstone ----------------
add("redstone_torch", "Redstone Torch", ["Redstone"], "Constant power source.",
    craft([["redstone"], ["stick"]]), "🔺")
add("repeater", "Redstone Repeater", ["Redstone"], "Delays and repeats signals.",
    craft([["redstone_torch", "redstone", "redstone_torch"], ["stone", "stone", "stone"]]), "🔁")
add("comparator", "Redstone Comparator", ["Redstone"], "Compares signals; reads containers.",
    craft([[None, "redstone_torch", None], ["redstone_torch", "quartz", "redstone_torch"],
           ["stone", "stone", "stone"]]), "⚖️")
add("redstone_lamp", "Redstone Lamp", ["Redstone"], "Glowstone + four redstone. Toggleable light.",
    craft([[None, "redstone", None], ["redstone", "glowstone", "redstone"], [None, "redstone", None]]), "💡")
add("piston", "Piston", ["Redstone", "Blocks"], "Pushes blocks when powered.",
    craft([["oak_planks", "oak_planks", "oak_planks"], ["cobblestone", "iron_ingot", "cobblestone"],
           ["cobblestone", "redstone", "cobblestone"]]), "🟩")
add("sticky_piston", "Sticky Piston", ["Redstone"], "Piston + slimeball. Pulls blocks back.",
    craft([["slime_ball"], ["piston"]]), "🟩")
add("observer", "Observer", ["Redstone"], "Pulses when the watched block changes.",
    craft([["cobblestone", "cobblestone", "cobblestone"], ["redstone", "redstone", "quartz"],
           ["cobblestone", "cobblestone", "cobblestone"]]), "👁️")
add("hopper", "Hopper", ["Redstone", "Essential"], "Moves items between containers.",
    craft([["iron_ingot", None, "iron_ingot"], ["iron_ingot", "chest", "iron_ingot"],
           [None, "iron_ingot", None]]), "🔻")
add("dropper", "Dropper", ["Redstone"], "Drops items when powered.",
    craft([["cobblestone", "cobblestone", "cobblestone"], ["cobblestone", None, "cobblestone"],
           ["cobblestone", "redstone", "cobblestone"]]), "📦")
add("dispenser", "Dispenser", ["Redstone"], "Shoots or places items. Adds a bow to a dropper.",
    craft([["cobblestone", "cobblestone", "cobblestone"], ["cobblestone", "bow", "cobblestone"],
           ["cobblestone", "redstone", "cobblestone"]]), "🎰")
add("lever", "Lever", ["Redstone"], "Toggle power on/off.",
    craft([["stick"], ["cobblestone"]]), "🎚️")
add("stone_button", "Stone Button", ["Redstone"], "Momentary power pulse.", shapeless(["stone"]), "🔘")
add("oak_button", "Oak Button", ["Redstone"], "Momentary power pulse.", shapeless(["oak_planks"]), "🔘")
add("stone_pressure_plate", "Stone Pressure Plate", ["Redstone"], "Triggers when stepped on.",
    craft([["stone", "stone"]]), "⬛")
add("oak_pressure_plate", "Oak Pressure Plate", ["Redstone"], "Triggers when stepped on.",
    craft([["oak_planks", "oak_planks"]]), "🟫")
add("tripwire_hook", "Tripwire Hook", ["Redstone"], "String trap trigger.",
    craft([["iron_ingot"], ["stick"], ["oak_planks"]], 2), "🪝")
add("target", "Target", ["Redstone"], "Emits signal by hit accuracy. Redstone + hay.",
    craft([[None, "redstone", None], ["redstone", "hay_block", "redstone"], [None, "redstone", None]]), "🎯")
add("daylight_detector", "Daylight Detector", ["Redstone"], "Outputs power based on sunlight.",
    craft([["glass", "glass", "glass"], ["quartz", "quartz", "quartz"],
           ["oak_slab", "oak_slab", "oak_slab"]]), "🔆")
add("note_block", "Note Block", ["Redstone"], "Plays notes when powered.",
    craft([["oak_planks", "oak_planks", "oak_planks"], ["oak_planks", "redstone", "oak_planks"],
           ["oak_planks", "oak_planks", "oak_planks"]]), "🎵")
add("tnt", "TNT", ["Redstone", "Blocks"], "Explosive. Five gunpowder + four sand.",
    craft([["gunpowder", "sand", "gunpowder"], ["sand", "gunpowder", "sand"],
           ["gunpowder", "sand", "gunpowder"]]), "🧨")
add("lightning_rod", "Lightning Rod", ["Redstone"], "Three copper ingots. Diverts lightning.",
    craft([["copper_ingot"], ["copper_ingot"], ["copper_ingot"]]), "⚡")
add("crafter", "Crafter", ["Redstone"], "Auto-crafts when powered (1.21+).",
    craft([["iron_ingot", "iron_ingot", "iron_ingot"], ["iron_ingot", "crafting_table", "iron_ingot"],
           ["redstone", "dropper", "redstone"]]), "🛠️")

# rails & transport
add("rail", "Rail", ["Transport", "Redstone"], "Six iron + a stick make sixteen.",
    craft([["iron_ingot", None, "iron_ingot"], ["iron_ingot", "stick", "iron_ingot"],
           ["iron_ingot", None, "iron_ingot"]], 16), "🛤️")
add("powered_rail", "Powered Rail", ["Transport", "Redstone"], "Accelerates minecarts.",
    craft([["gold_ingot", None, "gold_ingot"], ["gold_ingot", "stick", "gold_ingot"],
           ["gold_ingot", "redstone", "gold_ingot"]], 6), "🟧")
add("detector_rail", "Detector Rail", ["Transport", "Redstone"], "Detects passing minecarts.",
    craft([["iron_ingot", None, "iron_ingot"], ["iron_ingot", "stone_pressure_plate", "iron_ingot"],
           ["iron_ingot", "redstone", "iron_ingot"]], 6), "🟥")
add("activator_rail", "Activator Rail", ["Transport", "Redstone"], "Activates minecart contents.",
    craft([["iron_ingot", "stick", "iron_ingot"], ["iron_ingot", "redstone_torch", "iron_ingot"],
           ["iron_ingot", "stick", "iron_ingot"]], 6), "🟨")
add("minecart", "Minecart", ["Transport"], "Rides on rails. Five iron.",
    craft([["iron_ingot", None, "iron_ingot"], ["iron_ingot", "iron_ingot", "iron_ingot"]]), "🛒", 1)
for cid, comp, label in [("chest_minecart", "chest", "Minecart with Chest"),
                         ("furnace_minecart", "furnace", "Minecart with Furnace"),
                         ("hopper_minecart", "hopper", "Minecart with Hopper"),
                         ("tnt_minecart", "tnt", "Minecart with TNT")]:
    add(cid, label, ["Transport"], f"{label}.", shapeless([comp, "minecart"]), "🛒", 1)
add("oak_boat", "Oak Boat", ["Transport"], "Five planks. Floats on water.", boat("oak_planks"), "🛶", 1)
add("oak_chest_boat", "Oak Boat with Chest", ["Transport"], "Boat + chest.",
    shapeless(["chest", "oak_boat"]), "🛶", 1)
add("carrot_on_a_stick", "Carrot on a Stick", ["Transport", "Tools"], "Steer saddled pigs.",
    craft([["fishing_rod", None], [None, "carrot"]]), "🥕", 1)

# ---------------- utility / station blocks ----------------
add("bookshelf", "Bookshelf", ["Blocks"], "Six planks + three books. Powers enchanting.",
    craft([["oak_planks", "oak_planks", "oak_planks"], ["book", "book", "book"],
           ["oak_planks", "oak_planks", "oak_planks"]]), "📚")
add("chiseled_bookshelf", "Chiseled Bookshelf", ["Blocks"], "Stores books; readable by comparators.",
    craft([["oak_planks", "oak_planks", "oak_planks"], ["oak_slab", "oak_slab", "oak_slab"],
           ["oak_planks", "oak_planks", "oak_planks"]]), "📚")
add("barrel", "Barrel", ["Blocks"], "Storage that opens in tight spaces.",
    craft([["oak_planks", "oak_slab", "oak_planks"], ["oak_planks", None, "oak_planks"],
           ["oak_planks", "oak_slab", "oak_planks"]]), "🛢️")
add("smithing_table", "Smithing Table", ["Blocks"], "Upgrade diamond gear to netherite.",
    craft([["iron_ingot", "iron_ingot"], ["oak_planks", "oak_planks"], ["oak_planks", "oak_planks"]]), "⚒️")
add("fletching_table", "Fletching Table", ["Blocks"], "Fletcher villager workstation.",
    craft([["flint", "flint"], ["oak_planks", "oak_planks"], ["oak_planks", "oak_planks"]]), "🪵")
add("cartography_table", "Cartography Table", ["Blocks"], "Copy and expand maps.",
    craft([["paper", "paper"], ["oak_planks", "oak_planks"], ["oak_planks", "oak_planks"]]), "🗺️")
add("loom", "Loom", ["Blocks"], "Apply patterns to banners.",
    craft([["string", "string"], ["oak_planks", "oak_planks"]]), "🧵")
add("grindstone", "Grindstone", ["Blocks"], "Repairs tools and removes enchantments.",
    craft([["stick", "stone_slab", "stick"], ["oak_planks", None, "oak_planks"]]), "🪨")
add("stonecutter", "Stonecutter", ["Blocks"], "Cut stone into shapes efficiently.",
    craft([[None, "iron_ingot", None], ["stone", "stone", "stone"]]), "🪚")
add("blast_furnace", "Blast Furnace", ["Blocks"], "Smelts ore twice as fast.",
    craft([["iron_ingot", "iron_ingot", "iron_ingot"], ["iron_ingot", "furnace", "iron_ingot"],
           ["smooth_stone", "smooth_stone", "smooth_stone"]]), "🔥")
add("smoker", "Smoker", ["Blocks"], "Cooks food twice as fast.",
    craft([[None, "oak_log", None], ["oak_log", "furnace", "oak_log"], [None, "oak_log", None]]), "🍖")
add("campfire", "Campfire", ["Blocks"], "Cooks food and gives light. No fuel needed.",
    craft([[None, "stick", None], ["stick", "coal", "stick"], ["oak_log", "oak_log", "oak_log"]]), "🔥")
add("lectern", "Lectern", ["Blocks"], "Holds a book; librarian workstation.",
    craft([["oak_slab", "oak_slab", "oak_slab"], [None, "bookshelf", None], [None, "oak_slab", None]]), "📖")
add("composter", "Composter", ["Blocks"], "Turns crops into bone meal.",
    craft([["oak_slab", None, "oak_slab"], ["oak_slab", None, "oak_slab"],
           ["oak_slab", "oak_slab", "oak_slab"]]), "🪵")
add("beehive", "Beehive", ["Blocks"], "Six planks + three honeycomb. Houses bees.",
    craft([["oak_planks", "oak_planks", "oak_planks"], ["honeycomb", "honeycomb", "honeycomb"],
           ["oak_planks", "oak_planks", "oak_planks"]]), "🐝")
add("enchanting_table", "Enchanting Table", ["Essential"], "Book + diamonds + obsidian.",
    craft([[None, "book", None], ["diamond", "obsidian", "diamond"],
           ["obsidian", "obsidian", "obsidian"]]), "📿")
add("anvil", "Anvil", ["Blocks", "Essential"], "Three iron blocks + four ingots. Repairs & renames.",
    craft([["iron_block", "iron_block", "iron_block"], [None, "iron_ingot", None],
           ["iron_ingot", "iron_ingot", "iron_ingot"]]), "🔨")
add("brewing_stand", "Brewing Stand", ["Blocks"], "Blaze rod + three cobblestone. Makes potions.",
    craft([[None, "blaze_rod", None], ["cobblestone", "cobblestone", "cobblestone"]]), "⚗️")
add("cauldron", "Cauldron", ["Blocks"], "Seven iron. Holds water or lava.",
    craft([["iron_ingot", None, "iron_ingot"], ["iron_ingot", None, "iron_ingot"],
           ["iron_ingot", "iron_ingot", "iron_ingot"]]), "🕳️")
add("jukebox", "Jukebox", ["Blocks"], "Eight planks + a diamond. Plays music discs.",
    craft([["oak_planks", "oak_planks", "oak_planks"], ["oak_planks", "diamond", "oak_planks"],
           ["oak_planks", "oak_planks", "oak_planks"]]), "🎶")
add("ender_chest", "Ender Chest", ["Blocks"], "Eight obsidian + eye of ender. Shared storage.",
    craft([["obsidian", "obsidian", "obsidian"], ["obsidian", "ender_eye", "obsidian"],
           ["obsidian", "obsidian", "obsidian"]]), "🟩")
add("shulker_box", "Shulker Box", ["Blocks"], "Chest + two shulker shells. Keeps items when broken.",
    craft([["shulker_shell"], ["chest"], ["shulker_shell"]]), "🟪")
add("beacon", "Beacon", ["Blocks"], "Glass + obsidian + nether star. Grants area buffs.",
    craft([["glass", "glass", "glass"], ["glass", "nether_star", "glass"],
           ["obsidian", "obsidian", "obsidian"]]), "🔆")
add("conduit", "Conduit", ["Blocks"], "Heart of the sea + eight nautilus shells.",
    craft([["nautilus_shell", "nautilus_shell", "nautilus_shell"],
           ["nautilus_shell", "heart_of_the_sea", "nautilus_shell"],
           ["nautilus_shell", "nautilus_shell", "nautilus_shell"]]), "🔱")
add("scaffolding", "Scaffolding", ["Blocks"], "Six bamboo + one string. Easy vertical building.",
    craft([["bamboo", "string", "bamboo"], ["bamboo", None, "bamboo"], ["bamboo", None, "bamboo"]], 6), "🪜")
add("ladder", "Ladder", ["Blocks"], "Seven sticks make three.",
    craft([["stick", None, "stick"], ["stick", "stick", "stick"], ["stick", None, "stick"]], 3), "🪜")

# ---------------- building blocks ----------------
add("glass_pane", "Glass Pane", ["Blocks"], "Six glass make sixteen panes.",
    craft([["glass", "glass", "glass"], ["glass", "glass", "glass"]], 16), "🪟")
add("iron_bars", "Iron Bars", ["Blocks"], "Six iron make sixteen bars.",
    craft([["iron_ingot", "iron_ingot", "iron_ingot"], ["iron_ingot", "iron_ingot", "iron_ingot"]], 16), "🔳")
add("stone_bricks", "Stone Bricks", ["Blocks"], "Four stone.", square4("stone", 4), "🧱")
add("bricks", "Bricks", ["Blocks"], "Four bricks.", square4("brick", 1), "🧱")
add("oak_door", "Oak Door", ["Blocks"], "Six planks make three doors.", door("oak_planks"), "🚪")
add("oak_trapdoor", "Oak Trapdoor", ["Blocks"], "Six planks make two.", trapdoor("oak_planks"), "🚪")
add("oak_fence", "Oak Fence", ["Blocks"], "Planks + sticks.", fence("oak_planks"), "🪵")
add("oak_fence_gate", "Oak Fence Gate", ["Blocks"], "Openable fence section.", fence_gate("oak_planks"), "🚧")
add("oak_sign", "Oak Sign", ["Blocks"], "Six planks + a stick make three.", sign("oak_planks"), "🪧")
for bid, mat, label in [("oak_stairs", "oak_planks", "Oak Stairs"),
                        ("cobblestone_stairs", "cobblestone", "Cobblestone Stairs"),
                        ("stone_stairs", "stone", "Stone Stairs"),
                        ("stone_brick_stairs", "stone_bricks", "Stone Brick Stairs"),
                        ("brick_stairs", "bricks", "Brick Stairs")]:
    add(bid, label, ["Blocks"], f"{label} — six blocks make four.", stairs(mat), "🪜")
for bid, mat, label in [("oak_slab", "oak_planks", "Oak Slab"),
                        ("cobblestone_slab", "cobblestone", "Cobblestone Slab"),
                        ("stone_slab", "stone", "Stone Slab"),
                        ("smooth_stone_slab", "smooth_stone", "Smooth Stone Slab"),
                        ("stone_brick_slab", "stone_bricks", "Stone Brick Slab")]:
    add(bid, label, ["Blocks"], f"{label} — three blocks make six.", slab(mat), "▬")
for bid, mat, label in [("cobblestone_wall", "cobblestone", "Cobblestone Wall"),
                        ("stone_brick_wall", "stone_bricks", "Stone Brick Wall")]:
    add(bid, label, ["Blocks"], f"{label} — six blocks make six.", wall(mat), "🧱")

# ---------------- decoration ----------------
add("item_frame", "Item Frame", ["Blocks"], "Eight sticks + leather. Displays items.",
    craft([["stick", "stick", "stick"], ["stick", "leather", "stick"], ["stick", "stick", "stick"]]), "🖼️")
add("glow_item_frame", "Glow Item Frame", ["Blocks"], "Item frame + glow ink sac.",
    shapeless(["item_frame", "glow_ink_sac"]), "🖼️")
add("painting", "Painting", ["Blocks"], "Eight sticks + wool.",
    craft([["stick", "stick", "stick"], ["stick", "white_wool", "stick"], ["stick", "stick", "stick"]]), "🖼️")
add("flower_pot", "Flower Pot", ["Blocks"], "Three bricks.",
    craft([["brick", None, "brick"], [None, "brick", None]]), "🪴")
add("armor_stand", "Armor Stand", ["Blocks"], "Six sticks + a stone slab. Displays armor.",
    craft([["stick", "stick", "stick"], [None, "stick", None],
           ["stick", "smooth_stone_slab", "stick"]]), "🧍")
add("candle", "Candle", ["Blocks"], "String + honeycomb. A dyeable light.",
    craft([["string"], ["honeycomb"]]), "🕯️")
add("sea_lantern", "Sea Lantern", ["Blocks"], "Prismarine shards + crystals.",
    craft([["prismarine_shard", "prismarine_crystals", "prismarine_shard"],
           ["prismarine_crystals", "prismarine_crystals", "prismarine_crystals"],
           ["prismarine_shard", "prismarine_crystals", "prismarine_shard"]]), "💡")

# ---------------- brewing & misc ----------------
add("paper", "Paper", [], "Three sugar cane make three.",
    craft([["sugar_cane", "sugar_cane", "sugar_cane"]], 3), "📄")
add("book", "Book", ["Essential"], "Three paper + leather.",
    shapeless(["paper", "paper", "paper", "leather"]), "📖")
add("writable_book", "Book and Quill", [], "Book + ink sac + feather.",
    shapeless(["book", "ink_sac", "feather"]), "📓", 1)
add("map", "Map", ["Tools"], "Eight paper + a compass.",
    craft([["paper", "paper", "paper"], ["paper", "compass", "paper"], ["paper", "paper", "paper"]]), "🗺️")
add("glass_bottle", "Glass Bottle", [], "Three glass make three bottles.",
    craft([["glass", None, "glass"], [None, "glass", None]], 3), "🍶")
add("blaze_powder", "Blaze Powder", ["Nether"], "One blaze rod makes two.",
    shapeless(["blaze_rod"], 2), "🟡")
add("ender_eye", "Eye of Ender", ["End"], "Ender pearl + blaze powder. Finds strongholds.",
    shapeless(["ender_pearl", "blaze_powder"]), "🟢")
add("fire_charge", "Fire Charge", ["Nether"], "Blaze powder + coal + gunpowder makes three.",
    shapeless(["blaze_powder", "coal", "gunpowder"], 3), "🔥")
add("fermented_spider_eye", "Fermented Spider Eye", [], "Spider eye + sugar + brown mushroom.",
    shapeless(["spider_eye", "sugar", "brown_mushroom"]), "👁️")
add("firework_star", "Firework Star", [], "Gunpowder + a dye.",
    shapeless(["gunpowder", "red_dye"]), "🎆")
add("firework_rocket", "Firework Rocket", ["Transport"], "Paper + gunpowder. Boosts elytra.",
    shapeless(["paper", "gunpowder"], 3), "🎆")

# ---------------- food ----------------
add("bread", "Bread", ["Food", "Most Used"], "Three wheat.", craft([["wheat", "wheat", "wheat"]]), "🍞")
add("bowl", "Bowl", [], "Three planks make four.",
    craft([["oak_planks", None, "oak_planks"], [None, "oak_planks", None]], 4), "🥣")
add("sugar", "Sugar", ["Food"], "From sugar cane.", shapeless(["sugar_cane"]), "🍬")
add("cookie", "Cookie", ["Food"], "Two wheat + cocoa makes eight.",
    craft([["wheat", "cocoa_beans", "wheat"]], 8), "🍪")
add("cake", "Cake", ["Food"], "Milk, sugar, egg and wheat.",
    craft([["milk_bucket", "milk_bucket", "milk_bucket"], ["sugar", "egg", "sugar"],
           ["wheat", "wheat", "wheat"]]), "🎂", 1)
add("pumpkin_pie", "Pumpkin Pie", ["Food"], "Pumpkin + sugar + egg.",
    shapeless(["pumpkin", "sugar", "egg"]), "🥧")
add("golden_apple", "Golden Apple", ["Food"], "Eight gold ingots around an apple.",
    craft([["gold_ingot", "gold_ingot", "gold_ingot"], ["gold_ingot", "apple", "gold_ingot"],
           ["gold_ingot", "gold_ingot", "gold_ingot"]]), "🍎")
add("golden_carrot", "Golden Carrot", ["Food"], "Eight gold nuggets around a carrot.",
    craft([["gold_nugget", "gold_nugget", "gold_nugget"], ["gold_nugget", "carrot", "gold_nugget"],
           ["gold_nugget", "gold_nugget", "gold_nugget"]]), "🥕")
add("glistering_melon_slice", "Glistering Melon Slice", [], "Melon slice + eight gold nuggets.",
    craft([["gold_nugget", "gold_nugget", "gold_nugget"], ["gold_nugget", "melon_slice", "gold_nugget"],
           ["gold_nugget", "gold_nugget", "gold_nugget"]]), "🍈")
add("melon", "Melon", ["Food"], "Nine melon slices.", block9("melon_slice"), "🍉")
add("pumpkin_seeds", "Pumpkin Seeds", ["Food"], "From a pumpkin.", shapeless(["pumpkin"], 4), "🌱")
add("melon_seeds", "Melon Seeds", ["Food"], "From a melon slice.", shapeless(["melon_slice"]), "🌱")
add("mushroom_stew", "Mushroom Stew", ["Food"], "Bowl + red + brown mushroom.",
    shapeless(["bowl", "red_mushroom", "brown_mushroom"]), "🍲", 1)
add("beetroot_soup", "Beetroot Soup", ["Food"], "Bowl + six beetroot.",
    shapeless(["beetroot", "beetroot", "beetroot", "beetroot", "beetroot", "beetroot", "bowl"]), "🍲", 1)

# ---------------- colours: dyes + families ----------------
add("soul_soil", "Soul Soil", ["Nether"], "Found in soul sand valleys.", gathered(), "🟫")  # ensure defined

COLORS = [("white", "White"), ("orange", "Orange"), ("magenta", "Magenta"), ("light_blue", "Light Blue"),
          ("yellow", "Yellow"), ("lime", "Lime"), ("pink", "Pink"), ("gray", "Gray"),
          ("light_gray", "Light Gray"), ("cyan", "Cyan"), ("purple", "Purple"), ("blue", "Blue"),
          ("brown", "Brown"), ("green", "Green"), ("red", "Red"), ("black", "Black")]

DYE_PRIMARY = {
    "white": shapeless(["bone_meal"]),
    "black": shapeless(["ink_sac"]),
    "blue": shapeless(["lapis_lazuli"]),
    "brown": shapeless(["cocoa_beans"]),
    "red": shapeless(["poppy"]),
    "yellow": shapeless(["dandelion"]),
    "green": furnace("cactus"),
}
DYE_COMBO = {
    "light_blue": ["blue_dye", "white_dye"],
    "lime": ["green_dye", "white_dye"],
    "gray": ["black_dye", "white_dye"],
    "pink": ["red_dye", "white_dye"],
    "orange": ["red_dye", "yellow_dye"],
    "cyan": ["blue_dye", "green_dye"],
    "purple": ["blue_dye", "red_dye"],
    "light_gray": ["gray_dye", "white_dye"],
    "magenta": ["purple_dye", "pink_dye"],
}
# order so combos reference already-defined dyes
DYE_ORDER = ["white", "black", "blue", "brown", "red", "yellow", "green",
             "light_blue", "lime", "gray", "pink", "orange", "cyan", "purple", "light_gray", "magenta"]
LABEL = dict(COLORS)
for c in DYE_ORDER:
    if c in DYE_PRIMARY:
        rec = DYE_PRIMARY[c]
    else:
        rec = shapeless(DYE_COMBO[c], 2)
    add(f"{c}_dye", f"{LABEL[c]} Dye", ["Decoration"], f"{LABEL[c]} dye for colouring blocks and items.",
        rec, "🎨")

for c, label in COLORS:
    dye = f"{c}_dye"
    wool = f"{c}_wool"
    if c == "white":
        add("white_wool", "White Wool", ["Decoration", "Blocks"], "Four string.",
            square4("string", 1), "🧶")
    else:
        add(wool, f"{label} Wool", ["Decoration", "Blocks"], f"{label} wool — dye white wool.",
            shapeless([dye, "white_wool"]), "🧶")
    add(f"{c}_carpet", f"{label} Carpet", ["Decoration", "Blocks"], f"{label} carpet — two wool make three.",
        craft([[wool, wool]], 3), "🟫")
    add(f"{c}_bed", f"{label} Bed", ["Decoration"], f"{label} bed — three wool + three planks.",
        craft([[wool, wool, wool], ["oak_planks", "oak_planks", "oak_planks"]]), "🛏️", 1)
    add(f"{c}_stained_glass", f"{label} Stained Glass", ["Decoration", "Blocks"],
        f"{label} stained glass — eight glass + a dye.",
        craft([["glass", "glass", "glass"], ["glass", dye, "glass"], ["glass", "glass", "glass"]], 8), "🟦")
    add(f"{c}_concrete_powder", f"{label} Concrete Powder", ["Decoration", "Blocks"],
        f"{label} concrete powder — sand + gravel + a dye.",
        shapeless([dye, "sand", "sand", "sand", "sand", "gravel", "gravel", "gravel", "gravel"], 8), "🟫")
    add(f"{c}_terracotta", f"{label} Terracotta", ["Decoration", "Blocks"],
        f"{label} terracotta — eight terracotta + a dye.",
        craft([["terracotta", "terracotta", "terracotta"], ["terracotta", dye, "terracotta"],
               ["terracotta", "terracotta", "terracotta"]], 8), "🟧")

# ---------------- more wood types ----------------
WOODS = [("birch", "Birch"), ("spruce", "Spruce"), ("jungle", "Jungle"), ("acacia", "Acacia"),
         ("dark_oak", "Dark Oak"), ("mangrove", "Mangrove"), ("cherry", "Cherry")]
for w, label in WOODS:
    log = f"{w}_log"; planks = f"{w}_planks"
    add(log, f"{label} Log", ["Blocks"], f"{label} log, chopped from {label.lower()} trees.", gathered(), "🪵")
    add(planks, f"{label} Planks", ["Blocks"], f"{label} planks. One log makes four.", shapeless([log], 4), "🟫")
    add(f"{w}_stairs", f"{label} Stairs", ["Blocks"], f"{label} stairs.", stairs(planks), "🪜")
    add(f"{w}_slab", f"{label} Slab", ["Blocks"], f"{label} slab.", slab(planks), "▬")
    add(f"{w}_fence", f"{label} Fence", ["Blocks"], f"{label} fence.", fence(planks), "🪵")
    add(f"{w}_fence_gate", f"{label} Fence Gate", ["Blocks"], f"{label} fence gate.", fence_gate(planks), "🚧")
    add(f"{w}_door", f"{label} Door", ["Blocks"], f"{label} door.", door(planks), "🚪")
    add(f"{w}_trapdoor", f"{label} Trapdoor", ["Blocks"], f"{label} trapdoor.", trapdoor(planks), "🚪")
    add(f"{w}_boat", f"{label} Boat", ["Transport"], f"{label} boat.", boat(planks), "🛶", 1)

# ---------------- stone & deepslate variants ----------------
for base, label, emo in [("granite", "Granite", "🟥"), ("diorite", "Diorite", "⬜"), ("andesite", "Andesite", "🪨")]:
    add(base, label, ["Blocks"], f"{label}, mined in stony areas.", gathered(), emo)
    add(f"polished_{base}", f"Polished {label}", ["Blocks"], f"Polished {label} — four {label.lower()}.", square4(base, 4), emo)
    add(f"{base}_stairs", f"{label} Stairs", ["Blocks"], f"{label} stairs.", stairs(base), "🪜")
    add(f"{base}_slab", f"{label} Slab", ["Blocks"], f"{label} slab.", slab(base), "▬")
add("deepslate", "Deepslate", ["Blocks"], "Deep stone found far underground.", gathered(), "⬛")
add("cobbled_deepslate", "Cobbled Deepslate", ["Blocks"], "Dropped when mining deepslate.", gathered(), "⬛")
add("polished_deepslate", "Polished Deepslate", ["Blocks"], "Four cobbled deepslate.", square4("cobbled_deepslate", 4), "⬛")
add("deepslate_bricks", "Deepslate Bricks", ["Blocks"], "Four polished deepslate.", square4("polished_deepslate", 4), "⬛")
add("deepslate_tiles", "Deepslate Tiles", ["Blocks"], "Four deepslate bricks.", square4("deepslate_bricks", 4), "⬛")
add("deepslate_brick_stairs", "Deepslate Brick Stairs", ["Blocks"], "Deepslate brick stairs.", stairs("deepslate_bricks"), "🪜")
add("deepslate_brick_slab", "Deepslate Brick Slab", ["Blocks"], "Deepslate brick slab.", slab("deepslate_bricks"), "▬")

# ---------------- nether & blackstone ----------------
add("netherrack", "Netherrack", ["Nether", "Blocks"], "The Nether's ground block.", gathered(), "🟥")
add("nether_brick", "Nether Brick", ["Nether"], "Smelted from netherrack.", furnace("netherrack"), "🧱")
add("nether_bricks", "Nether Bricks", ["Nether", "Blocks"], "Four nether bricks.", square4("nether_brick", 1), "🧱")
add("nether_brick_stairs", "Nether Brick Stairs", ["Nether", "Blocks"], "Nether brick stairs.", stairs("nether_bricks"), "🪜")
add("nether_brick_slab", "Nether Brick Slab", ["Nether", "Blocks"], "Nether brick slab.", slab("nether_bricks"), "▬")
add("blackstone", "Blackstone", ["Nether", "Blocks"], "Dark volcanic stone.", gathered(), "⬛")
add("polished_blackstone", "Polished Blackstone", ["Nether", "Blocks"], "Four blackstone.", square4("blackstone", 4), "⬛")
add("polished_blackstone_bricks", "Polished Blackstone Bricks", ["Nether", "Blocks"], "Four polished blackstone.", square4("polished_blackstone", 4), "⬛")

# ---------------- quartz, sandstone, copper, prismarine ----------------
add("smooth_quartz", "Smooth Quartz Block", ["Blocks"], "Smelted from a quartz block.", furnace("quartz_block"), "◻️")
add("quartz_bricks", "Quartz Bricks", ["Blocks"], "Four quartz blocks.", square4("quartz_block", 4), "◻️")
add("quartz_pillar", "Quartz Pillar", ["Blocks"], "Two quartz blocks.", craft([["quartz_block"], ["quartz_block"]], 2), "◻️")
add("quartz_stairs", "Quartz Stairs", ["Blocks"], "Quartz stairs.", stairs("quartz_block"), "🪜")
add("quartz_slab", "Quartz Slab", ["Blocks"], "Quartz slab.", slab("quartz_block"), "▬")
add("smooth_sandstone", "Smooth Sandstone", ["Blocks"], "Smelted from sandstone.", furnace("sandstone"), "🟨")
add("cut_sandstone", "Cut Sandstone", ["Blocks"], "Four sandstone.", square4("sandstone", 4), "🟨")
add("sandstone_stairs", "Sandstone Stairs", ["Blocks"], "Sandstone stairs.", stairs("sandstone"), "🪜")
add("sandstone_slab", "Sandstone Slab", ["Blocks"], "Sandstone slab.", slab("sandstone"), "▬")
add("cut_copper", "Cut Copper", ["Blocks"], "Four copper blocks.", square4("copper_block", 4), "🟧")
add("cut_copper_stairs", "Cut Copper Stairs", ["Blocks"], "Cut copper stairs.", stairs("cut_copper"), "🪜")
add("cut_copper_slab", "Cut Copper Slab", ["Blocks"], "Cut copper slab.", slab("cut_copper"), "▬")
add("prismarine_bricks", "Prismarine Bricks", ["Blocks"], "Nine prismarine shards.", block9("prismarine_shard"), "🔷")

# ---------------- honey & misc ----------------
add("honey_bottle", "Honey Bottle", ["Food"], "Bottled from a beehive.", gathered(), "🍯")
add("honey_block", "Honey Block", ["Redstone", "Blocks"], "Four honey bottles.", square4("honey_bottle", 1), "🍯")
add("honeycomb_block", "Honeycomb Block", ["Blocks"], "Four honeycomb.", square4("honeycomb", 1), "🍯")

# =====================================================================
# EXTENDED CATALOG (26.2) — complete the craftable item set.
# add() dedupes by id, so re-listing an already-defined id is a no-op;
# validation still checks that every referenced ingredient exists.
# =====================================================================

def button(m):          return shapeless([m])
def pressure_plate(m):  return craft([[m, m]])
def hanging_sign(strip): return craft([["chain", None, "chain"], [strip, strip, strip],
                                       [strip, strip, strip]], 6)

# ---- extra gathered / raw materials referenced below ----
GATH2 = [
    ("dirt", "Dirt", ["Blocks"], "🟫"),
    ("red_sand", "Red Sand", ["Blocks"], "🟧"),
    ("end_stone", "End Stone", ["End", "Blocks"], "🪨"),
    ("basalt", "Basalt", ["Nether", "Blocks"], "🪨"),
    ("moss_block", "Moss Block", ["Blocks"], "🟩"),
    ("chorus_fruit", "Chorus Fruit", ["End", "Food"], "🟣"),
    ("crimson_stem", "Crimson Stem", ["Nether", "Blocks"], "🟥"),
    ("warped_stem", "Warped Stem", ["Nether", "Blocks"], "🟦"),
    ("stripped_crimson_stem", "Stripped Crimson Stem", ["Nether", "Blocks"], "🟥"),
    ("stripped_warped_stem", "Stripped Warped Stem", ["Nether", "Blocks"], "🟦"),
    ("crying_obsidian", "Crying Obsidian", ["Nether", "Blocks"], "🟪"),
    ("ghast_tear", "Ghast Tear", ["Nether"], "💧"),
    ("wet_sponge", "Wet Sponge", ["Blocks"], "🧽"),
    ("pointed_dripstone", "Pointed Dripstone", ["Blocks"], "🪨"),
    ("nether_wart", "Nether Wart", ["Nether"], "🔴"),
    ("rabbit", "Raw Rabbit", ["Food"], "🍖"),
    ("pale_oak_log", "Pale Oak Log", ["Blocks"], "🪵"),
]
for gid, gname, gcats, gemo in GATH2:
    add(gid, gname, gcats, f"{gname} — gathered or mined in the world.", gathered(), gemo)

# ---- complete every overworld wood set ----
FULL_WOODS = [("oak", "Oak"), ("birch", "Birch"), ("spruce", "Spruce"), ("jungle", "Jungle"),
              ("acacia", "Acacia"), ("dark_oak", "Dark Oak"), ("mangrove", "Mangrove"),
              ("cherry", "Cherry"), ("pale_oak", "Pale Oak")]
for w, label in FULL_WOODS:
    log = f"{w}_log"; planks = f"{w}_planks"; strip = f"stripped_{w}_log"
    add(log, f"{label} Log", ["Blocks"], f"{label} log.", gathered(), "🪵")
    add(strip, f"Stripped {label} Log", ["Blocks"], "Strip a log with an axe.", gathered(), "🪵")
    add(f"{w}_wood", f"{label} Wood", ["Blocks"], "All-bark block. Four logs make three.",
        craft([[log, log], [log, log]], 3), "🪵")
    add(f"stripped_{w}_wood", f"Stripped {label} Wood", ["Blocks"], "Four stripped logs make three.",
        craft([[strip, strip], [strip, strip]], 3), "🪵")
    add(planks, f"{label} Planks", ["Blocks"], "One log makes four planks.", shapeless([log], 4), "🟫")
    add(f"{w}_stairs", f"{label} Stairs", ["Blocks"], f"{label} stairs.", stairs(planks), "🪜")
    add(f"{w}_slab", f"{label} Slab", ["Blocks"], f"{label} slab.", slab(planks), "▬")
    add(f"{w}_fence", f"{label} Fence", ["Blocks"], f"{label} fence.", fence(planks), "🪵")
    add(f"{w}_fence_gate", f"{label} Fence Gate", ["Blocks"], f"{label} fence gate.", fence_gate(planks), "🚧")
    add(f"{w}_door", f"{label} Door", ["Blocks"], f"{label} door — six planks make three.", door(planks), "🚪")
    add(f"{w}_trapdoor", f"{label} Trapdoor", ["Blocks"], f"{label} trapdoor.", trapdoor(planks), "🚪")
    add(f"{w}_button", f"{label} Button", ["Redstone"], f"{label} button.", button(planks), "🔘")
    add(f"{w}_pressure_plate", f"{label} Pressure Plate", ["Redstone"], f"{label} pressure plate.",
        pressure_plate(planks), "⬛")
    add(f"{w}_sign", f"{label} Sign", ["Decoration"], f"{label} sign — six planks + a stick make three.",
        sign(planks), "🪧")
    add(f"{w}_hanging_sign", f"{label} Hanging Sign", ["Decoration"],
        "Two chains + six stripped logs make six.", hanging_sign(strip), "🪧")
    add(f"{w}_boat", f"{label} Boat", ["Transport"], f"{label} boat.", boat(planks), "🛶", 1)
    add(f"{w}_chest_boat", f"{label} Boat with Chest", ["Transport"], "Boat + chest.",
        shapeless(["chest", f"{w}_boat"]), "🛶", 1)

# ---- nether "woods" (crimson / warped): stems, no boats ----
for w, label, emo in [("crimson", "Crimson", "🟥"), ("warped", "Warped", "🟦")]:
    stem = f"{w}_stem"; planks = f"{w}_planks"; strip = f"stripped_{w}_stem"
    add(f"{w}_hyphae", f"{label} Hyphae", ["Nether", "Blocks"], "Four stems make three.",
        craft([[stem, stem], [stem, stem]], 3), emo)
    add(f"stripped_{w}_hyphae", f"Stripped {label} Hyphae", ["Nether", "Blocks"],
        "Four stripped stems make three.", craft([[strip, strip], [strip, strip]], 3), emo)
    add(planks, f"{label} Planks", ["Nether", "Blocks"], "One stem makes four planks.",
        shapeless([stem], 4), "🟫")
    add(f"{w}_stairs", f"{label} Stairs", ["Nether", "Blocks"], f"{label} stairs.", stairs(planks), "🪜")
    add(f"{w}_slab", f"{label} Slab", ["Nether", "Blocks"], f"{label} slab.", slab(planks), "▬")
    add(f"{w}_fence", f"{label} Fence", ["Nether", "Blocks"], f"{label} fence.", fence(planks), "🪵")
    add(f"{w}_fence_gate", f"{label} Fence Gate", ["Nether", "Blocks"], f"{label} fence gate.",
        fence_gate(planks), "🚧")
    add(f"{w}_door", f"{label} Door", ["Nether", "Blocks"], f"{label} door.", door(planks), "🚪")
    add(f"{w}_trapdoor", f"{label} Trapdoor", ["Nether", "Blocks"], f"{label} trapdoor.", trapdoor(planks), "🚪")
    add(f"{w}_button", f"{label} Button", ["Redstone"], f"{label} button.", button(planks), "🔘")
    add(f"{w}_pressure_plate", f"{label} Pressure Plate", ["Redstone"], f"{label} pressure plate.",
        pressure_plate(planks), "⬛")
    add(f"{w}_sign", f"{label} Sign", ["Decoration"], f"{label} sign.", sign(planks), "🪧")
    add(f"{w}_hanging_sign", f"{label} Hanging Sign", ["Decoration"], "Chains + stripped stems.",
        hanging_sign(strip), "🪧")

# ---- bamboo wood set ----
add("bamboo_block", "Block of Bamboo", ["Blocks"], "Nine bamboo.", block9("bamboo"), "🎍")
add("stripped_bamboo_block", "Stripped Block of Bamboo", ["Blocks"], "Strip with an axe.", gathered(), "🎍")
add("bamboo_planks", "Bamboo Planks", ["Blocks"], "A block of bamboo makes two planks.",
    shapeless(["bamboo_block"], 2), "🟫")
add("bamboo_slab", "Bamboo Slab", ["Blocks"], "Bamboo slab.", slab("bamboo_planks"), "▬")
add("bamboo_stairs", "Bamboo Stairs", ["Blocks"], "Bamboo stairs.", stairs("bamboo_planks"), "🪜")
add("bamboo_mosaic", "Bamboo Mosaic", ["Blocks"], "Two bamboo slabs.",
    craft([["bamboo_slab"], ["bamboo_slab"]], 1), "🟫")
add("bamboo_mosaic_slab", "Bamboo Mosaic Slab", ["Blocks"], "Slab.", slab("bamboo_mosaic"), "▬")
add("bamboo_mosaic_stairs", "Bamboo Mosaic Stairs", ["Blocks"], "Stairs.", stairs("bamboo_mosaic"), "🪜")
add("bamboo_fence", "Bamboo Fence", ["Blocks"], "Bamboo fence.", fence("bamboo_planks"), "🪵")
add("bamboo_fence_gate", "Bamboo Fence Gate", ["Blocks"], "Bamboo fence gate.", fence_gate("bamboo_planks"), "🚧")
add("bamboo_door", "Bamboo Door", ["Blocks"], "Bamboo door.", door("bamboo_planks"), "🚪")
add("bamboo_trapdoor", "Bamboo Trapdoor", ["Blocks"], "Bamboo trapdoor.", trapdoor("bamboo_planks"), "🚪")
add("bamboo_button", "Bamboo Button", ["Redstone"], "Bamboo button.", button("bamboo_planks"), "🔘")
add("bamboo_pressure_plate", "Bamboo Pressure Plate", ["Redstone"], "Bamboo pressure plate.",
    pressure_plate("bamboo_planks"), "⬛")
add("bamboo_sign", "Bamboo Sign", ["Decoration"], "Bamboo sign.", sign("bamboo_planks"), "🪧")
add("bamboo_hanging_sign", "Bamboo Hanging Sign", ["Decoration"], "Chains + stripped bamboo.",
    hanging_sign("stripped_bamboo_block"), "🪧")
add("bamboo_raft", "Bamboo Raft", ["Transport"], "Bamboo boat.", boat("bamboo_planks"), "🛶", 1)
add("bamboo_chest_raft", "Bamboo Raft with Chest", ["Transport"], "Raft + chest.",
    shapeless(["chest", "bamboo_raft"]), "🛶", 1)

# ---- colour families: banners, candles, panes, shulker boxes, glazed terracotta ----
for c, label in COLORS:
    dye = f"{c}_dye"; wool = f"{c}_wool"
    add(f"{c}_banner", f"{label} Banner", ["Decoration"], "Six wool + a stick.",
        craft([[wool, wool, wool], [wool, wool, wool], [None, "stick", None]], 1), "🚩", 16)
    add(f"{c}_candle", f"{label} Candle", ["Decoration"], "Candle + dye.",
        shapeless(["candle", dye]), "🕯️")
    add(f"{c}_stained_glass_pane", f"{label} Stained Glass Pane", ["Decoration", "Blocks"],
        "Six stained glass make sixteen panes.",
        craft([[f"{c}_stained_glass"] * 3, [f"{c}_stained_glass"] * 3], 16), "🪟")
    add(f"{c}_shulker_box", f"{label} Shulker Box", ["Blocks"], "Dye a shulker box.",
        shapeless(["shulker_box", dye]), "🟪", 1)
    add(f"{c}_glazed_terracotta", f"{label} Glazed Terracotta", ["Decoration", "Blocks"],
        "Smelt dyed terracotta.", furnace(f"{c}_terracotta"), "🟧")

# ---- stone brick family ----
add("chiseled_stone_bricks", "Chiseled Stone Bricks", ["Blocks"], "Two stone brick slabs.",
    craft([["stone_brick_slab"], ["stone_brick_slab"]], 1), "🧱")
add("cracked_stone_bricks", "Cracked Stone Bricks", ["Blocks"], "Smelt stone bricks.",
    furnace("stone_bricks"), "🧱")
add("moss_carpet", "Moss Carpet", ["Decoration", "Blocks"], "Two moss blocks make three.",
    craft([["moss_block", "moss_block"]], 3), "🟩")
add("mossy_cobblestone", "Mossy Cobblestone", ["Blocks"], "Cobblestone + moss block.",
    shapeless(["cobblestone", "moss_block"]), "🪨")
add("mossy_stone_bricks", "Mossy Stone Bricks", ["Blocks"], "Stone bricks + moss block.",
    shapeless(["stone_bricks", "moss_block"]), "🧱")

# ---- sandstone + red sandstone ----
add("chiseled_sandstone", "Chiseled Sandstone", ["Blocks"], "Two sandstone slabs.",
    craft([["sandstone_slab"], ["sandstone_slab"]], 1), "🟨")
add("red_sandstone", "Red Sandstone", ["Blocks"], "Four red sand.", square4("red_sand", 1), "🟧")
add("chiseled_red_sandstone", "Chiseled Red Sandstone", ["Blocks"], "Two red sandstone slabs.",
    craft([["red_sandstone_slab"], ["red_sandstone_slab"]], 1), "🟧")
add("cut_red_sandstone", "Cut Red Sandstone", ["Blocks"], "Four red sandstone.", square4("red_sandstone", 4), "🟧")
add("smooth_red_sandstone", "Smooth Red Sandstone", ["Blocks"], "Smelt red sandstone.",
    furnace("red_sandstone"), "🟧")

# ---- deepslate variants ----
add("chiseled_deepslate", "Chiseled Deepslate", ["Blocks"], "Two cobbled deepslate slabs.",
    craft([["cobbled_deepslate_slab"], ["cobbled_deepslate_slab"]], 1), "⬛")
add("cracked_deepslate_bricks", "Cracked Deepslate Bricks", ["Blocks"], "Smelt deepslate bricks.",
    furnace("deepslate_bricks"), "⬛")
add("cracked_deepslate_tiles", "Cracked Deepslate Tiles", ["Blocks"], "Smelt deepslate tiles.",
    furnace("deepslate_tiles"), "⬛")

# ---- blackstone ----
add("chiseled_polished_blackstone", "Chiseled Polished Blackstone", ["Nether", "Blocks"],
    "Two polished blackstone slabs.", craft([["polished_blackstone_slab"], ["polished_blackstone_slab"]], 1), "⬛")
add("cracked_polished_blackstone_bricks", "Cracked Polished Blackstone Bricks", ["Nether", "Blocks"],
    "Smelt polished blackstone bricks.", furnace("polished_blackstone_bricks"), "⬛")
add("polished_blackstone_button", "Polished Blackstone Button", ["Redstone"], "Momentary power pulse.",
    button("polished_blackstone"), "🔘")
add("polished_blackstone_pressure_plate", "Polished Blackstone Pressure Plate", ["Redstone"],
    "Triggers when stepped on.", pressure_plate("polished_blackstone"), "⬛")

# ---- nether bricks family ----
add("nether_brick_fence", "Nether Brick Fence", ["Nether", "Blocks"], "Nether bricks + nether brick.",
    craft([["nether_bricks", "nether_brick", "nether_bricks"],
           ["nether_bricks", "nether_brick", "nether_bricks"]], 6), "🧱")
add("chiseled_nether_bricks", "Chiseled Nether Bricks", ["Nether", "Blocks"], "Two nether brick slabs.",
    craft([["nether_brick_slab"], ["nether_brick_slab"]], 1), "🧱")
add("cracked_nether_bricks", "Cracked Nether Bricks", ["Nether", "Blocks"], "Smelt nether bricks.",
    furnace("nether_bricks"), "🧱")
add("nether_wart_block", "Nether Wart Block", ["Nether", "Blocks"], "Nine nether wart.",
    block9("nether_wart"), "🔴")
add("red_nether_bricks", "Red Nether Bricks", ["Nether", "Blocks"], "Two nether wart + two nether brick.",
    craft([["nether_wart", "nether_brick"], ["nether_brick", "nether_wart"]], 2), "🟥")

# ---- End ----
add("end_stone_bricks", "End Stone Bricks", ["End", "Blocks"], "Four end stone.", square4("end_stone", 4), "🟨")
add("popped_chorus_fruit", "Popped Chorus Fruit", ["End"], "Smelt chorus fruit.", furnace("chorus_fruit"), "🟣")
add("purpur_block", "Purpur Block", ["End", "Blocks"], "Four popped chorus fruit.",
    square4("popped_chorus_fruit", 4), "🟪")
add("purpur_pillar", "Purpur Pillar", ["End", "Blocks"], "Two purpur slabs.",
    craft([["purpur_slab"], ["purpur_slab"]], 1), "🟪")
add("end_rod", "End Rod", ["Decoration"], "Blaze rod + popped chorus fruit make four.",
    craft([["popped_chorus_fruit"], ["blaze_rod"]], 4), "🪄")

# ---- prismarine ----
add("dark_prismarine", "Dark Prismarine", ["Blocks"], "Eight prismarine shards + an ink sac.",
    craft([["prismarine_shard", "prismarine_shard", "prismarine_shard"],
           ["prismarine_shard", "ink_sac", "prismarine_shard"],
           ["prismarine_shard", "prismarine_shard", "prismarine_shard"]], 1), "🔷")

# ---- quartz ----
add("chiseled_quartz_block", "Chiseled Quartz Block", ["Blocks"], "Two quartz slabs.",
    craft([["quartz_slab"], ["quartz_slab"]], 1), "◻️")
add("smooth_quartz_stairs", "Smooth Quartz Stairs", ["Blocks"], "Stairs.", stairs("smooth_quartz"), "🪜")
add("smooth_quartz_slab", "Smooth Quartz Slab", ["Blocks"], "Slab.", slab("smooth_quartz"), "▬")

# ---- basalt / dirt / dripstone / amethyst ----
add("polished_basalt", "Polished Basalt", ["Nether", "Blocks"], "Four basalt.", square4("basalt", 4), "🪨")
add("smooth_basalt", "Smooth Basalt", ["Nether", "Blocks"], "Smelt basalt.", furnace("basalt"), "🪨")
add("coarse_dirt", "Coarse Dirt", ["Blocks"], "Two dirt + two gravel make four.",
    craft([["dirt", "gravel"], ["gravel", "dirt"]], 4), "🟫")
add("dripstone_block", "Dripstone Block", ["Blocks"], "Four pointed dripstone.",
    square4("pointed_dripstone", 1), "🪨")
add("amethyst_block", "Block of Amethyst", ["Blocks"], "Four amethyst shards.",
    square4("amethyst_shard", 1), "🟪")
add("tinted_glass", "Tinted Glass", ["Blocks"], "Glass + four amethyst shards make two.",
    craft([[None, "amethyst_shard", None], ["amethyst_shard", "glass", "amethyst_shard"],
           [None, "amethyst_shard", None]], 2), "🔲")

# ---- mud family ----
add("mud", "Mud", ["Blocks"], "Use a water bottle on dirt.", gathered(), "🟫")
add("packed_mud", "Packed Mud", ["Blocks"], "Mud + wheat.", shapeless(["mud", "wheat"]), "🟫")
add("mud_bricks", "Mud Bricks", ["Blocks"], "Four packed mud.", square4("packed_mud", 4), "🧱")

# ---- copper family (1.21) ----
add("iron_door", "Iron Door", ["Blocks", "Redstone"], "Six iron ingots make three.", door("iron_ingot"), "🚪")
add("iron_trapdoor", "Iron Trapdoor", ["Blocks", "Redstone"], "Four iron ingots.",
    square4("iron_ingot", 1), "🚪")
add("copper_door", "Copper Door", ["Blocks"], "Six copper ingots make three.", door("copper_ingot"), "🚪")
add("copper_trapdoor", "Copper Trapdoor", ["Blocks"], "Six copper ingots make two.",
    trapdoor("copper_ingot"), "🚪")
add("copper_grate", "Copper Grate", ["Blocks"], "Four blocks of copper make four.",
    craft([[None, "copper_block", None], ["copper_block", None, "copper_block"],
           [None, "copper_block", None]], 4), "🔳")
add("copper_bulb", "Copper Bulb", ["Redstone", "Blocks"], "Three copper blocks + blaze rod + redstone make four.",
    craft([[None, "copper_block", None], ["copper_block", "blaze_rod", "copper_block"],
           [None, "redstone", None]], 4), "💡")
add("chiseled_copper", "Chiseled Copper", ["Blocks"], "Two cut copper slabs.",
    craft([["cut_copper_slab"], ["cut_copper_slab"]], 1), "🟧")
for base in ["copper_block", "cut_copper", "cut_copper_stairs", "cut_copper_slab", "chiseled_copper",
             "copper_grate", "copper_bulb", "copper_door", "copper_trapdoor"]:
    add(f"waxed_{base}", "Waxed " + base.replace("_", " ").title(), ["Blocks"],
        "Copper + honeycomb — never oxidizes.", shapeless([base, "honeycomb"]), "🟧",
        1 if base in ("copper_door", "copper_trapdoor") else 64)

# ---- utility / decoration ----
add("respawn_anchor", "Respawn Anchor", ["Nether", "Blocks"], "Six crying obsidian + three glowstone.",
    craft([["crying_obsidian", "crying_obsidian", "crying_obsidian"],
           ["glowstone", "glowstone", "glowstone"],
           ["crying_obsidian", "crying_obsidian", "crying_obsidian"]], 1), "🔆")
add("lodestone", "Lodestone", ["Blocks"], "Eight chiseled stone bricks + a netherite ingot.",
    craft([["chiseled_stone_bricks", "chiseled_stone_bricks", "chiseled_stone_bricks"],
           ["chiseled_stone_bricks", "netherite_ingot", "chiseled_stone_bricks"],
           ["chiseled_stone_bricks", "chiseled_stone_bricks", "chiseled_stone_bricks"]], 1), "🧭")
add("end_crystal", "End Crystal", ["End"], "Seven glass + eye of ender + ghast tear.",
    craft([["glass", "glass", "glass"], ["glass", "ender_eye", "glass"],
           ["glass", "ghast_tear", "glass"]], 1), "🔮", 1)
add("sponge", "Sponge", ["Blocks"], "Smelt a wet sponge.", furnace("wet_sponge"), "🧽")
add("decorated_pot", "Decorated Pot", ["Decoration"], "Four bricks (or pottery sherds).",
    craft([[None, "brick", None], ["brick", None, "brick"], [None, "brick", None]], 1), "🏺", 1)
add("soul_lantern", "Soul Lantern", ["Nether"], "Soul torch + eight iron nuggets.",
    craft([["iron_nugget", "iron_nugget", "iron_nugget"], ["iron_nugget", "soul_torch", "iron_nugget"],
           ["iron_nugget", "iron_nugget", "iron_nugget"]], 1), "🏮")
add("soul_campfire", "Soul Campfire", ["Nether"], "Sticks + soul soil + logs.",
    craft([[None, "stick", None], ["stick", "soul_soil", "stick"],
           ["oak_log", "oak_log", "oak_log"]], 1), "🔥")
add("spectral_arrow", "Spectral Arrow", ["Combat"], "Four glowstone dust + an arrow make two.",
    craft([[None, "glowstone_dust", None], ["glowstone_dust", "arrow", "glowstone_dust"],
           [None, "glowstone_dust", None]], 2), "🎯")

# ---- extra food ----
add("cooked_rabbit", "Cooked Rabbit", ["Food"], "Cook raw rabbit.", furnace("rabbit"), "🍖")
add("rabbit_stew", "Rabbit Stew", ["Food"], "Bowl, cooked rabbit, carrot, baked potato, mushroom.",
    shapeless(["bowl", "cooked_rabbit", "carrot", "baked_potato", "red_mushroom"]), "🍲", 1)
add("suspicious_stew", "Suspicious Stew", ["Food"], "Bowl + red + brown mushroom + a flower.",
    shapeless(["bowl", "red_mushroom", "brown_mushroom", "dandelion"]), "🍲", 1)

# ---- stairs / slabs / walls for every stone-like block (add() dedupes) ----
SSW = [
    ("granite", "granite", "Granite", ["Blocks"], True),
    ("diorite", "diorite", "Diorite", ["Blocks"], True),
    ("andesite", "andesite", "Andesite", ["Blocks"], True),
    ("polished_granite", "polished_granite", "Polished Granite", ["Blocks"], False),
    ("polished_diorite", "polished_diorite", "Polished Diorite", ["Blocks"], False),
    ("polished_andesite", "polished_andesite", "Polished Andesite", ["Blocks"], False),
    ("cobblestone", "cobblestone", "Cobblestone", ["Blocks"], True),
    ("mossy_cobblestone", "mossy_cobblestone", "Mossy Cobblestone", ["Blocks"], True),
    ("stone_bricks", "stone_brick", "Stone Brick", ["Blocks"], True),
    ("mossy_stone_bricks", "mossy_stone_brick", "Mossy Stone Brick", ["Blocks"], True),
    ("bricks", "brick", "Brick", ["Blocks"], True),
    ("sandstone", "sandstone", "Sandstone", ["Blocks"], True),
    ("smooth_sandstone", "smooth_sandstone", "Smooth Sandstone", ["Blocks"], False),
    ("red_sandstone", "red_sandstone", "Red Sandstone", ["Blocks"], True),
    ("smooth_red_sandstone", "smooth_red_sandstone", "Smooth Red Sandstone", ["Blocks"], False),
    ("prismarine", "prismarine", "Prismarine", ["Blocks"], True),
    ("prismarine_bricks", "prismarine_brick", "Prismarine Brick", ["Blocks"], False),
    ("dark_prismarine", "dark_prismarine", "Dark Prismarine", ["Blocks"], False),
    ("nether_bricks", "nether_brick", "Nether Brick", ["Nether", "Blocks"], True),
    ("red_nether_bricks", "red_nether_brick", "Red Nether Brick", ["Nether", "Blocks"], True),
    ("blackstone", "blackstone", "Blackstone", ["Nether", "Blocks"], True),
    ("polished_blackstone", "polished_blackstone", "Polished Blackstone", ["Nether", "Blocks"], True),
    ("polished_blackstone_bricks", "polished_blackstone_brick", "Polished Blackstone Brick",
     ["Nether", "Blocks"], True),
    ("cobbled_deepslate", "cobbled_deepslate", "Cobbled Deepslate", ["Blocks"], True),
    ("polished_deepslate", "polished_deepslate", "Polished Deepslate", ["Blocks"], True),
    ("deepslate_bricks", "deepslate_brick", "Deepslate Brick", ["Blocks"], True),
    ("deepslate_tiles", "deepslate_tile", "Deepslate Tile", ["Blocks"], True),
    ("end_stone_bricks", "end_stone_brick", "End Stone Brick", ["End", "Blocks"], True),
    ("mud_bricks", "mud_brick", "Mud Brick", ["Blocks"], True),
    ("purpur_block", "purpur", "Purpur", ["End", "Blocks"], False),
]
for mat, pre, label, cats, want_wall in SSW:
    add(f"{pre}_stairs", f"{label} Stairs", cats, f"{label} stairs.", stairs(mat), "🪜")
    add(f"{pre}_slab", f"{label} Slab", cats, f"{label} slab.", slab(mat), "▬")
    if want_wall:
        add(f"{pre}_wall", f"{label} Wall", cats, f"{label} wall.", wall(mat), "🧱")


# ---- tuff family (1.21) ----
add("tuff", "Tuff", ["Blocks"], "A volcanic stone found underground.", gathered(), "🪨")
add("polished_tuff", "Polished Tuff", ["Blocks"], "Four tuff.", square4("tuff", 4), "🪨")
add("tuff_bricks", "Tuff Bricks", ["Blocks"], "Four polished tuff.", square4("polished_tuff", 4), "🧱")
add("chiseled_tuff", "Chiseled Tuff", ["Blocks"], "Two tuff slabs.",
    craft([["tuff_slab"], ["tuff_slab"]], 1), "🪨")
add("chiseled_tuff_bricks", "Chiseled Tuff Bricks", ["Blocks"], "Two tuff brick slabs.",
    craft([["tuff_brick_slab"], ["tuff_brick_slab"]], 1), "🧱")
for pre, mat, label in [("tuff", "tuff", "Tuff"), ("polished_tuff", "polished_tuff", "Polished Tuff"),
                        ("tuff_brick", "tuff_bricks", "Tuff Brick")]:
    add(f"{pre}_stairs", f"{label} Stairs", ["Blocks"], f"{label} stairs.", stairs(mat), "🪜")
    add(f"{pre}_slab", f"{label} Slab", ["Blocks"], f"{label} slab.", slab(mat), "▬")
    add(f"{pre}_wall", f"{label} Wall", ["Blocks"], f"{label} wall.", wall(mat), "🧱")

# ---- 1.21 combat / utility ----
add("heavy_core", "Heavy Core", ["Combat"], "Found in ominous trial vaults.", gathered(), "⚫", 1)
add("breeze_rod", "Breeze Rod", ["Combat", "Nether"], "Dropped by the Breeze.", gathered(), "🌬️")
add("mace", "Mace", ["Combat"], "Heavy core + breeze rod. A devastating slam attack.",
    craft([["heavy_core"], ["breeze_rod"]], 1), "🔨", 1)
add("echo_shard", "Echo Shard", [], "Found in ancient city chests.", gathered(), "🔊")
add("recovery_compass", "Recovery Compass", ["Tools"], "Eight echo shards + a compass. Points to your last death.",
    craft([["echo_shard", "echo_shard", "echo_shard"], ["echo_shard", "compass", "echo_shard"],
           ["echo_shard", "echo_shard", "echo_shard"]], 1), "🧭", 1)


# ---------------- finalize ----------------
# official names (en/fr) + French descriptions from the game's 26.2 lang files
import urllib.request


def _load_lang(fname, url):
    p = Path(__file__).resolve().parent / fname
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    req = urllib.request.Request(url, headers={"User-Agent": "MCcompanion/1.0"})
    d = json.load(urllib.request.urlopen(req, timeout=30))
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    return d


_LB = "https://raw.githubusercontent.com/InventivetalentDev/minecraft-assets/26.2/assets/minecraft/lang/"
try:
    _fr = _load_lang("_lang_fr.json", _LB + "fr_fr.json")
    _en = _load_lang("_lang_en.json", _LB + "en_us.json")

    def _strip(d):
        m = {}
        for k, v in d.items():
            if k.startswith("item.minecraft.") or k.startswith("block.minecraft."):
                m[k.split("minecraft.")[1]] = v
        return m
    FRM, ENM = _strip(_fr), _strip(_en)
except Exception as e:
    FRM, ENM = {}, {}
    print("[warn] could not load lang files:", e)

for it in items:
    iid = it["id"]
    if iid in ENM:
        it["name"] = ENM[iid]
    it["name_fr"] = FRM.get(iid, it["name"])
    r = it["recipe"]; y = r.get("yields", 1); nf = it["name_fr"]
    tp = r["type"]
    if tp == "gathered":
        it["description_fr"] = f"{nf} — se récupère ou se mine dans le monde."
    elif tp == "furnace":
        it["description_fr"] = "S'obtient en le faisant fondre au fourneau."
    elif tp == "shapeless":
        it["description_fr"] = "Assemblage libre sur l'établi" + (f" (donne {y})." if y > 1 else ".")
    else:
        it["description_fr"] = "Se fabrique sur l'établi" + (f" (donne {y})." if y > 1 else ".")

# attach already-downloaded icons
for it in items:
    p = ICONS / f"{it['id']}.png"
    if p.exists():
        it["icon"] = f"icons/{it['id']}.png"

# validation: every referenced id must be a defined item
defined = {it["id"] for it in items}
referenced = set()
for it in items:
    for row in it["recipe"].get("grid", []):
        for cell in row:
            if cell:
                referenced.add(cell)
    referenced.update(it["recipe"].get("ingredients", {}).keys())
missing = sorted(referenced - defined)

OUT.write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Wrote {OUT.relative_to(ROOT)} with {len(items)} items.")
if missing:
    print(f"\n[WARNING] {len(missing)} referenced id(s) are NOT defined as items:")
    for m in missing:
        print("   -", m)
else:
    print("Validation OK — every referenced ingredient is a defined item.")
