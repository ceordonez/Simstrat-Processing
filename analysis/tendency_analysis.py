
import os
import sys

script_dir = os.path.dirname(__file__)
scr_dir = os.path.join(script_dir, '..')
sys.path.append(scr_dir)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyhomogeneity as ho
import pymannkendall as mk
#from pandas._libs.tslibs import period
from scr.read_data import read_config, read_forcing, read_varconfig

plt.style.use('~/.config/matplotlib/aslo-paper.mplstyle')

cfg = read_varconfig('../config_preprocessing.yml')
inputdata = read_forcing(cfg, 'Forcing.dat')

datam = inputdata.loc[:'31-12-2021','Solar radiation [W/m^2]'].resample('ME').mean()
datay = inputdata.loc[:'31-12-2021','Solar radiation [W/m^2]'].resample('YE').mean()

# Find tipping point using yearly average data
respt = ho.pettitt_test(datay)
loc = pd.to_datetime(respt.cp)

__import__('pdb').set_trace()
# Find the tendency for the periods define with the pettitt test on montly data
period = 12
resst1 = mk.seasonal_test(datam[:loc], period=period)
resst2 = mk.seasonal_test(datam[loc:], period=period)
sens1 = mk.sens_slope(datam[:loc])
sens2 = mk.sens_slope(datam[loc:])
trend1 = np.arange(len(datam[:loc]))/period*resst1.slope + resst1.intercept
trend2 = np.arange(len(datam[loc:]))/period*resst2.slope + resst2.intercept
__import__('pdb').set_trace()

mu1 = respt.avg.mu1
mu2 = respt.avg.mu2

ylabel = read_varconfig('../utils/config_varfile.yml')
fig, ax = plt.subplots(figsize=(6,4), layout='constrained')
ax.plot(datay, label='Observation')
ax.plot(datam, label='', alpha=0.3, color='k')
ax.plot(datam[:loc].index, trend1, color='orange', label='Trend1')
ax.plot(datam[loc:].index, trend2, color='g', label='Trend2')
ax.hlines(mu1, xmin=datay.index[0], xmax=loc, linestyles='--', color='orange', label='mu1 : ' + str(round(mu1,2)))
ax.hlines(mu2, xmin=loc, xmax=datay.index[-1], linestyles='--', color='g', label='mu2 : ' + str(round(mu2,2)))
ax.axvline(x=loc, linestyle='-.', color='r', label='Change point : '+ loc.strftime('%Y-%m-%d') + '\n p-value : ' + str(respt.p))
ax.set_ylabel(ylabel['I_RAD'][1])
figname = os.path.join(cfg['path_figures'],'PRE_PROSCESING')
if not os.path.exists(figname):
    os.makedirs(figname)
ax.legend(ncols=2)
#fig.savefig(figname + '/Pettit_SolarRadiation.png', dpi=300)
plt.show()
