"""
compare.py — Bhagyagraha: Python vs C Output Comparison Framework
=================================================================

Compares the Python (astro.py) horoscope output against the original C program
(horos.exe / HOR.OUT) field-by-field, flagging mismatches.

Usage
-----
# Use an existing HOR.OUT reference file:
  python compare.py --input data.txt --c-ref tests/name/expected.out

# Run horos.exe live to generate fresh C output, then compare:
  python compare.py --input data.txt --horos ../../../Bhagyagraha/bin/horos.exe

# Show ALL fields (not just mismatches):
  python compare.py --input data.txt --c-ref tests/name/expected.out --verbose

# Limit to one section (calendar | planets | bhava-cusps | shadbala | bhava-bala | mutual-disp):  # noqa: E501
  python compare.py --input data.txt --c-ref tests/name/expected.out --section planets

# Run all built-in test cases (requires tests/ directory):
  python compare.py --all-tests [--horos path/to/horos.exe]
"""

import argparse
import io
import os
import re
import shutil
import subprocess
import sys

# Force UTF-8 output on Windows terminals (avoids cp1252 UnicodeEncodeError)
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ── Constants ──────────────────────────────────────────────────────────────────

WORKTREE = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.normpath(
    os.path.join(WORKTREE, "..", "..", "..", "Bhagyagraha", "bin")
)
HOROS_EXE = os.path.join(BIN_DIR, "horos.exe")
TESTS_DIR = os.path.join(WORKTREE, "tests")

PLANET_ORDER = [
    "LAGN",
    "SUN",
    "MOON",
    "MARS",
    "MERC",
    "JUPT",
    "VENU",
    "SATN",
    "URAN",
    "NEPT",
    "RAHU",
    "KETU",
]
SHAD_PLANETS = ["Sun", "Moon", "Mars", "Merc", "Jupt", "Venus", "Saturn"]
MUTUAL_PLANETS = ["Sun", "Moon", "Mars", "Merc", "Jupt", "Venu", "Satn", "Rahu", "Ketu"]

from constants import RASI_TO_IDX  # noqa: E402

# Thresholds
DEG_PASS = 0.05  # < 3 arcmin
DEG_WARN = 0.50  # < 30 arcmin
BAL_PASS = 0.05
BAL_WARN = 0.15

# ── Helpers ────────────────────────────────────────────────────────────────────


def _dm_to_deg(deg_str, min_str):
    """Convert 'deg' and 'min' strings to decimal degrees."""
    return int(deg_str) + int(min_str) / 60.0


def _deg_status(delta):
    if delta < DEG_PASS:
        return "PASS"
    if delta < DEG_WARN:
        return "WARN"
    return "FAIL"


def _bal_status(delta):
    if delta < BAL_PASS:
        return "PASS"
    if delta < BAL_WARN:
        return "WARN"
    return "FAIL"


def _str_status(a, b):
    return "PASS" if a.strip().lower() == b.strip().lower() else "FAIL"


# ── C Output Parser (HOR.OUT) ──────────────────────────────────────────────────


def parse_c_output(text):
    """Parse HOR.OUT text into a structured dict."""
    data = {
        "name": "",
        "calendar": {},
        "planets": {},
        "bhava_beg": [],
        "bhava_mid": [],
        "shadbala": {},
        "bhava_bala": {},
        "mutual_rasi": [],
        "mutual_navamsa": [],
    }

    lines = text.splitlines()

    # ── Name ──
    for line in lines:
        m = re.search(r"NAME\s*:\s*(.+?)(?:\s{3,}|$)", line)
        if m:
            data["name"] = m.group(1).strip()
            break

    # ── Calendar ──
    cal = {}
    for line in lines:
        m = re.search(r"Paksham\s*:\s*(.+?)(?:\s{4,}|Yogam)", line)
        if m:
            cal["paksham"] = m.group(1).strip()
        m = re.search(r"Yogam\s*:\s*(\S+)", line)
        if m:
            cal["yogam"] = m.group(1).strip()
        m = re.search(r"Thithi\s*:\s*(\S+)", line)
        if m:
            cal["thithi"] = m.group(1).strip()
        m = re.search(r"Karanam\s*:\s*(\S+)", line)
        if m:
            cal["karanam"] = m.group(1).strip()
        m = re.search(r"Tamil Date\s*:\s*(\d+)\s+(\w+)\s+(\w+)", line)
        if m:
            cal["tamil_date"] = f"{m.group(1)} {m.group(2)} {m.group(3)}"
        m = re.search(r"Saka Date\s*:\s*(.+?)(?:\s{3,}|$)", line)
        if m:
            cal["saka_date"] = m.group(1).strip()
        m = re.search(r"Kali Year\s*:\s*(\d+)", line)
        if m:
            cal["kali_year"] = int(m.group(1))
        m = re.search(r"Sun Rise.*?:\s*(\d+)H-(\d+)M", line)
        if m:
            cal["sunrise"] = f"{m.group(1)}:{m.group(2)}"
        m = re.search(r"Sun Set.*?:\s*(\d+)H-(\d+)M", line)
        if m:
            cal["sunset"] = f"{m.group(1)}:{m.group(2)}"
        m = re.search(r"\((\w+day)\)", line)
        if m:
            cal["weekday"] = m.group(1)
    data["calendar"] = cal

    # ── Nirayana Longitudes ──
    # C format:  LAGN      60-31    Mrigasirsha     3    MARS      7    0  0  0      0- 0  # noqa: E501
    planet_pat = re.compile(
        r"^\s*(LAGN|SUN|MOON|MARS|MERC|JUPT(?:\(R\))?|VENU|SATN(?:\(R\))?|"
        r"URAN(?:\(R\))?|NEPT(?:\(R\))?|RAHU|KETU)\s+"
        r"(\d+)-(\d+)\s+"  # longitude deg-min
        r"(\w+)\s+"  # nakshatra
        r"(\d+)\s+"  # pada
        r"(\w+)\s+"  # ruler
        r"(\d+)"  # navamsa number
    )
    for line in lines:
        m = planet_pat.match(line)
        if m:
            name = m.group(1).rstrip("(R)").rstrip("(").strip()
            # Normalise: JUPT(R) → JUPT, SATN(R) → SATN, etc.
            name = re.sub(r"\(R\)", "", name).strip()
            deg = int(m.group(2))
            mins = int(m.group(3))
            naks = m.group(4)
            pada = int(m.group(5))
            nav = int(m.group(7))  # 1-12
            long_abs = deg + mins / 60.0
            data["planets"][name] = {
                "long_abs": long_abs,
                "nakshatra": naks,
                "pada": pada,
                "navamsa_num": nav - 1,  # store as 0-11
            }

    # ── Bhava BEG / MID ──
    # BEG : 1 TO 6     45-15     73-29    100- 0    128-44    160-28    193-30
    #       7 TO 12   225-15    253-29    280- 0    308-44    340-28     13-30
    beg_vals = []
    mid_vals = []
    in_bhava = False
    for line in lines:
        if "BHAVA" in line and "DEG" in line:
            in_bhava = True
        if not in_bhava:
            continue
        m = re.search(
            r"BEG\s*:.*?(\d+)-(\d+)\s+(\d+)-(\d+)\s+(\d+)-\s*(\d+)\s+(\d+)-(\d+)\s+(\d+)-(\d+)\s+(\d+)-(\d+)",  # noqa: E501
            line,
        )
        if m:
            vals = [
                int(m.group(i)) + int(m.group(i + 1)) / 60.0 for i in range(1, 13, 2)
            ]
            beg_vals.extend(vals)
        m = re.search(
            r"^\s+(\d+)-(\d+)\s+(\d+)-(\d+)\s+(\d+)-\s*(\d+)\s+(\d+)-(\d+)\s+(\d+)-(\d+)\s+(\d+)-(\d+)",  # noqa: E501
            line,
        )
        if m and len(beg_vals) == 6 and len(beg_vals) < 12:
            vals = [
                int(m.group(i)) + int(m.group(i + 1)) / 60.0 for i in range(1, 13, 2)
            ]
            beg_vals.extend(vals)
        m = re.search(
            r"MID\s*:.*?(\d+)-(\d+)\s+(\d+)-(\d+)\s+(\d+)-\s*(\d+)\s+(\d+)-(\d+)\s+(\d+)-(\d+)\s+(\d+)-(\d+)",  # noqa: E501
            line,
        )
        if m:
            vals = [
                int(m.group(i)) + int(m.group(i + 1)) / 60.0 for i in range(1, 13, 2)
            ]
            mid_vals.extend(vals)
        if len(mid_vals) == 6:
            # look for the second MID row
            pass
    # Second rows (7-12) follow the same continuation pattern but tagged differently
    # Reparse in a two-pass approach
    beg_vals, mid_vals = _parse_bhava_beg_mid(lines)
    data["bhava_beg"] = beg_vals
    data["bhava_mid"] = mid_vals

    # ── Shadbala ──
    shad = {}
    shad_map = {
        "Sthana Bala": "sthana",
        "Kala Bala": "kala",
        "Dig Bala": "dig",
        "Naisargika Bala": "naisa",
        "Chesta Bala": "chesta",
        "Drik Bala(Benefic)": "ben_drig",
        "Drik Bala(Malefic)": "mal_drig",
        "TOTAL": "total",
        "Relative": "relative",
        "Ishta Bala": "ishta",
        "Kashta Bala": "kashta",
        "Ishta-Kashta Net": "net",
    }
    in_shad = False
    pending_key = None  # for two-line entries like "Relative\nStrength ..."
    for line in lines:
        if "SHADBALA" in line:
            in_shad = True
        if "BHAVABALA" in line:
            in_shad = False
        if not in_shad:
            continue
        # Handle continuation line for two-line entries (e.g. "Relative\nStrength ...")
        if pending_key:
            nums = re.findall(r"-?\d+\.\d+", line)
            if nums:
                shad[pending_key] = [float(x) for x in nums[:7]]
            pending_key = None
            continue
        for label, key in shad_map.items():
            if line.strip().startswith(label):
                nums = re.findall(r"-?\d+\.\d+", line)
                if nums:
                    shad[key] = [float(x) for x in nums[:7]]
                else:
                    pending_key = key  # values on next line
                break
    # Minimum required (string row, skip)
    data["shadbala"] = shad

    # ── Bhava Bala ──
    bhava_bal = {}
    bhava_map = {
        "  1 ": "swami",
        "  2 ": "dig",
        "  3 ": "drig",
        "  4 ": "spl",
        "  5 ": "occ",
        "TOTAL": "total",
        "Rel.": "relative",
    }
    in_bhava_bal = False
    for line in lines:
        if "BHAVABALA" in line:
            in_bhava_bal = True
        if in_bhava_bal:
            for label, key in bhava_map.items():
                if label in line:
                    nums = re.findall(r"-?\d+\.\d+", line)
                    if nums and len(nums) >= 12:
                        bhava_bal[key] = [float(x) for x in nums[:12]]
                    elif nums and label in ("TOTAL", "Rel."):
                        bhava_bal[key] = [float(x) for x in nums[:12]]
                    break
    data["bhava_bala"] = bhava_bal

    # ── Mutual Disposition ──
    data["mutual_rasi"], _ = _parse_mutual(lines, "RASI chart")
    data["mutual_navamsa"], _ = _parse_mutual(lines, "NAVAMSA chart")

    return data


def _parse_bhava_beg_mid(lines):
    """Two-pass parser for BEG/MID bhava lines in HOR.OUT."""
    beg, mid = [], []
    state = None  # "beg1","beg2","mid1","mid2"
    for line in lines:
        # BEG first row
        m = re.search(r"BEG\s*:\s*1 TO 6\s+([\d\s-]+)", line)
        if m:
            beg.extend(_extract_6dm(m.group(1)))
            state = "beg2"
            continue
        # BEG second row
        if state == "beg2" and re.search(r"7 TO 12", line):
            nums_part = re.sub(r"7 TO 12", "", line)
            beg.extend(_extract_6dm(nums_part))
            state = None
            continue
        # MID first row
        m = re.search(r"MID\s*:\s*1 TO 6\s+([\d\s-]+)", line)
        if m:
            mid.extend(_extract_6dm(m.group(1)))
            state = "mid2"
            continue
        # MID second row
        if state == "mid2" and re.search(r"7 TO 12", line):
            nums_part = re.sub(r"7 TO 12", "", line)
            mid.extend(_extract_6dm(nums_part))
            state = None
            continue
    return beg, mid


def _extract_6dm(text):
    """Extract up to 6 deg-min values from a string like '45-15  73-29  100- 0 ...'"""
    pairs = re.findall(r"(\d+)-\s*(\d+)", text)
    return [int(d) + int(m) / 60.0 for d, m in pairs[:6]]


def _parse_mutual(lines, section_marker):
    """Parse a 9x9 mutual disposition table."""
    matrix = []
    in_section = False
    header_seen = False
    for line in lines:
        if section_marker in line:
            in_section = True
            header_seen = False
            matrix = []
            continue
        if not in_section:
            continue
        # Header row (Sun Moon Mars ...)
        if re.search(r"Sun\s+Moon\s+Mars", line):
            header_seen = True
            continue
        if not header_seen:
            continue
        # Data rows: "    Sun     Sama   Sama   ..."
        m = re.match(
            r"\s+(\w+)\s+((?:(?:Sama|Mitra|Satru|A\.Mit|A\.Sat)\s*){2,})", line
        )
        if m:
            vals = re.findall(r"A\.Mit|A\.Sat|Sama|Mitra|Satru", line)
            matrix.append(vals[:9])
        # Stop after 9 rows
        if len(matrix) == 9:
            in_section = False
    return matrix, None


# ── Python Output Parser (astro.py stdout) ─────────────────────────────────────


def parse_py_output(text):
    """Parse astro.py stdout into the same structured dict."""
    data = {
        "name": "",
        "calendar": {},
        "planets": {},
        "bhava_beg": [],
        "bhava_mid": [],
        "shadbala": {},
        "bhava_bala": {},
        "mutual_rasi": [],
        "mutual_navamsa": [],
    }

    lines = text.splitlines()

    # ── Name ──
    for line in lines:
        m = re.search(r"Name\s*:\s*(.+)", line)
        if m:
            data["name"] = m.group(1).strip()
            break

    # ── Calendar ──
    cal = {}
    for line in lines:
        m = re.search(r"Paksham\s*:\s*(.+)", line)
        if m:
            cal["paksham"] = m.group(1).strip()
        m = re.search(r"Thithi\s*:\s*(.+)", line)
        if m:
            cal["thithi"] = m.group(1).strip()
        m = re.search(r"Yogam\s*:\s*(.+)", line)
        if m:
            cal["yogam"] = m.group(1).strip()
        m = re.search(r"Karanam\s*:\s*(.+)", line)
        if m:
            cal["karanam"] = m.group(1).strip()
        m = re.search(r"Tamil Date\s*:\s*(\d+)\s+(\w+)\s+(\w+)", line)
        if m:
            cal["tamil_date"] = f"{m.group(1)} {m.group(2)} {m.group(3)}"
        m = re.search(r"Saka Date\s*:\s*(.+)", line)
        if m:
            cal["saka_date"] = m.group(1).strip()
        m = re.search(r"Kali Year\s*:\s*(\d+)", line)
        if m:
            cal["kali_year"] = int(m.group(1))
        m = re.search(r"Sunrise\s*:\s*(\d+):(\d+)", line)
        if m:
            cal["sunrise"] = f"{m.group(1)}:{m.group(2)}"
        m = re.search(r"Sunset\s*:\s*(\d+):(\d+)", line)
        if m:
            cal["sunset"] = f"{m.group(1)}:{m.group(2)}"
        m = re.search(r"Weekday\s*:\s*(\w+)", line)
        if m:
            cal["weekday"] = m.group(1).strip()
    data["calendar"] = cal

    # ── Nirayana Longitudes ──
    # Python format:  LAGN       18-22      Rohini          3     Rishabha      Mithuna
    planet_pat = re.compile(
        r"^\s*(LAGN|SUN|MOON|MARS|MERC|JUPT|VENU|SATN|URAN|NEPT|RAHU|KETU)\s+"
        r"(\d+)-(\d+)\s+"  # deg-min within sign
        r"(\w+)\s+"  # nakshatra
        r"(\d+)\s+"  # pada
        r"(\w+)\s+"  # rasi name
        r"(\w+)"  # navamsa rasi name
    )
    for line in lines:
        m = planet_pat.match(line)
        if m:
            name = m.group(1)
            deg_in = int(m.group(2))
            min_in = int(m.group(3))
            naks = m.group(4)
            pada = int(m.group(5))
            rasi = m.group(6)
            nav_rasi = m.group(7)
            rasi_idx = RASI_TO_IDX.get(rasi, 0)
            long_abs = rasi_idx * 30.0 + deg_in + min_in / 60.0
            nav_num = RASI_TO_IDX.get(nav_rasi, 0)  # 0-11
            data["planets"][name] = {
                "long_abs": long_abs,
                "nakshatra": naks,
                "pada": pada,
                "navamsa_num": nav_num,
            }

    # ── Bhava Cusps ──
    # Python: "  House  1:   18-22  Rishabha"
    # Python doesn't output BEG separately — house cusps are the MID (Lagna = house 1 midpoint)  # noqa: E501
    # The Python astro.py prints house cusps as midpoints (lagna = ascendant degree)
    beg = []
    for line in lines:
        m = re.match(r"\s*House\s+(\d+):\s+(\d+)-(\d+)\s+(\w+)", line)
        if m:
            deg_in = int(m.group(2))
            min_in = int(m.group(3))
            rasi = m.group(4)
            rasi_idx = RASI_TO_IDX.get(rasi, 0)
            long_abs = rasi_idx * 30.0 + deg_in + min_in / 60.0
            beg.append(long_abs)
    data["bhava_beg"] = beg  # Python outputs house cusps (= C's MID row)
    data["bhava_mid"] = beg  # treat same for now

    # ── Shadbala ──
    shad = {}
    shad_map = {
        "Sthana Bala": "sthana",
        "Kala Bala": "kala",
        "Dig Bala": "dig",
        "Naisargika": "naisa",
        "Chesta Bala": "chesta",
        "Drik Bala (+)": "ben_drig",
        "Drik Bala (-)": "mal_drig",
        "TOTAL": "total",
        "Relative": "relative",
        "Ishta Bala": "ishta",
        "Kashta Bala": "kashta",
        "Ishta-Kashta": "net",
    }
    in_shad = False
    for line in lines:
        if "SHADBALA" in line:
            in_shad = True
        if "BHAVA BALA" in line:
            in_shad = False
        if not in_shad:
            continue
        for label, key in shad_map.items():
            if label in line:
                nums = re.findall(r"-?\d+\.\d+", line)
                if nums:
                    shad[key] = [float(x) for x in nums[:7]]
                break
    data["shadbala"] = shad

    # ── Bhava Bala ──
    bhava_bal = {}
    py_bhava_map = {
        "Swami Bala": "swami",
        "Dig Bala": "dig",
        "Drig Bala": "drig",
        "Spl Drig": "spl",
        "Occ Str": "occ",
        "Total": "total",
        "Relative": "relative",
    }
    in_bhava_bal = False
    for line in lines:
        if "BHAVA BALA" in line:
            in_bhava_bal = True
        if "MUTUAL DISPOSITION" in line:
            in_bhava_bal = False
        if not in_bhava_bal:
            continue
        for label, key in py_bhava_map.items():
            if label in line:
                nums = re.findall(r"-?\d+\.\d+", line)
                if nums and len(nums) >= 12:
                    bhava_bal[key] = [float(x) for x in nums[:12]]
                break
    data["bhava_bala"] = bhava_bal

    # ── Mutual Disposition ──
    data["mutual_rasi"], _ = _parse_py_mutual(lines, "MUTUAL DISPOSITION (RASI)")
    data["mutual_navamsa"], _ = _parse_py_mutual(lines, "MUTUAL DISPOSITION (NAVAMSA)")

    return data


def _parse_py_mutual(lines, section_marker):
    """Parse 9x9 mutual disposition table from Python output."""
    matrix = []
    in_section = False
    header_seen = False
    for line in lines:
        if section_marker in line:
            in_section = True
            header_seen = False
            matrix = []
            continue
        if not in_section:
            continue
        if re.search(r"Sun\s+Moon\s+Mars", line):
            header_seen = True
            continue
        if not header_seen:
            continue
        vals = re.findall(r"A\.Mit|A\.Sat|Sama|Mitra|Satru", line)
        if vals:
            matrix.append(vals[:9])
        if len(matrix) == 9:
            in_section = False
    return matrix, None


# ── Run programs ───────────────────────────────────────────────────────────────


def run_python(input_file):
    """Run astro.py with the given input file and return stdout."""
    astro_py = os.path.join(WORKTREE, "astro.py")
    with open(input_file, "r") as f:
        result = subprocess.run(
            [sys.executable, astro_py],
            stdin=f,
            capture_output=True,
            text=True,
            cwd=WORKTREE,
        )
    if result.returncode != 0:
        print(f"[ERROR] astro.py failed:\n{result.stderr}", file=sys.stderr)
    return result.stdout


def run_c(input_file, horos_exe=None):
    """
    Copy input_file → bin/data.txt, run horos.exe, return content of bin/HOR.OUT.
    Returns None if horos.exe not found.
    """
    if horos_exe is None:
        horos_exe = HOROS_EXE
    horos_exe = os.path.abspath(horos_exe)
    if not os.path.isfile(horos_exe):
        print(f"[ERROR] horos.exe not found at: {horos_exe}", file=sys.stderr)
        return None
    bin_dir = os.path.dirname(horos_exe)
    data_dest = os.path.join(bin_dir, "data.txt")
    hor_out = os.path.join(bin_dir, "HOR.OUT")

    shutil.copy(input_file, data_dest)
    subprocess.run([horos_exe], cwd=bin_dir, capture_output=True, text=True)
    if not os.path.isfile(hor_out):
        print("[ERROR] HOR.OUT not generated.", file=sys.stderr)
        return None
    with open(hor_out, "r", encoding="latin-1") as f:
        return f.read()


# ── Comparison ─────────────────────────────────────────────────────────────────


def compare(c_data, py_data, section=None, verbose=False):
    """Compare two parsed data dicts. Returns a list of result rows."""
    rows = []

    if section in (None, "calendar"):
        rows += _cmp_calendar(c_data["calendar"], py_data["calendar"], verbose)

    if section in (None, "planets"):
        rows += _cmp_planets(c_data["planets"], py_data["planets"], verbose)

    if section in (None, "bhava-cusps"):
        rows += _cmp_bhava_cusps(c_data, py_data, verbose)

    if section in (None, "shadbala"):
        rows += _cmp_shadbala(c_data["shadbala"], py_data["shadbala"], verbose)

    if section in (None, "bhava-bala"):
        rows += _cmp_bhava_bala(c_data["bhava_bala"], py_data["bhava_bala"], verbose)

    if section in (None, "mutual-disp"):
        rows += _cmp_mutual(
            c_data["mutual_rasi"], py_data["mutual_rasi"], "RASI", verbose
        )
        rows += _cmp_mutual(
            c_data["mutual_navamsa"], py_data["mutual_navamsa"], "NAVAMSA", verbose
        )

    return rows


def _cmp_calendar(c_cal, py_cal, verbose):
    rows = [("SECTION", "CALENDAR", "", "", "", "")]
    fields = [
        ("paksham", "Paksham"),
        ("thithi", "Thithi"),
        ("yogam", "Yogam"),
        ("karanam", "Karanam"),
        ("tamil_date", "Tamil Date"),
        ("saka_date", "Saka Date"),
        ("kali_year", "Kali Year"),
        ("weekday", "Weekday"),
        ("sunrise", "Sunrise"),
        ("sunset", "Sunset"),
    ]
    for key, label in fields:
        cv = str(c_cal.get(key, "—"))
        pv = str(py_cal.get(key, "—"))
        # Normalize HH:MM times — strip leading zeros so "5:38" == "05:38"
        if key in ("sunrise", "sunset"):
            cv_n = ":".join(p.lstrip("0") or "0" for p in cv.split(":"))
            pv_n = ":".join(p.lstrip("0") or "0" for p in pv.split(":"))
            st = _str_status(cv_n, pv_n)
        else:
            st = _str_status(cv, pv)
        if verbose or st != "PASS":
            rows.append(("DATA", label, cv, pv, "", st))
    return rows


def _cmp_planets(c_planets, py_planets, verbose):
    rows = [("SECTION", "NIRAYANA LONGITUDES (absolute degrees)", "", "", "", "")]
    rows.append(
        ("HEADER", "Planet", "C abs°", "Py abs°", "Δ°", "C Naksh / Py Naksh / Status")
    )
    for name in PLANET_ORDER:
        cp = c_planets.get(name, {})
        pp = py_planets.get(name, {})
        if not cp and not pp:
            continue
        c_abs = cp.get("long_abs", float("nan"))
        p_abs = pp.get("long_abs", float("nan"))
        delta = abs(c_abs - p_abs) if (cp and pp) else float("nan")
        # Handle wrap-around (e.g., 359° vs 1°)
        if delta > 180:
            delta = 360 - delta
        st = _deg_status(delta) if not (delta != delta) else "—"
        c_naks = cp.get("nakshatra", "—")
        p_naks = pp.get("nakshatra", "—")
        c_nav = cp.get("navamsa_num", "—")
        p_nav = pp.get("navamsa_num", "—")
        c_pada = cp.get("pada", "—")
        p_pada = pp.get("pada", "—")
        detail = f"{c_naks}/{p_naks}  Pada:{c_pada}/{p_pada}  Nav:{c_nav}/{p_nav}"
        if verbose or st not in ("PASS",):
            rows.append(
                (
                    "DATA",
                    name,
                    f"{c_abs:.3f}" if cp else "—",
                    f"{p_abs:.3f}" if pp else "—",
                    f"{delta:.3f}" if not (delta != delta) else "—",
                    f"{st}  {detail}",
                )
            )
    return rows


def _cmp_bhava_cusps(c_data, py_data, verbose):
    rows = [
        ("SECTION", "BHAVA CUSPS (house midpoint absolute degrees)", "", "", "", "")
    ]
    rows.append(("HEADER", "House", "C MID°", "Py Cusp°", "Δ°", "Status"))
    c_mid = c_data.get("bhava_mid", [])
    py_beg = py_data.get("bhava_beg", [])
    for i in range(min(len(c_mid), len(py_beg), 12)):
        c_v = c_mid[i]
        p_v = py_beg[i]
        delta = abs(c_v - p_v)
        if delta > 180:
            delta = 360 - delta
        st = _deg_status(delta)
        if verbose or st != "PASS":
            rows.append(
                ("DATA", str(i + 1), f"{c_v:.3f}", f"{p_v:.3f}", f"{delta:.3f}", st)
            )
    return rows


def _cmp_shadbala(c_shad, py_shad, verbose):
    rows = [
        (
            "SECTION",
            "SHADBALA (7 planets: Sun Moon Mars Merc Jupt Venus Saturn)",
            "",
            "",
            "",
            "",
        )
    ]
    components = [
        ("sthana", "Sthana Bala"),
        ("kala", "Kala Bala"),
        ("dig", "Dig Bala"),
        ("naisa", "Naisargika"),
        ("chesta", "Chesta Bala"),
        ("ben_drig", "Drik Bala (+)"),
        ("mal_drig", "Drik Bala (-)"),
        ("total", "TOTAL"),
        ("relative", "Relative"),
        ("ishta", "Ishta Bala"),
        ("kashta", "Kashta Bala"),
        ("net", "Net (I-K)"),
    ]
    for key, label in components:
        cv = c_shad.get(key, [])
        pv = py_shad.get(key, [])
        if not cv and not pv:
            continue
        rows.append(("SUBHEAD", label, "", "", "", ""))
        for i, pname in enumerate(SHAD_PLANETS):
            c_v = cv[i] if i < len(cv) else float("nan")
            p_v = pv[i] if i < len(pv) else float("nan")
            delta = abs(c_v - p_v) if not (c_v != c_v or p_v != p_v) else float("nan")
            st = _bal_status(delta) if not (delta != delta) else "—"
            if verbose or st not in ("PASS",):
                rows.append(
                    (
                        "DATA",
                        f"  {pname}",
                        f"{c_v:.4f}" if not (c_v != c_v) else "—",
                        f"{p_v:.4f}" if not (p_v != p_v) else "—",
                        f"{delta:.4f}" if not (delta != delta) else "—",
                        st,
                    )
                )
    return rows


def _cmp_bhava_bala(c_bb, py_bb, verbose):
    rows = [("SECTION", "BHAVA BALA (12 houses)", "", "", "", "")]
    components = [
        ("swami", "Swami Bala"),
        ("dig", "Dig Bala"),
        ("drig", "Drig Bala"),
        ("spl", "Spl Drig"),
        ("occ", "Occ Str"),
        ("total", "TOTAL"),
        ("relative", "Relative"),
    ]
    for key, label in components:
        cv = c_bb.get(key, [])
        pv = py_bb.get(key, [])
        if not cv and not pv:
            continue
        rows.append(("SUBHEAD", label, "", "", "", ""))
        for i in range(min(len(cv), len(pv), 12)):
            c_v = cv[i]
            p_v = pv[i]
            delta = abs(c_v - p_v)
            st = _bal_status(delta)
            if verbose or st != "PASS":
                rows.append(
                    (
                        "DATA",
                        f"  H{i+1}",
                        f"{c_v:.4f}",
                        f"{p_v:.4f}",
                        f"{delta:.4f}",
                        st,
                    )
                )
    return rows


def _cmp_mutual(c_mat, py_mat, label, verbose):
    rows = [("SECTION", f"MUTUAL DISPOSITION — {label} (9×9)", "", "", "", "")]
    if not c_mat or not py_mat:
        rows.append(("DATA", "—", "no data", "no data", "", "—"))
        return rows
    for i in range(min(len(c_mat), len(py_mat), 9)):
        cr = c_mat[i]
        pr = py_mat[i]
        planet = MUTUAL_PLANETS[i] if i < len(MUTUAL_PLANETS) else f"P{i}"
        for j in range(min(len(cr), len(pr), 9)):
            cv = cr[j]
            pv = pr[j]
            st = _str_status(cv, pv)
            target = MUTUAL_PLANETS[j] if j < len(MUTUAL_PLANETS) else f"P{j}"
            if verbose or st != "PASS":
                rows.append(("DATA", f"  {planet}→{target}", cv, pv, "", st))
    return rows


# ── Report Printer ─────────────────────────────────────────────────────────────


def print_report(rows, name=""):
    WIDTH = 76
    print()
    print("=" * WIDTH)
    print(f"  Bhagyagraha: Python vs C Comparison{f'  —  {name}' if name else ''}")
    print("=" * WIDTH)

    pass_count = warn_count = fail_count = 0

    for row in rows:
        kind = row[0]
        if kind == "SECTION":
            print()
            print(f"  -- {row[1]}")
            print(
                f"  {'Field':<22} {'C value':<20} {'Python value':<20} {'Delta':<8} {'Status'}"  # noqa: E501
            )
            print(f"  {'-'*22} {'-'*20} {'-'*20} {'-'*8} {'-'*10}")
        elif kind == "SUBHEAD":
            print(f"\n  {row[1]}")
        elif kind == "HEADER":
            print(f"  {row[1]:<22} {row[2]:<20} {row[3]:<20} {row[4]:<8} {row[5]}")
        elif kind == "DATA":
            _, field, cv, pv, delta, status = row
            st_word = status.split()[0] if status else ""
            indicator = (
                " <--" if st_word == "FAIL" else ("  ?" if st_word == "WARN" else "")
            )
            if st_word == "PASS":
                pass_count += 1
            elif st_word == "WARN":
                warn_count += 1
            elif st_word == "FAIL":
                fail_count += 1
            print(f"  {field:<22} {cv:<20} {pv:<20} {delta:<8} {status}{indicator}")

    print()
    print("=" * WIDTH)
    total = pass_count + warn_count + fail_count
    print(
        f"  Summary: {pass_count} PASS  |  {warn_count} WARN  |  {fail_count} FAIL  "
        f"  (of {total} checked fields)"
    )
    print("=" * WIDTH)
    print()


# ── CLI ────────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Bhagyagraha: compare Python vs C horoscope output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input", metavar="FILE", help="Birth data input file (default: data.txt)"
    )
    parser.add_argument(
        "--c-ref",
        metavar="FILE",
        help="Existing C output file (HOR.OUT) to use as reference",
    )
    parser.add_argument(
        "--horos",
        metavar="EXE",
        help="Path to horos.exe (runs it live to generate C output)",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show all fields, not just mismatches"
    )
    parser.add_argument(
        "--section",
        metavar="SEC",
        choices=[
            "calendar",
            "planets",
            "bhava-cusps",
            "shadbala",
            "bhava-bala",
            "mutual-disp",
        ],
        help="Show only one section",
    )
    parser.add_argument(
        "--all-tests",
        action="store_true",
        help="Run all test cases in tests/ directory",
    )
    args = parser.parse_args()

    if args.all_tests:
        _run_all_tests(args)
        return

    input_file = args.input or os.path.join(WORKTREE, "data.txt")
    if not os.path.isfile(input_file):
        print(f"[ERROR] Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    # Get C output
    if args.c_ref:
        ref_path = args.c_ref
        with open(ref_path, "r", encoding="latin-1") as f:
            c_text = f.read()
    elif args.horos:
        c_text = run_c(input_file, args.horos)
        if c_text is None:
            sys.exit(1)
    else:
        # Default: look for tests/name/expected.out
        default_ref = os.path.join(TESTS_DIR, "name", "expected.out")
        if os.path.isfile(default_ref):
            print(f"[INFO] Using default reference: {default_ref}")
            with open(default_ref, "r", encoding="latin-1") as f:
                c_text = f.read()
        else:
            print(
                "[ERROR] Provide --c-ref or --horos.  "
                "Example:\n  python compare.py --input data.txt "
                "--c-ref tests/name/expected.out",
                file=sys.stderr,
            )
            sys.exit(1)

    # Get Python output
    py_text = run_python(input_file)

    # Parse
    c_data = parse_c_output(c_text)
    py_data = parse_py_output(py_text)

    # Compare & report
    rows = compare(c_data, py_data, section=args.section, verbose=args.verbose)
    print_report(rows, name=c_data.get("name", ""))


def _run_all_tests(args):
    if not os.path.isdir(TESTS_DIR):
        print(f"[ERROR] tests/ directory not found: {TESTS_DIR}", file=sys.stderr)
        sys.exit(1)

    for case_dir in sorted(os.listdir(TESTS_DIR)):
        case_path = os.path.join(TESTS_DIR, case_dir)
        if not os.path.isdir(case_path):
            continue
        input_file = os.path.join(case_path, "input.txt")
        expected_out = os.path.join(case_path, "expected.out")

        if not os.path.isfile(input_file):
            print(f"[SKIP] {case_dir}: no input.txt")
            continue

        print(f"\n{'='*60}")
        print(f"  Test case: {case_dir}")
        print(f"{'='*60}")

        if args.horos:
            c_text = run_c(input_file, args.horos)
        elif os.path.isfile(expected_out):
            with open(expected_out, "r", encoding="latin-1") as f:
                c_text = f.read()
        else:
            print(f"[SKIP] {case_dir}: no expected.out and no --horos provided")
            continue

        py_text = run_python(input_file)
        c_data = parse_c_output(c_text)
        py_data = parse_py_output(py_text)
        rows = compare(c_data, py_data, section=args.section, verbose=args.verbose)
        print_report(rows, name=c_data.get("name", case_dir))


if __name__ == "__main__":
    main()
