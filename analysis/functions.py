

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
