
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
                ## Figure with all models together
                fig, ax = plt.subplots(figsize=(6,3), layout='constrained')
                obsvar = [x for x in var if 'O' in x.split('_')][0]
                modelvar = [x for x in var if 'O' not in x.split('_')][0]
                dataobsplot = obsdata['1D'][tavg][obsvar]
                make_ts(cfg, ax, dataobsplot, 'Obs.', ylabel[obsvar][1], tavg, 'OBS')
                plot_ts_allmodel(modeldata, tavg, modelvar, ylabel[modelvar][1], ax)
                ax.legend()
                namefig = '_'.join(['TS', cfg['lake'], '_'.join([*modeldata.keys()]), '_'.join(var), tavg])
                savefigure(cfg, path_figures, fig, namefig, 'MODEL_OBS/TIME_SERIES', save)
                ## Figure per model
                plot_per_model(cfg, modeldata, dataobsplot, tavg, modelvar, ylabel, '1O', path_figures, save)
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
                    plot_per_model(cfg, modeldata, '', tavg, var, ylabel, plotvar, path_figures, save)
                    if len(modeldata.keys())>1:
                        logging.info('Plotting all models together for: %s, %s', tavg, var)
                        namefig = '_'.join(['TS', cfg['lake'], '_'.join([*modeldata.keys()]), var, tavg])
                        fig, ax = plt.subplots(figsize=(6,3), layout='constrained')
                        plot_ts_allmodel(modeldata, tavg, var, ylabel[var][1], ax)
                        ax.legend()
                        savefigure(cfg, path_figures, fig, namefig, 'ALLMODELS/TIME_SERIES', save)

def plot_ts_allmodel(modeldata, tavg, var, ylabel, ax):
    for modelname in modeldata:
        modelplotdata = modeldata[modelname]['1D'][tavg][var].dropna()
        modelplotdata.plot(label=modelname, ax=ax)
    ax.set_ylabel(ylabel)

def plot_per_model(cfg, modeldata, obsdata, tavg, var, ylabel, plotvar, path_figures, save):

    for modelname in modeldata:
        logging.info('Plotting model name: %s, %s, %s', modelname, tavg, var)
        dataplot = modeldata[modelname]['1D'][tavg][var].dropna()
        fig, ax = plt.subplots(figsize=(6,3), layout='constrained')
        make_ts(cfg, ax, dataplot, modelname, ylabel[var][1], tavg, 'MODEL')
        namefig = '_'.join(['TS', cfg['lake'], modelname, tavg, var])
        if plotvar == '1O':
            make_ts(cfg, ax, obsdata, 'Obs.', ylabel[var][1], tavg, 'OBS')
            ax.legend()
        pathmodel = os.path.join('MODELS', modelname, 'TIME_SERIES')
        savefigure(cfg, path_figures, fig, namefig, pathmodel, save)

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
    if td == 'MODEL':
        mk = None

    data.plot(ax=ax, label=label, marker=mk, linestyle=ln)
    if cfg['date_periods']:
        ax.axvline(x=cfg['date_periods'][0], color='r', linestyle='-.')
        ax.axvline(x=cfg['date_periods'][1], color='r', linestyle='-.')
    ax.set_ylabel(ylabel)
