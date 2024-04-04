import codecs
import json
import os

import pandas as pd
from pandas._config import using_copy_on_write
import yaml


def read_data(cfg):
    modeldata = read_model(cfg)
    return modeldata

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
    if 'O_TEMPP' in cfg['var']:
        data_tp = pd.read_csv(os.path.join(path, cfg['file_wtempprof']))
        if 'date_complete' in data_tp.columns:
            data_tp.rename(columns={'date_complete': 'Datetime'}, inplace=True)
        data['Datetime'] = pd.to_datetime(data['Datetime'])
        data.update({'2D': {'O_TEMPP': data_tp}})
    
    if 'O_TEMP0' in cfg['var']:
        data_t0 = read_watertemp0(cfg)
        if '1D' not in data:
            data_t0 = {'O_TEMP0': data_t0}
            data.update({'1D': data_t0})
        else:
            data['1D']['O_TEMP0'] = data_t0
    if 'O_SD' in cfg['var']:
        data_sd = read_secchi(cfg)
        if '1D' not in data:
            data_sd = {'O_SD': data_sd}
            data.update({'1D': data_sd})
        else:
            data['1D']['O_SD'] = data_sd
    return data

def read_watertemp0(cfg):
    path = cfg['path_obs']
    data = pd.read_csv(os.path.join(path, cfg['file_wtempprof']), usecols=[2,4,5])
    data = data.loc[data.depth == 0]
    del data['depth']
    if 'date_complete' in data.columns:
        data.rename(columns={'date_complete': 'Datetime'}, inplace=True)
    data['Datetime'] = pd.to_datetime(data['Datetime'], format='%d/%m/%Y')
    data.sort_values(by='Datetime', inplace=True)
    data.set_index('Datetime', inplace=True)
    return data

def read_secchi(cfg):
    path = cfg['path_obs']
    data = pd.read_excel(os.path.join(path, cfg['file_secchi']), usecols=[3, 7])
    if 'date_complete' in data.columns:
        data.rename(columns={'date_complete': 'Datetime'}, inplace=True)
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
    var = [x for xs in var for x in xs]
    var = list(set(var))
    conf_file['var'] = var
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
