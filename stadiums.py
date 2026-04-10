"""
MLB stadium definitions and outfield section geometry.

Coordinate system used throughout:
  - Origin at home plate (0, 0)
  - Positive Y points toward center field
  - Positive X points toward right field
  - Angles measured from CF (0°): negative = LF side, positive = RF side
  - Foul lines are at exactly ±45° from center
"""

from __future__ import annotations
import numpy as np

# ---------------------------------------------------------------------------
# Stadium data
# team_id   : MLB Stats API team ID
# team      : full franchise name
# abbrev    : abbreviation used by Baseball Savant / pybaseball statcast()
# lf/cf/rf  : distance to outfield wall in feet at the foul pole / CF / foul pole
# ---------------------------------------------------------------------------
MLB_STADIUMS: dict[str, dict] = {
    "American Family Field": {
        "team_id": 158, "team": "Milwaukee Brewers",    "abbrev": "MIL",
        "lf": 344, "cf": 400, "rf": 345,
    },
    "Angel Stadium": {
        "team_id": 108, "team": "Los Angeles Angels",   "abbrev": "LAA",
        "lf": 330, "cf": 400, "rf": 330,
    },
    "Busch Stadium": {
        "team_id": 138, "team": "St. Louis Cardinals",  "abbrev": "STL",
        "lf": 336, "cf": 400, "rf": 335,
    },
    "Camden Yards": {
        "team_id": 110, "team": "Baltimore Orioles",    "abbrev": "BAL",
        "lf": 333, "cf": 400, "rf": 318,
    },
    "Chase Field": {
        "team_id": 109, "team": "Arizona Diamondbacks", "abbrev": "ARI",
        "lf": 330, "cf": 407, "rf": 334,
    },
    "Citi Field": {
        "team_id": 121, "team": "New York Mets",        "abbrev": "NYM",
        "lf": 335, "cf": 408, "rf": 330,
    },
    "Citizens Bank Park": {
        "team_id": 143, "team": "Philadelphia Phillies","abbrev": "PHI",
        "lf": 329, "cf": 401, "rf": 330,
    },
    "Comerica Park": {
        "team_id": 116, "team": "Detroit Tigers",       "abbrev": "DET",
        "lf": 345, "cf": 420, "rf": 330,
    },
    "Coors Field": {
        "team_id": 115, "team": "Colorado Rockies",     "abbrev": "COL",
        "lf": 347, "cf": 415, "rf": 350,
    },
    "Dodger Stadium": {
        "team_id": 119, "team": "Los Angeles Dodgers",  "abbrev": "LAD",
        "lf": 330, "cf": 395, "rf": 330,
    },
    "Fenway Park": {
        "team_id": 111, "team": "Boston Red Sox",       "abbrev": "BOS",
        "lf": 310, "cf": 420, "rf": 302,
    },
    "Globe Life Field": {
        "team_id": 140, "team": "Texas Rangers",        "abbrev": "TEX",
        "lf": 329, "cf": 407, "rf": 326,
    },
    "Great American Ball Park": {
        "team_id": 113, "team": "Cincinnati Reds",      "abbrev": "CIN",
        "lf": 328, "cf": 404, "rf": 325,
    },
    "Guaranteed Rate Field": {
        "team_id": 145, "team": "Chicago White Sox",    "abbrev": "CWS",
        "lf": 330, "cf": 400, "rf": 335,
    },
    "Kauffman Stadium": {
        "team_id": 118, "team": "Kansas City Royals",   "abbrev": "KC",
        "lf": 330, "cf": 410, "rf": 330,
    },
    "loanDepot Park": {
        "team_id": 146, "team": "Miami Marlins",        "abbrev": "MIA",
        "lf": 344, "cf": 407, "rf": 335,
    },
    "Minute Maid Park": {
        "team_id": 117, "team": "Houston Astros",       "abbrev": "HOU",
        "lf": 315, "cf": 409, "rf": 326,
    },
    "Nationals Park": {
        "team_id": 120, "team": "Washington Nationals", "abbrev": "WSH",
        "lf": 336, "cf": 402, "rf": 335,
    },
    "Oracle Park": {
        "team_id": 137, "team": "San Francisco Giants", "abbrev": "SF",
        "lf": 339, "cf": 399, "rf": 309,
    },
    "Petco Park": {
        "team_id": 135, "team": "San Diego Padres",     "abbrev": "SD",
        "lf": 336, "cf": 396, "rf": 322,
    },
    "PNC Park": {
        "team_id": 134, "team": "Pittsburgh Pirates",   "abbrev": "PIT",
        "lf": 325, "cf": 399, "rf": 320,
    },
    "Progressive Field": {
        "team_id": 114, "team": "Cleveland Guardians",  "abbrev": "CLE",
        "lf": 325, "cf": 405, "rf": 325,
    },
    "Rogers Centre": {
        "team_id": 141, "team": "Toronto Blue Jays",    "abbrev": "TOR",
        "lf": 328, "cf": 400, "rf": 328,
    },
    "Sutter Health Park": {
        "team_id": 133, "team": "Sacramento Athletics", "abbrev": "OAK",
        "lf": 330, "cf": 400, "rf": 325,
    },
    "T-Mobile Park": {
        "team_id": 136, "team": "Seattle Mariners",     "abbrev": "SEA",
        "lf": 331, "cf": 401, "rf": 326,
    },
    "Target Field": {
        "team_id": 142, "team": "Minnesota Twins",      "abbrev": "MIN",
        "lf": 339, "cf": 411, "rf": 328,
    },
    "Tropicana Field": {
        "team_id": 139, "team": "Tampa Bay Rays",       "abbrev": "TB",
        "lf": 315, "cf": 404, "rf": 322,
    },
    "Truist Park": {
        "team_id": 144, "team": "Atlanta Braves",       "abbrev": "ATL",
        "lf": 335, "cf": 400, "rf": 325,
    },
    "Wrigley Field": {
        "team_id": 112, "team": "Chicago Cubs",         "abbrev": "CHC",
        "lf": 355, "cf": 400, "rf": 353,
    },
    "Yankee Stadium": {
        "team_id": 147, "team": "New York Yankees",     "abbrev": "NYY",
        "lf": 318, "cf": 408, "rf": 314,
    },
}

STADIUM_NAMES = sorted(MLB_STADIUMS.keys())


def fence_distance_at_angle(angle_deg: float, lf: int, cf: int, rf: int) -> float:
    """
    Return the interpolated outfield fence distance (feet) at angle_deg from CF.

    Uses a quadratic fit through (−45°, lf), (0°, cf), (+45°, rf) so the wall
    passes through all three anchor points exactly.
    """
    a = (lf + rf - 2 * cf) / (2 * 45.0 ** 2)
    b = (rf - lf) / (2 * 45.0)
    c = float(cf)
    return a * angle_deg ** 2 + b * angle_deg + c


def wall_curve(lf: int, cf: int, rf: int, n: int = 200) -> tuple[np.ndarray, np.ndarray]:
    """
    Return (x, y) arrays for the outfield wall arc in feet-from-home-plate coords.
    """
    angles = np.linspace(-45, 45, n)
    dists  = np.array([fence_distance_at_angle(a, lf, cf, rf) for a in angles])
    rad    = np.radians(angles)
    x = dists * np.sin(rad)
    y = dists * np.cos(rad)
    return x, y


def section_polygon(
    angle_min: float, angle_max: float, r_inner_fn, r_outer_fn, n: int = 30
) -> tuple[np.ndarray, np.ndarray]:
    """
    Build a closed polygon (x, y) for one section of the stands.

    r_inner_fn(angle_deg) -> inner radius (fence distance)
    r_outer_fn(angle_deg) -> outer radius (fence + depth)
    """
    angles_fwd = np.linspace(angle_min, angle_max, n)
    angles_rev = angles_fwd[::-1]

    def to_xy(angles, r_fn):
        rad = np.radians(angles)
        r   = np.array([r_fn(a) for a in angles])
        return r * np.sin(rad), r * np.cos(rad)

    xi, yi = to_xy(angles_fwd, r_inner_fn)
    xo, yo = to_xy(angles_rev, r_outer_fn)

    x = np.concatenate([xi, xo, [xi[0]]])
    y = np.concatenate([yi, yo, [yi[0]]])
    return x, y
