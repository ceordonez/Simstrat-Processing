import os
import collections
import logging
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scr.read_data import read_varconfig
from scr.functions import changename_avg
from scr.plot_save import savefigure
from scr.plot_timeseries import plot_timeseries

plt.style.use('~/.config/matplotlib/aslo-paper.mplstyle')

def plot_data(cfg, obsdata, modeldata):
    """TODO: Docstring for plot_obsdata.

    Parameters
    ----------
    cfg : TODO
    obsdata : TODO
    modeldata : TODO

    Returns
    -------
    TODO

    """
    if cfg['makeplots']:
        save = cfg['plot']['save']
        path_figures = os.path.join(cfg['path_figures'], cfg['lake'])
        if not os.path.exists(path_figures):
            os.makedirs(path_figures)
        for plottype in cfg['plot']:
            if plottype == 'colormesh':
                if cfg['plot']['colormesh']:
                    plot_colormesh(cfg, modeldata, cfg['plot'][plottype], path_figures, save)
            if plottype == 'timeseries':
                if cfg['plot']['timeseries']:
                    logging.info('Plotting time series')
                    plot_timeseries(cfg, obsdata, modeldata, path_figures, save)
            if plottype == 'profiles':
                if cfg['plot']['profiles']:
                    plot_profiles(cfg, obsdata, modeldata, path_figures, save)
        if not save:
            plt.show()

def plot_profiles(cfg, obsdata, modeldata, path, save):
    """Make profile figure with one or two variables.

    Parameters
    ----------
    cfg : Configuration information
    obsdata : Dictionary with observation
    modeldata : Dictionary model data
    path : path where figures are saved
    save : bool. True is figure are save. False they are going to be shown

    Returns
    -------
    None
    """
    varnames = cfg['plot']['profiles']
    if '2D' in obsdata.keys():
        for tavg in obsdata['2D']:
            for date in obsdata['2D'][tavg].index.unique():
                strdate = date.strftime('%d-%m-%Y')
                for varname in varnames:
                    if isinstance(varname, str) or all('O' in x.split('_') for x in varname):
                        logging.info('Plotting observation profiles at %s for %s', strdate, varname)
                        datap = obsdata['2D'][tavg].loc[date].set_index('Depth_m')
                        fig, ax = plt.subplots(1, 1, figsize=(3.2, 4.0))
                        make_profile(ax, datap.loc[:, varname], '', strdate, varname, 'obs')
                        if isinstance(varname, list):
                            varname = '_'.join(varname)
                        namefig = '_'.join(['WP', cfg['lake'], tavg, varname, date.strftime('%Y%m%d')])
                        savefigure(cfg, path, fig, namefig, 'OBSERVATIONS/PROFILES', save)
                    else:
                        obsvar = [x for x in varname if 'O' in x.split('_')][0]
                        modelvar = [x for x in varname if 'O' not in x.split('_')][0]
                        logging.info('Plotting observation versus all models profile of %s on date %s', varname, strdate)
                        dataobsp = obsdata['2D'][tavg].loc[date, ['Depth_m', obsvar]].set_index('Depth_m')
                        fig, ax = plt.subplots(1, 1, figsize=(3.2, 4.0))
                        for i, modelname in enumerate(modeldata):
                            datemodeldata = modeldata[modelname]['2D'][tavg][modelvar].loc[date]
                            datemodp = pd.DataFrame({modelvar: datemodeldata.values}, index=datemodeldata.index.astype(float))
                            plotdata = pd.merge(datemodp, dataobsp, how='outer', left_index=True, right_index=True)
                            ax.plot(datemodp, datemodp.index, label=modelname)
                        make_profile(ax, dataobsp, '', strdate, obsvar, 'mix')
                        ax.legend()
                        namefig = '_'.join(['WP', cfg['lake'], '_'.join([*modeldata.keys()]), tavg, '_'.join(varname), date.strftime('%Y%m%d')])
                        savefigure(cfg, path, fig, namefig, 'MODEL_OBS/PROFILES', save)
                __import__('pdb').set_trace()

def make_profile(ax, data, label, date, var, typ):

    xlabel = read_varconfig('utils/config_varfile.yml')

    ccs = plt.rcParams['axes.prop_cycle'].by_key()['color']
    ax.invert_yaxis()
    ax.set_title('Date: ' + date)
    ax.set_ylabel('Depth (m)')

    ln1 = '-'
    mk = '.'
    label1 = None
    cc = ccs[1]

    if typ == 'mix':
        ln1 = '--'
        mk = None
        label1 = 'Obs.'

    if isinstance(var, list):
        data1 = data[var[0]].dropna()
        ax.plot(data1, data1.index, label=label1, marker='.', color=ccs[0], linestyle=ln1)
        ax.set_xlabel(xlabel[var[0]][1])
        if xlabel[var[0]][1] == xlabel[var[1]][1]:
            data2 = data[var[1]].dropna()
            ax.plot(data2, data2.index, label=label, marker=mk, color=cc)
        else:
            twy = ax.twiny()
            data2 = data[var[1]].dropna()
            lnty, = twy.plot(data2, data2.index, label=label, marker='.', color=cc)
            twy.set_xlabel(xlabel[var[1]][1])
            twy.spines.top.set_visible(True)
            twy.xaxis.label.set_color(lnty.get_color())
            twy.spines.top.set_color(lnty.get_color())
            twy.tick_params(axis='x', colors=lnty.get_color(), which='both')
    else:
        ax.plot(data, data.index, label=label1, marker='.', color=ccs[0], linestyle=ln1)
        ax.set_xlabel(xlabel[var][1])

def plot_colormesh(cfg, modeldata, plotvars, path_figures, save=True):

    cblabel = read_varconfig('utils/config_varfile.yml')
    for modelname in modeldata:
        path_figmodel = os.path.join(path_figures, modelname)
        for varname in plotvars:
            fig = ts_colormesh(modeldata, modelname, varname, cblabel)
            if not os.path.exists(path_figmodel):
                os.makedirs(path_figmodel)
            namefig = '_'.join(['CM', cfg['lake'], modelname, varname])
            if save:
                fig.savefig(os.path.join(path_figmodel, namefig) + '.' + cfg['plot']['figformat'], format=cfg['plot']['figformat'])

def ts_colormesh(modeldata, modelname, varname, cblabel, cmap='viridis', vmax=None, vmin=None):

    data = modeldata[modelname][varname]
    fig, ax = plt.subplots(figsize=(6,4), layout='constrained')
    ax.spines[['top','right']].set_visible(True)
    ax.set_title(modelname)
    x = data.index.values
    y = data.columns.values.astype(float)
    X, Y = np.meshgrid(x, y)
    pc = ax.pcolormesh(X, Y, data.T, cmap=cmap, vmax=vmax, vmin=vmin)
    ax.set_ylabel('Depth (m)')
    fig.colorbar(pc, ax=ax, label=cblabel[varname][1])
    return fig
