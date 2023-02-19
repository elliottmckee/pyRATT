import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import time
import pickle

# # Standard Atmosphere Model/Package (CANT HANDLE HIGH-ALT)
# # https://ambiance.readthedocs.io/en/latest/index.html
# from ambiance import Atmosphere

#I have to do stupid ass directory bullshit because Python is shit with imports
# Make it so it can find the 
sys.path.append(os.path.dirname(os.getcwd()))
#sys.path.append(os.path.dirname(os.path.dirname(os.getcwd())))

from stata_mater.src.obj_simulation import FlightSimulation
from stata_mater.src.obj_flight_rocket import Rocket, FlightData
from stata_mater.src.obj_wall_components import WallStack
from stata_mater.src.materials_fluid import AirModel


'''

I will be coming back to this later to expand this header a good bit


##### USAGE #####
I KNOW THIS IMPLEMENTATION IS DOGSHIT, BUT HERE'S HOW TO RUN THESE

From the stata_mater folder, run the following command:
python3 tests/hifire_5.py


I'm sorry 
'''



if __name__ == "__main__":


    start = time.time()

    # HiFire 5 Verification Case Setup
    AeroSurf = WallStack(materials="ALU6061", thicknesses=0.02, node_counts = 26)
    Flight    = FlightData( os.path.join(os.getcwd(), "example_files", "hifire_5", "hifire5_traj_interp.csv") )
    
    MySimulation= FlightSimulation(AeroSurf, Flight, AirModel(),
                                x_location = 0.2, 
                                deflection_angle_deg = 7.0, 
                                t_step = 0.0040,
                                t_end = 215.0,
                                initial_temp = 281.25,
                                boundary_layer_model = 'transition')


    #Run Simulation
    MySimulation.run()
    end = time.time()
    print("Elapsed Time: ", end - start)

    
    
    ### Export
    
    #CSV
    #MySimulation.export_data_to_csv(out_filename = 'hifire_5_out_data_new.csv')

    #Pickle
    # with open ("tests/hifire_5.pkl", "wb") as f: pickle.dump(MySimulation, f)




    # Verification Plotting

    #Load Matlab Simulation Data
    matlab_data = pd.read_csv( os.path.join(os.getcwd(), "example_files", "hifire_5", "hifire_5_matlab_data.csv"),
                                usecols=['time','q_hw(W?)','heat_trans_coeff','T_recover(K)', 'T_wall:x=0.0000', 'T_wall:x=0.0200'])

    #Load Ulsu Simsek Digitized Data
    simsek_temp_data = pd.read_csv( os.path.join(os.getcwd(), "example_files", "hifire_5", "raw_digitized", "HiFire_Temps.csv"),
                                header = 1,
                                names=['t_cw','T_cw','t_hw','T_hw'])

    simsek_h_tRec_data = pd.read_csv( os.path.join(os.getcwd(), "example_files", "hifire_5", "raw_digitized", "HiFire_h_Treco.csv"),
                                header = 1,
                                names=['t_h','h','t_Tr','Tr'])


    #Temperature Plot
    plt.figure()

    plt.plot(matlab_data["time"], matlab_data["T_wall:x=0.0000"],   label = "Matlab - Hot Wall", linestyle="-", color='maroon')
    plt.plot(matlab_data["time"], matlab_data["T_wall:x=0.0200"],   label = "Matlab - Cold Wall", linestyle="-", color='darkviolet')

    plt.plot(simsek_temp_data["t_hw"], simsek_temp_data["T_hw"],    label = "Simsek - Hot Wall", linestyle="--", color='orchid')
    plt.plot(simsek_temp_data["t_cw"], simsek_temp_data["T_cw"],    label = "Simsek - Cold Wall", linestyle="--", color='blue')

    plt.plot(MySimulation.t_vec, MySimulation.wall_temps[0,:],      label = "Python - Hot Wall", linestyle=":", color='fuchsia') 
    plt.plot(MySimulation.t_vec, MySimulation.wall_temps[-1,:],     label = "Python - Cold Wall", linestyle=":", color='deepskyblue')  

    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("Temeperature, K")
    plt.title("HiFire 5 Verification - Temps")


    # Heat Flux Plot
    plt.figure()

    plt.plot(matlab_data["time"], matlab_data["q_hw(W?)"],      label = "Matlab q_net", linestyle="-", color='hotpink')
    plt.plot(MySimulation.t_vec, MySimulation.q_conv[:],      label = "Python q_conv", linestyle="--", color='red') 
    plt.plot(MySimulation.t_vec, MySimulation.q_rad[:],       label = "Python q_rad", linestyle="--", color='blue') 
    plt.plot(MySimulation.t_vec, MySimulation.q_net[:],       label = "Python q_net", linestyle="-", color='purple') 

    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("q_, W")
    plt.title("HiFire 5 Verification - Heat Flux")
    

    #Heat Transfer Coefficient Plot
    plt.figure()

    plt.plot(matlab_data["time"], matlab_data["heat_trans_coeff"],  label = "Matlab h", linestyle="-", color='hotpink')
    plt.plot(simsek_h_tRec_data["t_h"], simsek_h_tRec_data["h"],    label = "Simsek h", linestyle="--", color='orchid')
    plt.plot(MySimulation.t_vec, MySimulation.h_coeff[:],           label = "Python h", linestyle="-", color='purple') 

    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("Heat Transfer Coeff, h")
    plt.title("HiFire 5 Verification - Heat Transfer Coeff")
    

    #Recovery Temperature Plot
    plt.figure()

    plt.plot(matlab_data["time"], matlab_data["T_recover(K)"],      label = "Matlab_Tr", linestyle="-", color='hotpink')
    plt.plot(simsek_h_tRec_data["t_Tr"], simsek_h_tRec_data["Tr"],  label = "Simsek_Tr", linestyle="--", color='orchid')
    plt.plot(MySimulation.t_vec, MySimulation.T_recovery[:],           label = "Python Tr", linestyle="-", color='purple')

    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("Recovery Temp, K")
    plt.title("HiFire 5 Verification - T_recovery")

    plt.show()






























