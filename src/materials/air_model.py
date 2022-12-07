import numpy as np
import scipy
import pandas
import os

from math import pow


#### Air Model
class AirModel:
    def __init__(self):

        print("In AirModel, only using Lookup table for Cp. Currently using sutherland-type expressions for mu and k")
        
        
        self.R = 287.0 #[J/KgK] # Air Specific Gas Constant 
        self.gam = 1.4 #Ratio of Specific Heats


        self.lookup_table_csv = 'src/materials/air_pressure_indepent_properties.csv'
        self.initialize_lookups()


    def initialize_lookups(self):

        #Read .csv containing air properties
        df = pandas.read_csv(self.lookup_table_csv, usecols=['Temp', 'Cp (J/KgK)'])

        #Convert Pandas Dataframe Object to a Numpy Array
        df = df.to_numpy()

        # Create Scipy Interpolation Object
        self.Cp_interp = scipy.interpolate.interp1d(df[:,0], df[:,1], kind='linear')


    def specific_heat(self, T):
        return self.Cp_interp(T)


    def thermal_conductivity(self, T):
        # Using Thermal Conductivity Model Provided in Ambience Documentation
        # Appears similar to that used in 1976 Standard Atmosphere
        # Bertin Sutherland is Different
        return (2.648151e-3 * pow(T, 3.0/2.0)) / (T + (245.4 * pow(10, -12.0/T)))


    def dynamic_viscosity(self, T):
        # Sutherland Law 
        # Source: Bertin, Hypersonic Aerothermodynamics
        return (1.458e-6 * pow(T, 3.0/2.0)) / (T + 110.4)














