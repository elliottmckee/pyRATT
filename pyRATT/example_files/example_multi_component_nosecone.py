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
This is an example script showing how to run simulations with
walls that are made out of multiple materials. 

In the below script, two nosecone simulations are run:

    1) 0.01m Thick Aluminum Wall

    2) 0.01m thick wall made up of :
            0.05m Aluminum 6061 on the Outside/exposed Surface, 
            0.05m Carbon Fiber

And the through-wall temperature distributions of each of the simulations, 
sampled at a point during ascent are plotted to show how the material change 
affects the temperature distribution. I also vary the element counts for each of 
the sections, just for funsies. 

In the plots that are generated by this script, you can see how bad of a 
conductor Carbon Fiber composite is in this through-wall direction (note
the discontinuity in the result plot)

*This is a pretty whacky example, since I haven't put any material properties for
any non-metals in yet. But this functionality becomes useful if you are
trying to simulate something like a TPS layer on top of an aluminum structural wall,
or maybe you have some sort of thin coating, idk, they'res a lot you can do here...*

This also scales to as many materials as you want. You'd just need the thermal 
properties of all the materials 

"""

if __name__ == "__main__":


    # (!!! REMOVE IF RUNNING SCRIPT FROM MAIN DIRECTORY!!!) #
    # Move up one level into main directory 
    os.chdir("..")
    # (!!! REMOVE IF RUNNING SCRIPT FROM MAIN DIRECTORY!!!) #

    
    # Define Wall Stack
    AeroSurf = WallStack(   materials = ["CARBONFIBER", "ALU6061"], 
                            thicknesses = [0.0066, 0.0033], 
                            element_counts = [15, 10])

    # Point to Trajectory Data CSV
    Flight    = FlightProfile( "example_ascent_traj_M2245_to_M1378.csv" )

    # Define Simulation Object
    MySimulation = Thermal_Sim_1D(AeroSurf, Flight, AirModel(),
                                x_location = 0.1, 
                                deflection_angle_deg = 7.0, 
                                t_step = 0.002,
                                t_end = 25.1,
                                initial_temp = 281.25,
                                shock_type = "oblique",
                                aerothermal_model = "flat_plate"
                                boundary_layer_model = 'transition')

    # Run Simulation
    MySimulation.run()


    # Plot Results (can also use GUI)
    # --------------
    Post.plot_results(MySimulation)


    # Export Data back into Examples folder
    # --------------
    
    # .csv Data
    MySimulation.export_data_to_csv("example_files/multi_material_example_out.csv")
    
    # Pickled Simulation Object
    with open ("example_files/multi_material_example_out.sim", "wb") as f: 
        pickle.dump(MySimulation, f)

