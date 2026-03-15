"""
html_report.py — Single-page HTML report generation for Bhagyagraha.

Generates a compact, self-contained HTML page with birth data, three
South Indian charts (Rasi, Navamsa, Bhava), and a longitude table.
All colors are driven by the theme dict passed in.
"""

from chart_utils import planets_by_bhava, planets_by_navamsa, planets_by_sign, south_indian_chart_html
from constants import GRAHA_NAMES, NAKSHATRA
from themes import get_theme


def _nakshatra_pada(degs):
    nak = min(int(degs / (360.0 / 27)), 26)
    rem = degs - nak * (360.0 / 27)
    pada = int(rem / (360.0 / 108)) + 1
    return nak, pada


def generate_single_page_html(result, theme_name="Teal & Charcoal"):
    """Compact single-page HTML: birth data + 3 charts + longitude table."""
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
    chart_w = cell_size * 4 + 10

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

    long_rows = ""
    for i, nm in enumerate(GRAHA_NAMES):
        degs = pd[i]
        d = int(degs)
        m = int((degs - d) * 60)
        nak, pada = _nakshatra_pada(degs)
        r_mark = f"&nbsp;<b style='color:{t['retro_color']}'>(R)</b>" if retro[i] else ""
        long_rows += (
            f"<tr>"
            f"<td style='padding:2px 6px;border-bottom:1px solid {t['table_border']}'>"
            f"<b>{nm}</b>{r_mark}</td>"
            f"<td align='right' style='padding:2px 4px;border-bottom:1px solid {t['table_border']}'>"
            f"{d}&deg;</td>"
            f"<td align='right' style='padding:2px 4px;border-bottom:1px solid {t['table_border']}'>"
            f"{m}&prime;</td>"
            f"<td style='padding:2px 6px;border-bottom:1px solid {t['table_border']}'>"
            f"{NAKSHATRA[nak]}</td>"
            f"<td align='center' style='padding:2px 4px;border-bottom:1px solid {t['table_border']}'>"
            f"{pada}</td>"
            f"</tr>\n"
        )

    td_hdr = (
        f"padding:4px 6px;background:{t['table_header_bg']};"
        f"border-bottom:2px solid {t['accent']};font-size:11px;color:{t['body_text']};"
    )
    td_key = (
        f"padding:4px 8px;font-weight:600;color:{t['body_text']};"
        f"white-space:nowrap;font-size:12px;"
    )
    td_val = f"padding:4px 8px;color:{t['body_text']};font-size:12px;"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; background:{t["body_bg"]}; margin:16px; color:{t["body_text"]}; }}
  h1   {{ text-align:center; color:{t["accent"]}; letter-spacing:5px; font-size:20px;
          border-bottom:2px solid {t["accent"]}; padding-bottom:6px; margin-bottom:12px; }}
  table {{ border-collapse:collapse; }}
</style>
</head>
<body>
<h1>B H A G Y A G R A H A</h1>

<table width="100%" style="margin-bottom:14px;">
<tr valign="top">
  <td>
    <table>
      <tr><td style="{td_key}">Name</td><td style="{td_val}">{name}</td></tr>
      <tr><td style="{td_key}">Date of Birth</td>
          <td style="{td_val}">{in_dt.day:02d}/{in_dt.month:02d}/{in_dt.year} &mdash; {cal["weekday"]}</td></tr>
      <tr><td style="{td_key}">Time of Birth</td>
          <td style="{td_val}">{in_dt.hour}H-{in_dt.minute:02d}M (Local Std Time)</td></tr>
      <tr><td style="{td_key}">Place of Birth</td><td style="{td_val}">{birthplace}</td></tr>
      <tr><td style="{td_key}">Lat-Long</td>
          <td style="{td_val}">{lat_d}&deg;-{lat_m:02d}&prime;({lat_dir})&nbsp;
              {lon_d}&deg;-{lon_m:02d}&prime;({lon_dir})</td></tr>
      <tr><td style="{td_key}">Janma Nakshatra</td>
          <td style="{td_val}">{cal["janma_nakshatra"]} Pada-{cal["janma_pada"]}</td></tr>
      <tr><td style="{td_key}">Paksham</td><td style="{td_val}">{cal["paksham"]}</td></tr>
      <tr><td style="{td_key}">Balance of {cal["dasa_lord"]} dasa</td>
          <td style="{td_val}">Y:&nbsp;{cal["dasa_y"]}&nbsp; M:&nbsp;{cal["dasa_m"]}&nbsp; D:&nbsp;{cal["dasa_d"]}</td></tr>
    </table>
  </td>
  <td>
    <table>
      <tr><td style="{td_key}">Thithi</td><td style="{td_val}">{cal["thithi"]}</td></tr>
      <tr><td style="{td_key}">Yogam</td><td style="{td_val}">{cal["yogam"]}</td></tr>
      <tr><td style="{td_key}">Karanam</td><td style="{td_val}">{cal["karanam"]}</td></tr>
      <tr><td style="{td_key}">Tamil Date</td>
          <td style="{td_val}">{cal["tamil_day"]} {cal["tamil_month"]} {cal["tamil_year"]}</td></tr>
      <tr><td style="{td_key}">Saka Date</td>
          <td style="{td_val}">{cal["saka_day"]} {cal["saka_month"]} {cal["saka_year"]}</td></tr>
      <tr><td style="{td_key}">Kali Year</td><td style="{td_val}">{cal["kali_year"]}</td></tr>
      <tr><td style="{td_key}">Sun Rise</td>
          <td style="{td_val}">{sunrise.strftime("%H:%M")} (Local Mean Time)</td></tr>
      <tr><td style="{td_key}">Sun Set</td>
          <td style="{td_val}">{sunset.strftime("%H:%M")} (Local Mean Time)</td></tr>
    </table>
  </td>
</tr>
</table>

<table>
<tr valign="top">
  <td align="left" width="{chart_w}" height="{chart_w}" style="padding-right:12px;">{rasi_chart}</td>
  <td align="left" width="{chart_w}" height="{chart_w}">{nav_chart}</td>
</tr>
<tr valign="top">
  <td align="left" width="{chart_w}" style="padding-right:12px;padding-top:10px;">{bhava_chart}</td>
  <td valign="top" style="padding-top:10px;">
    <table style="border-collapse:collapse;">
      <tr>
        <th style="{td_hdr}"></th>
        <th style="{td_hdr}" colspan="2">Longitude</th>
        <th style="{td_hdr}">Nakshatra</th>
        <th style="{td_hdr}">Pada</th>
      </tr>
      {long_rows}
    </table>
  </td>
</tr>
</table>

</body>
</html>"""
