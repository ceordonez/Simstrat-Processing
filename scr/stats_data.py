import logging
import os

import numpy as np
import pandas as pd
from sklearn.metrics import (mean_absolute_percentage_error, r2_score,
                             root_mean_squared_error)
import statsmodels.api as sm

from scr.functions import flatten
from scr.read_data import read_varconfig


def stats_data(cfg, obsdata, modeldata):

    rmse = []
    rmsec = []
    rmsen = []
    r2 = []
    mape = []
    var = []
    models = []
    pvalue = []
    bias = []
    std = []
    for varname in cfg['stats']['vars']:
        confvar = read_varconfig('utils/config_varfile.yml')
        obsvar = [x for x in varname if 'O' in x.split('_')][0]
        modelvar = [x for x in varname if 'O' not in x.split('_')][0]
        for modelname in modeldata:
            logging.info('Statistics for model: %s', modelname)
            if confvar[varname[0]][2] == '2D':
                y_obs = []
                y_mod = []
                for date in obsdata['2D']['ORG'].index.unique():
                    obsdatap = obsdata['2D']['ORG'].loc[date, ['Depth_m', obsvar]].dropna()
                    obsdatap.set_index('Depth_m', inplace=True)
                    modeldata_davg = modeldata[modelname]['2D']['ORG'][modelvar].resample('d').mean()
                    modeldatap = modeldata_davg.loc[date]
                    modeldatap = pd.DataFrame({modelvar:modeldatap.values}, index=modeldatap.index)
                    modeldatap.sort_index(inplace=True)
                    statdatap = pd.concat([obsdatap, modeldatap], axis=1).reindex(obsdatap.index).interpolate().sort_index()
                    y_obs.append(statdatap.values[:,0])
                    y_mod.append(statdatap.values[:,1])
            else:
                y_obs = obsdata['1D']['ORG'][obsvar].dropna()
                dates = obsdata['1D']['ORG'][obsvar].dropna().index
                tsmodel = modeldata[modelname]['1D']['ORG'].resample('d').mean()
                y_mod = tsmodel.loc[dates, modelvar]


            y_obs = np.array(flatten(y_obs))
            y_mod = np.array(flatten(y_mod))
            rmse.append(root_mean_squared_error(y_obs, y_mod))
            mape.append(mean_absolute_percentage_error(y_obs, y_mod))
            rmsec.append(root_mean_squared_error(y_obs - np.mean(y_obs), y_mod - np.mean(y_mod)))
            rmsen.append(root_mean_squared_error(y_obs, y_mod)/np.sqrt(1/len(y_mod)*np.sum(y_mod**2)))
            r2.append(r2_score(y_obs, y_mod))
            mod = sm.OLS(y_obs, y_mod).fit()
            pvalue.append(mod.pvalues[0])
            bias.append(np.mean(y_obs) - np.mean(y_mod))
            std.append(np.sqrt(np.sum((y_obs - np.mean(y_obs))**2)/ np.sum((y_mod - np.mean(y_mod))**2)))
            var.append(varname)
            models.append(modelname)

    statres = pd.DataFrame({'Model':models, 'Variable':var, 'RMSE': rmse, 'RMSEn': rmsen, 'RMSEc':rmsec, 'BIAS': bias, 'Std':std, 'MAPE': mape, 'R2': r2, 'p-value': pvalue})
    return statres
