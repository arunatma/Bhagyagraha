"""
html_report.py — Single-page HTML report generation for Bhagyagraha.

Generates a compact, self-contained HTML page with birth data, three
South Indian charts (Rasi, Navamsa, Bhava), and a longitude table.
All colors are driven by the theme dict passed in.
"""

from chart_utils import planets_by_bhava, planets_by_navamsa, planets_by_sign, south_indian_chart_html
from constants import GRAHA_NAMES, NAKSHATRA
from themes import get_theme
import time

def _nakshatra_pada(degs):
    nak = min(int(degs / (360.0 / 27)), 26)
    rem = degs - nak * (360.0 / 27)
    pada = int(rem / (360.0 / 108)) + 1
    return nak, pada


def generate_single_page_html(result, theme_name="Teal & Charcoal"):
    """Compact single-page HTML for embedding in Streamlit via st.components.v1.html()"""
    cache_bust = int(time.time() * 1000)  # fresh on every call so iframe re-renders
    t = get_theme(theme_name)
    inp = result["input"]
    cal = result["calendar"]
    pd = result["planet_degs"]
    nav = result["navamsa_positions"]

    name = inp["name"]
    birthplace = inp["birthplace"]
    in_dt = inp["in_datetime"]
    lat_d = int(inp["lat_degs"])
    lat_m = int((inp["lat_degs"] - lat_d) * 60)
    lon_d = int(inp["long_degs"])
    lon_m = int((inp["long_degs"] - lon_d) * 60)
    lat_dir = inp["lat_dirn"]
    lon_dir = inp["long_dirn"]
    sunrise = cal["sunrise"]
    sunset = cal["sunset"]

    retro = result.get("planet_retrograde", [False] * 12)
    cell_size = 75
    chart_w = cell_size * 4  # 300px

    rasi_chart = south_indian_chart_html(
        planets_by_sign(pd, retro), "RASI",
        cell_size=cell_size, border_color=t["chart_border"],
    )
    nav_chart = south_indian_chart_html(
        planets_by_navamsa(nav, retro), "NAVAMSA",
        cell_size=cell_size, border_color=t["chart_border"],
    )
    bhava_chart = south_indian_chart_html(
        planets_by_bhava(result["bhava_positions"], retro), "BHAVA",
        cell_size=cell_size, border_color=t["chart_border"],
    )

    # Longitude table rows: separate columns for name | (R) | degrees | minutes | nakshatra | pada
    td_b = f"padding:2px 4px;border-bottom:1px solid {t['table_border']};"
    long_rows = ""
    for i, nm in enumerate(GRAHA_NAMES):
        degs = pd[i]
        d = int(degs)
        m = int((degs - d) * 60)
        nak, pada = _nakshatra_pada(degs)
        r_mark = "(R)" if retro[i] else ""
        long_rows += (
            f"<tr>"
            f"<td style='{td_b}padding-left:6px;'><b>{nm}</b></td>"
            f"<td style='{td_b}color:{t['retro_color']};font-size:10px;width:22px;'>{r_mark}</td>"
            f"<td align='right' style='{td_b}width:30px;'>{d}&deg;</td>"
            f"<td align='right' style='{td_b}width:30px;padding-right:6px;'>{m:02d}&prime;</td>"
            f"<td style='{td_b}padding-left:6px;'>{NAKSHATRA[nak]}</td>"
            f"<td align='center' style='{td_b}padding-right:6px;width:28px;'>{pada}</td>"
            f"</tr>\n"
        )

    # All styles inline — no CSS classes — so theme changes always take effect
    td_hdr = (
        f"padding:4px 6px;background:{t['table_header_bg']};"
        f"border-bottom:2px solid {t['accent']};font-size:11px;"
        f"color:{t['body_text']};text-align:left;white-space:nowrap;"
    )
    td_key = (
        f"padding:3px 8px;font-weight:600;color:{t['body_text']};"
        f"white-space:nowrap;font-size:12px;width:150px;vertical-align:top;"
    )
    td_val = (
        f"padding:3px 8px;color:{t['body_text']};font-size:12px;"
        f"width:190px;vertical-align:top;"
    )

    # Birth info panels — fully inline styled
    birth_left = f"""
    <table style="border-collapse:collapse;">
      <tr><td style="{td_key}">Name</td>
          <td style="{td_val}">{name}</td></tr>
      <tr><td style="{td_key}">Date of Birth</td>
          <td style="{td_val}">{in_dt.day:02d}/{in_dt.month:02d}/{in_dt.year} &mdash; {cal["weekday"]}</td></tr>
      <tr><td style="{td_key}">Time of Birth</td>
          <td style="{td_val}">{in_dt.hour}H-{in_dt.minute:02d}M (Local Std Time)</td></tr>
      <tr><td style="{td_key}">Place of Birth</td>
          <td style="{td_val}">{birthplace}</td></tr>
      <tr><td style="{td_key}">Lat / Long</td>
          <td style="{td_val}">{lat_d}&deg;&nbsp;{lat_m:02d}&prime;&nbsp;({lat_dir})&nbsp;&nbsp;{lon_d}&deg;&nbsp;{lon_m:02d}&prime;&nbsp;({lon_dir})</td></tr>
      <tr><td style="{td_key}">Janma Nakshatra</td>
          <td style="{td_val}">{cal["janma_nakshatra"]} Pada-{cal["janma_pada"]}</td></tr>
      <tr><td style="{td_key}">Paksham</td>
          <td style="{td_val}">{cal["paksham"]}</td></tr>
      <tr><td style="{td_key}">Balance of {cal["dasa_lord"]} dasa</td>
          <td style="{td_val}">Y:&nbsp;{cal["dasa_y"]}&nbsp; M:&nbsp;{cal["dasa_m"]}&nbsp; D:&nbsp;{cal["dasa_d"]}</td></tr>
    </table>"""

    birth_right = f"""
    <table style="border-collapse:collapse;">
      <tr><td style="{td_key}">Thithi</td>
          <td style="{td_val}">{cal["thithi"]}</td></tr>
      <tr><td style="{td_key}">Yogam</td>
          <td style="{td_val}">{cal["yogam"]}</td></tr>
      <tr><td style="{td_key}">Karanam</td>
          <td style="{td_val}">{cal["karanam"]}</td></tr>
      <tr><td style="{td_key}">Tamil Date</td>
          <td style="{td_val}">{cal["tamil_day"]} {cal["tamil_month"]} {cal["tamil_year"]}</td></tr>
      <tr><td style="{td_key}">Saka Date</td>
          <td style="{td_val}">{cal["saka_day"]} {cal["saka_month"]} {cal["saka_year"]}</td></tr>
      <tr><td style="{td_key}">Kali Year</td>
          <td style="{td_val}">{cal["kali_year"]}</td></tr>
      <tr><td style="{td_key}">Sun Rise (Center)</td>
          <td style="{td_val}">{sunrise.hour}H-{sunrise.minute:02d}M (Local Mean Time)</td></tr>
      <tr><td style="{td_key}">Sun Set (Center)</td>
          <td style="{td_val}">{sunset.hour}H-{sunset.minute:02d}M (Local Mean Time)</td></tr>
    </table>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: Arial, sans-serif;
    background: transparent;
    color: {t["body_text"]};
    padding: 8px;
    max-width: 780px;
    margin: 0 auto;
  }}
  table {{ border-collapse: collapse; }}
</style>
</head>
<body>
<span style="display:none;">{cache_bust}</span>
<!-- Title: fully inline so accent color always reflects current theme -->
<h2 style="text-align:center;color:{t['accent']};letter-spacing:4px;font-size:16px;
           border-bottom:2px solid {t['accent']};padding-bottom:4px;margin-bottom:10px;">
  B H A G Y A G R A H A
</h2>

<!-- Birth details: two fixed-width panels, divider inline styled -->
<div style="display:flex;flex-direction:row;gap:0px;margin-bottom:12px;
            padding-bottom:10px;border-bottom:1px solid {t['table_border']};">
  <div style="flex:0 0 340px;">{birth_left}</div>
  <div style="flex:0 0 340px;">{birth_right}</div>
</div>

<!-- Row 1: Rasi | Navamsa -->
<div style="display:flex;flex-direction:row;align-items:flex-start;
            gap:20px;margin-bottom:14px;">
  <div style="flex:0 0 {chart_w}px;">{rasi_chart}</div>
  <div style="flex:0 0 {chart_w}px;">{nav_chart}</div>
</div>

<!-- Row 2: Bhava | Longitude table -->
<div style="display:flex;flex-direction:row;align-items:flex-start;gap:20px;">
  <div style="flex:0 0 {chart_w}px;">{bhava_chart}</div>
  <div style="flex:0 0 auto;">
    <table style="border-collapse:collapse;font-size:12px;color:{t['body_text']};">
      <thead>
        <tr>
          <th style="{td_hdr}padding-left:6px;">Graha</th>
          <th style="{td_hdr}width:22px;"></th>
          <th colspan="2" style="{td_hdr}text-align:center;">Longitude</th>
          <th style="{td_hdr}padding-left:6px;">Nakshatra</th>
          <th style="{td_hdr}text-align:center;width:28px;">Pada</th>
        </tr>
      </thead>
      <tbody>
        {long_rows}
      </tbody>
    </table>
  </div>
</div>

</body>
</html>"""