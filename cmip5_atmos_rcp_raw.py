from cmip5_paths import *
from cmip5_field import *
from interp_model2era import *
from numpy import *
from netCDF4 import Dataset

# NB for raijin users: interp_model2era needs python/2.7.6 but the
# default is 2.7.3. Before running this script, switch them as follows:
# module unload python/2.7.3
# module unload python/2.7.3-matplotlib
# module load python/2.7.6
# module load python/2.7.6-matplotlib

def cmip5_atmos_rcp_raw (model_name):

    expt_names = ['rcp45','rcp85']
    start_year = 2006
    end_year = 2100
    num_ts = 12*(end_year-start_year+1)
    # CMIP5 variable names
    var_names = ['ps', 'tas', 'huss', 'clt', 'uas', 'vas', 'pr', 'prsn', 'evspsbl', 'rsds', 'rlds']
    # Variable names to use in NetCDF file
    var_names_output = ['sp', 't2m', 'd2m', 'tcc', 'u10', 'v10', 'tp', 'sf', 'e', 'ssrd', 'strd']
    # Units of final variables
    var_units = ['Pa', 'K', 'K', 'fraction', 'm/s', 'm/s', 'm/12h', 'm/12h', 'm/12h', 'J/m^2/12h', 'J/m^2/12h']
    # Base path for output NetCDF files
    output_base = '/short/y99/kaa561/CMIP5_forcing/atmos/'
    # Path to ERA-Interim atmospheric climatology file (created using
    # eraint_climatology_netcdf.py), just for the grid
    eraint_file = '/short/y99/kaa561/CMIP5_forcing/atmos/climatology/ERA-Interim.nc'
    # Latent heat of vapourisation, J/kg
    Lv = 2.5e6
    # Ideal gas constant for water vapour, J/K/kg
    Rv = 461.5
    # Density of water, kg/m^3
    rho_w = 1e3

    # Read ERA-Interim grid
    id = Dataset(eraint_file, 'r')
    era_lon = id.variables['longitude'][:]
    era_lat = id.variables['latitude'][:]
    id.close()

    # Loop over RCPs
    for expt in expt_names:
        print 'Processing experiment ' + expt

        output_file = output_base + expt + '_raw/' + model_name + '.nc'
        # Set up NetCDF file
        print 'Setting up ' + output_file
        id = Dataset(output_file, 'w')
        # Define dimensions
        id.createDimension('longitude', size(era_lon))
        id.createDimension('latitude', size(era_lat))
        id.createDimension('time', num_ts)
        # Define dimension variables and fill with data
        id.createVariable('longitude', 'f8', ('longitude'))
        id.variables['longitude'].units = 'degrees'
        id.variables['longitude'][:] = era_lon
        id.createVariable('latitude', 'f8', ('latitude'))
        id.variables['latitude'].units = 'degrees'
        id.variables['latitude'][:] = era_lat
        id.createVariable('time', 'f8', ('time'))
        id.variables['time'].units = 'month'
        id.variables['time'][:] = arange(1, num_ts+1)    

        # Loop over variables
        for i in range(len(var_names)):
            var = var_names[i]
            print 'Processing variable ' + var
            # Define new variable
            id.createVariable(var_names_output[i], 'f8', ('time', 'latitude', 'longitude'))
            id.variables[var_names_output[i]].units = var_units[i]
            # Read one year of data at a time
            for year in range(start_year, end_year+1):
                model_data, model_lon, model_lat, tmp = cmip5_field(model_name, expt, var, year, year)
                if model_data is None:
                    print 'Missing data'
                    return
                # Set up array for data interpolated to ERA-Interim grid
                model_data_interp = ma.empty([12, size(era_lat), size(era_lon)])
                # Interpolate one month at a time
                for t in range(12):
                    model_data_interp[t,:,:] = interp_model2era(model_data[t,:,:], model_lon, model_lat, era_lon, era_lat)
                start_t = 12*(year-start_year)
                end_t = start_t + 12

                # Conversions if necessary
                if var == 'huss':
                    # Convert from surface specific humidity to dew point
                    huss = model_data_interp[:,:,:]
                    # First read surface pressure in Pa
                    sp = id.variables['sp'][start_t:end_t,:,:]
                    # Calculate vapour pressure in Pa
                    vap_p = huss*sp/(0.622 + 0.378*huss)
                    # Now calculate dew point in K
                    model_data_interp = (1/273.0 - Rv/Lv*log(vap_p/611))**(-1)
                elif var == 'clt':
                    # Convert total cloud cover from percent to fraction
                    model_data_interp *= 0.01
                elif var in ['pr', 'prsn', 'evspsbl']:
                    # Convert precip/snowfall/evap from kg/m^2/s to m/12h
                    model_data_interp *= 12*60*60/rho_w
                    if var == 'evspsbl':
                        # Switch sign of evaporation
                        model_data_interp *= -1
                elif var in ['rsds', 'rlds']:
                    # Convert radiation from W/m^2 to J/m^2/12h
                    model_data_interp *= 12*60*60

                id.variables[var_names_output[i]][start_t:end_t,:,:] = model_data_interp

        id.close()


# Command-line interface
if __name__ == "__main__":

    # Process one model at a time
    models = build_model_list()
    for model in models:
        print model
        cmip5_atmos_rcp_raw(model)
            

            
        
