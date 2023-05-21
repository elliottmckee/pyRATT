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

    def get_q_in(self, elem, time, time_step):
        return self.qDot


class HeatTransCoeffLoading:
        def __init__(self):
            raise Exception("TODO")


