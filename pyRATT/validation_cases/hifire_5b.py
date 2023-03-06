import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import time
import pickle

#todo: this is super goofy- find better way to do this
sys.path.append(os.path.dirname(os.getcwd()))


try:
    from pyRATT.src.obj_simulation import Thermal_Sim_1D
    from pyRATT.src.obj_flightprofile import FlightProfile
    from pyRATT.src.obj_wallcomponents import WallStack
    from pyRATT.src.materials_gas import AirModel
except:
    print("\n Run this script from the main pyRATT directory using 'python3 validation_cases/hifire_5b.py")
    quit()


'''

USAGE:  From the main pyRATT directory run: "python3 validation_cases/hifire_5b.py"


ABOUT:
    This script is a validation case studying the HiFIRE-5B flight data from the below reference.

    The HiFire payload was basically an aluminum nosecone instrumented with a TON of thermocouples,
    heat-flux sensors, etc. with the aim of investigating transition to turbulence for hypersonic flows.

    On this flight the 2nd stage did light, which resulted in a quite speedy boy, being just barely 
    shy of Mach 8 on re-entry. 

    However, there is much less raw-temperature data given in this report. There was a good few article on
    this mission, so I might just need to look harder...

    Nevertheless, we get a short window of data on descent at Mach 7+, where transition occurs, and can 
    be seen in both the flight data, as well as the simulation results below.



REFERENCES:

    [1] Hypersonic International Flight Research Experimentation-5b Flight Overview 
        Roger L. Kimmel, David W. Adamczak, David Hartley, Hans Alesi, Myles A. Frost, Robert Pietsch, Jeremy Shannon, and Todd Silvester
        Journal of Spacecraft and Rockets 2018 55:6, 1303-1314

'''



if __name__ == "__main__":


   
    # Define Wall
    AeroSurf = WallStack(materials="ALU6061", thicknesses=0.02, node_counts = 26)

    # Point to Flight Trajectory
    MyFlight    = FlightProfile( os.path.join(os.getcwd(), "validation_cases", "resources", "hifire_5b", "hifire_5b_flight_profile.csv") )

    # Setup 400mm downstream sim
    Sim_400 = Thermal_Sim_1D(AeroSurf, MyFlight, AirModel(),
                                x_location = 0.40,
                                deflection_angle_deg = 7.0, 
                                t_step = 0.001,
                                t_start = 510.0,
                                t_end = 520.0,
                                initial_temp = 368.15,
                                boundary_layer_model = 'transition')

    # Setup 650mm downstream sim
    Sim_650 = Thermal_Sim_1D(AeroSurf, MyFlight, AirModel(),
                                x_location = 0.65,
                                deflection_angle_deg = 7.0, 
                                t_step = 0.001,
                                t_start = 510.0,
                                t_end = 520.0,
                                initial_temp = 361.36,
                                boundary_layer_model = 'transition')
                                
    # Setup 800mm downstream sim
    Sim_800 = Thermal_Sim_1D(AeroSurf, MyFlight, AirModel(),
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
    Sim_400.export_data_to_csv(out_filename = 'hifire_5b_400mm_validation.csv')
    Sim_650.export_data_to_csv(out_filename = 'hifire_5b_650mm_validation.csv')
    Sim_800.export_data_to_csv(out_filename = 'hifire_5b_800mm_validation.csv')

    # Pickles
    with open("hifire_5b_400mm_validation.sim", "wb") as f: pickle.dump(Sim_400, f)
    with open("hifire_5b_650mm_validation.sim", "wb") as f: pickle.dump(Sim_650, f)
    with open("hifire_5b_800mm_validation.sim", "wb") as f: pickle.dump(Sim_800, f)  
    





    ###########################  PLOTTING #########################

    #Load Matlab Simulation Data
    print("Try and extract Matlab 5B Simulation data at some point for these")
    # matlab_data = pd.read_csv( os.path.join(os.getcwd(), "example_files", "hifire_5", "hifire_5_matlab_data.csv"),
    #                             usecols=['time','q_hw(W?)','heat_trans_coeff','T_recover(K)', 'T_wall:x=0.0000', 'T_wall:x=0.0200'])

    #Load Juliano Digitized Flight Data
    flightData_400 = pd.read_csv( os.path.join(os.getcwd(), "validation_cases", "resources", "hifire_5b", "hifire_5b_temp_time_400.csv"), header = 1, names=['time','temp'])
    flightData_650 = pd.read_csv( os.path.join(os.getcwd(), "validation_cases", "resources", "hifire_5b", "hifire_5b_temp_time_650.csv"), header = 1, names=['time','temp'])
    flightData_800 = pd.read_csv( os.path.join(os.getcwd(), "validation_cases", "resources", "hifire_5b", "hifire_5b_temp_time_800.csv"), header = 1, names=['time','temp'])

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






























