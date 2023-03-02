"""
Contains all the tools, models, etc. for the convection and radiation 
portions of thermal heat transfer. 

"""

# Standard Modules
import numpy as np
from math import pow, sqrt, log10

#Internal Modules
from . import constants
from . import tools_aero



def get_net_heat_flux(Sim, i):
    """
    High-level driver for determining the net heat flux to hand into the conduction solver,
    for a simulation at a given timestep

    Inputs:
        Sim:    Simulation Object
        i:      Simulation Timestep
    Outputs:
        
    Updates:
        Sim.q_rad[i],   float, radiative heatflux in W/m^2. Positive if heat is going into the wall
        Sim.q_conv[i],  float, convective heatflux in W/m^2. Positive if heat is going into the wall
        Sim.q_net[i],   float, net heatflux in W/m^2. Positive if heat is going into the wall

    TODO:
        Ideally, make it so all updated variables return up to this funciton. 
        I kinda want all Sim.value[i] updates to be no more than 1 (2 at max) functions deep, 
        so we are not setting values silently super deep, in a nested chain of functions
        but may be a non-issue since you can search all files for where things get written

    """

    # Get Convective Heatflux
    Sim.q_conv[i] = aerothermal_heatflux(Sim, i)

    # Radiative Heat Flux
    Sim.q_rad[i] = radiative_heatflux(Sim, i)

    # Net Heat Flux
    Sim.q_net[i] = Sim.q_conv[i] + Sim.q_rad[i]



def radiative_heatflux(Sim, i):
    """
    High level wrapper for the radiative thermal models that are implmemented/can be used.

    Inputs:
        Sim:    Simulation Object
        i:      Simulation Timestep
    Outputs:
        q_rad:  float, radiative heatflux in W/m^2. Positive if heat is going into the wall
    """

    # Just the plain ole black body radiation equation. Nothing fancy here. 
    return constants.SB_CONST * Sim.Aerosurface.elements[0].emis * ((Sim.T_inf[i])**4 - Sim.wall_temps[0,i]**4)



def aerothermal_heatflux(Sim, i):
    '''
    High level wrapper/driver for the aerothermal convective models that are 
    implmemented and can be used. 

    Inputs:
        Sim:    Simulation Object
        i:      Simulation Timestep
    Updates:
        T_e:        float, edge temperature [K]
        T_te:       float, edge total temperature [K]
        T_recovery: float, recovery temperature [K]
        h_coeff:    float, heat transfer coefficient
    Outputs:
        q_conv:  float, convective heatflux in [W/m^2]. Positive if heat is going into the wall
    '''

    # Implemented Aerothermal Models
    # ------------------------------
    # 1) default: This is the correlation used in the Ulsu [1] paper. Arnas is who is referenced there,  
    # but it is not who actually developed these correlations. However, after long while of running into 
    # paywalls trying to find original source because I am not a student anymore, I give up. Fuck publishers.

    # Dictionary containing all models and their corresponding function calls
    aerothermal_model_dict = {  "default": ulsu_simsek_heating(Sim, i) }

    if Sim.aerothermal_model not in aerothermal_model_dict.keys():
        raise ValueError("Error in Aerothermal Model Specification")

    
    # Implemented Boundary Layer Models
    # ------------------------------
    # 1) turbulent: fully turbulent flow
    # 2) laminar: fully laminar flow
    # 3) transition: flow transitions using a modified Re correlation described in Ulsu [1], but
    #                 real source is: 
    #                 Quinn, R. D., and L. Gong. 2000. A method for calculating transient surface temperatures 
    #                 and surface heating rates for high-speed aircraft. NASA/TP-2000-209034. Washington, DC: NASA.
    
    valid_boundarylayer_models     = ["turbulent","laminar","transition"]

    if Sim.bound_layer_model not in valid_boundarylayer_models:
        raise ValueError("Error in Boundary Layer/Transition Model Specification")


    # Call Aerothermal Model
    # ------------------------------
    q_conv = aerothermal_model_dict[Sim.aerothermal_model]

    return q_conv





def ulsu_simsek_heating(Sim, i):
    """ 
    Driver script for the heating model outline in Ulsu [1] to determine the convective heatflux.

    This is the high-level computational flow outlined in Ulsu [1], to determine the convective
    heatflux. If you're confused about anything here, I *highly* reccomend reading that paper.
    Honestly, just go read it now. Like right now. Do it. 
    
    Inputs:
        Sim:    Simulation Object
        i:      Simulation Timestep
    Updates:
        T_inf
        Re_inf
        qbar_inf
        T_t
        T_e
        T_te
        T_recovery
        h_coeff
    Outputs:
        q_conv: float, Convective Heat Flux [W/m^2]

    """
    
    # alias exposed hot-wall surface temperature
    T_w = Sim.wall_temps[0,i]

    # Get Freestream Properties
    p_inf, T_inf, u_inf, m_inf, rho_inf, cp_inf, k_inf, mu_inf, pr_inf, Re_inf = tools_aero.get_freestream_complete(Sim, i)

    # calculate boundary layer edge properties (post-shock)
    p_e, rho_e, T_e, T_te, m_e, u_e, cp_e, k_e, mu_e, pr_e, Re_e = tools_aero.get_edge_state(p_inf, T_inf, m_inf, Sim)

    # check boundary layer state (laminar/turbulent)
    bl_state = tools_aero.get_bl_state(Sim, Re_inf, m_inf)
    
    # calculate recovery factor, temperature
    r   = recovery_factor(bl_state, pr_e)
    T_r = recovery_temperature(T_e, T_te, T_w, r)

    # calculate Eckert reference temperature
    T_ref = eckert_ref_temperature(T_e, T_te, T_w, r)

    # Get complete fluid properties evaluated at reference temperature
    rho_ref, cp_ref, k_ref, mu_ref, pr_ref, Re_ref = tools_aero.complete_aero_state( p_e, T_ref, u_e, Sim.x_location, Sim.AirModel)

    # Flat Plate Heating Model, properties evaluated at reference temperature
    q_conv, h = flat_plate_heat_transfer(Sim.x_location, T_w, T_r, k_ref, Re_ref, pr_ref, bl_state)


    # Update/Pass values out of sim
    Sim.T_inf[i] = T_inf
    Sim.Re_inf[i] = Re_inf
    Sim.qbar_inf[i] = 0.5*rho_inf*u_inf**2
    Sim.T_t[i] = tools_aero.total_temperature(T_inf, m_inf, Sim.AirModel.gam)

    Sim.bl_state[i] = bl_state

    Sim.T_e[i] = T_e
    Sim.T_te[i] = T_te
    Sim.T_recovery[i] = T_r
    Sim.h_coeff[i] = h
    

    return q_conv

    


def recovery_factor(isTurbulent, pr_e):
    """ 
    Returns the recovery factor of a gas

    TODO put a source, and prandtl 
    limits/checks for the applicability of this
    """
    if isTurbulent:
        return pow(pr_e, 1.0/3.0)
    else:
        return pow(pr_e, 1.0/2.0)


def recovery_temperature(T_e, T_te, T_w, r): 
    """ 
    Returns the recovery temperature of a flow.
    
    TODO: Prandtl number applicability limits
    Source: Bertin Hypersonic Aerothermodynamics
    """
    return r * (T_te - T_e) + T_e
    

def eckert_ref_temperature(T_e, T_te, T_w, r):
    """
    Calculate Eckert Reference Temperature of a high-speed boundary layer

    Notes:
    -The Recovery Factor is a function of the local air properties at a given
    point. However, we cannot calculate Eckert's Reference temperature until
    we have it. Currently using Free-stream Prandtl for this Calculation.
    -TODO: Prandtl number applicability limits

    Source:
    - Bertin, Hypersonic Aerothermodynamics
    """

    #Eckert Reference Temperature 
    return 0.5*(T_e + T_w) + 0.22*r*(T_te - T_e)


def flat_plate_heat_transfer(x, T_w, T_r, k_ref, Re_ref, pr_ref, isTurbulent):
    """ 
    Flat plate Nusselt-number/heating correlations.

    Source:
    -Ill find the root source at some point lol, but these are super common
    """

    #Get Heat Transfer Coefficient
    if isTurbulent:
        #Turbulent Heat Transfer Coeff
        h =  (k_ref/x) * 0.02914 * pow(Re_ref, 4.0/5.0) * pow(pr_ref, 1.0/3.0)
        #lambda = .4;
    else:
        #Laminar Heat Transfer Coeff
        h = (k_ref/x) * 0.33206 * pow(Re_ref, 1.0/2.0) * pow(pr_ref, 1.0/3.0)
        #lambda = .5;
        
    # Heat Flux
    q_conv = h*(T_r - T_w)

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

    # These are so close to the Ulsu simsek flat plate heating values lol, i dont need to implement

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







