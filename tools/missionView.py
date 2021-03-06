## missionView.py
# Import Packages
import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt
import cftime
import matplotlib.backends.backend_pdf

def main(mission_num=None, filename=None):
    '''
    @edwinrainville

    Description: A quick view of all data in a mission netCDF.

    Parameters:
        mission_nc: file name of mission netCDF file

    Returns:
        Drift tracks: Scatter plots of x and y position of the microSWIFT

        Accelerations:

        Magnetometers: 

        Gyroscope: 

        Click Through each microSWIFT in a mission 
    
    '''
    # User Inputs    
    if mission_num == None:
        mission_num = int(input('Enter mission number: '))

    # define the mission file name
    mission_nc_path = '../microSWIFT_Data/cleanedDataset/mission_{}.nc'.format(mission_num)

    # Create dataset object from the netCDF path
    mission_dataset = nc.Dataset(mission_nc_path, mode='r')

    # Define time from netCDF
    time = cftime.num2pydate(mission_dataset['time'][:], calendar=mission_dataset['time'].calendar, units=mission_dataset['time'].units)

    # Set up pdf to save figures to for each microSWIFT
    if filename == None:
        filename = 'mission_{}.pdf'.format(mission_num)
    pdf_name = '../microSWIFT_data/cleanedDataset/Figures/{}'.format(filename)
    pdf = matplotlib.backends.backend_pdf.PdfPages(pdf_name)

    # Get list of all microSWIFTs on the mission
    microSWIFTs_on_mission = list(mission_dataset.groups.keys())

    # Loop through all microSWIFTs on mission to build the mission View
    for microSWIFT in microSWIFTs_on_mission:
        print(microSWIFT)
        
        # Create map of drift tracks for the microSWIFT
        fig = plt.figure()
        fig.set_size_inches(8.5, 11)
        ax1 = fig.add_subplot(1,2,1)
        ax1.set_xlabel('FRF X Location [meters]')  
        ax1.set_ylabel('FRF Y Location [meters]')

        # Add the FRF Bathymetry to the map 
        # Data from September 28th, 2021
        # bathy_url = 'https://chlthredds.erdc.dren.mil/thredds/dodsC/frf/geomorphology/DEMs/surveyDEM/data/FRF_geomorphology_DEMs_surveyDEM_20210928.nc'
        # bathy_dataset = nc.Dataset(bathy_url)
        # # Create grid from coordinates
        # xFRF_grid, yFRF_grid = np.meshgrid(bathy_dataset['xFRF'][:],bathy_dataset['yFRF'][:])
        # bathy = bathy_dataset['elevation'][0,:,:]
        # ax1.contourf(xFRF_grid, yFRF_grid, bathy, cmap='gray')

        # Plot the microSWIFT drift track on bathymetry
        x = mission_dataset[microSWIFT]['xFRF'][:]
        y = mission_dataset[microSWIFT]['yFRF'][:]
        ax1.scatter(x, y, color='g')
        # ax1.set_xlim([np.nanmin(x)-100, np.nanmax(x)+100])
        # ax1.set_ylim([np.nanmin(y)-100, np.nanmax(y)+100])
        ax1.set_title('Drift Track for {}'.format(microSWIFT))

        # Plot the accelerations - Earth Frame
        ax2 = fig.add_subplot(4,2,2)
        ax2.plot(mission_dataset[microSWIFT]['accel_x'][:], color='g', label='accel_x')
        ax2.plot(mission_dataset[microSWIFT]['accel_y'][:], color='b', label='accel_y')
        ax2.plot(mission_dataset[microSWIFT]['accel_z'][:], color='k', label='accel_z')
        ax2.set_xlabel('Index')
        ax2.set_ylabel('Acceleration [m/s^2]')
        ax2.set_title('Accelerations - Earth Frame')
        ax2.legend(bbox_to_anchor=(0,1.04,1,0.2), loc="lower left", mode="expand", borderaxespad=0, ncol=3)
        ax2.set_xlim(0, len(time))

        # Plot Velocities - Earth Frame
        ax3 = fig.add_subplot(4,2,4)
        ax3.plot(mission_dataset[microSWIFT]['u'][:], color='g', label='u')
        ax3.plot(mission_dataset[microSWIFT]['v'][:], color='b', label='v')
        ax3.plot(mission_dataset[microSWIFT]['w'][:], color='k', label='w')
        ax3.set_xlabel('Index')
        ax3.set_ylabel('velocity [m/s]')
        ax3.set_title('Velocities - Earth Frame')
        ax3.legend(bbox_to_anchor=(0,1.04,1,0.2), loc="lower left", mode="expand", borderaxespad=0, ncol=3)
        ax3.set_xlim(0, len(time))

        # Plot Positions - Earth Frame
        ax4 = fig.add_subplot(4,2,6)
        ax4.plot(mission_dataset[microSWIFT]['eta'][:], color='k')
        ax4.set_xlabel('Index')
        ax4.set_ylabel('Sea Surface Elevation')
        ax4.set_title('Sea Surface Elevation')
        ax4.set_xlim(0, len(time))

        # Figure Properties 
        plt.tight_layout()
        ax1.set_aspect('equal')
        pdf.savefig(fig)
        plt.close()

    # Close the dataset
    mission_dataset.close()
    # bathy_dataset.close()
    pdf.close()

if __name__=='__main__':
    main()