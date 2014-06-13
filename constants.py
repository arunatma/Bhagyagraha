import datetime
import math

full_circle = 360.0
rads_per_degree = (math.pi / 180.0)
degs_per_radian = (180.0 / math.pi)

total_thithis = 30.0
total_yogams = 27.0
total_tamil_years = 60.0
tamil_year_base = 1987.0

def degminsec_to_deg(deg, min, sec):
	float_deg = deg + (min / constants.minutes_in_degree) + (sec / constants.seconds_in_degree)
	float_deg %= full_circle
	return float_deg
	
epoch = datetime.datetime(1900, 1, 1)
precession_at_epoch = degminsec_to_deg(22, 27, 44)
apse_position_at_epoch = degminsec_to_deg(2*30.0 + 18, 45, 32)
mean_sun_long_at_epoch = degminsec_to_deg(8*30.0 + 17, 58, 26)
mean_sun_rise = datetime.datetime(1, 1, 1, 6, 0, 0)
time_twelve = datetime.datetime(1, 1, 1, 12, 0, 0)

IST_longitude = 82.5
seconds_in_day = 24 * 3600.0
ist_offset_in_sec = IST_longitude / 360.0 * seconds_in_day

deg_angle_to_time_sec = (seconds_in_day)/deg_in_full_circle
deg_angle_in_one_day = 360.0		# 360 degrees in one day
min_angle_in_one_day = deg_angle_in_one_day * 60.0

solar_days_in_year = 365.242216
sidereal_days_in_year = 365.256374

moon_rev_days = 27.32166
mean_moon_long_at_epoch = degminsec_to_deg(8*30.0 + 17, 51, 16)
moon_apse_at_epoch = degminsec_to_deg(4*30.0 + 12, 0, 19)
moon_rahu_at_epoch = degminsec_to_deg(7*30.0 + 26, 41, 42)
moon_cv_degs = degminsec_to_deg(88, 22, 31)
moon_cv_rads = moon_cv_degs * rads_per_degree
moon_apse_revolution_days = 3232.54051
moon_rahu_revolution_days = 6793.39477
moon_eccentricity =  0.0549

precession_per_year_in_sec = 50.2564
apse_movement_per_year_in_sec = 11.63

minutes_in_degree = 60.0
seconds_in_minute = 60.0
seconds_in_degree = seconds_in_minute * minutes_in_degree

deg_in_house = 30		# 12 houses * 30 degrees = 360

arcsec_in_circle = seconds_in_degree * deg_in_full_circle
arcsec_in_radian = arcsec_in_circle / (2 * math.pi)

sec_to_rad_conv_factor = (rads_per_degree / 3600.0)
ghatikas_to_sec_conv_factor = 24 * 60.0

kali_day = 1826556
earth_eccentricity = 0.01675
omega_rads = (23.0 + 27.5 / 60.0) * rads_per_degree;

# Todo: Need to ascertain what these constants are!
# Todo: Need to ascertain the names "motion" are valid
moon_motion = (790.0 + (35.0 / 60.0))
apse_motion = (6.0 + (41.0 / 60.0))
sun_motion = (59.0 + (8.0 / 60.0))