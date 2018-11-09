from numpy import *
from netCDF4 import Dataset

def eraint_monthly_means (year):

    # Input file paths
    subdaily_6h_file = '/short/y99/kaa561/CMIP5_forcing/atmos/climatology/ERA_Interim_subdaily/AN_' + str(year) + '_subdaily_orig.nc'
    subdaily_12h_file = '/short/y99/kaa561/CMIP5_forcing/atmos/climatology/ERA_Interim_subdaily/ER_' + str(year) + '_subdaily_orig.nc'
    # Output file paths
    monthly_6h_file = '/short/y99/kaa561/CMIP5_forcing/atmos/climatology/ERA_Interim_monthly/AN_' + str(year) + '_monthly_orig.nc'
    monthly_12h_file = '/short/y99/kaa561/CMIP5_forcing/atmos/climatology/ERA_Interim_monthly/ER_' + str(year) + '_monthly_orig.nc'
    # Days per month
    days_per_month = [31,28,31,30,31,30,31,31,30,31,30,31]
    # Check for leap years
    if year % 4 == 0:
        days_per_month[1] = 29

    # 6-hourly (winds)
    # Read grid
    s_id = Dataset(subdaily_6h_file, 'r')
    lon = s_id.variables['longitude'][:]
    lat = s_id.variables['latitude'][:]
    print 'Setting up ' + monthly_6h_file
    o_id = Dataset(monthly_6h_file, 'w')
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
    o_id.createVariable('u10', 'f8', ('time', 'latitude', 'longitude'))
    o_id.createVariable('v10', 'f8', ('time', 'latitude', 'longitude'))
    # Loop over months
    t_start = 0
    for month in range(12):
        print 'Month ' + str(month+1)
        t_end = t_start + days_per_month[month]*4
        print 'Timesteps ' + str(t_start+1) + ' to ' + str(t_end)
        o_id.variables['time'][month] = mean(s_id.variables['time'][t_start:t_end])
        o_id.variables['u10'][month,:,:] = mean(s_id.variables['u10'][t_start:t_end,:,:], axis=0)
        o_id.variables['v10'][month,:,:] = mean(s_id.variables['v10'][t_start:t_end,:,:], axis=0)
        t_start = t_end
    s_id.close()
    o_id.close()

    '''# 6-hourly (pressure)
    # Read grid
    s_id = Dataset(subdaily_6h_file, 'r')
    lon = s_id.variables['longitude'][:]
    lat = s_id.variables['latitude'][:]
    print 'Setting up ' + monthly_6h_file
    o_id = Dataset(monthly_6h_file, 'w')
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
    o_id.createVariable('sp', 'f8', ('time', 'latitude', 'longitude'))
    # Loop over months
    t_start = 0
    for month in range(12):
        print 'Month ' + str(month+1)
        t_end = t_start + days_per_month[month]*4
        print 'Timesteps ' + str(t_start+1) + ' to ' + str(t_end)
        o_id.variables['time'][month] = mean(s_id.variables['time'][t_start:t_end])
        o_id.variables['sp'][month,:,:] = mean(s_id.variables['sp'][t_start:t_end,:,:], axis=0)
        t_start = t_end
    s_id.close()
    o_id.close()

    # 12-hourly (evaporation)
    # Read grid
    s_id = Dataset(subdaily_12h_file, 'r')
    print 'Setting up ' + monthly_12h_file
    o_id = Dataset(monthly_12h_file, 'w')
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
    o_id.createVariable('e', 'f8', ('time', 'latitude', 'longitude'))
    # Loop over months
    t_start = 0
    for month in range(12):
        print 'Month ' + str(month+1)
        t_end = t_start + days_per_month[month]*2
        print 'Timesteps ' + str(t_start+1) + ' to ' + str(t_end)
        o_id.variables['time'][month] = mean(s_id.variables['time'][t_start:t_end])
        o_id.variables['e'][month,:,:] = mean(s_id.variables['e'][t_start:t_end,:,:], axis=0)
        t_start = t_end
    s_id.close()
    o_id.close()'''


# Command-line interface
if __name__ == "__main__":

    # Run for the 12-year period 1994-2005 inclusive
    for year in range(1994,2005+1):
        print 'Processing year ' + str(year)
        eraint_monthly_means(year)

    
        
