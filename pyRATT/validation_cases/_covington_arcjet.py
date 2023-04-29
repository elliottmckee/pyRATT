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
- Add additional Hifire heatflux comparison plots
- Add Thermal Interface Resistances
- Ablation Modelling
- Expand Fin/Root Heating
- Stagnation Point Heating
- Add temperature dependant material properties, for example, thermal conductivity changes at high temp
- Lumped Capacitance Simulations for things like nosecones
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

#todo: this is super goofy- find better way to do this
sys.path.append(os.path.dirname(os.getcwd()))

try:
    from pyRATT.src.obj_simulation import Thermal_Sim_1D
    from pyRATT.src.obj_flightprofile import FlightProfile
    from pyRATT.src.obj_wallcomponents import WallStack
    from pyRATT.src.materials_gas import AirModel
    from pyRATT.src.materials_ablative import ABLATIVE_DICT

except:
    print("\n Run this script from the main pyRATT directory using 'python3 validation_cases/hifire_5.py")
    quit()








if __name__ == "__main__":



    # Define Ablative Wall
    AeroSurf = WallStack(materials="PICA", thicknesses=0.0274, element_counts =25)

    # Point to Trajectory Data CSV (not utilized, but currently breaks if you don't point to one)
    Flight    = FlightProfile( os.path.join(os.getcwd(), "example_files", "example_ascent_traj_M2245_to_M1378.csv") )
    

    MySimulation= Thermal_Sim_1D(AeroSurf, Flight, AirModel(),
                                t_step = 0.001,
                                t_end = 30,
                                aerothermal_model="covingtonArcJet")




    #Run Simulation
    MySimulation.run()

    #Calculate Recession:
    print(f"Recession: {(0.0274 - AeroSurf.get_ablative_thickness())[0] * 1000} mm" )


    # #Export
    # # To CSV
    # MySimulation.export_data_to_csv("mysimulation.csv")
    # #Export via Pickle
    # with open("mysimulation.sim", "wb") as f: pickle.dump(MySimulation, f)




    
    #################################### PLOTTING ####################

    # Load in validation Data
    valData_tempTime = pd.read_csv( os.path.join(os.getcwd(), "validation_cases", "resources", "covington_arcjet", "verify_TempVTime.csv"),
                                header = 1, names=['PyroX','PyroY','Cov2004X','Cov2004Y','UsluX','UsluY'])

    valData_T_dist = pd.read_csv( os.path.join(os.getcwd(), "validation_cases", "resources", "covington_arcjet", "verify_TempDist.csv"),
                                header = 0, names=['UlsuX','UlsuY'])

    valData_rho_dist = pd.read_csv( os.path.join(os.getcwd(), "validation_cases", "resources", "covington_arcjet", "verify_DensityDist.csv"),
                                header = 0, names=['UlsuX','UlsuY'])


    # valData_covington_dist = pd.read_csv( os.path.join(os.getcwd(), "validation_cases", "resources", "covington_arcjet", "CovingtonDataDist.csv"),
    #                             header = 0, names=['TC1-.52cm',,'TC2-1.02cm',,'TC3-1.76cm',,'FIAT-.52cm',,'FIAT-1.02cm',,'FIAT-1.76cm',])




    ########## Temperature vs. Time Plot
    plt.figure()

    plt.plot(MySimulation.t_vec, MySimulation.wall_temps[0,:] - 273.15,      label = "pyRATT", linestyle="-", color='red') 

    plt.plot(valData_tempTime["PyroX"], valData_tempTime["PyroY"],    label = "Pyrometer", linestyle="-", color='maroon')
    plt.plot(valData_tempTime["Cov2004X"], valData_tempTime["Cov2004Y"],    label = "Covington2004", linestyle="-", color='maroon')
    plt.plot(valData_tempTime["UsluX"], valData_tempTime["UsluY"],    label = "Ulsu", linestyle="-", color='blue')


    plt.plot((15, 15),(-10000, 10000), "k--")

    plt.xlabel("Time (s)")
    plt.ylabel("Temperature (C)")
    plt.title("Covington 2004 Arcjet Ablative Verification")

    plt.legend()

    plt.xlim( 0.0, 30.0)
    plt.ylim( 500.0, 3000.0)
        


    ######### Through-Wall Temperature Distribution Plot
    
    # Get Index corresponding to 15 seconds
    Idx_15 = np.where( np.isclose(MySimulation.t_vec, 15.0))[0]
    
    # Create New Figure
    fig, ax1 = plt.subplots()

    # Create righthand Y axis
    ax2 = ax1.twinx()



    ### Temperature Plot
    color = 'tab:red'

    ax1.plot(MySimulation.Aerosurface.y_coords, MySimulation.wall_temps[:,Idx_15] - 273.15, marker='o',  label = "pyRATT", color=color)

    ax1.plot(valData_T_dist["UlsuX"]/1000, valData_T_dist["UlsuY"],    label = "Ulsu", linestyle="-", color='maroon')


    ax1.set_xlabel('Through-Wall Location (m)')
    ax1.set_ylabel('Temperature (C)', color=color)
    ax1.tick_params(axis='y', labelcolor=color)



    ### Density Plot
    color = 'tab:blue'
    
    ax2.plot(MySimulation.Aerosurface.y_coords, MySimulation.wall_dens[:,Idx_15], marker='o',  label = "pyRATT", color=color)

    ax2.plot(valData_rho_dist["UlsuX"]/1000, valData_rho_dist["UlsuY"],    label = "Ulsu", linestyle="-", color='maroon')

    

    ax2.set_ylabel('Density (kg/m^3)', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    
    

    plt.title("Temperature and Density Distribution at T=15.0s")
    #fig.tight_layout()


    plt.show()







    # # Plot Results (can also use GUI)
    #Post.plot_results(MySimulation)