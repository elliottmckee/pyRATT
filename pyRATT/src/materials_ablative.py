"""
Dictionary containing all the ablating material definitions. 
You can modify properties or add new materials here, though they're a 
bit more involved than for solids.


Notes:
- 

Resources:
- 


"""
import numpy as np


#---------------------------------------------------------------------------------------------------#
#       Ablative  Materials Dictionary
#---------------------------------------------------------------------------------------------------#
ABLATIVE_DICT = { 
    
 
    'PICA': {
        'type':                     "arrhenious",
        'abl_temp_threshold':       1000,   #[K] Ablation Temperature Threshold. No Abl. below this temp (Dec, Braun)  uses 644 or 1000
        'num_arr_components':       3,      #[] Number of Components Modelled with Arrhenious
        'initial_total_density':    264.1,  #[kg/m3] Total Density of Original Material 
        'virgin_component_densities':    (229.0, 972.0, 160.0),  #[kg/m3] Ablative Component Virgin Densities
        'char_component_densities': (0.0, 792.0, 160.0),    #[kg/m3] Char Component Virgin Densities

        'arr_B':  (1.4e4, 4.48e9, 0.0),     #[1/s] Arrhenious Pre-Exponential Constants 
        'arr_ER': (8555.6,  20444.4, 0.0),   #[K] Arrhenious E/R Activation Energies/R
        'arr_N': (3.0, 3.0, 0.0),            #[] Arrhenous Reaction Orders

        'resin_frac': 0.1,                   #[]Resin Fraction ALTERED TO MATCH SIMSEK (LIKELY INCORRECT)

        'cp': 'resources/PICA_Ablative_Props/_CpvTemp.csv',                    #[J/KgK], Lookup table of Cp vs Temp
        'k': 'resources/PICA_Ablative_Props/_TCon_Temp.csv',                   #[W/mK], Lookup table of k (therm cond.) vs Temp
        'emis': 0.9,
        'Qstar': 'resources/PICA_Ablative_Props/_EffHeatAbl_ConvHeatFlux.csv'  #[J/kg] Q*? vs Convective Heat Flux [W/m^2]
        # If the above are strings, I am assume its its a path to a lookup table. Can use float for constant 
    },

    # 'GOLDSTIEN-PICA': {
    #     'type':                     "arrhenious",
    #     'abl_temp_threshold':       100,   #[K] Ablation Temperature Threshold. No Abl. below this temp (Dec, Braun)  uses 644 or 1000
    #     'num_arr_components':       3,      #[] Number of Components Modelled with Arrhenious
    #     'initial_total_density':    264.1,  #[kg/m3] Total Density of Original Material 
    #     'virgin_component_densities':    (229.0, 972.0, 160.0),  #[kg/m3] Ablative Component Virgin Densities
    #     'char_component_densities': (0.0, 792.0, 160.0),    #[kg/m3] Char Component Virgin Densities

    #     'arr_B':  (1.4e4, 4.48e9, 0.0),     #[1/s] Arrhenious Pre-Exponential Constants 
    #     'arr_ER': (8555.6,  20444.4, 0.0),   #[K] Arrhenious E/R Activation Energies/R
    #     'arr_N': (3.0, 3.0, 1.0),            #[] Arrhenous Reaction Orders

    #     'resin_frac': 0.1,                   #[]Resin Fraction ALTERED TO MATCH SIMSEK (LIKELY INCORRECT)

    #     'cp': 'resources/PICA_Ablative_Props/_CpvTemp.csv',                    #[J/KgK], Lookup table of Cp vs Temp
    #     'k': 'resources/PICA_Ablative_Props/_TCon_Temp.csv',                   #[W/mK], Lookup table of k (therm cond.) vs Temp
    #     'emis': 0.9,
    #     'Qstar': 'resources/PICA_Ablative_Props/_EffHeatAbl_ConvHeatFlux.csv'  #[J/kg] Q*? vs Convective Heat Flux [W/m^2]
    #     # If the above are strings, I am assume its its a path to a lookup table. Can use float for constant 
    # },



    'CORKP50': { 
        # Using values from Isil Sakraker, Aerothermodynamics of Pre-Flight and In-Flight Testing Methodologies for
        # Atmospheric Entry Probes
        
        'type':                     "arrhenious",
        'abl_temp_threshold':       430,      #[K] Ablation Temperature Threshold.
        'num_arr_components':       2,      #[] Number of Components Modelled with Arrhenious
        'initial_total_density':    465.0,  #[kg/m3] Total Density of Original Material 
        'virgin_component_densities':    (466.0, 464.0),  #[kg/m3] Ablative Component Virgin Densities
        'char_component_densities': (298.0, 279.0),    #[kg/m3] Char Component Virgin Densities

        'arr_B':  (4987.26, 10000.0),     #[1/s] Arrhenious Pre-Exponential Constants 
        'arr_ER': (82678.0/8.314,  51439.0/8.314),   #[K] Arrhenious E/R Activation Energies/R
        'arr_N': (1.07, 3.57),            #[] Arrhenous Reaction Orders

        'resin_frac': 0.5,                   #[]Resin Fraction ALTERED TO MATCH SIMSEK (LIKELY INCORRECT)

        'cp': 2100.0,                    #[J/KgK], Source: https://www.amorimasia.com/uploads/4/8/0/0/48004771/tps_pp_04_07_2008ac.pdf
        'k': 0.07,                   #[W/mK], Source: https://www.amorimasia.com/uploads/4/8/0/0/48004771/tps_pp_04_07_2008ac.pdf
        'emis': 0.8,    # I guessed
        'Qstar': 3.6e7  #[J/kg] Q*? vs Convective Heat Flux [W/m^2]
        # I am really shadily backing this out from the Table on Page 88 of Sakraker 
    },



}


