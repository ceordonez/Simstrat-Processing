import os
import glob
import netCDF4 as nc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pdb

PATH = '/home/cesar-ordonez/Dropbox/Cesar/PostDoc/Projects/WaterClarity/HalwillData/ctdmonitoringlakehallwilbycantonaargau_datalakesdownload'

PATH_BUOY = '/home/cesar-ordonez/Dropbox/Cesar/PostDoc/Projects/WaterClarity/HalwillData/temperaturemonitoringlakehallwil_datalakesdownload'

FILENAME = 'L2_LakeHallwil_20150107_110000.nc'
PATH_OBS = '/home/cesar-ordonez/Dropbox/Cesar/PostDoc/Projects/WaterClarity/HalwillData/Raw'
FILEOBS = 'Temperature_bafu85_98probes20.csv'

def main():
    # Not using buoy data
    #by_data = read_buoy(PATH_BUOY)
    obsdata = read_watertemp(PATH_OBS, FILEOBS)
    ncfile = os.path.join(PATH, FILENAME)
    ca_data = read_ncdata(ncfile, 'YSI') # Asuming YSI
    #plot_comparison(by_data, ca_data)
    idx = obsdata.index[-1]
    data = [obsdata, ca_data[idx:]]
    data = pd.concat(data)
    data.to_csv('Temperature_profiles.csv')
    pdb.set_trace()


def read_ncdata(ncfile, instrument):
    ncdata = nc.Dataset(ncfile, 'r')
    start_date = datetime(1970, 1, 1)
    nctime = pd.to_datetime(ncdata['time'][:].data, unit='s', origin=start_date)
    pdb.set_trace()
    # This is for comparison!
    #nctime = nctime - pd.to_timedelta(nctime.hour.values, unit='h')
    pdb.set_trace()
    ncdepth = ncdata['depth'][:].data
    nctemp = ncdata['temp'][:].data
    data = pd.DataFrame({'Datetime': np.repeat(nctime, len(ncdepth)),
                         'Depth_m': np.tile(ncdepth, len(nctime)),
                         'O_TEMPP': nctemp.flatten('F')})
    data['Instrument'] = instrument
    data.set_index('Datetime', inplace=True)
    return data

def read_buoy(path):
    ncfiles = glob.glob(path + '**/*.nc', recursive=True)
    datalist = []
    for ncfile in ncfiles:
        ncdata = read_ncdata(ncfile, 'Buoy')
        datalist.append(ncdata)
    data = pd.concat(datalist)
    return data

def read_watertemp(path, filename):
    data = pd.read_csv(os.path.join(path, filename), usecols=[2,4,5,6])
    if 'date_complete' in data.columns:
        data.rename(columns={'date_complete': 'Datetime', 'depth': 'Depth_m', 'temperature': 'O_TEMPP', 'Source': 'Instrument'}, inplace=True)
    data['Datetime'] = pd.to_datetime(data['Datetime'], format='%d/%m/%Y')
    data.sort_values(by=['Datetime', 'Depth_m'], inplace=True)
    data.set_index('Datetime', inplace=True)
    return data

def plot_comparison(data, obsdata):

    data = data[:obsdata.index[-1]]
    obsdata = obsdata[data.index[0]:]
    for tx in obsdata.index.unique():
        if tx in data.index.values:
            pncdata = data.loc[tx]
            pobsdata = obsdata.loc[tx]
            fig, ax = plt.subplots(layout='constrained')
            ax.invert_yaxis()
            ax.plot(pncdata.O_TEMPP.values, pncdata.Depth_m.values, 'b-', marker='.', label='ncdata')
            ax.plot(pobsdata.O_TEMPP.values, pobsdata.Depth_m.values, 'r-', marker='.', label='obs')
            ax.legend()
            ax.set_xlabel('Temperature')
            ax.set_ylabel('Depth (m)')
            filename = 'Temp_Profile_' + tx.strftime('%Y-%m-%d') + '.png'
            fig.savefig(filename, format='png')
            plt.close(fig)
        else:
            print(tx)

if __name__== "__main__":
    main()
