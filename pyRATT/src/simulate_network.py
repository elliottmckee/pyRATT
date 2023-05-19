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
# from ._tools_aerotherm import aerothermal_heatflux, get_net_heat_flux
# from .tools_conduction import get_new_wall_temps, stability_criterion_check

# Standard Atmosphere Model/Package (CANT HANDLE HIGH-ALT)
# https://ambiance.readthedocs.io/en/latest/index.html
from ambiance import Atmosphere



class TransientThermalSim:
    """
    Required Attributes/Objects:
    ----------
    - ThermalNetwork: Thermal Network object to be simulated
    
    Parameters, Config Options
    ----------
        - T_initial: Initial Temperature for all Nodes, in Kelvin
        - t_step: Simulation fixed-timestep, in Seconds
        - t_start: Start Time for simulation, in Seconds. Useful if your flight sim data or something starts at a weird time
        - t_end: End Time for simulation, in Seconds

    Results, Data
    ----------
    -

    Methods
    -------
    -

    Notes
    -------
    -
    """

    def __init__(self,
        ThermalNetwork,
        T_initial=290.0,
        t_step=0.001,
        t_start = 0.0,
        t_end = 60.0,
    ):
        
        self.ThermalNetwork = ThermalNetwork
        self.t_step             = t_step
        self.t_start            = t_start
        self.t_end              = t_end

        self.sim_initialize(T_initial)




    def sim_initialize(self, T_initial):
        """
        Pre-allocate and initialize all datastructs needed to run simulation
        """

        # Generate Time Vector
        # if t_end not specified, use last value in flightsim .csv. otherwise, end at t_end
        # if self.t_end is None:
        #     self.t_vec = np.arange(self.t_start, self.Flight.time_raw[-1], self.t_step)
        # else:
        self.t_vec = np.arange(self.t_start, self.t_end, self.t_step)
            
        # get time vector size
        self.t_vec_size      = np.size(self.t_vec)

        # Vector Quantities vs. Time
        self.ThermalNetwork.initialize_node_temps(T_initial)

        self.wall_temps = np.zeros((self.ThermalNetwork.Graph.number_of_nodes(), self.t_vec_size), dtype=float)
        self.wall_temps[:,0] = self.ThermalNetwork.get_node_temps()
        

        # Pre-interpolate Mach, Altitude, and Atmospheric Properties to the discrete Sim-time points 
        # self.Flight.get_sim_time_properties(self.t_vec)

    


    def run(self):
        """ 
        High-level Simulation Run Loop

        Notes:
        """

        print("Simulation Progress (in sim-time): ")
        time_progress_marker = self.t_vec[0] 

        ####### MAIN SIMULATION LOOP #######
        # For each timestep
        for i, t in enumerate(self.t_vec[:]):

            # Update thermal resistances (for temp-dependant material properties)
            self.ThermalNetwork.updateThermalResistances() 

            # Update Nodal Temperatures
            self.ThermalNetwork.updateNodeTemps(t, self.t_step)

            # Pull out Nodal temperatures 
            self.wall_temps[:,i] = self.ThermalNetwork.get_node_temps()

            # Update screen every 5 seconds in sim-time
            if self.t_vec[i] > time_progress_marker:  
                print(time_progress_marker, " seconds...")
                time_progress_marker += 5.0 

                
    


    
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





