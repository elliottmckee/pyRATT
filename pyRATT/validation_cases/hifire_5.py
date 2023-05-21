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
    print("\n Error in imports. Run this script from the main pyRATT directory using 'python3 validation_cases/hifire_5.py")
    quit()


'''

USAGE:  From the main pyRATT directory run: "python3 validation_cases/hifire_5.py"


ABOUT:
    This script is a validation case studying the HiFIRE-5 flight data from the below reference.

    The HiFire payload was basically an aluminum nosecone instrumented with a TON of thermocouples,
    heat-flux sensors, etc. with the aim of investigating transition to turbulence for hypersonic flows.

    The 2nd stage on this flight didn't light, only resulting in a peak mach number of ~3. Regardless,
    it still measured data, and provides a GREAT validation case for this tool.

    The other validation case is the HiFIRE-5B data, where the 2nd stage did light...


REFERENCES:

    [1] HIFiRE-5 Flight Test Results, Thomas J. Juliano, David Adamczak, and Roger L. Kimmel, Journal of Spacecraft and Rockets 2015 52:3, 650-663

'''


if __name__ == "__main__":



    ################################# CONFIGURATION INFO ########################################
    Shocks                  = ShockList(["oblique"], [7.0])
    Flight                    = FlightProfile( os.path.join(os.getcwd(), "validation_cases", "resources", "hifire_5", "hifire_5_flight_profile.csv") )
    AeroThermLoading    = AerothermalLoading( 0.2,
                                                                    Flight, 
                                                                    Shocks, 
                                                                    AirModel(), 
                                                                    aerothermal_model="flat-plate",
                                                                    boundary_layer_model="transition") 
    RadiationLoading = ExternalRadiationLoading(Flight=Flight)

    ############################# THERMAL NETWORK DEF'N ########################################
    TNetwork = ThermalNetwork()
    TNetwork.addComponent_1D("ALU6061", total_thickness=0.02, n_nodes=26)

    TNetwork.add_thermal_loading(nodeID = 0, ThermLoading = AeroThermLoading)
    TNetwork.add_thermal_loading(nodeID = 0, ThermLoading = RadiationLoading)

    Sim = TransientThermalSim( TNetwork,  T_initial=281.25,  t_step=0.004, t_start = 0.0, t_end = 25.0)
    
    ############################# RUN SIMULATIONS ########################################
    start = time.time()
    Sim.run()
    end = time.time()
    print("Elapsed Time: ", end - start)


    

    ################################################# PLOTTING ##############################################

    # Load HiFire 5 Digitized data
    hifire_temp_data = pd.read_csv( os.path.join(os.getcwd(), "validation_cases", "resources", "hifire_5", "hifire_5_300mm_7degminoraxis_temps.csv"),
                                header = 1,
                                names=['t_hw','T_hw','t_cw','T_cw'])

    hifire_heatflux_data = pd.read_csv( os.path.join(os.getcwd(), "validation_cases", "resources", "hifire_5", "hifire_5_300mm_7degminoraxis_heatflux.csv"),
                                header = 1,
                                names=['t_hw','q_hw','t_cw','q_cw'])


    #Load Ulsu Simsek Digitized Data
    simsek_temp_data = pd.read_csv( os.path.join(os.getcwd(), "validation_cases", "resources", "hifire_5", "hifire_5_ulsu_temps.csv"),
                                header = 1,
                                names=['t_cw','T_cw','t_hw','T_hw'])

    simsek_h_tRec_data = pd.read_csv( os.path.join(os.getcwd(), "validation_cases", "resources", "hifire_5", "hiFire_5_h_Trecovery.csv"),
                                header = 1,
                                names=['t_h','h','t_Tr','Tr'])


    #Temperature Plot
    plt.figure()

    plt.plot(hifire_temp_data["t_hw"], hifire_temp_data["T_hw"],    label = "Flight - Hot Wall", linestyle="-", color='maroon')
    plt.plot(hifire_temp_data["t_cw"], hifire_temp_data["T_cw"],    label = "Flight - Cold Wall", linestyle="-", color='navy')

    plt.plot(Sim.t_vec, Sim.wall_temps[0,:],      label = "Python - Hot Wall", linestyle="--", color='red') 
    plt.plot(Sim.t_vec, Sim.wall_temps[-1,:],     label = "Python - Cold Wall", linestyle="--", color='royalblue')

    plt.plot(simsek_temp_data["t_hw"], simsek_temp_data["T_hw"],    label = "Simsek - Hot Wall", linestyle=":", color='darkorange')
    plt.plot(simsek_temp_data["t_cw"], simsek_temp_data["T_cw"],    label = "Simsek - Cold Wall", linestyle=":", color='deepskyblue')

    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("Temeperature, K")
    plt.title("HiFire 5 Verification - Temperature vs. Time")

    plt.show()

    # # Heat Flux Plot
    # plt.figure()

    # plt.plot(hifire_heatflux_data["t_hw"], hifire_heatflux_data["q_hw"]*1000,    label = "Flight - Hot Wall", linestyle="-", color='maroon')

    # plt.plot(MySimulation.t_vec, MySimulation.q_net[:],       label = "Python q_net", linestyle="--", color='red')
    # #plt.plot(MySimulation.t_vec, MySimulation.q_conv[:],      label = "Python q_conv", linestyle="--", color='purple') 
    # #plt.plot(MySimulation.t_vec, MySimulation.q_rad[:],       label = "Python q_rad", linestyle="--", color='blue') 
     

    # plt.legend()
    # plt.xlabel("Time (s)")
    # plt.ylabel("Heat Flux, q, W")
    # plt.title("HiFire 5 Verification - Heat Flux")
    


    # #Heat Transfer Coefficient Plot
    # plt.figure()

    # plt.plot(simsek_h_tRec_data["t_h"], simsek_h_tRec_data["h"],    label = "Simsek h", linestyle="--", color='orchid')
    # plt.plot(MySimulation.t_vec, MySimulation.h_coeff[:],           label = "Python h", linestyle="-", color='purple') 

    # plt.legend()
    # plt.xlabel("Time (s)")
    # plt.ylabel("Heat Transfer Coeff, h")
    # plt.title("HiFire 5 Verification - Heat Transfer Coeff")
    

    # #Recovery Temperature Plot
    # plt.figure()

    # plt.plot(simsek_h_tRec_data["t_Tr"], simsek_h_tRec_data["Tr"],  label = "Simsek_Tr", linestyle="--", color='orchid')
    # plt.plot(MySimulation.t_vec, MySimulation.T_recovery[:],           label = "Python Tr", linestyle="-", color='purple')

    # plt.legend()
    # plt.xlabel("Time (s)")
    # plt.ylabel("Recovery Temp, K")
    # plt.title("HiFire 5 Verification - T_recovery")

    # plt.show()






























