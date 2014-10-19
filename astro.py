import functions as fn
import constants as cn
import datetime as dt
    
def test_tamil_date():
    input_params = fn.get_input()
    d, m, y = fn.calc_tamil_date(input_params["in_datetime"])
    print d
    print m
    print y
    
    
    