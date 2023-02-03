#Contains object definitions for anything relating to the representation of the wall or its components


from typing import Optional

from .materials_solid import solidMaterialDatabase
#from . import conversions
#from . import constants


class SolidWallComponent:
    """
    Class to represent a Solid, non-ablating wall component or layer.

    
    Example
    ----------
    AluminumWall = SolidWallComponent(material = "ALU6061", tot_thickness = 0.0025, n_nodes = 9, emis_override = None)
    
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
    tot_thickness : float
        total component or layer thickness
    el_thickness : float
        thickness of each individual element
    n_nod : int
        number of discrete computational elements that a wall component is split into

    Methods
    -------

    Notes
    -------
    -
    """

    def __init__(self, material, tot_thickness: float, n_nodes: int, emis_override: Optional[float] = None):
        
        #Get, assign material properties
        self.rho, self.cp, self.k, self.emis = solidMaterialDatabase(material)

        self.tot_thickness = tot_thickness
        self.n_nod = n_nodes

        self.el_thickness = tot_thickness / (n_nodes-1)

    
class SolidElement:
    """
    Class to represent a Solid, non-ablating wall element, for use in thermal conduction finite difference calculations

    Attributes
    ----------
    dy : float   
        element thickness (in the through-wall direction) [m]
    rho : float   
        material density [kg/m^3]
    cp : float  
        material specific heat at constant pressure [J/KgC]
    k : float     
        material thermal conductivity [W/mK]
    emis: float   
        material Black Body Emissivity Coefficient 
    
    Methods
    -------

    Notes
    -------
    -
    """

    def __init__(self, material, dy):


        # Pull material properties from Solid Material Database
        self.rho, self.cp, self.k, self.emis = solidMaterialDatabase(material)

        # Element Thickness
        self.dy = dy

        


        #Leaving this in cuz maybe some materials we won't know the emissivity of, and you only need it for the surface element
        # if hasattr(SolidWallComponent, 'emis'):
        #     self.emis = SolidWallComponent.emis
        # else:
        #     raise Exception("Wall Component does not have a Emissivity value")



class WallStack: 
    """
    Class to create the computational representation of a wall stack, which is the combined stack of all wall materials that makes up the 
    through-wall direction of an Aerosurface. 
    # EX: Cork->RTV->Alu
    
    Example
    ----------
    

    Attributes
    ----------
    wall_components : str list of Wall Component Objects  
        list of each of the wall material names that make up the wall
    elements : float  
        ordered list containing wall element objects (different than components) that form the numerical representation of the 1D wall/aerosurface
    n_tot : int    
        total number of elements
    y_loc: float list   
        list of through-wall node/element coordinate values 
    
    Methods
    -------

    Notes
    -------
    -
    """

    def __init__(self, materials, thicknesses, node_counts, interface_resistances: Optional[float] = None):

        # Future Notes
        if interface_resistances is not None:
            raise NotImplementedError("I have not implemented this yet")



        #Maintain the User Specified inputs
        self.materials = materials
        self.thicknesses = thicknesses
        self.node_counts = node_counts
        self.interface_resistances = interface_resistances

        #Get total number of elements
        self.n_tot = sum(node_counts)


        # Initializing Lists to Append to 
        self.elements = [] # List of Elements, which represents the entire Wall/Stack/Aerosurface
        self.y_loc = [] # y, or through-wall coordinates
        

        #For each of the wall components
        for i in range(len(materials)):

            #Create a computational element corresponding to that material
            dy_e = thicknesses[i]/(node_counts[i]-1)
            element = SolidElement(materials[i], dy_e)

            #Replicate for however many elements specified
            for j in range(node_counts[i]):
                self.elements.append(element)

                #Append new element to y_location vector, by adding an element thickness to the previous value
                if self.y_loc: #If y_loc isn't empty, increase previous value
                    self.y_loc.append( self.y_loc[-1] + dy_e)
                else: #If it is, its the first value (setting as 0.0)
                    self.y_loc.append(0.0)





