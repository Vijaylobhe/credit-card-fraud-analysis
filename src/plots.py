"""Shared chart style so every figure looks the same."""

from pathlib import Path

import matplotlib.pyplot as plt

VISUALS_DIR = Path(__file__).resolve().parents[1] / "visuals"

LEGIT_COLOR = "#2a78d6"   # blue  = legitimate
FRAUD_COLOR = "#eb6834"   # orange = fraud
TEXT_COLOR = "#0b0b0b"
MUTED_COLOR = "#52514e"
GRID_COLOR = "#e4e3df"
SURFACE = "#fcfcfb"


def set_style():
    plt.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": GRID_COLOR,
        "axes.labelcolor": MUTED_COLOR,
        "axes.titlecolor": TEXT_COLOR,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID_COLOR,
        "grid.linewidth": 0.8,
        "xtick.color": MUTED_COLOR,
        "ytick.color": MUTED_COLOR,
        "legend.frameon": False,
        "lines.linewidth": 2,
        "figure.dpi": 110,
    })


def save(fig, name):
    """Save a figure as PNG into visuals/."""
    VISUALS_DIR.mkdir(exist_ok=True)
    fig.savefig(VISUALS_DIR / f"{name}.png", bbox_inches="tight", dpi=150)
