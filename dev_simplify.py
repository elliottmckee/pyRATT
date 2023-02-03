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



if __name__ == "__main__":




    
    AluminumWall = WallStack(materials=["ALU6061"], thicknesses=[0.0025], node_counts = [9])
    

    quit()









    MyAerosurf = AerosurfaceStack(wall_components = [AluminumWall], surface_type = "nosecone", interface_resistances = None)
    MyRocket = Rocket(nosecone_half_angle_deg = 12.0)

    # Define a Flight Profile
    MyFlight = FlightData( os.path.join(os.getcwd(), "example_files", "mini_meat", "2022-12-17-serial-5939-flight-0003_RAS_FORMAT.CSV") )

    #Define a Flight Simulation Object
    MySimulation = FlightSimulation(MyAerosurf, MyRocket, MyFlight, AirModel(),
                                x_location = 0.0508, 
                                t_step = 0.0004,
                                t_end = 20.0,
                                initial_temp = 281.15,
                                boundary_layer_model = 'transition')
    
    # #Run Simulation
    MySimulation.run()
    # end = time.time()
    # print("Elapsed Time: ", end - start)
