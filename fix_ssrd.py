from numpy import *
from netCDF4 import Dataset

def fix_monthly ():

    directory_head = '/short/y99/kaa561/CMIP5_forcing/atmos/'
    directory_tail_raw = '_raw/'
    directory_tail = '_monthly/'
    directory_clim = directory_head + 'climatology/'
    expt_names = ['rcp45', 'rcp85']
    model_names = ['MMM', 'ACCESS1-3']
    eraint_name = 'ERA-Interim'
    var = 'ssrd'
    start_year = 2006
    end_year = 2100

    id = Dataset(directory_clim + eraint_name + '.nc', 'r')
    eraint_clim = id.variables[var][:,:,:]
    id.close()

    for model in model_names:
        print 'Model ' + model
        print 'Reading model climatology'
        id = Dataset(directory_clim + model + '.nc', 'r')
        model_clim = id.variables[var][:,:,:]
        id.close()

        for expt in expt_names:
            print 'Experiment ' + expt
            directory_raw = directory_head + expt + directory_tail_raw
            id_raw = Dataset(directory_raw + model + '.nc', 'r')
            directory = directory_head + expt + directory_tail
            id = Dataset(directory + model + '.nc', 'a')

            for year in range(start_year, end_year+1):
                start_t = 12*(year-start_year)
                end_t = start_t + 12
                model_rcp = id_raw.variables[var][start_t:end_t,:,:]
                index = model_rcp < 0
                model_rcp[index] = 0.0
                for month in range(12):
                    model_rcp[month,:,:] = model_rcp[month,:,:] - model_clim[month,:,:] + eraint_clim[month,:,:]
                index = model_rcp < 0
                model_rcp[index] = 0.0
                id.variables[var][start_t:end_t,:,:] = model_rcp
            id_raw.close()
            id.close()


def fix_subdaily (expt, model):

    monthly_file = '/short/y99/kaa561/CMIP5_forcing/atmos/' + expt + '_monthly/' + model + '.nc'
    subdaily_dir = '/short/y99/kaa561/CMIP5_forcing/atmos/climatology/ERA_Interim_variability/'
    sub12_head = subdaily_dir + '12h_variability_'
    output_dir = '/short/y99/kaa561/CMIP5_forcing/atmos/' + expt + '/' + model + '/'
    var = 'ssrd'
    year_start = 2006
    year_end = 2100
    subyear_start = 1994
    subyear_end = 2005
    days_per_month = [31,28,31,30,31,30,31,31,30,31,30,31]

    id = Dataset(monthly_file, 'r')
    lon = id.variables['longitude'][:]
    lat = id.variables['latitude'][:]
    id.close()

    subyear = subyear_start
    for year in range(year_start, year_end+1):
        print 'Processing year ' + str(year)

        if year % 4 == 0:
            days_per_month[1] = 29
        else:
            days_per_month[1] = 28
        if year == 2100:
            days_per_month[1] = 28
            subyear += 1
            if subyear > subyear_end:
                subyear = subyear_start
        print 'Submonthly variability from ' + str(subyear)

        file_12h = output_dir + str(year) + '_12h.nc'
        print 'Opening ' + file_12h
        o_id = Dataset(file_12h, 'a')

        subdaily_file = sub12_head + str(subyear) + '.nc'
        print 'Opening ' + subdaily_file
        s_id = Dataset(subdaily_file, 'r')

        m_id = Dataset(monthly_file, 'r')
        month_start = 12*(year-year_start)
        month_end = month_start + 12
        print 'Reading months ' + str(month_start+1) + ' to ' + str(month_end) + ' from ' + monthly_file
        monthly = m_id.variables[var][month_start:month_end,:,:]
        m_id.close()

        t_start = 0
        for month in range(12):
            t_end = t_start + days_per_month[month]*2
            print 'Month ' + str(month+1) + ' of ' + str(year) + '; timesteps ' + str(t_start+1) + ' to ' + str(t_end)
            for t in range(t_start, t_end):
                subdaily = s_id.variables[var][t,:,:]
                var_full = monthly[month] + subdaily
                index = var_full < 0
                var_full[index] = 0.0
                o_id.variables[var][t,:,:] = var_full
            t_start = t_end
        s_id.close()
        o_id.close()

        subyear += 1
        if subyear > subyear_end:
            subyear = subyear_start


def fix_fesom (expt, model):

    input_dir = '/short/y99/kaa561/CMIP5_forcing/atmos/' + expt + '/' + model + '/'
    output_dir = '/short/y99/kaa561/FESOM/RCP_forcing/' + expt + '/' + model + '/'
    var = 'ssrd'
    units = 'J/m^2/12h'
    file_head = 'dswrf'
    file_tails = ['_00_12.nc', '_12_12.nc']
    year_start = 2006
    year_end = 2100

    id = Dataset(input_dir + str(year_start) + '_6h.nc', 'r')
    lon = id.variables['longitude'][:]
    lat = id.variables['latitude'][:]
    id.close()

    for j in range(2):
        file_name = output_dir + file_head + file_tails[j]
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
        o_id.variables[var].units = units

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

    print 'STEP 1: Fixing monthly forcing'
    fix_monthly()
    print 'STEP 2: Fixing subdaily forcing'
    for expt in ['rcp45', 'rcp85']:
        for model in ['MMM', 'ACCESS1-3']:
            print expt + ', ' + model
            fix_subdaily(expt, model)
    print 'STEP 3: Fixing FESOM files'
    for expt in ['rcp45', 'rcp85']:
        for model in ['MMM', 'ACCESS1-3']:
            print expt + ', ' + model
            fix_fesom(expt, model)
