'''

This includes test cases for checking the Transient Thermal conduction implementation. 

Both are examples pulled from Incopera (see below) for a semi-infinite plate (infinite in all directions but one),
where a wall at a fixed temperature is subjected at t=0.0 to either a fixed surface temperature, or a prescribed heat flux. 



### USAGE ###
I KNOW THIS IMPLEMENTATION IS DOGSHIT, BUT HERE'S HOW TO RUN THESE

From the stata_mater base folder, run the following command:
python3 tests/transient_conduction_verify.py

I'm sorry 


References:
[1] Incropera et al., Fundamentals of Heat and Mass Transfer Sixth Edition, CH 5.7, Pg. 283-295

'''

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import time
import math
from scipy import special
import pickle

#I have to do stupid ass directory bullshit because Python is shit with imports
# Make it so it can find the 
sys.path.append(os.path.dirname(os.getcwd()))

#from stata_mater.src.materials_solid import solidMaterialDatabase
from stata_mater.src.materials_solid import MATERIALS_DICT
from stata_mater.src.obj_wallcomponents import WallStack
from stata_mater.src.tools_conduction import get_new_wall_temps



### ANALYTICAL SOLUTIONS

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
           



class Semi_Inf_Wall_Temp_Sim:
    #Pared down version of FligtSimulation object to just do wall conduction
    #Either Specify T_s OR q_0 to switch between ints. temp or heat flux cases

    def __init__(
        self,
        Aerosurface,
        t_step,
        t_start,
        t_end,
        T_initial=None,
        T_surface=None,
        q_0=None
    ):

        self.T_i = T_initial
        self.T_s = T_surface
        self.t_step = t_step
        self.Aerosurface    = Aerosurface

        # Generate Data Arrays
        self.t_vec = np.arange(t_start, t_end, t_step)
        self.wall_temps = np.zeros((self.Aerosurface.n_tot, np.size(self.t_vec)), dtype=float)

        #Set initial wall temp
        self.wall_temps[:,0] = self.T_i


        #Set heat flux, initial conditions
        if q_0 == None and T_surface is not None:
            self.q_net = np.zeros((np.size(self.t_vec),), dtype=float)
            self.wall_temps[0,0] = self.T_s
        elif q_0 is not None and T_surface is None:
            self.q_net = q_0*np.ones((np.size(self.t_vec),), dtype=float)
        else:
            print("Either specify T_s or q_0, not both")
        

    def run(self):

        print("Simulation Progress: ")
        # For each time step (except for the last)
        for i, t in enumerate(self.t_vec[:-1]):

            # Update Temps
            #self.wall_temps[:,i+1] = get_new_wall_temps( self.wall_temps[:,i], self.q_0, self)
            get_new_wall_temps(self, i)


            #Force Surface to stay at constant temp
            if self.T_s is not None:
                self.wall_temps[0,i+1] = self.T_s

            # Print Time to screen every 5 sim seconds
            if self.t_vec[i]%5 == 0:  print(self.t_vec[i], " seconds...") 




if __name__ == "__main__":

    
    ### INPUTS 
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

    

    ### SETUP AND SIMULATIONS
    
    # Create Wall Object
    Wall = WallStack(materials="ALU6061", thicknesses=0.5, node_counts = 400)
    #Get coordinate data from wall
    sim_x = Wall.get_wall_coords()

    
    #Create Simulation Objects
    Temp_Sim = Semi_Inf_Wall_Temp_Sim(Aerosurface=Wall,
                                        t_step = 0.01,
                                        t_start = 0.0,
                                        t_end = t_plot[-1]+0.001,
                                        T_initial=T_i,
                                        T_surface=T_s)

    q_Sim = Semi_Inf_Wall_Temp_Sim(Aerosurface=Wall,
                                        t_step = 0.01,
                                        t_start = 0.0,
                                        t_end = t_plot[-1]+0.001,
                                        T_initial=T_i,
                                        q_0 = q_0)

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
    with open ("validation_cases/trans_cond_set_temp.sim", "wb") as f: pickle.dump(Temp_Sim, f)
    with open ("validation_cases/trans_cond_set_q.sim", "wb") as f: pickle.dump(q_Sim, f)



    ### Plotting 
    
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
