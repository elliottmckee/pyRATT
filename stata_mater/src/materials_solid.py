

def solidMaterialDatabase(material_name: str):
    '''
    Returns material properties for a solid, nonablating wall material from the database (if-else chain) below 

            Parameters:
                    material_name (str): string corresponding to the material to be used,
                                            must match an item in the if-else chain below

            Returns:
                    rho,    material density [kg/m^3]
                    cp,     material specific heat at constant pressure [J/KgC]
                    k,      material thermal conductivity [W/mK]
                    emis    material Black Body Emissivity Coefficient 
    '''

    if material_name == "ALU6061":
        
        rho = 2700.0      #[kg/m^3] Density
        cp = 896.0        #[J/KgC] Specific Heat
        k = 167.0         #[W/mK]Thermal Conductivity
        emis = 0.8      #[] Black Body Emissivity Coefficient 
                        # Fundamentals of Thermal Fluid Sciences, Cengel 
                        # Polished 300–900K 0.04–0.06, Commercial sheet 400K 0.09
                        # Heavily oxidized 400–800K 0.20–0.33, Anodized 300K 0.8


    elif material_name == "MATERIAL_TEMPLATE":
        rho = -1      #[kg/m^3] Density
        cp = -1        #[J/KgC] Specific Heat
        k = -1         #[W/mK]Thermal Conductivity
        emis = -1      #[] Black Body Emissivity Coefficient 



    #If material isn't found
    else:
        raise Exception("Invalid Material Specification or Material not Found - Material Spelling, or solidMaterialDatabase()")


    # Return Material Properties
    return rho, cp, k, emis




























