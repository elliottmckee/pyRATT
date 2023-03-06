# Python Rocket AeroThermal Toolbox

PyRATT is an Aero/Thermal Analysis tool aimed at *very* high performance (or high-speed) amateur rockets, or for performing more general 1D Transient Thermal analyses.

Primarily, it performs coupled Aerothermal/Thermal simulations of the temperature response of structural components like nosecone walls and fins, given a flight profile material properties, geometric parameters, etc. This functionality aims to be as approachable and easy-to-use as possible, with GUIs both for running simulations, as well as plotting results. Even without the GUI's, running from a standalone script is only a handful of lines of code (see below).

Secondarily, it aims to be a more general tool for analyzing more general, 1D transient thermal behavior, with a ton of flexibility in being able to handle varied/mixed wall material types, wall thermal boundary conditions etc. 


#  Notices
This is currently in what I am humbly going to call a "Pre-Release" state. There are definitely still issues (specifically with the GUI's being a bit finicky and not fully polished by any means), but I want to get it out here to gauge interest to see how much I should be developing this for others vs. just myself.

Please do let me know if you run into any issues with any part of it, or have any questions. This helps me know what to fix, where to add additional information, etc. 


# Demonstrations

Some examples of the results of the flight-thermal-simulation functionality of the code are shown below. 

These example files used to generate these simulations can be found in `pyratt/example_files/`. Instructions on how to run them can be found below. 




## Nosecone Heating

`pyratt/example_files/example_nosecone.py`

This is a 1D Transient Thermal/Aerothermal simulation of a nosecone along a flight trajectory simulated by RASAeroII [1] of 2-stage rocket, using a M2245 to M1378 to get to just below Mach 5.  

A location/station 20 cm downstream of the nosecone tip was analyzed, using the following geometric properties:
 - Wall Thickness: 1.0 cm
 - Wall Material: 316 Stainless
 
 The first figure shows an animation of the through-wall temperature distribution in the through-wall direction, throughout flight, in real-time. 
 
 The second figure shows the hot-wall and cold-wall temperatures seen throughout the flight. 


![alt text](https://github.com/elliottmckee/stata_mater/blob/main/images/example_nosecone_SS.gif?raw=true)  |  ![alt text](https://github.com/elliottmckee/stata_mater/blob/main/images/example_nosecone_SS.jpg?raw=true)
:-------------------------:|:-------------------------:




##  Fin Heating


![alt text](https://github.com/elliottmckee/stata_mater/blob/main/images/example_fin_SS.gif?raw=true) | ![alt text](https://github.com/elliottmckee/stata_mater/blob/main/images/example_fin_SS.jpg?raw=true)
:-------------------------:|:-------------------------:


## Multi-Component Nosecone Heating

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




















