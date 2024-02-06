
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import scr.functions as fn
from scr.read_data import read_lakemeta, read_meteo, read_config
from scr.write_data import write_meteo

#METEO_FILE = 'Meteo_LUZ_1985_2000.xlsx'


def main():
    cfg = read_config('config_meteoforcing.yml')
    metalake = read_lakemeta(cfg['meta_path'], cfg['meta_file'], cfg['lake'])
    meteodata = read_meteo(cfg['meteo_path'], cfg['meteo_file'], cfg['date_interval'])
    meteodata = fn.cloudcover(meteodata, metalake)
    meteodata['U [m/s]'] = meteodata['WindVel [m/s]']*np.cos(meteodata['WindDir [degN]'])
    meteodata['V [m/s]'] = meteodata['WindVel [m/s]']*np.sin(meteodata['WindDir [degN]'])
    write_meteo(cfg['output_path'], cfg['output_file'], meteodata, cfg['date_interval'][0])

if __name__ == "__main__":
    main()
