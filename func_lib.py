import constants
import re
import datetime

def find_sum_degs(degs_list):
	sum_angle = 0
	
	for(angle_degs in degs_list):
		sum_angle += angle_degs
	
	sum_angle %= constants.full_circle
	return sum_angle

def find_diff_degs(deg1, deg2):
	deg_result = (deg1 - deg2) % constants.full_circle
	return deg_result

def deg_in_float(deg, min, sec):
	float_deg = deg + (min / constants.minutes_in_degree) + 
		(sec / constants.seconds_in_degree)
	return float_deg
	
def get_time_in_IST(in_datetime, diff_from_gst_in_sec, dirn):
	if(re.IGNORECASE(r"w|(west)", dirn)):
		diff_from_gst_in_sec = -diff_from_gst_in_sec
	
	time_adj_sec = constants.ist_offset_in_sec - diff_from_gst_in_sec
	
	datetimeIST = in_datetime + datetime.timedelta(0, time_adj_sec)
	return datetimeIST
	
def get_local_time(datetimeIST, local_longitude, dirn):
	if(re.IGNORECASE(r"w|(west)", dirn)):
		local_longitude = -local_longitude
	
	diff_longitude = constants.IST_longitude - local_longitude
	diff_time_in_sec = diff_longitude * constants.deg_angle_to_time_sec
	localtm = datetimeIST - datetime.timedelta(0, diff_time_in_sec)
	return localtm
	
def get_precession(datetimeIST):
	time_elapsed = datetimeIST - constants.epoch
	
	years_elapsed = 
		(time_elapsed.days + time_elapsed.seconds / constants.seconds_in_day) /
		constants.solar_days_in_year
	
	precession_movement = 
		(constants.precession_per_year_in_sec * years_elapsed) / 
		constants.seconds_in_degree
	precession = constants.precession_at_epoch + precession_movement
	
	return precession
	
def get_mean_longitude_sun(localtm):
	msle = constants.mean_sun_long_at_epoch
	epoch_sun_rise = constants.mean_sun_rise
	epoch_sun_rise = epoch_sun_rise.replace(day = constants.epoch.day, 
		month = constants.epoch.month, year = constants.epoch.year)
		
	time_elapsed = localtm - epoch_sun_rise
	
	num_revolutions = (time_elapsed.days + 
		time_elapsed.seconds / constants.seconds_in_day) / 
		constants.sidereal_days_in_year
	
	angle_movement = (num_revolutions * constants.full_circle) 
	
	# find_sum_degs needs arguments to be passed in a list
	mean_long_sun_degs = find_sum_degs([msle, angle_movement])
	
	return mean_long_sun_degs
	
def get_equation_of_centre(mean_anomaly_rads):
	ma = mean_anomaly_rads
	e  = constants.earth_eccentricity
	ma_degs = ma * constants.rad_to_deg_conv_factor
	
	mandaphalam_secs = constants.arcsec_in_radian * 
		(e * math.sin(ma) / 2.0 * (4.0 - 5.0 * e * math.cos(ma)) + 
		math.pow(e, 3) / 12.0 * (13.0 * math.sin(3.0 * ma) - 3.0 * 
		math.sin(ma))) + 0.5;
		
	# If Mean Anomaly is above 180 degrees, mandaphalam has to be negative
	if  ma_degs > 180.0:
		mandaphalam_secs = -abs(mandaphalam_secs)
	
	# Mandaphalam and EquationOfCentre are one and the same.
	eq_centre_in_secs = mandaphalam_secs	
	
	return eq_centre_in_secs
	
def get_true_longitude_sun(mean_anomaly_degs, 
						   mean_long_sun_degs):
						   
	mean_anomaly_rads = mean_anomaly_degs * deg_to_rad_conv_factor
	mandaphalam_secs = equation_of_centre(mean_anomaly_rads)

	mandaphalam_degs = mandaphalam_secs / 3600.0
	
	true_long_sun_degs = find_sum_degs([mean_long_sun_degs, mandaphalam_degs])
	
	return true_long_sun_degs
	
def get_trop_longitude_sun(true_long_sun_degs, prec_at_birth):
		
	# Add Precession at Birth to get Tropical Longitude of Sun
	trop_long_sun_degs = find_sum_degs([true_long_sun_degs, prec_at_birth])
	
	return trop_long_sun_degs
	
def get_helio_centric_vel(mean_anomaly_rads):
	ma = mean_anomaly_rads
	e  = constants.earth_eccentricy
	
	# Redo: Give a proper variable name
	n = 59 * 60.0 + 8.0;
	
	helio_vel_in_secs = n * ( 1.0 - 2.0 * e * math.cos(ma)
		+ 2.5 * e * e * math.cos(2.0 * ma)
		- e * e * e * (13.0 * math.cos(3.0 * ma) - math.cos(ma))/4.0 ) + 0.5;
		
	return helio_vel_in_secs
	
def get_radius_vector(apse_posn_degs, trop_long_sun_degs):
	theta_degs = find_diff_degs(apse_posn_degs, trop_long_sun_degs)
	theta_rads = theta_degs * deg_to_rad_conv_factor
	
	e  = constants.earth_eccentricy
	
	rad_vec = (1.0 - e * e) / (1.0 - e * math.cos(theta_rads));
	
	return rad_vec
	
def get_hour_angle(latitude_degs, trop_long_sun_rads):

	tlsr  = trop_long_sun_rads 
	omega = constants.omega_rads
	lat_rads = latitude_degs * deg_to_rad_conv_factor
	
	# Redo: Need to give a proper name for ltfi_rads
	ltfi_rads = 
		math.atan(abs(math.sqrt(1.0 - math.sin(omega) * math.sin(omega) * 
		math.sin(tlsr) * math.sin(tlsr)) / (math.sin(omega) * math.sin(tlsr))))
				
	if lat_rads > ltfi_rads:
		lat_rads = ltfi_rads
		
	hour_angle_rads =	
		math.acos((-1.0 * math.tan(lat_rads) * math.sin(omega) * 
		math.sin(tlsr)) / math.sqrt(1.0 - math.sin(omega) * math.sin(omega) *
		math.sin(tlsr) * math.sin(tlsr)))
	
	return hour_angle_rads
	
def get_charam(hour_angle_degs):
	# Charam is the positive difference from 90 degree
	charam_degs = abs(90 - hour_angle_degs)
	return charam_degs
	
def get_pranam(trop_long_sun_rads):
				
	tlsr = trop_long_sun_rads
	omega = constants.omega_rads
	
	pranam_rads = math.atan((2.0 * math.tan(tlsr) * math.sin(omega/2.0) * 
		math.sin(omega/2.0)) /
		(1.0 + math.tan(tlsr) * math.tan(tlsr) * math.cos(omega)))
	
	# Pranam is Negative if TropLong of Sun is between 0-90 and 180-270 degrees
	if 0 <= tlsr < 0.5 * math.pi or math.pi <= tlsr < 1.5 * math.pi:
		pranam_rads = -pranam_rads
		
	return pranam_rads

def get_sun_rise_set(trop_long_sun_degs,
					mandaphalam_secs, 
					mean_anomaly_degs, 
					charam_degs,
					pranam_rads):
	
	tlsd = trop_long_sun_degs
	mp_rads = mandaphalam_secs * constants.sec_to_rad_conv_factor
	
	# Redo: Need to give a suitable name for net_rads	
	net_rads = pranam_rads + mp_rads
	net_degs = net_rads * rad_to_deg_conv_factor
	
	# Convert the angle-degrees to time-seconds. 
	# Redo: Give a proper name for app_noon_sec
	app_noon_sec = net_degs * constants.deg_angle_to_time_sec 
	
	# Add 15 Ghatikas (1 Ghatika = 1 Nazhigai = 24 minutes of time)
	app_noon_sec += 15 * constants.ghatikas_to_sec_conv_factor
	
	# Add 6 hours to get App Noon
	app_noon_sec = app_noon_sec + 6 * 3600
	
	if (lat_dir == 'N' and tlsd > 180) or (lat_dir == 'S' and tlsd <= 180):
		charam_degs = -charam_degs
		
	halfday_sec = charam_degs * constants.deg_angle_to_time_sec
	
	sun_rise_sec = app_noon_sec - halfday_sec
	sun_set_sec = app_noon_sec + halfday_sec
	
	return sun_rise_sec, sun_set_sec
	
def get_net_corr_in_min(ref_long_degs, given_long_degs,
	charam_degs, pranam_degs, mandaphalam_degs):
	
	# This function assumes that the longitude on left of GMT are negative.
	diff_long_degs = find_diff_degs(ref_long_degs, given_long_degs)
	
	net_corr_degs = find_sum_degs([charam_degs, pranam_degs, 
		mandaphalam_degs, diff_long_degs)
	
	net_corr_min = net_corr_degs * 60.0
	
	return net_corr_min

def sun_long_correction(true_long_sun_degs, net_corr_min, helio_vel_in_secs):
	net_corr_day = net_corr_min / constants.min_angle_in_one_day
	helio_vel_degs = helio_vel_in_secs / 3600.0
	
	corrected_true_long = find_sum_degs([true_long_sun_degs, 
		net_corr_day * helio_vel_degs])
		
	return corrected_true_long
	
def calc_tamil_date(given_time, fine_tuning = True):  # given_time is of type "datetime"
	
	original_time = given_time
	
	sunrise_time, sunset_time = get_sun_rise_set(given_time)
	
	sun_long_pos = sun_long_correction(given_time)
	
	if sunrise_time <= given_time <= sunset_time:
		# Add 5 minutes - Not sure why, need to check
		given_time += datetime.timedelta(0, 300)
		sun_long_pos = sun_long_correction(given_time)
	
	tamil_month_num = sun_long_pos / constants.deg_in_house
	
	# Make the target position as closest multiple of 30 less than sunlongpos
	target_pos = tamil_month_num * constants.deg_in_house
	
	# The objective is to find when exactly the sun crosses the target_pos
	# That will be counted as day 1 if it falls between sunrise and sunset
	# If the crossing happens after the sunset, Day 1 starts from the next day
	
	tamil_day = 1
	while sun_long_pos > target_pos:
		if abs(sun_long_pos - target_pos) > 330:
			sun_long_pos -= 360
			break
		
		# Go one day prior and recalculate sun's position
		given_time -= datetime.timedelta(1,0)
		# Increase the count by one for every one day gone in reverse
		tamil_day += 1
	
		sun_long_pos = sun_long_correction(given_time)
		
	# Now, gone back in days such that sun's position is less than target
	# Increment minute by minute to find where it crosses the target degrees
	while sun_long_pos < target_pos:
		if abs(sun_long_pos - target_pos) > 330:
			sun_long_pos -= 360
			break

		# Store the current time to check if the crossing happens pas 00:00 hrs
		stored_time = given_time
		# Go one minute ahead and recalculate sun's position
		given_time += datetime.timedelta(0, 60)
		
		if datetime.datetime(saved_time.year, saved_time.month, 
			saved_time.day) == datetime.datetime(given_time.year, 
			given_time.month, given_time.day):
			# The day is changed, so reduce the count of tamil day
			tamil_day -= 1
			
		sun_long_pos = sun_long_correction(given_time)
		
		if target_pos == 0:
			sun_long_pos -= 360
			
	cross_time = given_time
	sunrise_time, sunset_time = get_sun_rise_set(cross_time)
	
	if cross_time > sunset_time:
		tamil_day -= 1
		
	# Reload the original time
	given_time = original_time
	
	sun_long_pos = sun_long_correction(given_time)
	sunrise_time, sunset_time = get_sun_rise_set(given_time)
	
	if fine_tuning == True:
		# Tamil Day or Month starts with the sun rise only
		# So, if the given time is less than sunrise, go back in count by 1 day
		if given_time < sunrise_time
			tamil_day -= 1
			
			if tamil_day == 0:
				# Go one day prior and recalculate tamil_day
				given_time -= datetime.timedelta(1, 0)
				fine_tuning = False
				tamil_day = calc_tamil_date(given_time, fine_tuning)
	
	# Now algo to calculate the tamil year number - out of total 60 years
	
	tamil_year_num = (original_time.year - constants.tamil_year_base) %
		constants.total_tamil_years
		
	if original_time.month <= 4 and tamil_month_num >= 8:
		tamil_year_num -= 1
	
	return tamil_day, tamil_month_num, tamil_year_num
	

def get_yogam_karanam_thithi(sun_posn_degs, moon_posn_degs):
	
	# There are totally 30 thithis in Shukla and Krishna Paksham combined
	# So divide the thithi angle by 12 to get the thithi number
	thithi_angle = find_diff_degs(sun_posn_degs, moon_posn_degs)
	thithi_divisor = constants.full_circle / constants.total_thithis
	thithi_num = math.floor(thithi_angle / thithi_divisor)
		
	# There are totally 27 yogams 
	# So divide the yogam angle by 13.33 to get the yogam number
	yogam_angle = find_sum_degs(sun_posn_degs, moon_posn_degs)
	yogam_divisor = constants.full_circle / constants.total_yogams
	yogam_num = math.floor(yogam_angle / yogam_divisor)
	
	karanam_num = (math.floor(thithi_angle / 6) - 1) % 7
	
	if thithi_angle < 6:
		karanam_num += 4
		
	if thithi_angle >= 342:
		karanam_num += 7
		
	return yogam_num, karanam_num, thithi_num

def calc_saka_date(given_date):
	saka_max = [21, 20, 22, 21, 22, 22, 23, 23, 23, 23, 22, 22]
	saka_add = [11, 9, 10, 10, 10, 9, 9, 9, 8, 9, 9, 10]
	
	given_year = given_date.year
	given_month = given_date.month
	given_day = given_date.day

	month_index = given_month - 1
	
	if given_date.day >= saka_max[month_index]:
		saka_month_num = (given_month - 3) % 12
		saka_day = given_day - saka_max[month_index] + 1
	else:
		saka_month_num = (given_month - 4) % 12
		saka_day = given_day + saka_add[(month_index - 1) % 12]
		if given_month == 2:
			saka_day += is_leap_year(given_year)
			
	saka_year = given_year - 78
	saka_year -= (given_month < 3) or ((given_month == 3) and (given_day < 22))
	
	return saka_day, saka_month_num, saka_year
	
def is_leap_year(given_year):
	if year % 4 != 0 or (year % 100 == 0 and year % 400 != 0):
		return 0
	else:
		return 1
	
def get_ramc(given_date):
	return 0