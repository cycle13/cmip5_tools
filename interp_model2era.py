from numpy import *
from scipy.interpolate import RegularGridInterpolator

# NB for raijin users: RegularGridInterpolator needs python/2.7.6 but the
# default is 2.7.3. Before running this script, switch them as follows:
# module unload python/2.7.3
# module unload python/2.7.3-matplotlib
# module load python/2.7.6
# module load python/2.7.6-matplotlib

# Interpolate a given CMIP5 field to the ERA-Interim grid.
# Input:
# model_data = 2D array (size mxn) of model data for the given variable
# model_lon = 1D array (length n) of longitude for this model
# model_lat = 1D array (length m) of latitude for this model
# era_lon = 1D array (length q) of longitude on the ERA-Interim grid
# era_lat = 1D array (length p) of latitude on the ERA-Interim grid
# Output:
# data_interp = 2D array (size pxq) of model data interpolated to the
#               ERA-Interim grid 
def interp_model2era(model_data, model_lon, model_lat, era_lon, era_lat):

    # Make sure the model's longitude goes from 0 to 360, not -180 to 180
    index = model_lon < 0
    model_lon[index] = model_lon[index] + 360

    # CMIP5 model axes don't wrap around; there is a gap between almost-180W
    # and almost-180E (these are 0 to 360 but you get the idea) and depending
    # on the grid, we may need to interpolate in this gap.
    # So copy the last longitude value (mod 360) to the beginning, and the
    # first longitude value (mod 360) to the end.
    model_lon_wrap = zeros(size(model_lon)+2)
    model_lon_wrap[0] = model_lon[-1] - 360
    model_lon_wrap[1:-1] = model_lon
    model_lon_wrap[-1] = model_lon[0] + 360
    model_lon = model_lon_wrap
    # Copy the westernmost and easternmost data points to match
    model_data_wrap = ma.array(zeros((size(model_lat), size(model_lon))))
    model_data_wrap[:,1:-1] = model_data
    model_data_wrap[:,0] = model_data[:,-1]
    model_data_wrap[:,-1] = model_data[:,0]
    model_data = model_data_wrap

    if amin(model_lat) > amin(era_lat):
        # Add a point at 90S
        model_lat_new = zeros(size(model_lat)+1)
        model_data_new = ma.array(zeros((size(model_lat_new), size(model_lon))))
        if model_lat[0] > model_lat[1]:
            model_lat_new[0:-1] = model_lat
            model_lat_new[-1] = -90.0
            model_data_new[0:-1,:] = model_data
            model_data_new[-1,:] = model_data[-1,:]
        elif model_lat[0] < model_lat[1]:
            model_lat_new[1:] = model_lat
            model_lat_new[0] = -90.0
            model_data_new[1:,:] = model_data
            model_data_new[0,:] = model_data[0,:]
        model_lat = model_lat_new
        model_data = model_data_new
    if amax(model_lat) < amax(era_lat):
        # Add a point at 90N
        model_lat_new = zeros(size(model_lat)+1)
        model_data_new = ma.array(zeros((size(model_lat_new), size(model_lon))))
        if model_lat[0] > model_lat[1]:
            model_lat_new[1:] = model_lat
            model_lat_new[0] = 90.0
            model_data_new[1:,:] = model_data
            model_data_new[0,:] = model_data[0,:]
        elif model_lat[0] < model_lat[1]:
            model_lat_new[0:-1] = model_lat
            model_lat_new[-1] = 90.0
            model_data_new[0:-1,:] = model_data
            model_data_new[-1,:] = model_data[-1,:]
        model_lat = model_lat_new
        model_data = model_data_new

    # Get 2D mesh of ERA-Interim lat and lon
    era_lon_2d, era_lat_2d = meshgrid(era_lon, era_lat)
    # Build an interpolation function for model_data
    interp_function = RegularGridInterpolator((model_lat, model_lon), model_data)
    # Call it for the ERA-Interim grid
    data_interp = interp_function((era_lat_2d, era_lon_2d))

    return data_interp
