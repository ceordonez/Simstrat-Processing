import codecs
import json
import logging
import os

import pandas as pd
import yaml
from pandas._config import using_copy_on_write

from scr.functions import N2, flatten, schmidtStability


def read_obs(cfg):
    """Read observation data.

    Parameters
    ----------
    cfg : TODO

    Returns
    -------
    TODO

    """
    data = {}
    list_temp1d = ['O_TEMP0', 'O_TEMPB', 'O_MN2', 'O_ST', 'O_HC']
    list_temp2d = ['O_TEMPP', 'O_N2']
    # Adding 2D variables (not finished)
    if any(map(lambda x: x in cfg['var'], list_temp2d)):
        data_tp = read_watertemp(cfg)
        if 'O_TEMPP' in cfg['var']:
            logging.info('Reading O_TEMPP')
            data = add2ddata(data, data_tp)
        if 'O_N2' in cfg['var']:
            logging.info('Reading O_N2')
            data_n2 = N2(data_tp)
            data = add2ddata(data, pd.DataFrame(data_n2[['O_N2', 'Depth_m']]))
        data['2D'] = data['2D'].loc[cfg['time_span'][0]:cfg['time_span'][1]]

    # Adding 1D variables
    if any(map(lambda x: x in cfg['var'], list_temp1d)):
        data_t = read_watertemp(cfg)

        if 'O_TEMP0' in cfg['var']:
            logging.info('Reading O_TEMP0')
            data_t0 = data_t.loc[data_t.Depth_m == 0].copy()
            if 'temperature' in data_t.columns:
                data_t0.rename(columns={'O_TEMPP': 'O_TEMP0'}, inplace=True)
            del data_t0['Depth_m']
            data = add1ddata(data, data_t0)

        if 'O_ST' in cfg['var']:
            logging.info('Reading O_ST')
            area = read_bathymetry(cfg)
            data_st = schmidtStability(data_t, area, 'O_ST')
            data = add1ddata(data, data_st)

        if 'O_MN2' in cfg['var']:
            logging.info('Reading O_MN2')
            data_n2 = N2(data_t)
            data_mn2 = data_n2.groupby('Datetime')['O_N2'].max()
            data_mn2 = pd.DataFrame(data_mn2)
            data_mn2.rename(columns={'O_N2': 'O_MN2'}, inplace=True)
            data = add1ddata(data, data_mn2)

    if 'O_SD' in cfg['var']:
        logging.info('Reading O_SD')
        data_sd = read_secchi(cfg)
        data = add1ddata(data, data_sd)

    # Average duplicated measurements
    if '1D' in data:
        if len(data['1D'].duplicated()) > 0:
            data['1D'] = data['1D'].groupby(data['1D'].index).mean()
        data['1D'].sort_index(inplace=True)
        data['1D'] = data['1D'].loc[cfg['time_span'][0]:cfg['time_span'][1]]
    return data


def filter_dxdz(x, Z):
    dxdz = np.gradient(x, Z)
    dxdz = signal.savgol_filter(dxdz, 9, 2)
    return dxdz# }}}

def add2ddata(data, datavar):
    if '2D' not in data:
        data.update({'2D': datavar})
    else:
        data['2D'].reset_index(inplace=True)
        data['2D'].set_index(['Datetime', 'Depth_m'], inplace=True)
        datavar.reset_index(inplace=True)
        datavar.set_index(['Datetime', 'Depth_m'], inplace=True)
        data['2D'] = pd.merge(data['2D'], datavar, how='outer', left_index=True, right_index=True)
        data['2D'].reset_index(inplace=True)
        data['2D'].set_index('Datetime', inplace=True)
    return data

def add1ddata(data, datavar):
    if '1D' not in data:
        data.update({'1D': datavar})
    else:
        data['1D'] = pd.merge(data['1D'], datavar, how='outer', left_index=True, right_index=True)
    return data

def read_watertemp(cfg):
    path = cfg['path_obs']
    data = pd.read_csv(os.path.join(path, cfg['file_wtempprof']), usecols=[2,4,5])
    if 'date_complete' in data.columns:
        data.rename(columns={'date_complete': 'Datetime', 'depth': 'Depth_m', 'temperature': 'O_TEMPP'}, inplace=True)
    data['Datetime'] = pd.to_datetime(data['Datetime'], format='%d/%m/%Y')
    data.sort_values(by='Datetime', inplace=True)
    data.set_index('Datetime', inplace=True)
    return data

def read_secchi(cfg):
    path = cfg['path_obs']
    data = pd.read_excel(os.path.join(path, cfg['file_secchi']), usecols=[3, 7])
    if 'date_complete' in data.columns:
        data.rename(columns={'date_complete': 'Datetime'}, inplace=True)
    if 'Secchi' in data.columns:
        data.rename(columns={'Secchi': 'O_SD'}, inplace=True)
    data['Datetime'] = pd.to_datetime(data['Datetime'])
    data.sort_values(by='Datetime', inplace=True)
    data.set_index('Datetime', inplace=True)
    return data

def read_model(cfg):

    path = cfg['path_models']
    lakename = cfg['lake']
    varfile = read_varconfig('utils/config_varfile.yml')

    data = {}

    for modelname in cfg['model_names']:
        filecfg_sims = os.path.join(path, lakename, modelname, 'INPUTS', 'config_simstrat.par')
        cfg_sims = read_varconfig(filecfg_sims)
        refyear = str(cfg_sims['Simulation']['Reference year'])
        datamodel = {}
        var1d_first = True
        for var in cfg['var']:
            if 'O' not in var.split('_'):
                varf = varfile[var][0]
                if 'I' in var.split('_'):
                    filename = os.path.join(path, lakename, modelname, 'INPUTS', varf)
                    if varf == 'Forcing.dat':
                        alldatafile = pd.read_csv(filename, sep='\s+')
                        alldatafile.rename(columns={'Time [d]':'Datetime'}, inplace=True)
                        if var == 'I_RAD':
                            datafile = alldatafile.loc[:,['Datetime', 'Solar radiation [W/m^2]']]
                        if var == 'I_VAP':
                            datafile = alldatafile.loc[:,['Datetime', 'Vapour pressure [mbar]']]
                    else:
                        datafile = pd.read_csv(filename, skiprows=3, sep='\s+', names=['Datetime',var])
                else:
                    newfile = '_'.join([lakename, varf])
                    filename = os.path.join(path, lakename, modelname, newfile)
                    datafile = pd.read_csv(filename)
                datafile['Datetime'] = pd.to_datetime(datafile.Datetime, origin=refyear, unit='D')
                datafile = datafile.set_index('Datetime')
                if '-0.000' in datafile.columns:
                    datafile.rename(columns={'-0.000':'0.000'}, inplace=True)
                if varfile[var][2] == '1D':
                    datafile.rename(columns={datafile.columns[0]:var}, inplace=True)
                    if var1d_first:
                        datamodel['1D'] = pd.DataFrame(datafile[cfg['time_span'][0]:cfg['time_span'][1]])
                        var1d_first = False
                    else:
                        datamodel['1D'] = pd.concat([datamodel['1D'], datafile[cfg['time_span'][0]:cfg['time_span'][1]]], axis=1, join='outer')
                if varfile[var][2] == '2D':
                    datamodel['2D'] = {}
                    datamodel['2D'][var] = datafile[cfg['time_span'][0]:cfg['time_span'][1]]
        #datamodel['1D'].sort_index(inplace=True)
        data[modelname] = datamodel

    return data

def read_meteo(path, filename, date_interval):
    #data = pd.read_excel(os.path.join(path, filename), skiprows=2)
    data = pd.read_csv(os.path.join(path, filename), skiprows=3, sep=';', na_values='-', parse_dates=[0], usecols=[1,2,3,4,5,7,8], date_format='%Y%m%d%H', names=['Station', 'Datetime', 'Vapour pressure [mbar]', 'Solar radiation [W/m^2]', 'Temperature [degC]', 'Precipitation [mm/h]', 'RH [%]', 'WindVel [m/s]', 'WindDir [degN]', 'Pressure [hPa]'] )
    data.set_index('Datetime', inplace=True)
    return data[date_interval[0]:date_interval[1]]

def read_lakemeta(path, filename, lake):
    lakesfile = os.path.join(path, filename)
    lakes = json.load(codecs.open(lakesfile,'r','utf-8'))
    metalake = []
    for ilake in lakes:
        if ilake['Name'] == lake:
            metalake = ilake
            break
    return metalake

def read_config(filename):
    with open(filename, 'r') as file:
        conf_file = yaml.safe_load(file)

    var = []
    for plottype in conf_file['plot']:
        if plottype not in ['figformat', 'save']:
            var.append(conf_file['plot'][plottype])
    #var = [x for xs in var for x in xs]
    #var = list(set(var))
    conf_file['var'] = flatten(var)
    return conf_file

def read_varconfig(filename):
    with open(filename, 'r') as file:
        conf_var = yaml.safe_load(file)
    return conf_var

def read_hydro(path, filename, date_interval):
    data = pd.read_csv(os.path.join(path, filename), sep=';', skiprows=9, usecols=[6,8], names=['Datetime', 'Q_in [m3/s]'])
    data['Datetime'] = pd.to_datetime(data.Datetime)
    data.set_index('Datetime', inplace=True)
    return data[date_interval[0]:date_interval[1]]

def read_inputs_meteo(cfg):
    path = cfg['paths']['models']
    filename = cfg['input_file']
    lakename = cfg['lake']
    varfile = read_varconfig('utils/config_varfile.yml')
    idata = {}
    for modelname in cfg['model_names']:
        filecfg_sims = os.path.join(path, lakename, modelname, 'INPUTS', 'config_simstrat.par')
        cfg_sims = read_varconfig(filecfg_sims)
        refyear = str(cfg_sims['Simulation']['Reference year'])
        datamodel = {}
        data = pd.read_csv(os.path.join(path, lakename, modelname, 'INPUTS', filename +'.dat'), sep=' ')
        data['Datetime'] = pd.to_datetime(data['Time [d]'], origin=refyear, unit='D')
        data.set_index('Datetime', inplace=True)
        idata[modelname] = data

    return idata

def read_forcing(cfg, filename):
    """TODO: Docstring for read_forcing.

    Parameters
    ----------
    cfg: TODO
    file : TODO

    Returns
    -------
    TODO

    """

    path = cfg['paths']['models']
    lakename = cfg['lake']
    modelname = cfg['modelname']
    filecfg_sims = os.path.join(path, lakename, modelname, 'INPUTS', 'config_simstrat.par')
    cfg_sims = read_varconfig(filecfg_sims)
    refyear = str(cfg_sims['Simulation']['Reference year'])
    filename = os.path.join(cfg['paths']['input'], cfg['lake'], filename)
    data= pd.read_csv(filename, sep='\s+')
    data.rename(columns={'Time [d]':'Datetime'}, inplace=True)
    data['Datetime'] = pd.to_datetime(data.Datetime, origin=refyear, unit='D')
    data= data.set_index('Datetime')

    return data

def read_absorption(cfg, filename):
    path = cfg['paths']['models']
    lakename = cfg['lake']
    modelname = cfg['modelname']
    filecfg_sims = os.path.join(path, lakename, modelname, 'INPUTS', 'config_simstrat.par')
    cfg_sims = read_varconfig(filecfg_sims)
    refyear = str(cfg_sims['Simulation']['Reference year'])
    filename = os.path.join(cfg['paths']['input'], cfg['lake'], filename)
    data= pd.read_csv(filename, sep='\s+', skiprows=3, names=['Datetime', 'I_KL'])
    data['Datetime'] = pd.to_datetime(data.Datetime, origin=refyear, unit='D')
    data= data.set_index('Datetime')
    return data

def read_bathymetry(cfg):
    path = cfg['path_obs']
    data = pd.read_csv(os.path.join(path, cfg['file_bathymetry']), sep='\s+', skiprows=1, names=['Depth_m', 'Area_m2'])
    data['Depth_m'] = -1*data['Depth_m']
    return data
