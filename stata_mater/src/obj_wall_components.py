#Contains object definitions for anything relating to the representation of the wall or its components


from typing import Optional

from .materials_solid import solidMaterialDatabase
#from . import conversions
#from . import constants



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
        print("In WallSurf- node/elememnt ambiguity may cause issues at interfaces when different sized wall elements, for y coord calculation")

        if interface_resistances is not None:
            raise NotImplementedError("I have not implemented this yet")

        # Handling List and Singular Values for the above entries
        if not isinstance(materials, list): 
            materials = [materials]
        if not isinstance(thicknesses, list): 
            thicknesses = [thicknesses]
        if not isinstance(node_counts, list): 
            node_counts = [node_counts]


        #Maintain the User Specified inputs
        self.materials = materials
        self.thicknesses = thicknesses
        self.node_counts = node_counts
        self.interface_resistances = interface_resistances

        #Get total number of elements
        self.n_tot = sum(list(node_counts))

        # List of Elements, which represents the entire Wall/Stack/Aerosurface
        self.elements = [] 
        
        #For each of the wall components
        for i in range(len(materials)):

            #Calculate Element Thickness            
            dy_e = thicknesses[i]/(node_counts[i]-1)

            #For the number of elements
            for j in range(node_counts[i]):

                #Update y location to feed into element
                if not self.elements: #If List is empty
                    y_e = 0.0
                else: #Increment based on previous y value
                    y_e = self.elements[-1].y + dy_e
                

                #Create a computational element corresponding to that material, append
                self.elements.append( SolidElement(materials[i], y_e, dy_e) )



    def get_wall_coords(self):
        
        out = []
        for i, el in enumerate(self.elements):
            out.append(el.y)

        return out

                





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

    def __init__(self, material, y, dy):

        # Pull material properties from Solid Material Database
        self.rho, self.cp, self.k, self.emis = solidMaterialDatabase(material)
        # Element Coord
        self.y = y
        # Element Thickness
        self.dy = dy

