

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import time
import math
from scipy import special
import pickle

#todo: this is super goofy- find better way to do this
sys.path.append(os.path.dirname(os.getcwd()))

try:
    from pyRATT.src.materials_solid import MATERIALS_DICT
    from pyRATT.src.obj_wallcomponents import WallStack
    from pyRATT.src.tools_conduction import get_new_wall_temps
except:
    print("\n Run this script from the main pyRATT directory using 'python3 validation_cases/transient_cond.py")
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
    Idk just like, clean this one up. Its gross, and needs to be sleeker and integrated better. 

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
           


################################# MODIFIED CLASS FOR TESTING ########################################

class Transient_Cond_Sim:
    """
    Pared down version of Thermal_Sim_1D for the purposes of these testcases.

    Should ideally make pull this functionality into the Thermal_Sim_1D object. 
    
    """

    def __init__(
        self,
        Aerosurface,
        t_step,
        t_start = 0.0,
        t_end = None,
        initial_temp = 290.0,
        set_T = None,
        set_q0 = 0.0,
        wall_thermal_bcs = ["q_in_aerothermal","adiabatic"]
    ):
        
        #Unavoidable gross block of passing-through variables
        self.Aerosurface            = Aerosurface 
        self.t_step                 = t_step
        self.t_start                = t_start
        self.t_end                  = t_end
        self.initial_temp           = initial_temp

        self.set_T                  = set_T
        self.set_q0                 = set_q0
        
    
        self.wall_thermal_bcs       = wall_thermal_bcs

        #Get Vector of Wall Nodal Coordinates
        #self.y_coords               = Aerosurface.get_wall_coords() 

        #Initialize Simulation 
        self.sim_initialize()


    def sim_initialize(self):
        """
        Pre-allocate and initialize all datastructs needed to run simulation
        """
        self.t_vec = np.arange(self.t_start, self.t_end, self.t_step)
            
        # get time vector size
        self.t_vec_size      = np.size(self.t_vec)

        ### PRE ALLOCATION OF DATA STRUCTS
        self.q_net     = self.set_q0 * np.ones((self.t_vec_size,), dtype=float) # Convective Heat Flux [w/m^2]
        
        # Vector Quantities vs. Time
        self.wall_temps = np.zeros((self.Aerosurface.elem_tot,self.t_vec_size), dtype=float)

        #Set Initial Values for Wall Temperature at First Step
        self.wall_temps[:,0] = self.initial_temp


    def run(self):
        """ 
        High-level Simulation Run Loop

        """

        print("Simulation Progress (in sim-time): ")
        time_progress_marker = self.t_vec[0] 

        ####### MAIN SIMULATION LOOP #######
        # For each timestep
        for i, t in enumerate(self.t_vec[:-1]):


            #If temp sim, force surface temp to be equal to setTemp
            if self.set_T:
                self.wall_temps[0,i] = self.set_T


            # Get New Wall Temperatures
            get_new_wall_temps(self, i)

            # Update screen every 5 seconds in sim-time
            if self.t_vec[i] > time_progress_marker:  
                print(time_progress_marker, " seconds...")
                time_progress_marker += 5.0 




################################# MAIN ########################################


if __name__ == "__main__":

    
    ###### INPUTS/PARAMETERS ###### 
    
    # Instantaneous Temp Testcase Parameters
    T_i = 300.0 #[K] Initial Material Temperature
    T_s = 350.0 #[K] Temperature Imparted instantanously at the surface at x=0

    # Fixed Heatflux Testcase Parameters
    q_0 = 150000 #[W/m^2]

    # Test Material
    test_material = "ALU6061"

    # Time Values to bound and plot at
    t_plot = np.array([0.0, 1.0, 2.5, 5.0, 10.0, 15.0, 25.0, 50.0])

    # Position Values to Bound and plot at
    x_plot = np.linspace(0.0, 0.05, num=50)
    
    ### DERIVED VALUES 
    rho    = MATERIALS_DICT["ALU6061"]["rho"]
    cp     = MATERIALS_DICT["ALU6061"]["cp"]
    k      = MATERIALS_DICT["ALU6061"]["k"]
    emis   = MATERIALS_DICT["ALU6061"]["emis"]

    alp             = k/(rho*cp)

    


    ##### SETUP AND SIMULATIONS #######
    
    # Create Wall Object
    Wall = WallStack(materials="ALU6061", thicknesses=0.5, element_counts = 400)
    #Get coordinate data from wall
    sim_x = Wall.get_wall_coords()

    
    # Specified Surface Temperature Sim
    Temp_Sim = Transient_Cond_Sim(Aerosurface=Wall,
                                t_step = 0.01,
                                t_start = 0.0,
                                t_end = t_plot[-1]+0.001,
                                initial_temp=T_i,
                                set_T=T_s,
                                wall_thermal_bcs = ["q_in_aerothermal","adiabatic"])



    # Specified Heatflux Sim
    q_Sim = Transient_Cond_Sim(Aerosurface=Wall,
                                t_step = 0.01,
                                t_start = 0.0,
                                t_end = t_plot[-1]+0.001,
                                initial_temp=T_i,
                                set_q0=q_0,
                                wall_thermal_bcs = ["q_in_aerothermal","adiabatic"])

    # Run Simulations
    start=time.time()
    Temp_Sim.run()
    end = time.time()
    print("Elapsed Time for Sim Run: ", end - start)

    start=time.time()
    q_Sim.run()
    end = time.time()
    print("Elapsed Time for Sim Run: ", end - start)


    ### Exporting/Pickling
    with open ("trans_cond_set_temp_validate.sim", "wb") as f: pickle.dump(Temp_Sim, f)
    with open ("trans_cond_set_q_validate.sim", "wb") as f: pickle.dump(q_Sim, f)



    



    ################################# PLOTTING ########################################
    
    ### Instant Temperature Plot
    plt.figure()

    for tP in t_plot:
        #Get Index of Sim time index at time
        sim_i = np.where(Temp_Sim.t_vec == tP)

        # Analytical 
        plt.plot(x_plot, inst_T_an(x_plot, tP, T_i, T_s, alp),                     label = "An "+str(tP)) 
        # Simulated
        plt.plot(sim_x, Temp_Sim.wall_temps[:,sim_i[0][0]],       linestyle='--',    label = "Sim "+str(tP)) 

    plt.legend()
    plt.xlabel("Depth (m)")
    plt.ylabel("Temeperature (K)")
    plt.title("Inst. Temp - Temp vs. Depth at Different Times")
    plt.xlim([x_plot[0], x_plot[-1]])
    plt.ylim([T_i, T_s])


    ### Heat Flux Plot
    plt.figure()
    
    for tP in t_plot:
        #Get Index of Sim time index at time
        sim_i = np.where(q_Sim.t_vec == tP)

        # Analytical 
        plt.plot(x_plot, q_0_an(x_plot, tP, T_i, q_0, alp),                     label = "An "+str(tP)) 
        # Simulated
        plt.plot(sim_x, q_Sim.wall_temps[:,sim_i[0][0]],       linestyle='--',    label = "Sim "+str(tP)) 

    plt.legend()
    plt.xlabel("Depth (m)")
    plt.ylabel("Temeperature (K)")
    plt.title("Heat Flux - Temp vs. Depth at Different Times")
    plt.xlim([x_plot[0], x_plot[-1]])
    plt.ylim([T_i, T_s])


    plt.show()
