import math
import scipy
import numpy as np


from math import pow, sqrt, log10

from ambiance import Atmosphere



def get_freestream(Sim, i):

     #Get Current Free-stream props
    atm_inf = Atmosphere([Sim.alt[i]])
    
    # Update Free-Stream State values to time step i in Sim
    Sim.p_inf[i]    = atm_inf.pressure
    Sim.T_inf[i]    = atm_inf.temperature
    Sim.rho_inf[i]  = atm_inf.density
    Sim.u_inf[i]    = sqrt(Sim.AirModel.gam * Sim.AirModel.R * atm_inf.temperature) * Sim.mach[i]











def total_temperature(T, M, gam):
    # Just Returns the Total Temperature
    return T * (1 + M ** 2 * (gam - 1) / 2)


# NORMAL SHOCK RELATIONS (FROM ASEN 3111)
def shock_calc(M_1, g):
    M2n = math.sqrt((1 + (g - 1) / 2 * M_1 ** 2) / (g * M_1 ** 2 - (g - 1) / 2))
    P2_P1 = 1 + 2 * g / (g + 1) * (M_1 ** 2 - 1)
    rho2_rho1 = (g + 1) * M_1 ** 2 / (2 + (g - 1) * M_1 ** 2)
    T2_T1 = P2_P1 / rho2_rho1
    deltasoR = g / (g - 1) * math.log(T2_T1) - math.log(P2_P1)
    P02_P01 = math.exp(-deltasoR)

    return M2n, P2_P1, rho2_rho1, T2_T1, deltasoR, P02_P01


# OBLIQUE SHOCK RELATIONS
def oblique_shock(M_1, g, theta):
    # ROOTSOLVE FOR SHOCK ANGLE:
    beta = btm(M_1, g, theta)

    # CALCULATE VELOCITY NORMAL TO SHOCK:
    M_1n = M_1 * math.sin(beta)

    # CALL NORMAL SHOCK RELATIONS:
    [M2n, P2_P1, rho2_rho1, T2_T1, deltasoR, P02_P01] = shock_calc(M_1n, g)

    # COMPUTE DOWNSTREAM MACH NUMBER GIVEN SHOCK ANGLE AND NORMAL VELOCITY COMPONENT:
    M2 = M2n / math.sin(beta - theta)

    return M2, P2_P1, rho2_rho1, T2_T1, deltasoR, P02_P01, beta


# BETA-THETA-MACH RELATION (ANDERSON, FUNDAMENTALS OF DYNAMICS p.624)
def btm(M_1, g, theta):
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


# CONICAL SHOCK CALCULATOR
def conical_shock(M_1, delta_c, g, N=100, deltaTol=1e-2):
    mu_1 = math.asin(1 / M_1)  # MACH ANGLE

    # ========================= PREDICTOR STEP =========================

    theta = delta_c + mu_1 / 2  # PREDICTOR

    # INTEGRATION PARAMETERS:
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
    P02_P01 = shock_calc(M_1n, g)[5]
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