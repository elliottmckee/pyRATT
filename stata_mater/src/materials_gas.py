import numpy as np
import scipy
import pandas as pd
from pathlib import Path
from math import pow



class AirModel:
    """
    Class to represent the standard Air Model for use in a Simulation

    Attributes:
    ----------
    R : float
        Specific gas constant
    gam : float
        ratio of specific heats
    lookup_table_csv : str
        file path pointing to .csv containing cp, mu, k, etc. w/ temperature for air
    Cp_interp : scipy interp1d object 
        1D interpolation lookup object for interpolating Cp at a specific temperature. 
        Intended for use internally by specific_heat() below
    
    Methods:
    -------
    initialize_lookups(self):
        Used by __init__ to initialize the lookup table, scipy.interp1d objects
    specific_heat(self, T):
        returns the specific heat of air at temperature T [K]
    thermal_conductivity(self, T):
        returns the thermal conductivity of air at temperature T [K]
    dynamic_viscosity(self, T):
        returns the dynamic viscosity of air at temperature T [K]

    Notes: 
    -------
    -Only uses the .CSV lookup table for Cp. Using Sutherland expressions (Bertin) for mu and k

    """

    def __init__(self):
        
        self.R = 287.0 #[J/KgK] # Air Specific Gas Constant 
        self.gam = 1.4 #Ratio of Specific Heats

        self.lookup_table_csv = Path("resources", "air_pressure_indepent_properties.csv")
        self.initialize_lookups()


    def initialize_lookups(self):

        #Read .csv containing air properties
        df = pd.read_csv(self.lookup_table_csv, usecols=['Temp', 'Cp (J/KgK)'])

        #Convert Pandas Dataframe Object to a Numpy Array
        df = df.to_numpy()

        # Create Scipy Interpolation Object
        self.Cp_interp = scipy.interpolate.interp1d(df[:,0], df[:,1], kind='linear')


    def specific_heat(self, T):
        return self.Cp_interp(T)


    def thermal_conductivity(self, T):
        # Using Thermal Conductivity Model Provided in Ambience Documentation
        # Appears similar to that used in 1976 Standard Atmosphere
        # Bertin Sutherland is Different...?
        return (2.648151e-3 * pow(T, 3.0/2.0)) / (T + (245.4 * pow(10, -12.0/T)))


    def dynamic_viscosity(self, T):
        # Sutherland Law 
        # Source: Bertin, Hypersonic Aerothermodynamics
        return (1.458e-6 * pow(T, 3.0/2.0)) / (T + 110.4)














