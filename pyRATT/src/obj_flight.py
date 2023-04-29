import pandas as pd
import numpy as np
import scipy

from math import sqrt
from typing import Optional

# Standard Atmosphere Model/Package
# https://ambiance.readthedocs.io/en/latest/index.html
from ambiance import Atmosphere

from . import constants


class FlightProfile:
    """
    Contains all the functionality to parse, interpolate, and return values 
    from a given external flight simulation dataset.


    Attributes:
    ----------
    trajectory_file : string 
        filename/path to external trajectory file
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

    Methods:
    -------
    RAS_traj_CSV_Parse(self, trajectory_filepath)
        Parse the RASAero Flight Trajectory .csv and pull Time, Mach, and Alt
    get_sim_time_properties(self, t_sim_vec)
        This Function performs the interpolation and atmospheric property lookup to change the "raw" values, which are currently
        in the arbitrary RASAero or Flight Traj. CSV time, and aligns them with the Simulation time step and time vector
    get_current_state(self, curr_time)
        Interpolate Mach and Alt to whatver the current time is, return this M-Alt state


    Notes:
    -------
    - Only "officially" supports RASAero files rn, but if you manipulate an arbitrary .CSV files
    to have the same units and column names specified below it'll read in just fine

    """

    def __init__(self, trajectory_file):
        
        self.trajectory_file = trajectory_file

        #Create time, mach, and alt numpy arrays
        self.time_raw, self.mach_raw, self.alt_raw = self.RAS_traj_CSV_Parse(trajectory_file)

        #Create interpolation functions for both Mach and Alt, so we don't have to create these every time we want to interpolate (which we do a lot)
        self.mach_raw_interp = scipy.interpolate.interp1d(self.time_raw, self.mach_raw, kind='linear')
        self.alt_raw_interp  = scipy.interpolate.interp1d(self.time_raw, self.alt_raw, kind='linear')


    def RAS_traj_CSV_Parse(self, trajectory_filepath):
        """Parse RASAero Flight Trajectory .csv and return Time, Mach, and Alt[m] numpy vectors"""

        #Parse the Trajectory CSV file for Mach, Alt, Time, etc. into a Pandas Dataframe
        df = pd.read_csv(trajectory_filepath, usecols=['Time (sec)', 'Mach Number', 'Altitude (ft)'])

        # Mach = 0.0 breaks a lot of the math later so just overwriting it here with a small value
        df["Mach Number"].replace(to_replace = 0, value = 0.001, inplace=True)

        #Convert Pandas Dataframe Object to a Numpy Array
        df = df.to_numpy()

        #Split array into Time, Mach, and Altitude Vectors and Return
        return df[:,0], df[:,1], df[:,2]*constants.FT2M



    def get_mach_alt(self, time):
        return self.mach_raw_interp(time), self.alt_raw_interp(time)




    def get_sim_time_properties(self, t_sim_vec):
        """
        Performs the interpolation and atmospheric property lookup to change the "raw" values, which are currently
        in the arbitrary RASAero or Flight Trajectory CSV time, and aligns them with the Simulation time step and time vector
        """

        #Interpolate Mach and altitude to Sim-time
        mach = self.mach_raw_interp(t_sim_vec)
        alt = self.alt_raw_interp(t_sim_vec)

        # Check if Clipping is needed, then Clip alt vector
        # Ambience can only handle values from [-5004 81020] m. 
        if max(alt) > 81020:
            print("Warning in class FlightData - get_atmospheric_properties(): Max (or Min) Altitude of Atmosphere Model Exceeded- Clipping to -5004 to 81020 m")
            alt = np.clip(alt, -5004, 81020)
        
        self.mach_sim_time = mach
        self.alt_sim_time = alt

        return mach, alt


    def get_current_state(self, curr_time):
        """Interpolate Mach and Alt to whatver the current time is, return this Mach, Alt state"""

        return self.mach_interp(curr_time), self.alt_interp(curr_time)









    

























