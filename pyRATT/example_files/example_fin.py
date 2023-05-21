'''
---------------------------------------------------------------------------
pyRATT - Python Rocket AeroThermal Toolbox 
---------------------------------------------------------------------------
'''

#Standard Libraries
import os
import numpy as np
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
    - Fin Thermal simulation with single-material (Stainless Steel) Fin 


Note that the only line that changes is the last argument of Thermal_Sim_1D, 
where we we assign thermal boundary conditions. 

The Simulation defaults to nosecones, which are modelled as having one exposed 
external surface, and one internal wall that we model as adiabatic. 

For Fins, we have heating on both sides, and so we have to tell the solver that. 
The wall_thermal_bcs argument is how you specify these different boundary conditions. 

For example, this is how this argument should look for the 2 standard cases:
    Nosecones:
        wall_thermal_bcs = ["q_in_aerothermal","adiabatic"] (default argument)
    Fins:
        wall_thermal_bcs = ["q_in_aerothermal","q_in_aerothermal"]


For list of currently available materials, or to add own, see materials_solid.py

with relatively standard settings otherwise.
"""

if __name__ == "__main__":


    # (!!! REMOVE IF RUNNING SCRIPT FROM MAIN DIRECTORY!!!) #
    # Move up one level into main directory 
    os.chdir("..")
    # (!!! REMOVE IF RUNNING SCRIPT FROM MAIN DIRECTORY!!!) #

    
    # Define Wall
    AeroSurf = WallStack(materials="SS316", 
                        thicknesses=0.0127, 
                        element_counts = 11)

    # Point to Trajectory Data CSV
    Flight    = FlightProfile( "example_files/example_ascent_traj_M2245_to_M1378.csv" )
    
    # Define Simulation Object
    MySimulation= Thermal_Sim_1D(AeroSurf, Flight, AirModel(),
                                x_location = 0.1, 
                                deflection_angle_deg = 10.0, 
                                t_step = 0.005,
                                t_end = 25.1,
                                initial_temp = 281.25,
                                boundary_layer_model = 'transition',
                                wall_thermal_bcs = ["q_conv","q_conv"]
                                )


    # Run Simulation
    # --------------
    MySimulation.run()


    # Export Data back into Examples folder
    # --------------
    
    # .csv Data
    MySimulation.export_data_to_csv("example_files/fin_example_out.csv")
    
    # Pickled Simulation Object
    with open ("example_files/fin_example_out.sim", "wb") as f: 
        pickle.dump(MySimulation, f)



    # Plot Results (can also use GUI)
    # --------------
    Post.plot_results(MySimulation)
