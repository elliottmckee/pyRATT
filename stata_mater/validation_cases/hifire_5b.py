import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import time
import pickle

#I have to do stupid ass directory bullshit because Python is shit with imports
# Make it so it can find the 
sys.path.append(os.path.dirname(os.getcwd()))
#sys.path.append(os.path.dirname(os.path.dirname(os.getcwd())))

# # Standard Atmosphere Model/Package (CANT HANDLE HIGH-ALT)
# # https://ambiance.readthedocs.io/en/latest/index.html
# from ambiance import Atmosphere

from stata_mater.src.obj_simulation import FlightSimulation
from stata_mater.src.obj_flightdata import Rocket, FlightData
from stata_mater.src.obj_wall_components import WallStack
from stata_mater.src.airmodel import AirModel


'''

I will be coming back to this later to expand this header a good bit


##### USAGE #####
I KNOW THIS IMPLEMENTATION IS DOGSHIT, BUT HERE'S HOW TO RUN THESE

From the stata_mater folder, run the following command:
python3 tests/hifire_5b.py


I'm sorry 
'''



if __name__ == "__main__":


    # HiFire 5B Verification Case Setup

    AeroSurf = WallStack(materials="ALU6061", thicknesses=0.02, node_counts = 26)

    MyFlight    = FlightData( os.path.join(os.getcwd(), "example_files", "hifire_5b", "Hifire5BData.csv") )

    
    Sim_400 = FlightSimulation(AeroSurf, MyFlight, AirModel(),
                                x_location = 0.40,
                                deflection_angle_deg = 7.0, 
                                t_step = 0.001,
                                t_start = 510.0,
                                t_end = 520.0,
                                initial_temp = 368.15,
                                boundary_layer_model = 'transition')


    Sim_650 = FlightSimulation(AeroSurf, MyFlight, AirModel(),
                                x_location = 0.65,
                                deflection_angle_deg = 7.0, 
                                t_step = 0.001,
                                t_start = 510.0,
                                t_end = 520.0,
                                initial_temp = 361.36,
                                boundary_layer_model = 'transition')
                                

    Sim_800 = FlightSimulation(AeroSurf, MyFlight, AirModel(),
                                x_location = 0.80, 
                                deflection_angle_deg = 7.0,
                                t_step = 0.001,
                                t_start = 510.0,
                                t_end = 520.0,
                                initial_temp = 360.86,
                                boundary_layer_model = 'transition')


    #Run Simulations
    start = time.time()

    Sim_400.run()
    Sim_650.run()
    Sim_800.run()

    end = time.time()
    print("Elapsed Time for all 3 Sims: ", end - start)

    ### Export

    # CSV's
    #Sim_400.export_data_to_csv(out_filename = 'hifire_5b_400mm_out_data_new.csv')
    #Sim_650.export_data_to_csv(out_filename = 'hifire_5b_650mm_out_data_new.csv')
    #Sim_800.export_data_to_csv(out_filename = 'hifire_5b_800mm_out_data_new.csv')

    # Pickles
    # with open("tests/hifire_5b_400mm.pkl", "wb") as f: pickle.dump(Sim_400, f)
    # with open("tests/hifire_5b_650mm.pkl", "wb") as f: pickle.dump(Sim_650, f)
    # with open("tests/hifire_5b_800mm.pkl", "wb") as f: pickle.dump(Sim_800, f)  
    



    # Verification Plotting

    #Load Matlab Simulation Data
    print("Try and extract Matlab 5B Simulation data at some point for these")
    # matlab_data = pd.read_csv( os.path.join(os.getcwd(), "example_files", "hifire_5", "hifire_5_matlab_data.csv"),
    #                             usecols=['time','q_hw(W?)','heat_trans_coeff','T_recover(K)', 'T_wall:x=0.0000', 'T_wall:x=0.0200'])

    #Load Juliano Digitized Flight Data
    flightData_400 = pd.read_csv( os.path.join(os.getcwd(), "example_files", "hifire_5b", "5B_TempTime400.csv"), header = 1, names=['time','temp'])
    flightData_650 = pd.read_csv( os.path.join(os.getcwd(), "example_files", "hifire_5b", "5B_TempTime650.csv"), header = 1, names=['time','temp'])
    flightData_800 = pd.read_csv( os.path.join(os.getcwd(), "example_files", "hifire_5b", "5B_TempTime800.csv"), header = 1, names=['time','temp'])

    # simsek_h_tRec_data = pd.read_csv( os.path.join(os.getcwd(), "example_files", "hifire_5", "raw_digitized", "HiFire_h_Treco.csv"),
    #                             header = 1,
    #                             names=['t_h','h','t_Tr','Tr'])


    #Temperature Plot
    plt.figure()

    # plt.plot(matlab_data["time"], matlab_data["T_wall:x=0.0000"],   label = "Matlab - Hot Wall", linestyle="-", color='maroon')
    # plt.plot(matlab_data["time"], matlab_data["T_wall:x=0.0200"],   label = "Matlab - Cold Wall", linestyle="-", color='darkviolet')

    plt.plot(flightData_400["time"], flightData_400["temp"] + 273.15,    label = "Juliano Hot Wall 400", linestyle="--", color='blue')
    plt.plot(flightData_650["time"], flightData_650["temp"] + 273.15,    label = "Juliano Hot Wall 650", linestyle="--", color='orchid')
    plt.plot(flightData_800["time"], flightData_800["temp"] + 273.15,    label = "Juliano Hot Wall 800", linestyle="--", color='maroon')
    #plt.plot(simsek_temp_data["t_cw"], simsek_temp_data["T_cw"],    label = "Simsek - Cold Wall", linestyle="--", color='blue')

    plt.plot(Sim_400.t_vec, Sim_400.wall_temps[0,:],      label = "Python Hot Wall 400", linestyle="-", color='deepskyblue') 
    plt.plot(Sim_650.t_vec, Sim_650.wall_temps[0,:],      label = "Python Hot Wall 650", linestyle="-", color='fuchsia') 
    plt.plot(Sim_800.t_vec, Sim_800.wall_temps[0,:],      label = "Python Hot Wall 800", linestyle="-", color='red') 
    #plt.plot(Sim_400.t_vec, Sim_400.wall_temps[-1,:],     label = "Python - Cold Wall", linestyle=":", color='deepskyblue')  

    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("Temeperature, K")
    plt.title("HiFire 5B Verification - Temps")


    # Heat Flux Plot
    plt.figure()

    # plt.plot(matlab_data["time"], matlab_data["q_hw(W?)"],      label = "Matlab q_net", linestyle="-", color='hotpink')
    
    plt.plot(Sim_400.t_vec, Sim_400.q_conv[:],      label = "Python q_conv", linestyle="--", color='red') 
    plt.plot(Sim_400.t_vec, Sim_400.q_rad[:],       label = "Python q_rad", linestyle="--", color='blue') 
    plt.plot(Sim_400.t_vec, Sim_400.q_net[:],       label = "Python q_net", linestyle="-", color='purple') 

    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("q_, W")
    plt.title("HiFire 5 Verification - Heat Flux")
    

    #Heat Transfer Coefficient Plot
    plt.figure()

    #plt.plot(matlab_data["time"], matlab_data["heat_trans_coeff"],  label = "Matlab h", linestyle="-", color='hotpink')
    #plt.plot(simsek_h_tRec_data["t_h"], simsek_h_tRec_data["h"],    label = "Simsek h", linestyle="--", color='orchid')
    plt.plot(Sim_400.t_vec, Sim_400.h_coeff[:],           label = "Python h", linestyle="-", color='purple') 

    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("Heat Transfer Coeff, h")
    plt.title("HiFire 5 Verification - Heat Transfer Coeff")
    

    #Recovery Temperature Plot
    plt.figure()

    #plt.plot(matlab_data["time"], matlab_data["T_recover(K)"],      label = "Matlab_Tr", linestyle="-", color='hotpink')
    #plt.plot(simsek_h_tRec_data["t_Tr"], simsek_h_tRec_data["Tr"],  label = "Simsek_Tr", linestyle="--", color='orchid')
    plt.plot(Sim_400.t_vec, Sim_400.T_recovery[:],           label = "Python Tr", linestyle="-", color='purple')

    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("Recovery Temp, K")
    plt.title("HiFire 5 Verification - T_recovery")

    plt.show()






























