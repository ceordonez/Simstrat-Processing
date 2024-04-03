
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
def write_absorption(cfg, data, path, filename):
    #fid.write('Time [d], Q_in [m3/s]\n')
    pathin = cfg['paths']['models']
    lakename = cfg['lake']
    modelname = cfg['modelname']
    filecfg_sims = os.path.join(pathin, lakename, modelname, 'INPUTS', 'config_simstrat.par')
    cfg_sims = read_varconfig(filecfg_sims)
    refyear = str(cfg_sims['Simulation']['Reference year'])

    fid = open(os.path.join(path, filename + '.dat'),'w',encoding='utf-8')
    fid.write('Time [d] (1.col) z[m] (1.row) Absorption [m-1] (rest)\n')
    fid.write('1\n')
    fid.write('-1, 0.00\n')
    fid.close()

    basedate = pd.to_datetime(refyear)
    data['Time [d]'] = (data.index - basedate).total_seconds()/(60*60*24)
    wdata = data.loc[:, ['Time [d]', 'I_KL']]
    wdata.to_csv(os.path.join(path, filename + '.dat'), mode='a', index=False, header=False, float_format='%.3f')
