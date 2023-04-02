"""
Contains all the aerodynamic tool functions. Mainly the Shock calculation scripts,
and determination of freestream states/properties

Notes:


"""

import math
import scipy
import numpy as np
from math import pow, sqrt, log10

from ambiance import Atmosphere

from . import constants



def get_freestream(alt, AirModel, mach=None):
    """
    Function for returning the base aero state - atmospheric/
    freestream pressure, temperature, density, and optionally, 
    velocity, if you supply mach as an argument

    Inputs:
    -------
        - alt: float, altitude [m]
        - mach: float, optional
        - gamma: float, gas ratio of specific heats
        - R:    float, specific gas constant [J/KgK?]

    Outputs:
        -p_inf: float, atmospheric pressure [Pa]
        -T_inf: float, atmospheric temperature [K]
        -rho_inf: float, atmospheric denisty, [kg/m^3]
        *u_inf: float, freestream velocity [m/s]
            *only if mach specified
    """

    #Get atmospheric properties
    atm_inf = Atmosphere(alt)
    
    #If Mach Specified
    if mach is not None:
        u_inf = sqrt(AirModel.gam * AirModel.R * atm_inf.temperature) * mach
        return atm_inf.pressure, atm_inf.temperature, atm_inf.density, u_inf
    else:
        return atm_inf.pressure, atm_inf.temperature, atm_inf.density



def complete_aero_state(p, T, u, x_loc, AirModel):
    """
    "Completes" the Aero state, by providing density (derived),
    Cp, k, mu, pr, and Re

    Inputs:
        -p:     float, static pressure at given point [Pa]
        -T:     float, static temperature at given point [K]
        -u:     float, flow velocity at given point [m/s]
        -x_loc, float, downstream location of analysis [m]
        -AirModel, AirModel object for the fluid

    Outputs:
        -rho,   float, fluid density [kg/m^3]
        -cp,    float, fluid specific heat at constant presure [J/KgK?]
        -k,     float, fluid thermal conductivity [too lazy to lookup units rn]
        -mu,    float, fluid viscosity
        -pr,    float, fluid prandtl number
        -Re,    float, fluid local reynolds number 
    """

    # Calculate Derived Density 
    rho = p / (AirModel.R*T)
    
    # Get Transport Properties from Air Model
    cp = AirModel.specific_heat(T)
    k  = AirModel.thermal_conductivity(T)
    mu = AirModel.dynamic_viscosity(T)
    
    # Prandtl Number
    pr = cp * mu / k 

    # Reynolds Number
    Re = (rho*u*x_loc)/mu 

    return rho, cp, k, mu, pr, Re 


def get_freestream_complete(Sim, i):
    """ 
    Returns both the "base" and "complete" fluid states at the freestream
    for a Simulation at timestep i

    Outputs:
        p_inf, See above definitions. _inf denotes freestream properties
        T_inf, 
        u_inf, 
        m_inf, 
        rho_inf, 
        cp_inf, 
        k_inf, 
        mu_inf, 
        pr_inf, 
        Re_inf
    """
    
    # Get Freestream values
    m_inf = Sim.mach[i]
    p_inf, T_inf, _, u_inf = get_freestream(Sim.alt[i], Sim.AirModel, mach=m_inf)

    # Get "complete" Freestream Aero State
    rho_inf, cp_inf, k_inf, mu_inf, pr_inf, Re_inf = complete_aero_state(p_inf, 
                                                                            T_inf, 
                                                                            u_inf, 
                                                                            Sim.x_location,
                                                                            Sim.AirModel)

    return p_inf, T_inf, u_inf, m_inf, rho_inf, cp_inf, k_inf, mu_inf, pr_inf, Re_inf


def get_edge_state(p_inf, T_inf, m_inf, Sim, shock_override=None):
    """ 
    Returns the flow properties at the boundary layer edge.

    Inputs:
        Sim:    Simulation Object
        i:      Simulation Timestep
    
    Outputs:
        p_e, See above definitions. _e denotes edge properties
        rho_e, 
        T_e, 
        T_te, 
        m_e, 
        u_e, 
        cp_e, 
        k_e, 
        mu_e, 
        pr_e, 
        Re_e
    """

    # Get Post-shock state
    if shock_override:
        m_e, p_e, T_e = get_post_shock_state(m_inf, p_inf, T_inf, Sim, shock_override=shock_override) 
    else:
        m_e, p_e, T_e = get_post_shock_state(m_inf, p_inf, T_inf, Sim) 

    # Edge Velocity
    u_e = sqrt(Sim.AirModel.gam * Sim.AirModel.R * T_e) * m_e

    # Total Temperature at Edge
    T_te = total_temperature(T_e, m_e, Sim.AirModel.gam)
    
    #Complete Aero State at Boundary Layer Edge
    rho_e, cp_e, k_e, mu_e, pr_e, Re_e = complete_aero_state(p_e, 
                                                                T_e, 
                                                                u_e, 
                                                                Sim.x_location,
                                                                Sim.AirModel)

    return p_e, rho_e, T_e, T_te, m_e, u_e, cp_e, k_e, mu_e, pr_e, Re_e



def get_bl_state(Sim, Re, mach):
    """
    Returns the state of the boundary layer. 
    Turbulent is 1, Laminar is 0. 

    Inputs:
        Sim: Simulation Object
        Re: Local Reynolds Number (freestream conditions)
        mach: Freestream Mach
    """

    if Sim.bound_layer_model == 'turbulent':
        return 1
    
    elif Sim.bound_layer_model == 'laminar':
        return 0

    elif Sim.bound_layer_model == 'transition':
        #Reynolds Number Criterion for Transition from Ulsu
            #Assuming this uses the Free-Stream Values for Re and Mach
        if (log10(Re) <= 5.5 + constants.C_M*mach):
            #If Laminar
            return 0
        else:
            #Turbulent
            return 1
    else:
        raise Exception("Invalid Boundary Layer Model Specification")



def total_temperature(T, M, gam):
    """Just returns the flow total temperature
    
    Inputs:
        T: Temperature [K]
        M: Mach
        gam: gas ratio of specific heats 
    """
    return T * (1 + M ** 2 * (gam - 1) / 2)









##########################################################################################
# ---------------------------------------------------------------------------------------#
#                               SHOCK FUNCTIONS                                          #
# ---------------------------------------------------------------------------------------#
##########################################################################################


def get_post_shock_state(m_inf, p_inf, T_inf, Sim, shock_override=None):
    """
    High-level driver function to handle the shock models/implementation

    Inputs:
        m_inf: Freestream Mach
        p_inf: Freestream Pressure
        T_inf: Freestream Temp
        Sim: Simulation Object

    Outputs:
        m_e: boundary-layer edge mach
        p_e: boundary-layer edge pressure
        T_e: boundary-layer edge temperature

    """

    if Sim.shock_type not in  ["normal", "oblique", "conical"]:
        raise NotImplementedError()


    if shock_override:
        print("Overriding Shock")
        shock = shock_override
    else:
        shock = Sim.shock_type


    # Determine if shock or not
    if m_inf >  1.0:
        # Yes Shock - Shock Relations for Post-Shock Properties
        if shock == "normal":
            m_e, p2op1, _, T2oT1, _, _ =  normal_shock( m_inf, Sim.AirModel.gam)

        if shock == "oblique":
            m_e, p2op1, _, T2oT1, _, _, _ =  oblique_shock( m_inf, Sim.AirModel.gam, Sim.deflection_angle_rad)

        if shock == "conical":
            raise Exception("Conical Shocks not implemented yet. Reccomed using Oblique")
            #_, _, M, p2op1, T2oT1, _, _, _ =  conical_shock( m_inf, Sim.AirModel.gam, Sim.deflection_angle_rad)


        p_e = p2op1 * p_inf
        T_e = T2oT1 * T_inf
        
    else:
        #No Shock, same as freestream
        m_e = m_inf
        p_e = p_inf
        T_e = T_inf

    return m_e, p_e, T_e



def normal_shock(M_1, g):
    """
    Normal Shock Relation functions

    Inputs
        T:          float, upstream static temperature
        M:          float, upstream mach number 
        gam:        float, ratio of specific heats

    Outputs
        M2n:        float, mach downstream of normal shock
        P2_P1:      float, ratio of downstream/upstream static pressure
        rho2_rho1:  float, ratio of downstream/upstream density
        T2_T1:      float, ratio of downstream/upstream static temperature
        deltasoR:   float, change in entropy or something
        P02_P01:    float, ratio of downstream/upstream total pressure

    Sources:
    -Adapted from material from the CU Boulder ASEN 3111 Fundamentals of Aerodynamics course
    """
    M2n = math.sqrt((1 + (g - 1) / 2 * M_1 ** 2) / (g * M_1 ** 2 - (g - 1) / 2))
    P2_P1 = 1 + 2 * g / (g + 1) * (M_1 ** 2 - 1)
    rho2_rho1 = (g + 1) * M_1 ** 2 / (2 + (g - 1) * M_1 ** 2)
    T2_T1 = P2_P1 / rho2_rho1
    deltasoR = g / (g - 1) * math.log(T2_T1) - math.log(P2_P1)
    P02_P01 = math.exp(-deltasoR)

    return M2n, P2_P1, rho2_rho1, T2_T1, deltasoR, P02_P01



def oblique_shock(M_1, g, theta):
    """
    Oblique Shock Relations

    Inputs
        M_1:        float, upstream mach number
        g:          float, gamma, ratio of specific heats
        theta:      float, turning angle of the 2D wedge flow

    Outputs
        M2:         float, mach downstream of normal shock
        P2_P1:      float, ratio of downstream/upstream static pressure
        rho2_rho1:  float, ratio of downstream/upstream density
        T2_T1:      float, ratio of downstream/upstream static temperature
        deltasoR:   float, 
        P02_P01:    float, ratio of downstream/upstream total pressure
        beta:       float, shock angle

    """
    
    # rootsolve beta-theta-mach relation to get shock angle
    beta = btm(M_1, g, theta)

    # calculate mach component normal to shock
    M_1n = M_1 * math.sin(beta)

    # use normal shock relations on the normal component of the upstream mach
    [M2n, P2_P1, rho2_rho1, T2_T1, deltasoR, P02_P01] = normal_shock(M_1n, g)

    # compute downstream total mach from the shock angle and normal component 
    M2 = M2n / math.sin(beta - theta)

    return M2, P2_P1, rho2_rho1, T2_T1, deltasoR, P02_P01, beta



def btm(M_1, g, theta):
    """ 
    Performs the rootsolve/residual-minimization numerical procedure to solve the 
    beta-theta-mach relation for oblique shocks.

    Inputs
        M_1:        float, upstream mach number
        g:          float, gamma, ratio of specific heats
        theta:      float, turning angle of the 2D wedge flow

    Returns
        beta:       float, shock angle

    Sources
        -Anderson, Fundamentals of Dynamics p. 624
    """

    # BTM RESIDUAL:
    fun = lambda beta: abs(math.tan(theta) - (2 * math.tan(beta) ** (-1) * (M_1 ** 2 * math.sin(beta) ** 2 - 1) / (
            M_1 ** 2 * (g + math.cos(2 * beta)) + 2)))

    # MINIMIZE BTM RESIDUAL:
    beta_oblique = scipy.optimize.minimize_scalar(fun, bounds=(theta, math.pi / 2 - 1e-6), method='bounded')

    # Check if M = 1. If equals one( or near 1), weird results happen.
    if (M_1 == 1):
        # Set beta to normal shock solution, pi/2
        beta = math.pi / 2

    # if exitflag == 1, "Equation solved. First-order optimality is small.
    elif (beta_oblique.success == 1 and beta_oblique.x < math.pi / 2):
        # Use oblique solution
        beta = beta_oblique.x

    # If exitflag == 0, Equation not solved. See OptimizeResult
    else:
        # Set beta to normal shock solution, pi / 2
        raise Exception("Unknown exitflag or other error thrown using fsolve- check normal_oblique_shock")

    return beta



def conical_shock(M_1, g, delta_c, N=100, deltaTol=1e-2):
    """
    Conical Shock Solver

    Not yet implemented
    
    """

    # mach angle
    mu_1 = math.asin(1 / M_1)  # MACH ANGLE

   
    # ========================= PREDICTOR STEP =========================

    # predictor
    theta = delta_c + mu_1 / 2

    # integration parameters
    M_1_star = ((g + 1) / 2 * M_1 ** 2 / (1 + (g - 1) / 2 * M_1 ** 2)) ** (1 / 2)
    v_psi_bar_s = -M_1_star * math.sin(theta) * (
            1 - (2 / (g + 1) * (M_1 ** 2 * math.sin(theta) ** 2 - 1) / (M_1 ** 2 * math.sin(theta) ** 2)))
    v_r_bar_s = M_1_star * math.cos(theta)
    psi_span = [theta, 1e-2]
    y0 = [v_r_bar_s, v_psi_bar_s]

    # RK4 SETUP FUNCTIONS:
    def int_eqns(psi, y, g=1.4):
        # psi: ANGLE CCW FROM FREESTREAM DIRECTION
        # y[0]: v_r_bar
        # y[1]: v_psi_bar
        a_astar_sq = (g + 1) / 2 - (g - 1) / 2 * (y[0] ** 2 + y[1] ** 2)  # (a/a*)**2
        dy = [0, 0]  # INIT
        dy[0] = y[1]
        dy[1] = a_astar_sq * (y[0] + y[1] * 1 / math.tan(psi)) / (y[1] ** 2 - a_astar_sq) - y[0]
        return dy

    def cone_surface(t, y, g):
        return y[1]

    cone_surface.terminal = True

    # INTEGRATION
    sol = scipy.integrate.solve_ivp(int_eqns, psi_span, y0, method='RK45', dense_output=False, events=cone_surface,
                                    args=(g,), max_step=(theta - delta_c) / N)

    delta = sol.t[-1]  # UPDATE CONE ANGLE FOUND

    
    # ========================= MULTI-CORRECTOR STEP =========================

    itrCorrect = 0  # CORRECTOR ITERATION COUNTER
    x = [0, theta]  # STORE LAST TWO THETA (SHOCK ANGLE) VALUES
    y = [0, delta - delta_c]  # STORE LAST TWO DELTA (CONE ANGLE) RESIDUALS



    while True:
        # CORRECTOR:
        itrCorrect = itrCorrect + 1  # INCREMENT CORRECTOR ITERATION COUNTER
        if itrCorrect == 1:
            theta = theta + (delta_c - delta)  # FIRST CORRECTOR
        else:
            theta = x[1] - y[1] * (x[1] - x[0]) / (y[1] - y[0])  # SECANT ROOTFINDING METHOD

        # INTEGRATION PARAMETERS:
        M_1_star = ((g + 1) / 2 * M_1 ** 2 / (1 + (g - 1) / 2 * M_1 ** 2)) ** (1 / 2)
        v_psi_bar_s = -M_1_star * math.sin(theta) * (
                1 - (2 / (g + 1) * (M_1 ** 2 * math.sin(theta) ** 2 - 1) / (M_1 ** 2 * math.sin(theta) ** 2)))
        v_r_bar_s = M_1_star * math.cos(theta)
        psi_span = [theta, 1e-2]
        y0 = [v_r_bar_s, v_psi_bar_s]

        # INTEGRATION:
        sol = scipy.integrate.solve_ivp(int_eqns, psi_span, y0, method='RK45', dense_output=False, events=cone_surface,
                                        args=(g,), max_step=(theta - delta_c) / N)

        delta = sol.t[-1]  # UPDATE CONE ANGLE FOUND

        # SHUFFLE LAST TWO VALUES:
        x[0] = x[1]
        x[1] = theta
        y[0] = y[1]
        y[1] = delta - delta_c

        # TOLERANCE CHECK:
        if abs(delta - delta_c) / delta_c < deltaTol:
            # print("Corrector Iterations: %d" % itrCorrect)
            break
        elif itrCorrect == 10:
            print("WARNING: Maximum Number of Corrector Iterations Reached: %d" % itrCorrect)
            break

    # COMPUTE PROPERTIES IMMEDIATELY AFTER SHOCK:
    M_1n = M_1 * math.sin(theta)
    # M_1t = M_1 * math.cos(theta)
    P02_P01 = normal_shock(M_1n, g)[5]
    # P2_P1 = 1+2*g/(g+1)*(M_1**2*math.sin(theta)**2-1)
    # rho2_rho1 = (1-2/(g+1)*(M_1**2*math.sin(theta)**2-1)/(M_1**2*math.sin(theta)**2))**(-1)
    # T2_T1 = 1+2*(g-1)/(g+1)**2*(M_1**2*math.sin(theta)**2-1)/(M_1**2*math.sin(theta)**2)*(g*M_1**2*math.sin(theta)+1)
    # M_2 = math.sqrt(M_1t**2*(T2_T1)**(-1)+M_2n**2)
    # P02_P01 = P2_P1*((1+(g-1)/2*M_2**2)/(1+(g-1)/2*M_1**2))**(g/(g-1))

    # COMPUTE PROPERTIES AT EACH INTEGRATION POINT:
    M_star = np.power(np.power(sol.y[0, :], 2) + np.power(sol.y[1, :], 2), 1 / 2)
    M = np.power(np.divide(2 / (g + 1) * np.power(M_star, 2), (1 - (g - 1) / (g + 1) * np.power(M_star, 2))), 1 / 2)
    P_P1 = P02_P01 * np.power(np.divide((1 + (g - 1) / 2 * M_1 ** 2), (1 + (g - 1) / 2 * np.power(M, 2))),
                              (g / (g - 1)))
    T_T1 = np.divide((1 + (g - 1) / 2 * M_1 ** 2), (1 + (g - 1) / 2 * np.power(M, 2)))
    rho_rho1 = np.divide(P_P1, T_T1)

    c_p_c = (P_P1[-1] - 1) / (1 / 2 * g * M_1 ** 2)  # PRESSURE COEFFICIENT ON CONE SURFACE

    return sol, theta, M, P_P1, T_T1, rho_rho1, c_p_c, P02_P01