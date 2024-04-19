
import os
import sys
import numpy as np
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

def read_secchi(cfg):
    path = cfg['path_obs']
    data = pd.read_excel(os.path.join(path, cfg['file_secchi']), usecols=[3, 7])
    if 'date_complete' in data.columns:
        data.rename(columns={'date_complete': 'Datetime'}, inplace=True)
    if 'Secchi' in data.columns:
        data.rename(columns={'Secchi': 'O_SD'}, inplace=True)
    data['Datetime'] = pd.to_datetime(data['Datetime'])
    data.sort_values(by='Datetime', inplace=True)
    data.set_index('Datetime', inplace=True)
    data = data.loc[cfg['time_span'][0]:cfg['time_span'][1]]
    return data

data = read_secchi(cfg)
data['Period'] = 'P'
data.loc[:'1995', 'Period'] = '1986-1995'
data.loc['1996':'2007', 'Period'] = '1996-2007'
data.loc['2008':, 'Period'] = '2008-2020'


fig, ax = plt.subplots(figsize=(3,3))
data.boxplot(ax=ax, column='O_SD', by='Period')
ax.set_title(None)
fig.suptitle(None)
ax.set_ylabel('Secchi Depth (m)')
ax.set_xlabel(None)
figname = 'Secchi_NewPeriods.png'
if not os.path.exists(PATHFIG):
    os.makedirs(PATHFIG)
fig.savefig(os.path.join(PATHFIG, figname), format='png')
plt.show()
