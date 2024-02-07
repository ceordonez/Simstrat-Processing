import os

import pandas as pd

def write_meteo(path, filename, data, basedate):
    basedate = pd.to_datetime(basedate)
    data['time [d]'] = (data.index - basedate).total_seconds()/(60*60*24)
    data.reset_index(inplace=True)
    wdata = data.loc[:, ['time [d]', 'U [m/s]', 'V [m/s]', 'Temperature [degC]', 'Solar radiation [W/m^2]', 'Vapour pressure [mbar]', 'Cloud cover [-]']]
    wdata.to_csv(os.path.join(path, filename),index=False)
