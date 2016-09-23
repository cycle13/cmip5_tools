from ARCCSSive import CMIP5
from cmip5_paths import *

# Build a list of all CMIP5 models which satisfy choose_models.py and also
# have all the data we need to create RCP 4.5 and 8.5 boundary conditions,
# including subdaily winds.
def choose_models_future ():

    # Get list of models that passed choose_models.py
    all_models = build_model_list()

    cmip5 = CMIP5.connect()

    var_names = ['ps', 'tas', 'huss', 'clt', 'uas', 'vas', 'pr', 'prsn', 'evspsbl', 'rsds', 'rlds', 'thetao', 'so']

    # Loop over models and find out which ones have all the data
    good_models = []
    for model_name in all_models:
        keep = True
        # Loop over RCPs
        for expt in ['rcp45', 'rcp85']:
            # Loop over variables
            for var in var_names:
                # Subdaily winds (we need 6-hourly but they come in 3-hourly or
                # at most daily), monthly averaged everything else
                if var in ['uas', 'vas']:
                    realm = '3hr'                
                elif var in ['ps', 'tas', 'huss', 'clt', 'pr', 'prsn', 'evspsbl', 'rsds', 'rlds']:
                    realm = 'Amon'
                elif var in ['thetao', 'so']:
                    realm = 'Omon'
                else:
                    print 'Unknown variable'
                # Find all output fields
                outputs=cmip5.outputs(experiment=expt, variable=var, mip=realm, model=model_name)
                # Get file path
                try:
                    dir = outputs[0].drstree_path()
                except (IndexError):
                    dir = ''
                if len(dir) == 0:
                    # Missing data
                    keep = False
                    print 'Skipping model ' + model_name + ' because missing ' + var + ' for experiment ' + expt
        if keep:
            # All the data was there
            good_models.append(model_name)

    # Print to screen
    print 'Models that have everything we need for RCPs 4.5 and 8.5:'
    for model_name in good_models:
        print model_name

    # Check if any of the remaining models have incomplete r1i1p1 ensemble
    # Repeat the above procedure but specify r1i1p1
    ensemble_problems = []
    for model_name in good_models:
        keep = True
        for expt in ['rcp45', 'rcp85']:
            for var in var_names:
                if var in ['uas', 'vas']:
                    realm = '3hr'
                elif var in ['ps', 'tas', 'huss', 'clt', 'pr', 'prsn', 'evspsbl', 'rsds', 'rlds']:
                    realm = 'Amon'
                elif var in ['thetao', 'so']:
                    realm = 'Omon'
                else:
                    print 'Unknown variable'
                outputs = cmip5.outputs(experiment=expt, variable=var, mip=realm, model=model_name,ensemble='r1i1p1')
                try:
                    dir = outputs[0].drstree_path()
                except(IndexError):
                    dir = ''
                if len(dir) == 0:
                    keep = False
        if not keep:
            ensemble_problems.append(model_name)

    # Print to screen
    if len(ensemble_problems) > 0:
        print 'These models do not have a complete r1i1p1; check if there is another complete ensemble member: '
        for model_name in ensemble_problems:
            print model_name


# Command-line interface
if __name__ == "__main__":

    choose_models_future()

    
