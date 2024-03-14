import os
import matplotlib.pyplot as plt
import numpy as np

from scr.read_data import read_varconfig, read_varconfig

plt.style.use('~/.config/matplotlib/aslo-paper.mplstyle')

def plot_model(cfg, modeldata):

    path_figures = os.path.join(cfg['path_models'],cfg['lake'], 'FIGURES')
    if not os.path.exists(path_figures):
        os.makedirs(path_figures)

    for plottype in cfg['plot']:
        if plottype == 'colormesh':
            if cfg['plot']['colormesh']:
                print('making colormesh plot')
                plot_colormesh(cfg, modeldata, cfg['plot'][plottype], path_figures)
        if plottype == 'timeseries':
            if cfg['plot']['timeseries']:
                plot_timeserie(cfg, modeldata, cfg['plot']['timeseries'], path_figures)



def plot_colormesh(cfg, modeldata, plotvars, path_figures):

    cblabel = read_varconfig('utils/config_varfile.yml')
    for modelname in modeldata:
        path_figmodel = os.path.join(path_figures, modelname)
        for varname in plotvars:
            fig = ts_colormesh(modeldata, modelname, varname, cblabel)
            if not os.path.exists(path_figmodel):
                os.makedirs(path_figmodel)
            namefig = '_'.join(['CM', cfg['lake'], modelname, varname])
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

def plot_timeserie(cfg, data, variables, path_figures):
    ylabel = read_varconfig('utils/config_varfile.yml')
    for var in variables:
        for modelname in data:
            fig, ax = plt.subplots(figsize=(6,3), layout='constrained')
            ax.plot(data[modelname][var].index, data[modelname][var], label=modelname)
            ax.set_ylabel(ylabel[var][1])
            path_figmodel = os.path.join(path_figures, modelname)
            if not os.path.exists(path_figmodel):
                os.makedirs(path_figmodel)
            namefig = '_'.join(['TS', cfg['lake'], modelname, var])
            fig.savefig(os.path.join(path_figmodel, namefig) + '.' + cfg['plot']['figformat'], format=cfg['plot']['figformat'])

    if len(data.keys())>1:
        for var in variables:
            fig, ax = plt.subplots(figsize=(6,3), layout='constrained')
            for modelname in data:
                ax.plot(data[modelname][var].index, data[modelname][var], label=modelname)
            ax.set_ylabel(ylabel[var][1])
            ax.legend()
            namefig = '_'.join(['TS', cfg['lake'], data.keys(), var])
            fig.savefig(os.path.join(path_figures, namefig) + '.' + cfg['plot']['figformat'], format=cfg['plot']['figformat'])
