from ARCCSSive import CMIP5

# Return the directory containing monthly output for the given variable and
# experiment.
# Input:
# expt = string containing name of experiment, eg 'historical'
# var_name = string containing name of variable, eg 'tas'
# Output: dir = string containing directory where the model output is
#               stored. If this model output doesn't exist, return an
#               empty string.
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

    # Choose ensemble
    ens = 'r1i1p1'
    if model_name == 'EC-EARTH':
        if realm == 'Amon':
            ens = 'r8i1p1'
        elif realm == 'Omon':
            ens = 'r6i1p1'

    outputs = cmip5.outputs(experiment=expt, variable=var_name, mip=realm, model=model_name, ensemble=ens)

    try:
        dir = outputs[0].drstree_path() + '/'
    except(IndexError):
        dir = ''

    return dir


# Array of model names for the 39 CMIP5 models used in this project.
def build_model_list ():

    return ['bcc-csm1-1', 'bcc-csm1-1-m', 'BNU-ESM', 'CanESM2', 'CMCC-CM', 'CMCC-CMS', 'CNRM-CM5', 'ACCESS1-0', 'ACCESS1-3', 'CSIRO-Mk3-6-0', 'FIO-ESM', 'EC-EARTH', 'inmcm4', 'IPSL-CM5A-LR', 'IPSL-CM5A-MR', 'IPSL-CM5B-LR', 'FGOALS-g2', 'MIROC-ESM', 'MIROC-ESM-CHEM', 'MIROC5', 'HadGEM2-CC', 'HadGEM2-ES', 'MPI-ESM-LR', 'MPI-ESM-MR', 'MRI-CGCM3', 'GISS-E2-H', 'GISS-E2-H-CC', 'GISS-E2-R', 'GISS-E2-R-CC', 'CCSM4', 'NorESM1-M', 'NorESM1-ME', 'HadGEM2-AO', 'GFDL-CM3', 'GFDL-ESM2G', 'GFDL-ESM2M', 'CESM1-BGC', 'CESM1-CAM5', 'CESM1-WACCM']
