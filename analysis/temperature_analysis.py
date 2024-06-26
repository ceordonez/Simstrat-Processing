import os
import sys

from pandas.core import window

script_dir = os.path.dirname(__file__)
scr_dir = os.path.join(script_dir, '..')
sys.path.append(scr_dir)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyhomogeneity as ho
import pymannkendall as mk
from scr.read_data import read_config, read_forcing, read_varconfig
from statsmodels.tsa.seasonal import seasonal_decompose, STL
from statsmodels.regression.linear_model import OLS

from scipy.stats import theilslopes

import functions as fn
import plots as pl
import write as wr

plt.style.use('~/.config/matplotlib/aslo-paper.mplstyle')

PATHOUT ='/home/cesar/Dropbox/Cesar/PostDoc/Projects/WaterClarity/Simulations/INPUTS/HALLWIL/'

VAR = 'I_ATEMP'
NAMEVAR = 'Temperature [degC]'
NORMPERIOD = 'all'
SEASON = ''
PERIOD = 12

cfg = read_varconfig('../config_preprocessing.yml')

inputdata = read_forcing(cfg, 'Forcing_NoBright.dat')
inputdata = inputdata.loc[:'31-12-2021']
inputdata = inputdata.rename(columns={NAMEVAR:VAR})
data = inputdata[VAR]
data.index = data.index.round('h')
datam = data.resample('ME').mean()

#respt = ho.pettitt_test(datam)
#loc = pd.to_datetime(respt.cp)
#resst0 = mk.seasonal_test(datam, period=PERIOD)
#resst1 = mk.seasonal_test(datam[:loc], period=PERIOD)
#resst2 = mk.seasonal_test(datam[loc:], period=PERIOD)
#
#print('Trend entire period:', resst1.trend, 'p-value:', resst0.p, 'Average:', inputdata.loc[:, VAR].mean(), 'Slope per year:', resst0.slope)
#print('Trend until:', loc, resst1.trend, 'p-value:', resst1.p, 'Average:', inputdata.loc[:loc, VAR].mean(), 'Solpe per year:', resst1.slope)
#print('Trend from:', loc, resst2.trend, 'p-value:', resst2.p, 'Average:', inputdata.loc[loc:, VAR].mean(), 'Slope per year:', resst2.slope)
#res = STL(datam).fit()
#lres = OLS(datam.values, list(range(datam.shape[0]))).fit()
#rres = datam.rolling(window=12).mean()
lresp = np.polyfit(range(data.shape[0]), data.values, 1)
lp = np.polyval(lresp, range(data.shape[0])) - lresp[1]

#lfit = pd.Series(lres.predict(range(datam.shape[0])), index=datam.index)
lfitp = pd.Series(lp, index=data.index)
#dtrend = datam - res.trend + res.trend.loc['1981'].mean()
dtrendp = datam - lfitp

slope, interp = mk.seasonal_sens_slope(datam.values)#,  range(datam.shape[0]))
res = mk.seasonal_test(datam)

conv = 1/365/24
#lfitt = pd.Series(range(datam.shape[0])*slope, index=datam.index)
lfitt = pd.Series(range(data.shape[0])*res.slope*conv, index=data.index)
dtrendt = data - lfitt

#restfit = mk.seasonal_test(dtrendt.resample('ME').mean(), period=PERIOD)

fig, ax = plt.subplots()
ax.plot(data.resample('ME').mean())
#ax.plot(lfitp)
#ax.plot(dtrend)
ax.plot(dtrendp.resample('ME').mean())
ax.plot(dtrendt.resample('ME').mean())

#res.plot()
#dtres = STL(dtrend).fit()
#dtres.plot()

dtresp = STL(dtrendp.resample('ME').mean()).fit()
dtresp.plot()
dtrest = STL(dtrendt.resample('ME').mean()).fit()
dtrest.plot()
plt.show()

newdata = inputdata.copy()
newdata.index = dtrendt.index
newdata[NAMEVAR] = dtrendt
wr.write_forcing(cfg, newdata, PATHOUT, 'Forcing_NSB-NCC.dat')
