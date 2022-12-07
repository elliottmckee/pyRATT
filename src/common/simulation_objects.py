#Contains Definitions for all the simulation Objects we are going to want to use

import pandas
#import os
import pathlib
import numpy as np
import scipy


# Standard Atmosphere Model/Package (CANT HANDLE HIGH-ALT)
# https://ambiance.readthedocs.io/en/latest/index.html
from ambiance import Atmosphere


from typing import Optional

from ..materials.materials_standard import SolidMaterial, solidMaterialDatabase
from . import conversions
from ..tools.aerotherm_tools import aerothermal_heatflux



class Simulation: 
    def __init__(
        self,
        Aerosurface,
        Rocket,
        Flight,
        AirModel,
        x_location,
        t_step,
        initial_temp = 290.0,
        aerothermal_model = 'flat_plate',
        boundary_layer_model = 'turbulent',
        shock_type = 'oblique',
        gas_model = 'air_standard'
    ):
        
        self.Aerosurface        = Aerosurface 
        self.Rocket             = Rocket 
        self.Flight             = Flight
        self.AirModel           = AirModel
        self.x_location         = x_location 
        self.t_step             = t_step
        self.initial_temp       = initial_temp
        self.aerothermal_model  = aerothermal_model
        self.bound_layer_model  = boundary_layer_model
        self.shock_type         = shock_type
        self.gas_model          = gas_model


    def sim_initialize(self):

        # Generate Time Vector (Pull last time value in Flight Data)
        self.t_vec = np.arange(0.0, self.Flight.time_raw[-1], self.t_step)

        ### Pre-Allocate the Things ###
        #Scalar Quantities vs. Time
        t_vec_size      = np.size(self.t_vec)
        self.q_hot_wall = np.zeros((t_vec_size,), dtype=float)
        self.h_coeff    = np.zeros((t_vec_size,), dtype=float)
        self.t_recovery = np.zeros((t_vec_size,), dtype=float)

        #Vector Quantities vs. Time
        self.wall_temps = np.zeros((self.Aerosurface.n_tot,t_vec_size), dtype=float)

        # Get/interpolate Sim-time values for Mach, Altitude, and Atmospheric Properties
        self.mach, self.alt, self.atmos = self.Flight.get_sim_time_properties(self.t_vec)


        #Set Initial Values for Wall Temperature at First Step
        self.wall_temps[:,0] = self.initial_temp






    def run(self):


        #Initialize Simulation Values
        self.sim_initialize()

        print("Warning in Sim.run(), did a bad workaround for atm_state in aerothermal_heatflux call")

        # For each time step (except for the last)
        for i, t in enumerate(self.t_vec[:-1]):
            print("Work In-Progress")


            # Calculate Aerothermal Hot-Wall Flux (possibly just pass 'self' into function to make cleaner)
            q_hw = aerothermal_heatflux(
                        Rocket              = self.Rocket,
                        AirModel            = self.AirModel,
                        T_w                 = self.wall_temps[0,i], 
                        x_location          = self.x_location, 
                        m_inf               = self.mach[i], 
                        atm_state           = Atmosphere([self.alt[i]]), 
                        shock_type          = self.shock_type,
                        aerothermal_model   = self.aerothermal_model,
                        bound_layer_model = self.bound_layer_model
            )



            # Calculate Temperature Rates of Change, and Propagate forward one time step













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

    #Not sure if I am doing this most-efficiently- may be better to just use interpolated altitudes and then use Atmosphere as a table lookup

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
        df = pandas.read_csv(trajectory_filepath, usecols=['Time (sec)', 'Mach Number', 'Altitude (ft)'])

        #Convert Pandas Dataframe Object to a Numpy Array
        df = df.to_numpy()

        #Split array into Time, Mach, and Altitude Vectors and Return
        return df[:,0], df[:,1], df[:,2]



    def get_sim_time_properties(self, t_sim_vec):
        #This Function performs the interpolation and atmospheric property lookup to change the "raw" values, which are currently
        # in the arbitrary RASAero or Flight Traj. CSV time, and aligns them with the Simulation time step and time vector

        #Interpolate Mach and altitude to Sim-time
        mach = self.mach_raw_interp(t_sim_vec)
        alt = self.alt_raw_interp(t_sim_vec)

        # Check if Clipping is needed, then Clip 
        # Ambience can only handle values from [-5004 81020] m. 
        if max(alt) > 81020:
            print("Warning in class FlightData - get_atmospheric_properties(): Max (or Min) Altitude of Atmosphere Model Exceeded- Clipping to -5004 to 81020 m")
            atmos = Atmosphere(np.clip(alt, -5004, 81020))
        else:
            atmos = Atmosphere(alt)

        return mach, alt, atmos


        



       
        
        

        





    def get_current_state(self, curr_time):
        #Interpolate Mach and Alt to whatver the current time is, return this M-Alt state

        return self.mach_interp(curr_time), self.alt_interp(curr_time)

    






    

























