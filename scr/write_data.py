import os

import pandas as pd

def write_meteo(path, filename, data, basedate):
    basedate = pd.to_datetime(basedate)
    data['time [d]'] = (data.index - basedate).total_seconds()/(60*60*24)
    data.reset_index(inplace=True)
    wdata = data.iloc[:, [11,9,10,3,2,1,8,4]]
    wdata.to_csv(os.path.join(path, filename),index=False)
