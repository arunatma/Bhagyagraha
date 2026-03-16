"""
app.py — Bhagyagraha Streamlit Application

Provides a web UI for the horoscope calculator.  Computation, HTML/PDF report
generation, chart utilities and theme definitions live in their own modules.

Run with:
  streamlit run app.py
"""

import datetime as dt
import os
import re
import sys

import streamlit as st
import streamlit.components.v1 as components

# ── Computation modules ──────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
import constants as cn  # noqa: E402
import functions as fn  # noqa: E402
import shadbala as sb  # noqa: E402
from constants import (  # noqa: E402
    DASA_LORDS,
    DASA_YEARS,
    GRAHA_NAMES,
    KARANAM,
    NAKSHATRA,
    RASI_NAMES,
    SAKA_MONTH,
    TAMIL_MONTH,
    TAMIL_YEAR,
    THITHI,
    WDAYS,
    YOGAM,
)
from html_report import generate_single_page_html  # noqa: E402
from pdf_report import generate_pdf  # noqa: E402
from themes import THEME_NAMES, build_streamlit_css, get_theme  # noqa: E402

# ── City presets (lat, lon in decimal degrees) ────────────────────────────────
CITIES = {
    "Custom": None,
    "Chennai": {"lat": 13.0827, "lon": 80.2707, "lat_dir": "N", "lon_dir": "E"},
    "Salem": {"lat": 11.6643, "lon": 78.1460, "lat_dir": "N", "lon_dir": "E"},
    "Coimbatore": {"lat": 11.0168, "lon": 76.9558, "lat_dir": "N", "lon_dir": "E"},
    "Madurai": {"lat": 9.9252, "lon": 78.1198, "lat_dir": "N", "lon_dir": "E"},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946, "lat_dir": "N", "lon_dir": "E"},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867, "lat_dir": "N", "lon_dir": "E"},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777, "lat_dir": "N", "lon_dir": "E"},
    "Pune": {"lat": 18.5204, "lon": 73.8567, "lat_dir": "N", "lon_dir": "E"},
    "Delhi": {"lat": 28.6139, "lon": 77.2090, "lat_dir": "N", "lon_dir": "E"},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873, "lat_dir": "N", "lon_dir": "E"},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639, "lat_dir": "N", "lon_dir": "E"},
    "Varanasi": {"lat": 25.3176, "lon": 82.9739, "lat_dir": "N", "lon_dir": "E"},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714, "lat_dir": "N", "lon_dir": "E"},
    "Thiruvananthapuram": {
        "lat": 8.5241, "lon": 76.9366, "lat_dir": "N", "lon_dir": "E",
    },
    "Kochi": {"lat": 9.9312, "lon": 76.2673, "lat_dir": "N", "lon_dir": "E"},
    "Vijayawada": {"lat": 16.5062, "lon": 80.6480, "lat_dir": "N", "lon_dir": "E"},
    "Colombo": {"lat": 6.9271, "lon": 79.8612, "lat_dir": "N", "lon_dir": "E"},
    "London": {"lat": 51.5074, "lon": 0.1278, "lat_dir": "N", "lon_dir": "W"},
    "New York": {"lat": 40.7128, "lon": 74.0060, "lat_dir": "N", "lon_dir": "W"},
    "Singapore": {"lat": 1.3521, "lon": 103.8198, "lat_dir": "N", "lon_dir": "E"},
    "Dubai": {"lat": 25.2048, "lon": 55.2708, "lat_dir": "N", "lon_dir": "E"},
}

# ── Timezone presets (seconds offset from GMT) ────────────────────────────────
TIMEZONES = {
    "IST  \u2014 India               (+05:30)": 5 * 3600 + 30 * 60,
    "AoE  \u2014 Baker Island        (-12:00)": -12 * 3600,
    "NUT  \u2014 Niue                (-11:00)": -11 * 3600,
    "HST  \u2014 Hawaii              (-10:00)": -10 * 3600,
    "MART \u2014 Marquesas           (-09:30)": -9 * 3600 - 30 * 60,
    "AKST \u2014 Alaska              (-09:00)": -9 * 3600,
    "PST  \u2014 Los Angeles         (-08:00)": -8 * 3600,
    "MST  \u2014 Denver              (-07:00)": -7 * 3600,
    "CST  \u2014 Chicago             (-06:00)": -6 * 3600,
    "EST  \u2014 New York            (-05:00)": -5 * 3600,
    "AST  \u2014 Puerto Rico         (-04:00)": -4 * 3600,
    "NST  \u2014 Newfoundland        (-03:30)": -3 * 3600 - 30 * 60,
    "BRT  \u2014 S\u00e3o Paulo           (-03:00)": -3 * 3600,
    "GST  \u2014 South Georgia       (-02:00)": -2 * 3600,
    "AZOT \u2014 Azores              (-01:00)": -1 * 3600,
    "GMT  \u2014 London              (+00:00)": 0,
    "CET  \u2014 Paris / Berlin      (+01:00)": 1 * 3600,
    "EET  \u2014 Athens / Cairo      (+02:00)": 2 * 3600,
    "MSK  \u2014 Moscow              (+03:00)": 3 * 3600,
    "IRST \u2014 Tehran              (+03:30)": 3 * 3600 + 30 * 60,
    "GST  \u2014 Dubai               (+04:00)": 4 * 3600,
    "AFT  \u2014 Kabul               (+04:30)": 4 * 3600 + 30 * 60,
    "PKT  \u2014 Karachi             (+05:00)": 5 * 3600,
    "NPT  \u2014 Kathmandu           (+05:45)": 5 * 3600 + 45 * 60,
    "BST  \u2014 Dhaka               (+06:00)": 6 * 3600,
    "MMT  \u2014 Yangon              (+06:30)": 6 * 3600 + 30 * 60,
    "ICT  \u2014 Bangkok             (+07:00)": 7 * 3600,
    "CST  \u2014 China               (+08:00)": 8 * 3600,
    "ACWST \u2014 Eucla              (+08:45)": 8 * 3600 + 45 * 60,
    "JST  \u2014 Japan               (+09:00)": 9 * 3600,
    "ACST \u2014 Adelaide            (+09:30)": 9 * 3600 + 30 * 60,
    "AEST \u2014 Sydney              (+10:00)": 10 * 3600,
    "LHST \u2014 Lord Howe Island    (+10:30)": 10 * 3600 + 30 * 60,
    "SBT  \u2014 Solomon Islands     (+11:00)": 11 * 3600,
    "NZST \u2014 New Zealand         (+12:00)": 12 * 3600,
    "CHAST \u2014 Chatham Islands    (+12:45)": 12 * 3600 + 45 * 60,
    "TOT  \u2014 Tonga               (+13:00)": 13 * 3600,
    "LINT \u2014 Line Islands        (+14:00)": 14 * 3600,
}


# ── Helpers ──────────────────────────────────────────────────────────────────


def _nakshatra_pada(degs):
    nak = min(int(degs / (360.0 / 27)), 26)
    rem = degs - nak * (360.0 / 27)
    pada = int(rem / (360.0 / 108)) + 1
    return nak, pada


def _dasa_balance(moon_degs):
    """Return (lord_name, Y, M, D) for the Vimsottari dasa balance at birth."""
    nak_width = 360.0 / 27
    nak_idx = min(int(moon_degs / nak_width), 26)
    frac_remaining = 1.0 - (moon_degs - nak_idx * nak_width) / nak_width
    lord_idx = nak_idx % 9
    bal_years = frac_remaining * DASA_YEARS[lord_idx]
    y = int(bal_years)
    m = int((bal_years - y) * 12)
    d = round(((bal_years - y) * 12 - m) * 30)
    return DASA_LORDS[lord_idx], y, m, d


def _full_dasa_table(moon_degs, birth_dt):
    """Build full 120-year Vimsottari Dasa/Bukti table starting from birth."""
    nak_width = 360.0 / 27
    nak_idx = min(int(moon_degs / nak_width), 26)
    frac_remaining = 1.0 - (moon_degs - nak_idx * nak_width) / nak_width
    lord_idx = nak_idx % 9
    current = birth_dt + dt.timedelta(
        days=frac_remaining * DASA_YEARS[lord_idx] * 365.25
    )
    table = []
    for d in range(9):
        di = (lord_idx + d) % 9
        buktis = []
        for b in range(9):
            bi = (di + b) % 9
            current += dt.timedelta(
                days=DASA_YEARS[di] * DASA_YEARS[bi] / 120.0 * 365.25
            )
            buktis.append((DASA_LORDS[bi], current.strftime("%Y-%m-%d")))
        table.append({"dasa": DASA_LORDS[di], "buktis": buktis})
    return table


def _dt_to_hrs(d):
    return d.hour + d.minute / 60.0 + d.second / 3600.0


def _ramc_hms(r):
    h = int(r / 15)
    m = int((r / 15 - h) * 60)
    s = int(((r / 15 - h) * 60 - m) * 60)
    return f"{h}H-{m:02d}M-{s:02d}S"


# ── Core computation ─────────────────────────────────────────────────────────


def compute(input_params):
    """Run all calculations; return a single structured result dict."""
    sun_params = fn.get_sun_params(input_params)
    moon_params = fn.get_moon_params(input_params, sun_params)
    lagn_params = fn.get_lagn_params(input_params, sun_params)
    seven = fn.get_seven_planets(sun_params, moon_params)

    planet_names_order = [
        "LAGN", "SUN", "MOON", "MARS", "MERCURY", "JUPITER",
        "VENUS", "SATURN", "URANUS", "NEPTUNE", "RAHU", "KETU",
    ]

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

    # Velocity, latitude, retrograde
    planet_velocity = [None] * 12
    planet_latitude = [None] * 12
    planet_retrograde = [False] * 12

    planet_velocity[1] = abs(sun_params.get("hvel", 1.0))
    planet_latitude[1] = 0.0
    planet_velocity[2] = 13.18
    planet_latitude[2] = 0.0

    for _idx, _nm in zip(
        [3, 4, 5, 6, 7, 8, 9],
        ["MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "URANUS", "NEPTUNE"],
    ):
        _gvel = seven[_nm].get("gvel", 0.0)
        planet_velocity[_idx] = abs(_gvel)
        planet_latitude[_idx] = seven[_nm].get("lat", 0.0)
        planet_retrograde[_idx] = _gvel < 0

    ashta = sb.compute_ashtavarga(planet_degs)

    prec_degs = sun_params["prec"]
    ramc_degs = lagn_params["ramc"]
    lagn_degs = lagn_params["lagn"]
    lat_degs = input_params["lat_degs"]
    lat_dirn = input_params["lat_dirn"]
    south_hemi = bool(re.match(r"s|(south)", lat_dirn, re.IGNORECASE))

    nirayana_dhasa = fn.get_culm_point(ramc_degs, lat_degs, prec_degs, south_hemi)
    house_positions = fn.get_house_positions(
        lagn_degs, nirayana_dhasa, lat_degs, ramc_degs, prec_degs, south_hemi
    )

    bhava_positions, bhava1, bhava2 = fn.get_bhava_positions(
        house_positions, planet_degs
    )
    navamsa_positions = fn.get_navamsa_positions(planet_degs)
    rasi_positions = fn.get_rasi_positions(planet_degs)

    tamil_day, tamil_month, tamil_year = fn.calc_tamil_date(input_params)
    saka_day, saka_month, saka_year = fn.calc_saka_date(input_params["in_datetime"])
    kali_year = fn.get_kali_year(saka_year)

    yogam, karanam, thithi = fn.get_yogam_karanam_thithi(
        sun_params["true_long"], moon_params["moon"]
    )

    birth_day = (input_params["in_datetime"].weekday() + 1) % 7

    kali_dina = int(sun_params["d_epoch"]) + cn.kali_day

    p7_degs = [planet_degs[i] for i in [1, 2, 3, 4, 5, 6, 7]]
    all_signs = [int(d // 30) for d in planet_degs]
    all_deg_in = [d % 30 for d in planet_degs]
    all_min_in = [int((d % 30 - int(d % 30)) * 60) for d in planet_degs]
    all_navamsa = [int(n) for n in navamsa_positions]

    helio_5 = [
        seven["MARS"]["helio_long"], seven["MERCURY"]["helio_long"],
        seven["JUPITER"]["helio_long"], seven["VENUS"]["helio_long"],
        seven["SATURN"]["helio_long"],
    ]

    local_hrs = _dt_to_hrs(sun_params["local_time"])
    sunrise_hrs = _dt_to_hrs(sun_params["rise"])
    sunset_hrs = _dt_to_hrs(sun_params["set"])

    shad = sb.compute_shadbala(
        p7_degs, all_signs, all_deg_in, all_min_in, all_navamsa,
        helio_5, house_positions, bhava1, bhava2,
        local_hrs, sunrise_hrs, sunset_hrs,
        kali_dina, birth_day, prec_degs,
    )

    bhava_bala = sb.compute_bhava_bala(
        shad["total"], p7_degs, house_positions, bhava1, bhava2
    )

    mutual = sb.compute_mutual_disp(all_signs, all_navamsa)

    # Paksham / Thithi display
    paksha = "Krishna" if thithi >= 15 else "Shukla"
    thithi_idx = (thithi - 15) if thithi >= 15 else thithi
    if thithi_idx == 14:
        thithi_idx = 15

    moon_degs = planet_degs[2]
    janma_nak_idx, janma_pada = _nakshatra_pada(moon_degs)
    dasa_lord, dasa_y, dasa_m, dasa_d = _dasa_balance(moon_degs)

    return {
        "input": input_params,
        "planet_degs": planet_degs,
        "navamsa_positions": navamsa_positions,
        "rasi_positions": rasi_positions,
        "house_positions": house_positions,
        "bhava_positions": bhava_positions,
        "sun_params": sun_params,
        "moon_params": moon_params,
        "planet_velocity": planet_velocity,
        "planet_latitude": planet_latitude,
        "planet_retrograde": planet_retrograde,
        "sidereal_time": ramc_degs,
        "ayanamsa": prec_degs,
        "ashtavarga": ashta,
        "calendar": {
            "paksham": f"{paksha} Paksham",
            "thithi": THITHI[thithi_idx],
            "yogam": YOGAM[yogam],
            "karanam": KARANAM[karanam],
            "tamil_day": tamil_day,
            "tamil_month": TAMIL_MONTH[tamil_month],
            "tamil_year": TAMIL_YEAR[tamil_year % 60],
            "saka_day": saka_day,
            "saka_month": SAKA_MONTH[saka_month],
            "saka_year": saka_year,
            "kali_year": kali_year,
            "weekday": WDAYS[birth_day],
            "sunrise": sun_params["rise"],
            "sunset": sun_params["set"],
            "janma_nakshatra": NAKSHATRA[janma_nak_idx],
            "janma_pada": janma_pada,
            "dasa_lord": dasa_lord,
            "dasa_y": dasa_y,
            "dasa_m": dasa_m,
            "dasa_d": dasa_d,
            "dasa_table": _full_dasa_table(moon_degs, input_params["in_datetime"]),
        },
        "shad": shad,
        "bhava_bala": bhava_bala,
        "mutual": mutual,
    }


# ── Main Streamlit App ───────────────────────────────────────────────────────


def main():
    st.set_page_config(
        page_title="Bhagyagraha \u2013 Hindu Horoscope",
        page_icon="\U0001fa90",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ────────────────────── Sidebar ──────────────────────
    with st.sidebar:
        # Theme selector at top
        theme_name = st.selectbox(
            "Theme",
            THEME_NAMES,
            index=0,
            key="theme_select",
        )
        theme = get_theme(theme_name)

        st.divider()

        st.markdown(
            f'<div style="text-align:center;padding:0.5rem 0;">'
            f'<div style="font-size:1.1rem;font-weight:800;letter-spacing:3px;'
            f'color:{theme["accent"]};">BHAGYAGRAHA</div></div>',
            unsafe_allow_html=True,
        )

        st.divider()

        name = st.text_input(
            "Full Name", value="Sample Data", placeholder="Enter full name"
        )

        st.divider()

        birth_date = st.date_input(
            "Date of Birth",
            value=dt.date(1947, 8, 15),
            min_value=dt.date(1800, 1, 1),
            max_value=dt.date(2100, 12, 31),
            format="DD/MM/YYYY",
        )

        DEFAULT_TIME = "10:30"
        if "time_input" not in st.session_state:
            st.session_state.time_input = DEFAULT_TIME
        try:
            dt.datetime.strptime(st.session_state.time_input, "%H:%M")
        except ValueError:
            st.session_state.time_input = DEFAULT_TIME

        time_str = st.text_input(
            "Time of Birth (Local Standard Time HH:MM)", key="time_input"
        )
        birth_time = dt.datetime.strptime(time_str, "%H:%M").time()

        tz_choice = st.selectbox(
            "Select timezone",
            options=list(TIMEZONES.keys()),
            index=0,
            label_visibility="collapsed",
        )
        diff_sec = TIMEZONES[tz_choice]

        st.divider()

        birthplace = st.text_input(
            "Place of Birth", value="Salem", placeholder="City, State"
        )

        def_lat, def_lon = 11.6643, 78.1460
        ck = 0

        cl, cd = st.columns([3, 1])
        lat_val = cl.number_input(
            "Latitude", min_value=0.0, max_value=90.0,
            value=def_lat, step=0.0001, format="%.4f", key=f"lat_{ck}",
        )
        lat_dir = cd.radio("N/S", ["N", "S"], index=0, key=f"latd_{ck}")

        ol, od = st.columns([3, 1])
        lon_val = ol.number_input(
            "Longitude", min_value=0.0, max_value=180.0,
            value=def_lon, step=0.0001, format="%.4f", key=f"lon_{ck}",
        )
        lon_dir = od.radio("E/W", ["E", "W"], index=0, key=f"lond_{ck}")

        st.divider()

        calculate = st.button(
            "\U0001f52d  Calculate", use_container_width=True, type="primary",
        )

    # Inject themed CSS
    st.markdown(build_streamlit_css(theme), unsafe_allow_html=True)

    # ── Page header ──
    st.markdown(
        f'<div class="bhagya-header">'
        f'<h1>\U0001fa90 BHAGYAGRAHA \U0001fa90</h1></div>',
        unsafe_allow_html=True,
    )

    # ── Build input_params ──
    input_params = {
        "name": name,
        "birthplace": birthplace,
        "in_datetime": dt.datetime(
            birth_date.year, birth_date.month, birth_date.day,
            birth_time.hour, birth_time.minute,
        ),
        "diff_from_gst_in_sec": int(diff_sec),
        "lat_degs": float(lat_val),
        "lat_dirn": lat_dir,
        "long_degs": float(lon_val),
        "long_dirn": lon_dir,
    }

    # ── Compute ──
    if calculate:
        with st.spinner("Computing horoscope\u2026"):
            try:
                st.session_state.result = compute(input_params)
                st.session_state.result_theme = theme_name
            except Exception as e:
                st.error(f"Calculation error: {e}")
                st.stop()

    if "result" not in st.session_state:
        st.markdown(
            f'<div style="text-align:center;padding:4rem 2rem;color:{theme["body_text"]};">'
            f'<div style="font-size:4rem;margin-bottom:1rem;">\U0001fa90</div>'
            f'<div style="font-size:1.3rem;font-weight:700;letter-spacing:2px;'
            f'margin-bottom:0.5rem;color:{theme["accent"]};">Welcome to Bhagyagraha</div>'
            f'<div style="font-size:0.95rem;color:{theme["muted_text"]};">'
            f'Enter birth details in the sidebar and click <b>Calculate</b> to begin.'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        st.stop()

    result = st.session_state.result
    active_theme = st.session_state.get("result_theme", theme_name)

    # ── Download buttons + single-page HTML display ──
    single_html = generate_single_page_html(result, active_theme)

    _, btn_col1, btn_col2, _ = st.columns([2, 1, 1, 2])
    with btn_col1:
        st.download_button(
            label="\u2b07 Single Page Download",
            data=single_html.encode("utf-8"),
            file_name=f"{result['input']['name']}_horoscope.html",
            mime="text/html",
            use_container_width=True,
        )
    with btn_col2:
        try:
            pdf_bytes = generate_pdf(result)
            st.download_button(
                label="\u2b07 Complete Download",
                data=pdf_bytes,
                file_name=f"{result['input']['name']}_horoscope.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as _pdf_err:
            st.warning(f"PDF unavailable: {_pdf_err}")

    components.html(single_html, height=1000, scrolling=False)

    # ── Footer ──
    st.markdown(
        f'<hr style="margin-top:2rem;border-color:{theme["table_border"]};">'
        f'<div style="text-align:center;font-size:0.75rem;color:{theme["muted_text"]};'
        f'padding:0.5rem 0 1rem;">'
        f'Bhagyagraha &nbsp;\u00b7&nbsp; Hindu Horoscope Calculator &nbsp;\u00b7&nbsp;'
        f'Calculations based on Lahiri Ayanamsa (sidereal)</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
