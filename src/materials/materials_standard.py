from typing import Optional


def solidMaterialDatabase(material_name: str):
    #emis_override optional argument is to override surface emissivity, if desired

    #######################################################################
    ###################    MATERIAL DATABASE      ########################
    #######################################################################

    if material_name == "ALU6061":
        
        rho = 2700;     #[kg/m^3] Density
        cp = 896;       #[J/KgC] Specific Heat
        k = 167;        #[W/mK]Thermal Conductivity
        emis = 0.8      #[] Black Body Emissivity Coefficient 
                        # Fundamentals of Thermal Fluid Sciences, Cengel 
                        # Polished 300–900K 0.04–0.06, Commercial sheet 400K 0.09
                        # Heavily oxidized 400–800K 0.20–0.33, Anodized 300K 0.8


    elif material_name == "OTHER EXAMPLE MATERIAL":
        rho = -1;     #[kg/m^3] Density
        cp = -1;       #[J/KgC] Specific Heat
        k = -1;        #[W/mK]Thermal Conductivity
        emis = -1      #[] Black Body Emissivity Coefficient 





    #If material isn't found
    else:
        raise Exception("Invalid Material Specification or Material not Found - Material Spelling, or solidMaterialDatabase()")

    #######################################################################
    ###################    END OF DATABASE         ########################
    #######################################################################


    # Return Material Properties
    return rho, cp, k, emis




























