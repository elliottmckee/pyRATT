

import numpy as np

from math import pow, sqrt, log10

from ..common import constants
from . import aero_tools


def aerothermal_heatflux(
                    Rocket,
                    AirModel,
                    T_w, 
                    x_location, 
                    m_inf, 
                    atm_state, 
                    shock_type, 
                    aerothermal_model,
                    bound_layer_model = 'turbulent',
):
    '''
    Returns material properties for a solid, nonablating wall material from the database (if-else chain) below 

            Parameters:
                    material_name (str): string corresponding to the material to be used,
                                            must match an item in the if-else chain below

            Returns:
                    rho,    material density [kg/m^3]
 
    '''


    # Shock Calc
    if shock_type != "oblique":
        raise NotImplementedError()


    # Break-out Pre-Shock/Free-Stream State, 
    p_inf   = atm_state.pressure
    T_inf   = atm_state.temperature
    rho_inf = atm_state.density
    mu_inf  = atm_state.dynamic_viscosity



    #Determine Edge Properties (behind shock if needed)
    if m_inf >  1.0:
        # Yes Shock - Shock Relations for Post-Shock Properties
        m_e, p2op1, rho2orho1, T2oT1, _, p02op01, _ =  aero_tools.oblique_shock( m_inf, AirModel.gam, Rocket.nosecone_angle_rad)

        p_e = p2op1 * p_inf
        T_e = T2oT1 * T_inf
        
    else:
        #No Shock
        m_e = m_inf
        p_e = p_inf
        T_e = T_inf
        
        
    #Get Aero Properties at BL Edge
    rho_e = p_e / (AirModel.R*T_e)
    T_te = aero_tools.total_temperature(T_e, m_e, AirModel.gam) #Total Temperature at Edge
    u_e = sqrt(AirModel.gam * AirModel.R * T_e) * m_e

    #Get Transport Properties at BL Edge
    cp_e = AirModel.specific_heat(T_e)
    k_e  = AirModel.thermal_conductivity(T_e)
    mu_e = AirModel.dynamic_viscosity(T_e)
    pr_e = cp_e * mu_e / k_e  #Prandtl at Edge

    Re_e = (rho_e*u_e*x_location)/mu_e #Reynolds eval'd at Edge

    
    # Get Recovery Factor Based on BL State
    isTurbulent = True #Flag - Defaults to Turbulent

    if bound_layer_model == 'turbulent':
        r = pow(pr_e, 1.0/3.0)
    
    elif bound_layer_model == 'laminar':
        isTurbulent = False
        r = pow(pr_e, 1.0/2.0)
    
    elif bound_layer_model == 'transition':
        #Reynolds Number Criterion for Transition from Ulsu
        if (log10(Re_e) <= 5.5 + constants.C_M*m_e):
            #If Laminar
            isTurbulent = False
            r = pow(pr_e, 1.0/2.0)
        else:
            #Turbulent
            r = pow(pr_e, 1.0/3.0)
    else:
        raise Exception("Invalid Boundary Layer Model Specification")

    r = pow(pr_e, 1.0/3.0)
    T_r     = recovery_temperature(T_e, T_te, T_w, r)
    T_ref   = eckert_ref_temperature(T_e, T_te, T_w, r)

    
    # Calculate Transport Properties at Reference Temperature
    cp_ref = AirModel.specific_heat(T_ref)
    k_ref  = AirModel.thermal_conductivity(T_ref)
    mu_ref = AirModel.dynamic_viscosity(T_ref)

    rho_ref = p_e / (AirModel.R*T_ref)

    #SHOULD VELOCITY BE ALTERED AT ALL FROM REFERENCE TEMP?
    Re_ref = (rho_ref*u_e*x_location)/mu_ref #Reynolds eval'd at RefTemp
    pr_ref = cp_ref * mu_ref / k_ref  #Prandtl eval'd at RefTemp

    # Heating Model
    q_conv, h = ulsu_simsek_heat_transfer(x_location, T_w, T_r, k_ref, Re_ref, pr_ref, isTurbulent)

    return q_conv, h, T_te, T_r




def recovery_temperature(T_e, T_te, T_w, r): 
    # Source: Bertin Hypersonic Aerothermodynamics
    return r * (T_te - T_e) + T_e
    



def eckert_ref_temperature(T_e, T_te, T_w, r):
    #Calculate Eckert Reference Temperature

    # Note: The Recovery Factor is a function of the local air properties at a given
    # point. However, we cannot calculate Eckert's Reference temperature until
    # we have it. Using Free-stream Prandtl for this Calculation

    #Eckert Reference Temperature 
    return 0.5*(T_e + T_w) + 0.22*r*(T_te - T_e) # Source: Bertin, Hypersonic Aerothermodynamics



#Fay-Riddell Stagnation Point Heating
def fay_riddell_stagnation_point_heating():
    pass

#Flat-Plate Heating Correlations
def tauber_flat_plate_heating():
    pass

def tauber_cone_heating():
    pass



def ulsu_simsek_heat_transfer(x, T_w, T_r, k_ref, Re_ref, pr_ref, isTurbulent):

    # #Laminar to Turbulent Transition as given in Quinn and Gong
    if isTurbulent:
        #Turbulent Heat Transfer Coeff
        h =  (k_ref/x) * 0.02914 * pow(Re_ref, 4.0/5.0) * pow(pr_ref, 1.0/3.0)
        #lam = .4;
    else:
        #Laminar Heat Transfer Coeff
        h = (k_ref/x) * 0.33206 * pow(Re_ref, 1.0/2.0) * pow(pr_ref, 1.0/3.0)
        #lam = .5;
        

    # Heat Flux
    q_conv = h*(T_r - T_w)


    #Heat Flux
    return q_conv, h 



#Incopera Flat-Plate Heating Correlations
def incopera_heating_correlations():
    # Source:  Bergman, T. L., & Incropera, F. P.. Fundamentals of heat and mass transfer (Sixth edition.). Wiley. 
    # Page: 455, Summary of Convection Heat Transfer Correlations for External Flow

    # THERE ARE ALSO AVERAGE NUSSELT NUMBER CORRELATIONS - POSSIBLY USEFUL FOR LUMPED SUM?

    #This doens't acutally work yet - PLEASE CHECK THESE

    raise NotImplementedError()

    #Nusselt Number Correlations
    if "flat_plate":
        
        if "laminar":
            Nu_x = 0.332 * pow(Re_x, 1.0/2.0) * pow(Pr, 1.0/3.0)
        if "turbulent":
            Nu_x = 0.0296 * pow(Re_x, 4.0/5.0) * pow(Pr, 1.0/3.0)
    if "cylinder":
        #This is just a reminder that these are in the Incopera tables referenced, if we want them for body tube heating
        pass







