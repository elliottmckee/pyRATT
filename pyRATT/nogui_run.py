'''
---------------------------------------------------------------------------
PyRATT - Python Rocket AeroThermal Toolbox 
---------------------------------------------------------------------------

PyRATT is a thermal analysis toolbox for *very* high-performance/high-altitude 
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
- Fix Bug with Coordinates when using multi-component walls
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



if __name__ == "__main__":



    # Define Wall
    AeroSurf = WallStack(materials="ALU6061", thicknesses=0.02, node_counts = 15)

    # Point to Trajectory Data CSV
    Flight    = FlightProfile( os.path.join(os.getcwd(), "example_files", "example_ascent_traj_M2245_to_M1378.csv") )
    
    # Define Simulation Object
    MySimulation= Thermal_Sim_1D(AeroSurf, Flight, AirModel(),
                                x_location = 0.2, 
                                deflection_angle_deg = 7.0, 
                                t_end = 30.0,
                                t_step = 0.0050,
                                boundary_layer_model = 'transition')

    #Run Simulation
    MySimulation.run()


    #Export
    # To CSV
    MySimulation.export_data_to_csv("mysimulation.csv")
    #Export via Pickle
    with open("mysimulation.sim", "wb") as f: pickle.dump(MySimulation, f)


    # Plot Results (can also use GUI)
    Post.plot_results(MySimulation)