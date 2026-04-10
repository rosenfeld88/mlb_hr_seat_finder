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

from stadiums import (
    SECTION_NAMES,
    NEAR_DEPTH,
    FAR_DEPTH,
    fence_distance_at_angle,
    wall_curve,
    section_polygon,
)

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
    title: str = "",
) -> None:
    """Draw the stadium field and stand sections with no probability color."""
    _draw_field(ax, lf, cf, rf)
    _draw_sections(ax, lf, cf, rf, probabilities=None, highlight=None)
    _set_limits(ax, cf)
    if title:
        ax.set_title(title, color="white", fontsize=11, pad=8)


def draw_heatmap(
    ax: plt.Axes,
    lf: int,
    cf: int,
    rf: int,
    probabilities: dict[str, float],
    hr_df=None,
    highlight_section: Optional[str] = None,
    title: str = "",
    total_hrs: int = 0,
) -> Optional[plt.colorbar]:
    """
    Draw the full heatmap.

    Parameters
    ----------
    probabilities   : {section_id: probability} mapping from data.compute_probabilities()
    hr_df           : raw DataFrame with angle_deg / distance_ft columns (scatter dots)
    highlight_section : section_id to outline prominently
    title           : plot title
    total_hrs       : shown in sub-title
    """
    ax.cla()
    ax.set_facecolor("#1c1c1c")
    ax.set_aspect("equal")
    ax.axis("off")

    _draw_field(ax, lf, cf, rf)
    _draw_sections(ax, lf, cf, rf, probabilities=probabilities, highlight=highlight_section)
    _draw_hr_scatter(ax, hr_df)
    _set_limits(ax, cf)

    if title:
        sub = f"  ({total_hrs} HR{'s' if total_hrs != 1 else ''})" if total_hrs else ""
        ax.set_title(f"{title}{sub}", color="white", fontsize=11, pad=8)

    # Colorbar
    cmap   = mcm.get_cmap(CMAP_NAME)
    norm   = mcolors.Normalize(vmin=0, vmax=max(probabilities.values()) or 1)
    sm     = mcm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar   = ax.figure.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
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
) -> Optional[str]:
    """
    Return the section_id clicked at data coordinates (x, y), or None.
    Uses the same angle/distance logic as data.py section assignment.
    """
    angle_deg = float(np.degrees(np.arctan2(x, y)))
    dist      = float(np.sqrt(x ** 2 + y ** 2))

    if angle_deg < -45 or angle_deg > 45:
        return None

    fence_d = fence_distance_at_angle(angle_deg, lf, cf, rf)
    # Only within the stands (between fence and fence + NEAR_DEPTH + FAR_DEPTH)
    if dist < fence_d or dist > fence_d + NEAR_DEPTH + FAR_DEPTH:
        return None

    is_near = dist < fence_d + NEAR_DEPTH
    for sid, _lbl, a_min, a_max, near_band in SECTION_NAMES:
        if a_min <= angle_deg <= a_max and near_band == is_near:
            return sid
    return None


# ---------------------------------------------------------------------------
# Internal drawing helpers
# ---------------------------------------------------------------------------

def _draw_field(ax: plt.Axes, lf: int, cf: int, rf: int) -> None:
    """Draw grass, dirt, bases, foul lines, wall, warning track."""

    max_r = cf + NEAR_DEPTH + FAR_DEPTH + 10

    # --- Grass background (full extent) ---
    ax.set_xlim(-max_r * 0.65, max_r * 0.65)
    ax.set_ylim(-30, max_r)

    # Grass wedge (fair territory) from home plate to the outfield
    foul_angles = np.linspace(-45, 45, 200)
    foul_rad    = np.radians(foul_angles)
    # Fan-shaped grass patch
    xs = np.concatenate([[0], (max_r * np.sin(foul_rad)), [0]])
    ys = np.concatenate([[0], (max_r * np.cos(foul_rad)), [0]])
    ax.fill(xs, ys, color=FIELD_GREEN, zorder=0)

    # Infield dirt: filled circle centred at home plate
    dirt_r = 95
    dirt_circle = mpatches.Circle((0, 0), dirt_r, color=INFIELD_DIRT, zorder=1)
    ax.add_patch(dirt_circle)

    # Re-draw grass over the dirt for the outfield grass (between inner and outer)
    ax.fill(xs, ys, color=FIELD_GREEN, zorder=2, alpha=0.0)  # placeholder

    # Inner infield grass (diamond area) — square rotated 45°
    base_d = 90.0 / np.sqrt(2)   # ~63.6 ft from HP to each base in x/y
    diamond_x = [0, base_d, 0, -base_d, 0]
    diamond_y = [0, base_d, 2 * base_d, base_d, 0]
    ax.fill(diamond_x, diamond_y, color=FIELD_GREEN, zorder=3)

    # --- Warning track (thin arc just inside the wall) ---
    wt_offset = 15   # warning track width in feet
    wt_angles = np.linspace(-47, 47, 200)
    wt_outer  = np.array([fence_distance_at_angle(a, lf, cf, rf) for a in wt_angles])
    wt_inner  = wt_outer - wt_offset
    rad       = np.radians(wt_angles)
    wt_ox = wt_outer * np.sin(rad); wt_oy = wt_outer * np.cos(rad)
    wt_ix = wt_inner * np.sin(rad)[::-1]; wt_iy = wt_inner * np.cos(rad)[::-1]
    wt_xs = np.concatenate([wt_ox, wt_ix])
    wt_ys = np.concatenate([wt_oy, wt_iy])
    ax.fill(wt_xs, wt_ys, color=WARNING_TRACK, zorder=4)

    # --- Outfield wall ---
    wx, wy = wall_curve(lf, cf, rf)
    ax.plot(wx, wy, color=WALL_COLOR, linewidth=3, zorder=5)

    # --- Foul lines ---
    foul_len = max(lf, rf) + 30
    for sign in (-1, 1):
        angle_rad = np.radians(sign * 45)
        fx = foul_len * np.sin(angle_rad)
        fy = foul_len * np.cos(angle_rad)
        ax.plot([0, fx], [0, fy], color=FOUL_LINE, linewidth=1, zorder=6,
                linestyle="--", alpha=0.6)

    # --- Foul poles (small vertical markers) ---
    for sign, dist in ((-1, lf), (1, rf)):
        angle_rad = np.radians(sign * 45)
        fx = dist * np.sin(angle_rad)
        fy = dist * np.cos(angle_rad)
        ax.plot(fx, fy, marker="^", color="yellow", markersize=7, zorder=10)

    # --- Bases ---
    base_positions = [
        (base_d,     base_d,     "1B"),
        (0,          2 * base_d, "2B"),
        (-base_d,    base_d,     "3B"),
        (0,          0,          "HP"),
    ]
    for bx, by, lbl in base_positions:
        ax.add_patch(mpatches.Rectangle(
            (bx - 3, by - 3), 6, 6,
            color=BASE_COLOR, zorder=11, angle=45, rotation_point="center"
        ))

    # --- Pitcher's mound ---
    ax.add_patch(mpatches.Circle((0, 60.5), 9, color=INFIELD_DIRT, zorder=10))

    # --- Distance markers ---
    for sign in (-1, 0, 1):
        for dist_label in (300, 350, 400):
            a_deg = sign * 20
            a_rad = np.radians(a_deg)
            mx = dist_label * np.sin(a_rad)
            my = dist_label * np.cos(a_rad)
            # Only show if within the grass area
            if dist_label <= fence_distance_at_angle(a_deg, lf, cf, rf) - 5:
                ax.text(mx, my, f"{dist_label}′", color="white", fontsize=6,
                        ha="center", va="center", zorder=12, alpha=0.7,
                        fontfamily="monospace")

    # Fence distance markers at foul poles and CF
    for a_deg, label_text in [(-45, f"{lf}′"), (0, f"{cf}′"), (45, f"{rf}′")]:
        a_rad = np.radians(a_deg)
        fd = fence_distance_at_angle(a_deg, lf, cf, rf)
        ax.text(
            (fd + 5) * np.sin(a_rad),
            (fd + 5) * np.cos(a_rad),
            label_text,
            color="yellow", fontsize=7, ha="center", va="center", zorder=13,
            fontweight="bold"
        )


def _draw_sections(
    ax: plt.Axes,
    lf: int,
    cf: int,
    rf: int,
    probabilities: Optional[dict[str, float]],
    highlight: Optional[str],
) -> None:
    """Draw the 10 stand sections as colored polygon patches."""
    cmap = mcm.get_cmap(CMAP_NAME)
    max_prob = max(probabilities.values()) if probabilities else 1.0
    norm = mcolors.Normalize(vmin=0, vmax=max_prob if max_prob > 0 else 1.0)

    for sid, label, a_min, a_max, is_near in SECTION_NAMES:
        # "Lower" section occupies [fence, fence+NEAR_DEPTH)
        # "Upper" section occupies [fence+NEAR_DEPTH, fence+NEAR_DEPTH+FAR_DEPTH)
        if is_near:
            def r_inner(a, lf=lf, cf=cf, rf=rf):
                return fence_distance_at_angle(a, lf, cf, rf)

            def r_outer(a, lf=lf, cf=cf, rf=rf):
                return fence_distance_at_angle(a, lf, cf, rf) + NEAR_DEPTH
        else:
            def r_inner(a, lf=lf, cf=cf, rf=rf):
                return fence_distance_at_angle(a, lf, cf, rf) + NEAR_DEPTH

            def r_outer(a, lf=lf, cf=cf, rf=rf):
                return fence_distance_at_angle(a, lf, cf, rf) + NEAR_DEPTH + FAR_DEPTH

        sx, sy = section_polygon(a_min, a_max, r_inner, r_outer)

        # Color
        if probabilities and sid in probabilities:
            prob  = probabilities[sid]
            color = cmap(norm(prob))
            alpha = 0.85
        else:
            color = "#444444"
            alpha = 0.6

        is_highlighted = highlight == sid
        edge_color = "cyan" if is_highlighted else SECTION_EDGE
        edge_width  = 2.5   if is_highlighted else 0.6

        patch = mpatches.Polygon(
            np.column_stack([sx, sy]),
            facecolor=color,
            edgecolor=edge_color,
            linewidth=edge_width,
            alpha=alpha,
            zorder=7,
        )
        ax.add_patch(patch)

        # Section label at the centroid
        cx = np.mean(sx)
        cy = np.mean(sy)
        prob_str = f"{probabilities[sid]*100:.1f}%" if probabilities and sid in probabilities else ""
        ax.text(cx, cy, f"{label}\n{prob_str}",
                color="white", fontsize=6, ha="center", va="center",
                zorder=9, fontweight="bold" if is_highlighted else "normal")


def _draw_hr_scatter(ax: plt.Axes, hr_df) -> None:
    """Scatter-plot individual HR landing spots (faint dots)."""
    if hr_df is None or hr_df.empty:
        return
    if "angle_deg" not in hr_df.columns or "distance_ft" not in hr_df.columns:
        return

    rad = np.radians(hr_df["angle_deg"].values)
    dist = hr_df["distance_ft"].values
    sx = dist * np.sin(rad)
    sy = dist * np.cos(rad)

    ax.scatter(sx, sy, s=12, color="white", alpha=0.25, zorder=8, marker="o",
               linewidths=0)


def _set_limits(ax: plt.Axes, cf: int) -> None:
    max_r = cf + NEAR_DEPTH + FAR_DEPTH + 20
    ax.set_xlim(-max_r * 0.65, max_r * 0.65)
    ax.set_ylim(-40, max_r)
