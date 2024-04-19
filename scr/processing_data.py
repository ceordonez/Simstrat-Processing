
import numpy as np
import pandas as pd

import scr.functions as fn
from scr.read_data import read_varconfig


def process_data(cfg, obsdata, modeldata):

    if obsdata:
        obsdata = process_obsdata(cfg, obsdata)
    if modeldata:
        modeldata = process_model(cfg, modeldata)
    return obsdata, modeldata

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

def process_obsdata(cfg, obsdata):
    data = {}
    if '1D' in obsdata:
        data['1D'] = {'ORG': obsdata['1D']}
        #interp = obsdata['1D'].resample('D').interpolate(method='linear')
    if '2D' in obsdata:
        data['2D'] = {'ORG': obsdata['2D']}
    if cfg['timeaverage']:
        for time_avg in cfg['timeaverage']:
            if '1D' in obsdata:
                indata = obsdata['1D']
                data['1D'] = average1D(indata, data['1D'], time_avg)
            if '2D' in obsdata:
                pass
    return data


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
    data = {}
    for model in modeldata:
        modeldic = {model: {}}
        if '1D' in modeldata[model]:
            dic1d = {'1D': {'ORG': modeldata[model]['1D']}}
            modeldic[model].update(dic1d)
            data.update(modeldic)
        if '2D' in modeldata[model]:
            dic2d = {'2D': {'ORG': modeldata[model]['2D']}}
            modeldic[model].update(dic2d)
            data.update(modeldic)
        if cfg['timeaverage']:
            for time_avg in cfg['timeaverage']:
                if '1D' in modeldata[model]:
                    indata = modeldata[model]['1D']
                    data[model]['1D'] = average1D(indata, data[model]['1D'], time_avg)
                if '2D' in modeldata[model]:
                    for var in modeldata[model]['2D']:
                        if time_avg == 'M':
                            avgdata = modeldata[model]['2D'][var].resample('ME').mean()
                            data[model]['2D'].update({'MONTHLY': {var: avgdata}})
                        if time_avg == 'Y':
                            avgdata = modeldata[model]['2D'][var].resample('YE').mean()
                            data[model]['2D'].update({'YEARLY': {var: avgdata}})
    return data

def average1D(indata, outdata, time_avg):
    if time_avg == 'M':
        avgdata = indata.resample('ME').agg(['mean', 'std'])
        outdata.update({'MONTHLY': avgdata})
    if time_avg == 'Y':
        avgdata = indata.resample('YE').agg(['mean', 'std'])
        outdata.update({'YEARLY': avgdata})
    if time_avg == 'YS':
        mindata= indata.resample('ME').mean().interpolate()
        avgdata = mindata.resample('YE').sum()
        outdata.update({'YEARLY_S': avgdata})
    return outdata

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
