from cmip5_paths import *
from numpy import *
from netCDF4 import Dataset
from matplotlib.pyplot import *
from matplotlib.font_manager import FontProperties

# Create two plots: (1) the maximum zonal wind speed between 30S and 65S, and
# (2) the latitude of that maximum zonal wind speed, both against longitude.
# Plot results for ERA-Interim as well as the given CMIP5 models, averaged over
# the given season, for the 1992-2005 climatology. Note that in order to run
# this script, you must first run eraint_climatology_netcdf.py,
# cmip5_atmos_climatology_netcdf.py, and mmm_atmos_netcdf.py.
# Input:
# model_names = list of strings containing model names (either one of the CMIP5
#               models from cmip5_paths.py, or 'MMM' for the multi-model mean)
# season = string containing the season key: 'djf', 'mam', 'jja', 'son', or
#          'annual'
# save = optional boolean indicating that the plot should be saved to a file
#        rather than displayed on the screen
# fig_names = if save=True, an array of length 2 containing the names of the
#             files to save the 2 figures to
def cmip5_max_uwind (model_names, season, save=False, fig_names=None):

    # Directory where the NetCDF climatology files, creating using the scripts
    # listed above, are stored
    directory = '/short/y99/kaa561/CMIP5_forcing/atmos/climatology/'
    # Bounds on latitude to search for the maximum uwind between
    latS = -65
    latN = -30

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

    # Initialise figures
    fig1, ax1 = subplots(figsize=(12,9))
    fig2, ax2 = subplots(figsize=(12,9))

    print 'Processing ERA-Interim'
    # Read ERA-Interim grid
    id = Dataset(directory + 'ERA-Interim.nc', 'r')
    lon = id.variables['longitude'][:]
    lat = id.variables['latitude'][:]

    # Find bounds on j to extend just past latS and latN
    j_min = nonzero(lat < latN)[0][0] - 1
    j_max = nonzero(lat < latS)[0][0] + 1
    lat = lat[j_min:j_max]

    # Read ERA-Interim data
    era_data_t = id.variables['u10'][:,j_min:j_max,:]
    id.close()
    # Take time average
    era_data = None
    for month in range(12):
        if month+1 in months:
            if era_data is None:
                era_data = era_data_t[month,:,:]
            else:
                era_data += era_data_t[month,:,:]
    era_data /= len(months)
    # Find the maximum along the latitude axis for each longitude point
    era_max = amax(era_data, axis=0)
    # Find the latitude indices of these maximum values
    era_index = argmax(era_data, axis=0)
    # Find the latitude values at these indices
    era_loc = zeros(size(era_index))
    for i in range(size(era_index)):
        era_loc[i] = lat[era_index[i]]        

    # Add to plots (setting zorder means it will be on top)
    ax1.plot(lon, era_max, label='ERA-Interim', color='black', linewidth=3, zorder=num_models+1)
    ax2.plot(lon, era_loc, label='ERA-Interim', color='black', linewidth=3, zorder=num_models+1)

    # Loop over models
    for j in range(len(model_names)):
        model_name = model_names[j]
        print 'Processing ' + model_name
        # Read model data (note it has already been interpolated to ERA-Interim
        # grid)
        id = Dataset(directory + model_name + '.nc', 'r')
        model_data_t = id.variables['u10'][:,j_min:j_max,:]
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
            # Take time average
            model_data = None            
            for month in range(12):
                if month+1 in months:
                    if model_data is None:
                        model_data = model_data_t[month,:,:]
                    else:
                        model_data += model_data_t[month,:,:]
            model_data /= len(months)
            # Find the maximum along the latitude axis for each longitude point
            model_max = amax(model_data, axis=0)
            # Find the latitude indices of these maximum values
            model_index = argmax(model_data, axis=0)
            # Find the latitude values at these indices
            model_loc = zeros(size(model_index))
            for i in range(size(model_index)):
                model_loc[i] = lat[model_index[i]]
            # Add to plots
            if model_name == 'MMM':
                # Put multi-model mean second from top
                ax1.plot(lon, model_max, label=model_name, color=cmip5_colours[j], linewidth=2, zorder=num_models)
                ax2.plot(lon, model_loc, label=model_name, color=cmip5_colours[j], linewidth=2, zorder=num_models)
            else:
                ax1.plot(lon, model_max, label=model_name, color=cmip5_colours[j], linewidth=2)
                ax2.plot(lon, model_loc, label=model_name, color=cmip5_colours[j], linewidth=2)

    # Configure first plot
    ax1.set_title('Maximum zonal wind')
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('m/s')
    ax1.grid(True)
    ax1.set_xlim([0, 360])
    # Move the plot over so the legend fits
    box = ax1.get_position()
    ax1.set_position([box.x0, box.y0, box.width*0.8, box.height])
    fontP = FontProperties()
    fontP.set_size('small')
    ax1.legend(loc='center left', bbox_to_anchor=(1,0.5), prop=fontP)

    # Configure second plot
    ax2.set_title('Latitude of maximum zonal wind')
    ax2.set_xlabel('Longitude')
    ax2.set_ylabel('Latitude')
    ax2.grid(True)
    ax2.set_xlim([0, 360])
    box = ax2.get_position()
    ax2.set_position([box.x0, box.y0, box.width*0.8, box.height])
    ax2.legend(loc='center left', bbox_to_anchor=(1,0.5), prop=fontP)

    if save:
        fig1.savefig(fig_names[0])
        fig2.savefig(fig_names[1])
    else:
        fig1.show()
        fig2.show()


# Command-line interface
if __name__ == "__main__":

    # Make a list of all valid model names
    all_model_names = build_model_list()
    all_model_names.append('MMM')
    model_names = []

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

    season = raw_input("Season (djf, mam, jja, son, or annual): ")

    action = raw_input("Save figures (s) or display in window (d)? ")
    if action == 's':
        save = True
        # Get file names for both figures
        fig_name1 = raw_input("File name for first figure (maximum u10): ")
        fig_name2 = raw_input("File name for second figure (latitude of maximum u10): ")
        fig_names = [fig_name1, fig_name2]        
    elif action == 'd':
        save = False
        fig_names = None

    # Make the plots
    cmip5_max_uwind(model_names, season, save, fig_names)

    # Repeat until the user wants to exit
    while True:
        repeat = raw_input("Make another plot (y/n)? ")
        if repeat == 'y':
            while True:
                # Keep asking for changes to parameters until the user is
                # finished
                changes = raw_input("Enter a paramter to change: (1) models, (2) season, (3) save/display; or enter to continue: ")
                if len(changes) == 0:
                    break
                else:
                    if int(changes) == 1:
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
                    elif int(changes) == 2:
                        # New season
                        season = raw_input("Season (djf, mam, jja, son, or annual): ")
                    elif int(changes) == 3:
                        # Switch from save to display, or vice versa
                        save = not save
            if save:
                # Get new figure names
                fig_name1 = raw_input("File name for first figure (maximum u10): ")
                fig_name2 = raw_input("File name for second figure (latitude of maximum u10): ")
                fig_names = [fig_name1, fig_name2]
            # Make the plot
            cmip5_max_uwind(model_names, season, save, fig_names)
        else:
            break

                        
    

        
    
