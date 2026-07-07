#!/usr/bin/env python3

"""

Generate snake SVG animation from GitHub contribution graph.


Fetches the user's public contribution data from GitHub,

renders the contribution grid, then draws a snake path that

"eats" the user's most active days.

"""

import urllib.request

import re

import os

from datetime import datetime


USERNAME = os.environ.get("GH_USER", "LucasSantos9711")

OUTPUT = os.environ.get("OUTPUT", "output/github-snake.svg")


# --- Fetch contribution HTML ---

url = f"https://github.com/users/{USERNAME}/contributions"

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

try:

    html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8")

except Exception as e:

    print(f"ERROR fetching contributions: {e}")

    raise


# --- Parse contribution data ---

# Each day looks like:

# <td class="ContributionCalendar-day" ... data-date="2024-01-15" data-level="2" data-count="5">

pattern = r'data-date="([\d-]+)"[^>]*data-level="(\d+)"'

matches = re.findall(pattern, html)


if not matches:

    print("ERROR: No contribution data found")

    raise SystemExit(1)


data = {date: int(level) for date, level in matches}

print(f"Found {len(data)} days of contribution data")


# --- Layout constants ---

CELL = 13          # cell size in px

GAP = 2            # gap between cells

COLS = 53          # ~52 weeks in a year

ROWS = 7           # 7 days per week

PAD = 20           # padding around grid


# Sort dates to align grid properly

dates_sorted = sorted(data.keys())

start_date = datetime.strptime(dates_sorted[0], "%Y-%m-%d")


# --- Color palette (GitHub dark theme) ---

COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

SNAKE_COLOR = "#58a6ff"

SNAKE_HEAD = "#f78166"

BG = "#0d1117"


# --- Build SVG ---

W = COLS * (CELL + GAP) + PAD * 2

H = ROWS * (CELL + GAP) + PAD * 2 + 30   # extra space for header


parts = []

parts.append(

    f'<svg xmlns="http://www.w3.org/2000/svg" '

    f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">'

)

parts.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')


# Header text

parts.append(

    f'<text x="{PAD}" y="14" fill="#58a6ff" '

    f'font-family="monospace" font-size="11" font-weight="bold">'

    f'🐍 {USERNAME} contribution snake</text>'

)


# Draw contributions grid

active_cells = []

for date, level in data.items():

    d = datetime.strptime(date, "%Y-%m-%d")

    delta_days = (d - start_date).days

    week = delta_days // 7

    day_of_week = d.weekday()

    x = PAD + week * (CELL + GAP)

    y = PAD + 20 + day_of_week * (CELL + GAP)

    color = COLORS[min(level, 4)]

    parts.append(

        f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '

        f'rx="2" ry="2" fill="{color}"/>'

    )

    if level > 0:

        active_cells.append((date, week, day_of_week, level))


# --- Draw snake path through active cells ---

# Strategy: sort by date, snake connects through cells in chronological order.

# For visual interest, prefer days with level >= 2.

snake_points = [

    (week, day_of_week)

    for _, week, day_of_week, level in sorted(active_cells, key=lambda c: c[0])

    if level >= 1

]


if snake_points:

    # Build path connecting all snake points in order

    cx = lambda w, d: PAD + w * (CELL + GAP) + CELL / 2

    cy = lambda w, d: PAD + 20 + d * (CELL + GAP) + CELL / 2


    # Body

    path_d = f"M {cx(*snake_points[0])} {cy(*snake_points[0])}"

    for w, d in snake_points[1:]:

        path_d += f" L {cx(w, d)} {cy(w, d)}"


    parts.append(

        f'<path d="{path_d}" stroke="{SNAKE_COLOR}" stroke-width="2.5" '

        f'fill="none" stroke-linecap="round" stroke-linejoin="round" '

        f'opacity="0.85"/>'

    )


    # Head (last point)

    hw, hd = snake_points[-1]

    parts.append(

        f'<circle cx="{cx(hw, hd)}" cy="{cy(hw, hd)}" r="4" '

        f'fill="{SNAKE_HEAD}"/>'

    )


parts.append("</svg>")


# --- Write output ---

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

with open(OUTPUT, "w", encoding="utf-8") as f:

    f.write("\n".join(parts))


size = os.path.getsize(OUTPUT)

print(f"✅ Snake SVG generated: {OUTPUT} ({size} bytes)")
