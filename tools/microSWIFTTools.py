# Tools for analyzing data from microSWIFTs
# Import modules
import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc
import cftime
import datetime
from scipy import signal
from scipy import integrate


def missionMap(mission_num, mission_dir_path, mission_nc_path):
    '''
    @edwinrainville

    '''
    # Load in netCDF file as a dataset
    mission_dataset = nc.Dataset(mission_nc_path, mode='r')
    
    # Get list of all microSWIFTs on the mission
    microSWIFTs_on_mission = list(mission_dataset.groups.keys())

    # Create map of all drift tracks during mission
    fig, ax = plt.subplots(figsize=(8,6))
    ax.set_xlabel('FRF X Location [meters]')  
    ax.set_ylabel('FRF Y Location [meters]')

    # Add the FRF Bathymetry to the map 
    # Data from September 28th, 2021
    bathy_url = 'https://chlthredds.erdc.dren.mil/thredds/dodsC/frf/geomorphology/DEMs/surveyDEM/data/FRF_geomorphology_DEMs_surveyDEM_20210928.nc'
    bathy_dataset = nc.Dataset(bathy_url)
    # Create grid from coordinates
    xFRF_grid, yFRF_grid = np.meshgrid(bathy_dataset['xFRF'][:],bathy_dataset['yFRF'][:])
    bathy = bathy_dataset['elevation'][0,:,:]
    ax.contourf(xFRF_grid, yFRF_grid, bathy, cmap='gray')

    # Sort time labels 
    initial_values_set = False
    while initial_values_set == False:
        for microSWIFT in microSWIFTs_on_mission:
            if 'GPS' in list(mission_dataset[microSWIFT].groups.keys()):
                if 'time' in list(mission_dataset[microSWIFT]['GPS'].variables):
                    # Set initial time labels
                    min_time_label = mission_dataset[microSWIFT]['GPS']['time'][0]
                    max_time_label = mission_dataset[microSWIFT]['GPS']['time'][-1]

                    # Sort x and y locations for map  
                    x, y = transform2FRF(mission_dataset[microSWIFT]['GPS']['lat'], mission_dataset[microSWIFT]['GPS']['lon']) 
                    min_x = np.min(x)
                    max_x = np.max(x)
                    min_y = np.min(y)
                    max_y = np.max(y)
                    initial_values_set = True
                else:
                    continue
            else:
                continue
                
    for microSWIFT in microSWIFTs_on_mission:
        # Compute local coordinates from each lat-lon series
        if 'GPS' in list(mission_dataset[microSWIFT].groups.keys()):
            if 'lat' and 'lon' in list(mission_dataset[microSWIFT]['GPS'].variables):
                # Transform the coordinates to the FRF coordinates
                x, y = transform2FRF(lat=mission_dataset[microSWIFT]['GPS']['lat'][:], lon=mission_dataset[microSWIFT]['GPS']['lon'][:])

                # Plot the lat-lon map with color coded points in time
                map = ax.scatter(x, y, c=mission_dataset[microSWIFT]['GPS']['time'][:], cmap='plasma')
                # reset time labels for colormap 
                if mission_dataset[microSWIFT]['GPS']['time'][0] < min_time_label:
                    min_time_label = mission_dataset[microSWIFT]['GPS']['time'][0]
                if mission_dataset[microSWIFT]['GPS']['time'][-1] > max_time_label:
                    max_time_label = mission_dataset[microSWIFT]['GPS']['time'][-1]
                # Set max and min position
                if np.min(x) < min_x:
                    min_x = np.min(x)
                if np.max(x) > max_x:
                    max_x = np.max(x)
                if np.min(y) < min_y:
                    min_y = np.min(y)
                if np.max(y) > max_y:
                    max_y = np.max(y)
                
                # Figure Properties
                time_labels = cftime.num2pydate([min_time_label, max_time_label],units=mission_dataset[microSWIFT]['GPS']['time'].units, calendar=mission_dataset[microSWIFT]['GPS']['time'].calendar)
            
    # Set colorbar and figure properties
    cbar = fig.colorbar(map, ax=ax, ticks=[min_time_label, max_time_label])
    map.set_clim([min_time_label, max_time_label])
    ax.set_xlim([min_x, max_x])
    ax.set_ylim([min_y, max_y])
    cbar.ax.set_xlabel('Time [UTC]')
    time_labels = [time_labels[0].strftime('%Y-%m-%d %H:%M'), time_labels[1].strftime('%Y-%m-%d %H:%M')]
    cbar.ax.set_yticklabels(time_labels, rotation=0, va='center')

    plt.tight_layout()
    ax.set_aspect('equal')
    figure_path = mission_dir_path + 'mission_{}_map.png'.format(mission_num)
    plt.savefig(figure_path)
    return figure_path
    
def transform2FRF(lat,lon):
    '''
    @edwinrainville, Originally written by J. Thomson, 1/2011

    Description: function to convert from lat & lon (decimal degrees, negative longitude) to FRF x,y (meters)
    '''

    # Define offsets
    lat_offset = 36.178039
    lon_offset = -75.749672

    # Define constants
    rotation = 19 #rotation in degress CCW from True north

    # Radius of Earth
    earth_rad = 6378.1 * 1000 # units are meters

    # correct radius for latitutde 
    radius_at_latoffset = earth_rad * np.cos(np.deg2rad(np.median(lat_offset))) 

    # Compute North-South and East-West Locations
    north = np.empty(lat.shape)
    east = np.empty(lon.shape)
    for n in np.arange(lat.shape[0]):
        north[n] = earth_rad * np.deg2rad(lat[n]- lat_offset)
        east[n] = radius_at_latoffset * np.deg2rad(lon_offset - lon[n]) 

    # Rotate Coordinates by 19 degrees CCW from True north
    x = east * np.cos(np.deg2rad(rotation))   -   north * np.sin (np.deg2rad(rotation))
    x = -x # Flip x 
    y = east * np.sin(np.deg2rad(rotation))   +   north * np.cos (np.deg2rad(rotation))

    # return x and y values
    return x, y

def localCoordinateTransform(lat, lon):
    '''
    @edwinrainville

    Description: This function transforms an arbitrary set of lat and lon coordinates from a mission and computes a 
    local coordinate system that has an origin at the meann value of the lat and lon coordinates. This returns the x and
    y values in the new coordinate system. Units are meters from origin.

    '''
    # Make sure that lat and lon are numpy arrays 
    lat = np.array(lat)
    lon = np.array(lon)

    # Compute origin of lat-lon coordinates
    lat_center = np.mean(lat)
    lon_center = np.mean(lon)

    # Radius of Earth
    earth_rad = 6378.1 * 1000 # units are meters

    # correct radius for latitutde 
    lon_earth_rad = np.cos(np.deg2rad(np.median(lat)))*earth_rad   

    # Compute Deviations about the lat-lon center in the new cooridnate system
    y = np.empty(lat.shape)
    x = np.empty(lon.shape)
    for n in np.arange(lat.shape[0]):
        y[n] = earth_rad * np.deg2rad(lat_center - lat[n])
        x[n] = lon_earth_rad * np.deg2rad(lon_center - lon[n])  

    # Return the x and y coordinates 
    return x, y

def computeEta(accel_z):       
    # Define the filter
    low_freq_cutoff = 0.05
    high_freq_cutoff = 2
    filt_order = 1
    fs = 12.0
    b, a = signal.butter(filt_order, [low_freq_cutoff, high_freq_cutoff], btype='bandpass', fs=fs)

    # Zero pad the edges to reduce edge effects
    pad_size = 500
    a_z_padded = np.zeros(accel_z.size + pad_size*2)
    a_z_padded[pad_size:-pad_size] = accel_z

    # Filter and integrate to velocity and position
    a_z = signal.filtfilt(b, a, a_z_padded)
    w_nofilt = integrate.cumulative_trapezoid(a_z, dx=1/fs, initial=0)
    w = signal.filtfilt(b, a, w_nofilt)
    z_nofilt = integrate.cumulative_trapezoid(w, dx=1/fs, initial=0)
    z = signal.filtfilt(b, a, z_nofilt)

    # Remove pads and Nan out edges to get rid of edge effects in the signal
    edge_removed = 100
    a_z = a_z[pad_size : -pad_size]
    a_z[:edge_removed] = np.NaN
    a_z[-edge_removed:] = np.NaN
    w = w[pad_size : -pad_size]
    w[:edge_removed] = np.NaN
    w[-edge_removed:] = np.NaN
    z = z[pad_size : -pad_size]
    z[:edge_removed] = np.NaN
    z[-edge_removed:] = np.NaN

    return w, z

def computeSpectra(z, fs):
    nperseg = 3600
    overlap = 0.50
    f_raw, E_raw = signal.welch(z, fs=fs, window='hann', nperseg=nperseg, noverlap=np.floor(nperseg*overlap))

    # Band Average the Spectra
    points_to_average = 5
    num_sections = E_raw.size // points_to_average
    f_chunks = np.array_split(f_raw, num_sections)
    E_chunks = np.array_split(E_raw, num_sections)
    f = np.array([np.mean(chunk) for chunk in f_chunks ])
    E = np.array([np.mean(chunk) for chunk in E_chunks ])
    # dof = np.floor(2 * z.shape[0]//nperseg) * points_to_average
    dof = np.floor(points_to_average * (8/3) * (z.shape[0]/ (nperseg//2)))
    return f, E, dof

def processZAccel(accel_z, fs, low_freq_cutoff, high_freq_cutoff, order):
    a_z, w, z = computeEta(accel_z, fs, low_freq_cutoff, high_freq_cutoff, order)

    # Compute the spectra
    f, E, dof = computeSpectra(z, fs)

    return a_z, w, z, f, E, dof

def computeBulkWaveParameters(f, E):
    # Compute Significant wave height 
    f_inds = np.where((f >= 0.04) & (f <= 0.5))[0]
    f_waves = np.array([f[i] for i in f_inds])
    E_waves = np.array([E[i] for i in f_inds])
    E_integrated = integrate.trapezoid(E_waves, f_waves)
    Hs = 4 * np.sqrt(E_integrated)
    
    # Compute Peak Period
    Tp = 1 / np.squeeze(f_waves[np.where(E_waves == np.amax(E_waves))])

    return Hs, Tp