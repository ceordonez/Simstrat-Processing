from datetime import datetime
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scr.read_data import read_config, read_model, read_inputs_meteo
from scr.plot_model import plot_model, ts_colormesh, plot_timeserie
from scr.processing_data import process_model
from scr.write_data import write_data

def main():

    cfg = read_config('config_plots.yml')
    #idata = read_inputs_meteo(cfg)
    modeldata = read_model(cfg)
    modeldata = process_model(cfg, modeldata)
    plot_model(cfg, modeldata)
    write_data(cfg, modeldata)

    #var = 'TEMP'
    #vmax = .4
    #vmin = -vmax
    #modeldata['DELTA_MODEL'] = {}
    #modeldata['DELTA_MODEL'][var] = modeldata[cfg['model_names'][0]][var] - modeldata[cfg['model_names'][1]][var]
    #ts_colormesh(modeldata, 'DELTA_MODEL', var, cmap='bwr', vmax=vmax, vmin=vmin)
    #plt.show()

if __name__ == "__main__":
    main()
