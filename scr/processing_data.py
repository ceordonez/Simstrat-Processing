
import numpy as np
import pandas as pd

import scr.functions as fn


def processing_meteo(data, meta):

    # Calculates wind V and U
    data['U [m/s]'] = -data['WindVel [m/s]']*np.cos(data['WindDir [degN]']*np.pi/180)
    data['V [m/s]'] = -data['WindVel [m/s]']*np.sin(data['WindDir [degN]']*np.pi/180)

    # Estimate cloud cover if there are no measurements
    data = fn.cloudcover(data, meta)
    return data

def processing_hydro(data, meta):
    return []

def cond2sal(cond):
    K1 =  0.0120
    K2 = -0.2174
    K3 = 25.3283
    K4 = 13.7714
    K5 = -6.4788
    K6 =  2.5842
    R = np.array(cond)/53087
    sal = K1 + K2*R**0.5 + K3*R + K4*R**1.5 + K5*R**2 + K6*R**2.5
    sal = np.round(sal,3)
    return (list(sal) if (type(cond) is list) else sal)
