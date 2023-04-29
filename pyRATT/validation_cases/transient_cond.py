import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import time
import math
from scipy import special


#todo: this is super goofy- find better way to do this
sys.path.append(os.path.dirname(os.getcwd()))

try:
    from pyRATT.src.materials_solid import MATERIALS_DICT
    from pyRATT.src.simulate_network import TransientThermalSim
    from pyRATT.src.thermal_network import  ThermalNetwork
    from pyRATT.src.loadings_thermal import ConstantQdotLoading
except:
    print("\n Error occured in imports. Run this script from the main pyRATT directory using 'python3 validation_cases/transient_cond.py")
    quit()



'''
USAGE:  From the main pyRATT directory run: "python3 validation_cases/transient_cond.py"

ABOUT:
    This includes test cases for checking the Transient Thermal conduction implementation. It compares against
    two Analytical solutions for transient thermal conduction in a semi-infinite plate (infinite in all directions but one).

    The analytical solutions are pulled from Incropera [1] below.

    The two cases that are compared below are:
        1) Instantaneous, Fixed Wall Temperature imparted at T=0 seconds
        2) Specified Heatflux imparted at T=0 seconds

    Both simulations start from equilibrium, and the semi-infinite-ness is approximated by making the walls really
    thick. Since this is a 1D tool, we are already handling the other dimensions fine.


TODO:
    -

REFERENCES:
    [1] Incropera et al., Fundamentals of Heat and Mass Transfer Sixth Edition, CH 5.7, Pg. 283-295
'''


################################# ANALYTICAL SOLUTIONS ########################################

# Instant Surface Temperature Analytical Solution
def inst_T_an(x, t, T_i, T_s, alp):
        # x x location list
        # t time, float
    return  (T_i-T_s) * special.erf(    x / (2*math.sqrt(alp*t))       ) + T_s


# Fixed Heat Flux Analytical Solution
def q_0_an(x, t, T_i, q_0, alp):
        # x x location list
        # t time, float
    return 2 * q_0 * math.sqrt(alp*t/math.pi) * np.exp( -x**2/(4*alp*t) ) / k   \
        - q_0 * x * ( 1-special.erf( x/(2*math.sqrt(alp*t))) ) / k      \
            + T_i
           


################################# MAIN ########################################
if __name__ == "__main__":

    
    ################################# INPUTS/PARAMETERS ########################################
    
    # Instantaneous Temp Testcase Parameters
    T_i = 300.0 #[K] Initial Material Temperature
    T_s = 350.0 #[K] Temperature Imparted instantanously at the surface at x=0

    # Fixed Heatflux Testcase Parameters
    q_0 = 150000 #[W/m^2]

    # Test thickness
    test_thickness = 0.05

    # Node count
    n_nodes = 250

    # Time Values to plot at
    t_plot = np.array([0.0, 1.0, 2.5, 5.0, 10.0, 15.0, 25.0, 50.0])

    # Position vectors to plot at
    x_anly = np.linspace(0.0, test_thickness, num=n_nodes)
    
    x_temp_sim = np.linspace(0.0, test_thickness*10, num=n_nodes)
    x_q0_sim = x_temp_sim + x_temp_sim[1]/2

    ### Material Properties 
    test_material = "ALU6061"

    rho    = MATERIALS_DICT["ALU6061"]["rho"]
    cp     = MATERIALS_DICT["ALU6061"]["cp"]
    k      = MATERIALS_DICT["ALU6061"]["k"]
    emis   = MATERIALS_DICT["ALU6061"]["emis"]
    alp             = k/(rho*cp)

    

    ############################## NETWORK DEF'N AND SIMULATIONS ########################################
    
    ### SPECIFIED TEMP NETWORK
    T0Network = ThermalNetwork()
    T0Network.addComponent_1D("ALU6061", total_thickness=test_thickness*10, n_nodes=n_nodes)
    T0Network.add_temperature_constraint(nodeID = 0, temperature=T_s)
    T0_Sim = TransientThermalSim( T0Network,  T_initial=T_i,  t_step=0.01, t_start = 0.0, t_end = t_plot[-1]+0.001)

    ### SPECIFIED QDOT NETWORK
    qDotNetwork = ThermalNetwork()
    qDotNetwork.addComponent_1D("ALU6061", total_thickness=test_thickness*10, n_nodes=n_nodes)
    qDotNetwork.add_thermal_loading(nodeID = 0, ThermLoading = ConstantQdotLoading(q_0))
    q0_Sim = TransientThermalSim( qDotNetwork,  T_initial=T_i,  t_step=0.01, t_start = 0.0, t_end = t_plot[-1]+0.001)
    
    ### Run Simulations
    T0_Sim.run()
    q0_Sim.run()



    ################################# PLOTTING ########################################
    
    ### Instant Temperature Plot
    plt.figure()
    for tP in t_plot:
        #Get Index of Sim time index at time
        sim_i = np.where(T0_Sim.t_vec == tP)

        # Analytical 
        plt.plot(x_anly, inst_T_an(x_anly, tP, T_i, T_s, alp),                     label = "An "+str(tP)) 
        # Simulated
        plt.plot(x_temp_sim, T0_Sim.wall_temps[:,sim_i[0][0]],       linestyle='--',    label = "Sim "+str(tP)) 

    plt.legend()
    plt.xlabel("Depth (m)")
    plt.ylabel("Temeperature (K)")
    plt.title("Inst. Temp - Temp vs. Depth at Different Times")
    plt.xlim([x_anly[0], x_anly[-1]])
    plt.ylim([T_i, T_s])


    ### Heat Flux Plot
    plt.figure()
    for tP in t_plot:
        #Get Index of Sim time index at time
        sim_i = np.where(q0_Sim.t_vec == tP)

        # Analytical 
        plt.plot(x_anly, q_0_an(x_anly, tP, T_i, q_0, alp),                     label = "An "+str(tP)) 
        # Simulated
        plt.plot(x_q0_sim, q0_Sim.wall_temps[:,sim_i[0][0]],       linestyle='--',    label = "Sim "+str(tP)) 

    plt.legend()
    plt.xlabel("Depth (m)")
    plt.ylabel("Temeperature (K)")
    plt.title("Heat Flux - Temp vs. Depth at Different Times")
    plt.xlim([x_anly[0], x_anly[-1]])
    plt.ylim([T_i, T_s])

    plt.show()

