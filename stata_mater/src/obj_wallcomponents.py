from typing import Optional

from .materials_solid import MATERIALS_DICT
#from . import conversions
#from . import constants

# ---------------------------------------------------------------------------
# This file contains the object definitions pertaining to any of the wall
# component representations
# ---------------------------------------------------------------------------



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

    def __init__(self, materials, thicknesses, node_counts, interface_resistances: Optional[float] = None):



        if interface_resistances is not None:
            raise NotImplementedError("I have not implemented this yet")


        # handling both list and single values for the above entries (convert everything to a list if isnt already)
        if not isinstance(materials, list): 
            materials = [materials]
        if not isinstance(thicknesses, list): 
            thicknesses = [thicknesses]
        if not isinstance(node_counts, list): 
            node_counts = [node_counts]


        # Maintain the User Specified inputs
        self.materials = materials
        self.thicknesses = thicknesses
        self.node_counts = node_counts
        self.interface_resistances = interface_resistances

        # Get total number of elements
        self.n_tot = sum(list(node_counts))

        # List of Elements, which represents the entire Wall/Stack/Aerosurface
        self.elements = [] 
        
        #For each of the wall components
        for i in range(len(materials)):

            #Calculate Element Thickness            
            dy_e = thicknesses[i]/(node_counts[i]-1)

            #For the number of nodes for a given component
            for j in range(node_counts[i]):

                #Update y location to feed into element
                if not self.elements: #If List is currently empty
                    y_e = 0.0
                else: #Increment based on previous y value
                    y_e = self.elements[-1].y + dy_e
                

                #Append computational node/element corresponding to that material
                self.elements.append( SolidElement(materials[i], y_e, dy_e) )



    def get_wall_coords(self):
        """Function for pulling out a list of the wall cooordinates 
        
        TODO: I should probably put this in the init() of WallStack...
        """
        out = []
        for i, el in enumerate(self.elements):
            out.append(el.y)
        return out

                





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

    def __init__(self, material, y, dy):

        # Pull material properties from Solid Material Database
        self.rho    = MATERIALS_DICT[material]["rho"]
        self.cp     = MATERIALS_DICT[material]["cp"]
        self.k      = MATERIALS_DICT[material]["k"]
        self.emis   = MATERIALS_DICT[material]["emis"]

        # Element Coord
        self.y = y
        # Element Thickness
        self.dy = dy

