

class SolidMaterial:
    #Initialize, populate material properties - default to Aluminum 6061
    def __init__(self, material = "ALU6061"):
        
        self.rho, self.cp, self.k = solidMaterialDatabase(material)



def solidMaterialDatabase(material_name):


    #######################################################################
    ###################    MATERIAL DATABASE      ########################
    #######################################################################



    if material_name == "ALU6061":
        
        rho = 2700;     #[kg/m^3] Density
        cp = 896;       #[J/KgC] Specific Heat
        k = 167;        #[W/mK]Thermal Conductivity

    elif material_name == "OTHER EXAMPLE MATERIAL":
        rho = -1;     #[kg/m^3] Density
        cp = -1;       #[J/KgC] Specific Heat
        k = -1;        #[W/mK]Thermal Conductivity



    #######################################################################
    ###################    END OF DATABASE         ########################
    #######################################################################


    #If material isn't found
    else:
        raise Exception("Invalid Material Specification or Material not Found - Material Spelling, or solidMaterialDatabase()")


    # Return Material Properties
    return rho, cp, k




























