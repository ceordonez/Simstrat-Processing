
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pandas._libs.tslibs import period

import pymannkendall as mk
import pyhomogeneity as ho

from scr.read_data import read_hydro, read_lakemeta, read_meteo, read_config, read_forcing, read_varconfig
from scr.processing_data import processing_meteo
from scr.write_data import write_meteo, write_hydro
plt.style.use('~/.config/matplotlib/aslo-paper.mplstyle')

def main():
    cfg = read_varconfig('config_preprocessing.yml')
    inputdata = read_forcing(cfg, 'Forcing.dat')

    datam = inputdata.loc[:'31-12-2021','Solar radiation [W/m^2]'].resample('ME').mean()
    datay = inputdata.loc[:'31-12-2021','Solar radiation [W/m^2]'].resample('YE').mean()
    data = datay
    respt = ho.pettitt_test(data)
    loc = pd.to_datetime(respt.cp)

    period = 12
    resst1 = mk.seasonal_test(datam[:loc], period=period)
    resst2 = mk.seasonal_test(datam[loc:], period=period)
    print(resst2)
    trend1 = np.arange(len(datam[:loc]))/period*resst1.slope + resst1.intercept
    trend2 = np.arange(len(datam[loc:]))/period*resst2.slope + resst2.intercept

    mu1 = respt.avg.mu1
    mu2 = respt.avg.mu2

    ylabel = read_varconfig('utils/config_varfile.yml')
    fig, ax = plt.subplots(figsize=(5,3), layout='constrained')
    ax.plot(data, label='Observation')
    ax.plot(datam, label='', alpha=0.3, color='k')
    ax.plot(datam[:loc].index, trend1, color='g', label='Trend1')
    ax.plot(datam[loc:].index, trend2, color='orange', label='Trend2')
    ax.hlines(mu1, xmin=data.index[0], xmax=loc, linestyles='--', color='orange', label='mu1 : ' + str(round(mu1,2)))
    ax.hlines(mu2, xmin=loc, xmax=data.index[-1], linestyles='--', color='g', label='mu2 : ' + str(round(mu2,2)))
    ax.axvline(x=loc, linestyle='-.', color='r', label='Change point : '+ loc.strftime('%Y-%m-%d') + '\n p-value : ' + str(respt.p))
    ax.set_ylabel(ylabel['I_RAD'][1])
    figname = os.path.join(cfg['path_figures'],'PRE_PROSCESING')
    if not os.path.exists(figname):
        os.makedirs(figname)
    ax.legend()
    #fig.savefig(figname + '/Pettit_SolarRadiation.png', dpi=300)
    plt.show()
    __import__('pdb').set_trace()
    
    #__import__('pdb').set_trace()
    # STEP 1: Read data
    #metalake = read_lakemeta(cfg['meta_path'], cfg['meta_file'], cfg['lake'])
    #hydrodata = read_hydro(cfg['hydro_path'], cfg['hydro_file'], cfg['date_interval'])
    #meteodata = read_meteo(cfg['meteo_path'], cfg['meteo_file'], cfg['date_interval'])
    #write_hydro(cfg['output_path'], cfg['output_hydro'][3], hydrodata, cfg['date_interval'][0])

    ## STEP 2: Processing data
    meteodata = processing_meteo(meteodata, metalake)

    ### STEP 3: Write outputs
    write_meteo(cfg['output_path'], cfg['output_meteo'], meteodata, cfg['date_interval'][0])

if __name__ == "__main__":
    main()
