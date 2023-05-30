"""
Contains Definitions for all the Main, High-Level Simulation Objects
which handle the running and data from a given Simulation. 
"""

import numpy as np
import pandas as pd
import itertools 
import time
import os 
from pathlib import Path
#from sys import path

import matplotlib
matplotlib.use('TkAgg')  # or 'QtAgg', 'TkAgg'

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


from . import constants
# from ._tools_aerotherm import aerothermal_heatflux, get_net_heat_flux
# from .tools_conduction import get_new_wall_temps, stability_criterion_check

# Standard Atmosphere Model/Package (CANT HANDLE HIGH-ALT)
# https://ambiance.readthedocs.io/en/latest/index.html
from ambiance import Atmosphere

# Setting up fonts for plotting cuz im a nerd
font_dir = os.path.dirname(__file__)  # Get the directory of the script
custom_font_path = Path(os.path.join( os.path.dirname(os.path.dirname(__file__)), 'fonts', 'ProFontWindows.ttf'))



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
        Flight = None
    ):
        
        self.ThermalNetwork = ThermalNetwork
        self.t_step             = t_step
        self.t_start            = t_start
        self.t_end              = t_end

        self.sim_initialize(T_initial)

        # Only used for plotting
        if Flight:
            self.Flight = Flight
            # Pre-interpolate Mach, Altitude, and Atmospheric Properties to the discrete Sim-time points for plotting
            self.Flight.get_sim_time_properties(self.t_vec)





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

        return 0



    def plot_temp_trace_results(self):

        custom_font = FontProperties(fname=custom_font_path, size=16)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 10), facecolor='black')

        ax1.set_facecolor("black")
        ax1.spines['top'].set_edgecolor("white")
        ax1.spines['bottom'].set_edgecolor("white")
        ax1.spines['left'].set_edgecolor("white")
        ax1.spines['right'].set_edgecolor("white")

        ax2.set_facecolor("black")
        ax2.spines['top'].set_edgecolor("white")
        ax2.spines['bottom'].set_edgecolor("white")
        ax2.spines['left'].set_edgecolor("white")
        ax2.spines['right'].set_edgecolor("white")


        # First Plot
        ax1.set_title(f'Temperature Time Trace\n Max Surface Temp: {np.max(self.wall_temps[0,:]):.3f} K', color='white', font=custom_font_path, fontsize=20)
        #ax1.set_xlabel('Time', color='white', font=custom_font_path, fontsize=18)
        ax1.set_ylabel('Temperature [K]', color='#ff3544', font=custom_font_path, fontsize=18)
        ax1.tick_params(colors="white")
        
        ax1.grid(color="#1a1a1a",which='major')

        ax1.plot(self.t_vec, self.wall_temps[0,:], linewidth=2, color='#ff3544', label="Outer Surface")
        ax1.plot(self.t_vec, np.mean(self.wall_temps, 0), linewidth=2, color='#ff8000', label="Average")
        ax1.plot(self.t_vec, self.wall_temps[-1,:], linewidth=2, color='#01d1fe', label="Inner Surface")
        ax1.xaxis.set_ticklabels(ax1.xaxis.get_ticklabels(), fontproperties=custom_font)
        ax1.yaxis.set_ticklabels(ax1.yaxis.get_ticklabels(), fontproperties=custom_font)

        legend = ax1.legend( prop=custom_font )
        legend.get_frame().set_facecolor('none')  # Set the background color to blue
        for text in legend.get_texts(): text.set_color('white')


        # Second Plot Left
        ax2.set_title('Trajectory', color='white', font=custom_font_path, fontsize=20)
        ax2.set_xlabel('Time [s]', color='white', font=custom_font_path, fontsize=18)
        ax2.set_ylabel('Mach', color='#ff3544', font=custom_font_path, fontsize=18)
        ax2.tick_params(colors="white")
        ax2.grid(color="#1a1a1a",which='major')

        ax2.plot(self.t_vec, self.Flight.mach_sim_time, linewidth=2, color='#ff3544', label="Outer Surface")
        ax2.xaxis.set_ticklabels(ax1.xaxis.get_ticklabels(), fontproperties=custom_font)
        ax2.yaxis.set_ticklabels(ax2.yaxis.get_ticklabels(), fontproperties=custom_font)


        # Second Plot Right
        ax2_right = ax2.twinx()
        ax2_right.spines['top'].set_edgecolor("white")
        ax2_right.spines['bottom'].set_edgecolor("white")
        ax2_right.spines['left'].set_edgecolor("white")
        ax2_right.spines['right'].set_edgecolor("white")
        ax2_right.set_ylabel('Alt [Km]', color='#01d1fe', font=custom_font_path, fontsize=18)
        ax2_right.tick_params(colors="white")
        #ax2_right.grid(color="#1a1a1a",which='major')

        ax2_right.plot(self.t_vec, self.Flight.alt_sim_time/1000, linewidth=2, color='#01d1fe', label="Inner Surface")
        ax2_right.yaxis.set_ticklabels(ax2_right.yaxis.get_ticklabels(), fontproperties=custom_font)


        plt.subplots_adjust(hspace=0.2)
        plt.show()


    


    
    def export_data_to_csv(self, out_filename):
        """
        Creates .csv of that has, at each timestep:
            - Element Temperatures, labelled by their location/depth into the wall

        Inputs:
            out_filename: str, output filename. duy

        TODO:
            - Simulation variables (mach, alt, q_conv, q_rad, etc.)
            - Re-add coordinates
            -Make this not-hard-coded
            - MAKE THIS NOT OVERWRITE FILES
        """

        #Export Variable namelist
        #export_variables = ['t_vec', 'mach', 'alt', 'T_inf', 'qbar_inf','Re_inf', 'bl_state', 'q_conv', 'h_coeff', 'q_rad', 'q_net', 'T_e', 'T_recovery', 'T_t', 'T_te']

        # Create Blank Dataframe
        out_data = pd.DataFrame()

        #For each of the export Variables, append 
        # for var in export_variables:
        #     out_data[var] =  getattr(self, var)

        out_data["time"] = self.t_vec
        out_data["mach"] = self.Flight.mach_sim_time
        out_data["altitude"] = self.Flight.alt_sim_time

        # For each element, append the time history of wall temperatures
        for i in range( self.wall_temps.shape[0] ):
            
            col_name = f"T_wall:node_{i}"
            out_data[col_name] =   self.wall_temps[i,:]
    
        #Export CSV 
        if os.path.exists(out_filename):
            print(f"WARNING: {out_filename} already exists. OVERWRITING...")
        
        out_data.to_csv(out_filename, index=False)





