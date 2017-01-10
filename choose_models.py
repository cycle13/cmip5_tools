from ARCCSSive import CMIP5
from cmip5_paths import *

# Build a list of all CMIP5 models that have the data we need for the historical
# RMS error analysis.
def choose_models ():

    cmip5 = CMIP5.connect()
    # Get a list of all models in the database
    all_models = cmip5.models()
    good_models = []

    # Variables we care about
    var_names = ['ps', 'tas', 'huss', 'clt', 'uas', 'vas', 'pr', 'prsn', 'evspsbl', 'rsds', 'rlds', 'thetao', 'so', 'vo']

    # Loop over models and find out which ones have all the data
    for model_name in all_models:
        keep = True
        # Loop over variables
        for var in var_names:
            # Monthly averaged variables
            if var in ['ps', 'tas', 'huss', 'clt', 'uas', 'vas', 'pr', 'prsn', 'evspsbl', 'rsds', 'rlds']:
                realm = 'Amon'
            elif var in ['thetao', 'so', 'vo']:
                realm = 'Omon'
            else:
                print 'Unknown variable'
            # Find all output fields
            outputs=cmip5.outputs(experiment='historical', variable=var, mip=realm, model=model_name)
            # Get file path
            try:
                dir = outputs[0].drstree_path()
            except (IndexError):
                dir = ''
            # Special case
            if var == 'clt' and model_name == 'bcc-csm1-1-m':
                dir = '/g/data1/ua6/unofficial-ESG-replica/tmp/tree/esgf2.dkrz.de/thredds/fileServer/cmip5/output1/BCC/bcc-csm1-1-m/historical/mon/atmos/Amon/r1i1p1/v20120709/clt/'
            if len(dir) == 0:
                # Missing data
                keep = False
                print 'Skipping model ' + model_name + ' because missing ' + var
        if keep:
            # All the data was there
            good_models.append(str(model_name))

    # Alphabetise and print to screen
    good_models = sorted(good_models, key=str.lower)
    print 'Models that have all variables: '
    for model_name in good_models:
        print model_name

    # Check if any of the remaining models have incomplete r1i1p1 ensemble
    ensemble_problems = []
    for model_name in good_models:
        keep = True
        for var in var_names:
            # Call the function in cmip5_paths which assumes r1i1p1
            dir = get_directory(model_name, 'historical', var)
            if len(dir) == 0:
                keep = False
        if not keep:
            ensemble_problems.append(model_name)

    # Print to screen
    if len(ensemble_problems) > 0:
        print 'These models do not have a complete r1i1p1; check if there is another complete ensemble member:'
        for model_name in ensemble_problems:
            print model_name


# Command-line interface
if __name__ == "__main__":

    choose_models()

    
