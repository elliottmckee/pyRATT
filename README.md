# stata-mater
The protectress against damage by fire... 
https://en.wikipedia.org/wiki/Stata_Mater
(Don't think this name is final- more of a codeword)



# Background
Aerothermal analysis, characterization for high-performance amateur rockets. 

This aims to be a follow-on analysis to trajectory analysis for high-performance amateur rockets; as in, ones that go fast enough for aerothermal heating to do more than just char the paint off the leading edges...

The scope here is definitely somewhat flexible, but basically, I want this to be singular tool that can perform any/all aerothermal analysis you would want to perform short of full (FEM?)+CFD. So things like:

Transient Aero/thermal Analysis across a given rocket trajectory for:
- Environment Characterization (Stagnation+Recovery Temps vs. time)
- 1D (for now) Conduction in the through-wall direction for "standard" materials (metals, isotropic)
  - Nosecones
  - Fins
- Ablative Modelling, TPS sizing
- Lumped Capacitance Modelling of Structures (metals, fins/nosecone tips?) 

This is a Python-rework and hopefully expansion of this previous work: https://github.com/elliottmckee/1DThermal-Ablation



# Usage
This leverages a flight trajectory as simulated by your favorite rocket flight simulation software (RASAero, ~~RockSim, or if you're a real masochist, OpenRocket~~). 

Using both the .CDX1, ~~.ork, or .rkt~~ file, along with the exported flight simulation data, with a few additional user inputs to fully define the geometry and the simulation parameters, certain modules will be ran to perform the desired aerothermal analysis, plot things, and save the data so it can be manipulated with later. 




# Coding Emphases 

-**Modularity**

-Ease of Use

-Reccomended values set as Default- User inputs required, or over-writes as desired

-Readability

-Expandability

-Efficiency, hopefully




















