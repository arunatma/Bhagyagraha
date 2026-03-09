# Bhagyagraha

A Hindu horoscope calculator written in Python, converted from a C program.
Computes nirayana (sidereal) planetary positions and astrological data following
the traditional Indian Surya Siddhanta method.

## Features

- Planetary longitudes (Nirayana / sidereal) for all 12 grahas including Rahu and Ketu
- Lagna (Ascendant) and Bhava cusps (equal-house system)
- Calendar data: Thithi, Yogam, Karanam, Paksham, Tamil Date, Saka Date, Kali Year
- Janma Nakshatra (birth star) and Vimsottari Dasa balance at birth
- Shadbala (six-fold planetary strength) and Bhava Bala (house strength)
- Navamsa and Mutual Disposition charts
- Streamlit web application with South Indian chart diagrams
- Downloadable single-page HTML report (PDF via browser print or WeasyPrint)
- Comparison framework (`compare.py`) to diff Python output against the C reference

## Project Structure

```
Bhagyagraha/
├── app.py          # Streamlit web application
├── astro.py        # Command-line entry point (prints full horoscope)
├── functions.py    # Core astronomical calculations
├── shadbala.py     # Shadbala, Bhava Bala, Mutual Disposition
├── constants.py    # Astronomical constants (epoch, eccentricities, etc.)
├── compare.py      # Python-vs-C comparison framework
└── tests/
    ├── arunram/        # input.txt + expected.out (HOR.OUT reference)
    ├── anusha/         # input.txt
    └── warren_buffett/ # input.txt
```

## Installation

Python 3.9 or later is required.

```bash
pip install -r requirements.txt
```

PDF download in the web app requires WeasyPrint (optional):

```bash
pip install weasyprint
```

## Usage

### Streamlit web app

```bash
streamlit run app.py
```

Open http://localhost:8501, fill in the birth details in the sidebar, and click
**Calculate Horoscope**.  Two tabs are available:

- **Horoscope** — calendar data, South Indian charts, planetary tables, Shadbala
- **HTML Report** — single-page C-style report with download buttons (HTML / PDF)

### Command-line

Create an input file in the same format as `tests/arunram/input.txt` (see Input
Format below), then:

```bash
python astro.py < input.txt
```

### Comparison framework

Compare Python output against a C reference file (HOR.OUT):

```bash
# Using a pre-generated reference file
python compare.py --input data.txt --c-ref tests/arunram/expected.out

# Run the C executable live, then compare
python compare.py --input data.txt --horos path/to/horos.exe

# Limit to a section: calendar | planets | shadbala | bhava-bala | mutual-disp
python compare.py --input data.txt --c-ref tests/arunram/expected.out --section planets

# Show all fields, not just mismatches
python compare.py --input data.txt --c-ref tests/arunram/expected.out --verbose
```

## Input Format

Plain text, one value per line:

```
Name
Day (1-31)
Month (1-12)
Year
Hour (0-23)
Minute (0-59)
Place of birth
Latitude degrees
Latitude minutes
N or S
Longitude degrees
Longitude minutes
E or W
Timezone hours offset from GMT
Timezone minutes offset from GMT
```

Example (`tests/arunram/input.txt` — Arunram, born Salem, India):

```
Arunram
28
05
1983
 7
 11
Salem
 11
 39
N
 78
 12
E
 5
 30
```

## Calculation Method

The calculations follow the traditional Surya Siddhanta / Indian almanac method
as implemented in the original C program:

- Epoch: 1 January 1900, 06:00 (sunrise at Lanka reference meridian)
- Moon position uses the classical corrections: annual variation, evection,
  variation, equation of centre (eccentricity 0.0549), ecliptic reduction,
  and a six-term final correction
- Ayanamsa (precession) follows the Lahiri convention embedded in the epoch
  constants
- Shadbala follows the traditional six components: Sthana, Kala, Dig,
  Naisargika, Chesta, and Drik Bala

## Known Limitations

- Outer planet longitudes (Jupiter, Venus, Saturn, Uranus, Neptune) currently
  differ from the C reference by ~90°; this is an ongoing investigation into
  the heliocentric-to-geocentric conversion for slow planets
- Lagna (Ascendant) differs from the C reference by ~12°; under investigation

## License

MIT — see [LICENSE](LICENSE).
