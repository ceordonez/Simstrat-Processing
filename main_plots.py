from datetime import datetime
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import logging

from scr.logging_conf import logging_conf
from scr.read_data import read_config, read_model, read_inputs_meteo, read_obs
from scr.plot_data import plot_data
from scr.processing_data import process_data
from scr.write_data import write_data

def main():

    #idata = read_inputs_meteo(cfg)

    logging_conf()
    logging.info('STEP 0: READING CONFIGURATION FILES')
    cfg = read_config('config_plots.yml')
    logging.info('STEP 1: READING OBS FILES')
    obsdata = read_obs(cfg)
    logging.info('STEP 2: READING MODELS')
    modeldata = read_model(cfg)
    logging.info('STEP 3: PROCESSING')
    obsdata, modeldata = process_data(cfg, obsdata, modeldata)
    logging.info('STEP 4: PLOTTING DATA')
    plot_data(cfg, obsdata, modeldata)
    logging.info('STEP 5: WRITING RESULTS')
    __import__('pdb').set_trace()
    write_data(cfg, modeldata)

if __name__ == "__main__":
    main()
