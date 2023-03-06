# pyRATT - python Rocket AeroThermal Toolbox

pyRATT is an Aero/Thermal Analysis tool aimed at *very* high performance (or high-speed) amateur rockets, or for performing more general 1D Transient Thermal analyses.

Primarily, it performs coupled Aerothermal/Thermal simulations of the temperature response of structural components like nosecone walls and fins, given a flight profile, material properties, geometric parameters, etc. This functionality aims to be as approachable and easy-to-use as possible, with GUIs both for running simulations, as well as plotting results. Even without the GUI's, running from a standalone script is only a handful of lines of code (see below).

Secondarily, it aims to be a more general tool for analyzing more general, 1D transient thermal behavior, with a ton of flexibility in being able to handle varied/mixed wall material types, wall thermal boundary conditions etc. 


#  Notices
This is currently in what I am humbly going to call a "Pre-Release" state. There are definitely still issues (specifically with the GUI's being a bit finicky and not fully polished by any means), but I want to get it out here to gauge interest to see how much I should be developing this for others vs. just myself.

Please do let me know if you run into any issues with any part of it, or have any questions. This helps me know what to fix, where to add additional information, etc. 


# Demonstrations

Some examples of the results of the flight-thermal-simulation functionality of the code are shown below. 

These example files used to generate these simulations can be found in `pyratt/example_files/`. Instructions on how to run them can be found below. 




## Nosecone Heating: `pyratt/example_files/example_nosecone.py`

This is a 1D Transient Thermal/Aerothermal simulation of a nosecone along a flight trajectory simulated by RASAeroII [1] of 2-stage rocket, using a M2245 to M1378 to get to just below Mach 5 (trajectory shown in the figure below).

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









# Core Functionality


# Planned Functionality









# Quickstart Guide

# Installation/Requirements

This requires 




## Running with the GUI

## Running without the GUI

## Code Examples





# Validation Cases






# References

Ambiance

ULSU

HiFire




















