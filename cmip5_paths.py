from ARCCSSive import CMIP5

# Return the directory containing monthly output for the given variable and
# experiment.
# Input:
# expt = string containing name of experiment, eg 'historical'
# var_name = string containing name of variable, eg 'tas'
# Output: 
# dir = string containing directory where the model output is stored. If this 
#       model output doesn't exist, return an empty string.
def get_directory (model_name, expt, var_name):

    cmip5 = CMIP5.connect()

    # Figure out whether it is an atmosphere or ocean variable
    if var_name in ['ps', 'tas', 'huss', 'clt', 'uas', 'vas', 'pr', 'prsn', 'evspsbl', 'rsds', 'rlds']:
        realm = 'Amon'
    elif var_name in ['thetao', 'so']:
        realm = 'Omon'
    else:
        print 'Unknown variable'
        # Exit early
        return ''

    # All the models in build_model_list have complete output for r1i1p1
    ens = 'r1i1p1'

    outputs = cmip5.outputs(experiment=expt, variable=var_name, mip=realm, model=model_name, ensemble=ens)

    try:
        dir = outputs[0].drstree_path() + '/'
    except(IndexError):
        dir = ''

    # Special cases
    if expt=='historical' and var_name=='clt' and model_name=='bcc-csm1-1-m':
        dir = '/g/data1/ua6/unofficial-ESG-replica/tmp/tree/esgf2.dkrz.de/thredds/fileServer/cmip5/output1/BCC/bcc-csm1-1-m/historical/mon/atmos/Amon/r1i1p1/v20120709/clt/'

    return dir


# Array of model names for the 27 CMIP5 models used in this project.
def build_model_list ():

    model_names = ['bcc-csm1-1', 'bcc-csm1-1-m', 'BNU-ESM', 'CanESM2', 'CNRM-CM5', 'ACCESS1-0', 'ACCESS1-3', 'CSIRO-Mk3-6-0', 'inmcm4', 'IPSL-CM5A-LR', 'IPSL-CM5A-MR', 'IPSL-CM5B-LR', 'MIROC-ESM', 'MIROC-ESM-CHEM', 'MIROC5', 'HadGEM2-CC', 'HadGEM2-ES', 'MRI-CGCM3', 'GISS-E2-H', 'GISS-E2-H-CC', 'GISS-E2-R', 'GISS-E2-R-CC', 'NorESM1-M', 'NorESM1-ME', 'GFDL-CM3', 'GFDL-ESM2G', 'GFDL-ESM2M']

    # Alphabetise
    return sorted(model_names, key=str.lower)
