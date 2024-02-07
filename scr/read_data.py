import os

import json, codecs
import pandas as pd
import yaml

def read_model(cfg):
    path = cfg['path_models']
    lakename = cfg['lake']
    varfile = read_config('utils/config_varfile.yml')
    data = {}

    for modelname in cfg['model_names']:
        filecfg_sims = os.path.join(path, lakename, modelname, 'INPUTS', 'config_simstrat.par')
        cfg_sims = read_config(filecfg_sims)
        refyear = str(cfg_sims['Simulation']['Reference year'])
        datamodel = {}

        for var in cfg['var']:
            varf = varfile[var][0]
            newfile = '_'.join([lakename, varf])
            datafile = pd.read_csv(os.path.join(path, lakename, modelname, newfile))
            datafile['Datetime'] = pd.to_datetime(datafile.Datetime, origin=refyear, unit='D')
            datafile = datafile.set_index('Datetime')
            if '-0.000' in datafile.columns:
                datafile.rename(columns={'-0.000':'0.000'}, inplace=True)
            datamodel[var] = datafile[cfg['time_span'][0]:cfg['time_span'][1]]

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
    return conf_file

def read_hydro(filename):
    pass
