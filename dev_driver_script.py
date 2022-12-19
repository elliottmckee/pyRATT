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
import pandas as pd
import matplotlib.pyplot as plt

# Standard Atmosphere Model/Package (CANT HANDLE HIGH-ALT)
# https://ambiance.readthedocs.io/en/latest/index.html
from ambiance import Atmosphere

from src.materials.air_model import AirModel
#from src.common.structure_definitions import NoseconeSingleMaterialWall
#from src.tools.RAS_file_parsing_tools import RAS_traj_CSV_Parse


from src.common.simulation_objects import SolidMaterial, WallComponent, AerosurfaceStack, FlightData, Rocket, Simulation



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



    # HiFire 5 Verification Case

    AluWall = WallComponent(material = "ALU6061", tot_thickness = 0.02, n_nodes = 26, emis_override = None)
    AeroSurf = AerosurfaceStack(wall_components = [AluWall], surface_type = "nosecone", interface_resistances = None)
    MyRocket = Rocket(nosecone_half_angle_deg = 7.0)
    MyFlight = FlightData( os.path.join(os.getcwd(), "example_files", "hifire_5", "hifire5_traj_interp.csv") )

    MySimulation = Simulation(AeroSurf, MyRocket, MyFlight, AirModel(),
                                x_location = 0.2, 
                                t_step = 0.004,
                                t_end = 215.0,
                                initial_temp = 281.25)

    MySimulation.run()

    MySimulation.export_data_to_csv(out_filename = 'hifire_out_data.csv')




    #Verification Plotting

    #Matlab Simulation Data
    matlab_data = pd.read_csv( os.path.join(os.getcwd(), "example_files", "hifire_5", "hifire_5_matlab_data.csv"),
                                usecols=['time','q_hw(W?)','heat_trans_coeff','T_recover(K)', 'T_wall:x=0.0000', 'T_wall:x=0.0200'])

    #Ulsu Simsek Digitized Data
    simsek_data = pd.read_csv( os.path.join(os.getcwd(), "example_files", "hifire_5", "raw_digitized", "HiFire_Temps.csv"),
                                header = 1,
                                names=['t_cw','T_cw','t_hw','T_hw'])


    #Temperature Plot
    plt.plot(matlab_data["time"], matlab_data["T_wall:x=0.0000"],   label = "Matlab - Hot Wall", linestyle="-", color='maroon')
    plt.plot(matlab_data["time"], matlab_data["T_wall:x=0.0200"],   label = "Matlab - Cold Wall", linestyle="-", color='darkviolet')

    plt.plot(simsek_data["t_hw"], simsek_data["T_hw"],              label = "Simsek - Hot Wall", linestyle="--", color='orchid')
    plt.plot(simsek_data["t_cw"], simsek_data["T_cw"],              label = "Simsek - Cold Wall", linestyle="--", color='blue')

    plt.plot(MySimulation.t_vec, MySimulation.wall_temps[0,:],      label = "Python - Hot Wall", linestyle=":", color='fuchsia') 
    plt.plot(MySimulation.t_vec, MySimulation.wall_temps[-1,:],      label = "Python - Cold Wall", linestyle=":", color='deepskyblue')  

    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("Temeperature, K")
    plt.title("HiFire 5 Verification Case - Simsek v. Matlab v. Python")

    plt.show()





























