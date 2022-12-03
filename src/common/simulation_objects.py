#Contains Definitions for all the simulation Objects we are going to want to use

import pandas
#import os
import pathlib
import numpy as np
import scipy 



class FlightData:
    #Contains data for a specific Trajectory, and the functions for pulling the values we r gonna need

    #ONLY SUPPORTS RASAERO FILES AS OF RN

    def __init__(self, trajectory_file):
        
        self.trajectory_file = trajectory_file

        #Create time, mach, and alt numpy arrays
        self.time, self.mach, self.alt = self.RAS_traj_CSV_Parse(trajectory_file)

        #Create interpolation functions for both Mach and Alt, so we don't have to create these every time we want to interpolate (which we do a lot)
        self.mach_interp = scipy.interpolate.interp1d(self.time, self.mach)
        self.alt_interp  = scipy.interpolate.interp1d(self.time, self.alt)


    def RAS_traj_CSV_Parse(self, trajectory_filepath):
        #Parse the RASAero Flight Trajectory .csv and pull Time, Mach, and Alt

        #Parse the Trajectory CSV file for Mach, Alt, Time, etc. into a Pandas Dataframe
        df = pandas.read_csv(trajectory_filepath, usecols=['Time (sec)', 'Mach Number', 'Altitude (ft)'])

        #Convert Pandas Dataframe Object to a Numpy Array
        df = df.to_numpy()

        #Split array into Time, Mach, and Altitude Vectors and Return
        return df[:,0], df[:,1], df[:,2]


    def get_current_state(self, curr_time):
        #Interpolate Mach and Alt to whatver the current time is, return this M-Alt state

        return self.mach_interp(curr_time), self.alt_interp(curr_time)










    

























