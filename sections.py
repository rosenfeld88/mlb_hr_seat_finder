"""
Per-stadium outfield section definitions using real section numbers.

Tuple format: (section_id, display_label, angle_min, angle_max, r_inner, r_outer)
  angle_min / angle_max : degrees from CF  (−45 = LF foul pole, +45 = RF foul pole)
  r_inner   / r_outer   : feet beyond the outfield wall (inner / outer edge of section)

Angular positions are geometrically proportional to each stadium's real section layout.
Section IDs match the printed section numbers on each team's official seating charts.

CF gap (batter's eye): most stadiums have no seats in dead-CF roughly −7° to +7°.
Stadiums with CF seating (Coors Rockpile, etc.) fill that range explicitly.
"""

from __future__ import annotations

# Shared depth constants (feet beyond the outfield wall)
_L  = (0,  52)   # lower / main outfield (bleachers / reserved)
_FL = (0,  26)   # field level (right behind the wall, e.g. Crawford Boxes)
_ML = (26, 52)   # mid level (rows behind field level when both tiers exist)
_U  = (52, 90)   # upper deck / club level outfield


def _sec(sid: str, label: str, a0: float, a1: float, r: tuple) -> tuple:
    return (sid, label, a0, a1, r[0], r[1])


# ---------------------------------------------------------------------------
# STADIUM_SECTIONS
# Each entry: list of section tuples (section_id, label, a_min, a_max, r_in, r_out)
# Sections are ordered LF → RF (most-negative angle first).
# ---------------------------------------------------------------------------
STADIUM_SECTIONS: dict[str, list[tuple]] = {

    # ── American Family Field – Milwaukee Brewers ────────────────────────────
    # Lower outfield 101-108; Loge 201-206
    "American Family Field": [
        _sec("101","101", -45,-35, _L), _sec("102","102", -35,-25, _L),
        _sec("103","103", -25,-15, _L), _sec("104","104", -15, -7, _L),
        _sec("105","105",   7, 15, _L), _sec("106","106",  15, 25, _L),
        _sec("107","107",  25, 35, _L), _sec("108","108",  35, 45, _L),
        _sec("201","201", -45,-30, _U), _sec("202","202", -30,-15, _U),
        _sec("203","203", -15, -7, _U), _sec("204","204",   7, 15, _U),
        _sec("205","205",  15, 30, _U), _sec("206","206",  30, 45, _U),
    ],

    # ── Angel Stadium – Los Angeles Angels ──────────────────────────────────
    # Lower LF 246-243; Lower RF 207-210; Upper LF 446-443; Upper RF 407-410
    "Angel Stadium": [
        _sec("246","246", -45,-35, _L), _sec("245","245", -35,-25, _L),
        _sec("244","244", -25,-15, _L), _sec("243","243", -15, -7, _L),
        _sec("207","207",   7, 15, _L), _sec("208","208",  15, 25, _L),
        _sec("209","209",  25, 35, _L), _sec("210","210",  35, 45, _L),
        _sec("446","446", -45,-30, _U), _sec("445","445", -30,-15, _U),
        _sec("444","444", -15, -7, _U), _sec("407","407",   7, 15, _U),
        _sec("408","408",  15, 30, _U), _sec("409","409",  30, 45, _U),
    ],

    # ── Busch Stadium – St. Louis Cardinals ─────────────────────────────────
    # Main outfield: 140-159 (LF-RF); Upper: 241-258
    "Busch Stadium": [
        _sec("140","140", -45,-35, _L), _sec("141","141", -35,-25, _L),
        _sec("142","142", -25,-16, _L), _sec("143","143", -16, -7, _L),
        _sec("157","157",   7, 16, _L), _sec("158","158",  16, 25, _L),
        _sec("159","159",  25, 35, _L), _sec("160","160",  35, 45, _L),
        _sec("241","241", -45,-30, _U), _sec("242","242", -30,-15, _U),
        _sec("243","243", -15, -7, _U), _sec("256","256",   7, 15, _U),
        _sec("257","257",  15, 30, _U), _sec("258","258",  30, 45, _U),
    ],

    # ── Camden Yards – Baltimore Orioles ────────────────────────────────────
    # LF boxes 52-56; Bleachers 86-96; RF upper 352-356 / 388-392
    "Camden Yards": [
        _sec("52","52",   -45,-35, _L), _sec("53","53",   -35,-25, _L),
        _sec("54","54",   -25,-15, _L), _sec("55","55",   -15, -7, _L),
        _sec("86","86",     7, 17, _L), _sec("87","87",   17, 27, _L),
        _sec("88","88",    27, 35, _L), _sec("89","89",   35, 45, _L),
        _sec("352","352", -45,-30, _U), _sec("353","353", -30,-15, _U),
        _sec("354","354", -15, -7, _U), _sec("388","388",  7, 15, _U),
        _sec("389","389",  15, 30, _U), _sec("390","390", 30, 45, _U),
    ],

    # ── Chase Field – Arizona Diamondbacks ──────────────────────────────────
    # Lower 108-129; Upper 308-329
    "Chase Field": [
        _sec("108","108", -45,-35, _L), _sec("109","109", -35,-25, _L),
        _sec("110","110", -25,-15, _L), _sec("111","111", -15, -7, _L),
        _sec("126","126",   7, 15, _L), _sec("127","127",  15, 25, _L),
        _sec("128","128",  25, 35, _L), _sec("129","129",  35, 45, _L),
        _sec("308","308", -45,-30, _U), _sec("309","309", -30,-15, _U),
        _sec("310","310", -15, -7, _U), _sec("327","327",   7, 15, _U),
        _sec("328","328",  15, 30, _U), _sec("329","329",  30, 45, _U),
    ],

    # ── Citi Field – New York Mets ──────────────────────────────────────────
    # RF 101-109; LF Pepsi Porch 136-139; Upper 521-539
    "Citi Field": [
        _sec("136","136", -45,-35, _L), _sec("137","137", -35,-25, _L),
        _sec("138","138", -25,-15, _L), _sec("139","139", -15, -7, _L),
        _sec("101","101",   7, 17, _L), _sec("102","102",  17, 27, _L),
        _sec("103","103",  27, 36, _L), _sec("104","104",  36, 45, _L),
        _sec("532","532", -45,-30, _U), _sec("533","533", -30,-15, _U),
        _sec("534","534", -15, -7, _U), _sec("521","521",   7, 15, _U),
        _sec("522","522",  15, 30, _U), _sec("523","523",  30, 45, _U),
    ],

    # ── Citizens Bank Park – Philadelphia Phillies ───────────────────────────
    # LF The Yard 140-143; RF 147-153; Upper 341-354
    "Citizens Bank Park": [
        _sec("140","140", -45,-35, _L), _sec("141","141", -35,-25, _L),
        _sec("142","142", -25,-15, _L), _sec("143","143", -15, -7, _L),
        _sec("148","148",   7, 17, _L), _sec("149","149",  17, 27, _L),
        _sec("150","150",  27, 36, _L), _sec("151","151",  36, 45, _L),
        _sec("342","342", -45,-30, _U), _sec("343","343", -30,-15, _U),
        _sec("344","344", -15, -7, _U), _sec("349","349",   7, 15, _U),
        _sec("350","350",  15, 30, _U), _sec("351","351",  30, 45, _U),
    ],

    # ── Comerica Park – Detroit Tigers ──────────────────────────────────────
    # LF bleachers 119-131 (no RF bleachers; RF has standing room / corner)
    # Lower 119-127; Upper 339-345 (partial)
    "Comerica Park": [
        _sec("119","119", -45,-33, _L), _sec("120","120", -33,-22, _L),
        _sec("121","121", -22,-11, _L), _sec("122","122", -11, -7, _L),
        _sec("123","123",   7, 11, _L), _sec("124","124",  11, 22, _L),
        _sec("125","125",  22, 33, _L), _sec("126","126",  33, 45, _L),
        _sec("339","339", -45,-30, _U), _sec("340","340", -30,-15, _U),
        _sec("341","341", -15, -7, _U), _sec("342","342",   7, 15, _U),
        _sec("343","343",  15, 30, _U), _sec("344","344",  30, 45, _U),
    ],

    # ── Coors Field – Colorado Rockies ──────────────────────────────────────
    # Lower 101-116; The Rockpile (CF bleachers) 301-305; Upper 201-216
    "Coors Field": [
        _sec("101","101", -45,-35, _L), _sec("102","102", -35,-25, _L),
        _sec("103","103", -25,-16, _L), _sec("104","104", -16, -7, _L),
        # CF Rockpile (fans can sit here)
        _sec("302","302",  -7,  0, _L), _sec("303","303",   0,  7, _L),
        _sec("113","113",   7, 16, _L), _sec("114","114",  16, 25, _L),
        _sec("115","115",  25, 35, _L), _sec("116","116",  35, 45, _L),
        _sec("201","201", -45,-30, _U), _sec("202","202", -30,-15, _U),
        _sec("203","203", -15, -7, _U), _sec("213","213",   7, 15, _U),
        _sec("214","214",  15, 30, _U), _sec("215","215",  30, 45, _U),
        # Rockpile upper
        _sec("301","301",  -7,  7, _U),
    ],

    # ── Dodger Stadium – Los Angeles Dodgers ────────────────────────────────
    # LF Pavilion (PL), RF Pavilion (PR); Top Deck LF 1-10 / RF 15-24
    "Dodger Stadium": [
        _sec("PL6","Pav\nLF6", -45,-35, _L), _sec("PL5","Pav\nLF5", -35,-25, _L),
        _sec("PL4","Pav\nLF4", -25,-15, _L), _sec("PL3","Pav\nLF3", -15, -7, _L),
        _sec("PR3","Pav\nRF3",   7, 15, _L), _sec("PR4","Pav\nRF4",  15, 25, _L),
        _sec("PR5","Pav\nRF5",  25, 35, _L), _sec("PR6","Pav\nRF6",  35, 45, _L),
        _sec("TD4","Top\n4",  -45,-30, _U),  _sec("TD5","Top\n5",  -30,-15, _U),
        _sec("TD6","Top\n6",  -15, -7, _U),  _sec("TD15","Top\n15",  7, 15, _U),
        _sec("TD16","Top\n16", 15, 30, _U),  _sec("TD17","Top\n17", 30, 45, _U),
    ],

    # ── Fenway Park – Boston Red Sox ─────────────────────────────────────────
    # Green Monster seats GM1-GM8 (at wall, LF); LF field boxes 91-99;
    # Bleachers 33-43 (RF-to-CF); no upper deck over outfield
    "Fenway Park": [
        # Green Monster seats sit atop the LF wall (r=0 to 10, LF only)
        _sec("GM1","GM1",  -45,-40, (0, 10)), _sec("GM2","GM2",  -40,-35, (0, 10)),
        _sec("GM3","GM3",  -35,-30, (0, 10)), _sec("GM4","GM4",  -30,-25, (0, 10)),
        # LF lower field seats (behind the Monster)
        _sec("91","91",   -45,-40, (10, 52)), _sec("92","92",   -40,-35, (10, 52)),
        _sec("93","93",   -35,-30, (10, 52)), _sec("94","94",   -30,-25, (10, 52)),
        _sec("95","95",   -25,-15, _L),
        # RF/CF Bleachers 33-43 (from RF foul pole toward CF)
        _sec("43","43",    -15, -7, _L),
        _sec("42","42",      7, 15, _L), _sec("41","41",   15, 22, _L),
        _sec("40","40",     22, 29, _L), _sec("39","39",   29, 35, _L),
        _sec("38","38",     35, 39, _L), _sec("37","37",   39, 45, _L),
        # Roof deck boxes (LF-RF upper perimeter)
        _sec("RD1","Roof\n1", -45,-30, _U), _sec("RD2","Roof\n2", -30,-15, _U),
        _sec("RD3","Roof\n3", -15, -7, _U), _sec("RD4","Roof\n4",   7, 15, _U),
        _sec("RD5","Roof\n5",  15, 30, _U), _sec("RD6","Roof\n6",  30, 45, _U),
    ],

    # ── Globe Life Field – Texas Rangers ────────────────────────────────────
    # Lower 19-45; Upper 219-245
    "Globe Life Field": [
        _sec("19","19", -45,-35, _L), _sec("20","20", -35,-25, _L),
        _sec("21","21", -25,-15, _L), _sec("22","22", -15, -7, _L),
        _sec("41","41",   7, 15, _L), _sec("42","42",  15, 25, _L),
        _sec("43","43",  25, 35, _L), _sec("44","44",  35, 45, _L),
        _sec("219","219", -45,-30, _U), _sec("220","220", -30,-15, _U),
        _sec("221","221", -15, -7, _U), _sec("240","240",   7, 15, _U),
        _sec("241","241",  15, 30, _U), _sec("242","242",  30, 45, _U),
    ],

    # ── Great American Ball Park – Cincinnati Reds ───────────────────────────
    # Lower 111-128; Upper 411-428
    "Great American Ball Park": [
        _sec("111","111", -45,-35, _L), _sec("112","112", -35,-25, _L),
        _sec("113","113", -25,-15, _L), _sec("114","114", -15, -7, _L),
        _sec("125","125",   7, 15, _L), _sec("126","126",  15, 25, _L),
        _sec("127","127",  25, 35, _L), _sec("128","128",  35, 45, _L),
        _sec("411","411", -45,-30, _U), _sec("412","412", -30,-15, _U),
        _sec("413","413", -15, -7, _U), _sec("425","425",   7, 15, _U),
        _sec("426","426",  15, 30, _U), _sec("427","427",  30, 45, _U),
    ],

    # ── Guaranteed Rate Field – Chicago White Sox ───────────────────────────
    # Lower 107-130; Upper 506-526
    "Guaranteed Rate Field": [
        _sec("107","107", -45,-35, _L), _sec("108","108", -35,-25, _L),
        _sec("109","109", -25,-15, _L), _sec("110","110", -15, -7, _L),
        _sec("127","127",   7, 15, _L), _sec("128","128",  15, 25, _L),
        _sec("129","129",  25, 35, _L), _sec("130","130",  35, 45, _L),
        _sec("507","507", -45,-30, _U), _sec("508","508", -30,-15, _U),
        _sec("509","509", -15, -7, _U), _sec("523","523",   7, 15, _U),
        _sec("524","524",  15, 30, _U), _sec("525","525",  30, 45, _U),
    ],

    # ── Kauffman Stadium – Kansas City Royals ────────────────────────────────
    # Lower 122-142; Upper 422-442
    "Kauffman Stadium": [
        _sec("122","122", -45,-35, _L), _sec("123","123", -35,-25, _L),
        _sec("124","124", -25,-15, _L), _sec("125","125", -15, -7, _L),
        _sec("139","139",   7, 15, _L), _sec("140","140",  15, 25, _L),
        _sec("141","141",  25, 35, _L), _sec("142","142",  35, 45, _L),
        _sec("422","422", -45,-30, _U), _sec("423","423", -30,-15, _U),
        _sec("424","424", -15, -7, _U), _sec("438","438",   7, 15, _U),
        _sec("439","439",  15, 30, _U), _sec("440","440",  30, 45, _U),
    ],

    # ── loanDepot Park – Miami Marlins ──────────────────────────────────────
    # Lower 17-31; Upper 117-131
    "loanDepot Park": [
        _sec("17","17", -45,-35, _L), _sec("18","18", -35,-25, _L),
        _sec("19","19", -25,-15, _L), _sec("20","20", -15, -7, _L),
        _sec("28","28",   7, 15, _L), _sec("29","29",  15, 25, _L),
        _sec("30","30",  25, 35, _L), _sec("31","31",  35, 45, _L),
        _sec("117","117", -45,-30, _U), _sec("118","118", -30,-15, _U),
        _sec("119","119", -15, -7, _U), _sec("127","127",   7, 15, _U),
        _sec("128","128",  15, 30, _U), _sec("129","129",  30, 45, _U),
    ],

    # ── Minute Maid Park – Houston Astros ────────────────────────────────────
    # Crawford Boxes (LF, right at the wall): field level 100-104
    # Main LF-CF-RF: 105-120; Upper 300-315
    "Minute Maid Park": [
        # Crawford Boxes — tiny field-level sections right at the LF wall
        _sec("100","Crawf\n100", -45,-40, _FL),
        _sec("101","Crawf\n101", -40,-35, _FL),
        _sec("102","Crawf\n102", -35,-30, _FL),
        _sec("103","Crawf\n103", -30,-25, _FL),
        _sec("104","Crawf\n104", -25,-20, _FL),
        # Main lower (behind Crawford Boxes and around to RF)
        _sec("105","105", -45,-35, _ML), _sec("106","106", -35,-25, _ML),
        _sec("107","107", -25,-15, _ML), _sec("108","108", -15, -7, _ML),
        _sec("115","115",   7, 15, _L),  _sec("116","116",  15, 25, _L),
        _sec("117","117",  25, 35, _L),  _sec("118","118",  35, 45, _L),
        # Upper
        _sec("300","300", -45,-30, _U), _sec("301","301", -30,-15, _U),
        _sec("302","302", -15, -7, _U), _sec("311","311",   7, 15, _U),
        _sec("312","312",  15, 30, _U), _sec("313","313",  30, 45, _U),
    ],

    # ── Nationals Park – Washington Nationals ────────────────────────────────
    # Lower 135-150; Upper 301-316
    "Nationals Park": [
        _sec("135","135", -45,-35, _L), _sec("136","136", -35,-25, _L),
        _sec("137","137", -25,-15, _L), _sec("138","138", -15, -7, _L),
        _sec("146","146",   7, 15, _L), _sec("147","147",  15, 25, _L),
        _sec("148","148",  25, 35, _L), _sec("149","149",  35, 45, _L),
        _sec("301","301", -45,-30, _U), _sec("302","302", -30,-15, _U),
        _sec("303","303", -15, -7, _U), _sec("311","311",   7, 15, _U),
        _sec("312","312",  15, 30, _U), _sec("313","313",  30, 45, _U),
    ],

    # ── Oracle Park – San Francisco Giants ──────────────────────────────────
    # LF lower 127-132; RF Arcade 2-8 (close to water, r= field level);
    # Upper 313-326
    "Oracle Park": [
        _sec("127","127", -45,-35, _L), _sec("128","128", -35,-25, _L),
        _sec("129","129", -25,-15, _L), _sec("130","130", -15, -7, _L),
        # RF Arcade (right at the RF wall, fans lean over the water)
        _sec("2","Arcade\n2",    7, 15, _FL), _sec("3","Arcade\n3",  15, 22, _FL),
        _sec("4","Arcade\n4",   22, 29, _FL), _sec("5","Arcade\n5",  29, 36, _FL),
        _sec("6","Arcade\n6",   36, 45, _FL),
        # RF main level (behind the arcade)
        _sec("135","135",   7, 15, _ML), _sec("136","136",  15, 25, _ML),
        _sec("137","137",  25, 35, _ML), _sec("138","138",  35, 45, _ML),
        # Upper
        _sec("314","314", -45,-30, _U), _sec("315","315", -30,-15, _U),
        _sec("316","316", -15, -7, _U), _sec("319","319",   7, 15, _U),
        _sec("320","320",  15, 30, _U), _sec("321","321",  30, 45, _U),
    ],

    # ── Petco Park – San Diego Padres ────────────────────────────────────────
    # LF has Western Metal Supply Co. building (unique quirk); Lower 101-120; Upper 301-315
    "Petco Park": [
        _sec("101","101", -45,-35, _L), _sec("102","102", -35,-25, _L),
        _sec("103","103", -25,-15, _L), _sec("104","104", -15, -7, _L),
        _sec("115","115",   7, 15, _L), _sec("116","116",  15, 25, _L),
        _sec("117","117",  25, 35, _L), _sec("118","118",  35, 45, _L),
        _sec("301","301", -45,-30, _U), _sec("302","302", -30,-15, _U),
        _sec("303","303", -15, -7, _U), _sec("311","311",   7, 15, _U),
        _sec("312","312",  15, 30, _U), _sec("313","313",  30, 45, _U),
    ],

    # ── PNC Park – Pittsburgh Pirates ────────────────────────────────────────
    # Lower 139-152; Upper 325-338
    "PNC Park": [
        _sec("139","139", -45,-35, _L), _sec("140","140", -35,-25, _L),
        _sec("141","141", -25,-15, _L), _sec("142","142", -15, -7, _L),
        _sec("149","149",   7, 15, _L), _sec("150","150",  15, 25, _L),
        _sec("151","151",  25, 35, _L), _sec("152","152",  35, 45, _L),
        _sec("325","325", -45,-30, _U), _sec("326","326", -30,-15, _U),
        _sec("327","327", -15, -7, _U), _sec("334","334",   7, 15, _U),
        _sec("335","335",  15, 30, _U), _sec("336","336",  30, 45, _U),
    ],

    # ── Progressive Field – Cleveland Guardians ──────────────────────────────
    # LF 176-182; RF 101-107; Upper 476-482 / 501-507
    "Progressive Field": [
        _sec("176","176", -45,-35, _L), _sec("177","177", -35,-25, _L),
        _sec("178","178", -25,-15, _L), _sec("179","179", -15, -7, _L),
        _sec("101","101",   7, 15, _L), _sec("102","102",  15, 25, _L),
        _sec("103","103",  25, 35, _L), _sec("104","104",  35, 45, _L),
        _sec("476","476", -45,-30, _U), _sec("477","477", -30,-15, _U),
        _sec("478","478", -15, -7, _U), _sec("501","501",   7, 15, _U),
        _sec("502","502",  15, 30, _U), _sec("503","503",  30, 45, _U),
    ],

    # ── Rogers Centre – Toronto Blue Jays ────────────────────────────────────
    # Lower 126-144; Upper 530-543
    "Rogers Centre": [
        _sec("126","126", -45,-35, _L), _sec("127","127", -35,-25, _L),
        _sec("128","128", -25,-15, _L), _sec("129","129", -15, -7, _L),
        _sec("140","140",   7, 15, _L), _sec("141","141",  15, 25, _L),
        _sec("142","142",  25, 35, _L), _sec("143","143",  35, 45, _L),
        _sec("530","530", -45,-30, _U), _sec("531","531", -30,-15, _U),
        _sec("532","532", -15, -7, _U), _sec("537","537",   7, 15, _U),
        _sec("538","538",  15, 30, _U), _sec("539","539",  30, 45, _U),
    ],

    # ── Sutter Health Park – Sacramento Athletics ────────────────────────────
    # Minor-league park (Athletics temporary home); Lower 101-108; Upper 201-206
    "Sutter Health Park": [
        _sec("101","101", -45,-35, _L), _sec("102","102", -35,-25, _L),
        _sec("103","103", -25,-15, _L), _sec("104","104", -15, -7, _L),
        _sec("105","105",   7, 15, _L), _sec("106","106",  15, 25, _L),
        _sec("107","107",  25, 35, _L), _sec("108","108",  35, 45, _L),
        _sec("201","201", -45,-30, _U), _sec("202","202", -30, -7, _U),
        _sec("203","203",   7, 30, _U), _sec("204","204",  30, 45, _U),
    ],

    # ── T-Mobile Park – Seattle Mariners ────────────────────────────────────
    # Lower 150-170; Upper 340-355
    "T-Mobile Park": [
        _sec("150","150", -45,-35, _L), _sec("151","151", -35,-25, _L),
        _sec("152","152", -25,-15, _L), _sec("153","153", -15, -7, _L),
        _sec("165","165",   7, 15, _L), _sec("166","166",  15, 25, _L),
        _sec("167","167",  25, 35, _L), _sec("168","168",  35, 45, _L),
        _sec("340","340", -45,-30, _U), _sec("341","341", -30,-15, _U),
        _sec("342","342", -15, -7, _U), _sec("349","349",   7, 15, _U),
        _sec("350","350",  15, 30, _U), _sec("351","351",  30, 45, _U),
    ],

    # ── Target Field – Minnesota Twins ──────────────────────────────────────
    # Lower 102-120; Upper 206-219
    "Target Field": [
        _sec("102","102", -45,-35, _L), _sec("103","103", -35,-25, _L),
        _sec("104","104", -25,-15, _L), _sec("105","105", -15, -7, _L),
        _sec("116","116",   7, 15, _L), _sec("117","117",  15, 25, _L),
        _sec("118","118",  25, 35, _L), _sec("119","119",  35, 45, _L),
        _sec("206","206", -45,-30, _U), _sec("207","207", -30,-15, _U),
        _sec("208","208", -15, -7, _U), _sec("215","215",   7, 15, _U),
        _sec("216","216",  15, 30, _U), _sec("217","217",  30, 45, _U),
    ],

    # ── Tropicana Field – Tampa Bay Rays ────────────────────────────────────
    # Lower 125-145; Upper 317-331
    "Tropicana Field": [
        _sec("125","125", -45,-35, _L), _sec("126","126", -35,-25, _L),
        _sec("127","127", -25,-15, _L), _sec("128","128", -15, -7, _L),
        _sec("140","140",   7, 15, _L), _sec("141","141",  15, 25, _L),
        _sec("142","142",  25, 35, _L), _sec("143","143",  35, 45, _L),
        _sec("317","317", -45,-30, _U), _sec("318","318", -30,-15, _U),
        _sec("319","319", -15, -7, _U), _sec("326","326",   7, 15, _U),
        _sec("327","327",  15, 30, _U), _sec("328","328",  30, 45, _U),
    ],

    # ── Truist Park – Atlanta Braves ─────────────────────────────────────────
    # Lower 108-124; Upper 251-263
    "Truist Park": [
        _sec("108","108", -45,-35, _L), _sec("109","109", -35,-25, _L),
        _sec("110","110", -25,-15, _L), _sec("111","111", -15, -7, _L),
        _sec("120","120",   7, 15, _L), _sec("121","121",  15, 25, _L),
        _sec("122","122",  25, 35, _L), _sec("123","123",  35, 45, _L),
        _sec("251","251", -45,-30, _U), _sec("252","252", -30,-15, _U),
        _sec("253","253", -15, -7, _U), _sec("259","259",   7, 15, _U),
        _sec("260","260",  15, 30, _U), _sec("261","261",  30, 45, _U),
    ],

    # ── Wrigley Field – Chicago Cubs ─────────────────────────────────────────
    # Famous ivy-covered bleachers. No upper deck in the outfield.
    # LF bleachers 501-505; RF bleachers 506-511. No CF seats (scoreboard).
    "Wrigley Field": [
        _sec("501","501", -45,-36, _L), _sec("502","502", -36,-27, _L),
        _sec("503","503", -27,-18, _L), _sec("504","504", -18, -7, _L),
        _sec("506","506",   7, 18, _L), _sec("507","507",  18, 27, _L),
        _sec("508","508",  27, 36, _L), _sec("509","509",  36, 45, _L),
    ],

    # ── Yankee Stadium – New York Yankees ────────────────────────────────────
    # RF bleachers 101-107 (lower); LF bleachers 201-207 (lower);
    # Upper outfield 303-316
    "Yankee Stadium": [
        _sec("201","201", -45,-36, _L), _sec("202","202", -36,-27, _L),
        _sec("203","203", -27,-18, _L), _sec("204","204", -18, -7, _L),
        _sec("101","101",   7, 18, _L), _sec("102","102",  18, 27, _L),
        _sec("103","103",  27, 36, _L), _sec("104","104",  36, 45, _L),
        _sec("313","313", -45,-30, _U), _sec("314","314", -30,-15, _U),
        _sec("315","315", -15, -7, _U), _sec("305","305",   7, 15, _U),
        _sec("306","306",  15, 30, _U), _sec("307","307",  30, 45, _U),
    ],
}


def get_sections(stadium_name: str) -> list[tuple]:
    """
    Return the outfield section list for a stadium.
    Each tuple: (section_id, label, angle_min, angle_max, r_inner, r_outer)
    """
    return STADIUM_SECTIONS.get(stadium_name, [])


def get_section_ids(stadium_name: str) -> list[str]:
    """Return just the section IDs for a stadium, sorted by angle."""
    sections = get_sections(stadium_name)
    return [s[0] for s in sorted(sections, key=lambda s: (s[4], s[2]))]


def classify_hr(
    angle_deg: float,
    dist_ft: float,
    lf: int,
    cf: int,
    rf: int,
    sections: list[tuple],
) -> str | None:
    """
    Map a home run (angle_deg, dist_ft from home plate) to a section_id.

    Returns None if the HR does not land in any defined section (e.g. foul ball,
    CF batter's eye gap, or short/long artifact).
    """
    from stadiums import fence_distance_at_angle

    if angle_deg < -45 or angle_deg > 45:
        return None

    wall_d = fence_distance_at_angle(angle_deg, lf, cf, rf)
    r_off  = dist_ft - wall_d   # feet beyond the wall

    for sid, _lbl, a_min, a_max, r_in, r_out in sections:
        if a_min <= angle_deg <= a_max and r_in <= r_off < r_out:
            return sid

    return None
