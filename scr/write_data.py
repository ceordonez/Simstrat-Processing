import os
import logging
import pandas as pd

def write_data(cfg, obsdata, modeldata, statdata):
    """Write process data.

    Parameters
    ----------
    cfg : TODO
    obsdata : TODO
    modeldata : TODO

    Returns
    -------
    TODO

    """

    if cfg['write']['model']:
        write_modeldata(cfg, modeldata)
    if cfg['write']['stats']:
        write_stats(cfg, statdata)
    if cfg['write']['obs']:
        write_obsdata(cfg, obsdata)

def write_obsdata(cfg, obsdata):
    """TODO: Docstring for write_obsdata.

    Parameters
    ----------
    arg1 : TODO

    Returns
    -------
    TODO

    """
    if '1D' in obsdata:
        for tavg in obsdata['1D']:
            filename = '_'.join([cfg['lake'], 'OBS', '1D', tavg])
            if not os.path.exists(cfg['path_outfiles']):
                os.makedirs(cfg['path_outfiles'])
            filename = os.path.join(cfg['path_outfiles'], filename +'.csv')
            if cfg['write']['append-o']:
                if os.path.exists(filename):
                    olddata = pd.read_csv(filename, index_col=[0], parse_dates=[0])
                    newdata = obsdata['1D'][tavg]
                    mergedata = append1d_data(olddata, newdata)
                    mergedata.to_csv(filename, index=False, float_format='%.3f')
                else:
                    logging.warning('No file for observation at % freq.', tavg)
                    logging.warning('Creating new file')
                    obsdata['1D'][tavg].reset_index(inplace=True)
                    obsdata['1D'][tavg].to_csv(filename, index=False, float_format='%.3f')
            else:
                obsdata['1D'][tavg].reset_index(inplace=True)
                obsdata['1D'][tavg].to_csv(filename, index=False, float_format='%.3f')


def write_modeldata(cfg, modeldata):

    for model in modeldata:
        if '1D' in modeldata[model]:
            logging.info('Writing model 1D data for model: %s', model)
            for tavg in modeldata[model]['1D']:
                filename = '_'.join([cfg['lake'], model, tavg])
                if not os.path.exists(cfg['path_outfiles']):
                    os.makedirs(cfg['path_outfiles'])
                filename = os.path.join(cfg['path_outfiles'], filename +'.csv')
                if cfg['write']['append-m']:
                    if os.path.exists(filename):
                        olddata = pd.read_csv(filename, index_col=[0], parse_dates=[0])
                        newdata = modeldata[model]['1D'][tavg]
                        mergedata = append1d_data(olddata, newdata)
                        mergedata.to_csv(filename, index=False, float_format='%.3f')
                    else:
                        logging.warning('No file for model %s at % freq.', model, tavg)
                        logging.warning('Creating new file')
                        modeldata[model]['1D'][tavg].reset_index(inplace=True)
                        modeldata[model]['1D'][tavg].to_csv(filename, index=False, float_format='%.3f')
                else:
                    modeldata[model]['1D'][tavg].reset_index(inplace=True)
                    modeldata[model]['1D'][tavg].to_csv(filename, index=False, float_format='%.3f')

def append1d_data(olddata, newdata):
    dupcol = olddata.columns.isin(newdata.columns)
    if all(dupcol):
        mergedata = newdata
    else:
        nolddata = olddata.drop(olddata.columns[dupcol], axis=1)
        mergedata = pd.merge(nolddata, newdata, left_index=True, right_index=True, how='outer')
    mergedata.reset_index(inplace=True)
    return mergedata

def write_stats(cfg, statdata):
    if not os.path.exists(cfg['path_outfiles']):
        os.makedirs(cfg['path_outfiles'])
    filename = 'STATISTICS'
    filename = os.path.join(cfg['path_outfiles'],filename +'.csv')
    if cfg['write']['append-s']:
        statdata.to_csv(filename, index=False, float_format='%.4f', mode='a')
    else:
        statdata.to_csv(filename, index=False, float_format='%.4f')


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

