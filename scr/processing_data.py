
import numpy as np
import pandas as pd

import scr.functions as fn
from scr.read_data import read_varconfig


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

def process_model(cfg, modeldata):
    """Process model data

    Parameters
    ----------
    cfg : TODO
    modeldata : TODO

    Returns
    -------
    TODO

    """
    if cfg['timeaverage']:
        data = {}
        for model in modeldata:
            if '1D' in modeldata[model]:
                data = {model: {'1D': {}}}
            if '2D' in modeldata[model]:
                data = {model: {'2D': {}}}
            for time_avg in cfg['timeaverage']:
                if '1D' in modeldata[model]:
                    data[model]['1D'].update({'ORG':modeldata[model]['1D']})
                    if time_avg == 'M':
                        avgdata = modeldata[model]['1D'].resample('ME').mean()
                        data[model]['1D'].update({'MONTHLY': avgdata})
                    if time_avg == 'Y':
                        avgdata = modeldata[model]['1D'].resample('YE').mean()
                        data[model]['1D'].update({'YEARLY': avgdata})
                if '2D' in modeldata[model]:
                    for var in modeldata['2D']:
                        data[model]['2D'].update({'ORG':modeldata[model]['2D']})
                        if time_avg == 'M':
                            avgdata = modeldata[model]['2D'][var].resample('ME').mean()
                            data[model]['2D'] = {'MONTHLY': {var: avgdata}}
                        if time_avg == 'Y':
                            avgdata = modeldata[model]['2D'][var].resample('YE').mean()
                            data[model]['2D'] = {'YEARLY': {var: avgdata}}
        return data
    else:
        return modeldata

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
