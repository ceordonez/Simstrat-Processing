import os
import matplotlib.pyplot as plt
import numpy as np

from scr.read_data import read_config

def plot_model(cfg, modeldata):
    for plottype in cfg['plot']:
        if plottype == 'colormesh':
            if cfg['plot']['colormesh']:
                print('making colormesh plot')
                plot_colormesh(modeldata, cfg['plot'][plottype])
        if plottype == 'timeseries':
            if cfg['plot']['timeseries']:
                plot_timeserie(modeldata, cfg['plot']['timeseries'])



def plot_colormesh(modeldata, plotvars):
    for modelname in modeldata:
        for varname in plotvars:
            ts_colormesh(modeldata, modelname, varname)

def ts_colormesh(modeldata, modelname, varname, cmap='viridis', vmax=None, vmin=None):

    data = modeldata[modelname][varname]

    fig, ax = plt.subplots()
    ax.set_title(modelname)
    x = data.index.values
    y = data.columns.values.astype(float)
    X, Y = np.meshgrid(x, y)
    pc = ax.pcolormesh(X, Y, data.T, cmap=cmap, vmax=vmax, vmin=vmin)
    ax.set_ylabel('Depth (m)')
    cblabel = read_config('utils/config_varfile.yml')
    fig.colorbar(pc, ax=ax, label=cblabel[varname][1])

def plot_timeserie(data, variables):
    for modeldata in data:
        for var in variables:
            fig, ax = plt.subplots(figsize=(6,3), constrained_layout=True)
            ax.plot(data[modeldata][var].index, data[modeldata][var], label=modeldata)
            ylabel = read_config('utils/config_varfile.yml')
            ax.set_ylabel(ylabel[var][1])
    plt.show()

