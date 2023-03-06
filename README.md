# pyRATT - python Rocket AeroThermal Toolbox

pyRATT is an Aero/Thermal Analysis tool aimed at *very* high performance (or high-speed) amateur rockets, or for performing more general 1D Transient Thermal analyses.

Primarily, it performs coupled Aerothermal/Thermal simulations of the temperature response of structural components like nosecone walls and fins, given a flight profile, material properties, geometric parameters, etc. This functionality aims to be as approachable and easy-to-use as possible, with GUIs both for running simulations, as well as plotting results. Even without the GUI's, running from a standalone script is only a handful of lines of code (see below).

Secondarily, it aims to be a more general tool for analyzing more general, 1D transient thermal behavior, with a ton of flexibility in being able to handle varied/mixed wall material types, wall thermal boundary conditions etc. 

This work is heavily inspired by the work of Ulsu, Simsek [1]. This paper talks about all the mathematical underpinnings of this tool in a much more succinct/organized way than I would be able to, so I will reccomend those looking for something like a theory-guide, to check out that paper (linked in References below)


#  Notices
This is currently in what I am humbly going to call a "Pre-Release" state. There are definitely still issues (specifically with the GUI's being a bit finicky and not fully polished by any means), but I want to get it out here to gauge interest to see how much I should be developing this for others vs. just myself.

Please do let me know if you run into any issues with any part of it, or have any questions. This helps me know what to fix, where to add additional information, etc. 
 
Currently, only RASAero files are supported for trajectory input, but let me know if you need another format. 

The best places to check for information are:
- This readme
- The header of `nogui_run.py`
- The comments/docstrings of the Objects/Functions .py files in `.src` themselves
- Asking me (elliottmckee)



# Demonstrations

Some examples of the results of the flight-thermal-simulation functionality of the code are shown below. 

These example files used to generate these simulations can be found in `pyratt/example_files/`. Instructions on how to run them can be found below. 




## Nosecone Heating: `pyratt/example_files/example_nosecone.py`

This is a 1D Transient Thermal/Aerothermal simulation of a nosecone along a flight trajectory simulated by RASAeroII [2] of 2-stage rocket, using a M2245 to M1378 to get to just below Mach 5 (trajectory shown in the figure below).

A location/station 20 cm downstream of the nosecone tip was analyzed, using the following geometric properties:
 - Wall Thickness: 1.0 cm
 - Wall Material: **316 Stainless**
 
 The first figure shows an animation of the temperature distribution in the through-wall direction, throughout flight, in real-time, alongside the flight trajectory. 
 
 The second figure shows the hot-wall (outer surface) and cold-wall (inner surface) temperatures seen throughout the flight. 


![alt text](https://github.com/elliottmckee/stata_mater/blob/main/images/example_nosecone_SS.gif?raw=true)  |  ![alt text](https://github.com/elliottmckee/stata_mater/blob/main/images/example_nosecone_SS.jpg?raw=true)
:-------------------------:|:-------------------------:



And here's the same trajectory and geometry as above, but with __much__ more thermally-conductive __6061 Aluminum__ as the Wall Material:

![alt text](https://github.com/elliottmckee/stata_mater/blob/main/images/example_nosecone_ALU.gif?raw=true)  |  ![alt text](https://github.com/elliottmckee/stata_mater/blob/main/images/example_nosecone_ALU.jpg?raw=true)
:-------------------------:|:-------------------------:




_These 25-second simulations each ran in ~10 seconds on a 1.8Ghz i5-8250U using Conda Python 3.9.7_




##  Fin Heating: `pyratt/example_files/example_fin.py`

This is a 1D Transient Thermal/Aerothermal simulation of a Fin along the same flight trajectory as the previous example.

A location/station 10 cm downstream of the fin leading edge was analyzed, using the following geometric properties:
 - Fin Thickness: 1.27cm or 0.5in  
 - Fin Material: 316 Stainless
 - Fin Chamfer Angle: 10 degrees
 
 The first figure shows an animation of the through-wall temperature distribution in the through-wall direction, throughout flight, in real-time, alongside the flight trajectory. 
 
 The second figure shows the hot-wall (outer surface) and centerline temperatures seen throughout the flight. 



![alt text](https://github.com/elliottmckee/stata_mater/blob/main/images/example_fin_SS.gif?raw=true) | ![alt text](https://github.com/elliottmckee/stata_mater/blob/main/images/example_fin_SS.jpg?raw=true)
:-------------------------:|:-------------------------:


## Multi-Component Nosecone Heating: `pyratt/example_files/example_multi_component_nosecone.py`

pyRATT can handle walls made up of multiple materials. For example, if you have a TPS material layer on top of a structural one. 

As a kinda goofy demonstration of this functionality, the following example is the same Aluminum nosecone from the first example, but where the inner 2/3rds is replaced with Carbon Fiber, as opposed to being 100% Al.


 - Wall Composition: 0.66cm of Carbon Fiber, then 0.33 cm of Aluminum 6061


In the below figure I have marked where the material transition occurs. 

The below figure shows just how bad traditional composite materials are at conducting heat- and because we are effectively removing a bunch of high-thermal-mass aluminum and not allowing the heat to go anywhere, it gets nice and toasty. 



![alt text](https://github.com/elliottmckee/stata_mater/blob/main/images/example_multi_material_nc.gif?raw=true) | ![alt text](https://github.com/elliottmckee/stata_mater/blob/main/images/example_multi_material_nc.jpg?raw=true)
:-------------------------:|:-------------------------:









# Functionality

## Core

## Planned









# Quickstart Guide

## Installation/Requirements

pyRATT requires Python 3. Just for reference, I am currently developing it on 3.9.7. 

The required packages to install can be found in the `requirements.txt` file in the repo base directory. 
- Running `pip install -r requirements.txt` from this folder should install them all automatically.

If you're new to python, and on Windows (maybe the others, this is just what I use) The plotting/GUI portions of this tool require some way of interacting with Linux graphical appications. So if plots and GUI's dont show up, you'll also need a Display Server or something, idk, see [here](https://devpress.csdn.net/python/62fd06487e6682346619136c.html "here").

This tool uses Ambiance [3] for the Atmosphere model. 



## Running with the GUI: `gui_run.py`

### Running Simulations

 Navigate to wherever you cloned this repo to, and enter the main `/pyratt` directory. You should see `gui_run.py` and `gui_post.py`, among other things here. 
 
 To open the Simulation-Run GUI: `python3 gui_run.py`
 
 * It'll look something like the image below, but with additional instructions.
 * There is an example flight trajectory here: `example_files/example_ascent_traj_M2245_to_M1378.csv`. 
   * If this wasn't an example, this is where you would normally input your own RASAeroII flight trajectory output file. The instructions on how to do that are at the top of the GUI window.
 * Enter your simulation properties. The GUI has explanations of all of the inputs, but it'll look something like this:

![alt text](https://github.com/elliottmckee/pyRATT/blob/main/images/gui_run_example.PNG?raw=true)

- Hit "Run"
 - The simulation should run. You check by looking at your terminal, where it will print the simulation progress as it goes:
 ```bash
Initializing Simulation1:
Running Simulation...
Simulation Progress (in sim-time):
0.0  seconds...
5.0  seconds...
10.0  seconds...
...
Time to Simulate:  27.074697971343994
Exporting Data...
Done!
```
* There will be 2 output files. `mysimulation.csv` will be a .csv file with your simulation data, and `mysimulation.sim` is a pickled/serialized version of the Thermal_Sim_1D Object that was used to run the sim, which can be read back into other python scripts for further data processing, etc. (this is what the post-gui uses)
* When the simulation is finished, close the window.


### Viewing Simulation Data: `gui_post.py`

* From the main `\pyratt` directory, run `gui_post.py`
* It'll look something like below. There are additional instructions in the GUI, but here's where you'll select which variables you want to plot
 * **NOT ALL THE VARIABLES AVAILABLE WILL WORK WHEN PLOTTED. (I just need to filter out the things that are and aren't data. Worst thing that'll happen if you plot something you shouldn't is that the GUI will crash lol)
* Here's an example of inputs showing how to plot the surface wall temperatures on the left Y-axis, and Mach on the right, both vs. Time.
![alt text](https://github.com/elliottmckee/pyRATT/blob/main/images/gui_post_example.PNG?raw=true)
* Plot and Save whatever you want. The GUI will remain up to make as many plots until you close it.

You can also make your own postprocessing scripts and either use the .csv or load in the pickled .sim file (more data/functionality).




## Running without the GUI

An example script for running a standalone simulation, without the GUI, can be found here: `pyratt/nogui_run.py`. This example closely mirrors the nosecone example discussed previously (and below), and contains some additional commentary/information in the header.

The high-level flow for running a simulation is relatively straightforward, and looks something like:


```python
    # Define Wall Composition
    AeroSurf = WallStack(materials="ALU6061", thicknesses=0.02, node_counts = 15)

    # Point to Trajectory Data .csv
    Flight    = FlightProfile( "path/to/flighttrajectory.csv" )
    
    # Define Simulation Object
    MySimulation= Thermal_Sim_1D(...)

    #Run Simulation
    MySimulation.run()

    # Export
    # to .csv
    MySimulation.export_data_to_csv()
    # pickle
    with open("animtest_2material.sim", "wb") as f: pickle.dump(MySimulation, f)
```


While straightforward, there are a good few arguments and things you can/need to pass to WallStack and Therml_Sim_1D(). I reccomend checking out the examples provided first, and the docstrings for those objects themselves. 



## Code Examples

Example driver scripts can be found in the `pyratt/example_files` directory. The following examples are provided, and correspond with the above demos:

* `example_nosecone.py`: Nosecone heating Example.
* `example_fin.py`: Fin heating Example.
* `example_multi_component_nosecone.py` :  Nosecone example but highlights the syntax for defining walls with multiple componenents.




# Validation Cases

There are multiple validation cases that are included in the above repo, that can be found in `pyratt/validation_cases`.

To run these cases: from the main `pyratt/` directory, run `python3 validation_cases/example-name-here.py`

This is a section I am looking to expand upon more. If you know of any examples, either in literature, or if anyone has data from strapping thermocouples to their hilarously powerful HPR rocket, please do let me know. 


## Hifire-5: `pyratt/validation_cases/hifire_5.py`

The HiFire-5 [4] flight vehicle was a two-stage rocket with a nosecone that was instrumented with a ton of pressure, temperature, and heat flux sensors to measure transition at hypersonic conditions.

Unfortunately for this test, the second stage didn't light, causing the vehicle to only reach ~Mach 3. 

Comparison between the Wall surface temperatures from the flight data presented in [4] are plotted alongside the results generated by pyRATT for the geometry specified. 







## [5] Hifire-5B:  `pyratt/validation_cases/hifire_5b.py`

The HiFire-5B [5] flight vehicle was equivalent to that of the HiFire-5 vehicle, except for the 2nd stage did successfully light. 

Unfortunately, however, temperature data througout the entire flight trajecory is not presented in the paper. Instead, there is a short window in which temperature data is presented. 

However, this still serves as an interesting validation case, firstly, due to the very-high Mach numbers (high 7's), as well as the data highlighting the transition to turbulence. 





## [6] Semi-Infinite Wall Analytical Solutions:  `pyratt/validation_cases/transient_cond.py`

The thermal conduction model along was verified using the analytical solutions for the transient conduction in a semi-infinite plate presented by Incopera [6].

In order to simulate the semi-infinite plate, the wall was just made very long, relative to the timescales examined, which introduces some error into the below solutions. 






# References

[1] Uslu, Sitki & Simsek, Bugra. (2019). One-Dimensional Aerodynamic Heating and Ablation Prediction. Journal of Aerospace Engineering. 32. 10.1061/%28ASCE%29AS.1943-5525.0001042. https://www.researchgate.net/publication/332963290_One-Dimensional_Aerodynamic_Heating_and_Ablation_Prediction

[2] RASAero II Rocket Aerodynamic Analysis and Flight Simulation Software, Rogers Aeroscience, Copyright © 2019, by Charles E. Rogers. https://www.rasaero.com/

[3] Ambiance: https://pypi.org/project/ambiance/

[4] HIFiRE-5 Flight Test Results, Thomas J. Juliano, David Adamczak, and 
    Roger L. Kimmel, Journal of Spacecraft and Rockets 2015 52:3, 650-663

[5] Kimmel, Roger & Adamczak, David & Hartley, David & Alesi, Hans & Frost, Myles & Pietsch, Robert & Shannon, Jeremy & Silvester, Todd. (2017). HIFiRE-5b Flight Overview. 10.2514/6.2017-3131. https://www.researchgate.net/publication/318143977_HIFiRE-5b_Flight_Overview

[6] Incropera F. P. & DeWitt D. P. Fundamentals of heat and mass transfer (6th ed.). J. Wiley.

















