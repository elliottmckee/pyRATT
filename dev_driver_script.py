'''

I will be coming back to this later to expand this header a good bit


Description:
This will be the main script that the User interacts with. 
They will select which modules to run, point to the desired
rocket/trajectory files, maybe point to a config file 
containing extra information, and this will hand things off to simulate.py


'''

#from materials_standard import SolidMaterial


import os
import numpy as np

# Standard Atmosphere Model/Package (CANT HANDLE HIGH-ALT)
# https://ambiance.readthedocs.io/en/latest/index.html
from ambiance import Atmosphere


from src.materials.materials_standard import SolidMaterial
#from src.common.structure_definitions import NoseconeSingleMaterialWall
#from src.tools.RAS_file_parsing_tools import RAS_traj_CSV_Parse


from src.common.simulation_objects import FlightSim



if __name__ == "__main__":


    # Wall_Material = SolidMaterial("ALU6061")
    # print(Wall_Material.rho)

    # Test_Wall = NoseconeSingleMaterialWall("ALU6061", 0.1, 20)
    # print(Test_Wall.thickness)


    ##### Testing Flight Sim Object 
    # flight_trajectory_file = os.path.join(os.getcwd(), "example_files", "Meat_Rocket_N5800.CSV")
    # Flight = FlightData(flight_trajectory_file)
 
    # curr_Mach, curr_Time = Flight.get_current_state(0.025)

    # print(Flight.time[0:5])
    # print(Flight.mach[0:5])
    # print(Flight.alt[0:5])

    # print(curr_Mach)
    # print(curr_Time)



    #atmosphere = Atmosphere([0, 1000, 80000])

    #print(atmosphere.speed_of_sound)


    # #Get Current Working Directory
    # cwd = os.getcwd()


    # #Input Files
    # rocket_file_path        = os.path.join(cwd, 'example_files', 'Meat_Rocket.CDX1')
    # trajectory_file_path    = os.path.join(cwd, 'example_files', 'Meat_Rocket_N5800.CSV')





















