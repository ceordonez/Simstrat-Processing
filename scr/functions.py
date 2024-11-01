import logging
import pdb
import calendar
import collections
#from scipy import signal
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

def flatten(x):
    if isinstance(x, collections.abc.Iterable) and not isinstance(x, str):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]

def doy365(time):
    if type(time)!=list: time=[time]
    year = np.array([t.year for t in time])
    leapYear = np.logical_and(year%4==0,np.logical_or(year%100!=0,year%400==0))
    doy = np.array([t.dayofyear for t in time])
    doy[np.logical_and(leapYear,doy>59)] = doy[np.logical_and(leapYear,doy>59)]-1
    return (doy-1)

def N2(data):
    """Calculate Bouyancy frequency

    Parameters
    ----------
    data: DataFrame

    Returns
    -------
    Append N2 calculation to the data DataFrame
    """
    #rho, Temp, Z = filterProf(data, 0.25) # Mean every n meters
    alldata= []
    for date in data.index.unique():
        data_p = data.loc[date]
        data_p = data_p.sort_values('Depth_m')
        newdata_p = interp_temp(data_p, date)
        newdata_p['rho'] = waterDensity(newdata_p.O_TEMPP)
        newdata_p['dpdz'] = filter_dxdz(newdata_p.rho, newdata_p.Depth_m) # Savinsky Golay filter
        newdata_p['O_N2'] = (9.8/998.*newdata_p.dpdz)
        alldata.append(newdata_p)
    alldata = pd.concat(alldata)
    return alldata

def interp_temp(data_p, date):
    """Make profile interpolation.
    Profile is interpolate every 1m using the slinear method.

    Parameters
    ----------
    data_p: DataFrame
            Data profile at specific date
    date: String

    Returns
    -------
    DataFrame of the profile interpolated every 1m
    """

    newz = pd.Series(np.arange(0, data_p.Depth_m.max()+1, 1), name='Depth_m')
    newdata_p = pd.merge(data_p, newz, on='Depth_m', how='outer')
    newdata_p = newdata_p.set_index('Depth_m')
    newdata_p = newdata_p.interpolate(method='slinear')
    newdata_p.reset_index(inplace=True)
    newdata_p['Datetime'] = date
    newdata_p.set_index('Datetime', inplace=True)
    return newdata_p


def filter_dxdz(x, Z):
    dxdz = np.gradient(x, Z)
    #dxdz = signal.savgol_filter(dxdz, 9, 2)
    #__import__('pdb').set_trace()
    return dxdz

def clearSkySolRad(time, pair, vap, lat):
    if type(time) is not list: time=[time]
    vap = np.array(vap)
    lat = lat*np.pi/180
    hr = np.array([t.hour + t.minute/60 + t.second/3600 for t in time])
    doy = doy365(time) + hr/24
    doy_winter = doy + 10
    doy_winter[doy_winter>=365.24] = doy_winter[doy_winter>=365.24] - 365.24
    phi = np.arcsin(-0.39779*np.cos(2*np.pi/365.24*doy_winter)) #Declination of the sun (Wikipedia)
    cosZ = np.sin(lat)*np.sin(phi)+np.cos(lat)*np.cos(phi)*np.cos(np.pi/12*(hr-12.5)) #Cosine of the solar zenith angle (Wikipedia); 13.5 is the average solar noon (13h30)
    cosZ[cosZ<0] = 0
    m = 35*cosZ*(1244*cosZ**2+1)**-0.5 #Air mass thickness coefficient
    G = np.interp(doy,[15,105,196,288],[2.7,2.95,2.77,2.71]) #Empirical constant for latitudes 40-50°
    Td = (243.5*np.log(vap/6.112))/(17.67-np.log(vap/6.112))+33.8 #Dew point temperature [°C]
    pw = np.exp(0.1133-np.log(G+1)+0.0393*(1.8*Td+32)) #Precipitable water
    Tw = 1-0.077*(pw*m)**0.3 #Attenuation coefficient for water vapour
    Ta = 0.935**m #Attenuation coefficient for aerosols
    TrTpg = 1.021-0.084*(m*(0.000949*pair+0.051))**0.5 #Attenuation coefficient for Rayleigh scattering and permanent gases
    Ieff = 1353*(1+0.034*np.cos(2*np.pi/365.24*doy)) #Effective solar constant
    return Ieff*cosZ*TrTpg*Tw*Ta

def CH1903ptoLat(X,Y):
    y = float(X-2.6E6)/1E6
    x = float(Y-1.2E6)/1E6
    lat = (16.9023892 + 3.238272*x - 0.270978*y**2 - 0.002528*x**2 - 0.0447*y**2*x - 0.014*x**3)*100/36
    return lat

def roundTime(t,roundTo=60,floor=False,ceil=False):
    t = t.to_pydatetime()
    seconds = (t.replace(tzinfo=None)-t.min).seconds
    rounding = (seconds+(0 if floor else roundTo if ceil else roundTo/2))//roundTo * roundTo
    return (t + timedelta(0,rounding-seconds,-t.microsecond))

def timeAverage(tdata,data,period=24*60*60):
    t_round = [roundTime(t,period) for t in tdata]
    t_ceil = np.array([roundTime(t,period,ceil=True) for t in tdata])
    data_np = np.array(data)
    data_avg = [np.nan]*len(data)
    for tr in np.unique(t_round):
        data_avg[t_round.index(tr)] = np.nanmean(data_np[t_ceil==tr])
    return data_avg

def interpNaN(x,y,tgap,valdef=np.nan):
    if type(x[0]) in (datetime, pd.Timestamp):
        x = [calendar.timegm(t.timetuple()) for t in x]
    x = np.array(x)
    if np.any(np.diff(x)<0):
        raise Exception('Error: x-values for interpolation must be increasing. Interpolation not performed.')
    y = np.array(y)
    nans = np.isnan(y)
    #Find out length of NaN-series
    nanlims = np.diff(np.hstack(([0],nans*1,[0])))
    nanlen_short = np.where(nanlims<0)[0]-np.where(nanlims>0)[0]
    nanlen = np.zeros(len(nans))
    idx = 0
    wait = True
    for k in range(len(nans)):
        if nans[k]:
            nanlen[k] = nanlen_short[idx]
            wait = False
        elif not wait:
            idx = idx+1
            wait = True
    nans_rep = np.logical_and(nanlen>0,nanlen<tgap)
    y[nans_rep] = np.interp(x[nans_rep],x[~nans_rep],y[~nans_rep])
    if valdef=='mean': valdef=np.nanmean(y)
    nans = np.isnan(y)
    nans[0:list(nans).index(False)] = [False]*list(nans).index(False) #Don't replace the left-side NaNs
    y[nans] = valdef
    return y.tolist()

def cloudcover(data, lake):
    #Estimate cloudiness based on ratio between measured and theoretical solar radiation
    #writelog('\t\tEstimating missing cloud cover data based on theoretical and measured solar radiation.\n')
    cssr = clearSkySolRad(data.index, 1013.25*np.exp((-9.81*0.029*lake['Properties']['Elevation [m]'])/(8.314*283.15)), data['Vapour pressure [mbar]'], CH1903ptoLat(lake['X [m]'], lake['Y [m]']))
    #Better estimate by using daily averages, giving daily values for cloud cover (at noon)

    data['cssr'] = cssr[0]
    #solrad = np.array(timeAverage(data.index,data['Solar radiation [W/m^2]'].values,24*60*60))
    #cssr2 = np.array(timeAverage(data.index,cssr[0],24*60*60))
    cssr = data['cssr']#.resample('D').mean()
#    __import__('pdb').set_trace()
    solrad = data['Solar radiation [W/m^2]']#.resample('D').mean()
    #__import__('pdb').set_trace()
    dcloud = (1-solrad/(0.9*cssr))
    dcloud[dcloud<0] = 0
    dcloud.name = 'Cloud cover [-]'
    data = data.join(dcloud)
    data['Cloud cover [-]'] = data['Cloud cover [-]'].interpolate()
    __import__('pdb').set_trace()
    #cloud = interpNaN(data.index, data['Cloud cover [%]'].values, len(data))
    #data['Cloud cover [%]'] = np.nan
    #tsol = [calendar.timegm(t.timetuple()) for t in data.index]
    #nans = np.isnan(data['Cloud cover [%]'])
    #tnans = np.array([calendar.timegm(t.timetuple()) for t in data.index])[nans]
    #cc = np.array(data['Cloud cover [%]'])
    #cc[nans] = np.interp(tnans,tsol,cloud)
    #data['Cloud cover [%]'] = list(cc)
    ##Adapt units and perform basic checks
    #data['Cloud cover [%]'] = [cc*0.01 if not np.isnan(cc) else 0.5 for cc in data['Cloud cover [%]']]
    #data['Cloud cover [-]'] = data.pop('Cloud cover [%]')
    return data

def schmidtStability(data, bathy, vartemp, var):
    """Calculate Schmidt Stability based on Kirillin and Shatwell, 2016.

    Parameters
    ----------
    data: DataFrame
    bathy: Lake bathymetry
    vartemp: TODO
    var: TODO

    Returns
    -------
    TODO
    """

    dates = []
    data_st = []

    for date in data.index.unique():
        data_tp = data.loc[date]
        data_tp.reset_index(inplace=True)
        del data_tp['Datetime']
        data_aux = pd.merge(bathy, data_tp, how='outer', on='Depth_m')
        data_aux = data_aux.interpolate('slinear')
        data_aux = data_aux.interpolate('linear')
        depth = np.abs(data_aux.Depth_m.values)
        areas = data_aux.Area_m2.values
        temp = data_aux[vartemp].bfill(limit=1)
        temp = temp.values
        if 'O_SAL' not in data_tp.columns:
            sal = np.array([0]*len(data_aux))
        else:
            sal = data_tp['O_SAL'].values

        rho = waterDensity(temp, sal)
        volume = sum(midValue(areas)*np.abs(np.diff(depth))) #Lake volume from bathymetry [m3]
        depthv = 1/volume*sum(midValue(depth*areas)*np.abs(np.diff(depth))) #Centre of volume [m]
        sst = 9.81/max(areas)*sum(midValue((depth - depthv)*rho*areas)*np.abs(np.diff(depth))) #Schmidt stability [J/m^2] (e.g. Kirillin and Shatwell 2016)
        if sst != 0:
            sst = np.round(sst, decimals=4) #Round to 4 significant figures
        if np.isnan(sst):
            print('Check Schmidt Stability calclulations')
            pdb.set_trace()
        dates.append(date)
        data_st.append(sst)

    alldata = pd.DataFrame({'Datetime': dates, var:data_st})
    alldata.set_index('Datetime', inplace=True)
    return alldata

def heatContent(data, bathy, vartemp, var):
    dates = []
    data_st = []
    for date in data.index.unique():
        data_tp = data.loc[date]
        data_tp.reset_index(inplace=True)
        del data_tp['Datetime']
        data_aux = pd.merge(bathy, data_tp, how='outer', on='Depth_m')
        data_aux = data_aux.interpolate('slinear')
        data_aux = data_aux.interpolate('linear')
        z = data_aux.Depth_m
        areas = data_aux.Area_m2
        T = data_aux[vartemp]
        T = T.bfill(limit=1)
        T = T.values
        if 'O_SAL' not in data_tp.columns:
            S=[0]*len(data_aux)

        z,areas,T,S = (np.array(z),np.array(areas),np.array(T),np.array(S))
        rho = waterDensity(T,S)
        hc = sum(4183*midValue(areas*rho*T)*np.abs(np.diff(z))) #Heat content [J] (e.g. Weinberger and Vetter 2014)
        if hc!=0: hc=np.round(hc, decimals=4) #Round to 4 significant figures
        if np.isnan(hc): pdb.set_trace()
        dates.append(date)
        data_st.append(hc)
    alldata = pd.DataFrame({'Datetime': dates, var:data_st})
    alldata.set_index('Datetime', inplace=True)
    return alldata

def waterDensity(T,S=None):
    if S is None: S=[0]*len(T)
    T,S = (np.array(T),np.array(S))
    rho = 1000*(0.9998395+T*(6.7914e-5+T*(-9.0894e-6+T*(1.0171e-7+T*(-1.2846e-9+T*(1.1592e-11+T*(-5.0125e-14))))))+(8.181e-4+T*(-3.85e-6+T*(4.96e-8)))*S)#Density [kg/m3]
    return list(rho)

def midValue(vec):
    mid = (np.array(vec)[:-1]+np.array(vec)[1:])/2
    if type(vec) is list: mid = list(mid)
    return mid

def changename_avg(tavg):
    if tavg == 'M': tavg='MONTHLY'
    elif tavg == 'Y': tavg='YEARLY'
    elif tavg == 'YS': tavg='YEARLY_S'
    return tavg

