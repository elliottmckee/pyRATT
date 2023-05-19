from typing import Optional

from .materials_solid import MATERIALS_DICT
from .materials_ablative import ABLATIVE_DICT


# ---------------------------------------------------------------------------
# This file contains the object definitions pertaining to any of the wall
# component representations
# ---------------------------------------------------------------------------

import numpy as np
import pandas as pd
import scipy
import networkx as nx
import matplotlib.pyplot as plt

from math import isnan


class ThermalNode:
    """
    The fundamental data structure in this architecture.

    Self-contained structure for maintaining the material/thermal properties:
        - rho: density
        - cp: Specific heat
        - k: thermal conductivity
        - emis: Black body emissivity
        - mass: total mass of the node
    as well the instantaneous state of the node:
        - T: temperature 

    TODO:
        - Properties that vary with temperature
    """

    def  __init__(self, material, mass = None, volume = None, area = 1.0, component_tag="DefaultComponent"):

        # Tags, Identifiers
        self.type = 'non-ablative'
        self.component_tag = component_tag

        # Pull material properties from Solid Material Database
        self.rho    = MATERIALS_DICT[material]["rho"]
        self.cp     = MATERIALS_DICT[material]["cp"]
        self.k      = MATERIALS_DICT[material]["k"]
        
        try:
            self.emis   = MATERIALS_DICT[material]["emis"]
        except KeyError:
            print(f"No Emissivity Entry found for {material}. Ignoring. ")

        # Get element mass, allow for specification by mass or volume
        if mass and volume:
            raise Exception("Please Specify mass OR volume, not both")
        elif mass and not volume:
            self.mass = mass
        elif volume and not mass:
            self.mass = volume * self.rho


        self.area = area
        self.dy = self.mass / self.rho / area


    def initialize_state(self, inital_temperature):
        self.T = inital_temperature


    


class AblativeThermalNode(ThermalNode):
    """
    Placeholder for definining an Ablative Node that extends the above 
    """
    pass





class ThermalNetwork():
    """
    Object that contains the Thermal Network
    graph representation,
    """
    def  __init__(self):
        # Initialize Empty Graph List
        self.Graph = nx.Graph()
        #Initialize Component Dictionary Object 
        self.ComponentDict = {}


    def addNodeToComponentList(self, NodeID, component_tag):
        # Add Node To Component List
        # If list exists in dictionary, append
        # If doesn't, create new dictionary entry
        if component_tag in self.ComponentDict.keys():
            self.ComponentDict[component_tag].append(NodeID)
        else:
            self.ComponentDict[component_tag] = [NodeID]


    def addGraphNode(self, ThermalNode):
        # Indexing by number currently. 
        # Since objects are hashable, can use the objects themselves as the nodes 
        # but this feels more intuitive        
        nodeID = self.Graph.number_of_nodes() 

        #Initialize Nodes and Attributes
        self.Graph.add_node( nodeID )
        self.Graph.nodes[nodeID]['element'] = ThermalNode
        self.Graph.nodes[nodeID]['thermal_loadings'] = [] 
        self.Graph.nodes[nodeID]['temp_constraint'] = None

        self.addNodeToComponentList(nodeID, ThermalNode.component_tag)
        
        return nodeID


    def addComponent_1D(self, material, total_thickness, n_nodes, surf_area = 1.0, component_tag = "DefaultComponent"):
        # Get element 
        # TODO: Assumes unit surface area
        element_volume = surf_area * total_thickness / n_nodes

        for i in range(n_nodes):
            
            # Nodes
            nodeID = self.addGraphNode( ThermalNode(material, volume = element_volume, component_tag=component_tag) )

            #Edges
            if i > 0: self.Graph.add_edge(nodeID, nodeID-1)



    def addComponent_0D(self, material, mass, component_tag="DefaultComponent"):
        self.addGraphNode( ThermalNode(component_tag, material, mass=mass, component_tag=component_tag) )


    def add_thermal_loading(self, nodeID, ThermLoading):
        self.Graph.nodes[nodeID]["thermal_loadings"].append(ThermLoading)

    def add_temperature_constraint(self, nodeID, temperature):
        self.Graph.nodes[nodeID]["temp_constraint"] = temperature


    def initialize_node_temps(self, temperature):
        """
        Sets all nodal temps to a constant. 
        
        All values with temperature constraints are set to that value.
        """
        for node in self.Graph.nodes():

            if self.Graph.nodes[node]["temp_constraint"]:
                 self.Graph.nodes[node]["element"].T = self.Graph.nodes[node]["temp_constraint"]
            else:
                self.Graph.nodes[node]["element"].T = temperature


        


    def get_node_temps(self):
        temps = []
        for node in self.Graph.nodes():
            temps.append(self.Graph.nodes[node]["element"].T) 
        return temps



    def updateThermalResistances(self):
        # Update all the edge weights with the thermal resistance values from conduction
        for edge in self.Graph.edges:
            T_resist = 0

            for nodeID in edge:
                node = self.Graph.nodes[nodeID]['element']
                T_resist += node.dy/ (2*node.area*node.k)

            self.Graph.edges[edge]['weight'] = T_resist



    def updateNodeTemps(self, time, t_step):
        """
        
        TODO:
            - Make the calculation of heat-fluxes non-redundant. Go on edge-by-edge basis, not nodal
            - Cleanup
            - Use Dictionary instead of list, for robustness of Node numbers being out of order or non-sequential 
            - 
        """

        # Set all of the nodal heat flux values to zero
        qDot_arr = np.zeros( [self.Graph.number_of_nodes(),])

        # Calculate Conduction, etc. between nodes
        for n0, n1, att in self.Graph.edges(data=True):

            node0 = self.Graph.nodes[n0]["element"]
            node1 = self.Graph.nodes[n1]["element"]

            # Calculate Conduction - Positive INTO first element
            q_cond = ( node1.T - node0.T ) / att["weight"]
            qDot_arr[n0] += q_cond
            qDot_arr[n1] += -q_cond

        # GET RATE OF CHANGE OF EACH NODE (DONT CHANGE NODE TEMPS WHILE DOING THIS DUMBASS)
        for nodeID_curr in self.Graph.nodes:
            elem_curr = self.Graph.nodes[nodeID_curr]["element"]

            # Temperature Constraint
            if self.Graph.nodes[nodeID_curr]["temp_constraint"]:
                qDot_arr[nodeID_curr] = 0.0
                continue

            # Thermal Loading
            for ThermalLoad in self.Graph.nodes[nodeID_curr]["thermal_loadings"]:
                qDot_arr[nodeID_curr] += ThermalLoad.get_q_in(elem_curr, time, t_step)


        # Propagate nodal temperatures forward
        self.updateTemperatures(qDot_arr, t_step)


    def updateTemperatures(self, qDot_arr, t_step):

        for nodeID_curr in self.Graph.nodes:

            el = self.Graph.nodes[nodeID_curr]["element"]

            el.T += qDot_arr[nodeID_curr] * t_step / el.mass / el.cp


    def draw(self):
        # https://networkx.org/documentation/stable/auto_examples/drawing/plot_weighted_graph.html
        plt.figure()

        # pos = nx.spring_layout(self.Graph, seed=3)
        pos = nx.spectral_layout(self.Graph)
        
        # nodes
        nx.draw_networkx_nodes(self.Graph, pos, node_size=700)

        # edges
        nx.draw_networkx_edges(self.Graph, pos, width=6)

        # node labels
        nx.draw_networkx_labels(self.Graph, pos, font_size=20, font_family="DejaVu Sans Mono")
        # edge weight labels
        edge_labels = nx.get_edge_attributes(self.Graph, "weight")

        res = dict()
        for key in edge_labels:
            res[key] = round(edge_labels[key], 6)


        nx.draw_networkx_edge_labels(self.Graph, pos, res, font_family="DejaVu Sans Mono")

        ax = plt.gca()
        ax.margins(0.08)
        plt.axis("off")
        plt.tight_layout()
        plt.show()

























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
                    #This just returns the constant values for above
                    print("CONSTANT PROPERTY LOOKUP IS BROKEN")
                    test = lambda T : ABLATIVE_DICT[material][prop]
                    setattr(self, prop+"_lookup", test )


            # Resin Fraction
            self.resin_frac = ABLATIVE_DICT[material]["resin_frac"]

            # Total Density
            self.rho    = ABLATIVE_DICT[material]["initial_total_density"]


            # Initialize Component Densities to Virgin Values
            self.rho_comp = np.copy(ABLATIVE_DICT[material]['virgin_component_densities'])
            
            # Thermal Properties
            self.emis   = ABLATIVE_DICT[material]['emis']

            # self.cp     = self.cp_lookup(290.0)
            # self.k      = self.k_lookup(290.0)

            self.cp     = 2100.0
            self.k      = 0.07

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

        self.cp     = 2100.0
        self.k      = 0.07


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
        if self.num_arr_components == 3.0:
            dRho_tot = self.resin_frac*(dRho_dt_comp[0] + dRho_dt_comp[1]) + (1.0-self.resin_frac)*dRho_dt_comp[2]
        elif self.num_arr_components == 2.0:
            dRho_tot = self.resin_frac*(dRho_dt_comp[0]) + (1.0-self.resin_frac)*dRho_dt_comp[1]
        else:
            raise Exception("Unsupported Number of Arrhenious Coeffs")


        # Update Densities
        for i in range(self.num_arr_components):
            self.rho_comp[i] = self.rho_comp[i] + dRho_dt_comp[i] * dt
 

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





