
# This will contain the class definitions for the *things*/structures to be analyzed
# Nosecone wall, Fin wall stacks


import numpy

from ..materials.materials_standard import SolidMaterial, solidMaterialDatabase



# class NoseconeWall:
#     def __init__(self, material_LIST, thickness_LIST, n_div_LIST, contact_resistances_LIST):


# class WallLayer:
#     def __init__(self, material, thickness, n_divisions):


class NoseconeSingleMaterialWall:
    def __init__(self, material, thickness, n_div):
        
        # Properties
        self.material  = solidMaterialDatabase(material)
        self.thickness = thickness
        self.n_div = n_div

        # Derived Values
        #self.wall_coords = linspace(0, Wall.delta, Sim.N)



# class Fin:
#     __init__(self):


# class BodyTube:
#     __init__(self):








