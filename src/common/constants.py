"""
For the definition of any hard-coded constants to be used througout a Simulation

For usage, see simulation_objects.py

Where it makes sense, make sure constants have sources. 
"""


#Stefan-Boltzman Constant 
SB_CONST = 5.6704e-8 #[W/(m^2*K^4)]

#Ambient Radiative Temperature
T_RAD_AMB = 290.0 #[K]

#Mach Number Coefficient for BL Transition Criteria (see Ulsu-Simsek) 
C_M = 0.2
# Used for the calculation of when the BL is Laminar/Turbulent.
# Reccomended (ULSU): USE 0.2 FOR FUSELAGE AND NO SWEEP WING, USE 0.1 FOR SWEPT WING.
    # Fuselage/No Sweep Wing: 0.2
    # Swept Wing: 0.1
# Coefficients/correlations like these, especially for this use case of predicting transition, are
# extrodinarily coarse, and results should be interpreted with that in mind.








