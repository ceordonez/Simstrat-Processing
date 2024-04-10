
import os
import logging
import matplotlib.pyplot as plt

from scr.read_data import read_varconfig
from scr.functions import changename_avg
from scr.plot_save import savefigure

def plot_timeseries(cfg, obsdata, modeldata, path_figures, save=True):

    ylabel = read_varconfig('utils/config_varfile.yml')
    varnames = cfg['plot']['timeseries']
    dataobsplot = []
    datamodplot = []
    allvars = cfg['timeaverage']
    allvars.append('ORG')
    for tavg in allvars:
        tavg = changename_avg(tavg)
        for var in varnames:
            if isinstance(var, list):
                logging.info('Plotting %s %s observation and with all models', tavg, '-'.join(var))
                fig, ax = plt.subplots(figsize=(6,3), layout='constrained')
                for var2 in var:
                    if 'O' in var2.split('_'):
                        dataobsplot = obsdata['1D'][tavg][var2]
                        make_ts(cfg, ax, dataobsplot, 'Obs.', ylabel[var2][1], tavg, 'OBS')
                    else:
                        plot_ts_allmodel(modeldata, tavg, var2, ylabel[var2][1], ax)
                ax.legend()
                namefig = '_'.join(['TS', cfg['lake'], '_'.join([*modeldata.keys()]), '_'.join(var), tavg])
                savefigure(cfg, path_figures, fig, namefig, 'MODEL_OBS/TIME_SERIES', save)
            else:
                if 'O' in var.split('_'):
                    logging.info('Plotting obs data: %s, %s', tavg, var)
                    dataplot = obsdata['1D'][tavg][var]
                    fig, ax = plt.subplots(figsize=(6,3), layout='constrained')
                    make_ts(cfg, ax, dataplot, '', ylabel[var][1], tavg, 'OBS')
                    namefig = '_'.join(['TS', cfg['lake'], tavg, var])
                    savefigure(cfg, path_figures, fig, namefig, 'OBSERVATIONS/TIME_SERIES', save)
                else:
                    plotvar = '1M'
                    for modelname in modeldata:
                        logging.info('Plotting model name: %s, %s, %s', modelname, tavg, var)
                        dataplot = modeldata[modelname]['1D'][tavg][var]
                        fig, ax = plt.subplots(figsize=(6,3), layout='constrained')
                        make_ts(cfg, ax, dataplot, modelname, ylabel[var][1], tavg, plotvar)
                        namefig = '_'.join(['TS', cfg['lake'], modelname, tavg, var])
                        pathmodel = os.path.join('MODELS', modelname, 'TIME_SERIES')
                        savefigure(cfg, path_figures, fig, namefig, pathmodel, save)

                    if len(modeldata.keys())>1:
                        logging.info('Plotting all models together for: %s, %s', tavg, var)
                        namefig = '_'.join(['TS', cfg['lake'], '_'.join([*modeldata.keys()]), var, tavg])
                        fig, ax = plt.subplots(figsize=(6,3), layout='constrained')
                        plot_ts_allmodel(modeldata, tavg, var, ylabel[var][1], ax)
                        ax.legend()
                        savefigure(cfg, path_figures, fig, namefig, 'ALLMODELS/TIME_SERIES', save)

def plot_ts_allmodel(modeldata, tavg, var, ylabel, ax):
    for modelname in modeldata:
        modeldata[modelname]['1D'][tavg][var].plot(label=modelname, ax=ax)
    ax.set_ylabel(ylabel)

def make_ts(cfg, ax, data, label, ylabel, tavg, td='MODEL'):

    ax.set_title(tavg)
    ln = '-'
    mk = None
    if tavg != 'ORG':
        mk = 'o'

    if td == 'OBS':
        ln = '--'
        cc = 'k'
        mk = '.'

    data.plot(ax=ax, label=label, marker=mk, linestyle=ln)
    if cfg['date_periods']:
        ax.axvline(x=cfg['date_periods'][0], color='r', linestyle='-.')
        ax.axvline(x=cfg['date_periods'][1], color='r', linestyle='-.')
    ax.set_ylabel(ylabel)
