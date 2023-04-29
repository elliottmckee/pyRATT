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



class ConstantQdotLoading:
    def __init__(self, qDot):
        self.qDot = qDot

    def get_q_in(self, elem, time):
        return self.qDot




class ExternalRadiationLoading:

    def __init__(self,  Flight=None):
        """
        Object that defines an external Radiation loading.

        Uses black-body radiation equation between the Node and an ambient radiative
        temperature to determine heat flux into or out of the Node

        If you specify a flight profile with the Flight argument, it will use the 
        freestream T_infinity for the ambient radiative temperature. Otherwise, will
        default to the value in constants.py, constants.T_RAD_AMB

        TODO:
            -Look into what should be used for this T_infinity (not super important though)
        """
        self.Flight             = Flight
        

    def get_q_in(self, elem, time):
    
        if self.Flight:
            _, alt_inf = self.Flight.get_mach_alt(time)
            T_rad_inf = Atmosphere(alt_inf).temperature
        else:
            T_rad_inf = constants.T_RAD_AMB

        return self.black_body_radiation(self, elem.T, elem.emis, T_rad_inf)


    def black_body_radiation(self, T_node, emis_node, T_rad_inf):
        # Just the plain ole black body radiation equation. Nothing fancy here. 

        return constants.SB_CONST * emis_node * (T_rad_inf**4 - T_node**4)
    
        

