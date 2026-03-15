"""
pdf_report.py — Multi-page PDF report generation for Bhagyagraha.

Uses ReportLab to produce a downloadable PDF matching the HOR.OUT structure.
"""

import shadbala as sb
from chart_utils import (
    pdf_ashta_chart,
    pdf_si_chart,
    planets_by_bhava,
    planets_by_navamsa,
    planets_by_sign,
)
from constants import GRAHA_NAMES, NAKSHATRA, RASI_NAMES, SHAD_LABELS


def _nakshatra_pada(degs):
    nak = min(int(degs / (360.0 / 27)), 26)
    rem = degs - nak * (360.0 / 27)
    pada = int(rem / (360.0 / 108)) + 1
    return nak, pada


def _ramc_hms(r):
    h = int(r / 15)
    m = int((r / 15 - h) * 60)
    s = int(((r / 15 - h) * 60 - m) * 60)
    return f"{h}H-{m:02d}M-{s:02d}S"


def _section_title(text, styles):
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph

    style = ParagraphStyle(
        "sect", parent=styles["Heading2"], textColor=colors.darkred, spaceAfter=3
    )
    return Paragraph(text, style)


def _std_table_style():
    from reportlab.lib import colors
    from reportlab.platypus import TableStyle

    return TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1),
         [colors.white, colors.Color(0.96, 0.96, 0.96)]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ])


# ── Page builders ────────────────────────────────────────────────────────────


def _p1(story, result, styles, mm):
    """Page 1: Birth data, Panchangam, Astronomical."""
    from reportlab.lib import colors
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

    inp = result["input"]
    cal = result["calendar"]
    in_dt = inp["in_datetime"]
    lat_d = int(inp["lat_degs"])
    lat_m = int((inp["lat_degs"] - lat_d) * 60)
    lon_d = int(inp["long_degs"])
    lon_m = int((inp["long_degs"] - lon_d) * 60)

    story.append(Paragraph("B H A G Y A G R A H A", styles["Heading1"]))
    story.append(Spacer(1, 4 * mm))

    ts = _std_table_style()
    birth_data = [
        ["Name", inp["name"]],
        ["Date of Birth",
         f"{in_dt.day:02d}/{in_dt.month:02d}/{in_dt.year}  ({cal['weekday']})"],
        ["Time of Birth",
         f"{in_dt.hour:02d}H-{in_dt.minute:02d}M  (Local Standard Time)"],
        ["Place of Birth", inp["birthplace"]],
        ["Latitude", f"{lat_d}-{lat_m:02d} ({inp['lat_dirn']})"],
        ["Longitude", f"{lon_d}-{lon_m:02d} ({inp['long_dirn']})"],
        ["Sun Rise", cal["sunrise"].strftime("%H:%M")],
        ["Sun Set", cal["sunset"].strftime("%H:%M")],
    ]
    t = Table(birth_data, colWidths=[55 * mm, 120 * mm])
    t.setStyle(ts)
    story.append(t)
    story.append(Spacer(1, 5 * mm))

    story.append(_section_title("Panchangam", styles))
    pan_data = [
        ["Paksham", cal["paksham"], "Thithi", cal["thithi"]],
        ["Yogam", cal["yogam"], "Karanam", cal["karanam"]],
        ["Tamil Date",
         f"{cal['tamil_day']} {cal['tamil_month']} {cal['tamil_year']}",
         "Saka Date",
         f"{cal['saka_day']} {cal['saka_month']} {cal['saka_year']}"],
        ["Kali Year", str(cal["kali_year"]), "Weekday", cal["weekday"]],
        ["Nakshatra",
         f"{cal['janma_nakshatra']} Pada-{cal['janma_pada']}",
         "Dasa Balance",
         f"{cal['dasa_lord']}  Y:{cal['dasa_y']} M:{cal['dasa_m']} D:{cal['dasa_d']}"],
    ]
    ts2 = TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1),
         [colors.white, colors.Color(0.96, 0.96, 0.96)]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ])
    t2 = Table(pan_data, colWidths=[36 * mm, 56 * mm, 36 * mm, 56 * mm])
    t2.setStyle(ts2)
    story.append(t2)
    story.append(Spacer(1, 5 * mm))

    story.append(_section_title("Astronomical Data", styles))
    ast_data = [
        ["Sidereal Time (RAMC)", _ramc_hms(result.get("sidereal_time", 0.0))],
        ["Ayanamsa", f"{result.get('ayanamsa', 0.0):.4f}\u00b0"],
    ]
    t3 = Table(ast_data, colWidths=[70 * mm, 105 * mm])
    t3.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t3)


def _p2(story, result, styles, mm):
    """Page 2: Nirayana Longitudes + RASI + NAVAMSA + Dasa balance."""
    from reportlab.lib import colors
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

    pd_ = result["planet_degs"]
    nav = result["navamsa_positions"]
    retro = result.get("planet_retrograde", [False] * 12)
    cal = result["calendar"]

    story.append(_section_title("Nirayana Longitudes", styles))

    long_data = [["Graha", "Longitude", "Rasi", "Nakshatra", "Pada", "Navamsa"]]
    for i, nm in enumerate(GRAHA_NAMES):
        degs = pd_[i]
        sign = int(degs // 30)
        d = int(degs)
        m = int((degs - d) * 60)
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
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.Color(0.96, 0.96, 0.96)]),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),
    ])
    t = Table(long_data,
              colWidths=[22 * mm, 22 * mm, 28 * mm, 36 * mm, 14 * mm, 28 * mm])
    t.setStyle(ts)
    story.append(t)
    story.append(Spacer(1, 6 * mm))

    _cw = 62
    rasi_t = pdf_si_chart(planets_by_sign(pd_, retro), "RASI", cell_w=_cw, cell_h=34)
    nav_t = pdf_si_chart(planets_by_navamsa(nav, retro), "NAVAMSA", cell_w=_cw, cell_h=34)
    outer = Table([[rasi_t, "", nav_t]], colWidths=[_cw * 4, 6, _cw * 4])
    outer.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(outer)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph(
        f"<b>Dasa Balance at Birth:</b>  "
        f"{cal['dasa_lord']} — "
        f"Y: {cal['dasa_y']}  M: {cal['dasa_m']}  D: {cal['dasa_d']}",
        styles["Normal"],
    ))


def _p3(story, result, styles, mm):
    """Page 3: Bhava table + BHAVA chart + Dasa/Bukti table."""
    from reportlab.lib import colors
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

    house = result["house_positions"]
    retro = result.get("planet_retrograde", [False] * 12)
    cal = result["calendar"]

    story.append(_section_title("Bhava Cusps", styles))
    bhava_data = [["Bhava", "Longitude", "Rasi"]]
    for i in range(12):
        degs = house[i]
        sign = int(degs // 30)
        d = int(degs)
        m = int((degs - d) * 60)
        bhava_data.append([str(i + 1), f"{d}\u00b0-{m:02d}\u2032", RASI_NAMES[sign]])
    ts = TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.Color(0.96, 0.96, 0.96)]),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),
    ])
    t = Table(bhava_data, colWidths=[20 * mm, 28 * mm, 32 * mm])
    t.setStyle(ts)

    _cw_b = 70
    bhava_chart = pdf_si_chart(
        planets_by_bhava(result["bhava_positions"], retro),
        "BHAVA", cell_w=_cw_b, cell_h=34,
    )
    outer = Table([[t, "", bhava_chart]], colWidths=[int(80 * mm), 6, _cw_b * 4])
    outer.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(outer)
    story.append(Spacer(1, 6 * mm))

    story.append(_section_title("Vimsottari Dasa/Bukti Table", styles))
    dasa_table = cal.get("dasa_table", [])
    for drow in dasa_table:
        story.append(Paragraph(f"<b>{drow['dasa']} Dasa</b>", styles["Normal"]))
        bdata = [[b[0], b[1]] for b in drow["buktis"]]
        rows = []
        for idx in range(0, 9, 3):
            row = []
            for jj in range(3):
                if idx + jj < len(bdata):
                    row.extend(bdata[idx + jj])
                else:
                    row.extend(["", ""])
            rows.append(row)
        bt = Table(rows,
                   colWidths=[28 * mm, 24 * mm, 28 * mm, 24 * mm, 28 * mm, 24 * mm])
        bt.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.2, colors.grey),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ]))
        story.append(bt)
        story.append(Spacer(1, 2 * mm))


def _p4(story, result, styles, mm):
    """Page 4: Mutual Disposition (Rasi + Navamsa)."""
    from reportlab.lib import colors
    from reportlab.platypus import Spacer, Table, TableStyle

    mut = result["mutual"]
    pnames = mut["planet_names"]

    def _mat_table(matrix, pnames_):
        header = [""] + pnames_
        rows = [header]
        for i, row in enumerate(matrix):
            rows.append([pnames_[i]] + list(row))
        ts = TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ])
        cw = [18 * mm] + [16 * mm] * len(pnames_)
        t = Table(rows, colWidths=cw)
        t.setStyle(ts)
        return t

    story.append(_section_title("Mutual Disposition \u2014 Rasi", styles))
    story.append(_mat_table(mut["rasi"], pnames))
    story.append(Spacer(1, 8 * mm))
    story.append(_section_title("Mutual Disposition \u2014 Navamsa", styles))
    story.append(_mat_table(mut["navamsa"], pnames))


def _ashta_section(ashta_dict, styles, mm):
    """Return flowables for one planet's Ashtavarga section."""
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

    name = ashta_dict["name"]
    raw = ashta_dict["raw"]
    thri = ashta_dict["thri"]
    eka = ashta_dict["eka"]
    contribs = ashta_dict["contributors"]
    sp = ashta_dict["sodhya_pinda"]

    flowables = []
    flowables.append(_section_title(f"{name} Ashtavarga  (Total={sum(raw)})", styles))

    main_by = {}
    for s in range(12):
        abbrs = " ".join(contribs[s])
        main_by[s] = [f"{abbrs}", f"{raw[s]}"] if abbrs else [f"{raw[s]}"]

    def cell_main(s):
        return "\n".join(main_by.get(s, []))

    main_data = [
        [cell_main(11), cell_main(0), cell_main(1), cell_main(2)],
        [cell_main(10), f"{name}\nMain\n{sum(raw)}", "", cell_main(3)],
        [cell_main(9), "", "", cell_main(4)],
        [cell_main(8), cell_main(7), cell_main(6), cell_main(5)],
    ]
    from reportlab.lib import colors

    mt = Table(main_data, colWidths=[44 * mm] * 4, rowHeights=[32 * mm] * 4)
    mt.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("SPAN", (1, 1), (2, 2)),
        ("ALIGN", (1, 1), (2, 2), "CENTER"),
        ("VALIGN", (1, 1), (2, 2), "MIDDLE"),
        ("FONTNAME", (1, 1), (2, 2), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("LEADING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    flowables.append(mt)

    _cw2 = 62
    thri_t = pdf_ashta_chart(thri, "Thri", cell_w=_cw2, cell_h=22)
    eka_t = pdf_ashta_chart(eka, "Eka", cell_w=_cw2, cell_h=22)
    side2 = Table([[thri_t, "", eka_t]], colWidths=[_cw2 * 4, 6, _cw2 * 4])
    side2.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    flowables.append(side2)
    flowables.append(Paragraph(f"Sodhya Pinda: <b>{sp}</b>", styles["Normal"]))
    flowables.append(Spacer(1, 5 * mm))
    return flowables


def _p8(story, result, styles, mm):
    """Page 8: Drig Bala 7x7 matrix + Benefic/Malefic."""
    from reportlab.lib import colors
    from reportlab.platypus import Spacer, Table, TableStyle

    shad = result["shad"]
    p7_degs = [result["planet_degs"][i] for i in [1, 2, 3, 4, 5, 6, 7]]
    pl7 = SHAD_LABELS

    story.append(_section_title("Drig Bala \u2014 Pairwise Aspect Strengths", styles))

    try:
        drig_mat = sb.drig_bala_matrix(p7_degs)
    except Exception:
        drig_mat = [[0.0] * 7 for _ in range(7)]

    header = [""] + pl7
    rows = [header]
    for i, row in enumerate(drig_mat):
        rows.append([pl7[i]] + [f"{v:.2f}" for v in row])
    ts = TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ])
    cw = [22 * mm] + [23 * mm] * 7
    t = Table(rows, colWidths=cw)
    t.setStyle(ts)
    story.append(t)
    story.append(Spacer(1, 8 * mm))

    story.append(_section_title("Benefic / Malefic Drig Bala", styles))
    bd = shad.get("ben_drig", [0] * 7)
    md = shad.get("mal_drig", [0] * 7)
    bm_data = [
        [""] + pl7,
        ["Ben(+)"] + [f"{v:.2f}" for v in bd],
        ["Mal(-)"] + [f"{v:.2f}" for v in md],
    ]
    bmt = Table(bm_data, colWidths=[22 * mm] + [23 * mm] * 7)
    bmt.setStyle(ts)
    story.append(bmt)


def _p9(story, result, styles, mm):
    """Page 9: Shadbala + Bhava Bala."""
    from reportlab.lib import colors
    from reportlab.platypus import Spacer, Table, TableStyle

    shad = result["shad"]
    bb = result["bhava_bala"]
    pl7 = SHAD_LABELS

    story.append(_section_title("Shadbala \u2014 Planetary Strength", styles))
    shad_components = [
        ("Sthana Bala", "sthana"), ("Kala Bala", "kala"),
        ("Dig Bala", "dig"), ("Naisargika", "naisa"),
        ("Chesta Bala", "chesta"), ("Drik (+)", "ben_drig"),
        ("Drik (-)", "mal_drig"), ("TOTAL", "total"),
        ("Min Req", "min_required"), ("Relative", "relative"),
        ("Ishta", "ishta"), ("Kashta", "kashta"),
    ]
    shad_rows = [["Bala"] + pl7]
    for label, key in shad_components:
        shad_rows.append([label] + [f"{v:.2f}" for v in shad[key]])

    ts = TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.Color(0.96, 0.96, 0.96)]),
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),
        ("BACKGROUND", (0, 8), (-1, 8), colors.Color(0.80, 0.90, 0.80)),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ])
    t = Table(shad_rows, colWidths=[30 * mm] + [22 * mm] * 7)
    t.setStyle(ts)
    story.append(t)
    story.append(Spacer(1, 8 * mm))

    story.append(_section_title("Bhava Bala \u2014 House Strength", styles))
    bb_components = [
        ("Swami Bala", "swami"), ("Dig Bala", "dig"),
        ("Drig Bala", "drig"), ("Spl Drig", "spl_drig"),
        ("Occ Str", "ostr"), ("TOTAL", "total"),
        ("Relative", "relative"),
    ]
    hdr = ["Bala"] + [f"H{h + 1}" for h in range(12)]
    bb_rows = [hdr]
    for label, key in bb_components:
        bb_rows.append([label] + [f"{v:.2f}" for v in bb[key]])

    ts2 = TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.Color(0.96, 0.96, 0.96)]),
        ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ])
    t2 = Table(bb_rows, colWidths=[22 * mm] + [13 * mm] * 12)
    t2.setStyle(ts2)
    story.append(t2)


# ── Public API ───────────────────────────────────────────────────────────────


def generate_pdf(result):
    """Generate a multi-page PDF horoscope. Returns raw PDF bytes."""
    try:
        from io import BytesIO

        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import KeepTogether, PageBreak, SimpleDocTemplate
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
    styles["Heading1"].fontSize = 16
    styles["Heading1"].spaceAfter = 6

    story = []

    _p1(story, result, styles, mm)
    story.append(PageBreak())
    _p2(story, result, styles, mm)
    story.append(PageBreak())
    _p3(story, result, styles, mm)
    story.append(PageBreak())
    _p4(story, result, styles, mm)

    if result.get("ashtavarga"):
        ashta = result["ashtavarga"]
        story.append(PageBreak())
        for p in ashta.get("planets", []):
            story.append(KeepTogether(_ashta_section(p, styles, mm)))
        sarva = ashta.get("sarva")
        if sarva:
            story.append(KeepTogether(_ashta_section(sarva, styles, mm)))

    story.append(PageBreak())
    _p8(story, result, styles, mm)
    story.append(PageBreak())
    _p9(story, result, styles, mm)

    doc.build(story)
    return buf.getvalue()
