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
        'abl_temp_threshold':       100,   #[K] Ablation Temperature Threshold. No Abl. below this temp (Dec, Braun)  uses 644 or 1000
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




}


