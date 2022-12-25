

import numpy as np

# Standard Atmosphere Model/Package (CANT HANDLE HIGH-ALT)
# https://ambiance.readthedocs.io/en/latest/index.html
from ambiance import Atmosphere

from math import pow, sqrt, log10

from ..common import constants
from . import aero_tools


# def aerothermal_heatflux(
#                     Rocket,
#                     AirModel,
#                     T_w, 
#                     x_location, 
#                     m_inf, 
#                     atm_state, 
#                     shock_type, 
#                     aerothermal_model,
#                     bound_layer_model = 'turbulent',
# ):
def aerothermal_heatflux(Sim, i):
    '''
    Returns material properties for a solid, nonablating wall material from the database (if-else chain) below 

            Parameters:
                    material_name (str): string corresponding to the material to be used,
                                            must match an item in the if-else chain below

            Returns:
                    rho,    material density [kg/m^3]
 
    '''
    
    #Break out Exposed Surface Wall Temp
    T_w = Sim.wall_temps[0,i]

    # calculate boundary layer edge properties
    p_e, rho_e, T_e, T_te, m_e, u_e, cp_e, k_e, mu_e, pr_e, Re_e = get_edge_properties(Sim, i)

    # determine boundary layer state
    isTurbulent = get_bl_state(Sim, Re_e, m_e)
    
    # calculate recovery factor, temperature
    r   = recovery_factor(isTurbulent, pr_e)
    T_r = recovery_temperature(T_e, T_te, T_w, r)

    # calculate Eckert reference temperature
    T_ref = eckert_ref_temperature(T_e, T_te, T_w, r)

    # Get fluid properties evaluated at reference temperature
    rho_ref, cp_ref, k_ref, mu_ref, pr_ref, Re_ref = complete_aero_state(Sim.AirModel, Sim.x_location, p_e, T_ref, u_e)

    # Heating Model
    q_conv, h = ulsu_simsek_heat_transfer(Sim.x_location, T_w, T_r, k_ref, Re_ref, pr_ref, isTurbulent)

    return q_conv, h, T_te, T_r



def get_edge_properties(Sim, i):

    #Pulling the Air model out because it gets used a lot
    AirModel = Sim.AirModel

    #Get Current Free-stream props
    atm_inf = Atmosphere([Sim.alt[i]])
    m_inf = Sim.mach[i]

    # Break-out Pre-Shock/Free-Stream State, 
    p_inf   = atm_inf.pressure
    T_inf   = atm_inf.temperature
    rho_inf = atm_inf.density
    mu_inf  = atm_inf.dynamic_viscosity

    # Shock Calc
    if Sim.shock_type != "oblique":
        raise NotImplementedError()

    #Determine Edge Properties (behind shock if needed)
    if m_inf >  1.0:
        # Yes Shock - Shock Relations for Post-Shock Properties
        m_e, p2op1, _, T2oT1, _, _, _ =  aero_tools.oblique_shock( m_inf, AirModel.gam, Sim.Rocket.nosecone_angle_rad)

        p_e = p2op1 * p_inf
        T_e = T2oT1 * T_inf
        
    else:
        #No Shock
        m_e = m_inf
        p_e = p_inf
        T_e = T_inf
        
        
    # Total Temperature at Edge
    T_te = aero_tools.total_temperature(T_e, m_e, AirModel.gam) 

    # Edge Velocity
    u_e = sqrt(AirModel.gam * AirModel.R * T_e) * m_e
    
    #Complete Aero State at Edge conditions
    rho_e, cp_e, k_e, mu_e, pr_e, Re_e = complete_aero_state(AirModel, Sim.x_location, p_e, T_e, u_e)

    return p_e, rho_e, T_e, T_te, m_e, u_e, cp_e, k_e, mu_e, pr_e, Re_e



def complete_aero_state(AirModel, x_location, p, T, u):

    #Get Aero Properties
    rho = p / (AirModel.R*T)
    
    #Get Transport Properties
    cp = AirModel.specific_heat(T)
    k  = AirModel.thermal_conductivity(T)
    mu = AirModel.dynamic_viscosity(T)
    pr = cp * mu / k 

    #Reynolds No
    Re = (rho*u*x_location)/mu 

    return rho, cp, k, mu, pr, Re 


def get_bl_state(Sim, Re_e, m_e):

    if Sim.bound_layer_model == 'turbulent':
        return True
    
    elif Sim.bound_layer_model == 'laminar':
        return False
    
    elif Sim.bound_layer_model == 'transition':
        #Reynolds Number Criterion for Transition from Ulsu
        if (log10(Re_e) <= 5.5 + constants.C_M*m_e):
            #If Laminar
            return False
        else:
            #Turbulent
            return True
    else:
        raise Exception("Invalid Boundary Layer Model Specification")



def recovery_factor(isTurbulent, pr_e):
    if isTurbulent:
        return pow(pr_e, 1.0/3.0)
    else:
        return pow(pr_e, 1.0/2.0)



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



#Fay-Riddell Stagnation Point Heating
def fay_riddell_stagnation_point_heating():
    pass

#Flat-Plate Heating Correlations
def tauber_flat_plate_heating():
    pass

def tauber_cone_heating():
    pass




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







