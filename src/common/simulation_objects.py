#Contains Definitions for all the simulation Objects we are going to want to use

import pandas
#import os
import pathlib
import numpy as np
import scipy

from typing import Optional

from ..materials.materials_standard import SolidMaterial, solidMaterialDatabase
from . import conversions



class Simulation: 
    def __init__(
        self,
        Aerosurface,
        Rocket,
        Flight,
        x_locations,
        t_step,
        initial_temp = 290.0,
        aerothermal_model = 'flat_plate',
        shock_type = 'oblique',
        gas_model = 'air_standard'
    ):
        
        self.Aerosurface        = Aerosurface 
        self.Rocket             = Rocket 
        self.Flight             = Flight
        self.x_locations        = x_locations 
        self.t_step             = t_step
        self.initial_temp       = initial_temp
        self.aerothermal_model  = aerothermal_model
        self.shock_type         = shock_type
        self.gas_model          = gas_model


    def sim_initialize(self):

        
        # Generate Time Vector (Pull last time value in Flight Data, add one step to it to make it inclusive at the end because im OCD like that)
        self.t_vec = np.arange(0.0, self.Flight.time[-1] + self.t_step, self.t_step)

        
        ### Pre-Allocate the Things
        #Scalar Quantities vs. Time
        t_vec_size      = np.size(self.t_vec)
        self.q_hot_wall = np.empty((t_vec_size,), dtype=float)
        self.h_coeff    = np.empty((t_vec_size,), dtype=float)
        self.t_recovery = np.empty((t_vec_size,), dtype=float)
        self.time_vec   = np.empty((t_vec_size,), dtype=float)

        #Vector Quantities vs. Time
        self.wall_temps = np.empty((self.Aerosurface.n_tot,t_vec_size), dtype=float)


        






    def run(self):

        #Initialize Simulation Values
        self.sim_initialize()






class WallComponent:
    def __init__(self, material, thickness: float, n_div: int, emis_override: Optional[float] = None):
        
        # Properties
        self.material  = SolidMaterial("ALU6061", emis_override)
        self.thickness = thickness
        self.n_div = n_div


        

class AerosurfaceStack: 
    # An Aerosurface Stack is the stack of Materials which makes up the through-wall direction of an Aerosurface. 
    # EX: Cork->RTV->Alu
    def __init__(
        self,
        wall_components,
        surface_type,
        interface_resistances: Optional[float] = None
    ):

        if interface_resistances is not None:
            raise Exception("I have not implemented this yet, nor do I know if the __init__ syntax for an optional list argument is correct")

        if surface_type != "nosecone":
            raise Exception("Only type: 'nosecone' has been implmented")


        self.wall_components = wall_components
        self.surface_type = surface_type


        #Calculate Total Number of elements in the Stack
        self.n_tot = 0
        
        for i in range(len(self.wall_components)):
            self.n_tot += self.wall_components[i].n_div







class Rocket:
    #High-level geometrical specification of Rocket shape n whatnot
    def __init__(self, nosecone_half_angle_deg, RAS_Filename: Optional[str] = None, nosecone_tip_radius: Optional[float] = None, nosecone_surface_roughness: Optional[float] = None):

        self.nosecone_angle_deg = nosecone_half_angle_deg                           #Degrees
        self.nosecone_angle_rad = nosecone_half_angle_deg * conversions.DEG2RAD     #Radians
        self.nosecone_tip_radius = nosecone_tip_radius
        self.nosecone_surface_roughness = nosecone_surface_roughness

        #Automatic-Parsing of CDX1 File example here
        #self.nosecone_angle, etc. = self.parse_RAS(RAS_Filename)

    def parse_RAS(RAS_Filename):
        print("RAS CDX1 Parsing Functionality not yet implemented")





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






    

























