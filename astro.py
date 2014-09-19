import functions as fn
import constants as cn
import datetime as dt

def get_sun_position():
    
    # in_datetime is as given as input. This is an approximate local time
    # For example, the time given by Indians is that of 82.5 E, which is not
    # local to individual locations
    
    # Two Steps:
    # 1. Convert it to IST equivalent using the GST offset
    # 2. Get the exact local time, based on the given local longitude
    
    in_datetime = dt.datetime(2014, 9, 12, 17, 30)
    diff_from_gst_in_sec = 5 * 3600 + 30 * 60
    dirn = "E"
    local_longitude = 78.2
    latitude_degs = 11.66
    lat_dir = "N"
    
    datetimeIST = fn.get_time_in_IST(in_datetime, diff_from_gst_in_sec, dirn)
    local_time = fn.get_local_time(datetimeIST, local_longitude, dirn)
    
    years_since_epoch = fn.get_years_elapsed(datetimeIST, cn.epoch)
    precession_degs = fn.get_precession_degs(years_since_epoch)
    
    mean_long_sun_degs = fn.get_mean_longitude_sun(local_time)
    apse_posn_sun_degs = fn.get_apse_position_degs(cn.apse_position_at_epoch, 
                            cn.apse_movement_per_year_in_sec, years_since_epoch)
    mean_anom_sun_degs = fn.get_mean_anomaly_degs(apse_posn_sun_degs, 
                            mean_long_sun_degs)
    mandaphalam_secs = fn.get_equation_of_centre(cn.earth_eccentricity, 
        mean_anom_sun_degs)                            
    true_long_sun_degs = fn.get_true_longitude_sun(mean_anom_sun_degs, 
                            mean_long_sun_degs, mandaphalam_secs)
    
    helio_vel_sec = fn.get_helio_centric_vel(mean_anom_sun_degs)
    
    trop_long_sun_degs = fn.get_trop_longitude_sun(true_long_sun_degs, 
                            precession_degs)
    radius_vect_sun  = fn.get_radius_vector(apse_posn_sun_degs, trop_long_sun_degs,
                            cn.earth_eccentricity, cn.earth_lsma)
    
    hour_angle_degs = fn.get_hour_angle(latitude_degs, trop_long_sun_degs)
    charam_degs = fn.get_charam(hour_angle_degs)
    
    pranam_degs = fn.get_pranam(trop_long_sun_degs)
    sunrise_sec, sunset_sec = fn.get_sun_rise_set_sec(trop_long_sun_degs, 
        mandaphalam_secs, mean_anom_sun_degs, charam_degs, pranam_degs, lat_dir)
        
    base_date = in_datetime.replace(hour = 0, minute = 0, second = 0)
    sunrise_time = base_date + dt.timedelta(seconds = sunrise_sec)
    sunset_time = base_date + dt.timedelta(seconds = sunset_sec)
    
    