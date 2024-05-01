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
#VAR = 'I_RAD'
#NAMEVAR = 'Solar radiation [W/m^2]'
#NORMPERIOD = ''
#VAR = 'I_VAP'
#NAMEVAR = 'Vapour pressure [mbar]'
#NORMPERIOD = ''
VAR = 'I_ATEMP'
NAMEVAR = 'Temperature [degC]'
NORMPERIOD = 'all'
SEASON = 'WINTER'

cfg = read_varconfig('../config_preprocessing.yml')

inputdata = read_forcing(cfg, 'Forcing.dat')
inputdata = inputdata.loc[:'31-12-2021']
inputdata = inputdata.rename(columns={NAMEVAR:VAR})

inputdata = fn.select_season(inputdata, SEASON)

datam = inputdata[VAR].resample('ME').mean()
datay = inputdata[VAR].resample('YE').mean()

# Find tipping point using yearly average data
respt = ho.pettitt_test(datay)
loc = pd.to_datetime(respt.cp)

mu1 = respt.avg.mu1
mu2 = respt.avg.mu2

newdata = fn.normalize_data(inputdata, loc, VAR, NORMPERIOD)
__import__('pdb').set_trace()
newdatam = newdata[VAR].resample('ME').mean()
newdatay = newdata[VAR].resample('YE').mean()
mu3 = newdata.loc[loc:, VAR].mean()

# Find the tendency for the periods define with the pettitt test on montly data
if SEASON == '':
    PERIOD = 12
    resst0 = mk.seasonal_test(datam, period=PERIOD)
    resst1 = mk.seasonal_test(datam[:loc], period=PERIOD)
    resst2 = mk.seasonal_test(datam[loc:], period=PERIOD)
    resst3 = mk.seasonal_test(newdatam[loc:], period=PERIOD)

    trend1 = np.arange(len(datam[:loc]))/PERIOD*resst1.slope + resst1.intercept
    trend2 = np.arange(len(datam[loc:]))/PERIOD*resst2.slope + resst2.intercept

    print('SEASONAL TEST USING MONTLY DATA')
    print('Trend entire period:', resst1.trend, 'p-value:', resst0.p, 'Average:', inputdata.loc[:, VAR].mean(), 'Slope per year:', resst0.slope)
    print('Trend until:', loc, resst1.trend, 'p-value:', resst1.p, 'Average:', inputdata.loc[:loc, VAR].mean(), 'Solpe per year:', resst1.slope)
    print('Trend from:', loc, resst2.trend, 'p-value:', resst2.p, 'Average:', inputdata.loc[loc:, VAR].mean(), 'Slope per year:', resst2.slope)
    print('New trend from:', loc, resst3.trend, 'p-value:', resst3.p, 'Average:', newdata.loc[loc:, VAR].mean(), 'Slope per year:', resst3.slope)

    pl.plot_ts(inputdata, newdata, VAR, loc, respt, mu3, resst1, resst2, PERIOD, SEASON, cfg)

res0 = mk.original_test(datay)
res1 = mk.original_test(datay[:loc])
res2 = mk.original_test(datay[loc:])
res3 = mk.original_test(newdatay[loc:])

print('ORIGINAL TEST USING YEARLY DATA')
print('Trend entire period:', res1.trend, 'Average:', inputdata.loc[:, VAR].mean(), 'Slope per year:', res0.slope)
print('Trend until:', loc, res1.trend, 'Average:', inputdata.loc[:loc, VAR].mean(), 'Slope per year:', res1.slope)
print('Trend from:', loc, res2.trend, 'Average:', inputdata.loc[loc:, VAR].mean(), 'Slope per year:', res2.slope)
print('New trend from:', loc, res3.trend, 'Average:', newdata.loc[loc:, VAR].mean(), 'Slope per year:', res3.slope)
pl.plot_ts(inputdata, newdata, VAR, loc, respt, mu3, res1, res2, 1, SEASON, cfg)

plt.show()

__import__('pdb').set_trace()
#wr.write_forcing(cfg, newdata, VAR, PATHOUT)
