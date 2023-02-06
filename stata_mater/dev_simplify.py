'''

I will be coming back to this later to expand this header a good bit


Description:
This will be the main script that the User interacts with. 
They will select which modules to run, point to the desired
rocket/trajectory files, maybe point to a config file 
containing extra information, and this will hand things off to simulate.py


'''

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import filecmp
import time

# # Standard Atmosphere Model/Package (CANT HANDLE HIGH-ALT)
# # https://ambiance.readthedocs.io/en/latest/index.html
# from ambiance import Atmosphere

from src.obj_simulation import FlightSimulation
from src.obj_flight_rocket import Rocket, FlightData
from src.obj_wall_components import WallStack
from src.materials_fluid import AirModel
import src.tools_postproc as Post



if __name__ == "__main__":




    # Mini Meat
    # Wall = WallStack(materials="ALU6061", thicknesses=0.0025, node_counts = 9)
    
    # MyFlight = FlightData( os.path.join(os.getcwd(), "example_files", "mini_meat", "2022-12-17-serial-5939-flight-0003_RAS_FORMAT.CSV") )

    # MySimulation = FlightSimulation(Wall, MyFlight, AirModel(),
    #                             x_location = 0.0508,
    #                             deflection_angle_deg = 12.0, 
    #                             t_step = 0.0004,
    #                             t_end = 5.0,
    #                             initial_temp = 281.15,
    #                             boundary_layer_model = 'transition')

    
    # #Hifire 5

    # AeroSurf = WallStack(materials="ALU6061", thicknesses=0.02, node_counts = 26)
    # Flight    = FlightData( os.path.join(os.getcwd(), "example_files", "hifire_5", "hifire5_traj_interp.csv") )
    

    
    # MySimulation = FlightSimulation(AeroSurf, Flight, AirModel(),
    #                             x_location = 0.2, 
    #                             deflection_angle_deg = 7.0, 
    #                             t_step = 0.0040,
    #                             t_end = 40.0,
    #                             initial_temp = 281.25,
    #                             boundary_layer_model = 'transition')
    
    
    # HiFire 5B
    AeroSurf = WallStack(materials="ALU6061", thicknesses=0.02, node_counts = 26)
    MyFlight    = FlightData( os.path.join(os.getcwd(), "example_files", "hifire_5b", "Hifire5BData.csv") )
    MySimulation = FlightSimulation(AeroSurf, MyFlight, AirModel(),
                                x_location = 0.40,
                                deflection_angle_deg = 7.0, 
                                t_step = 0.001,
                                t_start = 510.0,
                                t_end = 520.0,
                                initial_temp = 360.7,
                                boundary_layer_model = 'transition')

    start=time.time()

    MySimulation.run()

    end = time.time()
    print("Elapsed Time for Sim Run: ", end - start)

    Post.plot_results(MySimulation)

    plt.show()