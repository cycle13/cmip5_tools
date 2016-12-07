from numpy import *
from netCDF4 import Dataset

def rcp_forcing_subdaily_atmos (expt, model):

    monthly_file = '/short/y99/kaa561/CMIP5_forcing/atmos/' + expt + '_monthly/' + model + '.nc'
    subdaily_dir = '/short/y99/kaa561/CMIP5_forcing/atmos/climatology/ERA_Interim_variability/'
    sub6_head = subdaily_dir + '6h_variability_'
    sub12_head = subdaily_dir + '12h_variability_'
    output_dir = '/short/y99/kaa561/CMIP5_forcing/atmos/' + expt + '/' + model + '/'
    var_names_6h = ['sp', 't2m', 'd2m', 'tcc', 'u10', 'v10']
    var_names_12h = ['tp', 'sf', 'e', 'ssrd', 'strd']
    var_units_6h = ['Pa', 'K', 'K', 'fraction', 'm/s', 'm/s']
    var_units_12h = ['m/12h', 'm/12h', 'm/12h', 'J/m^2/12h', 'J/m^2/12h']
    year_start = 2006
    year_end = 2100
    subyear_start = 1994
    subyear_end = 2005
    days_per_month = [31,28,31,30,31,30,31,31,30,31,30,31]

    id = Dataset(monthly_file, 'r')
    lon = id.variables['longitude'][:]
    lat = id.variables['latitude'][:]
    id.close()

    subyear = subyear_start
    for year in range(year_start, year_end+1):
        print 'Processing year ' + str(year)
        print 'Submonthly variability from ' + str(subyear)

        if year % 4 == 0:
            days_per_month[1] = 29
        else:
            days_per_month[1] = 28

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
        o_id.variables['time'][:] = s_id.variables['time'][:] + hours_since_subyear

        for i in range(len(var_names_6h)):
            var = var_names_6h[i]
            print 'Processing variable ' + var
            o_id.createVariable(var, 'f8', ('time', 'latitude', 'longitude'))
            o_id.variables[var].units = var_units_6h[i]

            m_id = Dataset(monthly_file, 'r')
            month_start = 12*(year-year_start)
            month_end = month_start + 12
            if i == 0:
                print 'Reading months ' + str(month_start+1) + ' to ' + str(month_end) + ' from ' + monthly_file
            monthly = m_id.variables[var][month_start:month_end,:,:]
            m_id.close()
            
            t_start = 0
            for month in range(12):
                t_end = t_start + days_per_month[month]*4
                if i == 0:
                    print 'Month ' + str(month+1) + ' of ' + str(year) + '; timesteps ' + str(t_start+1) + ' to ' + str(t_end)
                for t in range(t_start, t_end):                    
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

        file_12h = output_dir + str(year) + '_12h.nc'
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
        subdaily_file = sub12_head + str(subyear) + '.nc'
        print 'Opening ' + subdaily_file
        s_id = Dataset(subdaily_file, 'r')
        o_id.variables['time'][:] = s_id.variables['time'][:] + hours_since_subyear

        for i in range(len(var_names_12h)):
            var = var_names_12h[i]
            print 'Processing variable ' + var
            o_id.createVariable(var, 'f8', ('time', 'latitude', 'longitude'))
            o_id.variables[var].units = var_units_12h[i]

            m_id = Dataset(monthly_file, 'r')
            month_start = 12*(year-year_start)
            month_end = month_start + 12
            if i == 0:
                print 'Reading months ' + str(month_start+1) + ' to ' + str(month_end) + ' from ' + monthly_file
            monthly = m_id.variables[var][month_start:month_end,:,:]
            m_id.close()
            
            t_start = 0
            for month in range(12):
                t_end = t_start + days_per_month[month]*2
                if i == 0:
                    print 'Month ' + str(month+1) + ' of ' + str(year) + '; timesteps ' + str(t_start+1) + ' to ' + str(t_end)
                for t in range(t_start, t_end):                    
                    subdaily = s_id.variables[var][t,:,:]
                    var_full = monthly[month] + subdaily
                    # Impose physical limits on some variables
                    if var in ['tp', 'sf']:
                        # Precipitation and snowfall have minimum 0
                        index = var_full < 0
                        var_full[index] = 0.0
                    if var == 'e':
                        # Evaporation has maximum zero
                        index = var_full > 0
                        var_full[index] = 0.0
                    o_id.variables[var][t,:,:] = var_full
                t_start = t_end
        s_id.close()
        o_id.close()        

        subyear += 1
        if subyear > subyear_end:
            subyear = subyear_start


if __name__ == "__main__":

    expt = raw_input("Experiment (rcp45 or rcp85): ")
    model = raw_input("Model name (MMM or ACCESS1-3): ")
    rcp_forcing_subdaily_atmos(expt, model)

    

    
