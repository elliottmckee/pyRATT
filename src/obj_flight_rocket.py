#Contains Definitions for all the simulation Objects we are going to want to use

import pandas as pd
import numpy as np
import scipy

from math import sqrt
from typing import Optional

# Standard Atmosphere Model/Package (CANT HANDLE HIGH-ALT)
# https://ambiance.readthedocs.io/en/latest/index.html
from ambiance import Atmosphere

from . import constants


class Rocket:
    """
    Class to represent the high-level geometrical parameters of a Rocket Vehicle
    
    Example
    ----------

    Attributes
    ----------
    nosecone_angle_deg : float
        angle of nosecone half angle, in deg
    nosecone_angle_rad : float
        angle of nosecone half angle, in rad
    nosecone_tip_radius : float
        nosecone tip radius (i assume in m but i haven't implemented yet)
    nosecone_surface_roughness : float
        nosecone surface roughness (not yet implemented)
    
    Methods
    -------

    Notes
    -------
    -
    """

    #High-level geometrical specification of Rocket shape n whatnot
    def __init__(self, nosecone_half_angle_deg, RAS_Filename: Optional[str] = None, nosecone_tip_radius: Optional[float] = None, nosecone_surface_roughness: Optional[float] = None):

        self.nosecone_angle_deg     = nosecone_half_angle_deg                           #Degrees
        self.nosecone_angle_rad     = nosecone_half_angle_deg * constants.DEG2RAD     #Radians
        self.nosecone_tip_radius    = nosecone_tip_radius
        self.nosecone_surface_roughness = nosecone_surface_roughness

        #Automatic-Parsing of CDX1 File example here
        if RAS_Filename is not None:
            raise NotImplementedError("RAS CDX1 Parsing not yet implemented")
            #self.nosecone_angle, etc. = self.parse_RAS(RAS_Filename)

    # def parse_RAS(RAS_Filename):
    #     raise NotImplementedError()





class FlightData:
    """
    Class to represent an "Aerosurface Stack," which is the combined stack of all wall materials that makes up the 
    through-wall direction of an Aerosurface. 

    Example
    ----------
    SingleComponentSolidAerosurf = AerosurfaceStack(wall_components = [AluminumSolidWallComponent], surface_type = "nosecone", interface_resistances = None)

    Attributes
    ----------
    trajectory_file : string 
        list of each of the wall material components that make up the aerosurface
    time_raw : numpy array
        array containing raw time values contained in the flight trajectory file
    mach_raw : numpy array
        array containing raw mach values contained in the flight trajectory file
    alt_raw : numpy array
        array containing raw altitude values contained in the flight trajectory file
    mach_raw_interp : scipy interp1d object
        interpolation object to interpolate upon raw_time-raw_mach to get mach values at any time in the trajectory
    alt_raw_interp : scipy interp1d object
        interpolation object to interpolate upon raw_time-raw_alt to get alt values at any time in the trajectory

    Methods
    -------
    RAS_traj_CSV_Parse(self, trajectory_filepath)
        Parse the RASAero Flight Trajectory .csv and pull Time, Mach, and Alt
    get_sim_time_properties(self, t_sim_vec)
        This Function performs the interpolation and atmospheric property lookup to change the "raw" values, which are currently
        in the arbitrary RASAero or Flight Traj. CSV time, and aligns them with the Simulation time step and time vector
    get_current_state(self, curr_time)
        Interpolate Mach and Alt to whatver the current time is, return this M-Alt state


    Notes
    -------
    -Only supports RASAero Files right now
    """

    def __init__(self, trajectory_file):
        
        self.trajectory_file = trajectory_file

        #Create time, mach, and alt numpy arrays
        self.time_raw, self.mach_raw, self.alt_raw = self.RAS_traj_CSV_Parse(trajectory_file)

        #Create interpolation functions for both Mach and Alt, so we don't have to create these every time we want to interpolate (which we do a lot)
        self.mach_raw_interp = scipy.interpolate.interp1d(self.time_raw, self.mach_raw, kind='linear')
        self.alt_raw_interp  = scipy.interpolate.interp1d(self.time_raw, self.alt_raw, kind='linear')


    def RAS_traj_CSV_Parse(self, trajectory_filepath):
        #Parse the RASAero Flight Trajectory .csv and pull Time, Mach, and Alt

        #Parse the Trajectory CSV file for Mach, Alt, Time, etc. into a Pandas Dataframe
        df = pd.read_csv(trajectory_filepath, usecols=['Time (sec)', 'Mach Number', 'Altitude (ft)'])

        #Convert Pandas Dataframe Object to a Numpy Array
        df = df.to_numpy()

        #Split array into Time, Mach, and Altitude Vectors and Return
        return df[:,0], df[:,1], df[:,2]*constants.FT2M


    def get_sim_time_properties(self, t_sim_vec):
        #This Function performs the interpolation and atmospheric property lookup to change the "raw" values, which are currently
        # in the arbitrary RASAero or Flight Traj. CSV time, and aligns them with the Simulation time step and time vector

        #Interpolate Mach and altitude to Sim-time
        mach = self.mach_raw_interp(t_sim_vec)
        alt = self.alt_raw_interp(t_sim_vec)

        # Check if Clipping is needed, then Clip alt vector
        # Ambience can only handle values from [-5004 81020] m. 
        if max(alt) > 81020:
            print("Warning in class FlightData - get_atmospheric_properties(): Max (or Min) Altitude of Atmosphere Model Exceeded- Clipping to -5004 to 81020 m")
            alt = np.clip(alt, -5004, 81020)
            
        atmos = Atmosphere(alt)


        return mach, alt, atmos


    def get_current_state(self, curr_time):
        #Interpolate Mach and Alt to whatver the current time is, return this M-Alt state

        return self.mach_interp(curr_time), self.alt_interp(curr_time)




def convert_AVA_traj_to_RAS(AVA_traj_filepath, out_filepath):
    #Standalone function to convert the AVA flight data format into a format that will work in FlightData

    # Parse the Trajectory CSV file for Mach, Alt, Time, etc. into a Pandas Dataframe
    #df = pandas.read_csv( AVA_traj_filepath, header=0, skiprows=range(1, 269), usecols=['Flight Time(s)', ' Pos xi(m)', 'Vel xi(m/s)'])
    #df = pandas.read_csv( AVA_traj_filepath, header=0, skiprows=range(1, 269), usecols=['time', 'altitude', 'speed'])
    

    # Convert Pandas Dataframe Object to a Numpy Array
    df = df.dropna()
    df = df.to_numpy()

    # Offset Altitude
    print("Offsetting Altitude using FAR altitude: 609.6m, converting to feet")

    alt = (df[:,2] + 609.6) / constants.FT2M

    # Pre-Allocate Mach Array
    mach = np.zeros(np.shape(alt))

    #Get Current Atmosphere State   
    for i in range(np.size(mach)):   

        a = sqrt(1.4 * 287.0 * Atmosphere([alt[i]]).temperature)
        mach[i] = df[i,1] / a
    

    #from scipy.signal import savgol_filter
    alt = scipy.signal.savgol_filter(alt, window_length=61, polyorder=3, mode="nearest")
    mach = scipy.signal.savgol_filter(mach, window_length=41, polyorder=3, mode="nearest") 
    mach = np.clip(mach, a_min = 0.0, a_max = 5.0)
    
    d = {'Time (sec)': df[:,0], 'Mach Number': mach, 'Altitude (ft)': alt}

    out_df = pd.DataFrame(data=d)
    out_df.to_csv(out_filepath, sep=',', index=False)

    return 







    

























