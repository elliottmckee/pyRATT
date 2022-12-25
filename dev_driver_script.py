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

# # Standard Atmosphere Model/Package (CANT HANDLE HIGH-ALT)
# # https://ambiance.readthedocs.io/en/latest/index.html
# from ambiance import Atmosphere

from src.common.obj_simulation import Simulation
from src.common.obj_flight_rocket import Rocket, FlightData
from src.common.obj_wall_components import SolidWallComponent, AerosurfaceStack
from src.materials.air_model import AirModel



if __name__ == "__main__":

    # #Define a Wall Component of Aluminum 6061 with following properties
    # AluminumWall = WallComponent(material = "ALU6061", tot_thickness = 0.01, n_nodes = 11, emis_override = None)
    # NotAluWall = WallComponent(material = "OTHER EXAMPLE MATERIAL", tot_thickness = 0.05, n_nodes = 11, emis_override = None)

    # #Define an Aerosurface of just the above wall section, since only doing one material (still taking in list format tho for future improvements)
    # MyAerosurf = AerosurfaceStack(wall_components = [AluminumWall], surface_type = "nosecone", interface_resistances = None)

    # #Define a Rocket geometry
    # MyRocket = Rocket(nosecone_half_angle_deg = 7.0)

    # # Define a Flight Profile
    # MyFlight = FlightData( os.path.join(os.getcwd(), "example_files", "Meat_Rocket_N5800_ASCENTONLY.CSV") )

    # #Define a Simulation Object
    # MySimulation = Simulation(MyAerosurf, MyRocket, MyFlight, AirModel(),
    #                             x_location = 0.02, 
    #                             t_step = 0.005)
    
    # # #Run Simulation
    # MySimulation.run()

    # #Export Simulation Data to CSV
    # MySimulation.export_data_to_csv(out_filename = 'export_data.csv')


    # #Plotting
    # plt.plot(MySimulation.t_vec, MySimulation.wall_temps[0,:])   
    # plt.show()



    ### Mini MeatRocket Section ###
    
    #convert_AVA_traj_to_RAS(os.path.join(os.getcwd(), "example_files", "mini_meat", "2022-12-17-serial-5939-flight-0003.csv"), os.path.join(os.getcwd(), "example_files", "mini_meat", "2022-12-17-serial-5939-flight-0003_RAS_FORMAT.CSV"))
    #flight_data = pd.read_csv(os.path.join(os.getcwd(), "example_files", "mini_meat", "2022-12-17-serial-5939-flight-0003_RAS_FORMAT.CSV"), usecols=['Time (sec)', 'Mach Number', 'Altitude (ft)'])

    AluminumWall = SolidWallComponent(material = "ALU6061", tot_thickness = 0.0025, n_nodes = 9, emis_override = None)
    MyAerosurf = AerosurfaceStack(wall_components = [AluminumWall], surface_type = "nosecone", interface_resistances = None)
    MyRocket = Rocket(nosecone_half_angle_deg = 12.0)

    # Define a Flight Profile
    MyFlight = FlightData( os.path.join(os.getcwd(), "example_files", "mini_meat", "2022-12-17-serial-5939-flight-0003_RAS_FORMAT.CSV") )

    #Define a Simulation Object
    MySimulation = Simulation(MyAerosurf, MyRocket, MyFlight, AirModel(),
                                x_location = 0.0508, 
                                t_step = 0.0004,
                                t_end = 20.0,
                                initial_temp = 281.15,
                                boundary_layer_model = 'transition')
    
    # #Run Simulation
    MySimulation.run()


    print("Add Emissivity Override as a Sim Variable")
    print("Deleting the SolidMaterial object")
    print("Nodes or elements? Resolve confusion in var names, etc.")
    print("Plot Cp table points and interpolation to see if linear interpolation is enough")
    print("Find better way to index from Atmos?")



    #Plotting
    
    # # Flight Data Conversion
    # plt.figure
    # plt.plot(flight_data['Time (sec)'], flight_data['Altitude (ft)'])
    # #plt.plot(flight_data['Time (sec)'], flight_data['Mach Number'])
    # plt.show()


    TC_data = pd.read_csv( os.path.join(os.getcwd(), "example_files", "mini_meat", "FL79.csv"), 
                                header=0, skiprows=range(1, 269), usecols=['Flight Time(s)', ' TC Tip (C)', ' TC Wall Flush (C)', ' TC Wall Inside (C)'])


    #Temperature Plot
    plt.figure()

    plt.plot(MySimulation.t_vec, MySimulation.wall_temps[0,:] - 273.15,     label = "Simulated - Surface", linestyle="-", color='firebrick')
    plt.plot(TC_data['Flight Time(s)'], TC_data[' TC Wall Flush (C)'],      label = "Flight TC - Wall Flush", linestyle=":", color='red') 

    plt.plot(MySimulation.t_vec, MySimulation.wall_temps[-1,:] - 273.15,     label = "Simulated - Inside", linestyle="-", color='darkblue')
    plt.plot(TC_data['Flight Time(s)'], TC_data[' TC Wall Inside (C)'],      label = "Flight TC - Wall Inside", linestyle=":", color='blue')

    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("Temperature, C")
    plt.title("Mini Meat - Wall Temps")
    plt.axis([0, 30, 5, 40])



    plt.figure()
    plt.plot(MySimulation.t_vec, MySimulation.T_recovery[:] - 273.15,       label = "Simulated - Recovery Temp", linestyle="-", color='mediumorchid')
    plt.plot(TC_data['Flight Time(s)'], TC_data[' TC Tip (C)'],             label = "Flight TC - Tip", linestyle=":", color='fuchsia')

    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("Temperature, C")
    plt.title("Mini Meat - Tip Temps")
    plt.axis([-5, 30, 5, 100])

    plt.show()

