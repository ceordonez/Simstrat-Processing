
import numpy as np
import pandas as pd

import scr.functions as fn


def processing_meteo(data, meta):

    # Calculates wind V and U
    data.interpolate(inplace=True) # linearly interpolate Nan values
    data.loc[data['WindVel [m/s]'].isnull(), 'WindVel [m/s]'] = data['WindVel [m/s]'].mean()
    data.loc[data['WindDir [degN]'].isnull(), 'WindDir [degN]'] = data['WindDir [degN]'].mean()
    data['U [m/s]'] = -data['WindVel [m/s]']*np.sin(data['WindDir [degN]']*np.pi/180)
    data['V [m/s]'] = -data['WindVel [m/s]']*np.cos(data['WindDir [degN]']*np.pi/180)
    data['Precipitation [m/h]'] = data['Precipitation [mm/h]']/1000
    del data['Precipitation [mm/h]']
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
