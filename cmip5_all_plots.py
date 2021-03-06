from cmip5_paths import *
from cmip5_plot import *

# Call cmip5_plot.py for all models (including the multi-model mean), all
# variables (atmosphere and ocean), and all seasons. The directory "cmip5/" must
# exist.
# Input: season = string containing the season key: 'djf', 'mam', 'jja', 'son',
#                 or 'annual'
def cmip5_all_plots (season):

    # All possible variable names
    var_names = ['sp', 't2m', 'd2m', 'tcc', 'u10', 'v10', 'tp', 'sf', 'e', 'ssrd', 'strd'] #, 'temp', 'salt', 'v']

    # Make a list of all possible model names
    model_names = build_model_list()
    model_names.append('MMM')
    #model_names = ['ACCESS1-3', 'HadGEM2-ES', 'GFDL-ESM2G', 'MMM']

    # Call cmip5_plot for each variable
    for i in range(len(var_names)):
        var = var_names[i]
        print 'Plotting ' + var
        cmip5_plot(var, season, model_names, True, 'cmip5/' + var + '_' + season + '.png')


# Command-line interface
if __name__ == "__main__":

    # Run for each season key at a time
    cmip5_all_plots('djf')
    cmip5_all_plots('mam')
    cmip5_all_plots('jja')
    cmip5_all_plots('son')
    cmip5_all_plots('annual')

    
                     
    
