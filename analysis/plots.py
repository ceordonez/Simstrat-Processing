
import os

import matplotlib.pyplot as plt
import pymannkendall as mk
import numpy as np

from scr.read_data import read_varconfig

def plot_ts(data, newdata, var, loc, respt, mu3, resst0, resst1, period, cfg):

    mu1 = respt.avg.mu1
    mu2 = respt.avg.mu2
    newdatam = newdata.resample('ME').mean()
    newdatay = newdata.resample('YE').mean()

    datam = data[var].resample('ME').mean()
    datay = data[var].resample('YE').mean()

    trend1 = np.arange(len(datam[:loc]))/period*resst0.slope + resst0.intercept
    trend2 = np.arange(len(datam[loc:]))/period*resst1.slope + resst1.intercept

    ylabel = read_varconfig('../utils/config_varfile.yml')

    fig, ax = plt.subplots(1, 1, figsize=(6,4), layout='constrained')
    #ax.plot(inputdata[var], 'k', alpha=0.3, label='')
    ax.plot(datay, '-o', label='Yearly Avg.')
    ax.plot(datam, label='Monthly Avg', alpha=0.3, color='k')
    ax.plot(newdatam[var], label='New Monthly Avg.', alpha=0.3, color='r')
    #ax.plot(newdata[var], 'r', alpha=0.3, label='')
    ax.plot(newdatay[var], '-o', label='New Yearly Avg.', color='r')
    #ax.plot(datam[:loc].index, trend1, color='orange', label='Trend1')
    #ax.plot(datam[loc:].index, trend2, color='g', label='Trend2')
    ax.hlines(mu1, xmin=datay.index[0], xmax=loc, linestyles='--', color='orange', label='mu1 : ' + str(round(mu1,2)))
    ax.hlines(mu2, xmin=loc, xmax=datay.index[-1], linestyles='--', color='g', label='mu2 : ' + str(round(mu2,2)))
    ax.hlines(mu3, xmin=datay.index[0], xmax=loc, linestyles='--', color='red', label='mu3 : ' + str(round(mu3,2)))
    ax.axvline(x=loc, linestyle='-.', color='r', label='Change point : '+ loc.strftime('%Y-%m-%d') + '\n p-value : ' + str(respt.p))
    ax.set_ylabel(ylabel['I_RAD'][1])

    ax.legend(ncols=2)

    figname = os.path.join(cfg['paths']['figures'],'PRE_PROSCESING')
    if not os.path.exists(figname):
        os.makedirs(figname)
    #fig.savefig(figname + '/Pettit_SolarRadiationNewdata.png', dpi=300)
    plt.show()
