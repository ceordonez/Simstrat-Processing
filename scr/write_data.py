from operator import index
import os

import pandas as pd

def write_meteo(path, filename, data, basedate):
    basedate = pd.to_datetime(basedate)
    data['Time [d]'] = (data.index - basedate).total_seconds()/(60*60*24)
    data.reset_index(inplace=True)
    wdata = data.loc[:, ['Time [d]', 'U [m/s]', 'V [m/s]', 'Temperature [degC]', 'Solar radiation [W/m^2]', 'Vapour pressure [mbar]', 'Cloud cover [-]', 'Precipitation [m/h]']]
    wdata.to_csv(os.path.join(path, filename),index=False, float_format='%.3f')

def write_hydro(path, filename, data, basedate):
    fid = open(os.path.join(path, filename),'w',encoding='utf-8')
    #fid.write('Time [d], Q_in [m3/s]\n')
    fid.write('Time [d], Q_out [m3/s]\n')
    fid.write('0, 1\n')
    fid.write('-1, 0\n')
    fid.close()
    basedate = pd.to_datetime(basedate)
    data['time [d]'] = (data.index - basedate).total_seconds()/(60*60*24)
    data['Q_in [m3/s]'] = 1000# data['Q_in [m3/s]'] * 0
    print(filename)
    wdata = data.loc[:, ['time [d]', 'Q_in [m3/s]']]
    wdata.to_csv(os.path.join(path, filename), mode='a', index=False, header=False, float_format='%.3f')
    #for it in range(len(data['Flowrate [m^3/s]']['Time'])):
    #    if not np.isnan(data['Flowrate [m^3/s]']['Data'][it]):
    #        fid.write('%10.4f' % daydiff(data['Flowrate [m^3/s]']['Time'][it],tref))
    #        fid.write(' %9.4f' % data['Flowrate [m^3/s]']['Data'][it])
    #        fid.write('\n')
    #fid.close()

def write_data(cfg, data):
    """Write process data

    Parameters
    ----------
    cfg : TODO
    data : TODO

    Returns
    -------
    TODO

    """
    if cfg['writedata']:
        for model in data:
            if '1D' in data[model]:
                for tavg in data[model]['1D']:
                    var = '_'.join(data[model]['1D'][tavg].columns)
                    filename = '_'.join([cfg['lake'],model,tavg, var])
                    if not os.path.exists(cfg['path_outfiles']):
                        os.makedirs(cfg['path_outfiles'])
                    filename = os.path.join(cfg['path_outfiles'],filename +'.csv')
                    data[model]['1D'][tavg].reset_index(inplace=True)
                    data[model]['1D'][tavg].to_csv(filename, index=False, float_format='%.3f')
