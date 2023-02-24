"""
Dictionary containing all the solid (standard, non-ablating) material definitions. 
You can modify properties or add new materials here.

Notes:
- ALL MATERIAL PROPERTIES MUST BE INPUT IN THE UNITS SPECIFIED IN 'TEMPLATE_MATERIAL'
    (kg/m^3 for density, J/KgK or J/KgC for Specific Heat, W/mK for Thermal Conductivity)
- Any materials added here will automatically show up in the GUI

HOW-TO-ADD MATERIAL (idk if i really needed to add this, if you're here you prob know how python works):
- Make a copy of template material, 
- Paste it below it (but not outside the last closing bracket)
- Input material properties, taking note of units.

"""

#---------------------------------------------------------------------------------------------------#
#       Solid Materials Dictionary
#---------------------------------------------------------------------------------------------------#
MATERIALS_DICT = { 
    
    # 6061 Aluminum 
    'ALU6061': {
        'rho':  2700.0, #[kg/m^3] Density
        'cp':   896.0,  #[J/KgC] Specific Heat
        'k':    167.0,  #[W/mK]Thermal Conductivity
        'emis': 0.8     #[] Black Body Emissivity Coefficient
                        # Fundamentals of Thermal Fluid Sciences, Cengel 
                        # Polished 300–900K 0.04–0.06, Commercial sheet 400K 0.09
                        # Heavily oxidized 400–800K 0.20–0.33, Anodized 300K 0.8
    },



    # TEMPLATE MATERIAL, please do not actually use this material.
    #   Just copy it and use it to define new materials
    'TEMPLATE_MATERIAL': {
        'rho':  -1.0, #[kg/m^3]   Density
        'cp':   -1.0,  #[J/KgC]    Specific Heat
        'k':    -1.0,  #[W/mK]     Thermal Conductivity
        'emis': -1.0     #[]         Black Body Emissivity Coefficient
    },





}