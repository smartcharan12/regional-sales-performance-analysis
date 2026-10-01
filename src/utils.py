"""
Shared helpers: project paths, reference data and chart styling.

Keeping these in one place means every script and notebook uses the same
folder locations, the same "correct" region/category spellings and the same
chart look. If a value has to change, it changes here only.
"""

from pathlib import Path

import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Paths (resolved relative to this file, so code works from any directory)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
POWERBI_EXPORT = DATA_PROCESSED / "powerbi"
VIZ_DIR = PROJECT_ROOT / "visualizations"

RAW_FILE = DATA_RAW / "sales_raw.csv"
CLEAN_FILE = DATA_PROCESSED / "sales_cleaned.csv"
CLEANING_LOG_FILE = DATA_PROCESSED / "cleaning_log.csv"

# ---------------------------------------------------------------------------
# Reference data: the "single source of truth" used for validation
# ---------------------------------------------------------------------------
VALID_REGIONS = ["Central", "East", "South", "West"]
VALID_CATEGORIES = ["Furniture", "Office Supplies", "Technology"]
VALID_SEGMENTS = ["Consumer", "Corporate", "Home Office"]
VALID_SHIP_MODES = ["Same Day", "First Class", "Second Class", "Standard Class"]

# Discounts RetailCo's pricing system is allowed to apply (fractions, 0.2 = 20%)
VALID_DISCOUNTS = [0.0, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

# State -> Region. Used to validate Region and to rebuild it when missing.
STATE_TO_REGION = {
    # West
    "California": "West", "Washington": "West", "Oregon": "West",
    "Arizona": "West", "Colorado": "West", "Utah": "West", "Nevada": "West",
    # East
    "New York": "East", "Pennsylvania": "East", "Ohio": "East",
    "Massachusetts": "East", "New Jersey": "East", "Maryland": "East",
    "Connecticut": "East",
    # Central
    "Texas": "Central", "Illinois": "Central", "Michigan": "Central",
    "Minnesota": "Central", "Wisconsin": "Central", "Missouri": "Central",
    "Indiana": "Central",
    # South
    "Florida": "South", "Georgia": "South", "North Carolina": "South",
    "Tennessee": "South", "Virginia": "South", "Kentucky": "South",
    "Alabama": "South",
}

# ---------------------------------------------------------------------------
# Chart styling
# ---------------------------------------------------------------------------
# One colour per *entity* (never per rank), so "West" is the same colour in
# every chart. Order follows a colour-blind-validated categorical palette.
REGION_COLORS = {
    "Central": "#2a78d6",  # blue
    "East": "#eb6834",     # orange
    "South": "#1baf7a",    # aqua
    "West": "#eda100",     # yellow
}
CATEGORY_COLORS = {
    "Furniture": "#2a78d6",
    "Office Supplies": "#eb6834",
    "Technology": "#1baf7a",
}
PRIMARY = "#2a78d6"      # single-series charts
MUTED = "#c3c2b7"        # de-emphasised bars
LOSS = "#d03b3b"         # reserved for "negative / loss" meaning only
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRID = "#e1e0d9"


def set_chart_style() -> None:
    """Apply a clean, consistent matplotlib style to every chart."""
    plt.rcParams.update({
        "figure.figsize": (10, 5.5),
        "figure.dpi": 110,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
        "figure.facecolor": "#fcfcfb",
        "axes.facecolor": "#fcfcfb",
        "axes.edgecolor": MUTED,
        "axes.labelcolor": INK_SECONDARY,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlecolor": INK,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": INK_SECONDARY,
        "ytick.color": INK_SECONDARY,
        "legend.frameon": False,
        "font.size": 10,
        "ytick.major.size": 0,
    })


def money(value: float) -> str:
    """Format a number as compact currency: 1234567 -> '$1.23M'."""
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000:
        return f"{sign}${value / 1_000_000:.2f}M"
    if value >= 10_000:
        return f"{sign}${value / 1_000:.0f}K"
    if value >= 1_000:
        return f"{sign}${value / 1_000:.1f}K"
    return f"{sign}${value:,.0f}"
