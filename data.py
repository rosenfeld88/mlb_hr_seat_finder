"""
Data fetching module.

Uses:
  - statsapi (MLB-StatsAPI) : team list, team roster, player metadata
  - requests                : direct Baseball Savant CSV download for HR spray-chart data
  - pybaseball              : statcast_batter() fallback and data helpers

Spray-chart coordinate system (Statcast image space):
  Home plate is approximately at pixel (125, 199).
  hc_x increases to the right (toward RF in standard orientation).
  hc_y increases downward (home plate = high hc_y, CF = low hc_y).

We convert to our plot space:
  dx = hc_x - 125           (positive → RF side)
  dy = 199 - hc_y           (positive → toward outfield)
  angle = atan2(dx, dy)     (0 = CF, + = RF, − = LF)
  distance = hit_distance_sc (feet, from Statcast)
"""

from __future__ import annotations

import io
import logging
import time
from functools import lru_cache
from typing import Optional

import numpy as np
import pandas as pd
import requests

try:
    import statsapi as _statsapi
    _STATSAPI_OK = True
except Exception:
    _statsapi   = None  # type: ignore[assignment]
    _STATSAPI_OK = False

logger = logging.getLogger(__name__)

# Statcast home-plate pixel coordinates
_HP_X = 125.0
_HP_Y = 199.0

# Baseball Savant search endpoint
_SAVANT_URL = "https://baseballsavant.mlb.com/statcast_search/csv"

# Request timeout (seconds)
_TIMEOUT = 30

# Minimum HRs required to generate a meaningful heatmap
MIN_HR_COUNT = 3


# ---------------------------------------------------------------------------
# Team / roster helpers  (statsapi — MLB-StatsAPI by toddrob99)
#
# statsapi.get() returns plain Python dicts mirroring the MLB Stats REST API.
# Reference: https://github.com/toddrob99/MLB-StatsAPI
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_teams() -> list[dict]:
    """
    Return a sorted list of MLB teams as dicts with keys:
    id, name, abbreviation.
    """
    if not _STATSAPI_OK:
        raise RuntimeError("statsapi (MLB-StatsAPI) is not available. "
                           "Run: py -3.14 -m pip install mlb-statsapi")
    resp = _statsapi.get("teams", {"sportId": 1})
    result = [
        {
            "id":           t["id"],
            "name":         t["name"],
            "abbreviation": t.get("abbreviation", ""),
        }
        for t in resp.get("teams", [])
    ]
    return sorted(result, key=lambda t: t["name"])


@lru_cache(maxsize=64)
def get_roster(team_id: int) -> list[dict]:
    """
    Return the 40-man roster for a team as a list of dicts:
    { id, full_name, position }
    """
    if not _STATSAPI_OK:
        raise RuntimeError("statsapi (MLB-StatsAPI) is not available.")
    resp = _statsapi.get("team_roster", {"teamId": team_id, "rosterType": "40Man"})
    result = []
    for p in resp.get("roster", []):
        person = p.get("person", {})
        result.append({
            "id":        person.get("id"),
            "full_name": person.get("fullName", "Unknown"),
            "position":  p.get("position", {}).get("abbreviation", ""),
        })
    return sorted(result, key=lambda p: p["full_name"])


# ---------------------------------------------------------------------------
# Statcast HR data download (Baseball Savant)
# ---------------------------------------------------------------------------

def _savant_params(season: int, **extra) -> dict:
    """Build the common Baseball Savant search parameters."""
    return {
        "all":          "true",
        "type":         "details",
        "player_type":  "batter",
        "hfTypes":      "home_run|",
        "hfSea":        f"{season}|",
        "metric_1":     "",
        "sort_col":     "pitches",
        "sort_order":   "desc",
        "min_pitches":  "0",
        "min_results":  "0",
        **extra,
    }


def _download_savant_csv(params: dict, retries: int = 3) -> pd.DataFrame:
    """Download a CSV from Baseball Savant and return a DataFrame."""
    for attempt in range(retries):
        try:
            resp = requests.get(_SAVANT_URL, params=params, timeout=_TIMEOUT)
            resp.raise_for_status()
            content = resp.text.strip()
            if not content or content.startswith("Error"):
                raise ValueError(f"Baseball Savant returned: {content[:200]}")
            df = pd.read_csv(io.StringIO(content), low_memory=False)
            return df
        except requests.exceptions.RequestException as exc:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise RuntimeError(f"Network error fetching Savant data: {exc}") from exc
    return pd.DataFrame()


def fetch_player_hr_data(player_id: int, season: int) -> pd.DataFrame:
    """
    Download Statcast home-run rows for a single batter in a given season.

    Returns a DataFrame with at least: hc_x, hc_y, hit_distance_sc, game_date.
    """
    params = _savant_params(season, **{"batters_lookup[]": player_id})
    df = _download_savant_csv(params)
    return _clean_hr_df(df)


def fetch_team_hr_data(team_abbrev: str, season: int) -> pd.DataFrame:
    """
    Download Statcast home-run rows for all batters on a team in a given season.
    Uses pybaseball as a fallback if the direct download returns no data.
    """
    params = _savant_params(season, team=team_abbrev)
    df = _download_savant_csv(params)
    df = _clean_hr_df(df)

    if df.empty:
        # Fallback: try pybaseball
        df = _pybaseball_fallback(team_abbrev=team_abbrev, season=season)

    return df


def _pybaseball_fallback(
    player_id: Optional[int] = None,
    team_abbrev: Optional[str] = None,
    season: int = 2023,
) -> pd.DataFrame:
    """Use pybaseball.statcast as a fallback data source."""
    try:
        from pybaseball import statcast, statcast_batter  # noqa: F401
    except ImportError:
        return pd.DataFrame()

    start = f"{season}-03-01"
    end   = f"{season}-11-30"
    try:
        if player_id:
            df = statcast_batter(start, end, player_id=player_id)
        else:
            df = statcast(start, end, team=team_abbrev)
        df = df[df["events"] == "home_run"].copy()
        return _clean_hr_df(df)
    except Exception as exc:
        logger.warning("pybaseball fallback failed: %s", exc)
        return pd.DataFrame()


def _clean_hr_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter to home-run rows only, drop rows with missing coordinates,
    and add derived 'angle_deg' and 'distance_ft' columns.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    # Keep only confirmed home runs (download should already filter, but be safe)
    if "events" in df.columns:
        df = df[df["events"] == "home_run"].copy()

    required = ["hc_x", "hc_y"]
    df = df.dropna(subset=[c for c in required if c in df.columns])

    if df.empty:
        return df

    # Derive angle and distance
    dx = df["hc_x"].astype(float) - _HP_X
    dy = _HP_Y - df["hc_y"].astype(float)

    df = df.copy()
    df["angle_deg"] = np.degrees(np.arctan2(dx, dy))

    if "hit_distance_sc" in df.columns:
        df["distance_ft"] = pd.to_numeric(df["hit_distance_sc"], errors="coerce")
    else:
        # Approximate distance in feet from pixel displacement (≈1 px per foot)
        df["distance_ft"] = np.sqrt(dx ** 2 + dy ** 2)

    df = df.dropna(subset=["angle_deg", "distance_ft"])
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Section probability analysis
# ---------------------------------------------------------------------------

def assign_sections(hr_df: pd.DataFrame, lf: int, cf: int, rf: int) -> pd.DataFrame:
    """
    Add a 'section_id' column to hr_df by mapping each HR's angle and distance
    to one of the 10 outfield sections.
    """
    from stadiums import SECTION_NAMES, NEAR_DEPTH, fence_distance_at_angle

    if hr_df.empty:
        return hr_df

    section_ids = []
    for _, row in hr_df.iterrows():
        angle = row["angle_deg"]
        dist  = row["distance_ft"]
        sid   = _classify_hr(angle, dist, lf, cf, rf, SECTION_NAMES, NEAR_DEPTH,
                              fence_distance_at_angle)
        section_ids.append(sid)

    hr_df = hr_df.copy()
    hr_df["section_id"] = section_ids
    return hr_df


def _classify_hr(
    angle: float,
    dist: float,
    lf: int,
    cf: int,
    rf: int,
    section_names,
    near_depth: float,
    fence_dist_fn,
) -> Optional[str]:
    """Map a single HR to a section_id, or None if out of fair territory."""
    # Outside fair territory (foul ball mis-classified, or tracking artifact)
    if angle < -45 or angle > 45:
        return None

    fence_d = fence_dist_fn(angle, lf, cf, rf)
    is_near = dist < (fence_d + near_depth)

    for sid, _label, a_min, a_max, near_band in section_names:
        if a_min <= angle < a_max and near_band == is_near:
            return sid

    # Edge: angle == 45 goes to RF-L or RF-U
    for sid, _label, a_min, a_max, near_band in section_names:
        if a_min <= angle <= a_max and near_band == is_near:
            return sid

    return None


def compute_probabilities(hr_df: pd.DataFrame) -> dict[str, float]:
    """
    Return a dict mapping section_id → probability (0.0–1.0).
    Probability = fraction of total HRs that landed in each section.
    """
    from stadiums import SECTION_NAMES

    total = len(hr_df.dropna(subset=["section_id"]))
    if total == 0:
        return {sid: 0.0 for sid, *_ in SECTION_NAMES}

    counts = hr_df["section_id"].value_counts()
    return {
        sid: float(counts.get(sid, 0)) / total
        for sid, *_ in SECTION_NAMES
    }
