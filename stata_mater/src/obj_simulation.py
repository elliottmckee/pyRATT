#Contains Definitions for all the simulation Objects we are going to want to use

import pandas as pd
import numpy as np
import itertools 
import time


from . import constants
from .tools_aerotherm import aerothermal_heatflux, get_net_heat_flux
from .tools_conduction import get_new_wall_temps, stability_criterion_check

# Standard Atmosphere Model/Package (CANT HANDLE HIGH-ALT)
# https://ambiance.readthedocs.io/en/latest/index.html
from ambiance import Atmosphere


class FlightSimulation:
    """
    (ideally) self-contained, high-level driver class for instatiating, initializing, and running a 
    aerothermal simulation along a specified flight trajectory. Stores all simulation within itself, 
    and has methods for exporting sim data as needed 

    Attributes
    ----------
    REQUIRED OBJECTS
        Aerosurface : AeroSurface object
            object representing the aerosurface being simulated
        Rocket : Rocket object
            object representing the rocket geometry
        Flight : FlightData object
            object containing the flight data for the desired flight trajectory
        AirModel : AirModel object
            object representing the free-stream/atmospheric air model
    PARAMETERS/OPTIONS
        x_location: float
            downstream x location to be simulated
        t_step: float
            simulation timestep
        t_end : float
            simulation end time
        t_vec : numpy float array
            array containing simulation time values
        initial_temp : float
            initial temperature for all of the wall surface elements
        aerothermal_model : string
            used to specify which aerothermal heating equations/models are utilized
        bound_layer_model : string
            used to specify the boundary layer behavior (laminar, turbulent, transition)
        shock_type : string
            used for specifying normal, oblique, or conical shock for the upstream shock modelling
        gas_model : ???
            ??????????????????????????????????
    RESULTS/DATA
        mach : numpy float array
            mach at each timestep
        alt : numpy float array
            altitude (clipped to atmosphere model if needed) at each timestep
        atmos : Ambience Atmosphere object
            can be used to re-create other free stream atmosphere variables, like pressure, temp, etc. 
        q_conv : numpy float 1D array  
            convective heat flux at each time step 
        q_rad : numpy float 1D array  
            radiative heat flux at each time step   
        q_net : numpy float 1D array 
            net heat flux at each time step     
        h_coeff : numpy float 1D array 
            heat transfer coefficient at each time step   
        T_stag : numpy float 1D array
            free stream stagnation or total temperature  at each time step    
        T_recovery : numpy float 1D array 
            flow recovery temperature at each time step 
        wall_temps : numpy float 2D array
            2D array, wall_temps[k,i], where k is the element number (0 is exposed/hot wall, -1 is interior wall for nosecone), and i is the simulation timestep
        
        

    Methods
    -------
    sim_initialize(self)
        Initializes simulation variables, both those required for sim, as well as empty result arrays
    run(self)
        Runs the simulation
    export_data_to_csv(self, out_filename = None)
        Exports specific data from the simulation to a .csv file



    Notes
    -------
    -
    """

    def __init__(
        self,
        Aerosurface,
        Flight,
        AirModel,
        x_location,
        deflection_angle_deg,
        t_step,
        t_start = 0.0,
        t_end = None,
        initial_temp = 290.0,
        aerothermal_model = 'flat_plate',
        boundary_layer_model = 'turbulent',
        shock_type = 'oblique',
        gas_model = 'air_standard'
    ):
        
        #really gross block of passing-through variables
        self.Aerosurface        = Aerosurface 
        self.Flight             = Flight
        self.AirModel           = AirModel
        self.x_location         = x_location
        self.deflection_angle_deg = deflection_angle_deg 
        self.deflection_angle_rad = deflection_angle_deg*constants.DEG2RAD
        self.t_step             = t_step
        self.t_start            = t_start
        self.t_end              = t_end
        self.initial_temp       = initial_temp
        self.aerothermal_model  = aerothermal_model
        self.bound_layer_model  = boundary_layer_model
        self.shock_type         = shock_type
        self.gas_model          = gas_model

        print("I am calling get_wall_coords here and in transient rn, which is redundant")
        self.y_coords           = Aerosurface.get_wall_coords() 

        #Initialize Simulation 
        self.sim_initialize()


    def sim_initialize(self):

        ### GENERATE TIME VECTOR
        # Either ends at t_end if specified, otherwise last time value in the flight data
        if self.t_end is not None:
            #If a end value is specified
            self.t_vec = np.arange(self.t_start, self.t_end, self.t_step)
        else:
            self.t_vec = np.arange(self.t_start, self.Flight.time_raw[-1], self.t_step)

        t_vec_size      = np.size(self.t_vec)

    
        ### PRE ALLOCATION OF DATA STRUCTS
        
        # Boolean Values vs. Time 
        self.bl_state   = list(itertools.repeat(0, t_vec_size)) # 1 is turbulent
        
        # Scalar Quantities vs. Time
        self.q_conv     = np.zeros((t_vec_size,), dtype=float)
        self.q_rad      = np.zeros((t_vec_size,), dtype=float)
        self.q_net      = np.zeros((t_vec_size,), dtype=float)
        self.h_coeff    = np.zeros((t_vec_size,), dtype=float)
        
        self.p_inf      = np.zeros((t_vec_size,), dtype=float)
        self.T_inf      = np.zeros((t_vec_size,), dtype=float)
        self.rho_inf    = np.zeros((t_vec_size,), dtype=float)
        self.mu_inf     = np.zeros((t_vec_size,), dtype=float)
        self.u_inf      = np.zeros((t_vec_size,), dtype=float)

        self.qbar_inf   = np.zeros((t_vec_size,), dtype=float)
        self.Re_inf     = np.zeros((t_vec_size,), dtype=float) #Free-Stream Re, based on Sim.x_location
        
        
        self.T_e        = np.zeros((t_vec_size,), dtype=float)
        self.T_te       = np.zeros((t_vec_size,), dtype=float)
        self.T_t        = np.zeros((t_vec_size,), dtype=float)
        self.T_recovery = np.zeros((t_vec_size,), dtype=float)
        

        # Vector Quantities vs. Time
        self.wall_temps = np.zeros((self.Aerosurface.n_tot,t_vec_size), dtype=float)

        # Pre-interpolate Mach, Altitude, and Atmospheric Properties to the discrete Sim-time points 
        self.mach, self.alt, self.atmos = self.Flight.get_sim_time_properties(self.t_vec)

        #Set Initial Values for Wall Temperature at First Step
        self.wall_temps[:,0] = self.initial_temp



    def run(self):

        
        print("Warning: Modifications to Stability Criterion Check Needed when Ablative is added")

        print("Simulation Progress (in sim-time): ")

        # For each time step (except for the last)
        for i, t in enumerate(self.t_vec[:-1]):

            # Calculate Aerothermal Hot-Wall Heat Flux
            aerothermal_heatflux(self, i)

            # Radiative Heat Flux
            get_net_heat_flux(self, i)

            # Check Stability Criterion
            stability_criterion_check(self, i)

            # Update Temps (this function was not writing new data when trying to write to self.wall_temps[:,i+1] from within get_new_wall_temps)
            self.wall_temps[:,i+1] = get_new_wall_temps(self, i)

            # Print Time to screen every 5 flight seconds
            if self.t_vec[i]%5 == 0:  print(self.t_vec[i], " seconds...") 
  
                

    
    def export_data_to_csv(self, out_filename):
        """
        Creates CVS of time, and each of the export_variables specified, using those names as the column headers, 
        followed each of the node temperatures vs time, with each node being a different column, starting from the surface, to the inner wall, 
        """

        # List of Simulation Variables to export
        export_variables = ['t_vec', 'mach', 'alt', 'q_conv', 'q_rad', 'q_net', 'h_coeff', 'T_stag', 'T_recovery']

        # Create Blank Dataframe
        out_data = pd.DataFrame()

        #For each of the export Variables, append 
        for var in export_variables:
            out_data[var] =  getattr(self, var)

        # For each element, append the time history of wall temperatures
        for i in range(self.Aerosurface.n_tot):
            
            col_name = f"T_wall:x={self.Aerosurface.elements[i].y:.4f}"
            out_data[col_name] =   self.wall_temps[i,:]
    
        #Export CSV 
        out_data.to_csv(out_filename, index=False)


