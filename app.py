"""
app.py — Bhagyagraha Streamlit Application

Provides a web UI for the horoscope calculator with two tabs:
  Tab 1 – Horoscope: structured Python output (tables, charts)
  Tab 2 – HTML Report: C-style single-page report, downloadable as PDF

Run with:
  streamlit run app.py
"""

import datetime as dt
import io
import math
import os
import re
import sys
from collections import defaultdict

import streamlit as st
import streamlit.components.v1 as components

# ── Computation modules ────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
import constants as cn
import functions as fn
import shadbala as sb

# ── Name tables (same as astro.py) ────────────────────────────────────────────

GRAHA_NAMES = ["LAGN", "SUN", "MOON", "MARS", "MERC", "JUPT",
               "VENU", "SATN", "URAN", "NEPT", "RAHU", "KETU"]

GRAHA_DISPLAY = ["Lagn", "Sun", "Moon", "Mars", "Merc", "Jupt",
                 "Venu", "Satn", "Uran", "Nept", "Rahu", "Ketu"]

NAKSHATRA = [
    "Aswini", "Bharani", "Krittiga", "Rohini",
    "Mrigasirsha", "Ardra", "Punarvasu", "Pushyam",
    "Aslesha", "Makam", "Pooram", "Uttiram",
    "Hastham", "Chitrai", "Swathi", "Vishakam",
    "Anusham", "Jyeshta", "Moolam", "Purvashada",
    "Uthirashada", "Sravanam", "Dhanishta", "Sadabhisha",
    "Poorattathi", "Uttirattathi", "Revathi",
]

RASI_NAMES = [
    "Mesha", "Rishabha", "Mithuna", "Kataka",
    "Simha", "Kanya", "Tula", "Vrischika",
    "Dhanus", "Makara", "Kumbha", "Meena",
]

TAMIL_MONTH = [
    "Chittirai", "Vaikasi", "Aaani", "Aadi",
    "Aavani", "Purattaasi", "Aippasi", "Kaarthigai",
    "Maargazhi", "Thai", "Maasi", "Panguni",
]

TAMIL_YEAR = [
    "Prabhava", "Vibhava", "Sukla", "Pramodha", "Prajoth", "Aangirasa",
    "Sreemuga", "Bhava", "Yuva", "Thaatru", "Easwara", "Bagudhanya",
    "Pramaadhi", "Vikrama", "Virusha", "Chitrabaanu", "Subaanu", "Dhaarana",
    "Paarthiva", "Vyaya", "Sarvajith", "Sarvadhaari", "Virodhi", "Vikrudhi",
    "Gara", "Nandhana", "Vijaya", "Jaya", "Manmadha", "Dhurmuga",
    "Hemalamba", "Vilambhi", "Vigaari", "Saarvari", "Plava", "Subhakruth",
    "Sobhakruth", "Krodhi", "Visuvaavaga", "Paraabhava", "Plavanga", "Keelaga",
    "Sowmya", "Saadhaarana", "Virodha", "Paridhaavi", "Pramaadheesa", "Aanandha",
    "Raakshasa", "Nala", "Bingala", "Kaalayuktha", "Siddhaartha", "Raudhra",
    "Dhurmadhi", "Thundhubi", "Rudhirodh", "Rakthaaksha", "Krodhana", "Akshaya",
]

SAKA_MONTH = [
    "Chaitra", "Vaisaka", "Jyaistha", "Asadaha",
    "Sravana", "Bhadra", "Asvina", "Kartika",
    "Agrahayana", "Pausa", "Magha", "Phalguna",
]

THITHI = [
    "Prathamai", "Dwithiai", "Thrithiai", "Chathurthi",
    "Panchami", "Sashti", "Sapthami", "Ashtami",
    "Navami", "Dasami", "Ekadasi", "Dwadasi",
    "Thrayodasi", "Chaturdasi", "Poornima", "Amavasya",
]

YOGAM = [
    "Viskumbha", "Priti", "Ayusman", "Saubhagya", "Sobhana",
    "Atiganda", "Sukarma", "Dhriti", "Sula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Siva",
    "Siddha", "Sadhya", "Subha", "Sukla", "Brahma",
    "Indra", "Vaidhriti",
]

KARANAM = [
    "Bava", "Balava", "Kaulava", "Taitila",
    "Gara", "Vanij", "Vishti",
    "Sakuni", "Chatuspada", "Naaga", "Kinstughna",
]

WDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday",
         "Thursday", "Friday", "Saturday"]

SHAD_LABELS = ["Sun", "Moon", "Mars", "Merc", "Jupt", "Venus", "Saturn"]

# ── City presets (lat, lon in decimal degrees) ────────────────────────────────
CITIES = {
    "Custom": None,
    "Chennai":             {"lat": 13.0827, "lon": 80.2707, "lat_dir": "N", "lon_dir": "E"},
    "Salem":               {"lat": 11.6643, "lon": 78.1460, "lat_dir": "N", "lon_dir": "E"},
    "Coimbatore":          {"lat": 11.0168, "lon": 76.9558, "lat_dir": "N", "lon_dir": "E"},
    "Madurai":             {"lat":  9.9252, "lon": 78.1198, "lat_dir": "N", "lon_dir": "E"},
    "Bengaluru":           {"lat": 12.9716, "lon": 77.5946, "lat_dir": "N", "lon_dir": "E"},
    "Hyderabad":           {"lat": 17.3850, "lon": 78.4867, "lat_dir": "N", "lon_dir": "E"},
    "Mumbai":              {"lat": 19.0760, "lon": 72.8777, "lat_dir": "N", "lon_dir": "E"},
    "Pune":                {"lat": 18.5204, "lon": 73.8567, "lat_dir": "N", "lon_dir": "E"},
    "Delhi":               {"lat": 28.6139, "lon": 77.2090, "lat_dir": "N", "lon_dir": "E"},
    "Jaipur":              {"lat": 26.9124, "lon": 75.7873, "lat_dir": "N", "lon_dir": "E"},
    "Kolkata":             {"lat": 22.5726, "lon": 88.3639, "lat_dir": "N", "lon_dir": "E"},
    "Varanasi":            {"lat": 25.3176, "lon": 82.9739, "lat_dir": "N", "lon_dir": "E"},
    "Ahmedabad":           {"lat": 23.0225, "lon": 72.5714, "lat_dir": "N", "lon_dir": "E"},
    "Thiruvananthapuram":  {"lat":  8.5241, "lon": 76.9366, "lat_dir": "N", "lon_dir": "E"},
    "Kochi":               {"lat":  9.9312, "lon": 76.2673, "lat_dir": "N", "lon_dir": "E"},
    "Vijayawada":          {"lat": 16.5062, "lon": 80.6480, "lat_dir": "N", "lon_dir": "E"},
    "Colombo":             {"lat":  6.9271, "lon": 79.8612, "lat_dir": "N", "lon_dir": "E"},
    "London":              {"lat": 51.5074, "lon":  0.1278, "lat_dir": "N", "lon_dir": "W"},
    "New York":            {"lat": 40.7128, "lon": 74.0060, "lat_dir": "N", "lon_dir": "W"},
    "Singapore":           {"lat":  1.3521, "lon": 103.8198,"lat_dir": "N", "lon_dir": "E"},
    "Dubai":               {"lat": 25.2048, "lon": 55.2708, "lat_dir": "N", "lon_dir": "E"},
}

# ── Timezone presets (seconds offset from GMT) ────────────────────────────────
TIMEZONES = {
    "IST  — India          (+5:30)":   5 * 3600 + 30 * 60,
    "GMT  — London         (+0:00)":   0,
    "CET  — Paris / Berlin (+1:00)":   1 * 3600,
    "EET  — Athens / Cairo (+2:00)":   2 * 3600,
    "MSK  — Moscow         (+3:00)":   3 * 3600,
    "GST  — Dubai          (+4:00)":   4 * 3600,
    "PKT  — Karachi        (+5:00)":   5 * 3600,
    "BST  — Dhaka          (+6:00)":   6 * 3600,
    "ICT  — Bangkok        (+7:00)":   7 * 3600,
    "CST  — China          (+8:00)":   8 * 3600,
    "JST  — Japan          (+9:00)":   9 * 3600,
    "AEST — Sydney        (+10:00)":  10 * 3600,
    "EST  — New York       (-5:00)":  -5 * 3600,
    "CST  — Chicago        (-6:00)":  -6 * 3600,
    "MST  — Denver         (-7:00)":  -7 * 3600,
    "PST  — Los Angeles    (-8:00)":  -8 * 3600,
}

# Vimsottari Dasa — lord and period (years) for each nakshatra (cycle of 9, repeated)
DASA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars",
              "Rahu", "Jupiter", "Saturn", "Mercury"]
DASA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]

# South Indian chart: fixed grid positions → sign index (0-11)
# (row, col) → sign
SOUTH_INDIAN_GRID = {
    (0,0): 11, (0,1): 0,  (0,2): 1,  (0,3): 2,
    (1,0): 10,                        (1,3): 3,
    (2,0): 9,                         (2,3): 4,
    (3,0): 8,  (3,1): 7,  (3,2): 6,  (3,3): 5,
}
# Reverse map: sign → (row, col)
SIGN_TO_CELL = {v: k for k, v in SOUTH_INDIAN_GRID.items()}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _nakshatra_pada(degs):
    nak  = min(int(degs / (360.0 / 27)), 26)
    rem  = degs - nak * (360.0 / 27)
    pada = int(rem / (360.0 / 108)) + 1
    return nak, pada


def _dasa_balance(moon_degs):
    """Return (lord_name, Y, M, D) for the Vimsottari dasa balance at birth."""
    nak_width = 360.0 / 27
    nak_idx   = min(int(moon_degs / nak_width), 26)
    nak_start = nak_idx * nak_width
    frac_elapsed   = (moon_degs - nak_start) / nak_width
    frac_remaining = 1.0 - frac_elapsed

    lord_idx    = nak_idx % 9
    lord        = DASA_LORDS[lord_idx]
    bal_years   = frac_remaining * DASA_YEARS[lord_idx]

    y = int(bal_years)
    m = int((bal_years - y) * 12)
    d = round(((bal_years - y) * 12 - m) * 30)
    return lord, y, m, d


def _full_dasa_table(moon_degs, birth_dt):
    """Build full 120-year Vimsottari Dasa/Bukti table starting from birth."""
    nak_width = 360.0 / 27
    nak_idx   = min(int(moon_degs / nak_width), 26)
    nak_start = nak_idx * nak_width
    frac_remaining = 1.0 - (moon_degs - nak_start) / nak_width
    lord_idx = nak_idx % 9
    current  = birth_dt + dt.timedelta(
        days=frac_remaining * DASA_YEARS[lord_idx] * 365.25)
    table = []
    for d in range(9):
        di = (lord_idx + d) % 9
        buktis = []
        for b in range(9):
            bi = (di + b) % 9
            current = current + dt.timedelta(
                days=DASA_YEARS[di] * DASA_YEARS[bi] / 120.0 * 365.25)
            buktis.append((DASA_LORDS[bi], current.strftime("%Y-%m-%d")))
        table.append({"dasa": DASA_LORDS[di], "buktis": buktis})
    return table


def _vel_str(v):
    """Format velocity (degrees/day) as 'D-MM-SS'."""
    if v is None:
        return "- - -"
    d = int(v)
    m = int((v - d) * 60)
    s = int(((v - d) * 60 - m) * 60)
    return f"{d}-{m:02d}-{s:02d}"


def _ramc_hms(r):
    """RAMC degrees → sidereal time string H:MM:SS."""
    h = int(r / 15)
    m = int((r / 15 - h) * 60)
    s = int(((r / 15 - h) * 60 - m) * 60)
    return f"{h}H-{m:02d}M-{s:02d}S"


def _dt_to_hrs(d):
    return d.hour + d.minute / 60.0 + d.second / 3600.0


# ── Core computation ──────────────────────────────────────────────────────────

def compute(input_params):
    """Run all calculations; return a single structured result dict."""

    sun_params  = fn.get_sun_params(input_params)
    moon_params = fn.get_moon_params(input_params, sun_params)
    lagn_params = fn.get_lagn_params(input_params, sun_params)
    seven       = fn.get_seven_planets(sun_params, moon_params)

    planet_names_order = ["LAGN", "SUN", "MOON", "MARS", "MERCURY",
                          "JUPITER", "VENUS", "SATURN", "URANUS", "NEPTUNE",
                          "RAHU", "KETU"]

    planet_degs = []
    for nm in planet_names_order:
        if nm == "LAGN":
            planet_degs.append(lagn_params["lagn"])
        elif nm == "SUN":
            planet_degs.append(sun_params["true_long"])
        elif nm == "MOON":
            planet_degs.append(moon_params["moon"])
        elif nm == "RAHU":
            planet_degs.append(moon_params["rahu"])
        elif nm == "KETU":
            planet_degs.append(moon_params["ketu"])
        else:
            planet_degs.append(seven[nm]["true_long"])

    # ── Velocity, latitude, retrograde ────────────────────────────────────────
    planet_velocity   = [None] * 12
    planet_latitude   = [None] * 12
    planet_retrograde = [False] * 12

    planet_velocity[1]   = abs(sun_params.get("hvel", 1.0))   # Sun helio vel
    planet_latitude[1]   = 0.0
    planet_velocity[2]   = 13.18                               # Moon ~avg deg/day
    planet_latitude[2]   = 0.0

    for _idx, _nm in zip(
        [3, 4, 5, 6, 7, 8, 9],
        ["MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "URANUS", "NEPTUNE"]
    ):
        _gvel = seven[_nm].get("gvel", 0.0)
        planet_velocity[_idx]   = abs(_gvel)
        planet_latitude[_idx]   = seven[_nm].get("lat", 0.0)
        planet_retrograde[_idx] = (_gvel < 0)

    planet_retrograde[10] = True   # Rahu always retrograde
    planet_retrograde[11] = True   # Ketu always retrograde

    ashta = sb.compute_ashtavarga(planet_degs)

    prec_degs   = sun_params["prec"]
    ramc_degs   = lagn_params["ramc"]
    lagn_degs   = lagn_params["lagn"]
    lat_degs    = input_params["lat_degs"]
    lat_dirn    = input_params["lat_dirn"]
    south_hemi  = bool(re.match(r"s|(south)", lat_dirn, re.IGNORECASE))

    nirayana_dhasa  = fn.get_culm_point(ramc_degs, lat_degs, prec_degs, south_hemi)
    house_positions = fn.get_house_positions(lagn_degs, nirayana_dhasa,
                                             lat_degs, ramc_degs, prec_degs,
                                             south_hemi)

    bhava_positions, bhava1, bhava2 = fn.get_bhava_positions(house_positions, planet_degs)
    navamsa_positions = fn.get_navamsa_positions(planet_degs)
    rasi_positions    = fn.get_rasi_positons(planet_degs)

    tamil_day, tamil_month, tamil_year = fn.calc_tamil_date(input_params)
    saka_day, saka_month, saka_year    = fn.calc_saka_date(input_params["in_datetime"])
    kali_year                          = fn.get_kali_year(saka_year)

    yogam, karanam, thithi = fn.get_yogam_karanam_thithi(
        sun_params["true_long"], moon_params["moon"])

    birth_day = input_params["in_datetime"].weekday()
    birth_day = (birth_day + 1) % 7

    epoch_days = sun_params["d_epoch"]
    kali_dina  = int(epoch_days) + cn.kali_day

    p7_degs   = [planet_degs[i] for i in [1, 2, 3, 4, 5, 6, 7]]
    p7_signs  = [int(d // 30) for d in p7_degs]
    p7_deg_in = [d % 30 for d in p7_degs]
    p7_min_in = [int((d % 30 - int(d % 30)) * 60) for d in p7_degs]

    all_signs   = [int(d // 30) for d in planet_degs]
    all_deg_in  = [d % 30 for d in planet_degs]
    all_min_in  = [int((d % 30 - int(d % 30)) * 60) for d in planet_degs]
    all_navamsa = [int(n) for n in navamsa_positions]

    helio_5 = [
        seven["MARS"]["helio_long"],
        seven["MERCURY"]["helio_long"],
        seven["JUPITER"]["helio_long"],
        seven["VENUS"]["helio_long"],
        seven["SATURN"]["helio_long"],
    ]

    local_hrs   = _dt_to_hrs(sun_params["local_time"])
    sunrise_hrs = _dt_to_hrs(sun_params["rise"])
    sunset_hrs  = _dt_to_hrs(sun_params["set"])

    shad = sb.compute_shadbala(
        p7_degs, all_signs, all_deg_in, all_min_in, all_navamsa,
        helio_5, house_positions, bhava1, bhava2,
        local_hrs, sunrise_hrs, sunset_hrs,
        kali_dina, birth_day, prec_degs,
    )

    bhava_bala = sb.compute_bhava_bala(
        shad["total"], p7_degs, house_positions, bhava1, bhava2)

    mutual = sb.compute_mutual_disp(all_signs, all_navamsa)

    # Paksham / Thithi display
    paksha = "Krishna" if thithi >= 15 else "Shukla"
    thithi_idx = (thithi - 15) if thithi >= 15 else thithi
    if thithi_idx == 14:
        thithi_idx = 15

    # Janma Nakshatra (birth star) from Moon
    moon_degs = planet_degs[2]
    janma_nak_idx, janma_pada = _nakshatra_pada(moon_degs)
    janma_nakshatra = NAKSHATRA[janma_nak_idx]

    # Vimsottari Dasa balance
    dasa_lord, dasa_y, dasa_m, dasa_d = _dasa_balance(moon_degs)

    return {
        "input":              input_params,
        "planet_degs":        planet_degs,
        "navamsa_positions":  navamsa_positions,
        "rasi_positions":     rasi_positions,
        "house_positions":    house_positions,
        "bhava_positions":    bhava_positions,
        "sun_params":         sun_params,
        "moon_params":        moon_params,
        "planet_velocity":    planet_velocity,
        "planet_latitude":    planet_latitude,
        "planet_retrograde":  planet_retrograde,
        "sidereal_time":      ramc_degs,
        "ayanamsa":           prec_degs,
        "ashtavarga":         ashta,
        "calendar": {
            "paksham":         f"{paksha} Paksham",
            "thithi":          THITHI[thithi_idx],
            "yogam":           YOGAM[yogam],
            "karanam":         KARANAM[karanam],
            "tamil_day":       tamil_day,
            "tamil_month":     TAMIL_MONTH[tamil_month],
            "tamil_year":      TAMIL_YEAR[tamil_year % 60],
            "saka_day":        saka_day,
            "saka_month":      SAKA_MONTH[saka_month],
            "saka_year":       saka_year,
            "kali_year":       kali_year,
            "weekday":         WDAYS[birth_day],
            "sunrise":         sun_params["rise"],
            "sunset":          sun_params["set"],
            "janma_nakshatra": janma_nakshatra,
            "janma_pada":      janma_pada,
            "dasa_lord":       dasa_lord,
            "dasa_y":          dasa_y,
            "dasa_m":          dasa_m,
            "dasa_d":          dasa_d,
            "dasa_table":      _full_dasa_table(moon_degs, input_params["in_datetime"]),
        },
        "shad":       shad,
        "bhava_bala": bhava_bala,
        "mutual":     mutual,
    }


# ── South Indian chart HTML ───────────────────────────────────────────────────

def _south_indian_chart_html(by_sign, label, cell_size=90):
    """Generate HTML for a 4×4 South Indian chart table."""
    rows = []
    for r in range(4):
        cells = []
        for c in range(4):
            # Skip the centre 2×2 (handled by rowspan/colspan)
            if r in (1, 2) and c in (1, 2):
                continue
            sign = SOUTH_INDIAN_GRID.get((r, c))
            planets_here = "<br>".join(by_sign.get(sign, []))
            # Centre label spanning rows 1-2, cols 1-2
            if r == 1 and c == 1:
                cells.append(
                    f'<td align="center" rowspan="2" colspan="2" '
                    f'style="font-weight:bold;font-size:14px;vertical-align:middle;">'
                    f'{label}</td>'
                )
            style = (f'width:{cell_size}px;height:{cell_size}px;'
                     f'vertical-align:top;padding:4px;font-size:11px;')
            # For centre placeholder, we already appended it
            if r == 1 and c == 1:
                continue
            cells.append(
                f'<td style="{style}">{planets_here}</td>'
            )
        rows.append("<tr>" + "".join(cells) + "</tr>")

    table_style = ("border-collapse:collapse;border:2px solid #000;"
                   "width:100%;height:100%;")
    td_border   = ("td { border:1px solid #444; }")
    return (
        f'<table style="{table_style}">'
        f'<style>{td_border}</style>'
        + "".join(rows)
        + "</table>"
    )


def _make_south_indian_chart_html(by_sign, label):
    """Build a complete South Indian chart table (4 rows, handles centre span)."""
    # Grid: row 0 → 4 normal cells, row 1 → left + centre-span(2×2) + right,
    #        row 2 → left + [skipped centre] + right, row 3 → 4 normal cells
    cell_h = 90
    cell_w = 90
    cell_s = f"width:{cell_w}px;height:{cell_h}px;vertical-align:top;padding:4px;font-size:11px;border:1px solid #444;"

    def cell(sign):
        planets_here = "<br>".join(by_sign.get(sign, []))
        return f'<td style="{cell_s}">{planets_here}</td>'

    centre_td = (
        f'<th align="center" rowspan="2" colspan="2" '
        f'style="width:{cell_w*2}px;height:{cell_h*2}px;'
        f'border:1px solid #444;font-size:15px;">'
        f'{label}</th>'
    )

    row0 = f"<tr>{cell(11)}{cell(0)}{cell(1)}{cell(2)}</tr>"
    row1 = f"<tr>{cell(10)}{centre_td}{cell(3)}</tr>"
    row2 = f"<tr>{cell(9)}{cell(4)}</tr>"
    row3 = f"<tr>{cell(8)}{cell(7)}{cell(6)}{cell(5)}</tr>"

    table_style = ("border-collapse:collapse;border:2px solid #000;"
                   f"width:{cell_w*4+10}px;")
    return (
        f'<table style="{table_style}">'
        + row0 + row1 + row2 + row3
        + "</table>"
    )


def _planets_by_sign(planet_degs):
    """Map sign index → list of planet abbreviations (for Rasi chart)."""
    by_sign = defaultdict(list)
    for i, degs in enumerate(planet_degs):
        sign = int(degs // 30)
        by_sign[sign].append(GRAHA_DISPLAY[i])
    return dict(by_sign)


def _planets_by_navamsa(navamsa_positions):
    """Map navamsa sign index → list of planet abbreviations."""
    by_sign = defaultdict(list)
    for i, sign in enumerate(navamsa_positions):
        by_sign[int(sign)].append(GRAHA_DISPLAY[i])
    return dict(by_sign)


def _planets_by_bhava(bhava_positions):
    """Map sign index → planet list for the Bhava (house) chart.

    bhava_positions is the 12-element list returned by fn.get_bhava_positions().
    Each element is the *sign index* (0–11) of the South Indian chart cell where
    that planet should appear — already offset by the Lagna sign so that the
    Lagna always falls in its own sign's cell.
    """
    by_sign = defaultdict(list)
    for i, sign in enumerate(bhava_positions):
        by_sign[int(sign)].append(GRAHA_DISPLAY[i])
    return dict(by_sign)


def _graha_label(i, planet_retrograde):
    """Return planet display name; append (R) if retrograde."""
    label = GRAHA_DISPLAY[i]
    if planet_retrograde and planet_retrograde[i]:
        label += "(R)"
    return label


def _planets_by_sign_r(planet_degs, planet_retrograde):
    """Like _planets_by_sign but includes (R) for retrograde planets."""
    by_sign = defaultdict(list)
    for i, degs in enumerate(planet_degs):
        sign = int(degs // 30)
        by_sign[sign].append(_graha_label(i, planet_retrograde))
    return dict(by_sign)


def _planets_by_navamsa_r(navamsa_positions, planet_retrograde):
    """Like _planets_by_navamsa but includes (R) for retrograde planets."""
    by_sign = defaultdict(list)
    for i, sign in enumerate(navamsa_positions):
        by_sign[int(sign)].append(_graha_label(i, planet_retrograde))
    return dict(by_sign)


def _planets_by_bhava_r(bhava_positions, planet_retrograde):
    """Like _planets_by_bhava but includes (R) for retrograde planets."""
    by_sign = defaultdict(list)
    for i, sign in enumerate(bhava_positions):
        by_sign[int(sign)].append(_graha_label(i, planet_retrograde))
    return dict(by_sign)


# ── HTML Report (Tab 2) ────────────────────────────────────────────────────────

def generate_html_report(result):
    """Generate a self-contained HTML report matching the C program's style."""
    inp   = result["input"]
    cal   = result["calendar"]
    pd    = result["planet_degs"]
    nav   = result["navamsa_positions"]
    house = result["house_positions"]
    shad  = result["shad"]
    bb    = result["bhava_bala"]
    mut   = result["mutual"]

    name      = inp["name"]
    birthplace = inp["birthplace"]
    in_dt     = inp["in_datetime"]
    lat_d     = int(inp["lat_degs"])
    lat_m     = int((inp["lat_degs"] - lat_d) * 60)
    lon_d     = int(inp["long_degs"])
    lon_m     = int((inp["long_degs"] - lon_d) * 60)
    lat_dir   = inp["lat_dirn"]
    lon_dir   = inp["long_dirn"]

    sunrise = cal["sunrise"]
    sunset  = cal["sunset"]

    # Chart data
    retro = result.get("planet_retrograde", [False] * 12)
    rasi_by_sign  = _planets_by_sign_r(pd, retro)
    nav_by_sign   = _planets_by_navamsa_r(nav, retro)
    bhava_by_sign = _planets_by_bhava_r(result["bhava_positions"], retro)

    rasi_chart  = _make_south_indian_chart_html(rasi_by_sign,  "RASI")
    nav_chart   = _make_south_indian_chart_html(nav_by_sign,   "NAVAMSA")
    bhava_chart = _make_south_indian_chart_html(bhava_by_sign, "BHAVA")

    # Longitude table rows
    long_rows = ""
    for i, nm in enumerate(GRAHA_NAMES):
        degs = pd[i]
        d    = int(degs)
        m    = int((degs - d) * 60)
        nak, pada = _nakshatra_pada(degs)
        retro_mark = "<b style='color:#c00'>(R)</b>" if retro[i] else ""
        long_rows += (
            f"<tr><td><b>{nm}</b>{retro_mark}</td>"
            f"<td align='right'>{d}&deg;</td>"
            f"<td align='right'>{m}&prime;</td>"
            f"<td>{NAKSHATRA[nak]}</td>"
            f"<td>{pada}</td></tr>\n"
        )

    # Shadbala table
    shad_rows = ""
    shad_components = [
        ("Sthana Bala",   "sthana"),
        ("Kala Bala",     "kala"),
        ("Dig Bala",      "dig"),
        ("Naisargika",    "naisa"),
        ("Chesta Bala",   "chesta"),
        ("Drik (+)",      "ben_drig"),
        ("Drik (-)",      "mal_drig"),
    ]
    for label, key in shad_components:
        vals = shad[key]
        cells = "".join(f"<td align='right'>{v:.2f}</td>" for v in vals)
        shad_rows += f"<tr><td><b>{label}</b></td>{cells}</tr>\n"
    total_cells = "".join(f"<td align='right'><b>{v:.2f}</b></td>" for v in shad["total"])
    shad_rows += f"<tr style='border-top:2px solid #000'><td><b>TOTAL</b></td>{total_cells}</tr>\n"
    rel_cells = "".join(f"<td align='right'>{v:.2f}</td>" for v in shad["relative"])
    shad_rows += f"<tr><td>Relative</td>{rel_cells}</tr>\n"

    # Bhava bala table
    bb_rows = ""
    bb_components = [
        ("Bhavaswami",  "swami"),
        ("Dig Bala",    "dig"),
        ("Drig Bala",   "drig"),
        ("Spl Aspect",  "spl_drig"),
        ("Occ Str",     "ostr"),
    ]
    for label, key in bb_components:
        vals = bb[key]
        cells = "".join(f"<td align='right'>{v:.2f}</td>" for v in vals)
        bb_rows += f"<tr><td><b>{label}</b></td>{cells}</tr>\n"
    tot_cells = "".join(f"<td align='right'><b>{v:.2f}</b></td>" for v in bb["total"])
    bb_rows += f"<tr style='border-top:2px solid #000'><td><b>TOTAL</b></td>{tot_cells}</tr>\n"
    rel_bb = "".join(f"<td align='right'>{v:.2f}</td>" for v in bb["relative"])
    bb_rows += f"<tr><td>Relative</td>{rel_bb}</tr>\n"

    # Mutual disposition
    pnames = mut["planet_names"]
    mut_header = "<tr><th></th>" + "".join(f"<th>{p}</th>" for p in pnames) + "</tr>"
    rasi_rows = ""
    for i, row in enumerate(mut["rasi"]):
        cells = "".join(f"<td align='center'>{v}</td>" for v in row)
        rasi_rows += f"<tr><td><b>{pnames[i]}</b></td>{cells}</tr>\n"
    nav_rows = ""
    for i, row in enumerate(mut["navamsa"]):
        cells = "".join(f"<td align='center'>{v}</td>" for v in row)
        nav_rows += f"<tr><td><b>{pnames[i]}</b></td>{cells}</tr>\n"

    shad_header = "<tr><th>Bala</th>" + "".join(f"<th>{p}</th>" for p in SHAD_LABELS) + "</tr>"
    bb_hd_cells = "".join(f"<th>H{i+1}</th>" for i in range(12))
    bb_header   = f"<tr><th>Bala</th>{bb_hd_cells}</tr>"

    ts = ("border-collapse:collapse;width:100%;border:1px solid #ccc;"
          "font-size:12px;margin-bottom:10px;")
    tds = "border:1px solid #ccc;padding:3px 6px;"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Bhagyagraha — {name}</title>
<style>
  body {{ font-family: Arial, sans-serif; background: #f0fff0; margin: 20px; font-size:13px; }}
  h1   {{ text-align:center; color: #8B0000; letter-spacing: 4px; }}
  h2   {{ color: #444; border-bottom: 1px solid #888; margin-top: 20px; font-size:14px; }}
  table {{ border-collapse:collapse; }}
  td, th {{ {tds} }}
  .charts {{ display:flex; gap:20px; flex-wrap:wrap; margin: 10px 0; }}
  .chart-box {{ text-align:center; }}
  .chart-label {{ font-weight:bold; margin-bottom:4px; }}
  @media print {{
    .no-print {{ display:none; }}
    body {{ margin:0; background:white; }}
  }}
</style>
</head>
<body>
<h1>&#9654; B H A G Y A G R A H A &#9664;</h1>

<div class="no-print" style="text-align:right;margin-bottom:10px;">
  <button onclick="window.print()"
    style="padding:8px 18px;background:#8B0000;color:white;border:none;
           border-radius:4px;cursor:pointer;font-size:13px;">
    &#128438; Print / Save as PDF
  </button>
</div>

<!-- ── Personal Data ── -->
<table style="{ts}width:100%">
<tr>
  <td style="vertical-align:top;width:50%">
    <table style="{ts}">
      <tr><td><b>Name</b></td><td>{name}</td></tr>
      <tr><td><b>Date of Birth</b></td>
          <td>{in_dt.day}/{in_dt.month}/{in_dt.year} &mdash; {cal["weekday"]}</td></tr>
      <tr><td><b>Time of Birth</b></td>
          <td>{in_dt.hour}H-{in_dt.minute:02d}M (Local Std Time)</td></tr>
      <tr><td><b>Place of Birth</b></td><td>{birthplace}</td></tr>
      <tr><td><b>Lat-Long</b></td>
          <td>{lat_d}&deg;-{lat_m}&prime;({lat_dir})&nbsp;
              {lon_d}&deg;-{lon_m}&prime;({lon_dir})</td></tr>
      <tr><td><b>Janma Nakshatra</b></td>
          <td>{cal["janma_nakshatra"]} Pada-{cal["janma_pada"]}</td></tr>
      <tr><td><b>Paksham</b></td><td>{cal["paksham"]}</td></tr>
      <tr><td><b>Balance of {cal["dasa_lord"]} dasa</b></td>
          <td>Y:&nbsp;{cal["dasa_y"]}&nbsp; M:&nbsp;{cal["dasa_m"]}&nbsp; D:&nbsp;{cal["dasa_d"]}</td></tr>
    </table>
  </td>
  <td style="vertical-align:top;width:50%">
    <table style="{ts}">
      <tr><td><b>Thithi</b></td><td>{cal["thithi"]}</td></tr>
      <tr><td><b>Yogam</b></td><td>{cal["yogam"]}</td></tr>
      <tr><td><b>Karanam</b></td><td>{cal["karanam"]}</td></tr>
      <tr><td><b>Tamil Date</b></td>
          <td>{cal["tamil_day"]} {cal["tamil_month"]} {cal["tamil_year"]}</td></tr>
      <tr><td><b>Saka Date</b></td>
          <td>{cal["saka_day"]} {cal["saka_month"]} {cal["saka_year"]}</td></tr>
      <tr><td><b>Kali Year</b></td><td>{cal["kali_year"]}</td></tr>
      <tr><td><b>Sun Rise</b></td>
          <td>{sunrise.strftime("%H:%M")} (Local Mean Time)</td></tr>
      <tr><td><b>Sun Set</b></td>
          <td>{sunset.strftime("%H:%M")} (Local Mean Time)</td></tr>
    </table>
  </td>
</tr>
</table>

<!-- ── Charts + Longitude Table ── -->
<h2>Charts &amp; Planetary Positions</h2>
<table style="width:100%;border:none">
<tr>
  <td style="border:none;width:48%;vertical-align:top">
    <div class="chart-label" style="text-align:center">RASI</div>
    {rasi_chart}
  </td>
  <td style="border:none;width:4%"></td>
  <td style="border:none;width:48%;vertical-align:top">
    <div class="chart-label" style="text-align:center">NAVAMSA</div>
    {nav_chart}
  </td>
</tr>
<tr><td colspan="3" style="border:none;height:15px"></td></tr>
<tr>
  <td style="border:none;vertical-align:top">
    <div class="chart-label" style="text-align:center">BHAVA</div>
    {bhava_chart}
  </td>
  <td style="border:none"></td>
  <td style="border:none;vertical-align:top">
    <table style="{ts}">
      <tr>
        <th></th><th colspan="2">Longitude</th>
        <th>Nakshatra</th><th>Pada</th>
      </tr>
      {long_rows}
    </table>
  </td>
</tr>
</table>

<!-- ── Shadbala ── -->
<h2>Shadbala (Planetary Strength)</h2>
<table style="{ts}">
{shad_header}
{shad_rows}
</table>

<!-- ── Bhava Bala ── -->
<h2>Bhava Bala (House Strength)</h2>
<table style="{ts}">
{bb_header}
{bb_rows}
</table>

<!-- ── Mutual Disposition ── -->
<h2>Mutual Disposition &mdash; Rasi</h2>
<table style="{ts}">
{mut_header}
{rasi_rows}
</table>

<h2>Mutual Disposition &mdash; Navamsa</h2>
<table style="{ts}">
{mut_header}
{nav_rows}
</table>

</body>
</html>"""
    return html


# ── PDF generation via ReportLab ──────────────────────────────────────────────

def _pdf_si_chart(by_sign, label, cell_w=50, cell_h=36):
    """Build a 4×4 South Indian chart as a ReportLab Table."""
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors

    def cell(s):
        return "\n".join(by_sign.get(s, []))

    data = [
        [cell(11), cell(0),  cell(1),  cell(2)],
        [cell(10), label,    "",        cell(3)],
        [cell(9),  "",       "",        cell(4)],
        [cell(8),  cell(7),  cell(6),   cell(5)],
    ]
    t = Table(data, colWidths=[cell_w] * 4, rowHeights=[cell_h] * 4)
    t.setStyle(TableStyle([
        ("GRID",     (0, 0), (-1, -1), 0.5, colors.black),
        ("SPAN",     (1, 1), (2, 2)),
        ("ALIGN",    (1, 1), (2, 2), "CENTER"),
        ("VALIGN",   (1, 1), (2, 2), "MIDDLE"),
        ("FONTNAME", (1, 1), (2, 2), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("LEADING",  (0, 0), (-1, -1), 8),
        ("VALIGN",   (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def _pdf_ashta_chart(vals, label, cell_w=42, cell_h=28):
    """Small 4×4 chart showing integer Ashtavarga values per sign."""
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors

    data = [
        [vals[11], vals[0],  vals[1],  vals[2]],
        [vals[10], label,    "",        vals[3]],
        [vals[9],  "",       "",        vals[4]],
        [vals[8],  vals[7],  vals[6],   vals[5]],
    ]
    t = Table(data, colWidths=[cell_w] * 4, rowHeights=[cell_h] * 4)
    t.setStyle(TableStyle([
        ("GRID",     (0, 0), (-1, -1), 0.5, colors.black),
        ("SPAN",     (1, 1), (2, 2)),
        ("ALIGN",    (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",   (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (1, 1), (2, 2), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    return t


def _pdf_section_title(text, styles):
    from reportlab.platypus import Paragraph
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    style = ParagraphStyle("sect", parent=styles["Heading2"],
                           textColor=colors.darkred, spaceAfter=3)
    return Paragraph(text, style)


def _pdf_p1(story, result, styles, mm):
    """Page 1: Birth data, Panchangam, Astronomical."""
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors

    inp   = result["input"]
    cal   = result["calendar"]
    in_dt = inp["in_datetime"]
    lat_d = int(inp["lat_degs"])
    lat_m = int((inp["lat_degs"] - lat_d) * 60)
    lon_d = int(inp["long_degs"])
    lon_m = int((inp["long_degs"] - lon_d) * 60)

    H1 = styles["Heading1"]
    N  = styles["Normal"]

    story.append(Paragraph("B H A G Y A G R A H A", H1))
    story.append(Spacer(1, 4 * mm))

    ts = TableStyle([
        ("FONTSIZE",  (0, 0), (-1, -1), 9),
        ("FONTNAME",  (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID",      (0, 0), (-1, -1), 0.3, colors.grey),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1),
         [colors.white, colors.Color(0.96, 0.96, 0.96)]),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ])

    birth_data = [
        ["Name",           inp["name"]],
        ["Date of Birth",  f"{in_dt.day:02d}/{in_dt.month:02d}/{in_dt.year}  ({cal['weekday']})"],
        ["Time of Birth",  f"{in_dt.hour:02d}H-{in_dt.minute:02d}M  (Local Standard Time)"],
        ["Place of Birth", inp["birthplace"]],
        ["Latitude",       f"{lat_d}-{lat_m:02d} ({inp['lat_dirn']})"],
        ["Longitude",      f"{lon_d}-{lon_m:02d} ({inp['long_dirn']})"],
        ["Sun Rise",       cal["sunrise"].strftime("%H:%M")],
        ["Sun Set",        cal["sunset"].strftime("%H:%M")],
    ]
    t = Table(birth_data, colWidths=[55 * mm, 120 * mm])
    t.setStyle(ts)
    story.append(t)
    story.append(Spacer(1, 5 * mm))

    story.append(_pdf_section_title("Panchangam", styles))
    pan_data = [
        ["Paksham",    cal["paksham"],  "Thithi",   cal["thithi"]],
        ["Yogam",      cal["yogam"],    "Karanam",  cal["karanam"]],
        ["Tamil Date", f"{cal['tamil_day']} {cal['tamil_month']} {cal['tamil_year']}",
         "Saka Date",  f"{cal['saka_day']} {cal['saka_month']} {cal['saka_year']}"],
        ["Kali Year",  str(cal["kali_year"]),
         "Weekday",    cal["weekday"]],
        ["Nakshatra",  f"{cal['janma_nakshatra']} Pada-{cal['janma_pada']}",
         "Dasa Balance",
         f"{cal['dasa_lord']}  Y:{cal['dasa_y']} M:{cal['dasa_m']} D:{cal['dasa_d']}"],
    ]
    ts2 = TableStyle([
        ("FONTSIZE",  (0, 0), (-1, -1), 9),
        ("FONTNAME",  (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",  (2, 0), (2, -1), "Helvetica-Bold"),
        ("GRID",      (0, 0), (-1, -1), 0.3, colors.grey),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1),
         [colors.white, colors.Color(0.96, 0.96, 0.96)]),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ])
    t2 = Table(pan_data, colWidths=[38 * mm, 58 * mm, 38 * mm, 58 * mm])
    t2.setStyle(ts2)
    story.append(t2)
    story.append(Spacer(1, 5 * mm))

    story.append(_pdf_section_title("Astronomical Data", styles))
    ast_data = [
        ["Sidereal Time (RAMC)", _ramc_hms(result.get("sidereal_time", 0.0))],
        ["Ayanamsa",             f"{result.get('ayanamsa', 0.0):.4f}\u00b0"],
    ]
    t3 = Table(ast_data, colWidths=[70 * mm, 105 * mm])
    t3.setStyle(TableStyle([
        ("FONTSIZE",  (0, 0), (-1, -1), 9),
        ("FONTNAME",  (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID",      (0, 0), (-1, -1), 0.3, colors.grey),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
    ]))
    story.append(t3)


def _pdf_p2(story, result, styles, mm):
    """Page 2: Nirayana Longitudes + RASI + NAVAMSA + Dasa balance."""
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors

    pd_   = result["planet_degs"]
    nav   = result["navamsa_positions"]
    retro = result.get("planet_retrograde", [False] * 12)
    cal   = result["calendar"]

    story.append(_pdf_section_title("Nirayana Longitudes", styles))

    long_data = [["Graha", "Longitude", "Rasi", "Nakshatra", "Pada", "Navamsa"]]
    for i, nm in enumerate(GRAHA_NAMES):
        degs = pd_[i]
        sign = int(degs // 30)
        d    = int(degs)
        m    = int((degs - d) * 60)
        nak, pada = _nakshatra_pada(degs)
        r_mark = "(R)" if retro[i] else ""
        long_data.append([
            nm + r_mark,
            f"{d}\u00b0-{m:02d}\u2032",
            RASI_NAMES[sign],
            NAKSHATRA[nak],
            str(pada),
            RASI_NAMES[int(nav[i])],
        ])
    ts = TableStyle([
        ("FONTSIZE",    (0, 0), (-1, -1), 8),
        ("FONTNAME",    (0, 0), (-1,  0), "Helvetica-Bold"),
        ("FONTNAME",    (0, 1), (0,  -1), "Helvetica-Bold"),
        ("GRID",        (0, 0), (-1, -1), 0.3, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.Color(0.96, 0.96, 0.96)]),
        ("LEFTPADDING",  (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("BACKGROUND",  (0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),
    ])
    t = Table(long_data, colWidths=[22*mm, 22*mm, 28*mm, 36*mm, 14*mm, 28*mm])
    t.setStyle(ts)
    story.append(t)
    story.append(Spacer(1, 6 * mm))

    # Charts side by side
    rasi_by  = _planets_by_sign_r(pd_, retro)
    nav_by   = _planets_by_navamsa_r(nav, retro)
    rasi_t   = _pdf_si_chart(rasi_by,  "RASI",    cell_w=47, cell_h=36)
    nav_t    = _pdf_si_chart(nav_by,   "NAVAMSA", cell_w=47, cell_h=36)
    outer    = Table([[rasi_t, "", nav_t]], colWidths=[192*mm, 6*mm, 192*mm])
    outer.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    # Fit both charts side by side on A4 (usable width ~186mm with 12mm margins each)
    # Use smaller cells
    rasi_t2  = _pdf_si_chart(rasi_by,  "RASI",    cell_w=42, cell_h=34)
    nav_t2   = _pdf_si_chart(nav_by,   "NAVAMSA", cell_w=42, cell_h=34)
    outer2   = Table([[rasi_t2, Spacer(4*mm, 1), nav_t2]],
                     colWidths=[168*mm, 4*mm, 168*mm])
    outer2.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(outer2)
    story.append(Spacer(1, 6 * mm))

    # Dasa balance
    story.append(Paragraph(
        f"<b>Dasa Balance at Birth:</b>  "
        f"{cal['dasa_lord']} — "
        f"Y: {cal['dasa_y']}  M: {cal['dasa_m']}  D: {cal['dasa_d']}",
        styles["Normal"]
    ))


def _pdf_p3(story, result, styles, mm):
    """Page 3: Bhava table + BHAVA chart + Dasa/Bukti table."""
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors

    house = result["house_positions"]
    retro = result.get("planet_retrograde", [False] * 12)
    cal   = result["calendar"]

    story.append(_pdf_section_title("Bhava Cusps", styles))
    bhava_data = [["Bhava", "Longitude", "Rasi"]]
    for i in range(12):
        degs = house[i]
        sign = int(degs // 30)
        d    = int(degs)
        m    = int((degs - d) * 60)
        bhava_data.append([str(i + 1), f"{d}\u00b0-{m:02d}\u2032", RASI_NAMES[sign]])
    ts = TableStyle([
        ("FONTSIZE",  (0, 0), (-1, -1), 8),
        ("FONTNAME",  (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("GRID",      (0, 0), (-1, -1), 0.3, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.Color(0.96, 0.96, 0.96)]),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),
    ])
    t = Table(bhava_data, colWidths=[20*mm, 28*mm, 32*mm])
    t.setStyle(ts)

    bhava_by = _planets_by_bhava_r(result["bhava_positions"], retro)
    bhava_chart = _pdf_si_chart(bhava_by, "BHAVA", cell_w=42, cell_h=34)

    outer = Table([[t, Spacer(6*mm, 1), bhava_chart]],
                  colWidths=[80*mm, 6*mm, 168*mm])
    outer.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(outer)
    story.append(Spacer(1, 6 * mm))

    # Dasa/Bukti table
    story.append(_pdf_section_title("Vimsottari Dasa/Bukti Table", styles))
    dasa_table = cal.get("dasa_table", [])
    for drow in dasa_table:
        story.append(Paragraph(f"<b>{drow['dasa']} Dasa</b>", styles["Normal"]))
        bdata = [[b[0], b[1]] for b in drow["buktis"]]
        # Split buktis into 3 columns
        rows = []
        for idx in range(0, 9, 3):
            row = []
            for jj in range(3):
                if idx + jj < len(bdata):
                    row.extend(bdata[idx + jj])
                else:
                    row.extend(["", ""])
            rows.append(row)
        bt = Table(rows, colWidths=[28*mm, 24*mm, 28*mm, 24*mm, 28*mm, 24*mm])
        bt.setStyle(TableStyle([
            ("FONTSIZE",  (0, 0), (-1, -1), 7),
            ("GRID",      (0, 0), (-1, -1), 0.2, colors.grey),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ]))
        story.append(bt)
        story.append(Spacer(1, 2 * mm))


def _pdf_p4(story, result, styles, mm):
    """Page 4: Natural Disposition + Mutual Disposition (Rasi + Navamsa)."""
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors

    mut    = result["mutual"]
    pnames = mut["planet_names"]

    def _mat_table(matrix, pnames):
        header = [""] + pnames
        rows   = [header]
        for i, row in enumerate(matrix):
            rows.append([pnames[i]] + list(row))
        ts = TableStyle([
            ("FONTSIZE",  (0, 0), (-1, -1), 7),
            ("FONTNAME",  (0, 0), (0,  -1), "Helvetica-Bold"),
            ("FONTNAME",  (0, 0), (-1,  0), "Helvetica-Bold"),
            ("GRID",      (0, 0), (-1, -1), 0.3, colors.grey),
            ("BACKGROUND",(0, 0), (-1, 0),  colors.Color(0.85, 0.85, 0.85)),
            ("LEFTPADDING",  (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ])
        cw = [22*mm] + [20*mm] * len(pnames)
        t  = Table(rows, colWidths=cw)
        t.setStyle(ts)
        return t

    story.append(_pdf_section_title("Mutual Disposition — Rasi", styles))
    story.append(_mat_table(mut["rasi"], pnames))
    story.append(Spacer(1, 8 * mm))
    story.append(_pdf_section_title("Mutual Disposition — Navamsa", styles))
    story.append(_mat_table(mut["navamsa"], pnames))


def _pdf_ashta_section(story, ashta_dict, styles, mm):
    """Add one planet's Ashtavarga section (3 charts + Sodhya Pinda)."""
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors

    name  = ashta_dict["name"]
    raw   = ashta_dict["raw"]
    thri  = ashta_dict["thri"]
    eka   = ashta_dict["eka"]
    contribs = ashta_dict["contributors"]
    sp    = ashta_dict["sodhya_pinda"]

    story.append(_pdf_section_title(f"{name} Ashtavarga  (Total={sum(raw)})", styles))

    # Main chart: contributor abbreviations + count
    main_by = {}
    for s in range(12):
        abbrs = " ".join(contribs[s])
        main_by[s] = [f"{abbrs}", f"{raw[s]}"] if abbrs else [f"{raw[s]}"]

    def cell_main(s):
        return "\n".join(main_by.get(s, []))

    from reportlab.platypus import Table as RLTable
    main_data = [
        [cell_main(11), cell_main(0),  cell_main(1),  cell_main(2)],
        [cell_main(10), f"{name}\nMain\n{sum(raw)}", "", cell_main(3)],
        [cell_main(9),  "", "",  cell_main(4)],
        [cell_main(8),  cell_main(7),  cell_main(6),  cell_main(5)],
    ]
    mt = RLTable(main_data, colWidths=[44*mm]*4, rowHeights=[32*mm]*4)
    mt.setStyle(TableStyle([
        ("GRID",     (0,0),(-1,-1), 0.5, colors.black),
        ("SPAN",     (1,1),(2,2)),
        ("ALIGN",    (1,1),(2,2), "CENTER"),
        ("VALIGN",   (1,1),(2,2), "MIDDLE"),
        ("FONTNAME", (1,1),(2,2), "Helvetica-Bold"),
        ("FONTSIZE", (0,0),(-1,-1), 7),
        ("LEADING",  (0,0),(-1,-1), 8),
        ("VALIGN",   (0,0),(-1,-1), "TOP"),
    ]))

    thri_t = _pdf_ashta_chart(thri, "Thri",  cell_w=38, cell_h=28)
    eka_t  = _pdf_ashta_chart(eka,  "Eka",   cell_w=38, cell_h=28)

    side = Table([[mt, Spacer(4*mm,1), thri_t, Spacer(4*mm,1), eka_t]],
                 colWidths=[176*mm, 4*mm, 152*mm, 4*mm, 152*mm])
    side.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(side)
    story.append(Paragraph(f"Sodhya Pinda: <b>{sp}</b>", styles["Normal"]))
    story.append(Spacer(1, 5*mm))


def _pdf_p5(story, result, styles, mm):
    """Page 5: Ashtavarga for Sun, Moon, Mars."""
    ashta = result.get("ashtavarga", {})
    planets = ashta.get("planets", [])
    for p in planets[:3]:
        _pdf_ashta_section(story, p, styles, mm)


def _pdf_p6(story, result, styles, mm):
    """Page 6: Ashtavarga for Merc, Jupt, Venu."""
    ashta = result.get("ashtavarga", {})
    planets = ashta.get("planets", [])
    for p in planets[3:6]:
        _pdf_ashta_section(story, p, styles, mm)


def _pdf_p7(story, result, styles, mm):
    """Page 7: Ashtavarga for Satn + Sarvashtavarga."""
    ashta = result.get("ashtavarga", {})
    planets = ashta.get("planets", [])
    if len(planets) > 6:
        _pdf_ashta_section(story, planets[6], styles, mm)
    sarva = ashta.get("sarva")
    if sarva:
        _pdf_ashta_section(story, sarva, styles, mm)


def _pdf_p8(story, result, styles, mm):
    """Page 8: Drig Bala 7×7 matrix + Bhava Drig aspects."""
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors

    shad  = result["shad"]
    p7_degs = [result["planet_degs"][i] for i in [1, 2, 3, 4, 5, 6, 7]]

    story.append(_pdf_section_title("Drig Bala — Pairwise Aspect Strengths", styles))

    try:
        drig_mat = sb.drig_bala_matrix(p7_degs)
    except Exception:
        drig_mat = [[0.0]*7 for _ in range(7)]

    pl7 = SHAD_LABELS
    header = [""] + pl7
    rows   = [header]
    for i, row in enumerate(drig_mat):
        rows.append([pl7[i]] + [f"{v:.2f}" for v in row])
    ts = TableStyle([
        ("FONTSIZE",  (0, 0), (-1, -1), 8),
        ("FONTNAME",  (0, 0), (0,  -1), "Helvetica-Bold"),
        ("FONTNAME",  (0, 0), (-1,  0), "Helvetica-Bold"),
        ("GRID",      (0, 0), (-1, -1), 0.3, colors.grey),
        ("BACKGROUND",(0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),
        ("LEFTPADDING",  (0,0),(-1,-1), 3),
        ("RIGHTPADDING", (0,0),(-1,-1), 3),
    ])
    cw = [22*mm] + [24*mm] * 7
    t  = Table(rows, colWidths=cw)
    t.setStyle(ts)
    story.append(t)
    story.append(Spacer(1, 8*mm))

    # Ben / Mal drig summary
    story.append(_pdf_section_title("Benefic / Malefic Drig Bala", styles))
    bd = shad.get("ben_drig", [0]*7)
    md = shad.get("mal_drig", [0]*7)
    bm_data = [
        [""] + pl7,
        ["Ben(+)"] + [f"{v:.2f}" for v in bd],
        ["Mal(-)"] + [f"{v:.2f}" for v in md],
    ]
    bmt = Table(bm_data, colWidths=[22*mm] + [24*mm]*7)
    bmt.setStyle(ts)
    story.append(bmt)


def _pdf_p9(story, result, styles, mm):
    """Page 9: Shadbala + Bhava Bala."""
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors

    shad = result["shad"]
    bb   = result["bhava_bala"]

    story.append(_pdf_section_title("Shadbala — Planetary Strength", styles))
    pl7 = SHAD_LABELS
    shad_components = [
        ("Sthana Bala", "sthana"),
        ("Kala Bala",   "kala"),
        ("Dig Bala",    "dig"),
        ("Naisargika",  "naisa"),
        ("Chesta Bala", "chesta"),
        ("Drik (+)",    "ben_drig"),
        ("Drik (-)",    "mal_drig"),
        ("TOTAL",       "total"),
        ("Min Req",     "min_required"),
        ("Relative",    "relative"),
        ("Ishta",       "ishta"),
        ("Kashta",      "kashta"),
    ]
    shad_rows = [["Bala"] + pl7]
    for label, key in shad_components:
        row = [label] + [f"{v:.2f}" for v in shad[key]]
        shad_rows.append(row)

    ts = TableStyle([
        ("FONTSIZE",  (0, 0), (-1, -1), 8),
        ("FONTNAME",  (0, 0), (0,  -1), "Helvetica-Bold"),
        ("FONTNAME",  (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID",      (0, 0), (-1, -1), 0.3, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.Color(0.96, 0.96, 0.96)]),
        ("BACKGROUND",(0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),
        ("BACKGROUND",(0, 8), (-1, 8), colors.Color(0.80, 0.90, 0.80)),
        ("LEFTPADDING",  (0,0),(-1,-1), 3),
        ("RIGHTPADDING", (0,0),(-1,-1), 3),
    ])
    cw = [30*mm] + [22*mm]*7
    t  = Table(shad_rows, colWidths=cw)
    t.setStyle(ts)
    story.append(t)
    story.append(Spacer(1, 8*mm))

    # Bhava Bala
    story.append(_pdf_section_title("Bhava Bala — House Strength", styles))
    bb_components = [
        ("Swami Bala", "swami"),
        ("Dig Bala",   "dig"),
        ("Drig Bala",  "drig"),
        ("Spl Drig",   "spl_drig"),
        ("Occ Str",    "ostr"),
        ("TOTAL",      "total"),
        ("Relative",   "relative"),
    ]
    hdr = ["Bala"] + [f"H{h+1}" for h in range(12)]
    bb_rows = [hdr]
    for label, key in bb_components:
        bb_rows.append([label] + [f"{v:.2f}" for v in bb[key]])

    ts2 = TableStyle([
        ("FONTSIZE",  (0, 0), (-1, -1), 7),
        ("FONTNAME",  (0, 0), (0,  -1), "Helvetica-Bold"),
        ("FONTNAME",  (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("GRID",      (0, 0), (-1, -1), 0.3, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.Color(0.96, 0.96, 0.96)]),
        ("BACKGROUND",(0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),
        ("LEFTPADDING",  (0,0),(-1,-1), 2),
        ("RIGHTPADDING", (0,0),(-1,-1), 2),
    ])
    cw2 = [25*mm] + [14*mm]*12
    t2  = Table(bb_rows, colWidths=cw2)
    t2.setStyle(ts2)
    story.append(t2)


def generate_pdf(result) -> bytes:
    """Generate a 9-page PDF horoscope matching HOR.OUT structure.

    Returns raw PDF bytes suitable for st.download_button.
    """
    try:
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, PageBreak, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
    except ImportError as e:
        raise RuntimeError(
            "reportlab is required for PDF generation. "
            "Install it with: pip install reportlab"
        ) from e

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=12 * mm, rightMargin=12 * mm,
        topMargin=12 * mm, bottomMargin=12 * mm,
    )
    styles = getSampleStyleSheet()
    # Override heading style
    styles["Heading1"].fontSize = 16
    styles["Heading1"].spaceAfter = 6

    story = []

    _pdf_p1(story, result, styles, mm)
    story.append(PageBreak())
    _pdf_p2(story, result, styles, mm)
    story.append(PageBreak())
    _pdf_p3(story, result, styles, mm)
    story.append(PageBreak())
    _pdf_p4(story, result, styles, mm)

    if result.get("ashtavarga"):
        story.append(PageBreak())
        _pdf_p5(story, result, styles, mm)
        story.append(PageBreak())
        _pdf_p6(story, result, styles, mm)
        story.append(PageBreak())
        _pdf_p7(story, result, styles, mm)

    story.append(PageBreak())
    _pdf_p8(story, result, styles, mm)
    story.append(PageBreak())
    _pdf_p9(story, result, styles, mm)

    doc.build(story)
    return buf.getvalue()


# ── Custom CSS injection ──────────────────────────────────────────────────────

_CSS = """
<style>
/* ── Sidebar: deep cosmic dark with saffron accents ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0500 0%, #1e0a00 60%, #0f0500 100%) !important;
    border-right: 2px solid #b8720a !important;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #f5d78e !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #ffd700 !important;
}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
    background-color: #2a0e00 !important;
    border: 1px solid #b8720a !important;
    color: #fff8e7 !important;
    border-radius: 6px !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stDateInput > div > div,
section[data-testid="stSidebar"] .stTimeInput > div > div {
    background-color: #2a0e00 !important;
    border: 1px solid #b8720a !important;
    color: #fff8e7 !important;
    border-radius: 6px !important;
}
section[data-testid="stSidebar"] hr {
    border-color: #6b3800 !important;
    margin: 0.6rem 0 !important;
}
/* Sidebar section dividers */
.sb-section {
    background: rgba(184,114,10,0.12);
    border-left: 3px solid #b8720a;
    border-radius: 0 6px 6px 0;
    padding: 8px 10px 8px 12px;
    margin: 8px 0 4px 0;
}
.sb-section-title {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #ffd700 !important;
}

/* ── Main area ── */
.main .block-container {
    background-color: #fffcf5;
    padding-top: 1rem !important;
}

/* ── Page header banner ── */
.bhagya-header {
    background: linear-gradient(135deg, #6b0000 0%, #a85200 50%, #6b0000 100%);
    color: #fff8e7;
    padding: 1.2rem 2rem;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 15px rgba(168,82,0,0.35);
}
.bhagya-header h1 {
    font-size: 1.8rem;
    letter-spacing: 6px;
    margin: 0 0 0.2rem 0;
    color: #ffd700;
    text-shadow: 1px 1px 4px rgba(0,0,0,0.5);
}
.bhagya-header .subhead {
    font-size: 0.85rem;
    color: #f5d78e;
    letter-spacing: 2px;
}

/* ── Birth info card ── */
.birth-card {
    background: linear-gradient(135deg, #fff9ee, #fff3d6);
    border: 1px solid #e0a040;
    border-radius: 10px;
    padding: 1rem 1.4rem;
    margin-bottom: 1rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem 2rem;
    box-shadow: 0 2px 8px rgba(160,80,0,0.1);
}
.birth-item { font-size: 0.9rem; color: #3a1a00; }
.birth-item b { color: #7a3500; }

/* ── Section headings ── */
.section-head {
    font-size: 1rem;
    font-weight: 700;
    color: #7a3500;
    border-bottom: 2px solid #e0a040;
    padding-bottom: 0.3rem;
    margin: 1.2rem 0 0.7rem 0;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #fff9ee !important;
    border: 1px solid #e0c070 !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    box-shadow: 0 2px 6px rgba(160,100,0,0.08) !important;
}
[data-testid="metric-container"] label {
    color: #8a5000 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #2a0e00 !important;
    font-size: 1rem !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #b8720a, #7a3500) !important;
    border: none !important;
    color: #fff8e7 !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    border-radius: 8px !important;
    padding: 0.6rem 1rem !important;
    box-shadow: 0 3px 10px rgba(120,50,0,0.4) !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #d4860c, #a04800) !important;
    box-shadow: 0 4px 14px rgba(120,50,0,0.55) !important;
    transform: translateY(-1px) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #fff3d6 !important;
    border-radius: 8px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px !important;
    color: #7a3500 !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #b8720a, #7a3500) !important;
    color: #fff8e7 !important;
}

/* ── Dataframes ── */
.stDataFrame {
    border: 1px solid #e0c070 !important;
    border-radius: 8px !important;
}

/* ── Divider ── */
hr { border-color: #e0c070 !important; }

/* ── South Indian chart cells ── */
.si-chart td {
    border: 2px solid #7a3500 !important;
    background: #fffcf5 !important;
    font-family: Georgia, serif !important;
    font-size: 12px !important;
    color: #2a0e00 !important;
}
.si-chart th {
    border: 2px solid #7a3500 !important;
    background: #fff3d6 !important;
    color: #7a3500 !important;
    font-size: 14px !important;
}
</style>
"""


def _chart_html_styled(by_sign, label):
    """South Indian chart with warm saffron styling."""
    cell_h, cell_w = 88, 88
    cs = (f"width:{cell_w}px;height:{cell_h}px;vertical-align:top;"
          f"padding:5px;font-size:12px;font-family:Georgia,serif;"
          f"color:#2a0e00;border:2px solid #7a3500;background:#fffcf5;")
    centre_s = (f"width:{cell_w*2}px;height:{cell_h*2}px;text-align:center;"
                f"vertical-align:middle;border:2px solid #7a3500;"
                f"background:linear-gradient(135deg,#fff3d6,#ffe8b0);"
                f"color:#7a3500;font-weight:bold;font-size:14px;"
                f"font-family:Georgia,serif;letter-spacing:2px;")

    def cell(sign):
        content = "<br>".join(by_sign.get(sign, []))
        return f'<td style="{cs}">{content}</td>'

    rows = (
        f"<tr>{cell(11)}{cell(0)}{cell(1)}{cell(2)}</tr>"
        f"<tr>{cell(10)}<th rowspan='2' colspan='2' style='{centre_s}'>{label}</th>{cell(3)}</tr>"
        f"<tr>{cell(9)}{cell(4)}</tr>"
        f"<tr>{cell(8)}{cell(7)}{cell(6)}{cell(5)}</tr>"
    )
    tbl_s = (f"border-collapse:collapse;border:3px solid #7a3500;"
             f"width:{cell_w*4+10}px;box-shadow:0 3px 12px rgba(120,50,0,0.2);")
    return f'<table style="{tbl_s}">{rows}</table>'


# ── Streamlit: Tab 1 — Horoscope ──────────────────────────────────────────────

def show_horoscope_tab(result):
    import pandas as pd_lib

    inp   = result["input"]
    cal   = result["calendar"]
    pd_   = result["planet_degs"]
    nav   = result["navamsa_positions"]
    shad  = result["shad"]
    bb    = result["bhava_bala"]
    mut   = result["mutual"]
    house = result["house_positions"]
    in_dt = inp["in_datetime"]

    # ── Birth info card ──
    st.markdown(f"""
    <div class="birth-card">
      <div class="birth-item"><b>Name</b><br>{inp["name"]}</div>
      <div class="birth-item"><b>Date of Birth</b><br>
        {in_dt.day:02d} / {in_dt.month:02d} / {in_dt.year} &nbsp;({cal["weekday"]})</div>
      <div class="birth-item"><b>Time</b><br>
        {in_dt.hour:02d}:{in_dt.minute:02d} &nbsp;LST</div>
      <div class="birth-item"><b>Place</b><br>{inp["birthplace"]}</div>
      <div class="birth-item"><b>Coordinates</b><br>
        {inp["lat_degs"]:.4f}&nbsp;{inp["lat_dirn"]} &nbsp;/&nbsp;
        {inp["long_degs"]:.4f}&nbsp;{inp["long_dirn"]}</div>
      <div class="birth-item"><b>Sunrise / Sunset</b><br>
        {cal["sunrise"].strftime("%H:%M")} &nbsp;/&nbsp; {cal["sunset"].strftime("%H:%M")}</div>
      <div class="birth-item"><b>Janma Nakshatra</b><br>
        {cal["janma_nakshatra"]} &nbsp;Pada&nbsp;{cal["janma_pada"]}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Calendar ──
    st.markdown('<div class="section-head">Panchangam</div>', unsafe_allow_html=True)
    r1 = st.columns(4)
    r1[0].metric("Paksham",  cal["paksham"])
    r1[1].metric("Thithi",   cal["thithi"])
    r1[2].metric("Yogam",    cal["yogam"])
    r1[3].metric("Karanam",  cal["karanam"])

    r2 = st.columns(4)
    r2[0].metric("Tamil Date",
                 f"{cal['tamil_day']} {cal['tamil_month']}\n{cal['tamil_year']}")
    r2[1].metric("Saka Date",
                 f"{cal['saka_day']} {cal['saka_month']}\n{cal['saka_year']}")
    r2[2].metric("Kali Year", str(cal["kali_year"]))
    r2[3].metric(f"{cal['dasa_lord']} Dasa balance",
                 f"Y {cal['dasa_y']}  M {cal['dasa_m']}  D {cal['dasa_d']}")

    # ── Charts ──
    st.markdown('<div class="section-head">Charts</div>', unsafe_allow_html=True)
    retro = result.get("planet_retrograde", [False] * 12)
    rasi_by_sign  = _planets_by_sign_r(pd_, retro)
    nav_by_sign   = _planets_by_navamsa_r(nav, retro)
    bhava_by_sign = _planets_by_bhava_r(result["bhava_positions"], retro)

    ch1, ch2, ch3 = st.columns(3)
    with ch1:
        st.markdown("<p style='text-align:center;font-weight:700;"
                    "color:#7a3500;letter-spacing:2px;'>RASI</p>",
                    unsafe_allow_html=True)
        components.html(_chart_html_styled(rasi_by_sign, "RASI"), height=430)
    with ch2:
        st.markdown("<p style='text-align:center;font-weight:700;"
                    "color:#7a3500;letter-spacing:2px;'>NAVAMSA</p>",
                    unsafe_allow_html=True)
        components.html(_chart_html_styled(nav_by_sign, "NAVAMSA"), height=430)
    with ch3:
        st.markdown("<p style='text-align:center;font-weight:700;"
                    "color:#7a3500;letter-spacing:2px;'>BHAVA</p>",
                    unsafe_allow_html=True)
        components.html(_chart_html_styled(bhava_by_sign, "BHAVA"), height=430)

    # ── Nirayana Longitudes ──
    st.markdown('<div class="section-head">Nirayana Longitudes</div>',
                unsafe_allow_html=True)
    rows = []
    for i, nm in enumerate(GRAHA_NAMES):
        degs = pd_[i]
        sign = int(degs // 30)
        d    = int(degs)
        m    = int((degs - d) * 60)
        nak, pada = _nakshatra_pada(degs)
        label = nm + ("(R)" if retro[i] else "")
        rows.append({
            "Graha":     label,
            "Long":      f"{d}\u00b0 {m:02d}\u2032",
            "Rasi":      RASI_NAMES[sign],
            "Nakshatra": NAKSHATRA[nak],
            "Pada":      pada,
            "Navamsa":   RASI_NAMES[int(nav[i])],
        })
    st.dataframe(pd_lib.DataFrame(rows), hide_index=True, use_container_width=True)

    # ── Bhava Cusps ──
    st.markdown('<div class="section-head">Bhava Cusps</div>', unsafe_allow_html=True)
    house_rows = []
    for i in range(12):
        degs = house[i]
        sign = int(degs // 30)
        d    = int(degs)
        m    = int((degs - d) * 60)
        house_rows.append({
            "Bhava": i + 1,
            "Long":  f"{d}\u00b0 {m:02d}\u2032",
            "Rasi":  RASI_NAMES[sign],
        })
    st.dataframe(pd_lib.DataFrame(house_rows), hide_index=True, use_container_width=True)

    # ── Shadbala ──
    st.markdown('<div class="section-head">Shadbala — Planetary Strength</div>',
                unsafe_allow_html=True)
    shad_components = [
        ("Sthana Bala",   "sthana"),
        ("Kala Bala",     "kala"),
        ("Dig Bala",      "dig"),
        ("Naisargika",    "naisa"),
        ("Chesta Bala",   "chesta"),
        ("Drik (+)",      "ben_drig"),
        ("Drik (-)",      "mal_drig"),
        ("TOTAL",         "total"),
        ("Min Required",  "min_required"),
        ("Relative",      "relative"),
        ("Ishta Bala",    "ishta"),
        ("Kashta Bala",   "kashta"),
    ]
    shad_data = {"Bala": [lbl for lbl, _ in shad_components]}
    for j, planet in enumerate(SHAD_LABELS):
        shad_data[planet] = [round(shad[key][j], 2) for _, key in shad_components]
    st.dataframe(pd_lib.DataFrame(shad_data), hide_index=True, use_container_width=True)

    # ── Bhava Bala ──
    st.markdown('<div class="section-head">Bhava Bala — House Strength</div>',
                unsafe_allow_html=True)
    bb_components = [
        ("Swami Bala", "swami"),
        ("Dig Bala",   "dig"),
        ("Drig Bala",  "drig"),
        ("Spl Drig",   "spl_drig"),
        ("Occ Str",    "ostr"),
        ("TOTAL",      "total"),
        ("Relative",   "relative"),
    ]
    bb_data = {"Bala": [lbl for lbl, _ in bb_components]}
    for h in range(12):
        bb_data[f"H{h+1}"] = [round(bb[key][h], 2) for _, key in bb_components]
    st.dataframe(pd_lib.DataFrame(bb_data), hide_index=True, use_container_width=True)

    # ── Mutual Disposition ──
    st.markdown('<div class="section-head">Mutual Disposition</div>',
                unsafe_allow_html=True)
    pnames = mut["planet_names"]
    mrasi  = pd_lib.DataFrame(mut["rasi"],    index=pnames, columns=pnames)
    mnav   = pd_lib.DataFrame(mut["navamsa"], index=pnames, columns=pnames)
    mrc, mnc = st.columns(2)
    with mrc:
        st.caption("Rasi")
        st.dataframe(mrasi, use_container_width=True)
    with mnc:
        st.caption("Navamsa")
        st.dataframe(mnav, use_container_width=True)


# ── Streamlit: Tab 2 — HTML Report ────────────────────────────────────────────

def show_html_tab(result):
    html = generate_html_report(result)

    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        st.download_button(
            label="⬇ Download HTML",
            data=html.encode("utf-8"),
            file_name=f"{result['input']['name']}_horoscope.html",
            mime="text/html",
            use_container_width=True,
        )
    with col2:
        try:
            pdf_bytes = generate_pdf(result)
            st.download_button(
                label="⬇ Download PDF",
                data=pdf_bytes,
                file_name=f"{result['input']['name']}_horoscope.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as _pdf_err:
            st.warning(f"PDF unavailable: {_pdf_err}")

    components.html(html, height=1150, scrolling=True)


# ── Sidebar helpers ───────────────────────────────────────────────────────────

def _sb_section(icon, title):
    st.markdown(
        f'<div class="sb-section"><span class="sb-section-title">'
        f'{icon}&nbsp;&nbsp;{title}</span></div>',
        unsafe_allow_html=True,
    )


# ── Main Streamlit App ────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Bhagyagraha – Hindu Horoscope",
        page_icon="🪐",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject CSS
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Page header ──
    st.markdown("""
    <div class="bhagya-header">
      <h1>&#9654;&nbsp; B H A G Y A G R A H A &nbsp;&#9664;</h1>
      <div class="subhead">Hindu Horoscope Calculator</div>
    </div>
    """, unsafe_allow_html=True)

    # ────────────────────── Sidebar ──────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1rem 0 0.5rem;">
          <div style="font-size:2.2rem;">🪐</div>
          <div style="font-size:1.1rem;font-weight:800;letter-spacing:3px;
                      color:#ffd700;">BHAGYAGRAHA</div>
          <div style="font-size:0.72rem;color:#c8a060;letter-spacing:1px;">
            BIRTH DATA</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── 1. Personal ──
        _sb_section("👤", "Personal")
        name       = st.text_input("Full Name",      value="Arunram",
                                   placeholder="Enter full name")
        birthplace = st.text_input("Place of Birth", value="Salem",
                                   placeholder="City, State")

        st.divider()

        # ── 2. Date & Time ──
        _sb_section("📅", "Date & Time of Birth")
        birth_date = st.date_input(
            "Date of Birth",
            value=dt.date(1983, 5, 28),
            min_value=dt.date(1800, 1, 1),
            max_value=dt.date(2100, 12, 31),
            format="DD/MM/YYYY",
        )
        birth_time = st.time_input(
            "Time of Birth (Local Standard Time)",
            value=dt.time(7, 11),
            step=60,
        )

        st.divider()

        # ── 3. Timezone ──
        _sb_section("🕐", "Timezone")
        tz_choice = st.selectbox(
            "Select timezone",
            options=list(TIMEZONES.keys()),
            index=0,
            label_visibility="collapsed",
        )
        diff_sec = TIMEZONES[tz_choice]

        st.divider()

        # ── 4. Location ──
        _sb_section("📍", "Location")
        city_choice = st.selectbox(
            "Preset city",
            options=list(CITIES.keys()),
            index=0,
            label_visibility="collapsed",
        )

        city_data = CITIES.get(city_choice)
        if city_data:
            def_lat     = city_data["lat"]
            def_lon     = city_data["lon"]
            def_lat_dir = 0 if city_data["lat_dir"] == "N" else 1
            def_lon_dir = 0 if city_data["lon_dir"] == "E" else 1
        else:
            def_lat, def_lon = 11.6643, 78.1460
            def_lat_dir, def_lon_dir = 0, 0

        # Use city_choice as part of the key so widgets reset when city changes
        ck = city_choice  # cache key suffix

        cl, cd = st.columns([3, 1])
        lat_val = cl.number_input(
            "Latitude", min_value=0.0, max_value=90.0,
            value=def_lat, step=0.0001, format="%.4f",
            key=f"lat_{ck}",
        )
        lat_dir = cd.radio("N/S", ["N", "S"], index=def_lat_dir,
                           key=f"latd_{ck}")

        ol, od = st.columns([3, 1])
        lon_val = ol.number_input(
            "Longitude", min_value=0.0, max_value=180.0,
            value=def_lon, step=0.0001, format="%.4f",
            key=f"lon_{ck}",
        )
        lon_dir = od.radio("E/W", ["E", "W"], index=def_lon_dir,
                           key=f"lond_{ck}")

        st.divider()

        calculate = st.button(
            "🔭  Calculate Horoscope",
            use_container_width=True,
            type="primary",
        )

    # ── Build input_params ──
    input_params = {
        "name":                 name,
        "birthplace":           birthplace,
        "in_datetime":          dt.datetime(birth_date.year, birth_date.month,
                                            birth_date.day,
                                            birth_time.hour, birth_time.minute),
        "diff_from_gst_in_sec": int(diff_sec),
        "lat_degs":             float(lat_val),
        "lat_dirn":             lat_dir,
        "long_degs":            float(lon_val),
        "long_dirn":            lon_dir,
    }

    # ── Compute ──
    if calculate:
        with st.spinner("Computing horoscope…"):
            try:
                st.session_state.result = compute(input_params)
            except Exception as e:
                st.error(f"Calculation error: {e}")
                st.stop()

    if "result" not in st.session_state:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:#7a3500;">
          <div style="font-size:4rem;margin-bottom:1rem;">🪐</div>
          <div style="font-size:1.3rem;font-weight:700;letter-spacing:2px;
                      margin-bottom:0.5rem;">Welcome to Bhagyagraha</div>
          <div style="font-size:0.95rem;color:#a06030;">
            Enter birth details in the sidebar and click
            <b>Calculate Horoscope</b> to begin.
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    result = st.session_state.result

    # ── Tabs ──
    tab1, tab2 = st.tabs(["📊  Horoscope", "🌐  HTML Report"])
    with tab1:
        show_horoscope_tab(result)
    with tab2:
        show_html_tab(result)

    # ── Footer ──
    st.markdown("""
    <hr style="margin-top:2rem;border-color:#e0c070;">
    <div style="text-align:center;font-size:0.75rem;color:#b08040;padding:0.5rem 0 1rem;">
      Bhagyagraha &nbsp;·&nbsp; Hindu Horoscope Calculator &nbsp;·&nbsp;
      Calculations based on Lahiri Ayanamsa (sidereal)
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
