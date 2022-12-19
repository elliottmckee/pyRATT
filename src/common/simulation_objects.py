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

from ..materials.materials_standard import solidMaterialDatabase
from . import conversions
from . import constants
from ..tools.aerotherm_tools import aerothermal_heatflux
from ..tools.thermal_conduction_tools import get_new_wall_temps



class Simulation: 
    def __init__(
        self,
        Aerosurface,
        Rocket,
        Flight,
        AirModel,
        x_location,
        t_step,
        t_end = None,
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
        self.t_end              = t_end
        self.initial_temp       = initial_temp
        self.aerothermal_model  = aerothermal_model
        self.bound_layer_model  = boundary_layer_model
        self.shock_type         = shock_type
        self.gas_model          = gas_model


    def sim_initialize(self):

        # Generate Time Vector (Pull last time value in Flight Data)
        #If we are clipping
        if self.t_end is not None:
            self.t_vec = np.arange(0.0, self.t_end, self.t_step)
        else:
            self.t_vec = np.arange(0.0, self.Flight.time_raw[-1], self.t_step)


        ### Pre-Allocate the Things ###
        #Scalar Quantities vs. Time
        t_vec_size      = np.size(self.t_vec)
        self.q_conv = np.zeros((t_vec_size,), dtype=float)
        self.q_net = np.zeros((t_vec_size,), dtype=float)
        self.h_coeff    = np.zeros((t_vec_size,), dtype=float)
        self.T_recovery = np.zeros((t_vec_size,), dtype=float)


        # Vector Quantities vs. Time
        self.wall_temps = np.zeros((self.Aerosurface.n_tot,t_vec_size), dtype=float)


        # Get/interpolate Sim-time values for Mach, Altitude, and Atmospheric Properties
        self.mach, self.alt, self.atmos = self.Flight.get_sim_time_properties(self.t_vec)


        #Set Initial Values for Wall Temperature at First Step
        self.wall_temps[:,0] = self.initial_temp


    def run(self):

        #Initialize Simulation Values
        self.sim_initialize()

        print("Warning in Sim.run(), did a bad workaround for atm_state in aerothermal_heatflux call")
        print("Warning: Lots of assumptions in Thermal Conduction Model")
        print("Warning: Hilarious Workaround in Aerothermal Heatflux for Overriding m_inf < 1.0 values")
        print("Simulation Progress: ")


        # For each time step (except for the last)
        for i, t in enumerate(self.t_vec[:-1]):

            # Calculate Aerothermal Hot-Wall Flux (possibly just pass 'self' into function to make cleaner)
            atm_curr = Atmosphere([self.alt[i]])
            
            self.q_conv[i], self.T_recovery[i] = aerothermal_heatflux(
                        Rocket              = self.Rocket,
                        AirModel            = self.AirModel,
                        T_w                 = self.wall_temps[0,i], 
                        x_location          = self.x_location, 
                        m_inf               = self.mach[i], 
                        atm_state           = atm_curr, 
                        shock_type          = self.shock_type,
                        aerothermal_model   = self.aerothermal_model,
                        bound_layer_model = self.bound_layer_model
            )


            # Net Heat Flux
            self.q_net[i] = self.q_conv[i] - constants.SB_CONST * self.Aerosurface.elements[0].emis * (self.wall_temps[0,i]**4 - atm_curr.temperature**4) 


            # Calculate Temperature Rates of Change, and Propagate forward one time step
            self.wall_temps[:,i+1] = get_new_wall_temps( self.wall_temps[:,i], self.q_net[i], self)

            # Print Time to screen every 5 flight seconds
            if self.t_vec[i]%5 == 0:
                print(self.t_vec[i], " seconds")

    
    def export_data_to_csv(self, out_filename = None):
        # Behavior:
        # Creates CVS of time, and each of the export_variables specified below, using those names as the column headers, 
        # followed each of the node temperatures vs time, with each node beign a different column, starting from the surface, to the inner wall, 


        # List of Variables to export
        export_variables = ['t_vec','mach','alt','q_conv', 'q_net', 'T_recovery']

        # Create Blank Dataframe
        out_data = pandas.DataFrame()

        #For each of the export Variables, append 
        for var in export_variables:
            out_data[var] =  getattr(self, var)

        # For each element, append the time history of wall temperatures
        for i in range(self.Aerosurface.n_tot):
            
            col_name = f"T_wall:x={self.Aerosurface.x_loc[i]:.4f}"
            out_data[col_name] =   self.wall_temps[i,:]

    
        #Export CSV 
        out_data.to_csv(out_filename, index=False)














class SolidMaterial:
    #Initialize, populate material properties - default to Aluminum 6061
    def __init__(self, material = "ALU6061",  emis_override: Optional[float] = None):
        
        self.rho, self.cp, self.k, self.emis = solidMaterialDatabase(material)

        #Override emissivity value if optional argument passed in
        if emis_override is not None:
            self.emis = emis_override



class WallComponent:
    def __init__(self, material, tot_thickness: float, n_nodes: int, emis_override: Optional[float] = None):
        
        # Properties
        self.Material  = SolidMaterial(material, emis_override)
        self.tot_thickness = tot_thickness
        self.n_nod = n_nodes

        #Derived
        self.el_thickness = tot_thickness / (n_nodes-1)

    
class Element:
    def __init__(
        self,
        WallComponent
    ):
        self.dy = WallComponent.el_thickness
        self.rho = WallComponent.Material.rho
        self.cp = WallComponent.Material.cp
        self.k = WallComponent.Material.k

        #Leaving this in cuz maybe some materials we won't know the emissivity of, and you only need it for the surface element
        if hasattr(WallComponent.Material, 'emis'):
            self.emis = WallComponent.Material.emis



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


        #Properties
        self.wall_components = wall_components
        self.surface_type = surface_type


        # Create List of Elements, which represents the entire Wall/Stack/Aerosurface
        self.elements = []
        self.n_tot      = 0

        #For the wall components
        for i in range(len(self.wall_components)):
            #For the number of elements in each wall section
            for j in range(self.wall_components[i].n_nod):

                #Append new element as specified by wall_component[i]
                self.elements.append( Element(self.wall_components[i]) )

            #Count total number of Elements
            self.n_tot += self.wall_components[i].n_nod

            
        #X location values array
        self.x_loc = []

        #Append new element to x_location vector, by adding an element thickness to the previous value
        for e in self.elements:
            if self.x_loc:
                self.x_loc.append( self.x_loc[-1] + e.dy)
            else:
                self.x_loc.append(0.0)






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
        raise NotImplementedError()





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
        return df[:,0], df[:,1], df[:,2]*conversions.FT2M


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

    






    

























