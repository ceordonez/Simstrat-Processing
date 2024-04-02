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
from scr.read_data import read_config, read_forcing, read_varconfig

import functions as fn
import plots as pl
import write as wr

plt.style.use('~/.config/matplotlib/aslo-paper.mplstyle')

PATHOUT ='/home/cesar/Dropbox/Cesar/PostDoc/Projects/WaterClarity/Simulations/INPUTS/HALLWIL/'
NAMEVAR = 'Solar radiation [W/m^2]'
VAR = 'I_RAD'

cfg = read_varconfig('../config_preprocessing.yml')

inputdata = read_forcing(cfg, 'Forcing.dat')
inputdata = inputdata.loc[:'31-12-2021']
inputdata = inputdata.rename(columns={NAMEVAR:VAR})

datam = inputdata[VAR].resample('ME').mean()
datay = inputdata[VAR].resample('YE').mean()

# Find tipping point using yearly average data
respt = ho.pettitt_test(datay)
loc = pd.to_datetime(respt.cp)

mu1 = respt.avg.mu1
mu2 = respt.avg.mu2

newdata = fn.normalize_data(inputdata, loc, VAR)
newdatam = newdata[VAR].resample('ME').mean()
mu3 = newdata.loc[loc:, VAR].mean()

# Find the tendency for the periods define with the pettitt test on montly data
PERIOD = 12
resst0 = mk.seasonal_test(datam, period=PERIOD)
resst1 = mk.seasonal_test(datam[:loc], period=PERIOD)
resst2 = mk.seasonal_test(datam[loc:], period=PERIOD)
resst3 = mk.seasonal_test(newdatam[loc:], period=PERIOD)

trend1 = np.arange(len(datam[:loc]))/PERIOD*resst1.slope + resst1.intercept
trend2 = np.arange(len(datam[loc:]))/PERIOD*resst2.slope + resst2.intercept

print('Trend entire period:', resst1.trend, 'Average:', inputdata.loc[:, VAR].mean())
print('Trend until:', loc, resst1.trend, 'Average:', inputdata.loc[:loc, VAR].mean())
print('Trend from:', loc, resst2.trend, 'Average:', inputdata.loc[loc:, VAR].mean())
print('New trend from:', loc, resst3.trend, 'Average:', newdata.loc[loc:, VAR].mean())

pl.plot_ts(inputdata, newdata, VAR, loc, respt, mu3, resst1, resst2, PERIOD, cfg)

wr.write_forcing(cfg, newdata, VAR, PATHOUT)
