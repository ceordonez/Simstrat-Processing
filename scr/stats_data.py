import os
import logging
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from scr.read_data import read_varconfig
from scr.functions import flatten

def stats_data(cfg, obsdata, modeldata):

    for varname in cfg['stats']['vars']:
        confvar = read_varconfig('utils/config_varfile.yml')
        obsvar = [x for x in varname if 'O' in x.split('_')][0]
        modelvar = [x for x in varname if 'O' not in x.split('_')][0]
        if confvar[varname[0]][2] == '2D':
            data = []
            y_obs = []
            y_mod = []
            for modelname in modeldata:
                logging.info('Statistics for model: %s', modelname)
                for date in obsdata['2D']['ORG'].index.unique():
                    obsdatap = obsdata['2D']['ORG'].loc[date, ['Depth_m', obsvar]]
                    obsdatap.set_index('Depth_m', inplace=True)
                    modeldata_davg = modeldata[modelname]['2D']['ORG'][modelvar].resample('d').mean()
                    modeldatap = modeldata_davg.loc[date]
                    modeldatap = pd.DataFrame({modelvar:modeldatap.values}, index=modeldatap.index)
                    statdatap = pd.concat([obsdatap, modeldatap], axis=1).reindex(obsdatap.index).interpolate().sort_index()
                    ## CHECH FOR NANs
                    y_obs.append(statdatap.values[:,0])
                    y_mod.append(statdatap.values[:,1])

                y_obs = flatten(y_obs)
                y_mod = flatten(y_mod)
                rmse = mean_squared_error(y_obs, y_mod)
                mae = mean_absolute_error(y_obs, y_mod)
                r2 = r2_score(y_obs, y_mod)
                __import__('pdb').set_trace()
