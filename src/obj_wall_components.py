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

    def __init__(self, SolidWallComponent):

        self.dy = SolidWallComponent.el_thickness
        self.rho = SolidWallComponent.rho
        self.cp = SolidWallComponent.cp
        self.k = SolidWallComponent.k

        #Leaving this in cuz maybe some materials we won't know the emissivity of, and you only need it for the surface element
        if hasattr(SolidWallComponent, 'emis'):
            self.emis = SolidWallComponent.emis
        else:
            raise Exception("Wall Component does not have a Emissivity value")



class AerosurfaceStack: 
    """
    Class to represent an "Aerosurface Stack," which is the combined stack of all wall materials that makes up the 
    through-wall direction of an Aerosurface. 
    # EX: Cork->RTV->Alu
    
    Example
    ----------
    SingleComponentSolidAerosurf = AerosurfaceStack(wall_components = [AluminumSolidWallComponent], surface_type = "nosecone", interface_resistances = None)

    Attributes
    ----------
    wall_components : list of Wall Component Objects  
        list of each of the wall material components that make up the aerosurface
    surface_type : str   
        defines what type of aerosurface this is (nosecone, fins, leading edge, etc)
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

    def __init__(self, wall_components, surface_type, interface_resistances: Optional[float] = None):

        if interface_resistances is not None:
            raise NotImplementedError("I have not implemented this yet")

        if surface_type != "nosecone":
            raise NotImplementedError("Only type: 'nosecone' has been implmented")


        self.wall_components = wall_components
        self.surface_type = surface_type

        # Create List of Elements, which represents the entire Wall/Stack/Aerosurface
        self.elements = []
        
        #For the wall components
        for i in range(len(self.wall_components)):
            #For the number of elements in each wall section
            for j in range(self.wall_components[i].n_nod):

                #Append new element as specified by wall_component[i]
                self.elements.append( SolidElement(self.wall_components[i]) )

        #Get total number of elements
        self.n_tot = len(self.elements)
            
        #y node/element coordinate (through-wall) values array
        self.y_loc = []

        #Append new element to y_location vector, by adding an element thickness to the previous value
        for e in self.elements:
            if self.y_loc:
                self.y_loc.append( self.y_loc[-1] + e.dy)
            else:
                self.y_loc.append(0.0)





