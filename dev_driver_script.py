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
from src.materials.air_model import AirModel
#from src.common.structure_definitions import NoseconeSingleMaterialWall
#from src.tools.RAS_file_parsing_tools import RAS_traj_CSV_Parse


from src.common.simulation_objects import WallComponent, AerosurfaceStack, FlightData, Rocket, Simulation



if __name__ == "__main__":


    #Define a Wall Component of Aluminum 6061 with following properties
    AluminumWall = WallComponent(material = "ALU6061", thickness = 0.02, n_div = 20, emis_override = None)

    #Define an Aerosurface of just the above wall section, since only doing one material (still taking in list format tho for future improvements)
    MyAerosurf = AerosurfaceStack(wall_components = [AluminumWall], surface_type = "nosecone", interface_resistances = None)

    #Define a Rocket geometry
    MyRocket = Rocket(nosecone_half_angle_deg = 7.0)

    # Define a Flight Profile
    MyFlight = FlightData( os.path.join(os.getcwd(), "example_files", "Meat_Rocket_N5800.CSV") )
    #curr_Mach, curr_Time = MyFlight.get_current_state(0.025)

    #Define a Simulation Object
    MySimulation = Simulation(MyAerosurf, MyRocket, MyFlight, AirModel(),
                                x_location = 0.02, 
                                t_step = 0.01,)


    # #Run Simulation
    MySimulation.run()









    #OLD TESTING SECTION

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



















