import os
import matplotlib.pyplot as plt
import numpy as np

from scr.read_data import read_varconfig, read_varconfig

plt.style.use('~/.config/matplotlib/aslo-paper.mplstyle')

def plot_data(cfg, obsdata, modeldata):

    if modeldata:
        plot_model(cfg, modeldata)
    if obsdata:
        plot_obsdata(cfg, obsdata)

def plot_obsdata(cfg, obsdata):
    """TODO: Docstring for plot_obsdata.

    Parameters
    ----------
    cfg : TODO
    obsdata : TODO

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
                    plot_colormesh(cfg, obsdata, cfg['plot'][plottype], path_figures, save)
            if plottype == 'timeseries':
                if cfg['plot']['timeseries']:
                    plot_obstimeserie(cfg, obsdata, cfg['plot']['timeseries'], path_figures, save)
        if not save:
            plt.show()

def plot_obstimeserie(cfg, data, variables, path_figures, save=True):

    ylabel = read_varconfig('utils/config_varfile.yml')
    for tavg in data['1D']:
        for var in data['1D'][tavg]:
            dataplot = data['1D'][tavg][var]
            fig = make_ts(cfg, dataplot, var, '', ylabel, tavg, 'OBS')
            path_figmodel = os.path.join(path_figures, 'OBSERVATIONS')
            if not os.path.exists(path_figmodel):
                os.makedirs(path_figmodel)
            namefig = '_'.join(['TS', cfg['lake'], tavg, var])
            if save:
                figfile = os.path.join(path_figmodel, namefig) + '.' + cfg['plot']['figformat']
                fig.savefig(figfile, format=cfg['plot']['figformat'])
                plt.close()


def plot_model(cfg, modeldata):
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
                    plot_modeltimeserie(cfg, modeldata, cfg['plot']['timeseries'], path_figures, save)
        if not save:
            plt.show()


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

def make_ts(cfg, data, var, label, ylabel, tavg, td='MODEL'):
    fig, ax = plt.subplots(figsize=(6,3), layout='constrained')
    ax.set_title(tavg)
    mk = '.'
    ln = '-'
    if tavg != 'ORG':
        mk = 'o'
    if td == 'OBS':
        ln = '--'
    data.plot(ax=ax, label=label, marker=mk, linestyle=ln)
    if cfg['date_periods']:
        ax.axvline(x=cfg['date_periods'][0], color='r', linestyle='-.')
        ax.axvline(x=cfg['date_periods'][1], color='r', linestyle='-.')
    ax.set_ylabel(ylabel[var][1])
    return fig

def plot_modeltimeserie(cfg, data, variables, path_figures, save=True):
    ylabel = read_varconfig('utils/config_varfile.yml')
    for var in variables:
        for modelname in data:
            for tavg in data[modelname]['1D']:
                dataplot = data[modelname]['1D'][tavg][var]
                fig = make_ts(cfg, dataplot, var, modelname, ylabel, tavg)
                path_figmodel = os.path.join(path_figures, modelname)
                if not os.path.exists(path_figmodel):
                    os.makedirs(path_figmodel)
                namefig = '_'.join(['TS', cfg['lake'], modelname, tavg, var])
                if save:
                    figfile = os.path.join(path_figmodel, namefig) + '.' + cfg['plot']['figformat']
                    fig.savefig(figfile, format=cfg['plot']['figformat'])
                    plt.close()

    if len(data.keys())>1:
        tavgs = cfg['timeaverage']
        tavgs.append('ORG')
        for var in variables:
            for tavg in tavgs:
                fig, ax = plt.subplots(figsize=(6,3), layout='constrained')
                if tavg == 'Y': tavg='YEARLY'
                elif tavg == 'M': tavg='MONTHLY'
                for modelname in data:
                    data[modelname]['1D'][tavg][var].plot(label=modelname)
                ax.set_ylabel(ylabel[var][1])
                ax.legend()
                namefig = '_'.join(['TS', cfg['lake'], '_'.join([*data.keys()]), var, tavg])
                fig.savefig(os.path.join(path_figures, namefig) + '.' + cfg['plot']['figformat'], format=cfg['plot']['figformat'])
                plt.close()
