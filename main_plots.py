from datetime import datetime
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scr.read_data import read_config, read_model, read_inputs_meteo, read_obs
from scr.plot_data import plot_data
from scr.processing_data import process_data
from scr.write_data import write_data

def main():

    cfg = read_config('config_plots.yml')
    #idata = read_inputs_meteo(cfg)
    obsdata = read_obs(cfg)
    modeldata = read_model(cfg)
    obsdata, modeldata = process_data(cfg, obsdata, modeldata)
    plot_data(cfg, obsdata, modeldata)
    __import__('pdb').set_trace()
    write_data(cfg, modeldata)

if __name__ == "__main__":
    main()
