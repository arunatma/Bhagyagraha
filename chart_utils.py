"""
chart_utils.py — South Indian chart generation and planet-placement helpers.

Used by both the Streamlit UI (HTML charts) and the PDF report (ReportLab tables).
"""

from collections import defaultdict

from constants import GRAHA_DISPLAY

# South Indian chart: fixed grid positions -> sign index (0-11)
SOUTH_INDIAN_GRID = {
    (0, 0): 11, (0, 1): 0,  (0, 2): 1,  (0, 3): 2,
    (1, 0): 10,                          (1, 3): 3,
    (2, 0): 9,                           (2, 3): 4,
    (3, 0): 8,  (3, 1): 7,  (3, 2): 6,  (3, 3): 5,
}
SIGN_TO_CELL = {v: k for k, v in SOUTH_INDIAN_GRID.items()}


# ── Planet placement helpers ─────────────────────────────────────────────────


def _graha_label(i, planet_retrograde):
    """Return display name; append (R) if retrograde."""
    label = GRAHA_DISPLAY[i]
    if planet_retrograde and planet_retrograde[i]:
        label += "(R)"
    return label


def planets_by_sign(planet_degs, planet_retrograde=None):
    """Map sign index -> list of planet abbreviations (for Rasi chart)."""
    by_sign = defaultdict(list)
    for i, degs in enumerate(planet_degs):
        sign = int(degs // 30)
        label = _graha_label(i, planet_retrograde) if planet_retrograde else GRAHA_DISPLAY[i]
        by_sign[sign].append(label)
    return dict(by_sign)


def planets_by_navamsa(navamsa_positions, planet_retrograde=None):
    """Map navamsa sign index -> list of planet abbreviations."""
    by_sign = defaultdict(list)
    for i, sign in enumerate(navamsa_positions):
        label = _graha_label(i, planet_retrograde) if planet_retrograde else GRAHA_DISPLAY[i]
        by_sign[int(sign)].append(label)
    return dict(by_sign)


def planets_by_bhava(bhava_positions, planet_retrograde=None):
    """Map sign index -> planet list for the Bhava (house) chart."""
    by_sign = defaultdict(list)
    for i, sign in enumerate(bhava_positions):
        label = _graha_label(i, planet_retrograde) if planet_retrograde else GRAHA_DISPLAY[i]
        by_sign[int(sign)].append(label)
    return dict(by_sign)


# ── HTML chart ───────────────────────────────────────────────────────────────


def south_indian_chart_html(by_sign, label, cell_size=90, border_color="#444"):
    """Build a complete South Indian chart as an HTML table string."""
    cell_s = (
        f"width:{cell_size}px;height:{cell_size}px;"
        f"vertical-align:top;padding:4px;font-size:11px;"
        f"border:1px solid {border_color};"
    )

    def cell(sign):
        planets_here = "<br>".join(by_sign.get(sign, []))
        return f'<td style="{cell_s}">{planets_here}</td>'

    centre_td = (
        f'<th align="center" rowspan="2" colspan="2" '
        f'style="width:{cell_size * 2}px;height:{cell_size * 2}px;'
        f'border:1px solid {border_color};font-size:15px;">'
        f"{label}</th>"
    )

    row0 = f"<tr>{cell(11)}{cell(0)}{cell(1)}{cell(2)}</tr>"
    row1 = f"<tr>{cell(10)}{centre_td}{cell(3)}</tr>"
    row2 = f"<tr>{cell(9)}{cell(4)}</tr>"
    row3 = f"<tr>{cell(8)}{cell(7)}{cell(6)}{cell(5)}</tr>"

    table_style = (
        f"border-collapse:collapse;border:2px solid {border_color};"
        f"width:{cell_size * 4 + 10}px;"
    )
    return f'<table style="{table_style}">{row0}{row1}{row2}{row3}</table>'


# ── ReportLab (PDF) chart ────────────────────────────────────────────────────


def pdf_si_chart(by_sign, label, cell_w=50, cell_h=36):
    """Build a 4x4 South Indian chart as a ReportLab Table."""
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle

    def cell(s):
        return "\n".join(by_sign.get(s, []))

    data = [
        [cell(11), cell(0), cell(1), cell(2)],
        [cell(10), label, "", cell(3)],
        [cell(9), "", "", cell(4)],
        [cell(8), cell(7), cell(6), cell(5)],
    ]
    t = Table(data, colWidths=[cell_w] * 4, rowHeights=[cell_h] * 4)
    t.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("SPAN", (1, 1), (2, 2)),
            ("ALIGN", (1, 1), (2, 2), "CENTER"),
            ("VALIGN", (1, 1), (2, 2), "MIDDLE"),
            ("FONTNAME", (1, 1), (2, 2), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("LEADING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )
    return t


def pdf_ashta_chart(vals, label, cell_w=42, cell_h=28):
    """Small 4x4 chart showing integer Ashtavarga values per sign."""
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle

    data = [
        [str(vals[11]), str(vals[0]), str(vals[1]), str(vals[2])],
        [str(vals[10]), label, "", str(vals[3])],
        [str(vals[9]), "", "", str(vals[4])],
        [str(vals[8]), str(vals[7]), str(vals[6]), str(vals[5])],
    ]
    t = Table(data, colWidths=[cell_w] * 4, rowHeights=[cell_h] * 4)
    t.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("SPAN", (1, 1), (2, 2)),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (1, 1), (2, 2), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ])
    )
    return t
