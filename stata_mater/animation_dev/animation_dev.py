'''
---------------------------------------------------------------------------
pyRATT - Python Rocket AeroThermal Toolbox 
---------------------------------------------------------------------------

pyRATT is a thermal analysis toolbox for *very* high-performance/high-altitude 
amateur rocketry applications. 

Primarily, it can perform a 1-Dimensional, transient thermal simulation of 
the wall structure of a vehicle for an arbitrary flight profile. For a 
specified flight trajectory, it calculates both the aerothermal heat loading, 
as well as the thermal conduction throughout the wall to simulate the through-
wall temperature distribution throughout the flight, to give the designer an
intuition on the types of temperatures they are likely to see in flight.

I have tried to make this tool as simple as possible, requiring the following 
as a minimum set of inputs to run a simulation:
    
    1) Trajectory Simulation Data (like from RASAero)
    2) Geometric Parameters (Wall thickness, nosecone angles, etc.)
    3) Material Properties (density, specific heat, 
                            thermal conductivity, and a ballpark emissivity)


There are a whole lot of simplifications and assumptions going into all of the
analyses performed here. I will attempt to document them better in the GitHub
ReadME, but I will list a non-exhaustive list of them here:

    1) The only conduction being modelled is in the through-wall direction. 
        No heat conduction along the axial or transverse axes is modelled.
    2) Most of the Aerothermal Models are derived from modified flat-plate
        heating correlations. 
    3) There is currently no implementation for the effects of surface coverings,
        like paints, etc.
    4) The boundary condition at the cold-wall side of the wall being simulated
        is assumed to be adiabatic- i.e. no heat transfer to the interior volume
    5) There's a lot more here I am forgetting...


This is all to say, I PROVIDE NO GUARANTEE OF THE ACCURACY/RELIABILITY
OF THE RESULTS OF THIS SIMULATION TOOL. THIS TOOL IS PROVIDED AS-IS. (i think
i'm missing some stuff here, but yeah)


That being said, I have found a couple of test-cases in the literature to compare 
with, and those verification/validation cases are furnished along with this code.

I am always looking to validate this more, however. I am working on my own projects
to give me more actual data to verify the predictive capability of this tool, but 
if you have any sort of thermal/thermocouple data from a rocket you've 
(or others have) flown, I would love to use it to benchmark this sim. 


---------------------------------------------------------------------------
AUTHOR, MAINTAINER: 
-Elliott McKee 
    email: elliott.mckee@proton.me
    github: elliottmckee


COLLABORATORS: 
-Owen Kaufmann


CREATED (initially): 2021-02-06
TRANSFERRED TO PYTHON: early 2023
---------------------------------------------------------------------------

REFERENCES: 
I have way too many references on rocket aerothermo, ablation, etc. at this 
point, but this is a (likely incomplete) list of some of the main ones.

*** 
The first reference below is what inspired this tool. Its explains all of
this so much better than I can, and to be quite honest, most of this tool
is basically designed in the footsteps of this work. Shoutout Ulsu et al. 
for real.
*** 


[1] Uslu, Sitki & Simsek, Bugra. (2019). One-Dimensional Aerodynamic 
    Heating and Ablation Prediction. Journal of Aerospace Engineering. 
    32. 10.1061/%28ASCE%29AS.1943-5525.0001042. 
 

[2] HIFiRE-5 Flight Test Results, Thomas J. Juliano, David Adamczak, and 
    Roger L. Kimmel, Journal of Spacecraft and Rockets 2015 52:3, 650-663


[3] Uslu, Sitki & Simsek, Bugra. (2020). VALIDATION OF AERODYNAMIC HEATING 
    PREDICTION TOOL. 40. 53-63. 

[4] Bertin, J.J. 1994. Hypersonic aerothermodynamics. Reston, VA: AIAA.



NOTES:
- 



TODO : 
- Add additional Hifire heatflux comparison plots
- Add Thermal Interface Resistances
- Ablation Modelling
- Expand Fin/Root Heating
- Stagnation Point Heating
- Add temperature dependant material properties, for example, thermal conductivity changes at high temp
- Lumped Capacitance Simulations for things like nosecones
- Clean up the nodes vs. elements nomenclature throughout
    -In WallSurf- node/elemement ambiguity may cause issues at interfaces when different sized wall elements, for y coord calculation
- (Low prio) Add emissivity value specification at runtime so can work like independant variable
- Find more efficient way to index from Atmos?

- Use CEA to create a high-temp air model? Also look into:
    https://www.cambridge.org/us/files/9513/6697/5546/Appendix_E.pdf



---------------------------------------------------------------------------
prRATT - Python Rocket AeroThermal Toolbox 
---------------------------------------------------------------------------
'''


#Standard Libraries
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import filecmp
import time
import pickle

#Internal Modules
from src.obj_simulation import Thermal_Sim_1D
from src.obj_flightprofile import FlightProfile
from src.obj_wallcomponents import WallStack
from src.materials_gas import AirModel
import src.tools_postproc as Post


import matplotlib.pyplot as plt 
import matplotlib.animation as animation

#plt.style.use('seaborn-pastel')



if __name__ == "__main__":

    
    # Read in Sim File
    with open("multi_material_example_out.sim", "rb") as input_file:
            Sim = pickle.load(input_file)

        

    # print(Sim.y_coords)

    # quit()


    plt.rcParams['text.color'] = "#f8f8f2"
    plt.rcParams['axes.labelcolor'] = "#f8f8f2"
    plt.rcParams['xtick.color'] = "#f8f8f2"
    plt.rcParams['ytick.color'] = "#f8f8f2"

    #Create Figure
    fig, ax = plt.subplots(2, facecolor="#282a36", figsize=(13, 10))
    #plt.tight_layout()

    

    # Plot 1 
    line, = ax[0].plot(Sim.y_coords, Sim.wall_temps[:,0], color="#bd93f9", linewidth=2)

    ax[0].set_title(f"Wall Temperature Distribution at t=0.000 seconds")
    ax[0].set_xlim(min(Sim.y_coords), max(Sim.y_coords))
    ax[0].set_ylim( 0.95*np.amin(Sim.wall_temps), 1.05*np.amax(Sim.wall_temps))

    ax[0].set_xlabel("Through-Wall Location [m]")
    ax[0].set_ylabel("Temperature [K]", color="#bd93f9")
    ax[0].tick_params(axis='y', labelcolor="#bd93f9")
    ax[0].set_facecolor("#44475a")

    ax[0].grid(True, color="#282a36")

    verticalline2, = ax[0].plot([0.00666, 0.00666], [-1000.0, 1000000.0], "k--", linewidth=2)

    ax[0].annotate("<- Carbon Fiber", [0.0054,800], color="#ff79c6")
    ax[0].annotate("Aluminum ->",  [0.0068, 800], color="#ff79c6")


    # verticalline2, = ax[0].plot([0.00635, 0.00635], [-1000.0, 1000000.0], "k--", linewidth=2)
    # ax[0].annotate("Fin Centerline", [0.00640, 530], color="#000000")
    # ax[0].set_xticks([0.0, 0.003175, 0.00635, 0.009525, 0.0127])
    



    # Plot 2 
    ax2 = ax[1].twinx()

    ax[1].set_title("Flight Profile")
    ax[1].set_xlim([0.0, max(Sim.t_vec)])
    ax[1].set_xlabel("Flight Time (s)")
    ax[1].set_ylabel('Mach', color="#50fa7b")
    ax[1].tick_params(axis='y', labelcolor="#50fa7b")
    ax[1].set_facecolor("#44475a")
    ax[1].grid(True, color="#282a36")

    
    
    
    
    machline, = ax[1].plot(Sim.t_vec, Sim.mach, color="#50fa7b")
    machpoint = ax[1].scatter(Sim.t_vec[0], Sim.mach[0], color="#50fa7b")


    ax2.set_ylim([0.0, max(Sim.alt)])
    ax2.set_ylabel('Altitude [m]', color="#8be9fd")
    ax2.tick_params(axis='y', labelcolor="#8be9fd")
    altline, = ax2.plot(Sim.t_vec, Sim.alt, color="#8be9fd")
    altpoint = ax2.scatter(Sim.t_vec[0], Sim.alt[0], color="#8be9fd")

    verticalline, = ax2.plot([0.0, 0.0], [-1000.0, 1000000.0], "k--", linewidth=0.5)

    def animate(i):
        
        #Skipping timesteps since i is called sequentialls
        i = i*40


        ax[0].set_title(f"Wall Temperature Distribution at t={Sim.t_vec[i]:.3f} seconds")

        line.set_ydata(np.flip(Sim.wall_temps[:,i]))

        verticalline.set_xdata([Sim.t_vec[i],Sim.t_vec[i]])

        machpoint.set_offsets([Sim.t_vec[i], Sim.mach[i]])
        altpoint.set_offsets([Sim.t_vec[i], Sim.alt[i]])


        return line

    ani = animation.FuncAnimation(fig, animate, frames=250, interval= 50, repeat=True) 

    #ani.save('flight.gif', fps=10.0)


    ani.save("test.gif", writer= animation.PillowWriter(fps=20))
    
    
    #plt.show()
