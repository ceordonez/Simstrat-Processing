
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
import ruptures as rpt
from statsmodels.tsa.seasonal import seasonal_decompose, STL
from statsmodels.tsa.ar_model import AutoReg
import statsmodels.stats.multicomp as mc
from scr.read_data import read_config, read_absorption, read_varconfig
import scipy.stats as stats

import functions as fn
import plots as pl
import write as wr

plt.style.use('~/.config/matplotlib/aslo-paper.mplstyle')

PATHOUT ='/home/cesar/Dropbox/Cesar/PostDoc/Projects/WaterClarity/Simulations/INPUTS/HALLWIL/'

cfg = read_varconfig('../config_preprocessing.yml')
ylabel = read_varconfig('../utils/config_varfile.yml')
PATHFIG = os.path.join(cfg['paths']['figures'],'PRE_PROSCESING')

if not os.path.exists(PATHFIG):
    os.makedirs(PATHFIG)

var = 'O_SD'
#model = 'PETT'
#model = 'KCPD'
model = 'PELT'

inputdata = read_absorption(cfg, 'Absorption.dat')
obsdata = inputdata.loc['1985':]
obsdata['O_SD'] = 1.7/obsdata['I_KL']

data = obsdata.resample('SME').mean().ffill()
aux = obsdata.resample('SME').mean()

datay = obsdata[var].resample('YE').mean()

fig, ax = plt.subplots(1, 1, figsize=(6, 2.5), layout='constrained')
ax.plot(obsdata[var], '-o', label='Obs')
ax.plot(data[var], '-o', label='Monthly Filled')
ax.plot(aux[var], '-o', label='Monthly')
#ax.axvline(x=loc1, linestyle='-.', color='r', label='Change point : '+ loc1.strftime('%Y-%m'))# + '\n p-value : ' + str(respt1.p))
#ax.axvline(x=loc2, linestyle='-.', color='r', label='Change point : '+ loc2.strftime('%Y-%m'))# + '\n p-value : ' + str(respt2.p))
ax.legend()
ax.set_ylabel(ylabel[var][1])
figname = '_'.join(['Bi-weakly-average', var])
fig.savefig(os.path.join(PATHFIG, figname) + '.png', dpi=300)
plt.close()

if model == 'PETT':
    LOC = '2002'
    datap1 = obsdata.loc[:LOC, var]
    datap2 = obsdata.loc[LOC:, var]
    respt1 = ho.pettitt_test(datap1.resample('YE').mean())
    respt2 = ho.pettitt_test(datap2.resample('YE').mean())
    loc1 = pd.to_datetime(respt1.cp)
    loc2 = pd.to_datetime(respt2.cp)

elif model == 'PELT':
    fitdata = rpt.Pelt(model='l2', jump=5, min_size=2).fit(datay.values)
    res = fitdata.predict(pen=2)
    loc1 = pd.to_datetime(datay.index[res[0]])
    loc2 = pd.to_datetime(datay.index[res[1]])

elif model == 'KCPD':
    fitdata = rpt.KernelCPD(kernel='linear', min_size=2).fit(datay.values)
    res = fitdata.predict(n_bkps=2)
    loc1 = pd.to_datetime(datay.index[res[0]])
    loc2 = pd.to_datetime(datay.index[res[1]])

print(model, loc1, loc2)

f_stat, p_value = stats.f_oneway(data.loc[:loc1, var], data.loc[loc1:loc2, var], data.loc[loc2:, var])
print("ANOVA results:")
print("F-statistic:", f_stat)
print("p-value:", p_value)

if p_value < 0.05:
    groups_labels = ['p0']*len(data.loc[:loc1, var]) + ['p1']*len(data.loc[loc1:loc2, var]) + ['p2']*len(data.loc[loc2:, var])
    alldata = pd.concat([data.loc[:loc1, var], data.loc[loc1:loc2, var], data.loc[loc2:, var]])
    tk_res = mc.MultiComparison(alldata, groups_labels).tukeyhsd()
    print(tk_res)

res1 = seasonal_decompose(data.loc[:loc1, var], model='additive', period=24)
res2 = seasonal_decompose(data.loc[loc1:loc2, var], model='additive', period=24)
res3 = seasonal_decompose(data.loc[loc2:, var], model='additive', period=24)

#res1 = STL(data[:loc1],period=25)
#res2 = STL(data[loc1:loc2], period=25)
#res3 = STL(data[loc2:], period=25)

for i, res in enumerate([res1, res2, res3]):
    fig = res.plot()
    fig.set_size_inches(6, 5.5)
    axs = fig.get_axes()
    fig.tight_layout()
    axs[0].set_ylabel(ylabel[var][1])
    figlabel = 'P'+ str(i)
    figname = '_'.join(['Seasonal_decomposition', model, var, figlabel])
    fig.savefig(os.path.join(PATHFIG, figname) + '.png', dpi=300)
    plt.close()


datap1 = res1.seasonal + data.loc[:loc1, var].mean()
datap2 = res2.seasonal + data.loc[loc1:loc2, var].mean()
datap3 = res3.seasonal + data.loc[loc2:, var].mean()

fig, ax = plt.subplots(1, 1, figsize=(6, 2.5), layout='constrained')
ax.plot(obsdata[var], '-o', label='Obs')
ax.plot(datap1, label='mu : ' + str(round(datap1.mean(),2)))
ax.plot(datap2, label='mu : ' + str(round(datap2.mean(),2)))
ax.plot(datap3, label='mu : ' + str(round(datap3.mean(),2)))
ax.axvline(x=loc1, linestyle='-.', color='r', label='Change point : '+ loc1.strftime('%Y-%m'))# + '\n p-value : ' + str(respt1.p))
ax.axvline(x=loc2, linestyle='-.', color='r', label='Change point : '+ loc2.strftime('%Y-%m'))# + '\n p-value : ' + str(respt2.p))
ax.legend()
ax.set_ylabel(ylabel[var][1])
figname = '_'.join(['Simulated', model, var])
fig.savefig(os.path.join(PATHFIG, figname) + '.png', dpi=300)
#plt.close()

# include interpolation before 1985
data = inputdata.resample('SME').mean().ffill()
data['O_SD'] = 1.7/data['I_KL']
for i, datap in enumerate([datap1, datap2, datap3]):
    automod = AutoReg(datap, lags=25).fit()
    pred = automod.predict(start=len(datap), end=len(data)-1, dynamic=False)

    sdata = pd.concat([datap, pred])
    rsdata = pd.Series(sdata.values, index=data.index)
    title = 'P' + str(i)
    fig, ax = plt.subplots(1, 1, figsize=(6, 2.5), layout='constrained')
    ax.set_title(title)
    ax.plot(data[var])
    ax.plot(rsdata)
    ax.set_ylabel(ylabel[var][1])
    filename = '_'.join(['Absorption', model, title])
    figname = '_'.join(['Simulated', var, model, 'AllPeriod', title])
    fig.savefig(os.path.join(PATHFIG, figname) + '.png', dpi=300)
    pddata = pd.DataFrame({'I_KL':1.7/rsdata.values}, index=rsdata.index)
    wr.write_absorption(cfg, pddata, PATHOUT, filename)

plt.show()
