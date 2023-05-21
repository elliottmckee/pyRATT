"""
Contains all the tools, models, etc. for the convection and radiation 
portions of thermal heat transfer. 

"""
# Standard Modules
import numpy as np
from math import pow, sqrt, log10, isnan
from ambiance import Atmosphere

#Internal Modules
from . import constants
from . import tools_aero



class ExternalRadiationLoading:

    def __init__(self,  Flight=None, T_inf_rad=constants.T_RAD_AMB, incidentSolarFlux = 0.0, absorbtivity = 0.2):
        """
        Object that defines an external Radiation loading.

        Uses black-body radiation equation between the Node and an ambient radiative
        temperature to determine heat flux into or out of the Node

        If you specify a flight profile with the Flight argument, it will use the 
        freestream T_infinity for the ambient radiative temperature. Otherwise, will
        default to the value in constants.py, constants.T_RAD_AMB

        TODO:
            -Look into what should be used for this T_infinity (not super important though)
            - Check solar flux stuff and sign of energy
        """
        self.Flight                  = Flight
        self.T_inf_rad              = T_inf_rad
        self.incidentSolarFlux  = incidentSolarFlux
        self.absorbtivity       = absorbtivity


    def get_q_in(self, elem, **kwargs):
    
        if self.Flight:
            _, alt_inf = self.Flight.get_mach_alt(kwargs["time"])
            T_rad_inf = Atmosphere(alt_inf).temperature
        else:
            T_rad_inf = constants.T_RAD_AMB

        if self.incidentSolarFlux == 0.0:
            return black_body_radiation(elem.T, elem.emis, T_rad_inf)
        else:
            return ( black_body_radiation(elem.T, elem.emis, T_rad_inf ) + self.incidentSolarFlux*self.absorbtivity )



def black_body_radiation(T, emis, T_rad_inf):
    # Just the plain ole black body radiation equation. Nothing fancy here. 

    return constants.SB_CONST * emis * (T_rad_inf**4 - T**4)
    
        


# class SolarRadiationLoading:
#     """
#     Define a incident solarradiative heat flux, in W/m2, and material
#     absorbtivity.

#     For estimates on material absorbtivity, 
#     https://www.engineeringtoolbox.com/solar-radiation-absorbed-materials-d_1568.html
#     or theres a good nasa or actual paper with a bunch i'll link later
#     """

#     def __init__(self, solarIntensity, absorbtivity = .5):
#         self.sol_intensity = solarIntensity
#         self.sol_absorbtivity = absorbtivity

#         self.qdot_rad 

#     def get_q_in(self):
#         return self.qdot_rad

