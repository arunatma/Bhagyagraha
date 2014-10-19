import constants as cn
import re
import datetime as dt
import math

def get_input_params():
    """ Return input parameters in dictionary data type """
    input_params = dict()
    input_params["in_datetime"] = dt.datetime(2014, 9, 12, 17, 30)
    input_params["diff_from_gst_in_sec"] = 5 * 3600 + 30 * 60
    input_params["long_degs"] = 78.2
    input_params["long_dirn"] = "E"
    input_params["lat_degs"] = 11.66
    input_params["lat_dirn"] = "N"

    return input_params

def find_sum_degs(degs_list):
    """
    Return the sum of degrees; Mod to 360
    Input: A list containing individual elements, to be summed up
    """
    sum_angle = 0
    for angle_degs in degs_list:
        sum_angle += angle_degs
    
    sum_angle %= cn.full_circle
    return sum_angle

def find_diff_degs(deg1, deg2):
    """
    Return the difference in degrees; Mod to 360; always positive.
    Input: Two numbers: deg1 and deg2
    """
    deg_result = (deg1 - deg2) % cn.full_circle
    return deg_result

def get_time_in_IST(in_datetime, diff_from_gst_in_sec, dirn):
    """
    Convert given time to Indian Standard Time (datetime type)
    Input: Local Time (datetime type), Difference from GST in seconds, E/W dirn
    """
    # get_local_time converts to local time, given IST
    # get_time_in_IST converts to IST, given local time
    if re.match(r"w|(west)", dirn, re.IGNORECASE):
        diff_from_gst_in_sec = -diff_from_gst_in_sec
    time_adj_sec = cn.ist_offset_in_sec - diff_from_gst_in_sec
    ist_time = in_datetime + dt.timedelta(0, time_adj_sec)
    return ist_time
    
def get_local_time(ist_time, local_longitude, dirn):
    """
    Convert Indian Standard Time to local time (datetime type)
    Input: IST (datetime type), local longitude, E/W dirn
    This function is NOT an inverse function of get_time_in_IST
    get_local_time gives the exact time based on the longitude
    """
    # get_local_time converts to local time, given IST
    # get_time_in_IST converts to IST, given local time
    if re.match(r"w|(west)", dirn, re.IGNORECASE):
        local_longitude = -local_longitude
    diff_longitude = cn.IST_longitude - local_longitude
    diff_time_in_sec = diff_longitude * cn.deg_angle_to_time_sec
    localtm = ist_time - dt.timedelta(0, diff_time_in_sec)
    return localtm
    
def get_years_elapsed(ist_time, epoch_time):
    """
    Return time elapsed in years (fractional), since a given base date
    Input: IST in datetime, base date in datetime
    """
    # Call this function using the following command for most needs
    # get_years_elapsed(ist_time, cn.epoch)
    
    time_elapsed = ist_time - epoch_time
    years_elapsed = (time_elapsed.days + 
        time_elapsed.seconds / cn.seconds_in_day) / cn.solar_days_in_year
    return years_elapsed
    
def get_precession_degs(years_elapsed):
    """
    Return the current precession in degrees
    Input: Years elapsed since Epoch
    """
    precession_movement = (cn.precession_per_year_in_sec 
        * years_elapsed) / cn.seconds_in_degree
    precession_degs = cn.precession_at_epoch + precession_movement
    return precession_degs 

def get_apse_position_degs(apse_at_epoch, apse_motion, years_elapsed):
    # Epoch is taken as first day of 1900 for which the constants are given
    # Years Elapsed is in Solar years (Tropical Year) since 1900 
    """
    Return the current apse position in degrees.
    Input: Apse Position at Epoch (deg), Apse Movement per year (sec), years
           elapsed since Epoch.
    """
    apse_movement_degs = (apse_motion * years_elapsed) / cn.seconds_in_degree
    apse_position_degs = find_sum_degs([apse_at_epoch, apse_movement_degs])
    return apse_position_degs
    
def get_mean_anomaly_degs(apse_position_degs, mean_long_planet_degs):
    # ApsePosition - Mean Longitude of a planet (incl. Sun) is "Mean Anomaly"
    """
    Return the mean anomaly in degrees
    Input: Current apse position (deg), Mean longitude (deg)
    """
    mean_anomaly_degs = find_diff_degs(apse_position_degs, 
        mean_long_planet_degs)
    return mean_anomaly_degs

def get_days_from_epoch(localtm):
    """
    Return the days since Epoch Sun Rise, given local time in datetime type
    """
    time_elapsed = localtm - cn.epoch_sun_rise
    epoch_days = (time_elapsed.days + time_elapsed.seconds / cn.seconds_in_day)
    return epoch_days
        
def get_equation_of_centre(e, mean_anomaly_degs):
    """
    Return the mean longitude of sun, given local time in datetime type
    """
    ma = mean_anomaly_degs * cn.rads_per_degree
    
    mandaphalam_secs = cn.arcsec_in_radian * \
        (e * math.sin(ma) / 2.0 * (4.0 - 5.0 * e * math.cos(ma)) + \
        math.pow(e, 3) / 12.0 * (13.0 * math.sin(3.0 * ma) - 3.0 * \
        math.sin(ma))) + 0.5
        
    # If Mean Anomaly is above 180 degrees, mandaphalam has to be negative
    if  mean_anomaly_degs > 180.0:
        mandaphalam_secs = -abs(mandaphalam_secs)
    
    # Mandaphalam and EquationOfCentre are one and the same.
    eq_centre_in_secs = mandaphalam_secs    
    
    return eq_centre_in_secs
    
def get_true_longitude(mean_longitude_degs, mandaphalam_secs):
    """
    Return the true longitude in degrees
    Input: Mean longitude and mandaphalam (eqn. of centre)
    """
    mandaphalam_degs = mandaphalam_secs / 3600.0
    true_longitude_degs = find_sum_degs([mean_longitude_degs, mandaphalam_degs])
    return true_longitude_degs
    
def get_trop_longitude_sun(true_long_sun_degs, precession_degs):
    """
    Return the tropical longitude of sun, given true longitude and precession
    """
    # Add Precession to True Longitude to get Tropical Longitude of Sun
    trop_long_sun_degs = find_sum_degs([true_long_sun_degs, precession_degs])
    return trop_long_sun_degs
    
def get_helio_centric_vel(mean_anomaly_degs):
    """
    Return the heliocentric velocity (deg), given the mean anomaly in degrees
    """
    ma = mean_anomaly_degs * cn.rads_per_degree
    e  = cn.earth_eccentricity
    
    # Redo: Give a proper variable name
    n = 59 * 60.0 + 8.0
    
    helio_vel_secs = n * ( 1.0 - 2.0 * e * math.cos(ma)
        + 2.5 * e * e * math.cos(2.0 * ma)
        - e * e * e * (13.0 * math.cos(3.0 * ma) - math.cos(ma))/4.0 ) + 0.5
        
    helio_vel_degs = helio_vel_secs / cn.seconds_in_degree    
    return helio_vel_degs
    
def get_radius_vector(apse_position_degs, tlpd, e, lsma):
    """
    Return the radius vector, given apse position, longitude, eccentricity and
    length of semi major axis of the planet
    """
    # e: eccentricity
    # lsma: length of semi major axis
    # tlpd: True Longitude of the Planet or Tropical Longitude (for only Sun)
    theta_degs = find_diff_degs(apse_position_degs, tlpd)
    theta_rads = theta_degs * cn.rads_per_degree
    rad_vector =  lsma * (1.0 - e * e) / (1.0 - e * math.cos(theta_rads))
    return rad_vector
    
def get_hour_angle(latitude_degs, trop_long_sun_degs):
    """
    Return the hour angle in degrees, given latitude and tropical longitude of 
    sun in degrees
    """
    trop_long_sun_rads = trop_long_sun_degs * cn.rads_per_degree
    tlsr  = trop_long_sun_rads 
    omega = cn.omega_rads
    lat_rads = latitude_degs * cn.rads_per_degree
    
    # Redo: Need to give a proper name for ltfi_rads
    ltfi_rads = math.atan(abs(math.sqrt(1.0 - math.sin(omega) * \
        math.sin(omega) * math.sin(tlsr) * math.sin(tlsr)) / \
        (math.sin(omega) * math.sin(tlsr))))
                
    if lat_rads > ltfi_rads:
        lat_rads = ltfi_rads
        
    hour_angle_rads = math.acos((-1.0 * math.tan(lat_rads) * math.sin(omega) *  
        math.sin(tlsr)) / math.sqrt(1.0 - math.sin(omega) * math.sin(omega) * 
        math.sin(tlsr) * math.sin(tlsr)))
    
    hour_angle_degs = hour_angle_rads * cn.degs_per_radian
    # print "hour_angle_degs = ", hour_angle_degs
    return hour_angle_degs
    
def get_charam(hour_angle_degs):
    """
    Return the charam in degrees, given the hour angle in degrees
    """
    # Charam is the positive difference from 90 degree
    charam_degs = abs(90 - hour_angle_degs)
    # print "charam_degs = ", charam_degs
    return charam_degs
    
def get_pranam(trop_long_sun_degs):
    """
    Return the pranam in degrees, given the tropical longitude of sun in degrees
    """
    trop_long_sun_rads = trop_long_sun_degs * cn.rads_per_degree
    tlsr = trop_long_sun_rads
    omega = cn.omega_rads
    
    # Get always a positive value for pranam_rads; later, assign the sign
    pranam_rads = abs(math.atan((2.0 * math.tan(tlsr) * math.sin(omega/2.0) * 
        math.sin(omega/2.0)) /
        (1.0 + math.tan(tlsr) * math.tan(tlsr) * math.cos(omega))))
    
    # Pranam is Negative if TropLong of Sun is between 0-90 and 180-270 degrees
    if (0 <= tlsr < 0.5 * math.pi) or (math.pi <= tlsr < 1.5 * math.pi):
        pranam_rads = -pranam_rads
    
    pranam_degs = pranam_rads * cn.degs_per_radian
    # print "Trop Long = ", trop_long_sun_degs
    # print "pranam_degs = ", pranam_degs
    return pranam_degs

def get_sun_rise_set(in_datetime, trop_long_sun_degs, mandaphalam_secs, 
    mean_anomaly_degs, charam_degs, pranam_degs, lat_dir):
    """
    Return the sun rise and sun set, in seconds from 00:00 hours
    """
    tlsd = trop_long_sun_degs
    mp_degs = mandaphalam_secs / cn.seconds_in_degree
    
    # Redo: Need to give a suitable name for net_degs
    net_degs = pranam_degs + mp_degs
    # print "net_min = ", net_degs * 60
    # Convert the angle-degrees to time-seconds. 
    # Redo: Give a proper name for app_noon_sec
    app_noon_sec = net_degs * cn.deg_angle_to_time_sec 
    
    # Add 15 Ghatikas (1 Ghatika = 1 Nazhigai = 24 minutes of time)
    app_noon_sec += 15 * cn.ghatikas_to_sec_conv_factor
    # print "app_noon_sec = ", app_noon_sec
    # Add 6 hours to get App Noon
    app_noon_sec = app_noon_sec + 6 * 3600
    # print "app_noon_sec = ", app_noon_sec
    if (lat_dir == 'N' and tlsd > 180) or (lat_dir == 'S' and tlsd <= 180):
        charam_degs = -charam_degs
        
    # print "charam_degs = ", charam_degs        
    halfday_sec = charam_degs * cn.deg_angle_to_time_sec
    halfday_sec += 15 * cn.ghatikas_to_sec_conv_factor
    # print "halfday_sec = ", halfday_sec
    
    sunrise_sec = app_noon_sec - halfday_sec
    sunset_sec = app_noon_sec + halfday_sec
    
    base_date = in_datetime.replace(hour = 0, minute = 0, second = 0)
    sunrise_time = base_date + dt.timedelta(seconds = sunrise_sec)
    sunset_time = base_date + dt.timedelta(seconds = sunset_sec)    
    # print sunrise_time
    # print sunset_time
    return sunrise_time, sunset_time
    
def get_net_correction(charam_degs, mandaphalam_secs, pranam_degs, 
    longitude_degs, dirn):
    """
    Return the net correction in minutes 
    Input: Charam, Mandaphalam, Pranam, Longitude and Direction (E or W)
    """
    if re.match(r"w|(west)", dirn, re.IGNORECASE):
        longitude_degs = -longitude_degs
    mandaphalam_degs = mandaphalam_secs / cn.seconds_in_degree
    cha_man_pra = find_sum_degs([charam_degs, mandaphalam_degs, pranam_degs])
    net_corr_degs = find_diff_degs(cha_man_pra, longitude_degs)
    net_corr_mins = net_corr_degs * cn.minutes_in_degree
    # print "charam_degs = ", charam_degs
    # print "mandaphalam_degs = ", mandaphalam_degs
    # print "pranam_degs = ", pranam_degs
    # print "longitude_degs = ", longitude_degs
    return net_corr_mins    

def sun_corrected_long(true_long_sun_degs, net_corr_min, helio_vel_degs):
    """
    Return the corrected longitude of sun, taking in true longitude(deg), net 
    correction(min) and helio centric velocity(degs)
    """
    net_corr_day = net_corr_min / cn.min_angle_in_one_day
    
    corrected_true_long = find_sum_degs([true_long_sun_degs, 
        net_corr_day * helio_vel_degs])
        
    return corrected_true_long
    
def get_sun_params(input_params):
    
    # Input time given in datetime format. This is an approximate local time
    # For example, the time given by Indians is that of 82.5 E, which is not
    # local to individual locations
    
    # Two Steps:
    # 1. Convert it to IST equivalent using the GST offset
    # 2. Get the exact local time, based on the given local longitude
    
    # in_datetime = dt.datetime(2014, 9, 12, 17, 30)
    # diff_from_gst_in_sec = 5 * 3600 + 30 * 60
    # dirn = "E"
    # longitude_degs = 78.2
    # latitude_degs = 11.66
    # lat_dir = "N"

    in_datetime = input_params["in_datetime"]
    diff_from_gst_in_sec = input_params["diff_from_gst_in_sec"]
    longitude_degs = input_params["long_degs"]
    dirn = input_params["long_dirn"]
    latitude_degs = input_params["lat_degs"]
    lat_dirn = input_params["lat_dirn"]
    
    ist_time = get_time_in_IST(in_datetime, diff_from_gst_in_sec, dirn)
    local_time = get_local_time(ist_time, longitude_degs, dirn)
    
    years_since_epoch = get_years_elapsed(ist_time, cn.epoch)
    precession_degs = get_precession_degs(years_since_epoch)

    epoch_days = get_days_from_epoch(local_time)
    rev_days = cn.sidereal_days_in_year
    msle = cn.mean_sun_long_at_epoch
    mean_long_sun_degs = get_mean_longitude(epoch_days, rev_days, msle)
    apse_posn_sun_degs = get_apse_position_degs(cn.apse_position_at_epoch, 
        cn.apse_movement_per_year_in_sec, years_since_epoch)
    mean_anom_sun_degs = get_mean_anomaly_degs(apse_posn_sun_degs, 
        mean_long_sun_degs)
    mandaphalam_secs = get_equation_of_centre(cn.earth_eccentricity, 
        mean_anom_sun_degs)                            
        
    true_long_sun_degs = get_true_longitude(mean_long_sun_degs, 
        mandaphalam_secs)
    trop_long_sun_degs = get_trop_longitude_sun(true_long_sun_degs, 
        precession_degs)
    
    helio_vel_degs = get_helio_centric_vel(mean_anom_sun_degs)
    radius_vect_sun = get_radius_vector(apse_posn_sun_degs, 
        trop_long_sun_degs, cn.earth_eccentricity, cn.earth_lsma)
    
    hour_angle_degs = get_hour_angle(latitude_degs, trop_long_sun_degs)
    charam_degs = get_charam(hour_angle_degs)
    pranam_degs = get_pranam(trop_long_sun_degs)
    
    net_corr_min = get_net_correction(charam_degs, mandaphalam_secs,
        pranam_degs, longitude_degs, dirn)
    true_long_sun_degs = sun_corrected_long(true_long_sun_degs, 
        net_corr_min, helio_vel_degs)                        
    
    sunrise_dt, sunset_dt = get_sun_rise_set(in_datetime, trop_long_sun_degs, 
        mandaphalam_secs, mean_anom_sun_degs, charam_degs, pranam_degs, lat_dirn)

    sun_params = dict()
    sun_params["ist_time"] = ist_time
    sun_params["local_time"] = local_time
    sun_params["y_epoch"] = years_since_epoch
    sun_params["prec"] = precession_degs
    sun_params["d_epoch"] = epoch_days
    sun_params["mean_long"] = mean_long_sun_degs
    sun_params["true_long"] = true_long_sun_degs
    sun_params["trop_long"] = trop_long_sun_degs
    sun_params["apse"] = apse_posn_sun_degs
    sun_params["anom"] = mean_anom_sun_degs
    sun_params["eqnc"] = mandaphalam_secs
    sun_params["hvel"] = helio_vel_degs
    sun_params["rad"] = radius_vect_sun
    sun_params["ha"] = hour_angle_degs
    sun_params["charam"] = charam_degs
    sun_params["pranam"] = pranam_degs
    sun_params["rise"] = sunrise_dt
    sun_params["set"] = sunset_dt
    
    return sun_params
    
def get_lagn_params(input_params, sun_params):
    lat_degs = input_params["lat_degs"]
    lat_dirn = input_params["lat_dirn"]
    long_degs = input_params["long_degs"]
    long_dirn = input_params["long_dirn"]
    
    local_time = sun_params["local_time"]
    mean_long_sun_degs = sun_params["mean_long"]
    precession_degs = sun_params["prec"]
    
    south_hemi = re.match(r"s|(south)", lat_dirn, re.IGNORECASE) # True / False
    lt_corr_degs = get_local_time_correction(local_time)
    ramc_degs = get_ramc(long_degs, mean_long_sun_degs, long_dirn,
        precession_degs, lt_corr_degs, south_hemi)
    lagn_degs = get_ascendant(ramc_degs, lat_degs, precession_degs, south_hemi)
        
    lagn_params = dict()
    lagn_params["ramc"] = ramc_degs
    lagn_params["lagn"] = lagn_degs
    
    return lagn_params
    
def get_all_planets():
    input_params  = get_input_params()
    sun_params    = get_sun_params(input_params)
    moon_params   = get_moon_params(input_params, sun_params)
    lagn_params   = get_lagn_params(input_params, sun_params)
    seven_planets = get_seven_planets(sun_params, moon_params)
    
    return (sun_params, moon_params, lagn_params, seven_planets)
    
def calc_tamil_date(input_params, fine_tuning = True):  
    """
    Return Tamil Day, Month and Year
    Input: Local Time
    """
    # localtm is of type "datetime"
    cur_params = input_params.copy()
    original_time = cur_params["in_datetime"]
    sun_long_pos, sunrise_time, sunset_time = get_sun_params(cur_params)
    
    if sunrise_time <= cur_params["in_datetime"] <= sunset_time:
        # Add 5 minutes - Not sure why, need to check
        cur_params["in_datetime"] += dt.timedelta(0, 300)
        sun_long_pos, sunrise_time, sunset_time = get_sun_params(cur_params)
    
    tamil_month_num = sun_long_pos / cn.deg_in_house
    
    # Make the target position as closest multiple of 30 less than sunlongpos
    target_pos = tamil_month_num * cn.deg_in_house
    
    # The objective is to find when exactly the sun crosses the target_pos
    # That will be counted as day 1 if it falls between sunrise and sunset
    # If the crossing happens after the sunset, Day 1 starts from the next day
    
    tamil_day = 1
    while sun_long_pos > target_pos:
        if abs(sun_long_pos - target_pos) > 330:
            sun_long_pos -= 360
            break
        
        # Go one day prior and recalculate sun's position
        cur_params["in_datetime"] -= dt.timedelta(1,0)
        # Increase the count by one for every one day gone in reverse
        tamil_day += 1
        sun_long_pos, sunrise_time, sunset_time = get_sun_params(cur_params)
        
    # Now, gone back in days such that sun's position is less than target
    # Increment minute by minute to find where it crosses the target degrees
    while sun_long_pos < target_pos:
        if abs(sun_long_pos - target_pos) > 330:
            sun_long_pos -= 360
            break

        # Store the current time to check if the crossing happens pas 00:00 hrs
        saved_time = cur_params["in_datetime"]
        # Go one minute ahead and recalculate sun's position
        cur_params["in_datetime"] += dt.timedelta(0, 60)
        
        if dt.datetime(saved_time.year, saved_time.month, 
            saved_time.day) == dt.datetime(cur_params["in_datetime"].year, 
            cur_params["in_datetime"].month, cur_params["in_datetime"].day):
            # The day is changed, so reduce the count of tamil day
            tamil_day -= 1
            
        sun_long_pos, sunrise_time, sunset_time = get_sun_params(cur_params)
        
        if target_pos == 0:
            sun_long_pos -= 360
            
    cross_time = cur_params["in_datetime"]
    sun_long_pos, sunrise_time, sunset_time = get_sun_params(cur_params)
    
    if cross_time > sunset_time:
        tamil_day -= 1
        
    # Reload the original time and recalculate the sun position
    cur_params["in_datetime"] = original_time
    sun_long_pos, sunrise_time, sunset_time = get_sun_params(cur_params)
    
    if fine_tuning == True:
        # Tamil Day or Month starts with the sun rise only
        # So, if the given time is less than sunrise, go back in count by 1 day
        if cur_params["in_datetime"] < sunrise_time:
            tamil_day -= 1
            
            if tamil_day == 0:
                # Go one day prior and recalculate tamil_day
                cur_params["in_datetime"] -= dt.timedelta(1, 0)
                tamil_day = calc_tamil_date(cur_params, fine_tuning = False)
    
    # Now algo to calculate the tamil year number - out of total 60 years
    tamil_year_num = (original_time.year - cn.tamil_year_base) % \
        cn.total_tamil_years

    if original_time.month <= 4 and tamil_month_num >= 8:
        tamil_year_num -= 1
    
    return tamil_day, tamil_month_num, tamil_year_num
    

def get_yogam_karanam_thithi(sun_posn_degs, moon_posn_degs):
    """
    Return Yogam, Karanam and Thithi numbers
    Input: Sun Position and Moon Position in degrees
    """
    # There are totally 30 thithis in Shukla and Krishna Paksham combined
    # So divide the thithi angle by 12 to get the thithi number
    thithi_angle = find_diff_degs(sun_posn_degs, moon_posn_degs)
    thithi_divisor = cn.full_circle / cn.total_thithis
    thithi_num = math.floor(thithi_angle / thithi_divisor)
        
    # There are totally 27 yogams 
    # So divide the yogam angle by 13.33 to get the yogam number
    yogam_angle = find_sum_degs([sun_posn_degs, moon_posn_degs])
    yogam_divisor = cn.full_circle / cn.total_yogams
    yogam_num = math.floor(yogam_angle / yogam_divisor)
    
    karanam_num = (math.floor(thithi_angle / 6) - 1) % 7
    
    if thithi_angle < 6:
        karanam_num += 4
        
    if thithi_angle >= 342:
        karanam_num += 7
        
    return yogam_num, karanam_num, thithi_num

def calc_saka_date(given_date):
    """
    Return Saka Day, Month and Year
    Input: Current Date
    """
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
    
def get_kali_year(saka_year):
    """
    Return Kali Year, given the Saka Year
    """
    return (saka_year + 3180)
    
def is_leap_year(given_year):
    """
    Return 1 if given year is leap, else 0
    (Note: This function does not return True / False)
    """
    if year % 4 != 0 or (year % 100 == 0 and year % 400 != 0):
        return 0
    else:
        return 1
    
def get_ramc(local_longitude, mean_long_sun_degs, dirn, precsn_birth_degs, 
    lt_corr_degs, south_hemi):
    """
    Return RAMC in degrees
    """
    if re.match(r"w|(west)", dirn, re.IGNORECASE):
        local_longitude = -local_longitude
      
    # Todo: Need to understand what this longitudinal correction is
    # Right now, just implemented as what is in old C code
    
    # Longitude correction in days
    long_correction = (local_longitude * (59.0 + 8.0/60.0) / 
        cn.deg_angle_in_one_day)
    
    cml_sun = find_diff_degs(mean_long_sun_degs, long_correction)
    tl_sun = find_sum_degs([cml_sun, precsn_birth_degs])
    ramc_degs = find_sum_degs([tl_sun, lt_corr_degs])
    
    if south_hemi:
        ramc_degs = find_sum_degs([ramc_degs, 180])
        
    return ramc_degs
    
def get_local_time_correction(localtm):
    """
    Return Local Time Correction in degrees 
    Input: Local Time
    """
    time_twelve = cn.time_twelve
    time_twelve = time_twelve.replace(day = localtm.day, month = localtm.month,
        year = localtm.year)
    
    time_diff = localtm - time_twelve
    
    t1_time_seconds = time_diff.days * cn.seconds_in_day + \
        time_diff.seconds
        
    if(time_diff.days < 0):
         t1_time_seconds = - t1_time_seconds
    
    # 1 second adjustment for every 6 minute movement (i.e every 360 seconds)
    # 12 * 60 = 720 minutes moved in 12 hours => adj of 120 seconds
    t1_adj_seconds = t1_time_seconds // 360.0
    
    t1_total_seconds = t1_time_seconds + t1_adj_seconds
    
    # Converting time into corresponding degrees
    lt_corr_degs = (t1_total_seconds / cn.seconds_in_day) * \
        cn.full_circle
    
    if(localtm <= time_twelve):
        lt_corr_degs = -lt_corr_degs
        
    return lt_corr_degs
    
def get_ascendant(ramc_degs, latitude_degs, precsn_birth_degs, south_hemi):
    """
    Return Nirayana Lagnam in degrees
    """
    ramc_rads = ramc_degs * cn.rads_per_degree
    latitude_rads = latitude_degs * cn.rads_per_degree
    omega_rads = cn.omega_rads
    
    gaman_rads = math.atan(((math.tan(latitude_rads) * math.sin(omega_rads)) / 
        math.cos(ramc_rads)) + math.cos(omega_rads) * math.tan(ramc_rads))
    gaman_degs = gaman_rads * cn.degs_per_radian
    general_diff = find_diff_degs(gaman_degs, ramc_degs)
    if (general_diff < 180):
        nearest_diff = general_diff
    else:
        nearest_diff = find_diff_degs(cn.full_circle, general_diff)
    
    if (nearest_diff > 90):
        gaman_degs = find_sum_degs([gaman_degs, 180])
        
    # Todo: Questionable! Adding just like that 90 degrees to gaman
    gaman_degs = find_sum_degs([gaman_degs, 90])
    
    if(south_hemi):
        gaman_degs = find_sum_degs([gaman_degs, 180])    
    
    sayana_lagn = gaman_degs
    nirayana_lagn = find_diff_degs(sayana_lagn, precsn_birth_degs)
    # Nirayana Lagn is the House Position of Lagn (Planet 0)
    
    #Planets[0][0] = NiraLagn
    #PlanetDir[0][0]='E'    
    return nirayana_lagn

def get_culm_point(ramc_degs, latitude_degs, precsn_birth_degs, south_hemi):
    """
    Return Nirayana Dhasa in degrees
    """
    ramc_rads = ramc_degs * cn.rads_per_degree
    omega_rads = cn.omega_rads
    hlong_rads = math.atan(math.tan(ramc_rads) / math.cos(omega_rads))
    hlong_degs = hlong_rads * cn.degs_per_radian
    
    general_diff = find_diff_degs(ramc_degs, hlong_degs)
        
    if (general_diff < 180):
        nearest_diff = general_diff
    else:
        nearest_diff = find_diff_degs(cn.full_circle, general_diff)

    if (nearest_diff > 90):
        hlong_degs = find_sum_degs([hlong_degs, 180])

    if south_hemi:
        hlong_degs = find_sum_degs([hlong_degs, 180])
        
    sayana_dhasa = hlong_degs
    nirayana_dhasa = find_diff_degs(sayana_dhasa, precsn_birth_degs)

    # Nirayana Dhasa is the House Position of Planet 9
    return nirayana_dhasa

    
def calculate_house(sine_value, ramc_degs, ramc_adder, pole_id, 
    precsn_birth_degs, south_hemi):
    """
    Return House Position in degrees
    """
    # Todo: give proper names for ramc_adder and pole_id arguments
    omega_rads = constant.omega_rads
    pole_rads = math.asin(sine_value)
    # Todo: 30 needs to be replaced with appropriate value
    oblasc_degs = find_sum_degs([ramc_degs, ramc_adder])
    oblasc_rads = oblasc_degs * cn.rads_per_degree
    pole_elev_rads = math.atan((1.0 / math.tan(omega_rads)) * 
        math.sin(pole_id * pole_rads / 3.0))
    
    oblasc_sub90_degs = find_diff_degs(oblasc_degs, 90)
    oblasc_sub90_rads = oblasc_sub90_degs * cn.rads_per_degree
    hlong_rads = math.atan(-1.0 / ((math.tan(pole_elev_rads) * 
        math.sin(omega_rads) / cos(oblasc_sub90_rads)) + 
        (math.tan(oblasc_sub90_rads) * cos(omega_rads))))
    hlong_degs = hlong_rads * cn.degs_per_radian
    
    general_diff = find_diff_degs(oblasc_degs, hlong_degs)
    if (general_diff < 180):
        nearest_diff = general_diff
    else:
        nearest_diff = find_diff_degs(cn.full_circle, general_diff)        
    
    if (nearest_diff > 67):
         hlong_degs = find_sum_degs([hlong_degs, 180])
         
    if south_hemi:
        hlong_degs = find_sum_degs([hlong_degs, 180])
    
    house_position = find_diff_degs(hlong_degs, precsn_birth_degs)
    return house_position
    
def get_house_positions(nirayana_lagn, nirayana_dhasa, latitude_degs, ramc_degs, 
    precsn_birth_degs, south_hemi):
    """
    Return a list of 12 house positions
    """
    # house_positions is a list containing 12 elements
    # initializing the default value to 0
    house_positions = [0] * 12
    house_positions[0] = nirayana_lagn
    house_positions[9] = nirayana_dhasa
    
    latitude_rads = latitude_degs * cn.rads_per_degree
    omega_rads = cn.omega_rads
    
    sine_value = math.tan(latitude_rads) * math.tan(omega_rads)
    
    # Todo: Need to understand why there are two different modes here
    # Todo: Based on the latitude and omega (axis angle)
    if (sine_value > 1):
        nirayana_diff = find_diff_degs(nirayana_lagn, nirayana_dhasa)
        adder_for_h10h11 = nirayana_diff / 3.0
        house_positions[10] = find_sum_degs(
            [house_positions[9], adder_for_h10h11])
        house_positions[11] = find_sum_degs(
            [house_positions[10], adder_for_h10h11])
        
        adder_for_h1h2 = find_diff_degs(60, adder_for_h10h11)
        house_positions[1] = find_sum_degs([house_positions[0], adder_for_h1h2])
        house_positions[2] = find_sum_degs([house_positions[1], adder_for_h1h2])
    else:
        house_positions[10] = calculate_house(sine_value, ramc_degs, 30, 1,
            precsn_birth_degs, south_hemi)
        house_positions[11] = calculate_house(sine_value, ramc_degs, 60, 2,
            precsn_birth_degs, south_hemi)
        house_positions[1] = calculate_house(sine_value, ramc_degs, 120, 2,
            precsn_birth_degs, south_hemi)
        house_positions[2] = calculate_house(sine_value, ramc_degs, 150, 1,
            precsn_birth_degs, south_hemi)
            
    # House Positions of 3, 4, 5 are 180 degree from that of 9, 10, 1l 
    # House Positions of 6, 7, 8 are 180 degree from that of 0, 1, 2
    for i in range(3, 9):
        house_positions[i] = find_sum_degs([house_positions[(i+6) % 12], 180])
        
    return house_positions    
    
def get_bhava_positions(house_positions, planet_positions):
    """
    Return a list of 12 Bhava Positions
    """
    house1_degs = [0] * 12
    house2_degs = [0] * 12
    for i in range(0, 12):
        cur_house_degs = house_positions[i]
        pre_house_degs = house_positions[(i - 1) % 12]
        nxt_house_degs = house_positions[(i + 1) % 12]
        
        # Simpler logic to find the House1 and House2 Position (compared to C code)
        house1_degs = find_sum_degs([cur_house_degs, pre_house_degs])
        if (abs(cur_house_degs - pre_house_degs) > 90):
            house1_degs[i] = find_sum_degs([house1_degs, 180])

        house2_degs = find_sum_degs([cur_house_degs, nxt_house_degs])
        if (abs(cur_house_degs - nxt_house_degs) > 90):
            house2_degs[i] = find_sum_degs([house2_degs, 180])

    lagn_house = planet_positions[0] % 30.0
    bhava_positions = list()
    for i in range(0, 12):
        planet_pos_degs = planet_positions[i]
        for j in range(0, 12):
            if (planet_pos_degs >= house1_degs or 
                planet_pos_degs < house2_degs):
                bhava_num = (j + lagn_house) % 12
                bhava_positions.append(bhava_num)
                break
    return bhava_positions
    
def get_navamsa_positions(planet_positions):
    """
    Return a list of 12 Navamsa Positions
    """
    navams_positions = list()
    for i in range(0, 12):
        planet_pos_degs = planet_positions[i]
        planet_house = (planet_pos_degs // 30.0)
        planet_degs = (planet_pos_degs % 30.0)
        navamsa_num =  planet_house * 9.0 + (planet_degs * 60.0 // 200.0)
        navamsa_num = navamsa_num % 12
        navamsa_positions.append(navamsa_num)
    return navamsa_positions
    
def get_rasi_positons(planet_positions):
    """
    Return a list of 12 Rasi Positions
    """
    rasi_positions = list()
    for i in range(0, 12):
        planet_pos_degs = planet_positions[i]
        rasi_num = (planet_pos_degs // 30.0)
        rasi_positions.append(rasi_num)
    return rasi_positions
    
def get_mean_longitude(epoch_days, rev_days, mple, rahu = False):
    """
    Return the mean longitude of the planet
    """
    # mple is mean planet longitude at epoch
    num_revolutions = epoch_days / rev_days
    angle_movement = (num_revolutions * cn.full_circle) 
    # print "epoch_days = ", epoch_days
    # print "rev_days = ", rev_days
    # print "num_revolutions = ", num_revolutions
    # print "angle_movement = ", angle_movement % 360)
    
    if rahu:
        # Only for Rahu calculation, angle_movement needs to be subtracted
        mean_long_degs = find_diff_degs(mple, angle_movement)
    else:
        # find_sum_degs needs arguments to be passed in a list
        mean_long_degs = find_sum_degs([mple, angle_movement])
            
    return mean_long_degs
    
def get_moon_annual_variation(mandaphalam_secs):
    """
    Return Moon Annual Variation in minutes
    """
    mandaphalam_mins = mandaphalam_secs / cn.seconds_in_minute
    annual_varn_mins = -1.0 * mandaphalam_mins / 16.0
    return annual_varn_mins
    
def get_evection(mean_long_moon_degs, mean_long_sun_degs, mean_moon_apse_degs):
    """
    Return Moon Evection in minutes
    """
    moon_and_apse = find_sum_degs([mean_long_moon_degs, mean_moon_apse_degs])
    double_sun = find_sum_degs([mean_long_sun_degs, mean_long_sun_degs])
    
    theta_degs = find_diff_degs(moon_and_apse, double_sun)
    theta_rads = theta_degs * cn.rads_per_degree
    
    angle_rads = math.atan(-4467.0 / (60.0 * math.sin(theta_rads)))
    
    if(theta_degs < 180.0):
        quadrant_value = angle_degs // 90
        if(quadrant_value == 0 or quadrant_value == 2):
            angle_rads += math.pi
    
    evection_mins =  (4467.0 * math.cos(angle_rads + theta_rads)) / 60.0
    return evection_mins
    
def get_variation(mean_long_moon_degs, mean_long_sun_degs):
    """
    Return Moon Variation in minutes
    """
    theta_degs = find_diff_degs(mean_long_moon_degs, mean_long_sun_degs)
    theta_rads = theta_degs * cn.rads_per_degree
    moon_cv_rads = cn.moon_cv_rads
    tpluscvby2 = (theta_rads + moon_cv_rads) / 2.0
    tminuscvby2 = (theta_rads - moon_cv_rads) / 2.0
    
    variation_mins = -8580.0 * math.sin(theta_rads) * math.sin(tpluscvby2) * \
        math.sin(tminuscvby2) / 60.0
    return variation_mins

# Not sure why this get_near_value function is written. Need to understand    
def get_near_value(a1, a2):
    n1 = a1 // 90.0
    n2 = a2 // 90.0
    if (a2 < 0):
        if (a1 > -a2):
            a2 += ((n1 + 1) - n2) * 90.0
        else:
            if ((a1 > 0) and (a1 < 90) and (abs(a2) < 90)):
                a2 += 180
            else:
                a2 += ((n2 + 1) - n1) * 90.0
    else:
        if (a1 > a2):
            a2 += (n1 - n2) * 90.0
        else:
            a2 -= (n2 - n1) * 90.0
    return a2
    
def get_ecliptic_moon(true_moon_degs, rahu_degs):
    nodal_dist_degs = find_diff_degs(true_moon_degs, rahu_degs)
    nodal_dist_rads = nodal_dist_degs * cn.rads_per_degree
    
    theta_rads = 5.1467 * cn.rads_per_degree
    other_node_rads = math.atan(math.cos(theta_rads) * 
        math.tan(nodal_dist_rads))
    other_node_degs = other_node_rads * cn.degs_per_radian
    
    # Todo: What is this "near_value" function. Need to understand.
    nodal_corr_degs = get_near_value(nodal_dist_degs, other_node_degs)
    
    eclp_moon_degs = find_sum_degs([nodal_corr_degs, rahu_degs])
    
    true_moon_quad = true_moon_degs // 90.0
    eclp_moon_quad = eclp_moon_degs // 90.0
    
    if(true_moon_quad != eclp_moon_quad):
        quad_diff_degs = (true_moon_quad - eclp_moon_quad) * 90.0
        eclp_moon_degs = find_sum_degs([eclp_moon_degs, quad_diff_degs])
        
    return eclp_moon_degs

def get_moon_final_correction(mean_sun, mean_moon, sun_apse, moon_apse, rahu):
    """
    Return final correction of moon in degrees
    """
    d2rad = cn.rads_per_degree
    a = moon_sun        = find_diff_degs(mean_moon, mean_sun) * d2rad
    b = sun_apse_sun    = find_diff_degs(sun_apse, mean_sun) * d2rad
    c = moon_apse_moon  = find_diff_degs(moon_apse, mean_moon) * d2rad
    d = sun_moon_apse   = find_diff_degs(mean_sun, moon_apse) * d2rad
    e = moon_rahu       = find_diff_degs(mean_moon, rahu) * d2rad
    f = sun_rahu        = find_diff_degs(mean_sun, rahu) * d2rad
    
    corr_secs = -155.0 * math.sin(2.0*a + b) + 198.0 * math.sin(a + b - d) + \
        112.0 * math.sin(b - c)    + 73.0 * math.sin(b + c) + \
        85.0 * math.sin(c + 2.0*e) - 81.0 * math.sin(2.0 * f)
    corr_degs = corr_secs / cn.seconds_in_degree    
    return corr_degs
    
def add_correction(degree, nc, motion):
    cor = (motion * nc) / 21600.0
    return find_sum_degs([degree, cor / 60.0])
    
def get_moon_params(input_params, sun_params):
    """
    Return dictionary with positions of Moon, Apse, Rahu and Ketu in degrees
    """
    long_degs = input_params["long_degs"]
    long_dirn = input_params["long_dirn"]
    
    mean_sun_degs = sun_params["mean_long"]
    epoch_days = sun_params["d_epoch"]
    charam_degs = sun_params["charam"]
    pranam_degs = sun_params["pranam"]
    mandaphalam_secs = sun_params["eqnc"]
    sun_apse_degs = sun_params["apse"] 
    
    moon_epoch = cn.mean_moon_long_at_epoch
    moon_rev_days = cn.moon_rev_days
    mean_moon_degs = get_mean_longitude(epoch_days, moon_rev_days, moon_epoch)
    
    apse_epoch = cn.moon_apse_at_epoch
    apse_rev_days = cn.moon_apse_revolution_days
    mean_apse_degs = get_mean_longitude(epoch_days, apse_rev_days, apse_epoch)
    
    rahu_epoch = cn.moon_rahu_at_epoch
    rahu_rev_days = cn.moon_rahu_revolution_days
    mean_rahu_degs = get_mean_longitude(epoch_days, rahu_rev_days, rahu_epoch, 
        rahu = True)
    mean_ketu_degs = find_sum_degs([mean_rahu_degs, 180])
    
    net_corr_mins = get_net_correction(charam_degs, mandaphalam_secs, 
        pranam_degs, long_degs, long_dirn)
    
    mmc = cn.moon_motion
    amc = cn.apse_motion
    smc = cn.sun_motion
    mean_moon_corr_degs = add_correction(mean_moon_degs, net_corr_mins, mmc)
    mean_apse_corr_degs = add_correction(mean_apse_degs, net_corr_mins, amc)
    mean_sun_corr_degs = add_correction(mean_sun_degs, net_corr_mins, smc)
    # print "mean_moon_degs = ", mean_moon_degs
    # print "mean_apse_degs = ", mean_apse_degs
    # print "mean_sun_degs = ", mean_sun_degs
    # print "net_corr_mins = ", net_corr_mins
    # print "mean_moon_corr_degs = ", mean_moon_corr_degs
    # print "mean_apse_corr_degs = ", mean_apse_corr_degs
    # print "mean_sun_corr_degs = ", mean_sun_corr_degs

    annual_var_mins = get_moon_annual_variation(mandaphalam_secs)
    evection_mins = get_evection(mean_moon_corr_degs, mean_sun_corr_degs, 
        mean_apse_corr_degs)
    var_mins = get_variation(mean_moon_corr_degs, mean_sun_corr_degs)
    second_corr_mins = annual_var_mins + evection_mins + var_mins
    second_corr_degs = second_corr_mins / cn.minutes_in_degree
    # print "annual_var_mins = ", annual_var_mins
    # print "evection_mins = ", evection_mins
    # print "var_mins = ", var_mins
    # print "second_corr_mins = ", second_corr_mins
    
    mean_long_moon_degs = find_sum_degs([mean_moon_corr_degs, second_corr_degs])
    mean_anomaly_degs = find_diff_degs(mean_apse_corr_degs, mean_long_moon_degs)
    eqn_secs = get_equation_of_centre(cn.moon_eccentricity, mean_anomaly_degs)
    true_moon_degs = get_true_longitude(mean_long_moon_degs, eqn_secs)
    # print "mean_long_moon_degs = ", mean_long_moon_degs
    # print "true_moon_degs = ", true_moon_degs
    
    ecli_moon_degs = get_ecliptic_moon(true_moon_degs, mean_rahu_degs)
    final_corr_degs = get_moon_final_correction(mean_sun_corr_degs, 
        mean_long_moon_degs, sun_apse_degs, mean_apse_corr_degs, mean_rahu_degs)
    true_long_moon_degs = find_sum_degs([ecli_moon_degs, final_corr_degs])
    # print "ecli_moon_degs = ", ecli_moon_degs
    # print "final_corr_degs = ", final_corr_degs
    # print "true_long_moon_degs = ", true_long_moon_degs
    
    moon_params = dict()
    moon_params["apse"] = mean_apse_degs
    moon_params["moon"] = true_long_moon_degs
    moon_params["rahu"] = mean_rahu_degs
    moon_params["ketu"] = mean_ketu_degs
    
    return moon_params
    
def get_helio_velocity(net_corr_mins, ma_degs, e):
    # ma = mean anomaly, and e = eccentricity
    """
    Return the heliocentric velocity in degrees
    """
    ma = ma_degs * cn.rads_per_degree
    vel_mins = net_corr_mins * (1.0 - 2.0 * e * math.cos(ma)
                           + 5.0 * e * e * math.cos(2.0 * ma) / 2.0
                           - (e * e * e / 4.0) * (13.0 * math.cos(3.0 * ma)
                                                  - math.cos(ma)));
    vel_degs = vel_mins / 60.0
    return vel_degs

def get_longitude_along_ecliptic(epoch_node_degs, tlpd, inclination_rads, 
                                 node_vel, years_elapsed):
    node_motion_secs = (node_vel * years_elapsed) + 0.5
    # find the absolute of the node_motion
    # Todo:  This could possibly be wrong!
    node_motion_secs = abs(node_motion_secs)
    node_motion_degs = node_motion_secs / 3600.0
    cur_node_degs = find_diff_degs(epoch_node_degs, node_motion_degs)
    angle_node_planet_degs = find_diff_degs(tlpd, cur_node_degs)
    anp_rads = angle_node_planet_degs * cn.rads_per_degree
    dis_rads = math.atan(math.cos(inclination_rads) * math.tan(anp_rads))
    dis_degs = dis_rads * cn.degs_per_radian
    dis_degs = get_near_value(angle_node_planet_degs, dis_degs)
    long_along_ecliptic_degs = find_sum_degs([cur_node_degs, dis_degs])
    return angle_node_planet_degs, long_along_ecliptic_degs

def get_geo_longitude(true_long_planet_degs, hvel_degs, inc_rads, 
                      node_planet_rads, rad_vec, inferior, rad_vec_sun,
                      true_long_sun_degs, hvel_sun_degs):
    pm_rads = math.asin(math.sin(inc_rads) * math.sin(node_planet_rads))
    sm = rad_vec * math.cos(pm_rads)
    se = rad_vec_sun # Earth with respect to Sun
    gama_se_degs = find_sum_degs([true_long_sun_degs, 180])
    gama_se_rads = gama_se_degs * cn.rads_per_degree
    gama_sm_degs = true_long_planet_degs
    gama_sm_rads = gama_sm_degs * cn.rads_per_degree

    angle_mse_degs = find_diff_degs(gama_sm_degs, gama_se_degs)
    angle_mse_rads = angle_mse_degs * cn.rads_per_degree
    em = math.sqrt(sm * sm + se * se - 2.0 * sm * se * math.cos(angle_mse_rads))
    sine_value = (se / em) * math.sin(angle_mse_rads)
    # Crop the sine value within the limits of -1 and 1
    if sine_value > 1:
        sine_value = 1
    if sine_value < -1:
        sine_value = -1
    angle_sme_rads = math.asin(sine_value)
    angle_sme_degs = angle_sme_rads * cn.degs_per_radian
    
    if inferior == 0: # Superior Planet (Outside earth orbit)
        if angle_sme_degs > 90.0:
            angle_sme_degs = find_diff_degs(180, angle_sme_degs)
    else:
        tangle_mse_degs = angle_mse_degs
        if tangle_mse_degs > 180.0:
            tangle_mse_degs = find_diff_degs(360, tangle_mse_degs)
        tangle_mse_rads = tangle_mse_degs * cn.rads_per_degree
        angle_mes_rads = math.asin(sm * math.sin(tangle_mse_rads) / em)
        angle_mes_degs = angle_mes_rads * cn.degs_per_radian
        tangle_mse_degs = abs(tangle_mse_degs) + abs(angle_sme_degs) + \
                          abs(angle_mes_degs)
        if abs(tangle_mse_degs - 180) > 2:
            if angle_sme_degs > 0:
                angle_sme_degs = find_diff_degs(180, angle_sme_degs)
            else:
                angle_sme_degs = find_diff_degs(-180, angle_sme_degs)

    angle_sme_rads = angle_sme_degs * cn.rads_per_degree
    true_long_planet_degs = find_sum_degs([true_long_planet_degs, 
        angle_sme_degs])
        
    sine_value = math.sin(inc_rads) * math.sin(node_planet_rads)
    planet_lat_rads = math.atan((rad_vec / em) * math.sin(sine_value))
    planet_lat_degs = planet_lat_rads * cn.degs_per_radian

    vel_diff_degs = find_diff_degs(hvel_degs, hvel_sun_degs)
    geo_vel_adder = ((se / em) * (math.cos(angle_mse_rads) / 
        math.cos(angle_sme_rads)) - \
        (sm * se / (em * em * em)) * ((math.sin(angle_mse_rads)) ** 2) / 
        math.cos(angle_sme_rads)) * vel_diff_degs * (1 / 1.1)
    geo_vel_degs = find_sum_degs([hvel_degs, geo_vel_adder])
    return geo_vel_degs, true_long_planet_degs, planet_lat_degs
    
def jupiter_correction(mean_long_degs, ist_time):
    t = get_years_elapsed(ist_time, cn.jupiter_base)
    h = 18.129 * (t - 241.75) - (41 + (11/60.0));
    sj = 0.4074926;

    t_rad = t * cn.rads_per_degree
    h_rad = h * cn.rads_per_degree
    
    adj_min = 20.8 * math.sin(t_rad * sj) - 1.3783 * math.sin(h_rad) \
        + 3.4050 * math.sin(2.0 * h_rad)  + 0.2830 * math.sin(3.0 * h_rad);
    
    adj_degs = adj_min / 60.0;
    
    return (mean_long_degs + adj_degs)

def saturn_correction(mean_long_degs, ist_time):
    t = get_years_elapsed(ist_time, cn.saturn_base)
    x1 = 168.48 - 5.8945 * t
    x2 = 243.15 - 11.794 * t
    sj = 0.4074926;
    
    x1_rad = x1 * cn.rads_per_degree
    x2_rad = x2 * cn.rads_per_degree
    sj_rad = sj * cn.rads_per_degree
    
    adj_min = -48.7 * math.sin(t * sj_rad) \
        +  7.0 * math.sin(x1_rad) + 10.85 * math.sin(x2_rad);

    adj_degs = adj_min / 60.0;

    return (mean_long_degs + adj_degs)
    
def get_seven_planets(sun_params, moon_params):
    planet_dict = cn.planet_dict
    
    ist_time = sun_params["ist_time"]
    years_elapsed = sun_params["y_epoch"]
    epoch_days = sun_params["d_epoch"]
    true_long_sun_degs = sun_params["true_long"]
    hvel_sun_degs = sun_params["hvel"]
    radius_vect_sun = sun_params["rad"]
    ketu_long = moon_params["ketu"]
    
    seven_planets = dict()
    for name in planet_dict.keys():
        planet = planet_dict[name]
        seven_planets[name] = get_planet_params(planet, ist_time, 
            years_elapsed, epoch_days, true_long_sun_degs, hvel_sun_degs, 
            radius_vect_sun, ketu_long)
            
    return seven_planets
        
def get_planet_params(planet, ist_time, years_elapsed, epoch_days, 
    true_long_sun_degs, hvel_sun_degs, radius_vect_sun, mean_ketu_degs):

    lsma = planet.length_semi_major_axis
    eccentricity = planet.eccentricity
    apse_motion = planet.apse_motion
    node_motion = planet.node_motion
    net_corr_mins = planet.nc
    
    mmle = planet.mean_long_at_epoch
    mmae = planet.mean_apse_at_epoch
    mmne = planet.mean_node_at_epoch
    
    orbit_degs = planet.orbit_inclination_degs
    
    mean_long_degs = get_mean_longitude(epoch_days, planet.rev_days, 
                                        planet.mean_long_at_epoch)
    
    if planet.name == "JUPITER":
        mean_long_degs = jupiter_correction(mean_long_degs, ist_time)

    if planet.name == "SATURN":
        mean_long_degs = saturn_correction(mean_long_degs, ist_time)
                                        
    mean_long_degs = add_correction(mean_long_degs, net_corr_mins,
                                    mean_ketu_degs)
        
    apse_position_degs = get_apse_position_degs(mmae, apse_motion, 
        years_elapsed)
    mean_anomaly_degs = get_mean_anomaly_degs(apse_position_degs, 
        mean_long_degs)
    mandaphalam_secs = get_equation_of_centre(eccentricity, mean_anomaly_degs)
    true_long_degs = get_true_longitude(mean_long_degs, mandaphalam_secs)
    hvel_degs = get_helio_velocity(net_corr_mins, mean_anomaly_degs,
                                   eccentricity)
    radius_vec = get_radius_vector(apse_position_degs, true_long_degs, 
                                   eccentricity, lsma)
    inc_rads = orbit_degs * cn.rads_per_degree
    planet_node_degs, true_long_degs = get_longitude_along_ecliptic(mmne, 
        true_long_degs, inc_rads, node_motion, years_elapsed)
    planet_node_rads = planet_node_degs * cn.rads_per_degree
    
    inferior = 0
    if planet.name == "MERCURY" or  planet.name == "VENUS":
        inferior = 1
        
    geo_vel_degs, true_long_degs, planet_lat_degs = get_geo_longitude(
        true_long_degs, hvel_degs, inc_rads, planet_node_rads, radius_vec, 
        inferior, radius_vect_sun, true_long_sun_degs, hvel_sun_degs)
    
    planet_params = dict()
    planet_params["name"] = planet.name
    planet_params["mean_long"] = mean_long_degs
    planet_params["apse"] = apse_position_degs
    planet_params["anom"] = mean_anomaly_degs
    planet_params["mand"] = mandaphalam_secs
    planet_params["hvel"] = hvel_degs
    planet_params["rad"] = radius_vec
    planet_params["node"] = planet_node_degs
    planet_params["gvel"] = geo_vel_degs
    planet_params["true_long"] = true_long_degs
    planet_params["lat"] = planet_lat_degs
    
    return planet_params