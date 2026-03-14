"""
astro.py — Entry point for Bhagyagraha horoscope calculation.

Reads data.txt (one field per line), computes all planetary positions,
Hindu calendar data, house positions, Shadbala, and prints output.

data.txt format (one token/line):
    Name
    Day
    Month
    Year
    Hour
    Minute
    BirthPlace
    LatDeg
    LatMin
    LatDir   (N or S)
    LongDeg
    LongMin
    LongDir  (E or W)
    DiffFromGMT_Hour
    DiffFromGMT_Min
"""

import datetime as dt
import math
import os
import sys

import constants as cn
import functions as fn
import shadbala as sb


# ---------------------------------------------------------------------------
# Constants / name tables (from SUN.H)
# ---------------------------------------------------------------------------

GRAHA_NAMES = ["LAGN", "SUN ", "MOON", "MARS", "MERC", "JUPT",
               "VENU", "SATN", "URAN", "NEPT", "RAHU", "KETU"]

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

DASA_TIME = [7, 20, 6, 10, 7, 18, 16, 19, 17]  # years, for 9 planets
RULER     = [11, 6, 1, 2, 3, 10, 5, 7, 4]       # planet indices for dasas


# ---------------------------------------------------------------------------
# Data file reading
# ---------------------------------------------------------------------------

def read_data_file(path="data.txt"):
    """Read data.txt and return input_params dict."""
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        sys.exit(1)

    with open(path, "r") as f:
        lines = [l.rstrip("\n") for l in f]

    name        = lines[0].strip()
    day         = int(lines[1])
    month       = int(lines[2])
    year        = int(lines[3])
    hour        = int(lines[4])
    minute      = int(lines[5])
    birthplace  = lines[6].strip()
    lat_deg     = int(lines[7])
    lat_min     = int(lines[8])
    lat_dir     = lines[9].strip().upper()
    long_deg    = int(lines[10])
    long_min    = int(lines[11])
    long_dir    = lines[12].strip().upper()
    gmt_h       = int(lines[13])
    gmt_m       = int(lines[14])

    lat_degs  = lat_deg  + lat_min  / 60.0
    long_degs = long_deg + long_min / 60.0

    diff_from_gst_in_sec = (gmt_h * 3600 + gmt_m * 60)
    if long_dir == "W":
        diff_from_gst_in_sec = -diff_from_gst_in_sec

    in_datetime = dt.datetime(year, month, day, hour, minute)

    params = {
        "name":                 name,
        "birthplace":           birthplace,
        "in_datetime":          in_datetime,
        "diff_from_gst_in_sec": diff_from_gst_in_sec,
        "lat_degs":             lat_degs,
        "lat_dirn":             lat_dir,
        "long_degs":            long_degs,
        "long_dirn":            long_dir,
    }
    return params


# ---------------------------------------------------------------------------
# Helper: degrees to deg-min-sec string
# ---------------------------------------------------------------------------

def _dms(degs):
    d = int(degs)
    m = int((degs - d) * 60)
    s = int(((degs - d) * 60 - m) * 60 + 0.5)
    return d, m, s


def _fmt_long(degs):
    d, m, s = _dms(degs)
    return f"{d:3d}-{m:02d} ({s:02d}\")"


def _nakshatra_pada(planet_degs):
    """Return (nakshatra_idx, pada) for a planet position in degrees."""
    nak = int(planet_degs / (360.0 / 27))
    nak = min(nak, 26)
    rem = planet_degs - nak * (360.0 / 27)
    pada = int(rem / (360.0 / 108)) + 1
    return nak, pada


# ---------------------------------------------------------------------------
# Main computation
# ---------------------------------------------------------------------------

def run():
    input_params = read_data_file()

    # Core calculations
    sun_params   = fn.get_sun_params(input_params)
    moon_params  = fn.get_moon_params(input_params, sun_params)
    lagn_params  = fn.get_lagn_params(input_params, sun_params)
    seven        = fn.get_seven_planets(sun_params, moon_params)

    # Assemble planet position list (degrees) in C order (0=Lagn, 1=Sun … 11=Ketu)
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

    # House cusps
    prec_degs    = sun_params["prec"]
    ramc_degs    = lagn_params["ramc"]
    lagn_degs    = lagn_params["lagn"]
    lat_degs     = input_params["lat_degs"]
    lat_dirn     = input_params["lat_dirn"]
    long_degs    = input_params["long_degs"]
    long_dirn    = input_params["long_dirn"]
    import re
    south_hemi   = bool(re.match(r"s|(south)", lat_dirn, re.IGNORECASE))

    lt_corr_degs   = fn.get_local_time_correction(sun_params["local_time"])
    nirayana_dhasa = fn.get_culm_point(ramc_degs, lat_degs, prec_degs, south_hemi)
    house_positions = fn.get_house_positions(lagn_degs, nirayana_dhasa,
                                              lat_degs, ramc_degs, prec_degs,
                                              south_hemi)

    bhava_result = fn.get_bhava_positions(house_positions, planet_degs)
    bhava_positions, bhava1, bhava2 = bhava_result

    navamsa_positions = fn.get_navamsa_positions(planet_degs)
    rasi_positions    = fn.get_rasi_positons(planet_degs)

    # Calendar data
    tamil_day, tamil_month, tamil_year = fn.calc_tamil_date(input_params)
    saka_day, saka_month, saka_year    = fn.calc_saka_date(input_params["in_datetime"])
    kali_year                          = fn.get_kali_year(saka_year)

    yogam, karanam, thithi = fn.get_yogam_karanam_thithi(
        sun_params["true_long"], moon_params["moon"])

    # Weekday
    birth_day = input_params["in_datetime"].weekday()
    birth_day = (birth_day + 1) % 7   # Python Mon=0; we want Sun=0

    # KaliDina
    epoch_days = sun_params["d_epoch"]
    kali_dina  = int(epoch_days) + cn.kali_day

    # Shadbala inputs
    p7_degs    = [planet_degs[i] for i in [1, 2, 3, 4, 5, 6, 7]]   # Sun…Saturn
    p7_signs   = [int(d // 30) for d in p7_degs]
    p7_deg_in  = [d % 30 for d in p7_degs]
    p7_min_in  = [int((d % 30 - int(d % 30)) * 60) for d in p7_degs]

    # All 12 signs/degs for saptha-vargaja (index 0=Lagna, 1=Sun…)
    all_signs   = [int(d // 30) for d in planet_degs]
    all_deg_in  = [d % 30 for d in planet_degs]
    all_min_in  = [int((d % 30 - int(d % 30)) * 60) for d in planet_degs]
    all_navamsa = [int(n) for n in navamsa_positions]

    # Heliocentric for Mars, Mercury, Jupiter, Venus, Saturn
    helio_5 = [
        seven["MARS"]["helio_long"],
        seven["MERCURY"]["helio_long"],
        seven["JUPITER"]["helio_long"],
        seven["VENUS"]["helio_long"],
        seven["SATURN"]["helio_long"],
    ]

    local_time   = sun_params["local_time"]
    sunrise_dt   = sun_params["rise"]
    sunset_dt    = sun_params["set"]

    def dt_to_hrs(d):
        return d.hour + d.minute / 60.0 + d.second / 3600.0

    local_hrs   = dt_to_hrs(local_time)
    sunrise_hrs = dt_to_hrs(sunrise_dt)
    sunset_hrs  = dt_to_hrs(sunset_dt)

    shad = sb.compute_shadbala(
        p7_degs, all_signs, all_deg_in, all_min_in, all_navamsa,
        helio_5, house_positions, bhava1, bhava2,
        local_hrs, sunrise_hrs, sunset_hrs,
        kali_dina, birth_day, prec_degs,
    )

    bhava_bala = sb.compute_bhava_bala(
        shad["total"], p7_degs, house_positions, bhava1, bhava2)

    mutual = sb.compute_mutual_disp(all_signs, all_navamsa)

    # -------------------------------------------------------------------
    # Print output
    # -------------------------------------------------------------------

    name      = input_params["name"]
    birthplace = input_params["birthplace"]
    in_dt     = input_params["in_datetime"]

    print(f"\n{'='*70}")
    print(f"  B H A G Y A G R A H A   —   Horoscope")
    print(f"{'='*70}")
    print(f"  Name        : {name}")
    print(f"  Birth Place : {birthplace}")
    print(f"  Date        : {in_dt.day:02d}/{in_dt.month:02d}/{in_dt.year}")
    print(f"  Time        : {in_dt.hour:02d}:{in_dt.minute:02d}  (Local Standard Time)")
    print(f"  Latitude    : {input_params['lat_degs']:.4f} {input_params['lat_dirn']}")
    print(f"  Longitude   : {input_params['long_degs']:.4f} {input_params['long_dirn']}")
    print(f"  Sunrise     : {sunrise_dt.strftime('%H:%M:%S')}")
    print(f"  Sunset      : {sunset_dt.strftime('%H:%M:%S')}")
    print(f"  Weekday     : {WDAYS[birth_day]}")
    print()

    # Calendar
    print(f"{'='*70}")
    print(f"  CALENDAR DATA")
    print(f"{'='*70}")
    paksha = "Krishna" if thithi >= 15 else "Shukla"
    thithi_idx = (thithi - 15) if thithi >= 15 else thithi
    if thithi_idx == 14:
        thithi_idx = 15
    print(f"  Paksham     : {paksha} Paksham")
    print(f"  Thithi      : {THITHI[thithi_idx]}")
    print(f"  Yogam       : {YOGAM[yogam]}")
    print(f"  Karanam     : {KARANAM[karanam]}")
    print(f"  Tamil Date  : {tamil_day}  {TAMIL_MONTH[tamil_month]}  {TAMIL_YEAR[tamil_year % 60]}")
    print(f"  Saka Date   : {saka_day} {SAKA_MONTH[saka_month]} {saka_year}")
    print(f"  Kali Year   : {kali_year}")
    print()

    # Planetary positions
    print(f"{'='*70}")
    print(f"  NIRAYANA LONGITUDES")
    print(f"{'='*70}")
    print(f"  {'Planet':<8}  {'Long':>8}  {'Nakshatra':<14}  Pada  {'Rasi':<12}  Navamsa")
    print(f"  {'-'*65}")
    for i, nm in enumerate(GRAHA_NAMES):
        degs = planet_degs[i]
        sign = int(degs // 30)
        d    = int(degs % 30)
        m    = int((degs % 30 - d) * 60)
        nak, pada = _nakshatra_pada(degs)
        nav_sign  = int(navamsa_positions[i])
        print(f"  {nm:<8}  {d:3d}-{m:02d}      {NAKSHATRA[nak]:<14}  {pada}     "
              f"{RASI_NAMES[sign]:<12}  {RASI_NAMES[nav_sign]}")
    print()

    # House cusps
    print(f"{'='*70}")
    print(f"  BHAVA CUSPS (House Positions)")
    print(f"{'='*70}")
    for i in range(12):
        degs = house_positions[i]
        sign = int(degs // 30)
        d    = int(degs % 30)
        m    = int((degs % 30 - d) * 60)
        print(f"  House {i+1:2d}:  {d:3d}-{m:02d}  {RASI_NAMES[sign]}")
    print()

    # Shadbala summary
    PLANET_LABELS = ["Sun    ", "Moon   ", "Mars   ", "Merc   ",
                     "Jupt   ", "Venus  ", "Saturn "]
    print(f"{'='*70}")
    print(f"  SHADBALA")
    print(f"{'='*70}")
    print(f"  {'Balam':<22}" + "".join(f"{l}" for l in PLANET_LABELS))
    print(f"  {'-'*70}")
    rows = [
        ("Sthana Bala",     "sthana"),
        ("Kala Bala",       "kala"),
        ("Dig Bala",        "dig"),
        ("Naisargika Bala", "naisa"),
        ("Chesta Bala",     "chesta"),
        ("Drik Bala (+)",   "ben_drig"),
        ("Drik Bala (-)",   "mal_drig"),
    ]
    for label, key in rows:
        vals = shad[key]
        print(f"  {label:<22}" + "".join(f"{v:<8.2f}" for v in vals))
    print(f"  {'-'*70}")
    print(f"  {'TOTAL':<22}" + "".join(f"{v:<8.2f}" for v in shad["total"]))
    print(f"  {'Min Required':<22}" + "".join(f"{v:<8.1f}" for v in shad["min_required"]))
    print(f"  {'Relative Strength':<22}" + "".join(f"{v:<8.2f}" for v in shad["relative"]))
    print(f"  {'-'*70}")
    print(f"  {'Ishta Bala':<22}" + "".join(f"{v:<8.2f}" for v in shad["ishta"]))
    print(f"  {'Kashta Bala':<22}" + "".join(f"{v:<8.2f}" for v in shad["kashta"]))
    net = [shad["ishta"][i] - shad["kashta"][i] for i in range(7)]
    print(f"  {'Ishta-Kashta Net':<22}" + "".join(f"{v:<8.2f}" for v in net))
    print()

    # Bhava Bala
    print(f"{'='*70}")
    print(f"  BHAVA BALA")
    print(f"{'='*70}")
    h_labels = "".join(f"{i+1:<6}" for i in range(12))
    print(f"  Bhava        {h_labels}")
    print(f"  {'-'*75}")
    for label, key in [("Swami Bala", "swami"), ("Dig Bala", "dig"),
                        ("Drig Bala", "drig"), ("Spl Drig", "spl_drig"),
                        ("Occ Str", "ostr")]:
        vals = bhava_bala[key]
        print(f"  {label:<14}" + "".join(f"{v:<6.2f}" for v in vals))
    print(f"  {'-'*75}")
    print(f"  {'Total':<14}" + "".join(f"{v:<6.2f}" for v in bhava_bala["total"]))
    print(f"  {'Relative':<14}" + "".join(f"{v:<6.2f}" for v in bhava_bala["relative"]))
    print()

    # Mutual disposition
    print(f"{'='*70}")
    print(f"  MUTUAL DISPOSITION (RASI)")
    print(f"{'='*70}")
    pnames = mutual["planet_names"]
    header = "           " + "  ".join(f"{n:<5}" for n in pnames)
    print(f"  {header}")
    for i, row in enumerate(mutual["rasi"]):
        line = f"  {pnames[i]:<10}" + "  ".join(row)
        print(line)
    print()

    print(f"  MUTUAL DISPOSITION (NAVAMSA)")
    print(f"  {header}")
    for i, row in enumerate(mutual["navamsa"]):
        line = f"  {pnames[i]:<10}" + "  ".join(row)
        print(line)
    print()

    print(f"{'='*70}")
    print(f"  Calculation complete.")
    print(f"{'='*70}\n")


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run()
