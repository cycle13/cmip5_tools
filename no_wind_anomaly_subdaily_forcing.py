from numpy import *
from netCDF4 import Dataset

def no_wind_anomaly_subdaily_forcing ():

    # Path to ERA-Interim climatology file
    monthly_file = '/short/y99/kaa561/CMIP5_forcing/atmos/climatology/ERA-Interim.nc'
    # Path to directory containing ERA-Interim submonthly variability
    subdaily_dir = '/short/y99/kaa561/CMIP5_forcing/atmos/climatology/ERA_Interim_variability/'
    sub6_head = subdaily_dir + '6h_variability_'
    sub12_head = subdaily_dir + '12h_variability_'
    # Path to output directory
    output_dir = '/short/y99/kaa561/CMIP5_forcing/atmos/no_wind_anomaly/'
    # Variable names
    var_names_6h = ['u10', 'v10']
    # Variable units
    var_units_6h = ['m/s', 'm/s']
    year_start = 2006
    year_end = 2100
    # Submonthly variability years
    # The combination of year_start = 2006 and subyear_start = 1994 is important
    # so the leap year cycles line up
    subyear_start = 1994 
    subyear_end = 2005
    # Days per month
    days_per_month = [31,28,31,30,31,30,31,31,30,31,30,31]

    # Read grid
    id = Dataset(monthly_file, 'r')
    lon = id.variables['longitude'][:]
    lat = id.variables['latitude'][:]
    id.close()

    subyear = subyear_start
    # Loop over years
    for year in range(year_start, year_end+1):
        print 'Processing year ' + str(year)
        # Check for leap years
        if year % 4 == 0:
            days_per_month[1] = 29
        else:
            days_per_month[1] = 28
        if year == 2100:
            # Not a leap year
            days_per_month[1] = 28
            # Increment subyear so it's also not a leap year
            subyear += 1
            # Go back to the beginning of the submonthly variability cycle
            # if necessary
            if subyear > subyear_end:
                subyear = subyear_start
        print 'Submonthly variability from ' + str(subyear)

        # Set up 6-hourly file
        file_6h = output_dir + str(year) + '_6h.nc'
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

        # Set up time array
        # Hours from the beginning of subyear to the beginning of this year
        # First assume no leap years
        hours_since_subyear = (year-subyear)*365*24
        # Account for leap days between the beginning of subyear and
        # the beginning of the RCP (2006)
        hours_since_subyear += (floor((2004-subyear)/4) + 1)*24
        # Account for leap days between the beginning of the RCP (2006)
        # and the beginning of this year
        hours_since_subyear += (floor((year-2009)/4) + 1)*24
        subdaily_file = sub6_head + str(subyear) + '.nc'
        print 'Opening ' + subdaily_file
        s_id = Dataset(subdaily_file, 'r')
        # Calculate the proper time array
        o_id.variables['time'][:] = s_id.variables['time'][:] + hours_since_subyear

        # Loop over variables
        for i in range(len(var_names_6h)):
            var = var_names_6h[i]
            print 'Processing variable ' + var
            o_id.createVariable(var, 'f8', ('time', 'latitude', 'longitude'))
            o_id.variables[var].units = var_units_6h[i]

            # Read ERA-Interim monthly climatology - same every year!
            m_id = Dataset(monthly_file, 'r')
            monthly = m_id.variables[var][:,:,:]
            m_id.close()
            
            t_start = 0
            # Loop over months
            for month in range(12):
                # Figure out 6-hourly timesteps that fit within this month
                t_end = t_start + days_per_month[month]*4
                if i == 0:
                    print 'Month ' + str(month+1) + ' of ' + str(year) + '; timesteps ' + str(t_start+1) + ' to ' + str(t_end)
                # Loop over 6-hourly timesteps
                for t in range(t_start, t_end):
                    # Read submonthly variability for this timestep and add
                    # to monthly average
                    subdaily = s_id.variables[var][t,:,:]
                    var_full = monthly[month] + subdaily
                    # Impose physical limits on some variables
                    if var == 'tcc':
                        # Cloud fraction has minimum 0, maximum 1
                        index = var_full < 0
                        var_full[index] = 0.0
                        index = var_full > 1
                        var_full[index] = 1.0                       
                    o_id.variables[var][t,:,:] = var_full
                t_start = t_end
        s_id.close()
        o_id.close()

        # Increment subyear and go back to the beginning of the submonthly
        # variability cycle if needed
        subyear += 1
        if subyear > subyear_end:
            subyear = subyear_start


# Command-line interface
if __name__ == "__main__":

    no_wind_anomaly_subdaily_forcing()

    

    
