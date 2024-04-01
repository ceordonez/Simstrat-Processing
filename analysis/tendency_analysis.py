
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

plt.style.use('~/.config/matplotlib/aslo-paper.mplstyle')

cfg = read_varconfig('../config_preprocessing.yml')
inputdata = read_forcing(cfg, 'Forcing.dat')
inputdata = inputdata.loc[:'31-12-2021']
inputdata = inputdata.rename(columns={'Solar radiation [W/m^2]':'rad'})


datam = inputdata['rad'].resample('ME').mean()
datay = inputdata['rad'].resample('YE').mean()

# Find tipping point using yearly average data
respt = ho.pettitt_test(datay)
loc = pd.to_datetime(respt.cp)

mu1 = respt.avg.mu1
mu2 = respt.avg.mu2

meanp1 = datam.loc[:loc].mean()
newdata = inputdata.copy()
aux1 = []
aux2 = []
for year in datam.loc[loc:].index.year.unique():
    mmeany = datam.loc[str(year)].mean()
    mmeany0 = datam.loc[str(loc.year-1):str(year)].mean()
    aux1.append(meanp1/mmeany*meanp1)
    aux2.append(mmeany/mmeany0*meanp1)
    newdata.loc[str(year),'rad'] = (meanp1/mmeany)*(mmeany/mmeany0)*newdata.loc[str(year), 'rad']

# Find the tendency for the periods define with the pettitt test on montly data

#print(resst3)
newdata[loc:] = meanp1/newdata[loc:].mean()*newdata[loc:]
newdatam = newdata.resample('ME').mean()
newdatay = newdata.resample('YE').mean()

mu3 = newdata.loc[loc:, 'rad'].mean()

print(newdata.loc[loc:, 'rad'].mean())
print(datam.loc[:loc].mean())

period = 12
resst1 = mk.seasonal_test(datam[:loc], period=period)
resst2 = mk.seasonal_test(datam[loc:], period=period)
resst3 = mk.seasonal_test(newdatam[loc:], period=period)
#resst3 = mk.seasonal_test(datam, period=period)

trend1 = np.arange(len(datam[:loc]))/period*resst1.slope + resst1.intercept
trend2 = np.arange(len(datam[loc:]))/period*resst2.slope + resst2.intercept

print(resst1)
print(resst2)
print(resst3)

ylabel = read_varconfig('../utils/config_varfile.yml')
fig, ax = plt.subplots(1, 1, figsize=(6,4), layout='constrained')
#ax.plot(inputdata['rad'], 'k', alpha=0.3, label='')
ax.plot(datay, '-o', label='Yearly Avg.')
ax.plot(datam, label='Monthly Avg', alpha=0.3, color='k')
ax.plot(newdatam['rad'], label='New Monthly Avg.', alpha=0.3, color='r')
#ax.plot(newdata['rad'], 'r', alpha=0.3, label='')
ax.plot(newdatay['rad'], '-o', label='New Yearly Avg.', color='r')
#ax.plot(datam[:loc].index, trend1, color='orange', label='Trend1')
#ax.plot(datam[loc:].index, trend2, color='g', label='Trend2')
ax.hlines(mu1, xmin=datay.index[0], xmax=loc, linestyles='--', color='orange', label='mu1 : ' + str(round(mu1,2)))
ax.hlines(mu2, xmin=loc, xmax=datay.index[-1], linestyles='--', color='g', label='mu2 : ' + str(round(mu2,2)))
ax.hlines(mu3, xmin=datay.index[0], xmax=loc, linestyles='--', color='red', label='mu3 : ' + str(round(mu3,2)))
ax.axvline(x=loc, linestyle='-.', color='r', label='Change point : '+ loc.strftime('%Y-%m-%d') + '\n p-value : ' + str(respt.p))
ax.set_ylabel(ylabel['I_RAD'][1])
figname = os.path.join(cfg['paths']['figures'],'PRE_PROSCESING')
if not os.path.exists(figname):
    os.makedirs(figname)
ax.legend(ncols=2)
fig.savefig(figname + '/Pettit_SolarRadiationNewdata.png', dpi=300)
plt.show()
