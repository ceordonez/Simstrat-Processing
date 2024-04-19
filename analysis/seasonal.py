import os
import sys
import pandas as pd
import matplotlib.pyplot as plt


script_dir = os.path.dirname(__file__)
scr_dir = os.path.join(script_dir, '..')
sys.path.append(scr_dir)

from scr.read_data import read_config, read_absorption, read_varconfig

plt.style.use('~/.config/matplotlib/aslo-paper.mplstyle')
cfg = read_varconfig('../config_plots.yml')
ylabel = read_varconfig('../utils/config_varfile.yml')
PATHFIG = os.path.join(cfg['path_figures'],'SEASONAL')
#FILE = 'HALLWIL_EAWAG_INPUTS_BASE_MONTHLY.csv'
FILE = 'HALLWIL_OBS_1D_ORG.csv'

filename = os.path.join(cfg['path_outfiles'], FILE)

data = pd.read_csv(filename, header=[0], index_col=0, parse_dates=[0], date_format='%Y-%m-%d')
#data = pd.read_csv(filename, header=[0, 1], index_col=0, parse_dates=[0], date_format='%Y-%m-%d')
data.sort_index(inplace=True)

data1 = data.loc[:'1995']
data2 = data.loc['1996':'2007']
data3 = data.loc['2008':]

def seasonal(data):
    #datam = data.loc[:, (data.columns.get_level_values(0), 'mean')].copy()
    datam = data.copy()
    datam['month'] = datam.index.month
    #datam.columns = datam.columns.droplevel(1)
    datamg = datam.groupby(by='month').agg(['mean', 'std'])
    datamg.reset_index(inplace=True)
    return datamg

fig, ax = plt.subplot_mosaic([['ss','leg'],['n2','leg'], ['hc', 'leg']], gridspec_kw={'width_ratios': [1, .1]}, figsize=(6, 5.25), layout='constrained')
ax['leg'].spines['bottom'].set_visible(False)
ax['leg'].spines['left'].set_visible(False)
ax['leg'].set_xticks([])
ax['leg'].set_yticks([])
ax['ss'].set_xticks([])
ax['n2'].set_xticks([])

labels = ['1986-1995', '1996-2007', '2008-2020']

data1s = seasonal(data1)
data2s = seasonal(data2)
data3s = seasonal(data3)

for i, datap in enumerate((data1s, data2s, data3s)):
    ax['ss'].errorbar(datap['month'], datap['O_ST']['mean'], yerr=datap['O_ST']['std'], marker='o', linestyle='-', label=labels[i], capsize=3)
    ax['n2'].errorbar(datap['month'], datap['O_MN2']['mean'], yerr=datap['O_MN2']['std'], marker='o', linestyle='-', label=labels[i], capsize=3)
    ax['hc'].errorbar(datap['month'], datap['O_HC']['mean'], yerr=datap['O_HC']['std'], marker='o', linestyle='-', label=labels[i], capsize=3)

ax['hc'].set_xlabel('Month')
ax['ss'].set_ylabel(r'Schmidt Stability (\si{\joule\per\square\meter})')
ax['n2'].set_ylabel(r'N\textsuperscript{2} (s\textsuperscript{-2})')
ax['hc'].set_ylabel(r'Heat Content (\si{\joule})')

handles, labels = ax['ss'].get_legend_handles_labels()
ax['leg'].legend(handles, labels, ncol=1, loc='center', bbox_to_anchor=(0.5, 0.5))
plt.show()
figname = 'Seasonal_ST_N2_HC_P1996-2008.png'
if not os.path.exists(PATHFIG):
    os.makedirs(PATHFIG)
fig.savefig(os.path.join(PATHFIG, figname), format='png')

