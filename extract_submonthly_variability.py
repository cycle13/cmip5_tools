from numpy import *
from netCDF4 import Dataset

def extract_submonthly_variability (year):

    monthly_dir = '/short/y99/kaa561/CMIP5_forcing/atmos/climatology/ERA_Interim_monthly/'
    monthly_tail = '_monthly_orig.nc'
    subdaily_dir = '/short/y99/kaa561/CMIP5_forcing/atmos/climatology/ERA_Interim_subdaily/'
    subdaily_tail = '_subdaily_orig.nc'
    output_dir = '/short/y99/kaa561/CMIP5_forcing/atmos/climatology/ERA_Interim_variability/'
    days_per_month = [31,28,31,30,31,30,31,31,30,31,30,31]
    if year % 4 == 0:
        days_per_month[1] = 29
    var_names_6h = ['sp', 't2m', 'd2m', 'tcc', 'u10', 'v10']
    var_names_12h = ['tp', 'sf', 'e', 'ssrd', 'strd']

    id = Dataset(subdaily_dir + 'AN_' + str(year) + subdaily_tail, 'r')
    lon = id.variables['longitude'][:]
    lat = id.variables['latitude'][:]
    time_6h = id.variables['time'][:]
    id.close()

    file_6h = output_dir + '6h_variability_' + str(year) + '.nc'
    print 'Setting up ' + file_6h
    o_id = Dataset(file_6h, 'w')
    o_id.createDimension('longitude', size(lon))
    o_id.createDimension('latitude', size(lat))
    o_id.createDimension('time', None)
    o_id.createVariable('longitude', 'f8', ('longitude'))
    o_id.variables['longitude'].units = 'degrees'
    o_id.variables['longitude'][:] = lon
    o_id.createVariable('latitude', 'f8', ('latitude'))
    o_id.variables['latitude'].units = 'degrees'
    o_id.variables['latitude'][:] = lat
    o_id.createVariable('time', 'f8', ('time'))
    o_id.variables['time'].units = 'hours since 1900-1-1 00:00:00'
    o_id.variables['time'].calendar = 'standard'
    o_id.variables['time'][:] = time_6h

    for var in var_names_6h:
        print 'Processing variable ' + var
        o_id.createVariable(var, 'f8', ('time', 'latitude', 'longitude'))
        m_id = Dataset(monthly_dir + 'AN_' + str(year) + monthly_tail, 'r')
        monthly = m_id.variables[var][:,:,:]
        m_id.close()
        s_id = Dataset(subdaily_dir + 'AN_' + str(year) + subdaily_tail, 'r')
        t_start = 0
        for month in range(12):
            print 'Month ' + str(month+1)
            t_end = t_start + days_per_month[month]*4
            print 'Timesteps ' + str(t_start+1) + ' to ' + str(t_end)
            for t in range(t_start, t_end):
                subdaily = s_id.variables[var][t,:,:]
                o_id.variables[var][t,:,:] = subdaily - monthly[month]
            t_start = t_end
        s_id.close()
    o_id.close()

    id = Dataset(subdaily_dir + 'FC_' + str(year) + subdaily_tail, 'r')
    time_12h = id.variables['time'][:]
    id.close()

    file_12h = output_dir + '12h_variability_' + str(year) + '.nc'
    print 'Setting up ' + file_12h
    o_id = Dataset(file_12h, 'w')
    o_id.createDimension('longitude', size(lon))
    o_id.createDimension('latitude', size(lat))
    o_id.createDimension('time', None)
    o_id.createVariable('longitude', 'f8', ('longitude'))
    o_id.variables['longitude'].units = 'degrees'
    o_id.variables['longitude'][:] = lon
    o_id.createVariable('latitude', 'f8', ('latitude'))
    o_id.variables['latitude'].units = 'degrees'
    o_id.variables['latitude'][:] = lat
    o_id.createVariable('time', 'f8', ('time'))
    o_id.variables['time'].units = 'hours since 1900-1-1 00:00:00'
    o_id.variables['time'].calendar = 'standard'
    o_id.variables['time'][:] = time_12h

    for var in var_names_12h:
        print 'Processing variable ' + var
        if var in ['tp', 'sf']:
            infile_head = 'FC_'
        elif var in ['e', 'ssrd', 'strd']:
            infile_head = 'ER_'
        o_id.createVariable(var, 'f8', ('time', 'latitude', 'longitude'))
        m_id = Dataset(monthly_dir + infile_head + str(year) + monthly_tail, 'r')
        monthly = m_id.variables[var][:,:,:]
        m_id.close()
        s_id = Dataset(subdaily_dir + infile_head + str(year) + subdaily_tail, 'r')
        t_start = 0
        for month in range(12):
            print 'Month ' + str(month+1)
            t_end = t_start + days_per_month[month]*2
            print 'Timesteps ' + str(t_start+1) + ' to ' + str(t_end)
            for t in range(t_start, t_end):
                subdaily = s_id.variables[var][t,:,:]
                o_id.variables[var][t,:,:] = subdaily - monthly[month]
            t_start = t_end
        s_id.close()
    o_id.close()


if __name__ == "__main__":

    for year in range(1994,2005+1):
        print 'Processing year ' + str(year)
        extract_submonthly_variability(year)
        

    
    

    

    
