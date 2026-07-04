"""Clip definitions for "Day in the Life of a Billionaire" — 9 viral shorts.

Hook patterns used (per wiki viral-content-formulas):
  MONEY+TIMEFRAME: clips 1, 6
  WHY/HARSH TRUTH: clips 2, 3, 4, 9
  CONTRARIAN: clips 5, 8
  THIS/VISUAL: clip 7

Each clip has value-add overlays (ADR 0008): timed icons/badges/flashes/text.
"""

CLIPS = [
    # ── 01: MONEY+TIMEFRAME — the origin story ──
    {
        "id": "01-12k-to-billion",
        "start": 335.0,
        "duration": 44.0,
        "hook": "FROM $12K TO BILLIONAIRE",
        "speaker": "Andy Frisella",
        "punchlines": {"12000", "$12", "started", "$7", "seven", "58", "380", "695", "month", "10", "years", "money", "broke", "store", "rich"},
        "overlays": [
            {"name": "icon_money", "ts": 1.0, "x": 780, "y": 200, "dur": 3.0, "scale": 1.4},
            {"name": "badge_money", "ts": 4.0, "x": 250, "y": 500, "dur": 2.5},
            {"name": "flash_green", "ts": 8.0, "x": 0, "y": 0, "dur": 0.2},
            {"name": "icon_warning", "ts": 16.0, "x": 100, "y": 400, "dur": 2.5},
            {"name": "text_fact", "ts": 20.0, "x": 140, "y": 650, "dur": 2.0},
            {"name": "icon_money", "ts": 28.0, "x": 800, "y": 300, "dur": 3.0, "scale": 1.5},
            {"name": "flash_yellow", "ts": 35.0, "x": 0, "y": 0, "dur": 0.2},
            {"name": "text_huge", "ts": 38.0, "x": 140, "y": 600, "dur": 2.5},
        ],
    },
    # ── 02: WHY/HARSH TRUTH — firing people ──
    {
        "id": "02-fire-them",
        "start": 140.0,
        "duration": 30.0,
        "hook": "WHY YOU MUST FIRE PEOPLE",
        "speaker": "Andy Frisella",
        "punchlines": {"fire", "firing", "holding", "back", "great", "realize", "hard", "younger", "business"},
        "overlays": [
            {"name": "icon_warning", "ts": 1.0, "x": 100, "y": 300, "dur": 3.0},
            {"name": "badge_warning", "ts": 4.0, "x": 250, "y": 480, "dur": 2.5},
            {"name": "flash_red", "ts": 8.0, "x": 0, "y": 0, "dur": 0.2},
            {"name": "text_truth", "ts": 14.0, "x": 140, "y": 650, "dur": 2.5},
            {"name": "icon_bolt", "ts": 22.0, "x": 800, "y": 350, "dur": 2.5, "scale": 1.2},
        ],
    },
    # ── 03: WHY/HARSH TRUTH — discipline as a bank account ──
    {
        "id": "03-discipline-bank",
        "start": 293.0,
        "duration": 33.0,
        "hook": "DISCIPLINE IS A BANK ACCOUNT",
        "speaker": "Andy Frisella",
        "punchlines": {"discipline", "bank", "account", "deposits", "withdrawals", "trash", "hurting", "invest", "standard", "culture"},
        "overlays": [
            {"name": "icon_idea", "ts": 1.0, "x": 780, "y": 200, "dur": 3.0, "scale": 1.3},
            {"name": "badge_key", "ts": 4.5, "x": 250, "y": 480, "dur": 2.5},
            {"name": "icon_money", "ts": 12.0, "x": 800, "y": 300, "dur": 3.0, "scale": 1.3},
            {"name": "text_fact", "ts": 18.0, "x": 140, "y": 650, "dur": 2.5},
            {"name": "flash_green", "ts": 25.0, "x": 0, "y": 0, "dur": 0.2},
            {"name": "icon_100", "ts": 27.0, "x": 100, "y": 450, "dur": 2.5, "scale": 1.2},
        ],
    },
    # ── 04: WHY/HARSH TRUTH — the grind reality ──
    {
        "id": "04-grind-reality",
        "start": 388.0,
        "duration": 42.0,
        "hook": "HE'S NOT JUST LAMBOS",
        "speaker": "Andy Frisella",
        "punchlines": {"hard", "grind", "wrong", "right", "Lamborghini", "balling", "internet", "real", "price", "great", "skills", "resilient"},
        "overlays": [
            {"name": "icon_fire", "ts": 1.0, "x": 780, "y": 200, "dur": 3.0, "scale": 1.3},
            {"name": "badge_truth", "ts": 5.0, "x": 250, "y": 480, "dur": 2.5},
            {"name": "icon_warning", "ts": 12.0, "x": 100, "y": 350, "dur": 2.5},
            {"name": "flash_yellow", "ts": 18.0, "x": 0, "y": 0, "dur": 0.2},
            {"name": "text_truth", "ts": 24.0, "x": 140, "y": 650, "dur": 2.5},
            {"name": "icon_bolt", "ts": 32.0, "x": 800, "y": 300, "dur": 3.0, "scale": 1.4},
            {"name": "badge_protip", "ts": 36.0, "x": 250, "y": 500, "dur": 2.5},
        ],
    },
    # ── 05: CONTRARIAN — rejection that built the empire ──
    {
        "id": "05-rejection-built-empire",
        "start": 481.0,
        "duration": 36.0,
        "hook": "REJECTION MADE HIM A BILLIONAIRE",
        "speaker": "Andy Frisella",
        "punchlines": {"no", "never", "work", "ourselves", "forced", "vertical", "challenges", "frustrating", "good", "thing", "2012", "biggest", "distributor"},
        "overlays": [
            {"name": "icon_target", "ts": 1.0, "x": 780, "y": 200, "dur": 3.0, "scale": 1.3},
            {"name": "flash_red", "ts": 8.0, "x": 0, "y": 0, "dur": 0.2},
            {"name": "badge_warning", "ts": 10.0, "x": 250, "y": 480, "dur": 2.5},
            {"name": "text_never", "ts": 16.0, "x": 140, "y": 650, "dur": 2.0},
            {"name": "icon_bolt", "ts": 24.0, "x": 800, "y": 350, "dur": 3.0, "scale": 1.4},
            {"name": "flash_green", "ts": 30.0, "x": 0, "y": 0, "dur": 0.2},
            {"name": "badge_key", "ts": 31.0, "x": 250, "y": 500, "dur": 2.5},
        ],
    },
    # ── 06: MONEY+TIMEFRAME — Bugatti encounter ──
    {
        "id": "06-bugatti-money",
        "start": 978.0,
        "duration": 24.0,
        "hook": "HOW TO AFFORD A BUGATTI",
        "speaker": "Andy Frisella",
        "punchlines": {"Bugatti", "rich", "entrepreneur", "afford", "sir", "question", "garage"},
        "overlays": [
            {"name": "icon_money", "ts": 1.0, "x": 780, "y": 200, "dur": 3.0, "scale": 1.5},
            {"name": "flash_yellow", "ts": 4.0, "x": 0, "y": 0, "dur": 0.2},
            {"name": "badge_luxury", "ts": 6.0, "x": 250, "y": 480, "dur": 3.0},
            {"name": "icon_crown", "ts": 12.0, "x": 800, "y": 300, "dur": 3.0, "scale": 1.3},
            {"name": "text_wow", "ts": 18.0, "x": 140, "y": 650, "dur": 2.0},
        ],
    },
    # ── 07: THIS/VISUAL — dream house manifestation ──
    {
        "id": "07-dream-house",
        "start": 1005.0,
        "duration": 30.0,
        "hook": "HE VISUALIZED THIS HOUSE",
        "speaker": "Andy Frisella",
        "punchlines": {"president", "house", "kid", "coolest", "owning", "broke", "visualize", "dream", "bought", "sale"},
        "overlays": [
            {"name": "icon_idea", "ts": 1.0, "x": 780, "y": 200, "dur": 3.0, "scale": 1.3},
            {"name": "badge_luxury", "ts": 5.0, "x": 250, "y": 480, "dur": 2.5},
            {"name": "icon_crown", "ts": 12.0, "x": 100, "y": 400, "dur": 3.0, "scale": 1.3},
            {"name": "flash_white", "ts": 18.0, "x": 0, "y": 0, "dur": 0.2},
            {"name": "text_wow", "ts": 22.0, "x": 140, "y": 650, "dur": 2.5},
        ],
    },
    # ── 08: CONTRARIAN — business with family ──
    {
        "id": "08-family-business",
        "start": 196.0,
        "duration": 37.0,
        "hook": "BUSINESS WITH FAMILY IS GOOD",
        "speaker": "Andy Frisella",
        "punchlines": {"family", "bad", "advice", "skills", "partner", "trust", "friends", "amazing", "table", "bring"},
        "overlays": [
            {"name": "icon_warning", "ts": 1.0, "x": 780, "y": 200, "dur": 2.5},
            {"name": "badge_truth", "ts": 5.0, "x": 250, "y": 480, "dur": 2.5},
            {"name": "flash_yellow", "ts": 12.0, "x": 0, "y": 0, "dur": 0.2},
            {"name": "text_truth", "ts": 18.0, "x": 140, "y": 650, "dur": 2.5},
            {"name": "icon_bolt", "ts": 28.0, "x": 800, "y": 350, "dur": 3.0, "scale": 1.3},
        ],
    },
    # ── 09: WHY/HARSH TRUTH — fitness = success ──
    {
        "id": "09-fitness-success",
        "start": 230.0,
        "duration": 42.0,
        "hook": "FITNESS = FINANCIAL SUCCESS",
        "speaker": "Andy Frisella",
        "punchlines": {"fitness", "financial", "success", "correlation", "huge", "mutual", "suffering", "trains", "culture", "team", "struggling", "hard"},
        "overlays": [
            {"name": "icon_chart_up", "ts": 1.0, "x": 780, "y": 200, "dur": 3.0, "scale": 1.3},
            {"name": "badge_key", "ts": 5.0, "x": 250, "y": 480, "dur": 2.5},
            {"name": "icon_fire", "ts": 14.0, "x": 100, "y": 400, "dur": 3.0, "scale": 1.3},
            {"name": "flash_green", "ts": 22.0, "x": 0, "y": 0, "dur": 0.2},
            {"name": "text_fact", "ts": 28.0, "x": 140, "y": 650, "dur": 2.5},
            {"name": "icon_100", "ts": 35.0, "x": 800, "y": 300, "dur": 3.0, "scale": 1.2},
        ],
    },
]
