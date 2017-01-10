from numpy import *
from netCDF4 import Dataset

# For the given year, calculate the 6- and 12-hourly anomalies from the monthly
# mean, for ERA-Interim atmospheric variables. Save this sub-monthly variability
# in NetCDF files (one file for 6-hourly, one for 12-hourly).
# Input: year = integer containing year to process
def extract_submonthly_variability (year):

    # Path to directory containing monthly averages of ERA-Interim atmospheric
    # variables, 1992-2005
    monthly_dir = '/short/y99/kaa561/CMIP5_forcing/atmos/climatology/ERA_Interim_monthly/'
    monthly_tail = '_monthly_orig.nc'
    # Path directory containing subdaily (6- and 12-hourly) values for the same
    # variables
    subdaily_dir = '/short/y99/kaa561/CMIP5_forcing/atmos/climatology/ERA_Interim_subdaily/'
    subdaily_tail = '_subdaily_orig.nc'
    # Path to output directory
    output_dir = '/short/y99/kaa561/CMIP5_forcing/atmos/climatology/ERA_Interim_variability/'
    # Days per month
    days_per_month = [31,28,31,30,31,30,31,31,30,31,30,31]
    # Check for leap years
    if year % 4 == 0:
        days_per_month[1] = 29
    # Variables with 6-hourly values
    var_names_6h = ['sp', 't2m', 'd2m', 'tcc', 'u10', 'v10']
    # Variables with 12-hourly values
    var_names_12h = ['tp', 'sf', 'e', 'ssrd', 'strd']

    # Read grid and 6-hour time axis for this year
    id = Dataset(subdaily_dir + 'AN_' + str(year) + subdaily_tail, 'r')
    lon = id.variables['longitude'][:]
    lat = id.variables['latitude'][:]
    time_6h = id.variables['time'][:]
    id.close()

    # Set up 6-hourly file
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

    # Loop over variables
    for var in var_names_6h:
        print 'Processing variable ' + var
        o_id.createVariable(var, 'f8', ('time', 'latitude', 'longitude'))
        # Read monthly values
        m_id = Dataset(monthly_dir + 'AN_' + str(year) + monthly_tail, 'r')
        monthly = m_id.variables[var][:,:,:]
        m_id.close()
        # Open file containing subdaily values
        s_id = Dataset(subdaily_dir + 'AN_' + str(year) + subdaily_tail, 'r')
        t_start = 0
        # Loop over months
        for month in range(12):
            print 'Month ' + str(month+1)
            # Figure out which 6-hourly timesteps fit in this month
            t_end = t_start + days_per_month[month]*4
            print 'Timesteps ' + str(t_start+1) + ' to ' + str(t_end)
            # Loop over 6-hourly timesteps
            for t in range(t_start, t_end):
                # Read 6-hourly data, subtract monthly average, and save
                subdaily = s_id.variables[var][t,:,:]
                o_id.variables[var][t,:,:] = subdaily - monthly[month]
            t_start = t_end
        s_id.close()
    o_id.close()

    # Read 12-hour time axis for this year
    id = Dataset(subdaily_dir + 'FC_' + str(year) + subdaily_tail, 'r')
    time_12h = id.variables['time'][:]
    id.close()

    # Set up 12-hourly file
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

    # Loop over variables
    for var in var_names_12h:
        print 'Processing variable ' + var
        o_id.createVariable(var, 'f8', ('time', 'latitude', 'longitude'))
        # Figure out filename
        if var in ['tp', 'sf']:
            infile_head = 'FC_'
        elif var in ['e', 'ssrd', 'strd']:
            infile_head = 'ER_'
        # Read monthly values
        m_id = Dataset(monthly_dir + infile_head + str(year) + monthly_tail, 'r')
        monthly = m_id.variables[var][:,:,:]
        m_id.close()
        # Open file containing subdaily values
        s_id = Dataset(subdaily_dir + infile_head + str(year) + subdaily_tail, 'r')
        t_start = 0
        # Loop over months
        for month in range(12):
            print 'Month ' + str(month+1)
            # Figure out which 12-hourly timesteps fit in this month
            t_end = t_start + days_per_month[month]*2
            print 'Timesteps ' + str(t_start+1) + ' to ' + str(t_end)
            # Loop over 12-hourly timesteps
            for t in range(t_start, t_end):
                # Read 12-hourly data, subtract monthly average, and save
                subdaily = s_id.variables[var][t,:,:]
                o_id.variables[var][t,:,:] = subdaily - monthly[month]
            t_start = t_end
        s_id.close()
    o_id.close()


# Command-line interface
if __name__ == "__main__":

    # Run for the 12-year period 1994-2005 inclusive
    for year in range(1994,2005+1):
        print 'Processing year ' + str(year)
        extract_submonthly_variability(year)
        

    
    

    

    
