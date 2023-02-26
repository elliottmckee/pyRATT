"""
Contains definitions of any hard-coded conversion factors, constants that are used

Name and usage for Conversions should be of the form:
var_in_meters = var_in_feet * constants.FT2M 

Notes:
    -Where it makes sense, try and add sources for #tracability 
"""

#---------------------------------------------------------------------------------------------------#
#       CONVERSIONS
#---------------------------------------------------------------------------------------------------#
#Feet to Meters
FT2M = 0.3048

#Degrees to Radians
DEG2RAD = 0.01745329251



#---------------------------------------------------------------------------------------------------#
#       CONSTANTS
#---------------------------------------------------------------------------------------------------#
#Stefan-Boltzman Constant 
SB_CONST = 5.6704e-8 #[W/(m^2*K^4)]

#Ambient Radiative Temperature
T_RAD_AMB = 290.0 #[K]

#Mach Number Coefficient for BL Transition Criteria (see Ulsu-Simsek) 
C_M = 0.2
# Used for the calculation of when the BL is Laminar/Turbulent.
# Reccomended (Ulsu, Ref [1]): USE 0.2 FOR FUSELAGE AND NO SWEEP WING, USE 0.1 FOR SWEPT WING.
    # Fuselage/No Sweep Wing: 0.2
    # Swept Wing: 0.1

