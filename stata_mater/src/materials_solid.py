"""
Dictionary containing all the solid (standard, non-ablating) material definitions. 
You can modify properties or add new materials here.


Notes:
- ALL MATERIAL PROPERTIES MUST BE INPUT IN THE UNITS SPECIFIED IN 'TEMPLATE_MATERIAL'
    (kg/m^3 for density, J/KgK or J/KgC for Specific Heat, W/mK for Thermal Conductivity)
- Any materials added here will automatically show up in the GUI
- For anisotropic materials (i.e. fibreglass, carbon fiber, etc.), the thermal conductivity
    value we care about is going to be in the THROUGH-WALL or TRANSVERSE direction. 


Resources:
- Carbon Fiber Tow Properties: https://www.toraycma.com/wp-content/uploads/T300-Technical-Data-Sheet-1.pdf.pdf
    k = 10.5 W/mK (i assume this is along-fibers), Cp = 777 J/KgK,
- Epoxy and Phenolic thermal properties can be found in Materials Science and Engineering: an introduction, Wiley
    - Epoxy: k = 0.19 W/mK, Cp = 1010 J/kgG
    - Phenolic: k = 0.15 W/mK, Cp = 1590-1760 J/KgK
- Phenolic Composite source? : https://sci-hub.ru/10.1016/0266-3538(87)90070-4




HOW-TO-ADD MATERIAL (idk if i really needed to add this, You're probably smare enough to add to a dict :))
- Make a copy of template material, 
- Paste it below it (but not outside the last closing bracket)
- Input material properties, taking note of units.

"""

#---------------------------------------------------------------------------------------------------#
#       Solid Materials Dictionary
#---------------------------------------------------------------------------------------------------#
MATERIALS_DICT = { 
    
    # Aluminum 6061
    'ALU6061': {
        'rho':  2700.0, #[kg/m^3] Density
        'cp':   896.0,  #[J/KgC] Specific Heat
        'k':    167.0,  #[W/mK]Thermal Conductivity
        'emis': 0.8     #[] Black Body Emissivity Coefficient
                        # Fundamentals of Thermal Fluid Sciences, Cengel 
                        # Polished 300–900K 0.04–0.06, Commercial sheet 400K 0.09
                        # Heavily oxidized 400–800K 0.20–0.33, Anodized 300K 0.8
    },


    # 316 Stainless Steel
    'SS316': {
        # Source: https://www.matweb.com/search/DataSheet.aspx?MatGUID=dfced4f11d63459e8ef8733d1c7c1ad2
        'rho':  8000.0,  #[kg/m^3] Density
        'cp':   500.0,   #[J/KgC] Specific Heat
        'k':    16.3,   #[W/mK]Thermal Conductivity
        'emis': 0.8     #[] Black Body Emissivity Coefficient
                        # THIS VALUE WAS NOT SPECIFIED, JUST PUTTING AS 0.8 AS DEFAULT
    },


    # 304 Stainless Steel
    'SS304': {
        # Source: https://www.matweb.com/search/datasheet.aspx?MatGUID=abc4415b0f8b490387e3c922237098da
        'rho':  8000.0,  #[kg/m^3] Density
        'cp':   500.0,   #[J/KgC] Specific Heat
        'k':    16.2,   #[W/mK]Thermal Conductivity
        'emis': 0.8     #[] Black Body Emissivity Coefficient
                        # THIS VALUE WAS NOT SPECIFIED, JUST PUTTING AS 0.8 AS DEFAULT
    },


    # 718 Inconel
    'INCO718': {
        # Source: https://www.matweb.com/search/DataSheet.aspx?MatGUID=94950a2d209040a09b89952d45086134
        'rho':  8190.0, #[kg/m^3] Density
        'cp':   435.0,  #[J/KgC] Specific Heat
        'k':    11.4,   #[W/mK]Thermal Conductivity
        'emis': 0.8     #[] Black Body Emissivity Coefficient
                        # THIS VALUE WAS NOT SPECIFIED, JUST PUTTING AS 0.8 AS DEFAULT
    },


    # FR-4, Woven Glass Fiber Composite
    'FR4': {
        # Source: https://www.engineersedge.com/heat_transfer/thermal_properties_of_nonmetals_13967.htm
        # No additional sources, but seemed pretty close to other values I was seeing (papers, mcmaster)
        'rho':  1900.0, #[kg/m^3] Density
        'cp':   1150.0,  #[J/KgC] Specific Heat
        'k':    0.294,   #[W/mK]Thermal Conductivity,
        'emis': 0.8     #[] Black Body Emissivity Coefficient - NO SOURCE, JUST PUTTING AS 0.8 AS DEFAULT
    },


    # Carbon Fiber Epoxy
    'CARBONFIBER': {
        'rho':  1500.0, #[kg/m^3] Density, https://www.mcmaster.com/5287T97-5287T731/
        'cp':   1100.0,  #[J/KgC] Specific Heat, using AS4 values at like 80C from p.44 https://digital.library.ncat.edu/cgi/viewcontent.cgi?article=1012&context=theses
        'k':    0.6,   #[W/mK]Thermal Conductivity, using AS4 values at like 80C from p.47 of above reference. 
                        # In family w/ here though: https://www.christinedemerchant.com/carbon_characteristics_heat_conductivity.html
        'emis': 0.8     #[] Black Body Emissivity Coefficient - NO SOURCE, JUST PUTTING AS 0.8 AS DEFAULT
    },


    # Fiberglass, Sumitomo E264H
    'FIBERGLASS': {
        # Source: https://www.osti.gov/servlets/purl/1328167
        'rho':  1815.0, #[kg/m^3] Density
        'cp':   1200.0,  #[J/KgC] Specific Heat
        'k':    0.48,   #[W/mK]Thermal Conductivity,
        'emis': 0.8     #[] Black Body Emissivity Coefficient - NO SOURCE, JUST PUTTING AS 0.8 AS DEFAULT
    },




    # TEMPLATE MATERIAL, please do not actually use this material in simulations.
    #   Just copy it and use it to define new materials
    'TEMPLATE_MATERIAL': {
        'rho':  -1.0, #[kg/m^3]   Density
        'cp':   -1.0,  #[J/KgC]    Specific Heat
        'k':    -1.0,  #[W/mK]     Thermal Conductivity
        'emis': -1.0     #[]         Black Body Emissivity Coefficient
    },





}