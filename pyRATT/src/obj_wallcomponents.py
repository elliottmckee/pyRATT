from typing import Optional

from .materials_solid import MATERIALS_DICT
from .materials_ablative import ABLATIVE_DICT
#from . import conversions
#from . import constants

# ---------------------------------------------------------------------------
# This file contains the object definitions pertaining to any of the wall
# component representations
# ---------------------------------------------------------------------------


import numpy as np
import pandas as pd
import scipy
from math import isnan
import copy


class WallStack: 
    """
    Computational representation of a wall stack, which is the combined stack of all wall materials that makes up the 
    through-wall direction of an Aerosurface. This wall is discretized into a number of computational nodes, which
    are used to solve for the 1D transient heat transfer
    
    A Wall stack is just the materials sandwiched together to form a wall. It can be a single material, or many,
    but is defined by the individual materials and their thicknesses.

    A wall stack is split up into components. These components are then split up into elements/nodes, which
    are used to perform the finite difference calculations.
    
    Inputs
    ----------
        materials: str list or str, List of strings containing the names (see materials_solid.py) of the 
                    components that make up the wall
    
        thicknesses: float list or float, List that defines how thick each of the components is
    
        node_counts: int list or int, list that defines how many nodes each component is divided into

    *The above inputs all must be in corresponding order, and be of equal length*
            

    
    Attributes
    ----------
        materials: str or str list of Wall material names
        thicknesses: float or float list of wall component thicknesses
        node_counts = int or int list of the number of nodes in each wall componenet
        elements: list of SolidElement objects  
            contains the material properties at node 
        n_tot: int    
            total number of elements
        y_loc: float list   
            list of through-wall node/element coordinate values 
        interface_resistances:
            not yet implemented
    
    Methods
    -------
    -

    Notes
    -------
    -
    """

    def __init__(self, materials, thicknesses, element_counts, interface_resistances: Optional[float] = None):



        if interface_resistances is not None:
            raise NotImplementedError("I have not implemented this yet")


        # handling both list and single values for the above entries (convert everything to a list if isnt already)
        if not isinstance(materials, list): 
            materials = [materials]
        if not isinstance(thicknesses, list): 
            thicknesses = [thicknesses]
        if not isinstance(element_counts, list): 
            element_counts = [element_counts]



        # Maintain the User Specified inputs
        self.materials = materials
        self.num_components = len(self.materials)

        self.thicknesses = thicknesses
        self.element_thicknesses = [ thicknesses[i]/element_counts[i] for i in range(len(materials))]
        
        self.element_counts = element_counts
        self.interface_resistances = interface_resistances

        # Get total number of elements
        self.elem_tot = sum(element_counts)



        # List of Elements, which represents the entire Wall/Stack/Aerosurface
        self.elements = [] 
        

        #For each of the wall components
        for i in range(self.num_components):

            # #Get Local Coordinate Vector
            # y_local = [ round(j*self.element_thicknesses[i] + self.element_thicknesses[i]/2.0, 8) for j in range(self.element_counts[i])]

            # #If First component, you're good
            # if i == 0:
            #     self.y_coords = self.y_coords + y_local
            # # If not, you have to account for previous wall amounts
            # else:
            #     y_global =  [round(y + self.y_coords[-1] + self.element_thicknesses[i-1]/2.0, 8) for y in y_local]
            #     self.y_coords = self.y_coords + y_global
            
            
            #For the number of nodes for a given component
            for j in range(element_counts[i]):
                

                if materials[i] in MATERIALS_DICT.keys():
                    self.elements.append( SolidElement(materials[i], self.element_thicknesses[i]) )

                if materials[i] in ABLATIVE_DICT.keys():
                    self.elements.append( AblativeElement(materials[i], self.element_thicknesses[i]) )


        self.update_wall_coords()



    def update_wall_coords(self):

        self.y_coords = []
        prev_dy = -1.0

        #For each of the wall components
        for i, el in enumerate(self.elements):

            #If first Element, put node at half thickness
            if prev_dy == -1.0:
                self.y_coords.append( round(el.dy/2.0, 8) )
                #Update Previous Element length
                prev_dy = el.dy 

            #If no change in element thickness, 
            elif el.dy == prev_dy:
                self.y_coords.append( round(self.y_coords[-1] + el.dy, 8))

            # If there is a change in element thickness
            elif el.dy != prev_dy:
                self.y_coords.append( round(self.y_coords[-1] + el.dy/2 + self.elements[i-1].dy/2.0, 8) )

                #Update Previous Element Length
                prev_dy = el.dy


            

            # #Get Local Coordinate Vector
            # y_local = [ round(j*self.element_thicknesses[i] + self.element_thicknesses[i]/2.0, 8) for j in range(self.element_counts[i])]

            # #If First component, you're good
            # if i == 0:
            #     self.y_coords = self.y_coords + y_local
            # # If not, you have to account for previous wall amounts
            # else:
            #     y_global =  [round(y + self.y_coords[-1] + self.element_thicknesses[i-1]/2.0, 8) for y in y_local]
            #     self.y_coords = self.y_coords + y_global
            



    def update_thermal_props(self, T_vec):

        for i, el in enumerate(self.elements):

            if el.type == "ablative":
                el.update_thermal_props(T_vec[i])


    def update_thicknesses(self, delta_recess):

        # Get number of Elements that are Ablative
        ablative_el_count = 0
        for el in self.elements:
            if el.type == "ablative":
                ablative_el_count += 1

        #Calculate Change in Element thickness. Just distribute recession equally across element
        delta_dy = delta_recess / ablative_el_count

        for el in self.elements:
            el.dy = el.dy-delta_dy



    def get_densities(self):
        """ Returns a list of element densities (for monitoring ablative densities)"""
        rho = []

        for el in self.elements:
            rho.append(el.rho)

        return rho


    



    def get_ablative_thickness(self):

        thickness = 0.0

        for el in self.elements:

            if el.type == "ablative":
                thickness += el.dy

        return thickness


                

                





class SolidElement:
    """
    Computational representation of a  single, solid, non-ablating wall element, 
    for use in thermal conduction finite difference calculations

    Attributes
    ----------
    rho : float   
        material density [kg/m^3]
    cp : float  
        material specific heat at constant pressure [J/KgC]
    k : float     
        material thermal conductivity [W/mK]
    emis: float   
        material Black Body Emissivity Coefficient 

    dy : float   
        element thickness (in the through-wall direction) [m]
    y : float   
        node coordinate (in the through-wall direction) [m]
    
    Methods
    -------

    Notes
    -------
    """

    def __init__(self, material, dy):

        self.type = 'solid'

        # Pull material properties from Solid Material Database
        self.rho    = MATERIALS_DICT[material]["rho"]
        self.cp     = MATERIALS_DICT[material]["cp"]
        self.k      = MATERIALS_DICT[material]["k"]
        self.emis   = MATERIALS_DICT[material]["emis"]

        self.dy = dy








class AblativeElement:

    def __init__(self, material, dy):

            # Type Flag
            self.type = 'ablative'

            #Initialize Functions for Returning Cp, k, Qstar (handles Lookup tables and constants)
            for prop in ['cp', 'k', 'Qstar']:
            

                # Assuming that if this entry is a string, it is pointing to a lookup table
                if isinstance(ABLATIVE_DICT[material][prop], str):


                    # Read Lookup Table
                    df = pd.read_csv(ABLATIVE_DICT[material][prop], skiprows=1, names=["input", "value"])
                    

                    # Assign Scipy Interp object to attribute. Current Behavior is to Clip values
                    setattr(self, prop+"_lookup", scipy.interpolate.interp1d(df["input"], df["value"], fill_value=(df.iloc[0]["value"], df.iloc[-1]["value"]), bounds_error=False, kind='linear'))
                    

                else:
                    #This just returns the constant Cp Value
                    setattr(self, prop+"_lookup", lambda T : ABLATIVE_DICT[material][prop] )


            # Resin Fraction
            self.resin_frac = ABLATIVE_DICT[material]["resin_frac"]

            # Total Density
            self.rho    = ABLATIVE_DICT[material]["initial_total_density"]

            # Initialize Component Densities to Virgin Values
            self.rho_comp = np.copy(ABLATIVE_DICT[material]['virgin_component_densities'])
            
            # Thermal Properties
            self.emis   = ABLATIVE_DICT[material]['emis']

            self.cp     = self.cp_lookup(290.0)
            self.k      = self.k_lookup(290.0)

            # Element Thickness
            self.dy = dy


            # Additional Properties
            self.num_arr_components = ABLATIVE_DICT[material]['num_arr_components']
            
            self.virgin_component_densities = ABLATIVE_DICT[material]['virgin_component_densities']
            self.char_component_densities = ABLATIVE_DICT[material]['char_component_densities']

            self.arr_B = ABLATIVE_DICT[material]['arr_B']
            self.arr_ER = ABLATIVE_DICT[material]['arr_ER']
            self.arr_N = ABLATIVE_DICT[material]['arr_N']


            self.ablation_temp_threshold = ABLATIVE_DICT[material]['abl_temp_threshold']



    def update_thermal_props(self, temp):
        """ This updates the materials properties, Cp, K , etc. """
        self.cp = self.cp_lookup(temp)
        self.k = self.k_lookup(temp)


    def update_Qstar(self, q):
        self.Qstar = self.Qstar_lookup(q)




    def arrhenious_decomp(self, T, dt):

        dRho_dt_comp = np.zeros((self.num_arr_components,1))

        # For Each Arrhenious Reaction Component
        for j in range(self.num_arr_components):

            #Calculate Change in Component Density
            dRho_dt_comp[j] = (-self.arr_B[j] * np.exp(-self.arr_ER[j] / T) * self.virgin_component_densities[j])  \
                              * (((self.rho_comp[j]-self.char_component_densities[j]) / self.virgin_component_densities[j]) ** self.arr_N[j])

                
        # Total Contribution to Total Density Change
        dRho_tot = self.resin_frac*(dRho_dt_comp[0] + dRho_dt_comp[1]) + (1.0-self.resin_frac)*dRho_dt_comp[2]


        # Update Densities
        self.rho_comp[0] = self.rho_comp[0] + dRho_dt_comp[0] * dt
        self.rho_comp[1] = self.rho_comp[1] + dRho_dt_comp[1] * dt
        self.rho_comp[2] = self.rho_comp[2] + dRho_dt_comp[2] * dt

        self.rho         = self.rho + dRho_tot * dt
        

        #Sum density change*cell volume across all elements. ASSUMES UNIT AREA
        mDot_g = -sum(dRho_tot * 1.0 * self.dy)

        return mDot_g, dRho_dt_comp








# class AblativeComponent:
#     """
#     Computational representation of a section representing an Ablative Wall

#     Attributes
#     ----------
    
#     Methods
#     -------

#     Notes
#     -------
#     """

#     def __init__(self, material, component_thickness, n_elements, temp_init):

#         self.thickness = component_thickness
#         self.n_elements = n_elements

#         # Pull all ABLATIVE_DICT entry properties in
#         for key in ABLATIVE_DICT[material]:
#             setattr(self, key, ABLATIVE_DICT[material][key])


#         #Initialize Functions for Returning Cp, k, Qstar (handles Lookup tables and constants)
#         for prop in ['cp', 'k', 'Qstar']:
        
#             # Assuming that if this entry is a string, it is pointing to a lookup table
#             if isinstance(ABLATIVE_DICT[material][prop], str):
                
#                 # Read Lookup Table
#                 df = pd.read_csv(ABLATIVE_DICT[material][prop], skiprows=1, names=["input", "value"])
                
#                 # Assign Scipy Interp object to attribute. Current Behavior is to Clip values
#                 setattr(self, prop, scipy.interpolate.interp1d(df["input"], df["value"], fill_value=(df.iloc[0]["value"], df.iloc[-1]["value"]), bounds_error=False, kind='linear'))

#         else:
#             #This just returns the constant Cp Value
#             setattr(self, prop, lambda T : ABLATIVE_DICT[material][prop] )


#         # Calculate element thicknesses
#         self.elem_thicknesses = component_thickness/n_elements

#         # Initialize List of Elements
#         self.elements = []


#         for i in range(n_elements):
#             self.elements.append( AblativeElement( material, self.cp(temp_init), self.k(temp_init), self.elem_thicknesses) )


        


#     def initialize_temps(self, T_init):
#         #Initialize Temperature Vector
#         self.T_vec = T_init * np.ones((len(self.elements), 1))



#     def update_thermal_props(self, temp):
#         """ This updates the materials properties, Cp, K , etc. """
        
#         for elem in self.elements:

#             elem.cp = self.cp(temp)
#             elem.k = self.k(temp)



#     def arrhenious_decomp(self):

#         # Gross Conversion that Pulls properties out from AblativeElement Object
#         temp = []
#         for elem in self.elements:
#             temp.append(elem.rho_comp)
#         np_component_densities = np.array(temp)


#         # Gonna Try and use numpy arrays here instead of just double-looping
#             # Need change, at each node (first index) of each component (2nd index)
#         dRho_dt_comp = np.zeros(( self.n_elements, self.num_components))

#         # For Each Arrhenious Reaction Component
#         for j in range(self.num_components):

#             #Calculate Change in Density
#             dRho_dt_comp[:, j] = (-self.arr_B[j] * np.exp(-self.arr_ER[j] / self.T_vec.T) * self.virgin_component_densities[j])  \
#                               * (((np_component_densities[:,j]-self.char_component_densities[j]) / self.virgin_component_densities[j]) ** self.arr_N[j])

                
#         # Total Contribution to Total Density Change
#         self.dRho_tot = self.resin_frac*(dRho_dt_comp[:,0] + dRho_dt_comp[:,1]) + (1.0-self.resin_frac)*dRho_dt_comp[:,2];

#         #Sum density change*cell volume across all elements. ASSUMES UNIT AREA
#         self.mDot_g = -sum(dRho_tot * 1.0 * self.elem_thicknesses)

        
#         # Update Ablative Thickness
#         #Abl.deltaVec(1,i+1) = Abl.deltaVec(i) + Abl.sDotVec(i) * dt;
#         # Update Ablative Densities
#         # Abl.rhoVec_tot(:,i+1) = Abl.rhoVec_tot(:,i) + dRho*dt ;
#         # Abl.rhoVec_comp(:,i+1,:) = squeeze(Abl.rhoVec_comp(:,i,:)) + dRho_comp*dt;





