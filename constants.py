import datetime
import math

full_circle = 360.0
rads_per_degree = (math.pi / 180.0)
degs_per_radian = (180.0 / math.pi)

total_thithis = 30.0
total_yogams = 27.0
total_tamil_years = 60.0
tamil_year_base = 1987.0

minutes_in_degree = 60.0
seconds_in_minute = 60.0
seconds_in_degree = seconds_in_minute * minutes_in_degree

def degminsec_to_deg(deg, min, sec):
	float_deg = deg + (min / minutes_in_degree) + (sec / seconds_in_degree)
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

deg_angle_to_time_sec = (seconds_in_day) / full_circle
deg_angle_in_one_day = 360.0		# 360 degrees in one day
min_angle_in_one_day = deg_angle_in_one_day * 60.0

solar_days_in_year = 365.242216
sidereal_days_in_year = 365.256374



precession_per_year_in_sec = 50.2564
apse_movement_per_year_in_sec = 11.63

deg_in_house = 30		# 12 houses * 30 degrees = 360

arcsec_in_circle = seconds_in_degree * full_circle
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


moon_rev_days = 27.32166
mean_moon_long_at_epoch = degminsec_to_deg(8*30.0 + 17, 51, 16)
moon_apse_at_epoch = degminsec_to_deg(4*30.0 + 12, 0, 19)
moon_rahu_at_epoch = degminsec_to_deg(7*30.0 + 26, 41, 42)
moon_cv_degs = degminsec_to_deg(88, 22, 31)
moon_cv_rads = moon_cv_degs * rads_per_degree
moon_apse_revolution_days = 3232.54051
moon_rahu_revolution_days = 6793.39477
moon_eccentricity =  0.0549


class Mars:
    name = "MARS"
    length_semi_major_axis = 1.5237
    eccentricity = 0.09331 
    rev_days = 686.98
    apse_motion = 16.01
    node_motion = -22.74
    nc = 31.0 + (26.0 / 60.0)
    mean_long_at_epoch = degminsec_to_deg(9*30.0 +  1, 40, 43)
    mean_apse_at_epoch = degminsec_to_deg(4*30.0 + 11, 45, 22)
    mean_node_at_epoch = degminsec_to_deg(0*30.0 + 26, 20, 28)
    orbit_inclination_degs = degminsec_to_deg(1, 51, 6)

class Mercury:
    name = "Mercury"
    length_semi_major_axis = 0.3871
    eccentricity = 0.20561
    rev_days = 87.969
    apse_motion = 5.74
    node_motion = -7.58
    nc = 245.0 + (32.0 / 60.0)
    mean_long_at_epoch = degminsec_to_deg(5*30.0 +  8, 47, 17)
    mean_apse_at_epoch = degminsec_to_deg(7*30.0 + 23, 26, 15)
    mean_node_at_epoch = degminsec_to_deg(0*30.0 + 24, 41,  2)
    orbit_inclination_degs = degminsec_to_deg(7, 0, 0)

class Jupiter:
    name = "JUPITER"
    length_semi_major_axis = 5.2028
    eccentricity = 0.04833
    rev_days = 4332.585
    apse_motion = 7.70
    node_motion = -13.88
    nc = 4.0 + (59.0 / 60.0)
    mean_long_at_epoch = degminsec_to_deg(7*30.0 +  5, 38, 58)
    mean_apse_at_epoch = degminsec_to_deg(5*30.0 + 20, 15, 32)
    mean_node_at_epoch = degminsec_to_deg(2*30.0 + 16, 58, 53)
    orbit_inclination_degs = degminsec_to_deg(1, 19, 0)
    
class Venus:
    name = "VENUS"
    length_semi_major_axis = 0.7233
    eccentricity = 0.00681 
    rev_days = 224.7
    apse_motion = 0.43
    node_motion = -17.87
    nc = 96.0 + (8.0 / 60.0)
    mean_long_at_epoch = degminsec_to_deg(10*30.0 + 21,  8, 23)
    mean_apse_at_epoch = degminsec_to_deg( 9*30.0 + 21, 30, 25)
    mean_node_at_epoch = degminsec_to_deg( 1*30.0 + 23, 19,  3)
    orbit_inclination_degs = degminsec_to_deg(3, 23, 36)

class Saturn:
    name = "SATURN"
    length_semi_major_axis = 9.5547
    eccentricity = 0.05589
    rev_days = 10759.22
    apse_motion = 20.24
    node_motion = -18.82
    nc = 2.0
    mean_long_at_epoch = degminsec_to_deg(8*30.0 +  4,  7, 39)
    mean_apse_at_epoch = degminsec_to_deg(8*30.0 +  8, 38, 10)
    mean_node_at_epoch = degminsec_to_deg(3*30.0 +  0, 19, 42)
    orbit_inclination_degs = degminsec_to_deg(2, 49, 54)

class Uranus:
    name = "URANUS"
    length_semi_major_axis = 19.2181
    eccentricity = 0.04634 
    rev_days = 30686.84
    apse_motion = 3.18
    node_motion = -32.24
    nc = (42.0 / 60.0)
    mean_long_at_epoch = degminsec_to_deg( 7*30.0 + 11, 44, 39)
    mean_apse_at_epoch = degminsec_to_deg(10*30.0 + 29,  5, 12)
    mean_node_at_epoch = degminsec_to_deg( 1*30.0 + 21,  0, 53)
    orbit_inclination_degs = degminsec_to_deg(0, 46, 24)

class Neptune:
    name = "NEPTUNE"
    length_semi_major_axis = 30.1096
    eccentricity = 0.009 
    rev_days = 60186.64
    apse_motion = 1.03
    node_motion = -10.7
    nc = (22.0 / 60.0)
    mean_long_at_epoch = degminsec_to_deg(2*30.0 +  2,  0,  1)
    mean_apse_at_epoch = degminsec_to_deg(6*30.0 + 24, 15, 55)
    mean_node_at_epoch = degminsec_to_deg(3*30.0 + 18, 13,  9)
    orbit_inclination_degs = degminsec_to_deg(1, 46, 54)
    
