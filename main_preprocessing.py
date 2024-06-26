
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pandas._libs.tslibs import period


from scr.read_data import read_hydro, read_lakemeta, read_meteo, read_config, read_forcing, read_varconfig
from scr.processing_data import processing_meteo
from scr.write_data import write_meteo, write_hydro

def main():
    cfg = read_varconfig('config_preprocessing.yml')
    
    #__import__('pdb').set_trace()
    # STEP 1: Read data
    #metalake = read_lakemeta(cfg['meta_path'], cfg['meta_file'], cfg['lake'])
    #hydrodata = read_hydro(cfg['hydro_path'], cfg['hydro_file'], cfg['date_interval'])
    #meteodata = read_meteo(cfg['meteo_path'], cfg['meteo_file'], cfg['date_interval'])
    #write_hydro(cfg['output_path'], cfg['output_hydro'][3], hydrodata, cfg['date_interval'][0])

    data = read_forcing(cfg, 'Forcing.dat')
    __import__('pdb').set_trace()
    ## STEP 2: Processing data
    #meteodata = processing_meteo(meteodata, metalake)

    ### STEP 3: Write outputs
    #write_meteo(cfg['output_path'], cfg['output_meteo'], meteodata, cfg['date_interval'][0])

if __name__ == "__main__":
    main()
