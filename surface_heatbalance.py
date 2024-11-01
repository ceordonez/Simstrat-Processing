
import os
import pandas as pd
import matplotlib.pyplot as plt
from scr.read_data import read_forcing, read_varconfig, read_config, read_obs
import numpy as np

#import scr.functions as fn
OBS_PATH = '/home/cesar/Dropbox/Cesar/PostDoc/Projects/WaterClarity/Simulations/OUTFILES'
OBS_FILENAME = 'HALLWIL_OBS_1D_ORG.csv'

def main():
    cfg = read_varconfig('config_preprocessing.yml')
    cfg2 = read_config('config_plots.yml')
    lakedata = read_obs(cfg2)
    data = read_forcing(cfg, 'Forcing.dat')
    data['WS_ms'] = np.sqrt(data['U [m/s]']**2 + data['V [m/s]'])
    data = data.resample('ME').mean()
    lakedata = lakedata['1D'].resample('ME').mean()
    data = pd.concat([data, lakedata['O_TEMP0']], axis=1)
    print(data.columns)
    #data['WS10c_ms'] = data['WS10_ms']*0.515
    data = swrad_in(data, cfg['latitude'])
    data = sat_vaporpress(data)
    data = transfer_function(data)
    data = psychrometric_constant(data)
    __import__('pdb').set_trace()
    #data =.vapor_pressure(data)
    data = atm_emmissivity(data)
    data = absorved_lw(data)
    data = emmited_lw(data)
    data = latent_heat(data)
    data = sensible_heat(data)
    data = heat_balance(data)
    #data.to_csv('Results_heat_budget_Soppen.csv', date_format='%d-%m-%Y %H:%M', float_format='%0.2f')
def swrad_in(data, lat):
    """Calculate solar radiation.
    """
    data['Rad_out_Wm2'] = 0
    data['Albedo'] = albedo(data, lat)
    data.loc[data['Solar radiation [W/m^2]'] < 5, 'Solar radiation [W/m^2]'] = 0
    data['Rad_out_Wm2'] = data['Solar radiation [W/m^2]']*data['Albedo']
    data['Hs_Wm2'] = data['Solar radiation [W/m^2]'] - data['Rad_out_Wm2']
    return data

def declination(data):
    """Calculate solar declination (Goyette).

    Parameters
    ----------
    data: TODO

    Returns
    -------
    Solar declination in radians
    """
    julday = data.index.day_of_year.values
    dec = 23.45*np.sin(2*np.pi*(284 + julday-1)/365.25)
    return dec*np.pi/180

def zenit(data, dec, lat):
    """Calculate solar Zenit angle.

    Parameters
    ----------
    data: TODO
    dec : Solar declination in radians
    lat : Latitude (deg N)

    Returns
    -------
    Zenit angle in radians
    """
    hangle = (data.index.hour.values + data.index.minute.values/60)*360/24*np.pi/180
    cos_z = np.sin(lat*np.pi/180)*np.sin(dec) + np.cos(lat*np.pi/180)*np.cos(dec)*np.cos(hangle)
    z_angle = np.arccos(cos_z)*np.pi/180
    return z_angle

def albedo(data, lat):
    """Calculate albedo for water surface (Goyette).

    Parameters
    ----------
    data: TODO
    lat: Latitude (deg N)

    Returns
    -------
    Albedo (fraction)
    """
    dec = declination(data)
    z_angle = zenit(data, dec, lat)
    alb = 0.05/(np.cos(z_angle) + 0.15)
    return alb


def atm_emmissivity(data):
    A1 = 0.98
    A2 = 0.17
    A3 = 1.24
    atemp_k = data['Temperature [degC]'] + 273.15
    data['AtmEmi'] = A1*(1 + A2*data['Clouds_Tot']**2)*A3*(data['ew_hPa']/atemp_k)**(1/7)
    return data

def absorved_lw(data):
    A1 = 0.03 # Reflection of IR from water surface
    sigma = 5.67E-8 #[Wm-2K-4]
    atemp_k = data['Temperature [degC]'] + 273.15
    data['Ha_Wm2'] = (1-A1)*data['AtmEmi']*sigma*atemp_k**4
    return data

def emmited_lw(data):
    A1 = 0.972 #LW water emmissivity
    sigma = 5.67E-8 #[Wm-2K-4]
    wtemp_k = data['Tsw_degC'] + 273.15
    data['Hw_Wm2'] = -A1*sigma*wtemp_k**4
    return data

def sat_vaporpress(data):
    A1 = 6.112
    A2 = 17.62
    A3 = 243.12
    data['ew_hPa'] = A1*np.exp((A2*data['O_TEMP0'])/(A3 + data['O_TEMP0']))
    return data

def transfer_function(data):
    A1 = 4.8
    A2 = 1.98
    A3 = 0.28
    f1 = A1 + A2*data['WS_ms'] + A3*(data['O_TEMP0'] - data['Temperature [degC]'])
    data['f1_Wm-2hPa-1'] = -f1
    return data

def latent_heat(data):
    #data['He_Wm2'] = -f1*(data['SatVP_hPa'] - data['VaporPress_hPa'])
    data['He_Wm2'] = -data['f1_Wm-2hPa-1']*(data['ew_hPa'] - data['ea_hPa']) ##CHECK THIS EQUATION IN THE PAPER!!!!
    return data

def psychrometric_constant(data):
    CP = 1005 # Air heat capacity [J Kg'1 K-1] at 20degC
    LV = 2.47E6 # Latent heat of vaporization [JKg-1]
    MV = 0.622 # MV ratio
    data['psychro_hPaK-1']= CP*data['AirPress_hPa']/(LV*MV)
    return data

def sensible_heat(data):

    data['Hc_Wm2'] = -data['psychro_hPaK-1']*data['f1_Wm-2hPa-1']*(data['Tsw_degC'] - data['Temperature [degC]'])
    return data


def heat_balance(data):
    data['Hnet_Wm2'] = data['Hs_Wm2'] + data['Ha_Wm2'] + data['Hw_Wm2'] + data['He_Wm2'] + data['Hc_Wm2']
    return data

if __name__ == "__main__":
    main()
