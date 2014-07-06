import constants
import re
import datetime
import math

def find_sum_degs(degs_list):
    sum_angle = 0
    
    for angle_degs in degs_list:
        sum_angle += angle_degs
    
    sum_angle %= constants.full_circle
    return sum_angle

def find_diff_degs(deg1, deg2):
    deg_result = (deg1 - deg2) % constants.full_circle
    return deg_result

def deg_in_float(deg, min, sec):
    float_deg = deg + (min / constants.minutes_in_degree) + \
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
    
def get_years_elapsed(datetimeIST):
    time_elapsed = datetimeIST - constants.epoch
    years_elapsed = (time_elapsed.days + 
        time_elapsed.seconds / constants.seconds_in_day) / \
        constants.solar_days_in_year
    return years_elapsed
    
def get_precession(years_elapsed):
    precession_movement = (constants.precession_per_year_in_sec 
        * years_elapsed) / constants.seconds_in_degree
    precession_degs = constants.precession_at_epoch + precession_movement
    return precession_degs 

def get_apse_position_degs(apse_at_epoch, apse_motion, years_elapsed):
    # Implement the code for to calculate Mean Anomaly
    # ApsePos() in C code
    # Epoch is taken as first day of 1900 for which the constants are given
    # Calculate the Solar years (Tropical Year) since 1900 
    # ApsePosition is calculated as Epoch + Years * 11.63 seconds
    # ApsePosition - Mean Longitude of Sun is "Mean Anomaly"
    apse_movement_degs = (apse_motion * years_elapsed) / \
        constants.seconds_in_degree
    apse_position_degs = find_sum_degs([apse_at_epoch, apse_movement_degs])
    return apse_position_degs
    
def get_mean_anomaly_degs(apse_position_degs, mean_long_planet_degs):
    # Implement the code for to calculate Mean Anomaly
    # ApsePos() in C code
    # Epoch is taken as first day of 1900 for which the constants are given
    # Calculate the Solar years (Tropical Year) since 1900 
    # ApsePosition is calculated as Epoch + Years * 11.63 seconds
    # ApsePosition - Mean Longitude of Sun is "Mean Anomaly"
    mean_anomaly_degs = find_diff_degs(apse_position_degs, mean_long_planet_degs)
    return mean_anomaly_degs

def get_days_from_epoch(localtm):
    epoch_sun_rise = constants.mean_sun_rise
    epoch_sun_rise = epoch_sun_rise.replace(day = constants.epoch.day, 
        month = constants.epoch.month, year = constants.epoch.year)
        
    time_elapsed = localtm - epoch_sun_rise
    epoch_days = (time_elapsed.days + 
        time_elapsed.seconds / constants.seconds_in_day)
    
def get_mean_longitude_sun(localtm):
    msle = constants.mean_sun_long_at_epoch
    epoch_days = get_days_from_epoch(localtm)
    num_revolutions = epoch_days / constants.sidereal_days_in_year
    angle_movement = (num_revolutions * constants.full_circle) 
    
    # find_sum_degs needs arguments to be passed in a list
    mean_long_sun_degs = find_sum_degs([msle, angle_movement])
    return mean_long_sun_degs
    
def get_equation_of_centre(e, mean_anomaly_rads):
    ma = mean_anomaly_rads
    ma_degs = ma * constants.degs_per_radian
    
    mandaphalam_secs = constants.arcsec_in_radian * \
        (e * math.sin(ma) / 2.0 * (4.0 - 5.0 * e * math.cos(ma)) + \
        math.pow(e, 3) / 12.0 * (13.0 * math.sin(3.0 * ma) - 3.0 * \
        math.sin(ma))) + 0.5
        
    # If Mean Anomaly is above 180 degrees, mandaphalam has to be negative
    if  ma_degs > 180.0:
        mandaphalam_secs = -abs(mandaphalam_secs)
    
    # Mandaphalam and EquationOfCentre are one and the same.
    eq_centre_in_secs = mandaphalam_secs    
    
    return eq_centre_in_secs
    
def get_true_longitude_sun(mean_anomaly_degs, 
                           mean_long_sun_degs):
                           
    e = constants.earth_eccentricity
    mean_anomaly_rads = mean_anomaly_degs * constants.rads_per_degree
    mandaphalam_secs = get_equation_of_centre(e, mean_anomaly_rads)

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
    n = 59 * 60.0 + 8.0
    
    helio_vel_in_secs = n * ( 1.0 - 2.0 * e * math.cos(ma)
        + 2.5 * e * e * math.cos(2.0 * ma)
        - e * e * e * (13.0 * math.cos(3.0 * ma) - math.cos(ma))/4.0 ) + 0.5
        
    return helio_vel_in_secs
    
def get_radius_vector(apse_posn_degs, trop_long_sun_degs):
    theta_degs = find_diff_degs(apse_posn_degs, trop_long_sun_degs)
    theta_rads = theta_degs * constants.rads_per_degree
    
    e  = constants.earth_eccentricy
    
    rad_vec = (1.0 - e * e) / (1.0 - e * math.cos(theta_rads))
    
    return rad_vec
    
def get_hour_angle(latitude_degs, trop_long_sun_rads):

    tlsr  = trop_long_sun_rads 
    omega = constants.omega_rads
    lat_rads = latitude_degs * constants.rads_per_degree
    
    # Redo: Need to give a proper name for ltfi_rads
    ltfi_rads = math.atan(abs(math.sqrt(1.0 - math.sin(omega) * \
        math.sin(omega) * math.sin(tlsr) * math.sin(tlsr)) / \
        (math.sin(omega) * math.sin(tlsr))))
                
    if lat_rads > ltfi_rads:
        lat_rads = ltfi_rads
        
    hour_angle_rads = math.acos((-1.0 * math.tan(lat_rads) * math.sin(omega) *  
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
    net_degs = net_rads * constants.degs_per_radian
    
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
        mandaphalam_degs, diff_long_degs])
    
    net_corr_min = net_corr_degs * 60.0
    
    return net_corr_min
    
def get_net_correction(charam_degs, mandaphalam_secs, pranam_degs, 
    longitude_degs, dirn):
    if(re.IGNORECASE(r"w|(west)", dirn)):
        longitude_degs = -longitude_degs
    mandaphalam_degs = mandaphalam_secs / constants.seconds_in_degree
    net_corr_degs = find_sum_degs([charam_degs, mandaphalam_degs, pranam_degs])
    net_corr_degs = find_diff_degs([net_corr_degs, longitude_degs])
    net_corr_mins = net_corr_degs * constants.minutes_in_degree
    return net_corr_mins    

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
        if given_time < sunrise_time:
            tamil_day -= 1
            
            if tamil_day == 0:
                # Go one day prior and recalculate tamil_day
                given_time -= datetime.timedelta(1, 0)
                fine_tuning = False
                tamil_day = calc_tamil_date(given_time, fine_tuning)
    
    # Now algo to calculate the tamil year number - out of total 60 years
    
    tamil_year_num = (original_time.year - constants.tamil_year_base) % \
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
    yogam_angle = find_sum_degs([sun_posn_degs, moon_posn_degs])
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
    
def get_kali_year(saka_year):
    return (saka_year + 3180)
    
def is_leap_year(given_year):
    if year % 4 != 0 or (year % 100 == 0 and year % 400 != 0):
        return 0
    else:
        return 1
    
def get_ramc(given_date, local_longitude, mean_long_sun_degs, dirn,
    precsn_birth_degs, lt_corr_degs, is_southern_hemisphere):
    
    if(re.IGNORECASE(r"w|(west)", dirn)):
        local_longitude = -local_longitude
      
    # Todo: Need to understand what this longitudinal correction is
    # Right now, just implemented as what is in old C code
    
    # Longitude correction in days
    long_correction = (local_longitude * (59.0 + 8.0/60.0)) / \
        deg_angle_in_one_day
    
    cml_sun = find_diff_degs(mean_long_sun_degs, long_correction)
    tl_sun = find_sum_degs([cml_sun, precsn_birth_degs])
    ramc_degs = find_sum_degs([tl_sun, lt_corr_degs])
    
    if(is_southern_hemisphere):
        ramc_degs = find_sum_degs([ramc_degs, 180])
        
    return ramc_degs
    
def get_local_time_correction(localtm):
    time_twelve = constants.time_twelve
    time_twelve = time_twelve.replace(day = localtm.day, month = localtm.month,
        year = localtm.year)
    
    time_diff = localtm - time_twelve
    
    t1_time_seconds = time_diff.days * constants.seconds_in_day + \
        time_diff.seconds
        
    if(time_diff.days < 0):
         t1_time_seconds = - t1_time_seconds
    
    # 1 second adjustment for every 6 minute movement (i.e every 360 seconds)
    # 12 * 60 = 720 minutes moved in 12 hours => adj of 120 seconds
    t1_adj_seconds = t1_time_seconds // 360.0
    
    t1_total_seconds = t1_time_seconds + t1_adj_seconds
    
    # Converting time into corresponding degrees
    lt_corr_degs = (t1_total_seconds / constants.seconds_in_day) * \
        constants.full_circle
    
    if(localtm <= time_twelve):
        lt_corr_degs = -lt_corr_degs
        
    return lt_corr_degs
    
def get_ascendant(ramc_degs, latitude_degs, precsn_birth_degs, 
    is_southern_hemisphere):
    
    ramc_rads = ramc_degs * constants.rads_per_degree
    latitude_rads = latitude_degs * constants.rads_per_degree
    omega_rads = constants.omega_rads
    
    gaman_rads = math.atan(((math.tan(latitude_rads) * math.sin(omega_rads)) / 
        math.cos(ramc_rads)) + math.cos(omega_rads) * math.tan(ramc_rads))
        
    gaman_degs = gaman_rads * constants.degs_per_radian
    
    general_diff = find_diff_degs(gaman_degs, ramc_degs)
    if (general_diff < 180):
        nearest_diff = general_diff
    else:
        nearest_diff = find_diff_degs(constants.full_circle, general_diff)
    
    if (nearest_diff > 90):
        gaman_degs = find_sum_degs([gaman_degs, 180])
        
    # Todo: Questionable! Adding just like that 90 degrees to gaman
    gaman_degs = find_sum_degs([gaman_degs, 90])
    
    if(is_southern_hemisphere):
        gaman_degs = find_sum_degs([gaman_degs, 180])    
    
    sayana_lagn = gaman_degs
    nirayana_lagn = find_diff_digs(sayana_lagn, precsn_birth_degs)
    # Nirayana Lagn is the House Position of Lagn (Planet 0)
    
    #Planets[0][0] = NiraLagn
    #PlanetDir[0][0]='E'    
    return nirayana_lagn

def get_culm_point(ramc_degs, latitude_degs, precsn_birth_degs, 
    is_southern_hemisphere):
    
    ramc_rads = ramc_degs * constants.rads_per_degree
    omega_rads = constants.omega_rads
    hlong_rads = math.atan(math.tan(ramc_rads) / math.cos(omega_rads))
    hlong_degs = hlong_rads * constants.degs_per_radian
    
    general_diff = find_diff_degs(ramc_degs, hlong_degs)
        
    if (general_diff < 180):
        nearest_diff = general_diff
    else:
        nearest_diff = find_diff_degs(constants.full_circle, general_diff)

    if (nearest_diff > 90):
        hlong_degs = find_sum_degs([hlong_degs, 180])

    if(is_southern_hemisphere):
        hlong_degs = find_sum_degs([hlong_degs, 180])
        
    sayana_dhasa = hlong_degs
    nirayana_dhasa = find_diff_digs(sayana_dhasa, precsn_birth_degs)

    # Nirayana Dhasa is the House Position of Planet 9
    return nirayana_dhasa

    
def calculate_house(sine_value, ramc_degs, ramc_adder, pole_id, 
    precsn_birth_degs, is_southern_hemisphere):
    # Todo: give proper names for ramc_adder and pole_id arguments
    
    omega_rads = constant.omega_rads
    pole_rads = math.asin(sine_value)
    # Todo: 30 needs to be replaced with appropriate value
    oblasc_degs = find_sum_degs([ramc_degs, ramc_adder])
    oblasc_rads = oblasc_degs * constants.rads_per_degree
    pole_elev_rads = math.atan((1.0 / math.tan(omega_rads)) * 
        math.sin(pole_id * pole_rads / 3.0))
    
    oblasc_sub90_degs = find_diff_degs(oblasc_degs, 90)
    oblasc_sub90_rads = oblasc_sub90_degs * constants.rads_per_degree
    hlong_rads = math.atan(-1.0 / ((math.tan(pole_elev_rads) * 
        math.sin(omega_rads) / cos(oblasc_sub90_rads)) + 
        (math.tan(oblasc_sub90_rads) * cos(omega_rads))))
    hlong_degs = hlong_rads * constants.degs_per_radian
    
    general_diff = find_diff_degs(oblasc_degs, hlong_degs)
    if (general_diff < 180):
        nearest_diff = general_diff
    else:
        nearest_diff = find_diff_degs(constants.full_circle, general_diff)        
    
    if (nearest_diff > 67):
         hlong_degs = find_sum_degs([hlong_degs, 180])
         
    if(is_southern_hemisphere):
        hlong_degs = find_sum_degs([hlong_degs, 180])
    
    house_position = find_diff_degs(hlong_degs, precsn_birth_degs)
    return house_position
    
def get_house_positions(nirayana_lagn,  nirayana_dhasa, latitude_degs, 
    ramc_degs, precsn_birth_degs, is_southern_hemisphere):
    # house_positions is a list containing 12 elements
    # initializing the default value to 0
    house_positions = [0] * 12
    
    house_positions[0] = nirayana_lagn
    house_positions[9] = nirayana_dhasa
    
    latitude_rads = latitude_degs * constants.rads_per_degree
    omega_rads = constants.omega_rads
    
    sine_value = math.tan(latitude_rads) * math.tan(omega_rads)
    
    # Todo: Need to understand why there are two different modes here
    # Todo: Based on the latitude and omega (axis angle)
    if (sine_value > 1):
        nirayana_diff = find_diff_degs(nirayana_lagn, nirayana_dhasa)
        adder_for_h10h11 = nirayana_diff / 3.0
        house_positions[10] = find_sum_degs([house_positions[9], adder_for_h10h11])
        house_positions[11] = find_sum_degs([house_positions[10], adder_for_h10h11])
        
        adder_for_h1h2 = find_diff_degs(60, adder_for_h10h11)
        house_positions[1] = find_sum_degs([house_positions[0], adder_for_h1h2])
        house_positions[2] = find_sum_degs([house_positions[1], adder_for_h1h2])
    else:
        house_positions[10] = calculate_house(sine_value, ramc_degs, 30, 1,
            precsn_birth_degs, is_southern_hemisphere)
        house_positions[11] = calculate_house(sine_value, ramc_degs, 60, 2,
            precsn_birth_degs, is_southern_hemisphere)
        house_positions[1] = calculate_house(sine_value, ramc_degs, 120, 2,
            precsn_birth_degs, is_southern_hemisphere)
        house_positions[2] = calculate_house(sine_value, ramc_degs, 150, 1,
            precsn_birth_degs, is_southern_hemisphere)
            
    # House Positions of 3, 4, 5 are 180 degree from that of 9, 10, 1l 
    # House Positions of 6, 7, 8 are 180 degree from that of 0, 1, 2
    for i in range(3, 9):
        house_positions[i] = find_sum_degs([house_positions[(i+6) % 12], 180])
        
    return house_positions    
    
def get_bhava_positions(house_positions, planet_positions):
    
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
    rasi_positions = list()
    for i in range(0, 12):
        planet_pos_degs = planet_positions[i]
        rasi_num = (planet_pos_degs // 30.0)
        rasi_positions.append(rasi_num)
    return rasi_positions
    
def get_mean_longitude(epoch_days, rev_days, mple):
    # mple is mean planet longitude at epoch
    num_revolutions = epoch_days / rev_days
    angle_movement = (num_revolutions * constants.full_circle) 
    
    # find_sum_degs needs arguments to be passed in a list
    mean_long_degs = find_sum_degs([mple, angle_movement])
    return mean_long_degs

def get_moon_cur_pos(epoch_pos, revolution_days, epoch_days):
    num_revolutions = epoch_days / revolution_days
    angle_movement = (num_revolutions * constants.full_circle) 
    
    moon_cur_degs = find_sum_degs([epoch_pos, angle_movement])
    return moon_cur_degs
    
def get_moon_annual_variation(mandaphalam_secs):
    mandaphalam_mins = mandaphalam_secs / constants.seconds_in_minute
    annual_varn_mins = -1.0 * mandaphalam_mins / 16.0
    return annual_varn_mins
    
def get_evection(mean_long_moon_degs, mean_long_sun_degs, mean_moon_apse_degs):
    moon_and_apse = find_sum_degs([mean_long_moon_degs, mean_moon_apse_degs])
    double_sun = find_sum_degs([mean_long_sun_degs, mean_long_sun_degs])
    
    theta_degs = find_diff_degs(moon_and_apse, double_sun)
    theta_rads = theta_degs * constants.rads_per_degree
    
    angle_rads = math.atan(-4467.0 / (60.0 * math.sin(theta_rads)))
    
    if(theta_degs < 180.0):
        quadrant_value = angle_degs // 90
        if(quadrant_value == 0 or quadrant_value == 2):
            angle_rads += math.pi
    
    evection_mins =  (4467.0 * math.cos(angle_rads + theta_rads)) / 60.0
    return evection_mins
    
def get_variation(mean_long_moon_degs, mean_long_sun_degs):
    theta_degs = find_diff_degs(mean_long_moon_degs, mean_long_sun_degs)
    theta_rads = theta_degs * constants.rads_per_degree
    moon_cv_rads = constants.moon_cv_rads
    tpluscvby2 = (theta_rads + moon_cv_rads) / 2.0
    tminuscvby2 = (theta_rads - moon_cv_rads) / 2.0
    
    variation_mins = -8580.0 * math.sin(theta_rads) * math.sin(tpluscvby2) * \
        math.sin(tminuscvby2) / 60.0
    return variation_mins

def get_true_longitude_moon(corrected_moon_degs, corrected_apse_degs):
    mean_anomaly_degs = find_diff_degs(corrected_apse_degs, 
        corrected_moon_degs)
    mean_anomaly_rads = mean_anomaly_degs * constants.rads_per_degree
    e = constants.moon_eccentricity
    eqn_secs = get_equation_of_centre(e, mean_anomaly_rads)
    eqn_degs = (eqn_secs/3600.0)
    true_long_moon_degs = find_sum_degs([corrected_moon_degs, eqn_degs])
    return true_long_moon_degs
    
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
    nodal_dist_rads = nodal_dist_degs * constants.rads_per_degree
    
    theta_rads = 5.1467 * constants.rads_per_degree
    other_node_rads = math.atan(math.cos(theta_rads) * 
        math.tan(nodal_dist_rads))
    other_node_degs = other_node_rads * constants.degs_per_radian
    
    # Todo: What is this "near_value" function. Need to understand.
    nodal_corr_degs = get_near_value(nodal_dist_degs, other_node_degs)
    
    eclp_moon_degs = find_sum_degs[(nodal_corr_degs, rahu_degs)]
    
    true_moon_quad = true_moon_degs // 90.0
    eclp_moon_quad = eclp_moon_degs // 90.0
    
    if(true_moon_quad != eclp_moon_quad):
        quad_diff_degs = (true_moon_quad - eclp_moon_quad) * 90.0
        eclp_moon_degs = find_sum_degs([eclp_moon_degs, quad_diff_degs])
        
    return eclp_moon_degs

def get_moon_final_correction (mean_sun, mean_moon, sun_apse, moon_apse, rahu):
    d2rad = constants.rads_per_degree
    a = moon_sun        = find_diff_degs(mean_moon, mean_sun) * d2rad
    b = sun_apse_sun    = find_diff_degs(sun_apse, mean_sun) * d2rad
    c = moon_apse_moon  = find_diff_degs(moon_apse, mean_moon) * d2rad
    d = sun_moon_apse   = find_diff_degs(mean_sun, moon_apse) * d2rad
    e = moon_rahu       = find_diff_degs(mean_moon, rahu) * d2rad
    f = sun_rahu        = find_diff_degs(mean_sun, rahu) * d2rad
    
    corr_secs = -155.0 * math.sin(2.0*a + b) + 198.0 * math.sin(a + b - d) + \
        112.0 * math.sin(b - c)    + 73.0 * math.sin(b + c) + \
        85.0 * math.sin(c + 2.0*e) - 81.0 * math.sin(2.0 * f)
    corr_degs = corr_secs / constants.seconds_in_degree    
    return corr_degs
    
def add_correction(degree, nc, motion):
  cor = (motion * nc) / 21600.0
  return find_sum_degs([deg, cor / 60.0])
    
def moon_positions(mean_long_sun_degs, epoch_days, charam_degs, pranam_degs,
    # Positions of Moon, Rahu and Ketu are calculated in this function
    
    mandaphalam_secs, longitude_degs, sun_apse_degs, dirn):
    mean_long_moon_degs = get_mean_longitude(epoch_days, 
        constants.moon_rev_days, constants.mean_moon_long_at_epoch)
   
    apse_epoch = constants.moon_apse_at_epoch
    apse_revolution_days = constants.moon_apse_revolution_days
    mean_apse_degs = get_moon_cur_pos(apse_epoch, apse_revolution_days,
        epoch_days)
    
    rahu_epoch = constants.moon_rahu_at_epoch
    rahu_revolution_days = constants.moon_rahu_revolution_days
    mean_rahu_degs = get_moon_cur_pos(rahu_epoch, rahu_revolution_days, 
        epoch_days)
        
    net_corr_mins = get_net_correction(charam_degs, mandaphalam_secs, 
        pranam_degs, longitude_degs, dirn)
    
    mmc = constants.moon_motion
    amc = constants.apse_motion
    smc = constants.sun_motion
    mean_long_moon_degs = add_correction(mean_long_moon_degs, net_corr_mins,mmc)
    mean_apse_degs = add_correction(mean_apse_degs, net_corr_mins, amc)
    mean_long_sun_degs = add_correction(mean_long_sun_degs, net_corr_mins, smc)
    
    second_corr_mins = get_moon_annual_variation(mandaphalam_secs) + \
        get_evection(mean_long_moon_degs, mean_long_sun_degs, mean_apse_degs) + \
        get_variation(mean_long_moon_degs, mean_long_sun_degs)
    
    second_corr_degs = second_corr_mins / constants.minutes_in_degree
    mean_long_moon_degs = find_sum_degs([mean_long_moon_degs, second_corr_degs])
    true_long_moon_degs = find_sum_degs([mean_long_moon_degs, mean_apse_degs])
    ecli_moon_degs = find_sum_degs([true_long_moon_degs, mean_rahu_degs])
    
    final_corr_mins = get_moon_final_correction(mean_long_sun_degs, 
        mean_long_moon_degs, sun_apse_degs, mean_apse_degs, mean_rahu_degs)
    true_long_moon_degs = find_sum_degs([true_long_moon_degs, final_corr_mins])
    
    mean_ketu_degs = find_sum_degs([mean_rahu_degs, 180])
    return true_long_moon_degs, mean_rahu_degs, mean_ketu_degs
    
def get_true_long_planet(mean_long_planet_degs, mandaphalam_secs):
    mandaphalam_degs = mandaphalam_secs / 3600.00
    true_long_planet_degs =  find_sum_degs([mean_long_planet_degs, 
        mandaphalam_degs])
    
def mars_positions():
    lsma = constants.mars_length_semi_major_axis
    eccentricity = constants.mars_eccentricity
    apse_motion = constants.mars_apse_motion
    node_motion = constants.mars_node_motion
    net_corr_mins = constants.mars_nc
    
    mmle = constants.mean_mars_long_at_epoch
    mmae = constants.mean_mars_apse_at_epoch
    mmne = constants.mean_mars_node_at_epoch
    
    orbit_degs = constants.mars_orbit_inclination_degs
    
    mean_long_mars_degs = get_mean_longitude(epoch_days, 
        constants.mars_rev_days, constants.mean_mars_long_at_epoch)
    
    mean_long_mars_degs = add_correction(mean_long_mars_degs, net_corr_mins,
        mean_ketu_degs)
        
    apse_position_degs = get_apse_position_degs(mmae, apse_motion, 
        years_elapsed)
    mean_anomaly_degs = get_mean_anomaly_degs(apse_position_degs, 
        mean_long_mars_degs)
    mean_anomaly_rads = mean_anomaly_degs * constants.rads_per_degree
    mandaphalam_secs = get_equation_of_centre(eccentricity, mean_anomaly_rads)
    true_long_mars_degs = get_true_long_planet(mean_long_mars_degs, 
        mandaphalam_secs)
    helio_velocity_mars = get_helio_velocity(net_corr_mins, mean_anomaly_degs,
        eccentricity)
    radius_vector_mars = get_radius_vector(apse_position_degs, 
        true_long_mars_degs, eccentricity, lsma)
    angle_mars_node_degs, true_long_mars_degs = get_longitude_along_ecliptic(
        mmne, true_long_mars_degs, orbit_degs, node_motion)
    
def get_helio_velocity(net_corr_mins, ma_degs, e):
    # ma = mean anomaly, and e = eccentricity
    ma = ma_degs * constants.rads_per_degree
    vel_mins = net_corr_mins * (1.0 - 2.0 * e * math.cos(ma)
                           + 5.0 * e * e * math.cos(2.0 * ma) / 2.0
                           - (e * e * e / 4.0) * (13.0 * math.cos(3.0 * ma)
                                                  - math.cos(ma)));
    vel_degs = vel_mins / 60.0
    return vel_degs

def get_radius_vector(apse_position_degs, tlpd, e, lsma):
    # e: eccentricity
    # lsma: length of semi major axis
    # tlpd: True Longitude of the Planet in degs
    theta_degs = find_diff_degs(apse_position_degs, tlpd)
    theta_rads = theta_degs * constants.rads_per_degree
    rad_vector =  lsma * (1.0 - e * e) / (1.0 - e * math.cos(theta_rads)) )
    return rad_vector

def get_longitude_along_ecliptic(epoch_node_degs, tlpd, orbit_degs, node_vel, years_elapsed):
    node_motion_secs = (node_vel * years_elapsed) + 0.5
    # find the absolute of the node_motion
    # Todo:  This could possibly be wrong!
    node_motion_secs = abs(node_motion_secs)
    node_motion_degs = node_motion_secs / 3600.0
    cur_node_degs = find_diff_degs(epoch_node_degs, node_motion_degs)
    angle_node_planet_degs = find_diff_degs(tlpd, cur_node_degs)
    anp_rads = angle_node_planet_degs * constants.rads_per_degree
    inclination_rads = orbit_degs * constants.rads_per_degree
    dis_rads = math.atan(math.cos(inclination_rads) * math.tan(anp_rads))
    dis_degs = dis_rads * constants.degs_per_radian
    dis_degs = find_near_value(angle_node_planet_degs, dis_degs)
    long_along_ecliptic_degs = find_sum_degs([cur_node_degs, dis_degs])
    return angle_node_planet_degs, long_along_ecliptic_degs

def get_geo_longitude(true_long_planet_degs, hvel_degs, inc_rads, 
                      node_planet_rads, rad_vec, inf, pos, rad_vec_sun,
                      true_long_sun_degs, hvel_sun_degs):
    pm_rads = math.asin(math.sin(inc_rads) * math.sin(node_planet_rads))
    sm = rad_vec * math.cos(pm_rads)
    se = rad_vec_sun
    gama_se_degs = find_sum_degs([true_long_sun_degs, 180])
    gama_se_rads = gama_se_degs * constants.rads_per_degree
    gama_sm_degs = true_long_planet_degs
    gama_sm_rads = gama_sm_degs * constants.rads_per_degree

    angle_mse_degs = find_diff_degs(gama_sm_degs, gama_se_degs)
    angle_mse_rads = angle_mse_degs * constants.rads_per_degree
    em = math.sqrt(sm * sm + se * se - 2.0 * sm * se * math.cos(angle_mse_rads))
    sine_value = (se / em) * math.sin(angle_mse_rads)
    # Crop the sine value within the limits of -1 and 1
    if sine_value > 1:
        sine_value = 1
    if sine_value < -1:
        sine_value = -1
    angle_sme_rads = math.asin(sine_value)
    angle_sme_degs = angle_sme_rads * constants.degs_per_radian
    
    if inf == 0: # Superior Planet
        if angle_sme_degs > 90.0:
            angle_sme_degs = find_diff_degs(180, angle_sme_degs)
    else:
        tangle_mse_degs = angle_mse_degs
        if tangle_mse_degs > 180.0:
            tangle_mse_degs = find_diff_degs(360, tangle_mse_degs)
        tangle_mse_rads = tangle_mse_degs * constants.rads_per_degree
        angle_mes_rads = math.asin(sm * math.sin(tangle_mse_rads) / em)
        angle_mes_degs = angle_mes_rads * constants.degs_per_radian
        tangle_mse_degs = abs(tangle_mse_degs) + abs(angle_sme_degs) + \
                          abs(angle_mes_degs)
        if abs(tangle_mse_degs - 180) > 2:
            if angle_sme_degs > 0:
                angle_sme_degs = find_diff_degs(180, angle_sme_degs)
            else:
                angle_sme_degs = find_diff_degs(-180, angle_sme_degs)

    angle_sme_rads = angle_sme_degs * constants.rads_per_degree
    true_long_planet_degs = find_sum_degs([true_long_planet_degs, angle_sme_degs])
        
    sine_value = math.sin(inc_rads) * math.sin(node_planet_rads)
    planet_rads = math.atan((rad_vec / em) * math.sin(sine_value))
    planet_degs = planet_rads * constants.degs_per_radian

    vel_diff_degs = find_diff_degs(hvel_degs, hvel_sun_degs)
    geo_vel_adder = ((se / em) * (math.cos(angle_mse_rads) / 
                        math.cos(angle_sme_rads)) - \
                        (sm * se / (em * em * em)) * ((math.sin(angle_mse_rads)) ** 2) / 
                        math.cos(angle_sme_rads)) * vel_diff_degs * (1 / 1.1)
    geo_vel_degs = find_sum_degs([hvel_degs, geo_vel_adder])
    return geo_vel_degs, true_long_planet_degs
