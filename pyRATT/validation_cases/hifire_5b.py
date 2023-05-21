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
    from pyRATT.src.simulate_network import TransientThermalSim
    from pyRATT.src.thermal_network import  ThermalNetwork
    from pyRATT.src.tools_aero import ShockList
    from pyRATT.src.loadings_aerothermal import AerothermalLoading
    from pyRATT.src.loadings_radiation import ExternalRadiationLoading
    from pyRATT.src.obj_flight import FlightProfile
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


    ################################# CONFIGURATION INFO ########################################
    Shocks                  = ShockList(["oblique"], [7.0])
    Flight                    = FlightProfile( os.path.join(os.getcwd(), "validation_cases", "resources", "hifire_5b", "hifire_5b_flight_profile.csv") )

    RadiationLoading = ExternalRadiationLoading(Flight=Flight)


    ############################# THERMAL NETWORK DEF'N ########################################
   
    # 400mm Downstream of Nosecone
    Net_400 = ThermalNetwork()
    Net_400.addComponent_1D("ALU6061", total_thickness=0.02, n_nodes=26)
    
    AeroThermLoading_400    = AerothermalLoading( 0.400, Flight, Shocks, AirModel(), aerothermal_model="flat-plate", boundary_layer_model="transition") 
    Net_400.add_thermal_loading(nodeID = 0, ThermLoading = RadiationLoading)
    Net_400.add_thermal_loading(nodeID = 0, ThermLoading = AeroThermLoading_400)
    
    Sim_400 = TransientThermalSim( Net_400,  T_initial=368.15,  t_step=0.001, t_start = 510.0, t_end = 520.0)

    # 650mm Downstream of Nosecone
    Net_650 = ThermalNetwork()   
    Net_650.addComponent_1D("ALU6061", total_thickness=0.02, n_nodes=26)
    
    AeroThermLoading_650    = AerothermalLoading( 0.650, Flight, Shocks, AirModel(), aerothermal_model="flat-plate", boundary_layer_model="transition") 
    Net_650.add_thermal_loading(nodeID = 0, ThermLoading = RadiationLoading)
    Net_650.add_thermal_loading(nodeID = 0, ThermLoading = AeroThermLoading_650)

    Sim_650 = TransientThermalSim( Net_650,  T_initial=361.36,  t_step=0.001, t_start = 510.0, t_end = 520.0)
    
    # 650mm Downstream of Nosecone
    Net_800 = ThermalNetwork()   
    Net_800.addComponent_1D("ALU6061", total_thickness=0.02, n_nodes=26)
    
    AeroThermLoading_800    = AerothermalLoading( 0.800, Flight, Shocks, AirModel(), aerothermal_model="flat-plate", boundary_layer_model="transition") 
    Net_800.add_thermal_loading(nodeID = 0, ThermLoading = RadiationLoading)
    Net_800.add_thermal_loading(nodeID = 0, ThermLoading = AeroThermLoading_800)

    Sim_800 = TransientThermalSim( Net_800,  T_initial=360.86,  t_step=0.001, t_start = 510.0, t_end = 520.0)




    ############################# RUN SIMULATIONS ########################################

    start = time.time()
    Sim_400.run()
    Sim_650.run()
    Sim_800.run()
    end = time.time()
    print("Elapsed Time for all sims: ", end - start)




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

    plt.show()

    # # Heat Flux Plot
    # plt.figure()

    # # plt.plot(matlab_data["time"], matlab_data["q_hw(W?)"],      label = "Matlab q_net", linestyle="-", color='hotpink')
    
    # plt.plot(Sim_400.t_vec, Sim_400.q_conv[:],      label = "Python q_conv", linestyle="--", color='red') 
    # plt.plot(Sim_400.t_vec, Sim_400.q_rad[:],       label = "Python q_rad", linestyle="--", color='blue') 
    # plt.plot(Sim_400.t_vec, Sim_400.q_net[:],       label = "Python q_net", linestyle="-", color='purple') 

    # plt.legend()
    # plt.xlabel("Time (s)")
    # plt.ylabel("q_, W")
    # plt.title("HiFire 5 Verification - Heat Flux")
    

    #Heat Transfer Coefficient Plot
    # plt.figure()

    # #plt.plot(matlab_data["time"], matlab_data["heat_trans_coeff"],  label = "Matlab h", linestyle="-", color='hotpink')
    # #plt.plot(simsek_h_tRec_data["t_h"], simsek_h_tRec_data["h"],    label = "Simsek h", linestyle="--", color='orchid')
    # plt.plot(Sim_400.t_vec, Sim_400.h_coeff[:],           label = "Python h", linestyle="-", color='purple') 

    # plt.legend()
    # plt.xlabel("Time (s)")
    # plt.ylabel("Heat Transfer Coeff, h")
    # plt.title("HiFire 5 Verification - Heat Transfer Coeff")
    

    # #Recovery Temperature Plot
    # plt.figure()

    # #plt.plot(matlab_data["time"], matlab_data["T_recover(K)"],      label = "Matlab_Tr", linestyle="-", color='hotpink')
    # #plt.plot(simsek_h_tRec_data["t_Tr"], simsek_h_tRec_data["Tr"],  label = "Simsek_Tr", linestyle="--", color='orchid')
    # plt.plot(Sim_400.t_vec, Sim_400.T_recovery[:],           label = "Python Tr", linestyle="-", color='purple')

    # plt.legend()
    # plt.xlabel("Time (s)")
    # plt.ylabel("Recovery Temp, K")
    # plt.title("HiFire 5 Verification - T_recovery")

    # plt.show()






























