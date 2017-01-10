from numpy import *
from netCDF4 import Dataset

# Bias-correct the RCP monthly atmospheric forcing from ACCESS1-3 and the 
# multi-model-mean (MMM): Subtract the model's 1992-2005 climatology, and add 
# ERA-Interim's 1992-2005 climatology in its place.
# Before running this script, go into the working directory
# (eg /short/y99/kaa561/CMIP5_forcing/atmos/) and make copies of the raw
# RCP files for ACCESS1-3 and MMM as follows:
# mkdir rcp45_monthly; cp rcp45_raw/ACCESS1-3.nc rcp45_raw/MMM.nc rcp45_monthly/
# mkdir rcp85_monthly; cp rcp85_raw/ACCESS1-3.nc rcp85_raw/MMM.nc rcp85_monthly/
# These files will be bias-corrected against ERA-Interim climatology.
def rcp_forcing_monthly_atmos ():

    # Working directory, containing the subdirectories "climatology"
    # "rcp45_monthly", and "rcp85_monthly"
    directory_head = '/short/y99/kaa561/CMIP5_forcing/atmos/'
    directory_tail = '_monthly/'
    directory_clim = directory_head + 'climatology/'
    expt_names = ['rcp45', 'rcp85']
    model_names = ['MMM', 'ACCESS1-3']
    eraint_name = 'ERA-Interim'
    # CMIP5 variable names
    var_names = ['sp', 't2m', 'd2m', 'tcc', 'u10', 'v10', 'tp', 'sf', 'e', 'ssrd', 'strd']
    start_year = 2006
    end_year = 2100

    # Loop over variables
    for var in var_names:
        print 'Variable ' + var
        # Read ERA-Interim 1992-2005 climatology
        print 'Reading ERA-Interim climatology'
        id = Dataset(directory_clim + eraint_name + '.nc', 'r')
        eraint_clim = id.variables[var][:,:,:]
        id.close()

        # Loop over models
        for model in model_names:
            print 'Model ' + model
            # Read 1992-2005 climatology
            print 'Reading model climatology'
            id = Dataset(directory_clim + model + '.nc', 'r')
            model_clim = id.variables[var][:,:,:]
            id.close()

            # Loop over RCPs
            for expt in expt_names:
                print 'Experiment ' + expt
                directory = directory_head + expt + directory_tail
                id = Dataset(directory + model + '.nc', 'a')

                # Correct one year at a time
                for year in range(start_year, end_year+1):
                    start_t = 12*(year-start_year)
                    end_t = start_t + 12
                    # Read monthly output
                    model_rcp = id.variables[var][start_t:end_t,:,:]
                    # Impose physical limits on some variables
                    if var in ['tp', 'sf', 'tcc', 'ssrd']:
                        # Precipitation, snowfall, cloud fraction, shortwave have minimum 0
                        index = model_rcp < 0
                        model_rcp[index] = 0.0
                    if var == 'tcc':
                        # Cloud fraction also has maximum 1
                        index = model_rcp > 1
                        model_rcp[index] = 1.0
                    if var == 'e':
                        # Evaporation has maximum 0
                        index = model_rcp > 0
                        model_rcp[index] = 0.0

                    # Subtract model climatology and replace with ERA-Interim
                    for month in range(12):
                        model_rcp[month,:,:] = model_rcp[month,:,:] - model_clim[month,:,:] + eraint_clim[month,:,:]

                    # Impose limits again
                    if var in ['tp', 'sf', 'tcc', 'ssrd']:
                        # Precipitation, snowfall, cloud cover, shortwave have minimum 0
                        index = model_rcp < 0
                        model_rcp[index] = 0.0
                    if var == 'tcc':
                        # Cloud cover also has maximum 1
                        index = model_rcp > 1
                        model_rcp[index] = 1.0
                    if var == 'e':
                        # Evaporation has maximum 0
                        index = model_rcp > 0
                        model_rcp[index] = 0.0
                        
                    id.variables[var][start_t:end_t,:,:] = model_rcp

                id.close()
                    

# Command-line interface
if __name__ == "__main__":

    rcp_forcing_monthly_atmos()
