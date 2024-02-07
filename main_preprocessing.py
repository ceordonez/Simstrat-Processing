
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from scr.read_data import read_lakemeta, read_meteo, read_config
from scr.processing_data import processing_meteo
from scr.write_data import write_meteo

def main():
    cfg = read_config('config_preprocessing.yml')

    ## STEP 1: Read data
    metalake = read_lakemeta(cfg['meta_path'], cfg['meta_file'], cfg['lake'])
    meteodata = read_meteo(cfg['meteo_path'], cfg['meteo_file'], cfg['date_interval'])


    ## STEP 2: Processing data
    meteodata = processing_meteo(meteodata, metalake)

    ## STEP 3: Write outputs
    write_meteo(cfg['output_path'], cfg['output_meteo'], meteodata, cfg['date_interval'][0])

if __name__ == "__main__":
    main()
