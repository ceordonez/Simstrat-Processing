
import os

import pandas as pd

from scr.read_data import read_varconfig

def write_forcing(cfg, data, var, pathout):
    pathin = cfg['paths']['models']
    lakename = cfg['lake']
    modelname = cfg['modelname']
    filecfg_sims = os.path.join(pathin, lakename, modelname, 'INPUTS', 'config_simstrat.par')
    cfg_sims = read_varconfig(filecfg_sims)
    refyear = str(cfg_sims['Simulation']['Reference year'])

    data = data.rename(columns={var: 'Solar radiation [W/m^2]'})
    basedate = pd.Timestamp('-'.join([refyear, '01', '01']))
    data.reset_index(inplace=True)
    data['Time [d]'] = (data['Datetime'] - basedate).dt.total_seconds()/(60*60*24)
    columns = list(data.columns)
    columns.remove('Time [d]')
    columns.insert(0, 'Time [d]')
    data = data[columns]
    del data['Datetime']

    #data.to_csv(os.path.join(pathout, 'Forcing_NoBright.dat'), index=False, sep=' ', float_format='%.4f')
