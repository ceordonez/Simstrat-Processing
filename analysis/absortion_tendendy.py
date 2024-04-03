
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
from statsmodels.tsa.seasonal import seasonal_decompose, STL
from statsmodels.tsa.ar_model import AutoReg
from scr.read_data import read_config, read_absorption, read_varconfig

import functions as fn
import plots as pl
import write as wr

plt.style.use('~/.config/matplotlib/aslo-paper.mplstyle')

PATHOUT ='/home/cesar/Dropbox/Cesar/PostDoc/Projects/WaterClarity/Simulations/INPUTS/HALLWIL/'
LOC = '2002'


cfg = read_varconfig('../config_preprocessing.yml')

PATHFIG = os.path.join(cfg['paths']['figures'],'PRE_PROSCESING')

if not os.path.exists(PATHFIG):
    os.makedirs(PATHFIG)

inputdata = read_absorption(cfg, 'Absorption.dat')
data = inputdata.resample('SME').mean().ffill()
aux = inputdata.resample('SME').mean()

datap1 = inputdata.loc[:LOC]
datap2 = inputdata.loc[LOC:]
respt1 = ho.pettitt_test(datap1)
respt2 = ho.pettitt_test(datap2)
loc1 = pd.to_datetime(respt1.cp)
loc2 = pd.to_datetime(respt2.cp)

ylabel = read_varconfig('../utils/config_varfile.yml')
fig, ax = plt.subplots(1, 1, figsize=(6, 2.5), layout='constrained')
ax.plot(inputdata, '-o', label='Obs')
ax.plot(data, '-o', label='Monthly Filled')
ax.plot(aux, '-o', label='Monthly')
ax.axvline(x=loc1, linestyle='-.', color='r', label='Change point : '+ loc1.strftime('%Y-%m') + '\n p-value : ' + str(respt1.p))
ax.axvline(x=loc2, linestyle='-.', color='r', label='Change point : '+ loc2.strftime('%Y-%m') + '\n p-value : ' + str(respt2.p))
ax.legend()
ax.set_ylabel(ylabel['I_KL'][1])
figname = '_'.join(['Bi-weakly-average', 'I_KL'])
fig.savefig(os.path.join(PATHFIG, figname) + '.png', dpi=300)
plt.close()

res1 = seasonal_decompose(data[:loc1], model='additive', period=24)
res2 = seasonal_decompose(data[loc1:loc2], model='additive', period=24)
res3 = seasonal_decompose(data[loc2:], model='additive', period=24)

#res1 = STL(data[:loc1],period=25)
#res2 = STL(data[loc1:loc2], period=25)
#res3 = STL(data[loc2:], period=25)

for i, res in enumerate([res1, res2, res3]):
    fig = res.plot()
    fig.set_size_inches(6, 5.5)
    axs = fig.get_axes()
    fig.tight_layout()
    axs[0].set_ylabel(ylabel['I_KL'][1])
    figlabel = 'P'+ str(i)
    figname = '_'.join(['Seasonal_decomposition', 'I_KL', figlabel])
    fig.savefig(os.path.join(PATHFIG, figname) + '.png', dpi=300)
    plt.close()


datap1 = res1.seasonal + data[:loc1].mean().values
datap2 = res2.seasonal + data[loc1:loc2].mean().values
datap3 = res3.seasonal + data[loc2:].mean().values

fig, ax = plt.subplots(1, 1, figsize=(6, 2.5), layout='constrained')
ax.plot(inputdata, '-o', label='Obs')
ax.plot(datap1, label='mu : ' + str(round(datap1.mean(),2)))
ax.plot(datap2, label='mu : ' + str(round(datap2.mean(),2)))
ax.plot(datap3, label='mu : ' + str(round(datap3.mean(),2)))
ax.axvline(x=loc1, linestyle='-.', color='r', label='Change point : '+ loc1.strftime('%Y-%m') + '\n p-value : ' + str(respt1.p))
ax.axvline(x=loc2, linestyle='-.', color='r', label='Change point : '+ loc2.strftime('%Y-%m') + '\n p-value : ' + str(respt2.p))
ax.legend()
ax.set_ylabel(ylabel['I_KL'][1])
figname = '_'.join(['Simulated', 'I_KL'])
fig.savefig(os.path.join(PATHFIG, figname) + '.png', dpi=300)
plt.close()

for i, datap in enumerate([datap1, datap2, datap3]):
    model = AutoReg(datap, lags=25).fit()
    pred = model.predict(start=len(datap), end=len(data)-1, dynamic=False)

    sdata = pd.concat([datap, pred])
    rsdata = pd.Series(sdata.values, index=data.index)
    title = 'P' + str(i)
    fig, ax = plt.subplots(1, 1, figsize=(6, 2.5), layout='constrained')
    ax.set_title(title)
    ax.plot(data)
    ax.plot(rsdata)
    ax.set_ylabel(ylabel['I_KL'][1])
    filename = '_'.join(['Absorption', title])
    figname = '_'.join(['Simulated', 'I_KL', 'AllPeriod', title])
    fig.savefig(os.path.join(PATHFIG, figname) + '.png', dpi=300)
    pddata = pd.DataFrame({'I_KL':rsdata.values}, index=rsdata.index)
    wr.write_absorption(cfg, pddata, PATHOUT, filename)
plt.show()
