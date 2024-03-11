import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scr.read_data import read_config, read_model
from scr.plot_model import plot_model, ts_colormesh, plot_timeserie

def main():

    cfg = read_config('config_plots.yml')

    modeldata = read_model(cfg)
    plot_model(cfg, modeldata)

    var = 'TEMP'
    vmax = .4
    vmin = -vmax
    modeldata['DELTA_MODEL'] = {}
    modeldata['DELTA_MODEL'][var] = modeldata[cfg['model_names'][0]][var] - modeldata[cfg['model_names'][1]][var]
    ts_colormesh(modeldata, 'DELTA_MODEL', var, cmap='bwr', vmax=vmax, vmin=vmin)
    plt.show()
    __import__('pdb').set_trace()



if __name__ == "__main__":
    main()
