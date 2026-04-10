"""
Stadium visualization module.

Draws a bird's-eye top-down view of an MLB stadium and overlays a
heatmap showing the probability of a home-run ball landing in each
outfield section.

Coordinate system (same as stadiums.py):
  Origin at home plate, +Y toward CF, +X toward RF (right side of field).
  All distances in feet.
"""

from __future__ import annotations

from typing import Optional

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import matplotlib.cm as mcm
import numpy as np

from stadiums import fence_distance_at_angle, wall_curve, section_polygon
from sections import get_sections, classify_hr

# ---------------------------------------------------------------------------
# Color / style constants
# ---------------------------------------------------------------------------

FIELD_GREEN   = "#3a7d44"
INFIELD_DIRT  = "#c4924a"
WARNING_TRACK = "#b8864e"
WALL_COLOR    = "#2b2b2b"
FOUL_LINE     = "#ffffff"
BASE_COLOR    = "#f5f5f5"
SECTION_EDGE  = "#cccccc"

CMAP_NAME = "YlOrRd"   # yellow → orange → red for probability

# Maximum stand depth rendered (feet beyond the fence).
# Sections in sections.py define their own r_inner/r_outer, but we need
# a ceiling for _set_limits and for _draw_field sizing.
_MAX_STAND_DEPTH = 95


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_figure(figsize: tuple[float, float] = (8, 8)) -> tuple[plt.Figure, plt.Axes]:
    """Create and return a new (fig, ax) with dark background and square aspect."""
    fig, ax = plt.subplots(1, 1, figsize=figsize, facecolor="#1c1c1c")
    ax.set_facecolor("#1c1c1c")
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def draw_empty_stadium(
    ax: plt.Axes,
    lf: int,
    cf: int,
    rf: int,
    stadium_name: str = "",
    title: str = "",
) -> None:
    """Draw the stadium field and stand sections with no probability color."""
    ax.cla()
    ax.set_facecolor("#1c1c1c")
    ax.set_aspect("equal")
    ax.axis("off")
    sections = get_sections(stadium_name)
    _draw_field(ax, lf, cf, rf, sections)
    _draw_sections(ax, lf, cf, rf, sections, probabilities=None, highlight=None)
    _set_limits(ax, cf, sections)
    if title:
        ax.set_title(title, color="white", fontsize=11, pad=8)


def draw_heatmap(
    ax: plt.Axes,
    lf: int,
    cf: int,
    rf: int,
    stadium_name: str,
    probabilities: dict[str, float],
    hr_df=None,
    highlight_section: Optional[str] = None,
    title: str = "",
    total_hrs: int = 0,
) -> Optional[object]:
    """
    Draw the full heatmap.

    Parameters
    ----------
    probabilities     : {section_id: probability} from data.compute_probabilities()
    hr_df             : DataFrame with angle_deg / distance_ft columns (scatter dots)
    highlight_section : section_id to outline in cyan
    title             : plot title
    total_hrs         : appended to title as HR count
    """
    ax.cla()
    ax.set_facecolor("#1c1c1c")
    ax.set_aspect("equal")
    ax.axis("off")

    sections = get_sections(stadium_name)
    _draw_field(ax, lf, cf, rf, sections)
    _draw_sections(ax, lf, cf, rf, sections,
                   probabilities=probabilities, highlight=highlight_section)
    _draw_hr_scatter(ax, hr_df)
    _set_limits(ax, cf, sections)

    if title:
        sub = f"  ({total_hrs} HR{'s' if total_hrs != 1 else ''})" if total_hrs else ""
        ax.set_title(f"{title}{sub}", color="white", fontsize=11, pad=8)

    # Colorbar
    max_prob = max(probabilities.values()) if probabilities else 1.0
    cmap = mcm.get_cmap(CMAP_NAME)
    norm = mcolors.Normalize(vmin=0, vmax=max_prob if max_prob > 0 else 1.0)
    sm   = mcm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = ax.figure.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("HR Probability", color="white", fontsize=9)
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white", fontsize=8)
    cbar.ax.set_facecolor("#1c1c1c")

    return cbar


def section_at_point(
    x: float,
    y: float,
    lf: int,
    cf: int,
    rf: int,
    stadium_name: str,
) -> Optional[str]:
    """
    Return the section_id for a click at data coordinates (x, y), or None.
    Delegates to the same classify_hr logic used during data assignment.
    """
    angle_deg = float(np.degrees(np.arctan2(x, y)))
    dist_ft   = float(np.sqrt(x ** 2 + y ** 2))
    sections  = get_sections(stadium_name)
    return classify_hr(angle_deg, dist_ft, lf, cf, rf, sections)


# ---------------------------------------------------------------------------
# Internal drawing helpers
# ---------------------------------------------------------------------------

def _stand_max_r(sections: list[tuple]) -> float:
    """Return the largest r_outer across all sections (feet beyond the wall)."""
    if not sections:
        return _MAX_STAND_DEPTH
    return max(s[5] for s in sections)


def _draw_field(ax: plt.Axes, lf: int, cf: int, rf: int, sections: list[tuple]) -> None:
    """Draw grass, dirt, bases, foul lines, wall, warning track."""

    stand_depth = _stand_max_r(sections)
    max_r = cf + stand_depth + 10

    # --- Grass wedge (fair territory) ---
    foul_angles = np.linspace(-45, 45, 200)
    foul_rad    = np.radians(foul_angles)
    xs = np.concatenate([[0], max_r * np.sin(foul_rad), [0]])
    ys = np.concatenate([[0], max_r * np.cos(foul_rad), [0]])
    ax.fill(xs, ys, color=FIELD_GREEN, zorder=0)

    # --- Infield dirt circle ---
    ax.add_patch(mpatches.Circle((0, 0), 95, color=INFIELD_DIRT, zorder=1))

    # --- Inner infield grass (diamond) ---
    base_d = 90.0 / np.sqrt(2)
    diamond_x = [0,  base_d, 0, -base_d, 0]
    diamond_y = [0,  base_d, 2 * base_d, base_d, 0]
    ax.fill(diamond_x, diamond_y, color=FIELD_GREEN, zorder=3)

    # --- Warning track (15 ft arc inside the wall) ---
    wt_angles = np.linspace(-47, 47, 200)
    wt_outer  = np.array([fence_distance_at_angle(a, lf, cf, rf) for a in wt_angles])
    wt_inner  = wt_outer - 15
    rad       = np.radians(wt_angles)
    wt_ox = wt_outer * np.sin(rad);        wt_oy = wt_outer * np.cos(rad)
    wt_ix = wt_inner * np.sin(rad)[::-1];  wt_iy = wt_inner * np.cos(rad)[::-1]
    ax.fill(np.concatenate([wt_ox, wt_ix]),
            np.concatenate([wt_oy, wt_iy]), color=WARNING_TRACK, zorder=4)

    # --- Outfield wall ---
    wx, wy = wall_curve(lf, cf, rf)
    ax.plot(wx, wy, color=WALL_COLOR, linewidth=3, zorder=5)

    # --- Foul lines ---
    foul_len = max(lf, rf) + 30
    for sign in (-1, 1):
        a_rad = np.radians(sign * 45)
        ax.plot([0, foul_len * np.sin(a_rad)], [0, foul_len * np.cos(a_rad)],
                color=FOUL_LINE, linewidth=1, linestyle="--", alpha=0.6, zorder=6)

    # --- Foul poles ---
    for sign, dist in ((-1, lf), (1, rf)):
        a_rad = np.radians(sign * 45)
        ax.plot(dist * np.sin(a_rad), dist * np.cos(a_rad),
                marker="^", color="yellow", markersize=7, zorder=10)

    # --- Bases ---
    for bx, by in [(base_d, base_d), (0, 2*base_d), (-base_d, base_d), (0, 0)]:
        ax.add_patch(mpatches.Rectangle(
            (bx - 3, by - 3), 6, 6,
            color=BASE_COLOR, zorder=11, angle=45, rotation_point="center"
        ))

    # --- Pitcher's mound ---
    ax.add_patch(mpatches.Circle((0, 60.5), 9, color=INFIELD_DIRT, zorder=10))

    # --- Distance labels in the grass ---
    for sign in (-1, 0, 1):
        for d_label in (300, 350, 400):
            a_deg = sign * 20
            a_rad = np.radians(a_deg)
            if d_label <= fence_distance_at_angle(a_deg, lf, cf, rf) - 5:
                ax.text(d_label * np.sin(a_rad), d_label * np.cos(a_rad),
                        f"{d_label}′", color="white", fontsize=6,
                        ha="center", va="center", zorder=12, alpha=0.7,
                        fontfamily="monospace")

    # --- Fence distance labels at poles and CF ---
    for a_deg, lbl in [(-45, f"{lf}′"), (0, f"{cf}′"), (45, f"{rf}′")]:
        a_rad = np.radians(a_deg)
        fd    = fence_distance_at_angle(a_deg, lf, cf, rf)
        ax.text((fd + 5) * np.sin(a_rad), (fd + 5) * np.cos(a_rad),
                lbl, color="yellow", fontsize=7, ha="center", va="center",
                zorder=13, fontweight="bold")


def _draw_sections(
    ax: plt.Axes,
    lf: int,
    cf: int,
    rf: int,
    sections: list[tuple],
    probabilities: Optional[dict[str, float]],
    highlight: Optional[str],
) -> None:
    """Draw per-stadium outfield section polygons with optional heatmap coloring."""
    if not sections:
        return

    cmap     = mcm.get_cmap(CMAP_NAME)
    max_prob = max(probabilities.values()) if probabilities else 1.0
    norm     = mcolors.Normalize(vmin=0, vmax=max_prob if max_prob > 0 else 1.0)

    for sid, label, a_min, a_max, r_in, r_out in sections:
        # Build r_inner / r_outer as functions of angle.
        # r_in and r_out are feet beyond the outfield wall.
        def r_inner_fn(a, lf=lf, cf=cf, rf=rf, r_in=r_in):
            return fence_distance_at_angle(a, lf, cf, rf) + r_in

        def r_outer_fn(a, lf=lf, cf=cf, rf=rf, r_out=r_out):
            return fence_distance_at_angle(a, lf, cf, rf) + r_out

        sx, sy = section_polygon(a_min, a_max, r_inner_fn, r_outer_fn)

        if probabilities and sid in probabilities:
            color = cmap(norm(probabilities[sid]))
            alpha = 0.85
        else:
            color = "#444444"
            alpha = 0.6

        is_highlighted = highlight == sid
        patch = mpatches.Polygon(
            np.column_stack([sx, sy]),
            facecolor=color,
            edgecolor="cyan" if is_highlighted else SECTION_EDGE,
            linewidth=2.5 if is_highlighted else 0.6,
            alpha=alpha,
            zorder=7,
        )
        ax.add_patch(patch)

        # Label at centroid
        cx, cy    = float(np.mean(sx)), float(np.mean(sy))
        prob_str  = (f"{probabilities[sid]*100:.1f}%"
                     if probabilities and sid in probabilities else "")
        # Fit long section labels: use first line only if two-line label given
        ax.text(cx, cy, f"{label}\n{prob_str}",
                color="white", fontsize=6, ha="center", va="center",
                zorder=9, fontweight="bold" if is_highlighted else "normal")


def _draw_hr_scatter(ax: plt.Axes, hr_df) -> None:
    """Scatter-plot individual HR landing spots (faint white dots)."""
    if hr_df is None or hr_df.empty:
        return
    if "angle_deg" not in hr_df.columns or "distance_ft" not in hr_df.columns:
        return

    rad  = np.radians(hr_df["angle_deg"].values)
    dist = hr_df["distance_ft"].values
    ax.scatter(dist * np.sin(rad), dist * np.cos(rad),
               s=12, color="white", alpha=0.25, zorder=8, marker="o", linewidths=0)


def _set_limits(ax: plt.Axes, cf: int, sections: list[tuple]) -> None:
    max_r = cf + _stand_max_r(sections) + 20
    ax.set_xlim(-max_r * 0.65, max_r * 0.65)
    ax.set_ylim(-40, max_r)
