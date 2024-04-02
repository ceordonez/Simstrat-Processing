

def normalize_data(data, loc, var):

    datam = data[var].resample('ME').mean()
    meanp1 = datam.loc[:loc].mean()
    newdata = data.copy()
    aux1 = []
    aux2 = []
    for year in datam.loc[loc:].index.year.unique():
        mmeany = datam.loc[str(year)].mean()
        mmeany0 = datam.loc[str(loc.year-1):str(year)].mean()
        aux1.append(meanp1/mmeany*meanp1)
        aux2.append(mmeany/mmeany0*meanp1)
        newdata.loc[str(year), var] = (meanp1/mmeany)*(mmeany/mmeany0)*newdata.loc[str(year), var]
    newdata.loc[loc:, var] = meanp1/newdata.loc[loc:, var].mean()*newdata.loc[loc:, var]
    return newdata

def select_season(data, season):
    data.reset_index(inplace=True)
    if season == 'SUMMER':
        data = data[(data.Datetime.dt.month >= 6) & (data.Datetime.dt.month <=8)]
    elif season == 'AUTUMN':
        data = data[(data.Datetime.dt.month >= 9) & (data.Datetime.dt.month <=11)]
    elif season == 'WINTER':
        data = data[(data.Datetime.dt.month == 12) | (data.Datetime.dt.month <=2)]
    elif season == 'SPRING':
        data = data[(data.Datetime.dt.month >= 3) & (data.Datetime.dt.month <=5)]
    data.set_index('Datetime', inplace=True)
    return data
