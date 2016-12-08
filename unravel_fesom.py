from netCDF4 import Dataset
from numpy import *

def unravel_fesom (expt, model):

    input_dir = '/short/y99/kaa561/CMIP5_forcing/atmos/' + expt + '/' + model + '/'
    output_dir = '/short/y99/kaa561/FESOM/RCP_forcing/' + expt + '/' + model + '/'
    var_names_6h = ['t2m', 'd2m', 'u10', 'v10']
    var_units_6h = ['K', 'K', 'm/s', 'm/s']
    file_heads_6h = ['tair', 'tdew', 'uwind', 'vwind']
    file_tails_6h = ['_00.nc', '_06.nc', '_12.nc', '_18.nc']
    var_names_12h = ['tp', 'sf', 'e', 'ssrd', 'strd']
    var_units_12h = ['m/12h', 'm/12h', 'm/12h', 'J/m^2/12h', 'J/m^2/12h']
    file_heads_12h = ['precip', 'snow', 'evap', 'dswrf', 'dlwrf']
    file_tails_12h = ['_00_12.nc', '_12_12.nc']
    year_start = 2006
    year_end = 2100

    id = Dataset(input_dir + str(year_start) + '_6h.nc', 'r')
    lon = id.variables['longitude'][:]
    lat = id.variables['latitude'][:]
    id.close()

    for i in range(len(var_names_6h)):
        var = var_names_6h[i]
        print 'Processing variable ' + var

        for j in range(4):
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

            t_posn = 0
            for year in range(year_start, year_end+1):
                print 'Year ' + str(year)
                id = Dataset(input_dir + str(year) + '_6h.nc', 'r')
                num_days = 365
                if year % 4 == 0 and year != 2100:
                    num_days = 366
                for t in range(num_days):
                    time = id.variables['time'][4*t+j]
                    o_id.variables['time'][t_posn] = time
                    data = id.variables[var][4*t+j,:,:]
                    o_id.variables[var][t_posn,:,:] = data
                    t_posn += 1
            o_id.close()

    for i in range(len(var_names_12h)):
        var = var_names_12h[i]
        print 'Processing variable ' + var

        for j in range(2):
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

            t_posn = 0
            for year in range(year_start, year_end+1):
                print 'Year ' + str(year)
                id = Dataset(input_dir + str(year) + '_12h.nc', 'r')
                num_days = 365
                if year % 4 == 0 and year != 2100:
                    num_days = 366
                for t in range(num_days):
                    time = id.variables['time'][2*t+j]
                    o_id.variables['time'][t_posn] = time
                    data = id.variables[var][2*t+j,:,:]
                    o_id.variables[var][t_posn,:,:] = data
                    t_posn += 1
            o_id.close()
            
        

if __name__ == "__main__":

    expt = raw_input("Experiment (rcp45 or rcp85): ")
    model = raw_input("Model name (MMM or ACCESS1-3): ")
    unravel_fesom(expt, model)
