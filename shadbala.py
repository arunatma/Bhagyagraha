"""
shadbala.py — Planetary and House strength calculations.
Converted from SHAD.C (original C code by Dr R Natarajan).

Planet order throughout (index 0-6): Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn.

Interface:
    compute_shadbala(planets, house_data, birth_data) -> dict
    compute_bhava_bala(shadbala_totals, house_data)   -> dict
    compute_mutual_disp(planets)                       -> dict
"""

import math


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _deg_diff(a, b):
    """(a - b) % 360, always positive."""
    return (a - b) % 360.0


def _temp_stat(k):
    """Temporary disposition based on sign distance k (1-12).
    Returns +1 (friendly), -1 (enemy), or 0 (neutral).
    Matches C TempStat().
    """
    if k in (2, 3, 4, 10, 11, 12):
        return 1
    if k in (1, 5, 6, 7, 8, 9):
        return -1
    return 0


def _sign_dist(sign_a, sign_b):
    """Distance in signs from sign_a to sign_b, 1-indexed (1-12).
    Matches C's (P.sign <= Planets[j][0].sign) ? ... pattern.
    """
    if sign_a <= sign_b:
        return sign_b - sign_a + 1
    return (12 - sign_a) + sign_b + 1


# ---------------------------------------------------------------------------
# 1. Uchcha Bala (Exaltation Strength)
# ---------------------------------------------------------------------------

def uchcha_bala(p_degs):
    """Exaltation strength for 7 planets. Returns list of 7 floats (0-1).
    Debilitation points (degrees 0-359):
      Sun=190, Moon=213, Mars=118, Mercury=345, Jupiter=275, Venus=177, Saturn=20
    """
    debi = [190, 213, 118, 345, 275, 177, 20]
    result = []
    for i in range(7):
        diff = _deg_diff(p_degs[i], debi[i])
        if diff > 180:
            diff = 360.0 - diff
        result.append(diff / 180.0)
    return result


# ---------------------------------------------------------------------------
# 2. Saptha Vargaja Bala (Seven-chart dignity strength)
# ---------------------------------------------------------------------------

def saptha_vargaja_bala(p_signs, p_degs_in_sign, p_mins_in_sign, navamsa_signs):
    """Seven-varga dignity strength. Returns list of 7 floats.

    p_signs         : list of 12 sign indices (0-11), index 0=Lagna, 1=Sun, …
    p_degs_in_sign  : list of 12 degree-within-sign values
    p_mins_in_sign  : list of 12 minute-within-sign values
    navamsa_signs   : list of 12 navamsa sign indices (0-11), same planet order
    """
    # Natural disposition matrix: NatDisp[i][j] — i vs j (0-indexed planets)
    nat_disp = [
        [ 0, 1, 1, 0, 1,-1,-1],  # Sun
        [ 1, 0, 0, 1, 0, 0, 0],  # Moon
        [ 1, 1, 0,-1, 1, 0, 0],  # Mars
        [ 1,-1, 0, 0, 0, 1, 0],  # Mercury
        [ 1, 1, 1,-1, 0,-1, 0],  # Jupiter
        [-1,-1, 0, 1, 0, 0, 1],  # Venus
        [-1,-1,-1, 1, 0, 1, 0],  # Saturn
    ]

    # Moola Trikona: (sign, from_deg, to_deg) for each planet 0-6
    moola = [
        (4,  0, 20),   # Sun: Leo 0-20
        (1,  3, 30),   # Moon: Taurus 3-30
        (0,  0, 12),   # Mars: Aries 0-12
        (5, 15, 20),   # Mercury: Virgo 15-20
        (8,  0, 10),   # Jupiter: Sagittarius 0-10
        (6,  0, 15),   # Venus: Libra 0-15
        (10, 0, 20),   # Saturn: Aquarius 0-20
    ]

    # Own signs: (primary_sign, from_deg, to_deg, alt_sign) for each planet 0-6
    # The planet is in own sign if in primary_sign with deg in [from,to) OR in alt_sign
    own = [
        (4, 20, 30, 100),  # Sun: Leo 20-30 (no alt)
        (3,  0, 30, 100),  # Moon: Cancer (no alt)
        (0, 12, 30,   7),  # Mars: Aries 12-30 or Scorpio
        (5, 20, 30,   2),  # Mercury: Virgo 20-30 or Gemini
        (8, 20, 30,  11),  # Jupiter: Sagittarius 20-30 or Pisces
        (6, 15, 30,   1),  # Venus: Libra 15-30 or Taurus
        (10,20, 30,   9),  # Saturn: Aquarius 20-30 or Capricorn
    ]

    marks  = [0.75, 0.50, 0.375, 0.25, 0.125, 0.0625, 0.03125]
    order  = [2, 1, 0, -1, -2]

    # Trimsamsam spans and rulers: (span_degrees, planet_index_1based)
    # For odd signs (C sign%2==0 means odd in 0-indexed)
    thrim = [(5, 3), (5, 7), (8, 5), (7, 4), (5, 6)]

    def find_owner(sign):
        """Return 0-based planet index of the owner of `sign` (0-11)."""
        for jj in range(7):
            if sign == own[jj][0] or sign == own[jj][3]:
                return jj
        return 0  # fallback

    def disp_index_for_sign(planet_i, sign_k):
        """Compute varga marks index for planet_i (0-6) occupying sign_k (0-11).
        Returns index into marks[] array.
        """
        # Own or exalted first
        if own[planet_i][0] == sign_k or own[planet_i][3] == sign_k:
            return 1
        owner = find_owner(sign_k)
        dist = _sign_dist(p_signs[planet_i + 1], p_signs[owner + 1])
        k = _temp_stat(dist) + nat_disp[planet_i][owner]
        for idx in range(5):
            if order[idx] == k:
                return idx + 2
        return 4  # worst if not found

    saptha = []
    for i in range(7):
        s   = p_signs[i + 1]       # geocentric sign of planet i (1-indexed in p_signs)
        d   = p_degs_in_sign[i + 1]
        m   = p_mins_in_sign[i + 1]
        total = 0.0

        # — Rasi (natal sign) —
        mo = moola[i]
        if s == mo[0] and d >= mo[1] and d < mo[2]:
            index = 0   # Moola Trikona
        elif s == own[i][3] or (s == own[i][0] and d >= own[i][1] and d < own[i][2]):
            index = 1   # Own sign
        else:
            index = disp_index_for_sign(i, s)
        total += marks[index]

        # — Hora —
        if d < 15:
            j = 0 if ((s + 1) % 2 == 1) else 1   # 0=Sun, 1=Moon (0-based)
        else:
            j = 1 if ((s + 1) % 2 == 1) else 0
        owner_sign = p_signs[j + 1]
        dist = _sign_dist(s, owner_sign)
        k = _temp_stat(dist) + nat_disp[i][j]
        for idx in range(5):
            if order[idx] == k:
                index = idx + 2; break
        else:
            index = 4
        total += marks[index]

        # — Drekanam (decan) —
        k = d // 10
        k = 0 if k == 0 else (4 if k == 1 else 8)   # 0, 4, or 8 added to sign
        dreka_sign = (s + k) % 12
        if own[i][0] == dreka_sign or own[i][3] == dreka_sign:
            index = 1
        else:
            index = disp_index_for_sign(i, dreka_sign)
        total += marks[index]

        # — Saptamsam (1/7th division) —
        k = (d * 7) // 30 + 1
        if s % 2 == 0:   # C: P.sign%2==0 means 0-indexed odd sign
            sapt_sign = (s + k - 1) % 12
        else:
            sapt_sign = ((s + 6) % 12 + k - 1) % 12
        if own[i][0] == sapt_sign or own[i][3] == sapt_sign:
            index = 1
        else:
            index = disp_index_for_sign(i, sapt_sign)
        total += marks[index]

        # — Navamsam —
        nava_sign = navamsa_signs[i + 1]
        if own[i][0] == nava_sign or own[i][3] == nava_sign:
            index = 1
        else:
            index = disp_index_for_sign(i, nava_sign)
        total += marks[index]

        # — Dwadasamsam (1/12th division) —
        k = int((int(d) + m / 60.0) * 2.0 / 5.0) + 1
        dwa_sign = (s + k - 1) % 12
        if own[i][0] == dwa_sign or own[i][3] == dwa_sign:
            index = 1
        else:
            index = disp_index_for_sign(i, dwa_sign)
        total += marks[index]

        # — Trimsamsam (1/30th division) —
        k = 0
        if s % 2 == 0:   # C: P.sign%2==0 means odd signs
            j_found = -1
            for jj in range(5):
                k += thrim[jj][0]
                if k > d:
                    j_found = jj; break
            ruler = thrim[j_found][1] - 1 if j_found >= 0 else 0  # 0-based
        else:
            j_found = -1
            for jj in range(4, -1, -1):
                k += thrim[jj][0]
                if k > d:
                    j_found = jj; break
            ruler = thrim[j_found][1] - 1 if j_found >= 0 else 0

        if i == ruler:
            index = 1
        else:
            dist = _sign_dist(s, p_signs[ruler + 1])
            kk = _temp_stat(dist) + nat_disp[i][ruler]
            for idx in range(5):
                if order[idx] == kk:
                    index = idx + 2; break
            else:
                index = 4
        total += marks[index]

        saptha.append(total)

    return saptha


# ---------------------------------------------------------------------------
# 3. Oja Bala (Odd/Even sign strength)
# ---------------------------------------------------------------------------

def oja_bala(p_signs, navamsa_signs):
    """Odd/even sign strength. Returns list of 7 floats.
    gender: 0=masculine (favours odd), 1=feminine (favours even).
    Planets: Sun=0, Moon=1, Mars=0, Mercury=0, Jupiter=0, Venus=1, Saturn=0
    """
    gender = [0, 1, 0, 0, 0, 1, 0]
    result = []
    for i in range(7):
        tmp = 0.0
        if gender[i] == 0:   # masculine → odd rasi and odd navamsa are strong
            tmp  = 0.25 if (p_signs[i + 1] + 1) % 2 == 1 else 0.0
            tmp += 0.25 if navamsa_signs[i + 1] % 2 == 0 else 0.0
        else:                 # feminine → even rasi and even navamsa are strong
            tmp  = 0.25 if (p_signs[i + 1] + 1) % 2 == 0 else 0.0
            tmp += 0.25 if navamsa_signs[i + 1] % 2 == 1 else 0.0
        result.append(tmp)
    return result


# ---------------------------------------------------------------------------
# 4. Kendra Di Bala (Angular/Succedent/Cadent strength)
# ---------------------------------------------------------------------------

def kendra_di_bala(p_degs, bhava1, bhava2):
    """Angle/succedent/cadent house strength. Returns list of 7 floats."""
    result = []
    for i in range(7):
        pos = p_degs[i]
        house = -1
        for j in range(12):
            h1, h2 = bhava1[j], bhava2[j]
            if h2 < h1:
                if (pos >= h1 and pos < 360.0) or (pos >= 0.0 and pos < h2):
                    house = j; break
            else:
                if pos >= h1 and pos < h2:
                    house = j; break
        if house == -1:
            house = 0
        bhava_num = (house % 12) + 1   # 1-indexed
        if bhava_num in (1, 4, 7, 10):
            result.append(1.0)
        elif bhava_num in (2, 5, 8, 11):
            result.append(0.5)
        else:
            result.append(0.25)
    return result


# ---------------------------------------------------------------------------
# 5. Drekana Bala (Decan strength)
# ---------------------------------------------------------------------------

def drekana_bala(p_degs_in_sign):
    """Decan strength. Returns list of 7 floats.
    gender: 0=masculine (1st decan strong), 1=feminine (3rd decan strong),
            2=neuter (2nd decan strong).
    """
    gender = [0, 1, 0, 2, 0, 1, 2]
    result = []
    for i in range(7):
        d = p_degs_in_sign[i + 1]
        decan = d // 10   # 0, 1, or 2
        if gender[i] == 0:
            result.append(0.25 if decan == 0 else 0.0)
        elif gender[i] == 1:
            result.append(0.25 if decan == 2 else 0.0)
        else:
            result.append(0.25 if decan == 1 else 0.0)
    return result


# ---------------------------------------------------------------------------
# 6. Paksha Bala (Lunar phase strength)
# ---------------------------------------------------------------------------

def paksha_bala(moon_degs, sun_degs):
    """Lunar phase strength. Returns list of 7 floats.
    Bright planets (Moon, Mercury, Jupiter, Venus) are strong in Shukla paksha.
    Dark planets (Sun, Mars, Saturn) are strong in Krishna paksha.
    """
    diff = _deg_diff(moon_degs, sun_degs)
    tmp = (360.0 - diff) / 180.0 if diff > 180 else diff / 180.0
    # tmp=1 at full moon, 0 at new moon
    return [
        1.0 - tmp,   # Sun: strong in Krishna
        tmp,         # Moon: strong in Shukla
        1.0 - tmp,   # Mars: strong in Krishna
        tmp,         # Mercury: strong in Shukla
        tmp,         # Jupiter: strong in Shukla
        tmp,         # Venus: strong in Shukla
        1.0 - tmp,   # Saturn: strong in Krishna
    ]


# ---------------------------------------------------------------------------
# 7. Nathon Bala (Time-of-day strength)
# ---------------------------------------------------------------------------

def nathon_bala(local_time_hrs, sunrise_hrs, sunset_hrs):
    """Mid-day/mid-night strength. Returns list of 7 floats."""
    day_duration_hrs = sunset_hrs - sunrise_hrs
    half_day_nadi = day_duration_hrs * 2.5        # day in nadis * 2
    midnight_nadi = half_day_nadi + (60.0 - half_day_nadi) * 0.5
    midday_nadi   = midnight_nadi - 30.0

    elapsed_hrs = local_time_hrs - sunrise_hrs
    elapsed_nadi = elapsed_hrs * 2.5

    if elapsed_nadi < midday_nadi:
        tmp = (30.0 - (midday_nadi - elapsed_nadi)) / 30.0
    else:
        tmp = (30.0 - (midnight_nadi - elapsed_nadi)) / 30.0

    return [
        1.0 - tmp,   # Sun
        tmp,         # Moon
        tmp,         # Mars
        1.0,         # Mercury (always 1)
        1.0 - tmp,   # Jupiter
        1.0 - tmp,   # Venus
        tmp,         # Saturn
    ]


# ---------------------------------------------------------------------------
# 8. Dina Ratri Bala (Day/Night strength)
# ---------------------------------------------------------------------------

def dina_ratri_bala(local_time_hrs, sunrise_hrs, sunset_hrs):
    """Day/night planetary strength. Returns list of 7 floats."""
    if sunrise_hrs <= local_time_hrs < sunset_hrs:
        elapsed = local_time_hrs - sunrise_hrs
        is_day = True
    else:
        elapsed = local_time_hrs if local_time_hrs < sunrise_hrs else local_time_hrs - sunset_hrs
        is_day = False

    result = [0.0] * 7
    day_pl  = [3, 0, 6]  # 0-indexed: Mercury, Sun, Saturn → indices 3,0,6
    ngt_pl  = [1, 5, 2]  # Moon, Venus, Mars → indices 1,5,2

    if is_day:
        period_idx = min(int(elapsed / 10.0), 2)
        result[day_pl[period_idx]] = 1.0
    else:
        period_idx = min(int(elapsed / 10.0), 2)
        result[ngt_pl[period_idx]] = 1.0

    result[4] = 1.0   # Jupiter always gets 1.0
    return result


# ---------------------------------------------------------------------------
# 9. VMDH Bala (Vara/Masa/Dina/Hora strength)
# ---------------------------------------------------------------------------

def vmdh_bala(kali_dina, birth_day, local_time_hrs, sunrise_hrs):
    """Year-lord/Month-lord/Day-lord/Hour-lord strength. Returns list of 7 floats."""
    hour_ord = [1, 6, 4, 2, 7, 5, 3]  # 1-indexed planet order in hour sequence

    result = [0.0] * 7

    # Varsha (year) lord
    count = (int(kali_dina / 360) * 3 + 1) % 7
    day   = (count + 4) % 7
    result[day] += 0.25

    # Masa (month) lord
    count = (int(kali_dina / 30) * 2 + 1) % 7
    day   = (count + 4) % 7
    result[day] += 0.5

    # Dina (day of week) lord
    result[birth_day] += 0.75

    # Hora (hour) lord — find starting planet for this weekday
    count = int(local_time_hrs) + 1
    if local_time_hrs < sunrise_hrs:
        count += 24
    count -= int(sunrise_hrs)

    for i in range(7):
        if hour_ord[i] == birth_day + 1:
            break
    idx = ((count + i) % 7) - 2
    if 0 <= idx < 7:
        result[idx] = 1.0

    return result


# ---------------------------------------------------------------------------
# 10. Ayana Bala (Solstice/Declination strength)
# ---------------------------------------------------------------------------

def ayana_bala(p_degs, prec_degs):
    """Declination-based strength. Returns list of 7 floats."""
    dec_table = [
        0,
        6.0 + 4.0/60,
        11.0 + 43.0/60,
        16.0 + 42.0/60,
        20.0 + 38.0/60,
        23.0 + 8.0/60,
        24.0,
    ]
    # strong: 0=always northern, 1=northern in Uttarayana (spos<180 is bad),
    #         2=northern is good
    strong = [1, 0, 2, 0, 0, 1, 1]

    result = []
    for i in range(7):
        # Tropical longitude = geocentric + precession
        sayana_degs = (p_degs[i] + prec_degs) % 360.0
        n = int(sayana_degs / 90.0)
        pos = ((n + 1) * 90.0) - sayana_degs if n > 0 else sayana_degs

        n_idx = int(pos / 15.0)
        if n_idx >= 6:
            declination = dec_table[6]
        else:
            declination = (dec_table[n_idx]
                           + (dec_table[n_idx + 1] - dec_table[n_idx])
                           / 15.0 * (pos - n_idx * 15.0))

        st = strong[i]
        if st in (1, 3, 5, 6):
            n = -1 if sayana_degs < 180.0 else 1
        elif st in (2, 7):
            n = 1 if sayana_degs < 180.0 else -1
        else:
            n = 1

        result.append(0.5 + n * (declination / 48.0))

    return result


# ---------------------------------------------------------------------------
# 11. Dig Bala (Directional strength)
# ---------------------------------------------------------------------------

def dig_bala(p_degs, house_degs):
    """Directional strength. Returns list of 7 floats.
    Strong houses (0-indexed): Sun/Mars=3(4th), Moon/Venus=9(10th),
                                Mercury=6(7th), Jupiter=0(1st), Saturn=0→weak at 6(7th)
    """
    strong = [3, 9, 3, 6, 6, 9, 0]   # C uses house index 0-11
    result = []
    for i in range(7):
        f1 = p_degs[i]
        f2 = house_degs[strong[i]]
        diff = f1 - f2 if f1 > f2 else 360.0 + f1 - f2
        if diff > 180.0:
            diff = 360.0 - diff
        result.append(diff / 180.0)
    return result


# ---------------------------------------------------------------------------
# 12. Naisargika Bala (Natural/inherent strength)
# ---------------------------------------------------------------------------

def naisargika_bala():
    """Natural strength. Fixed values. Returns list of 7 floats."""
    ratio = [7, 6, 2, 3, 4, 5, 1]
    return [r / 7.0 for r in ratio]


# ---------------------------------------------------------------------------
# 13. Chesta Bala (Motional strength)
# ---------------------------------------------------------------------------

def chesta_bala(ayana_sun, paksha_moon, p_degs, helio_degs):
    """Motional strength. Returns list of 7 floats.
    Sun uses AyanaBala, Moon uses PakshaBala.
    Planets 2-6 (Mars-Saturn) use |geo - helio| distance.
    """
    result = [ayana_sun, paksha_moon, 0.0, 0.0, 0.0, 0.0, 0.0]
    # helio_degs: list of 5 heliocentric positions [Mars, Mercury, Jupiter, Venus, Saturn]
    for i in range(5):
        geo  = p_degs[i + 1]
        helio = helio_degs[i]
        diff  = geo - helio if geo > helio else 360.0 + geo - helio
        if diff > 180.0:
            diff = 360.0 - diff
        result[i + 2] = diff / 180.0
    return result


# ---------------------------------------------------------------------------
# 14. Drig Bala (Aspectual strength)
# ---------------------------------------------------------------------------

# Aspect strength table (0-indexed planet, distance 0-11 signs)
_ASPEX = [
    [0, 1, 3, 2, 0, 4, 3, 2, 1, 0, 0, 0],   # Sun/Moon/Mercury/Venus (pattern 0)
    [0, 1, 4, 2, 0, 4, 4, 2, 1, 0, 0, 0],   # Mars (pattern 1)
    [0, 1, 3, 4, 0, 4, 3, 4, 1, 0, 0, 0],   # Jupiter (pattern 2)
    [0, 4, 3, 2, 0, 4, 3, 2, 4, 0, 0, 0],   # Saturn (pattern 3)
]
_ASP_PTR = [0, 0, 1, 0, 2, 0, 3]   # pattern index for each planet 0-6
_BEN_PLAN = [0, 1, 0, 1, 1, 1, 0]  # 1=benefic (Moon, Mercury, Jupiter, Venus)


def _aspect_strength(aspector_idx, aspected_sign_diff_degs, aspected_pos_in_sign):
    """Compute aspect strength of planet aspector_idx casting an aspect
    across sign_diff signs with fractional position within the last sign.
    sign_diff is the HOUSE.sign of (target - aspector) in C terms (0=conjunct).
    """
    pattern = _ASP_PTR[aspector_idx]
    sign = int(sign_diff_degs // 30)
    if sign <= 0:
        return 0.0
    frac = (sign_diff_degs % 30) / 30.0
    asp = _ASPEX[pattern]
    return 0.25 * (asp[sign - 1] + (asp[sign] - asp[sign - 1]) * frac)


def drig_bala(p_degs):
    """Aspectual strength. Returns (ben_drig, mal_drig) each a list of 7 floats."""
    ben_drig = [0.0] * 7
    mal_drig = [0.0] * 7

    for i in range(7):           # aspector
        for j in range(7):       # aspected
            if i == j:
                continue
            diff_degs = _deg_diff(p_degs[j], p_degs[i])
            sign = int(diff_degs // 30)
            if sign <= 0:
                tmp = 0.0
            else:
                frac = (diff_degs % 30) / 30.0
                asp  = _ASPEX[_ASP_PTR[i]]
                tmp  = 0.25 * (asp[sign - 1] + (asp[sign] - asp[sign - 1]) * frac)

            if _BEN_PLAN[i] == 1:
                ben_drig[j] += tmp * 0.25
            else:
                mal_drig[j] += tmp * (-0.25)

    return ben_drig, mal_drig


# ---------------------------------------------------------------------------
# 15. Shadbala orchestrator
# ---------------------------------------------------------------------------

def compute_shadbala(p_degs, p_signs, p_degs_in_sign, p_mins_in_sign,
                     navamsa_signs, helio_degs_5,
                     house_degs, bhava1, bhava2,
                     local_time_hrs, sunrise_hrs, sunset_hrs,
                     kali_dina, birth_day, prec_degs):
    """
    Compute Shadbala for 7 planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn).

    Parameters
    ----------
    p_degs          : list[7]  geocentric longitudes in degrees
    p_signs         : list[12] sign (0-11) for all 12 bodies (index 0=Lagna, 1=Sun…)
    p_degs_in_sign  : list[12] degree within sign for all 12 bodies
    p_mins_in_sign  : list[12] minute within sign for all 12 bodies
    navamsa_signs   : list[12] navamsa sign (0-11) for all 12 bodies
    helio_degs_5    : list[5]  heliocentric longitudes [Mars, Mercury, Jupiter, Venus, Saturn]
    house_degs      : list[12] raw house cusp positions in degrees
    bhava1          : list[12] lower bhava boundaries in degrees
    bhava2          : list[12] upper bhava boundaries in degrees
    local_time_hrs  : float    local civil time as decimal hours
    sunrise_hrs     : float    sunrise as decimal hours
    sunset_hrs      : float    sunset as decimal hours
    kali_dina       : int      days from Kali epoch
    birth_day       : int      day of week 0=Sunday
    prec_degs       : float    precession at birth in degrees

    Returns
    -------
    dict with keys:
        "uchcha", "saptha", "oja", "kendra", "dreka"  → Sthana Bala components
        "paksha", "nathon", "dina", "vmdh", "ayana"   → Kala Bala components
        "sthana", "kala"                               → sums
        "dig", "naisa", "chesta"                       → individual
        "ben_drig", "mal_drig"                         → Drig components
        "total"                                        → grand total per planet
        "min_required"                                 → minimum required (fixed)
        "relative"                                     → total / min_required
        "ishta", "kashta"                              → derived strengths
    """
    moon_degs = p_degs[1]
    sun_degs  = p_degs[0]

    uchcha  = uchcha_bala(p_degs)
    saptha  = saptha_vargaja_bala(p_signs, p_degs_in_sign, p_mins_in_sign, navamsa_signs)
    oja     = oja_bala(p_signs, navamsa_signs)
    kendra  = kendra_di_bala(p_degs, bhava1, bhava2)
    dreka   = drekana_bala(p_degs_in_sign)
    sthana  = [uchcha[i] + saptha[i] + oja[i] + kendra[i] + dreka[i] for i in range(7)]

    paksha  = paksha_bala(moon_degs, sun_degs)
    nathon  = nathon_bala(local_time_hrs, sunrise_hrs, sunset_hrs)
    dina    = dina_ratri_bala(local_time_hrs, sunrise_hrs, sunset_hrs)
    vmdh    = vmdh_bala(kali_dina, birth_day, local_time_hrs, sunrise_hrs)
    ayana   = ayana_bala(p_degs, prec_degs)
    kala    = [paksha[i] + nathon[i] + dina[i] + vmdh[i] + ayana[i] for i in range(7)]

    dig     = dig_bala(p_degs, house_degs)
    naisa   = naisargika_bala()

    # ChestaBala: Sun uses AyanaBala[0], Moon uses PakshaBala[1]
    chesta  = chesta_bala(ayana[0], paksha[1], p_degs, helio_degs_5)

    ben_drig, mal_drig = drig_bala(p_degs)

    total   = [sthana[i] + kala[i] + dig[i] + naisa[i]
               + chesta[i] + ben_drig[i] + mal_drig[i] for i in range(7)]

    min_req = [6.5, 6.0, 5.0, 7.0, 6.5, 5.5, 5.0]
    relative = [total[i] / min_req[i] for i in range(7)]

    ishta  = [math.sqrt(uchcha[i] * chesta[i]) for i in range(7)]
    kashta = [math.sqrt((1.0 - uchcha[i]) * (1.0 - chesta[i])) for i in range(7)]

    return {
        "uchcha": uchcha,
        "saptha": saptha,
        "oja": oja,
        "kendra": kendra,
        "dreka": dreka,
        "sthana": sthana,
        "paksha": paksha,
        "nathon": nathon,
        "dina": dina,
        "vmdh": vmdh,
        "ayana": ayana,
        "kala": kala,
        "dig": dig,
        "naisa": naisa,
        "chesta": chesta,
        "ben_drig": ben_drig,
        "mal_drig": mal_drig,
        "total": total,
        "min_required": min_req,
        "relative": relative,
        "ishta": ishta,
        "kashta": kashta,
    }


# ---------------------------------------------------------------------------
# 16. Bhava Bala
# ---------------------------------------------------------------------------

def bhava_swami_bala(shad_totals, bhava1, bhava2):
    """House lord strength contribution. Returns list of 12 floats."""
    # Lord of each sign (0-indexed sign → 0-indexed planet index)
    lord = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4]
    result = []
    for i in range(12):
        h1, h2 = bhava1[i], bhava2[i]
        k = int(h1 / 30)
        if h1 == k * 30.0:
            result.append(shad_totals[lord[k]])
        else:
            h2_adj = h2 + 360.0 if abs(h1 - h2) > 90.0 else h2
            w1 = ((k + 1) * 30.0 - h1) / 30.0
            w2 = (h2_adj - (k + 1) * 30.0) / 30.0
            result.append(w1 * shad_totals[lord[k]]
                          + w2 * shad_totals[lord[(k + 1) % 12]])
    return result


def bhava_dig_bala(house_degs):
    """Directional strength for each bhava. Returns list of 12 floats."""
    weak = [9, 3, 6, 6, 0, 3, 9, 6, 9, 3, 3, 6]
    result = []
    for i in range(12):
        diff = _deg_diff(house_degs[i], house_degs[weak[i]])
        if diff > 180:
            diff = 360.0 - diff
        result.append(diff / 180.0)
    return result


def bhava_drig_bala(p_degs, house_degs):
    """Bhava aspect strength. Returns (bdrig, spl_drig) each list of 12 floats."""
    lord = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4]
    bdrig   = [0.0] * 12
    spl_drig = [0.0] * 12

    asp_per_bhava = [[0.0] * 7 for _ in range(12)]

    for i in range(12):                 # aspected bhava
        for j in range(7):             # aspecting planet (0-6)
            diff = _deg_diff(house_degs[i], p_degs[j])
            sign = int(diff // 30)
            if sign <= 0:
                tmp = 0.0
            else:
                frac = (diff % 30) / 30.0
                asp  = _ASPEX[_ASP_PTR[j]]
                tmp  = 0.25 * (asp[sign - 1] + (asp[sign] - asp[sign - 1]) * frac)
            asp_per_bhava[i][j] = tmp

        ben_asp = sum(asp_per_bhava[i][j] for j in range(7) if _BEN_PLAN[j] == 1)
        mal_asp = sum(asp_per_bhava[i][j] for j in range(7) if _BEN_PLAN[j] == 0)
        bdrig[i] = 0.25 * (ben_asp - mal_asp)

        # Special aspect: lord of bhava + Mercury + Jupiter
        k = int(house_degs[i] / 30)
        spl_drig[i] = (asp_per_bhava[i][lord[k]]
                       + asp_per_bhava[i][3]   # Mercury
                       + asp_per_bhava[i][4])  # Jupiter

    return bdrig, spl_drig


def occupational_strength(p_degs, bhava1, bhava2):
    """Occupational strength of bhavas. Returns list of 12 floats."""
    ben_plan = [-1, 1, -1, 1, 1, 1, -1]
    plpos = [0] * 7

    for i in range(7):
        pos = p_degs[i]
        for j in range(12):
            h1, h2 = bhava1[j], bhava2[j]
            if h2 < h1:
                if (pos >= h1 and pos < 360.0) or (pos >= 0.0 and pos < h2):
                    plpos[i] = j; break
            else:
                if pos >= h1 and pos < h2:
                    plpos[i] = j; break

    result = [0.0] * 12
    for i in range(12):
        for j in range(7):
            if plpos[j] == i:
                result[i] += ben_plan[j]
    return result


def compute_bhava_bala(shad_totals, p_degs, house_degs, bhava1, bhava2):
    """Compute Bhava Bala for 12 houses.

    Parameters
    ----------
    shad_totals : list[7]  total Shadbala for 7 planets
    p_degs      : list[7]  geocentric longitudes for 7 planets
    house_degs  : list[12] raw house cusp positions
    bhava1      : list[12] lower bhava boundaries
    bhava2      : list[12] upper bhava boundaries

    Returns
    -------
    dict with keys: "swami", "dig", "drig", "spl_drig", "ostr", "total", "relative"
    """
    swami    = bhava_swami_bala(shad_totals, bhava1, bhava2)
    bdig     = bhava_dig_bala(house_degs)
    bdrig, spl_drig = bhava_drig_bala(p_degs, house_degs)
    ostr     = occupational_strength(p_degs, bhava1, bhava2)
    total    = [swami[i] + bdig[i] + bdrig[i] + spl_drig[i] + ostr[i] for i in range(12)]
    relative = [t / 6.0 for t in total]
    return {
        "swami": swami,
        "dig": bdig,
        "drig": bdrig,
        "spl_drig": spl_drig,
        "ostr": ostr,
        "total": total,
        "relative": relative,
    }


# ---------------------------------------------------------------------------
# 17. Mutual Disposition
# ---------------------------------------------------------------------------

def compute_mutual_disp(p_signs, navamsa_signs):
    """Compute mutual disposition for 9 planets (Sun-Saturn + Rahu/Ketu).

    p_signs      : list[12] signs for all 12 bodies (index 0=Lagna, 1=Sun…11=Ketu)
    navamsa_signs: list[12] navamsa signs for all 12 bodies

    Returns dict with "rasi" and "navamsa" matrices (9x9 lists of disposition strings).
    """
    nat_disp = [
        [ 0, 1, 1, 0, 1,-1,-1,-1,-1],
        [ 1, 0, 0, 1, 0, 0, 0,-1,-1],
        [ 1, 1, 0,-1, 1, 0, 0,-1,-1],
        [ 1,-1, 0, 0, 0, 1, 0, 0, 0],
        [ 1, 1, 1,-1, 0,-1, 0, 0, 0],
        [-1,-1, 0, 1, 0, 0, 1, 1, 1],
        [-1,-1,-1, 1, 0, 1, 0, 1, 1],
        [-1,-1,-1, 0, 0, 1, 1, 0,-1],
        [-1,-1,-1, 0, 0, 1, 1, 0, 0],
    ]
    lord = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4]
    order  = [0, 1, -1, 2, -2]
    disp   = ["Sama ", "Mitra", "Satru", "A.Mit", "A.Sat"]

    # Planet indices in p_signs (C skips Uranus/Neptune = indices 8,9)
    # C uses i/j from 1..11 skipping 8,9 → maps to planets 1..7,10,11
    pl_idx = [1, 2, 3, 4, 5, 6, 7, 10, 11]  # indices into p_signs

    def nat_idx(p_signs_idx):
        """Map p_signs index to NatDisp row/col (0-based, 0=Sun)."""
        if p_signs_idx <= 7:
            return p_signs_idx - 1
        return p_signs_idx - 3   # 10→7, 11→8

    def mutual(sign_i, sign_j, ni, nj):
        dist = (sign_j - sign_i + 1) if sign_i <= sign_j else (12 - sign_i) + sign_j + 1
        n = nat_disp[ni][nj] + _temp_stat(dist)
        for t in range(5):
            if n == order[t]:
                return disp[t]
        return disp[0]

    def self_disp(sign_i, ni):
        owner = lord[sign_i]
        t1 = nat_disp[ni][owner]
        sign_owner = p_signs[owner + 1]
        dist = (sign_owner - sign_i + 1) if sign_i <= sign_owner else (12 - sign_i) + sign_owner + 1
        n = t1 + _temp_stat(dist)
        for t in range(5):
            if n == order[t]:
                return disp[t]
        return disp[0]

    rasi_matrix = []
    for i, pi in enumerate(pl_idx):
        row = []
        for j, pj in enumerate(pl_idx):
            ni = nat_idx(pi)
            nj = nat_idx(pj)
            if i == j:
                row.append(self_disp(p_signs[pi], ni))
            else:
                row.append(mutual(p_signs[pi], p_signs[pj], ni, nj))
        rasi_matrix.append(row)

    # Navamsa matrix
    nava_matrix = []
    for i, pi in enumerate(pl_idx):
        row = []
        for j, pj in enumerate(pl_idx):
            ni = nat_idx(pi)
            nj = nat_idx(pj)
            if i == j:
                row.append(self_disp(navamsa_signs[pi], ni))
            else:
                row.append(mutual(navamsa_signs[pi], navamsa_signs[pj], ni, nj))
        nava_matrix.append(row)

    planet_names = ["Sun", "Moon", "Mars", "Merc", "Jupt", "Venu", "Satn", "Rahu", "Ketu"]
    return {
        "planet_names": planet_names,
        "rasi": rasi_matrix,
        "navamsa": nava_matrix,
    }


# ---------------------------------------------------------------------------
# 18. Ashtavarga
# ---------------------------------------------------------------------------

# Lookup table from C SUN.C Ashtavarga() function (ash[8][7][9])
# Outer dim: source body (0=Sun,1=Moon,2=Mars,3=Mercury,4=Jupiter,5=Venus,6=Saturn,7=Lagna)
# Inner dim: target planet (0=Sun,1=Moon,2=Mars,3=Mercury,4=Jupiter,5=Venus,6=Saturn)
# Values: 1-based sign offsets from source body's position that contribute a point
_ASH = [
    # from Sun
    [[1,2,4,7,8,9,10,11],[3,6,7,8,10,11],[3,5,6,10,11],[5,6,9,11,12],
     [1,2,3,4,7,8,9,10,11],[8,11,12],[1,2,4,7,8,10,11]],
    # from Moon
    [[3,6,10,11],[1,3,6,7,10,11],[3,6,11],[2,4,6,8,10,11],
     [2,5,7,9,11],[1,2,3,4,5,8,9,11,12],[3,6,11]],
    # from Mars
    [[1,2,4,7,8,9,10,11],[2,3,5,6,9,10,11],[1,2,4,7,8,10,11],
     [1,2,4,7,8,9,10,11],[1,2,4,7,8,10,11],[3,5,6,9,11,12],[3,5,6,10,11,12]],
    # from Mercury
    [[3,5,6,9,10,11,12],[1,3,4,5,7,8,10,11],[3,5,6,11],
     [1,3,5,6,9,10,11,12],[1,2,4,5,6,9,10,11],[3,5,6,9,11],[6,8,9,10,11,12]],
    # from Jupiter
    [[5,6,9,11],[1,4,7,8,10,11,12],[6,10,11,12],[6,8,11,12],
     [1,2,3,4,7,8,10,11],[5,8,9,10,11],[5,6,11,12]],
    # from Venus
    [[6,7,12],[3,4,5,7,9,10,11],[6,8,11,12],[1,2,3,4,5,8,9,11],
     [2,5,6,9,10,11],[1,2,3,4,5,8,9,10,11],[6,11,12]],
    # from Saturn
    [[1,2,4,7,8,9,10,11],[3,5,6,11],[1,4,7,8,9,10,11],
     [1,2,4,7,8,9,10,11],[3,5,6,12],[3,4,5,8,9,10,11],[3,5,6,11]],
    # from Lagna
    [[3,4,6,10,11,12],[3,6,10,11],[1,3,6,10,11],[1,2,4,6,8,10,11],
     [1,2,4,5,6,7,9,10,11],[1,2,3,4,5,8,9,11],[1,3,4,6,10,11]],
]

# Source body: (index into planet_degs list, 2-char abbreviation)
# planet_degs indices: 0=Lagn,1=Sun,2=Moon,3=Mars,4=Merc,5=Jupt,6=Venu,7=Satn,...
_ASH_SRC = [(1,"Su"),(2,"Mo"),(3,"Ma"),(4,"Me"),(5,"Ju"),(6,"Ve"),(7,"Sa"),(0,"La")]

# From SUN.H: planet gunakaram per planet and rasi gunakaram per sign
_GRA_GUN_PRE = [0, 5, 5, 8, 5, 10, 7, 5, 0, 0, 0, 0]   # indices: Lagn,Su,Mo,Ma,Me,Ju,Ve,Sa,Ur,Ne,Ra,Ke
_RASI_GUN    = [7, 10, 8, 4, 10, 5, 7, 8, 9, 5, 11, 12]  # signs 0-11


def _thrikona(thri):
    """Apply Thrikona Sodhana in-place (SUN.C Thrikona function, lines 2929-2948)."""
    for k in range(4):
        a, b, c = thri[k], thri[k + 4], thri[k + 8]
        if (a == b == c) or (a == 0 and b == 0) or (b == 0 and c == 0):
            thri[k] = thri[k + 4] = thri[k + 8] = 0
        elif a > 0 and b > 0 and c > 0:
            n = min(a, b, c)
            thri[k] -= n
            thri[k + 4] -= n
            thri[k + 8] -= n


def _ekathipathya(eka, signs):
    """Apply Ekathipathya Sodhana in-place (SUN.C Ekathipathya, lines 2951-2991).

    signs: list[12] — current sign (0-11) for each of the 12 bodies.
    """
    hfree = [0] * 12
    for i in range(1, 8):   # Sun(1) through Saturn(7)
        hfree[signs[i]] = 1

    hrule = [(0, 7), (1, 6), (2, 5), (8, 11), (9, 10)]
    for h0, h1 in hrule:
        if eka[h0] > 0 and eka[h1] > 0:
            occ = hfree[h0] + hfree[h1]
            if occ == 0:
                if eka[h0] == eka[h1]:
                    eka[h0] = eka[h1] = 0
                else:
                    n = min(eka[h0], eka[h1])
                    eka[h0] = eka[h1] = n
            elif occ == 1:
                occupied = h0 if hfree[h0] else h1
                empty    = h1 if hfree[h0] else h0
                if eka[occupied] >= eka[empty]:
                    eka[empty] = 0
                else:
                    eka[empty] = eka[occupied]


def compute_ashtavarga(planet_degs):
    """Compute Ashtavarga for 7 classical planets + Sarvashtavarga.

    Parameters
    ----------
    planet_degs : list[12]  geocentric longitudes for
                            [Lagn,Sun,Moon,Mars,Merc,Jupt,Venu,Satn,Uran,Nept,Rahu,Ketu]

    Returns
    -------
    dict with keys:
        "planets" : list[7] — one dict per Sun/Moon/Mars/Merc/Jupt/Venu/Satn
            each dict: "name", "raw"[12], "thri"[12], "eka"[12],
                       "sodhya_pinda"(int), "contributors"[12]
        "sarva"   : same structure for Sarvashtavarga (column sums of raw)
    """
    signs = [int(d / 30) % 12 for d in planet_degs]

    # Gra-gun: gunakaram contribution per sign
    gra_gun = [0] * 12
    for i, g in enumerate(_GRA_GUN_PRE):
        if i < len(signs):
            gra_gun[signs[i]] += g

    planet_names = ["Sun", "Moon", "Mars", "Merc", "Jupt", "Venu", "Satn"]
    results = []
    sarva_raw = [0] * 12

    for p in range(7):   # target planet (0=Sun ... 6=Saturn)
        cnt = [0] * 12
        contributors = [[] for _ in range(12)]

        for k, (src_idx, abbr) in enumerate(_ASH_SRC):
            src_sign = signs[src_idx]
            for offset in _ASH[k][p]:
                t = (src_sign + offset - 1) % 12
                cnt[t] += 1
                contributors[t].append(abbr)

        thri = cnt[:]
        _thrikona(thri)
        eka = thri[:]
        _ekathipathya(eka, signs)
        sp = int(sum(eka[i] * (gra_gun[i] + _RASI_GUN[i]) for i in range(12)))

        for i in range(12):
            sarva_raw[i] += cnt[i]

        results.append({
            "name": planet_names[p],
            "raw":  cnt,
            "thri": thri,
            "eka":  eka,
            "sodhya_pinda": sp,
            "contributors": contributors,
        })

    # Sarvashtavarga
    thri_s = sarva_raw[:]
    _thrikona(thri_s)
    eka_s = thri_s[:]
    _ekathipathya(eka_s, signs)
    sp_s = int(sum(eka_s[i] * (gra_gun[i] + _RASI_GUN[i]) for i in range(12)))
    sarva = {
        "name": "Sarva",
        "raw":  sarva_raw,
        "thri": thri_s,
        "eka":  eka_s,
        "sodhya_pinda": sp_s,
        "contributors": [[] for _ in range(12)],
    }

    return {"planets": results, "sarva": sarva}


def drig_bala_matrix(p_degs):
    """Return 7×7 pairwise aspectual strength matrix for HOR.OUT Page 8.

    matrix[i][j] = aspect strength exerted by planet i on planet j.
    """
    matrix = [[0.0] * 7 for _ in range(7)]
    for i in range(7):
        for j in range(7):
            if i == j:
                continue
            diff = _deg_diff(p_degs[j], p_degs[i])
            sign = int(diff // 30)
            if sign > 0:
                frac = (diff % 30) / 30.0
                asp = _ASPEX[_ASP_PTR[i]]
                matrix[i][j] = 0.25 * (asp[sign - 1] + (asp[sign] - asp[sign - 1]) * frac)
    return matrix
