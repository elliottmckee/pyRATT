'''
---------------------------------------------------------------------------
pyRATT - Python Rocket AeroThermal Toolbox 
---------------------------------------------------------------------------
'''

#Standard Libraries
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import filecmp
import time
import pickle

# For cases not run in main directory, need to add main folder to path 
# so Python can find modules
sys.path.append(os.path.dirname(os.getcwd()))

#Internal Modules
from src.obj_simulation import Thermal_Sim_1D
from src.obj_flightprofile import FlightProfile
from src.obj_wallcomponents import WallStack
from src.materials_gas import AirModel
import src.tools_postproc as Post


"""
This is an example script showing how to run the follwing simulation:
    - Nosecone Thermal Simulation with Single-Material (aluminum) Wall

with relatively standard settings otherwise.
"""

if __name__ == "__main__":


    # Move up one level into main directory (not needed if running script from main folder)
    os.chdir("..")

    
    # Define Wall
    AeroSurf = WallStack(materials="ALU6061", 
                        thicknesses=0.01, 
                        node_counts = 15)

    # Point to Trajectory Data CSV
    Flight    = FlightProfile( "example_files/example_trajectory_N5800_to_M1378.csv" )
    
    # Define Simulation Object
    MySimulation= Thermal_Sim_1D(AeroSurf, Flight, AirModel(),
                                x_location = 0.1, 
                                deflection_angle_deg = 7.0, 
                                t_step = 0.0030,
                                t_end = 80.0,
                                initial_temp = 281.25,
                                boundary_layer_model = 'transition')


    # Run Simulation
    # --------------
    MySimulation.run()


    # Export Data back into Examples folder
    # --------------
    
    # .csv Data
    MySimulation.export_data_to_csv("example_files/nosecone_example_out.csv")
    
    # Pickled Simulation Object
    with open ("example_files/nosecone_example_out.sim", "wb") as f: 
        pickle.dump(MySimulation, f)



    # Plot Results (can also use GUI)
    # --------------
    Post.plot_results(MySimulation)
