from cmip5_paths import *
from numpy import *
from netCDF4 import Dataset
from matplotlib.pyplot import *
from matplotlib.font_manager import FontProperties

# Compare output from CMIP5 models to ERA-Interim (for atmosphere variables) or
# ECCO2 (for ocean variables) by plotting the given variable, time-averaged over
# the given season and zonally averaged over the Southern Ocean (for atmosphere
# variables) or the northern boundary of ROMS, (for ocean variables). 
# The plot will have the given variable on the x-axis and latitude
# (for atmosphere variables) or depth (for ocean variables) on the y-axis.
# Note that in order to run this script, you must have previously run:
# eraint_climatology_netcdf.py, ecco2_climatology_netcdf.py,
# cmip5_atmos_climatology_netcdf.py, cmip5_ocean_climatology_netcdf.py,
# mmm_atmos_netcdf.py, and mmm_ocean_netcdf.py
# to generate the necessary NetCDF files.
# Input:
# var = string containing name of variable to plot
# season = string containing the season key: 'djf', 'mam', 'jja', 'son', or
#          'annual'
# model_names = list of strings containing model names (either one of the CMIP5
#               models from cmip5_paths.py, or 'MMM' for the multi-model mean)
# save = optional boolean indicating that the plot should be saved to a file
#        rather than displayed on the screen
# fig_name = if save=True, the name of the file to save the plot to
def cmip5_plot (var, season, model_names, save=False, fig_name=None):

    # Directory where the NetCDF climatology files, created using the scripts
    # listed above, are stored; it is assumed it has subdirectories "atmos/"
    # and "ocean/"
    directory = '/short/y99/kaa561/CMIP5_forcing/'
    # Path to ROMS grid file
    roms_grid = '/short/m68/kaa561/ROMS-CICE-MCT/apps/common/grid/circ30S_quarterdegree_good.nc'

    # Figure out whether this is an atmosphere or ocean variable
    if var in ['sp', 't2m', 'd2m', 'tcc', 'u10', 'v10', 'tp', 'sf', 'e', 'ssrd', 'strd']:
        realm = 'atmos'
    elif var in ['temp', 'salt', 'v']:
        realm = 'ocean'
    else:
        print 'Unknown variable'
        return None
    directory = directory + realm + '/climatology/'

    # Set the plot title and units
    if var == 'sp':
        plot_title = 'Surface Pressure'
        plot_units = 'Pa'
    elif var == 't2m':
        plot_title = 'Surface Air Temperature'
        plot_units = 'K'
    elif var == 'd2m':
        plot_title = 'Surface Dew Point Temperature'
        plot_units = 'K'
    elif var == 'tcc':
        plot_title = 'Total Cloud Cover'
        plot_units = 'fraction'
    elif var == 'u10':
        plot_title = 'Eastward Wind Velocity'
        plot_units = 'm/s'
    elif var == 'v10':
        plot_title = 'Northward Wind Velocity'
        plot_units = 'm/s'
    elif var == 'tp':
        plot_title = 'Total Precipitation'
        plot_units = 'm/12h'
    elif var == 'sf':
        plot_title = 'Snowfall'
        plot_units = 'm/12h'
    elif var == 'e':
        plot_title = 'Evaporation'
        plot_units = 'm/12h'
    elif var == 'ssrd':
        plot_title = 'Downgoing Shortwave Radiation'
        plot_units = r'J/m$^2$/12h'
    elif var == 'strd':
        plot_title = 'Downgoing Longwave Radiation'
        plot_units = r'J/m$^2$/12h'
    elif var == 'temp':
        plot_title = 'Temperature'
        plot_units = r'$^{\circ}$C'
    elif var == 'salt':
        plot_title = 'Salinity'
        plot_units = 'psu'

    # 38 visually distinct (or as visually distinct as possible) colours for
    # plotting, generated using http://phrogz.net/css/distinct-colors.html
    all_cmip5_colours = [(1,0,0), (0.58,0,0), (1,0.37,0.37), (0.58,0.22,0.22), (0.37,0.14,0.14), (1,0.74,0.74), (0.58,0.43,0.43), (1,0.78,0), (0.37,0.29,0), (0.58,0.5,0.22), (0.43,1,0), (0.16,0.37,0), (0.51,0.79,0.29), (0,0.58,0.2), (0.37,1,0.59), (0.74,1,0.83), (0.43,0.58,0.48), (0.27,0.37,0.31), (0.29,0.73,0.79), (0.14,0.34,0.37), (0.74,0.96,1), (0,0.08,1), (0,0.05,0.58), (0,0.03,0.37), (0.37,0.42,1), (0.22,0.24,0.58), (0.58,0.6,0.79), (0.55,0,0.79), (0.81,0.37,1), (0.47,0.22,0.58), (0.3,0.14,0.37), (0.92,0.74,1), (0.53,0.43,0.58), (0.34,0.27,0.37), (0.58,0,0.3), (1,0.37,0.69), (0.37,0.14,0.26), (1,0.74,0.87)]
    # Figure out how many colours we need, and select them evenly from the list
    num_colours = len(all_cmip5_colours)
    num_models = len(model_names)
    cmip5_colours = []
    for i in range(num_models):
        index = int(ceil(i*float(num_colours)/num_models))
        cmip5_colours.append(all_cmip5_colours[index])

    # If MMM (multi-model-mean) is in model_names, rearrange so it comes
    # first and will get (1,0,0) bright red colour
    if 'MMM' in model_names:
        mmm_index = model_names.index('MMM')
        new_order = [mmm_index]
        for i in range(len(model_names)):
            if i != mmm_index:
                new_order.append(i)
        model_names = [model_names[i] for i in new_order]

    # Choose the month indices we are interested in, based on the season
    if season == 'djf':
        months = [12, 1, 2]
    elif season == 'mam':
        months = [3, 4, 5]
    elif season == 'jja':
        months = [6, 7, 8]
    elif season == 'son':
        months = [9, 10, 11]
    elif season == 'annual':
        months = range(1,12+1)

    # Read ROMS grid to figure out the latitude bounds on the Southern Ocean,
    # based on the latitudes of ocean cells not in ice shelf cavities
    id = Dataset(roms_grid, 'r')
    lat_rho = id.variables['lat_rho'][:,:]
    mask_rho = id.variables['mask_rho'][:,:]
    mask_zice = id.variables['mask_zice'][:,:]
    id.close()
    lat_roms = ma.masked_where(mask_rho-mask_zice==0, lat_rho)
    latS = amin(lat_roms)
    latN = amax(lat_roms)

    # Initialise figure
    fig, ax = subplots(figsize=(12,9))

    if realm == 'atmos':
        # Read ERA-Interim data and latitude axis
        print 'Processing ERA-Interim'
        id = Dataset(directory + 'ERA-Interim.nc', 'r')
        lat = id.variables['latitude'][:]        
        era_data_t = id.variables[var][:,:,:]
        id.close()
        # Take zonal average
        era_data_t = mean(era_data_t, axis=2)
        # Take time average
        era_data = None
        for month in range(12):
            if month+1 in months:
                if era_data is None:
                    era_data = era_data_t[month,:]
                else:
                    era_data += era_data_t[month,:]
        era_data /= len(months)
        # Add to plot (setting zorder means it will be on top)
        ax.plot(era_data, lat, label='ERA-Interim', color='black', linewidth=3, zorder=num_models+1)

    elif realm == 'ocean':
        # Read ECCO2 data and depth axis
        print 'Processing ECCO2'
        id = Dataset(directory + 'ECCO2.nc', 'r')
        depth = id.variables['depth'][:]
        ecco_data_t = id.variables[var][:,:,:]
        id.close()
        # Take zonal average
        ecco_data_t = mean(ecco_data_t, axis=2)
        # Take time average
        ecco_data = None
        for month in range(12):
            if month+1 in months:
                if ecco_data is None:
                    ecco_data = ecco_data_t[month,:]
                else:
                    ecco_data += ecco_data_t[month,:]
        ecco_data /= len(months)
        # Add to plot (setting zorder means it will be on top)
        ax.plot(ecco_data, depth, label='ECCO2', color='black', linewidth=3, zorder=num_models+1)

    # Loop over models
    for j in range(len(model_names)):
        model_name = model_names[j]
        print 'Processing ' + model_name
        # Read model data
        id = Dataset(directory + model_name + '.nc', 'r')
        model_data_t = id.variables[var][:,:,:]
        id.close()
        # Check for missing data
        try:
            mask = model_data_t.mask
        except(AttributeError):
            # There is no mask
            mask = False
        if all(mask):
            # Everything is masked, so the variable is missing
            pass
        else:
            # Take zonal average
            model_data_t = mean(model_data_t, axis=2)
            # Take time average
            model_data = None
            for month in range(12):
                if month+1 in months:
                    if model_data is None:
                        model_data = model_data_t[month,:]
                    else:
                        model_data += model_data_t[month,:]
            model_data /= len(months)
            # Select axis based on realm
            if realm == 'atmos':
                realm_axis = lat
            elif realm == 'ocean':
                realm_axis = depth
            # Add to plot
            if model_name == 'MMM':
                # Put multi-model mean second from top
                ax.plot(model_data, realm_axis, label=model_name, color=cmip5_colours[j], linewidth=2, zorder=num_models)
            else:
                ax.plot(model_data, realm_axis, label=model_name, color=cmip5_colours[j], linewidth=2)

    # Configure plot
    title(plot_title)
    xlabel(plot_units)
    grid(True)
    if realm == 'atmos':
        ylim([latS, latN])
        ylabel('Latitude')
    elif realm == 'ocean':
        ylabel('Depth (m)')
        gca().invert_yaxis()
    # Move the plot over so the legend fits
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width*0.8, box.height])
    fontP = FontProperties()
    fontP.set_size('small')
    ax.legend(loc='center left', bbox_to_anchor=(1,0.5), prop=fontP)

    if save:
        fig.savefig(fig_name)
    else:
        fig.show()    


# Command-line interface
if __name__ == "__main__":

    # Make a list of all valid model names
    all_model_names = build_model_list()
    all_model_names.append('MMM')
    model_names = []

    var = raw_input("Variable name: ")
    season = raw_input("Season (djf, mam, jja, son, or annual): ")

    model_name = raw_input("Model name: ")
    # Check for validity of model name
    if model_name in all_model_names:
        model_names.append(model_name)
    else:
        print 'No such model'
    while True:
        # Keep asking for more models until the user is finished
        action = raw_input("Add another model (y/n)? ")
        if action == 'y':
            model_name = raw_input("Model name: ")
            if model_name in all_model_names:
                model_names.append(model_name)
            else:
                print 'No such model'
        else:
            break

    action = raw_input("Save figure (s) or display in window (d)? ")
    if action == 's':
        save = True
        fig_name = raw_input("File name for figure: ")
    elif action == 'd':
        save = False
        fig_name = None

    # Make the plot
    cmip5_plot(var, season, model_names, save, fig_name)

    # Repeat until the user wants to exit
    while True:
        repeat = raw_input("Make another plot (y/n)? ")
        if repeat == 'y':
            while True:
                # Keep asking for changes to parameters until the user is
                # finished
                changes = raw_input("Enter a parameter to change: (1) variable, (2) season, (3) models, (4) save/display; or enter to continue: ")
                if len(changes) == 0:
                    break
                else:
                    if int(changes) == 1:
                        # New variable name
                        var = raw_input("Variable name: ")
                    elif int(changes) == 2:
                        # New season
                        season = raw_input("Season (djf, mam, jja, son, or annual): ")
                    elif int(changes) == 3:
                        # New list of models
                        model_names = []
                        model_name = raw_input("Model name: ")
                        if model_name in all_model_names:
                            model_names.append(model_name)
                        else:
                            print 'No such model'
                        while True:
                            action = raw_input("Add another model (y/n)? ")
                            if action == 'y':
                                model_name = raw_input("Model name: ")
                                if model_name in all_model_names:
                                    model_names.append(model_name)
                                else:
                                    print 'No such model'
                            else:
                                break
                    elif int(changes) == 4:
                        # Switch from save to display, or vice versa
                        save = not save
            if save:
                fig_name = raw_input("File name for figure: ")
            # Make the plot
            cmip5_plot(var, season, model_names, save, fig_name)
        else:
            break
    
                        
