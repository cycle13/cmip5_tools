from netCDF4 import Dataset
from numpy import *

# For the given experiment (RCP 4.5 or 8.5) and model (ACCESS1-3 or MMM),
# convert the final bias-corrected, submonthly-variability-added RCP forcing
# from the original file structure (two files per year, containing all 6-hourly
# variables and all 12-hourly variables) to the file structure needed by FESOM
# (four files per 6-hourly variable and two files per 12-hourly variable, each
# containing data at the same time of day for the entire length of the 
# simulation).
# Input:
# expt = 'rcp45' or 'rcp85'
# model = 'ACCESS1-0' or 'MMM'
def unravel_fesom (expt, model):

    # Path to final bias-corrected, submonthly-variability-added RCP forcing
    input_dir = '/short/y99/kaa561/CMIP5_forcing/atmos/' + expt + '/' + model + '/'
    # Desired path to output FESOM forcing
    output_dir = '/short/y99/kaa561/FESOM/RCP_forcing/' + expt + '/' + model + '/'
    # Variable names
    var_names_6h = ['sp', 't2m', 'd2m', 'u10', 'v10']
    # Variable units
    var_units_6h = ['Pa', 'K', 'K', 'm/s', 'm/s']
    # Beginning of output filename for each variable
    file_heads_6h = ['pair', 'tair', 'tdew', 'uwind', 'vwind']
    # End of output filename for each time of day
    file_tails_6h = ['_00.nc', '_06.nc', '_12.nc', '_18.nc']
    # Same for 12-hourly variables
    var_names_12h = ['tp', 'sf', 'e', 'ssrd', 'strd']
    var_units_12h = ['m/12h', 'm/12h', 'm/12h', 'J/m^2/12h', 'J/m^2/12h']
    file_heads_12h = ['precip', 'snow', 'evap', 'dswrf', 'dlwrf']
    file_tails_12h = ['_00_12.nc', '_12_12.nc']
    year_start = 2006
    year_end = 2100

    # Read grid
    id = Dataset(input_dir + str(year_start) + '_6h.nc', 'r')
    lon = id.variables['longitude'][:]
    lat = id.variables['latitude'][:]
    id.close()

    # Loop over 6-hourly variables
    for i in range(len(var_names_6h)):
        var = var_names_6h[i]
        print 'Processing variable ' + var

        # Loop over time of day
        for j in range(4):
            # Construct output filename
            file_name = output_dir + file_heads_6h[i] + file_tails_6h[j]
            print 'Setting up ' + file_name
            o_id = Dataset(file_name, 'w')
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
            o_id.createVariable(var, 'f8', ('time', 'latitude', 'longitude'))
            o_id.variables[var].units = var_units_6h[i]

            t_posn = 0  # Day of simulation
            # Loop over years
            for year in range(year_start, year_end+1):
                print 'Year ' + str(year)
                # Open input file for this year
                id = Dataset(input_dir + str(year) + '_6h.nc', 'r')
                # Figure out number of days in this year
                num_days = 365
                if year % 4 == 0 and year != 2100:
                    num_days = 366
                # Loop over days
                for t in range(num_days):
                    # Select correct index and save to output file
                    time = id.variables['time'][4*t+j]
                    o_id.variables['time'][t_posn] = time
                    data = id.variables[var][4*t+j,:,:]
                    o_id.variables[var][t_posn,:,:] = data
                    t_posn += 1
            o_id.close()

    # Loop over 12-hourly variables
    for i in range(len(var_names_12h)):
        var = var_names_12h[i]
        print 'Processing variable ' + var

        # Loop over time of day
        for j in range(2):
            # Construct output filename
            file_name = output_dir + file_heads_12h[i] + file_tails_12h[j]
            print 'Setting up ' + file_name
            o_id = Dataset(file_name, 'w')
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
            o_id.createVariable(var, 'f8', ('time', 'latitude', 'longitude'))
            o_id.variables[var].units = var_units_12h[i]

            t_posn = 0  # Day of simulation
            # Loop over years
            for year in range(year_start, year_end+1):
                print 'Year ' + str(year)
                # Open input file for this year
                id = Dataset(input_dir + str(year) + '_12h.nc', 'r')
                # Figure out number of days in this year
                num_days = 365
                if year % 4 == 0 and year != 2100:
                    num_days = 366
                # Loop over days
                for t in range(num_days):
                    # Select correct index and save to output file
                    time = id.variables['time'][2*t+j]
                    o_id.variables['time'][t_posn] = time
                    data = id.variables[var][2*t+j,:,:]
                    o_id.variables[var][t_posn,:,:] = data
                    t_posn += 1
            o_id.close()
            
        
# Command-line interface
if __name__ == "__main__":

    expt = raw_input("Experiment (rcp45 or rcp85): ")
    model = raw_input("Model name (MMM or ACCESS1-0): ")
    unravel_fesom(expt, model)
