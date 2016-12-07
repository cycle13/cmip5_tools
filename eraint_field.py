from numpy import *
from netCDF4 import Dataset

# Read ERA-Interim monthly data for the given variable name, between the given
# start and end years. Return the monthly climatology.
# Input:
# var_name = string containing name of variable, eg 't2m'
# start_year, end_year = integers containing years over which to calculate the
#                        monthly climatology, from the beginning of start_year
#                        to the end of end_year. Therefore, if start_year = 
#                        end year, this script will read one year of output
#                        with no climatological averaging.
# Output:
# era_data = 3D array of ERA-Interim data, with dimension month x latitude x
#            longitude
# era_lon = 1D array containing longitude values
# era_lat = 1D array containing latitude values
def eraint_field (var_name, start_year, end_year):

    # Directory where ERA-Interim monthly averaged data is stored
    era_dir = '/short/y99/kaa561/CMIP5_forcing/atmos/climatology/ERA_Interim_monthly/'
    # String that ERA-Interim files end with
    era_tail = '_monthly_orig.nc'

    # Read ERA-Interim latitude and longitude
    id = Dataset(era_dir + 'AN_' + str(start_year) + era_tail, 'r')
    era_lat = id.variables['lat'][:]
    era_lon = id.variables['lon'][:]
    id.close()

    # Figure out how ERA-Interim filename will start; the atmospheric
    # variables for each year are split between 3 different files
    if var_name in ['sp', 't2m', 'd2m', 'tcc', 'u10', 'v10']:
        era_head = era_dir + 'AN_'
    elif var_name in ['tp', 'sf']:
        era_head = era_dir + 'FC_'
    elif var_name in ['e', 'ssrd', 'strd']:
        era_head = era_dir + 'ER_'

    era_data = None
    # Loop over years
    for year in range(start_year, end_year+1):

        # Construct filename
        era_file = era_head + str(year) + era_tail
        # Read data
        id = Dataset(era_file, 'r')
        data = id.variables[var_name][:,:,:]
        id.close()

        # Add to master array
        if era_data is None:
            era_data = data
        else:
            era_data += data

    # Divide master array by number of years to convert from monthly sums to
    # monthly averages
    era_data /= (end_year-start_year+1)

    return era_data, era_lon, era_lat
