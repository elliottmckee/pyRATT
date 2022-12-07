

import numpy as np

from math import pow, sqrt

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


    # Shock Calc
    if shock_type != "oblique":
        raise NotImplementedError()


    # Break-out Pre-Shock State
    #WORKAROUND ALERT###########
    print("Warning: Hilarious Workaround in Aerothermal Hearflux for Overriding m_inf < 1.0 values")
    if m_inf < 1.0:
        m_inf = 1.0

    p_inf   = atm_state.pressure
    T_inf   = atm_state.temperature
    rho_inf = atm_state.density
    mu_inf  = atm_state.dynamic_viscosity


    # Shock Calculator - Post-Shock Properties
    m_e, p2op1, rho2orho1, T2oT1, _, p02op01, _ =  aero_tools.oblique_shock( m_inf, AirModel.gam, Rocket.nosecone_angle_rad)

    p_e = p2op1 * p_inf
    T_e = T2oT1 * T_inf
    T_te = aero_tools.total_temperature(T_e, m_e, AirModel.gam) #Total Temperature at Edge
    
    u_e = sqrt(AirModel.gam * AirModel.R * T_e) * m_e
    
    #Get Transport Properties at BL Edge
    cp_e = AirModel.specific_heat(T_e)
    k_e  = AirModel.thermal_conductivity(T_e)
    mu_e = AirModel.dynamic_viscosity(T_e)
    
    pr_e = cp_e * mu_e / k_e  #Prandtl at Edge

    
    # Calculate Recovery, Reference Temperature
    if bound_layer_model == 'turbulent':
        r = pow(pr_e, 1.0/3.0)
        T_r     = recovery_temperature(T_e, T_te, T_w, r)
        T_ref   = eckert_ref_temperature(T_e, T_te, T_w, r)
    else:
        raise NotImplementedError('Turbulent only plox')
    
    # Calculate Transport Properties at Reference Temperature
    cp_ref = AirModel.specific_heat(T_ref)
    k_ref  = AirModel.thermal_conductivity(T_ref)
    mu_ref = AirModel.dynamic_viscosity(T_ref)

    rho_ref = p_e / (AirModel.R*T_ref)

    #SHOULD VELOCITY BE ALTERED AT ALL FROM REFERENCE TEMP?
    Re_ref = (rho_ref*u_e*x_location)/mu_ref #Reynolds eval'd at RefTemp
    pr_ref = cp_ref * mu_ref / k_ref  #Prandtl eval'd at RefTemp


    # Heating Model
    q_w = ulsu_simsek_heat_transfer(x_location, T_w, T_r, k_ref, Re_ref, pr_ref)

    return q_w




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



def ulsu_simsek_heat_transfer(x, T_w, T_r, k_ref, Re_ref, pr_ref):

    # CAN ONLY HANDLE TURBULENT AS OF RN

    # #Laminar to Turbulent Transition as given in Quinn and Gong
    # if (log10(Re_star) <= 5.5 + Sim.C_m*M_L)
    #     #Laminar Heat Transfer Coeff (USLU)
    #     h = (k_star/Sim.x) * 0.33206 * Re_star ^ (1/2) * Pr_star ^ (1/3);
    #     lam = .5;
    # else
    
    #Turbulent Heat Transfer Coeff
    h =  (k_ref/x) * 0.02914 * pow(Re_ref, 4.0/5.0) * pow(pr_ref, 1.0/3.0)
    #lam = .4;

    #Heat Flux
    return h*(T_r - T_w)



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






#Recovery Temperature






