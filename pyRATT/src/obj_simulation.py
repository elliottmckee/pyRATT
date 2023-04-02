"""
Contains Definitions for all the Main, High-Level Simulation Objects
which handle the running and data from a given Simulation. 
"""

import pandas as pd
import numpy as np
import itertools 
import time
from os import path


from . import constants
from .tools_aerotherm import aerothermal_heatflux, get_net_heat_flux
from .tools_conduction import get_new_wall_temps, stability_criterion_check

# Standard Atmosphere Model/Package (CANT HANDLE HIGH-ALT)
# https://ambiance.readthedocs.io/en/latest/index.html
from ambiance import Atmosphere



class Thermal_Sim_1D:
    """
    High-level driver class representing the entirity of a 1D Thermal Simulation.

    Handles the initialization and execution of a 1D Thermal simulation, and all
    the data generated by the simulation is stored within this object.

    As the main simulation loop runs, this object passes itself, and the current
    timestep into the functions it is calling (see run() below), such that all the
    data like temperatures, heatflux, etc. is all written within those functions 
    themselves, which helps kinda keep the high-level functionality of this 
    relatively clean-ish.  


    Required Attributes/Objects:
    ----------
        WallStack : obj_wallcomponents.Wallstack object
            object representing the wall structure, material properties
        FlightProfile : obj_flightprofile.FlightProfile object
            object containing the flight trajectory data (mach, alt v. time)
        GasModel : GasModel object (see materials.gas.py)
            object representing the working fluid medium that is doing the
            aerothermal heating. This will be Air, i.e. materials_gas.AirModel
            unless you're doing a #advanced analysis and know what you're doing. 
    
    Parameters, Config Options
    ----------
        x_location: float
            downstream x location to be simulated
        deflection_angle_deg: float
            angle that your geometry is deflecting the flow, in degrees. For nose-
            cones this will be the half-angle. This is used in the shock calcs.
        t_step: float
            simulation timestep
        t_start: float
            use to override the start-time of a simulation. Basically, if you have 
            a trajectory file or something where liftoff is at t=200 seconds, you 
            can use this to jump forward, so you don't waste time simming nothing.
        t_end : float
            simulation end time. If you don't want to sim all the way until touchdown,
            use this. Reccomended, since most of what we care about, aerothermally, 
            happens in first few seconds of flight
        initial_temp : float
            initial temperature for the entire wall. TODO make this set to STDATM
            values if not specified. 
        aerothermal_model : string
            used to specify which aerothermal heating equations/models are utilized
            see tools_aerotherm.aerothermal_heatflux() for supported values 
        bound_layer_model : string
            used to specify the boundary layer behavior (laminar, turbulent, transition)
            see tools_aerotherm.aerothermal_heatflux() for supported values
        shock_type : string
            used for specifying normal, oblique, or conical shock for the upstream shock modelling
        wall_thermal_bcs: string list (of length 2)
            used for specifying the thermal boundary conditions on either side of the wall. This 
            is what allows for modelling of both nosecones and fins. Default behavior is the 
            nosecone implementation, with ["q_in_aerothermal","adiabatic"]. The current specification
            for a fun simulation would be ["q_in_aerothermal",q_in_aerothermal"]
    
    Results, Data
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
        ...
         

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
        t_step,
        x_location = None,
        deflection_angle_deg = None,
        t_start = 0.0,
        t_end = None,
        initial_temp = 290.0,
        aerothermal_model = 'default',
        boundary_layer_model = 'turbulent',
        shock_type = 'oblique',
        wall_thermal_bcs = ["q_conv", "adiabatic"],
        nose_radius = None
        #gas_model = 'air_standard'
    ):
        
        #Unavoidable gross block of passing-through variables
        self.Aerosurface            = Aerosurface 
        self.Flight                 = Flight
        self.AirModel               = AirModel
        self.x_location             = x_location
        self.deflection_angle_deg   = deflection_angle_deg 

        self.t_step                 = t_step
        self.t_start                = t_start
        self.t_end                  = t_end
        self.initial_temp           = initial_temp
        self.aerothermal_model      = aerothermal_model
        self.bound_layer_model      = boundary_layer_model
        self.shock_type             = shock_type
        self.wall_thermal_bcs       = wall_thermal_bcs
        self.nose_radius            = nose_radius
        #self.gas_model          = gas_model

        if self.deflection_angle_deg: 
            self.deflection_angle_rad   = deflection_angle_deg*constants.DEG2RAD

        #Get Vector of Wall Nodal Coordinates
        #self.y_coords               = Aerosurface.get_wall_coords() 

        #Initialize Simulation 
        self.sim_initialize()


    def sim_initialize(self):
        """
        Pre-allocate and initialize all datastructs needed to run simulation
        """

        # Generate Time Vector
        # if t_end not specified, use last value in flightsim .csv. otherwise, end at t_end
        if self.t_end is None:
            self.t_vec = np.arange(self.t_start, self.Flight.time_raw[-1], self.t_step)
        else:
            self.t_vec = np.arange(self.t_start, self.t_end, self.t_step)
            
        # get time vector size
        self.t_vec_size      = np.size(self.t_vec)

    
        ### PRE ALLOCATION OF DATA STRUCTS
        
        # Boolean Values vs. Time 
        self.bl_state   = list(itertools.repeat(0, self.t_vec_size)) # 1 is turbulent
        
        # Scalar Quantities vs. Time
        # TODO: I don't think pre-allocating matters as much in Python. May be better to 
        # more dynamically add variables to the Sim, based on the model used. Will make this
        # Sim object more flexible, ideally.

        self.q_conv     = np.zeros((self.t_vec_size,), dtype=float) # Convective Heat Flux [w/m^2]
        self.q_rad      = np.zeros((self.t_vec_size,), dtype=float) # Radiative Heat Flux [w/m^2]
        self.q_net      = np.zeros((self.t_vec_size,), dtype=float) # Net Heat Flux [w/m^2]
        self.h_coeff    = np.zeros((self.t_vec_size,), dtype=float) # Heat Transfer Coeff [w/m^2]
        
        self.p_inf      = np.zeros((self.t_vec_size,), dtype=float) # Freestream properties
        self.T_inf      = np.zeros((self.t_vec_size,), dtype=float)
        self.rho_inf    = np.zeros((self.t_vec_size,), dtype=float)
        self.mu_inf     = np.zeros((self.t_vec_size,), dtype=float)
        self.u_inf      = np.zeros((self.t_vec_size,), dtype=float)

        self.qbar_inf   = np.zeros((self.t_vec_size,), dtype=float) # Freestream dynamic pressure [Pa]
        self.Re_inf     = np.zeros((self.t_vec_size,), dtype=float) # Local Free-Stream Re, based on Sim.x_location
        
        self.T_e        = np.zeros((self.t_vec_size,), dtype=float) # Static Tempe at BL Edge
        self.T_te       = np.zeros((self.t_vec_size,), dtype=float) # Total Temp at BL Edge
        self.T_t        = np.zeros((self.t_vec_size,), dtype=float) # Freestream Total Temp
        self.T_recovery = np.zeros((self.t_vec_size,), dtype=float) # Recovery Temperature
        


        # Vector Quantities vs. Time
        
        self.wall_temps = np.zeros((self.Aerosurface.elem_tot,self.t_vec_size), dtype=float)
        #Set Initial Values for Wall Temperature at First Step
        self.wall_temps[:,0] = self.initial_temp

        self.wall_dens = np.zeros((self.Aerosurface.elem_tot,self.t_vec_size), dtype=float)
        #Set Initial Values for Wall Temperature at First Step
        self.wall_dens[:,0] = self.Aerosurface.get_densities()




        # Pre-interpolate Mach, Altitude, and Atmospheric Properties to the discrete Sim-time points 
        self.mach, self.alt = self.Flight.get_sim_time_properties(self.t_vec)

    


    def run(self):
        """ 
        High-level Simulation Run Loop

        Handles the high-level simulation loop, outputs progress as it goes.
        All (most of, actually) the data initialized in sim_initialize gets 
        written to from within the functions called within the main simulation loop.

        Notes:
        """

        print("Simulation Progress (in sim-time): ")
        time_progress_marker = self.t_vec[0] 

        ####### MAIN SIMULATION LOOP #######
        # For each timestep
        for i, t in enumerate(self.t_vec[:-1]):

            # Calculate Net Heat Flux
            get_net_heat_flux(self, i)

            # Stability Criterion Check
            stability_criterion_check(self, i)

            # Get New Wall Temperatures
            get_new_wall_temps(self, i)


            # Pass Wall Densities Out
            self.wall_dens[:,i+1] = self.Aerosurface.get_densities()

            # Update Thermal Properties of the Wall
            self.Aerosurface.update_thermal_props(self.wall_temps[:,i+1])
            


            # Update screen every 5 seconds in sim-time
            if self.t_vec[i] > time_progress_marker:  
                print(time_progress_marker, " seconds...")
                time_progress_marker += 5.0 

        #Update Coordinate at end of simulation, (only matters if ablating)
        #self.Aerosurface.update_wall_coords()
  
                

    
    def export_data_to_csv(self, out_filename):
        """
        Creates .csv of that has, at each timestep:
            - Simulation variables (mach, alt, q_conv, q_rad, etc.)
            - Element Temperatures, labelled by their location/depth into the wall

        Inputs:
            out_filename: str, output filename. duy

        TODO: 
            -Make this not-hard-coded
            - MAKE THIS NOT OVERWRITE FILES
        """

        # Extract all timeseries data dynamically (this kinda worked, but didnt implement fully cuz wanted to sort in specific way)
            #Not a Dunder, and also a 1d vector of length t_vec_size
        #timeseries_data = [x for x in dir(self) if "__" not in x and np.shape(getattr(self, x)) == (self.t_vec_size,) ]
 
        #Export Variable namelist
        #export_variables = ['t_vec', 'mach', 'alt', 'u_inf', 'p_inf', 'T_inf', 'rho_inf', 'mu_inf', 'qbar_inf','Re_inf', 'bl_state', 'q_conv', 'h_coeff', 'q_rad', 'q_net', 'T_e', 'T_recovery', 'T_t', 'T_te']
        export_variables = ['t_vec', 'mach', 'alt', 'T_inf', 'qbar_inf','Re_inf', 'bl_state', 'q_conv', 'h_coeff', 'q_rad', 'q_net', 'T_e', 'T_recovery', 'T_t', 'T_te']


        # Create Blank Dataframe
        out_data = pd.DataFrame()

        #For each of the export Variables, append 
        for var in export_variables:
            out_data[var] =  getattr(self, var)

        # For each element, append the time history of wall temperatures
        for i in range(self.Aerosurface.elem_tot):
            
            col_name = f"T_wall:y={self.Aerosurface.y_coords[i]:.4f}"
            out_data[col_name] =   self.wall_temps[i,:]
    
        #Export CSV 
        if path.exists(out_filename):
            print(f"WARNING: {out_filename} already exists. OVERWRITING...")
        
        out_data.to_csv(out_filename, index=False)

















class Thermal_Sim_0D:
    """

    """

    def __init__(
        self,
        LumpedMass,
        Flight,
        AirModel,
        t_step,
        x_location = None,
        deflection_angle_deg = None,
        t_start = 0.0,
        t_end = None,
        initial_temp = 290.0,
        aerothermal_models = ['default', 'fay_riddell'],
        boundary_layer_model = 'transition',
        shock_type = 'oblique',
        nose_radius = None,
        axisymmetric = True
        #gas_model = 'air_standard'
    ):
        
        #Unavoidable gross block of passing-through variables
        self.LumpedMass            = LumpedMass
        
        self.Flight                 = Flight
        self.AirModel               = AirModel
        self.x_location             = x_location
        self.deflection_angle_deg   = deflection_angle_deg 

        self.t_step                 = t_step
        self.t_start                = t_start
        self.t_end                  = t_end

        self.initial_temp           = initial_temp
        self.aerothermal_models      = aerothermal_models
        self.bound_layer_model      = boundary_layer_model
        self.shock_type             = shock_type
        #self.wall_thermal_bcs       = wall_thermal_bcs
        self.nose_radius            = nose_radius
        self.axisymmetric           = axisymmetric
        #self.gas_model          = gas_model

        if self.deflection_angle_deg: 
            self.deflection_angle_rad   = deflection_angle_deg*constants.DEG2RAD

        # Flags
        self.LUMPEDMASS = 1


        #Initialize Simulation 
        self.sim_initialize()


    def sim_initialize(self):
        """
        Pre-allocate and initialize all datastructs needed to run simulation
        """

        # Generate Time Vector
        # if t_end not specified, use last value in flightsim .csv. otherwise, end at t_end
        if self.t_end is None:
            self.t_vec = np.arange(self.t_start, self.Flight.time_raw[-1], self.t_step)
        else:
            self.t_vec = np.arange(self.t_start, self.t_end, self.t_step)
            
        # get time vector size
        self.t_vec_size      = np.size(self.t_vec)

    
        ### PRE ALLOCATION OF DATA STRUCTS
        
        # Boolean Values vs. Time 
        self.bl_state   = list(itertools.repeat(0, self.t_vec_size)) # 1 is turbulent
        
        # Scalar Quantities vs. Time
        # TODO: I don't think pre-allocating matters as much in Python. May be better to 
        # more dynamically add variables to the Sim, based on the model used. Will make this
        # Sim object more flexible, ideally.

        self.q_conv     = np.zeros((self.t_vec_size,), dtype=float) # Convective Heat Flux [w/m^2]
        self.q_rad      = np.zeros((self.t_vec_size,), dtype=float) # Radiative Heat Flux [w/m^2]
        self.q_net      = np.zeros((self.t_vec_size,), dtype=float) # Net Heat Flux [w/m^2]
        self.h_coeff    = np.zeros((self.t_vec_size,), dtype=float) # Heat Transfer Coeff [w/m^2]
        
        self.p_inf      = np.zeros((self.t_vec_size,), dtype=float) # Freestream properties
        self.T_inf      = np.zeros((self.t_vec_size,), dtype=float)
        self.rho_inf    = np.zeros((self.t_vec_size,), dtype=float)
        self.mu_inf     = np.zeros((self.t_vec_size,), dtype=float)
        self.u_inf      = np.zeros((self.t_vec_size,), dtype=float)

        self.qbar_inf   = np.zeros((self.t_vec_size,), dtype=float) # Freestream dynamic pressure [Pa]
        self.Re_inf     = np.zeros((self.t_vec_size,), dtype=float) # Local Free-Stream Re, based on Sim.x_location
        
        self.T_e        = np.zeros((self.t_vec_size,), dtype=float) # Static Tempe at BL Edge
        self.T_te       = np.zeros((self.t_vec_size,), dtype=float) # Total Temp at BL Edge
        self.T_t        = np.zeros((self.t_vec_size,), dtype=float) # Freestream Total Temp
        self.T_recovery = np.zeros((self.t_vec_size,), dtype=float) # Recovery Temperature
        


        # Vector Quantities vs. Time
        
        self.wall_temps = np.zeros(( 1, self.t_vec_size), dtype=float)
        #Set Initial Values for Wall Temperature at First Step
        self.wall_temps[:,0] = self.initial_temp
        self.LumpedMass.initialize_temp(self.initial_temp)

        # self.wall_dens = np.zeros((self.Aerosurface.elem_tot,self.t_vec_size), dtype=float)
        # #Set Initial Values for Wall Temperature at First Step
        # self.wall_dens[:,0] = self.Aerosurface.get_densities()



        # Pre-interpolate Mach, Altitude, and Atmospheric Properties to the discrete Sim-time points 
        self.mach, self.alt = self.Flight.get_sim_time_properties(self.t_vec)

    


    def run(self):
        """ 
        High-level Simulation Run Loop

        Handles the high-level simulation loop, outputs progress as it goes.
        All (most of, actually) the data initialized in sim_initialize gets 
        written to from within the functions called within the main simulation loop.

        Notes:
        """

        print("Simulation Progress (in sim-time): ")
        time_progress_marker = self.t_vec[0] 

        ####### MAIN SIMULATION LOOP #######
        # For each timestep
        for i, t in enumerate(self.t_vec[:-1]):

            # Calculate Net Heat Flux
            total_flux = 0.0

            for j, aeromodel in enumerate(self.aerothermal_models):

                #Set Aerothermal Model
                self.aerothermal_model = aeromodel

                #Get Net Flux
                get_net_heat_flux(self, i)

                #Extract, add to total Flux
                total_flux += self.q_net[i] * self.LumpedMass.heating_areas[j]
            
            #Override Total Flux
            self.q_net[i] = total_flux

            # Stability Criterion Check
            #stability_criterion_check(self, i)

            # Get New Wall Temperatures
            # self.LumpedMass.update_temps( self.q_net[i], self.t_step )

            self.wall_temps[0, i+1] = self.LumpedMass.update_temps( self.q_net[i], self.t_step )[0]


            # Update screen every 5 seconds in sim-time
            if self.t_vec[i] > time_progress_marker:  
                print(time_progress_marker, " seconds...")
                time_progress_marker += 5.0 

        #Update Coordinate at end of simulation, (only matters if ablating)
        #self.Aerosurface.update_wall_coords()
  
                

    
    # def export_data_to_csv(self, out_filename):
    #     """
    #     Creates .csv of that has, at each timestep:
    #         - Simulation variables (mach, alt, q_conv, q_rad, etc.)
    #         - Element Temperatures, labelled by their location/depth into the wall

    #     Inputs:
    #         out_filename: str, output filename. duy

    #     TODO: 
    #         -Make this not-hard-coded
    #         - MAKE THIS NOT OVERWRITE FILES
    #     """

    #     # Extract all timeseries data dynamically (this kinda worked, but didnt implement fully cuz wanted to sort in specific way)
    #         #Not a Dunder, and also a 1d vector of length t_vec_size
    #     #timeseries_data = [x for x in dir(self) if "__" not in x and np.shape(getattr(self, x)) == (self.t_vec_size,) ]
 
    #     #Export Variable namelist
    #     #export_variables = ['t_vec', 'mach', 'alt', 'u_inf', 'p_inf', 'T_inf', 'rho_inf', 'mu_inf', 'qbar_inf','Re_inf', 'bl_state', 'q_conv', 'h_coeff', 'q_rad', 'q_net', 'T_e', 'T_recovery', 'T_t', 'T_te']
    #     export_variables = ['t_vec', 'mach', 'alt', 'T_inf', 'qbar_inf','Re_inf', 'bl_state', 'q_conv', 'h_coeff', 'q_rad', 'q_net', 'T_e', 'T_recovery', 'T_t', 'T_te']


    #     # Create Blank Dataframe
    #     out_data = pd.DataFrame()

    #     #For each of the export Variables, append 
    #     for var in export_variables:
    #         out_data[var] =  getattr(self, var)

    #     # For each element, append the time history of wall temperatures
    #     for i in range(self.Aerosurface.elem_tot):
            
    #         col_name = f"T_wall:y={self.Aerosurface.y_coords[i]:.4f}"
    #         out_data[col_name] =   self.wall_temps[i,:]
    
    #     #Export CSV 
    #     if path.exists(out_filename):
    #         print(f"WARNING: {out_filename} already exists. OVERWRITING...")
        
    #     out_data.to_csv(out_filename, index=False)


















