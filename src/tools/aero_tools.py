import math
import scipy



def total_temperature(T, M, gam):
    #Just Returns the Total Temperature
    return T * (1 + M**2 * (gam-1)/2) 


# NORMAL SHOCK RELATIONS (FROM ASEN 3111)
def shock_calc( M1, g ):

    M2n = math.sqrt((1 + (g - 1) / 2 * M1 ** 2) / (g * M1 ** 2 - (g - 1) / 2))
    p2op1 = 1 + 2 * g / (g + 1) * (M1 ** 2 - 1)
    rho2orho1 = (g + 1) * M1 ** 2 / (2 + (g - 1) * M1 ** 2)
    t2ot1 = p2op1 / rho2orho1
    deltasoR = g / (g - 1) * math.log(t2ot1) - math.log(p2op1)
    p02op01 = math.exp(-deltasoR)

    return M2n, p2op1, rho2orho1, t2ot1, deltasoR, p02op01

# OBLIQUE SHOCK RELATIONS
def oblique_shock( M1, g, theta ):

    # ROOTSOLVE FOR SHOCK ANGLE:
    beta = btm( M1, g, theta )

    # CALCULATE VELOCITY NORMAL TO SHOCK:
    M1n = M1 * math.sin(beta)

    # CALL NORMAL SHOCK RELATIONS:
    [M2n, p2op1, rho2orho1, t2ot1, deltasoR, p02op01] = shock_calc( M1n, g )

    # COMPUTE DOWNSTREAM MACH NUMBER GIVEN SHOCK ANGLE AND NORMAL VELOCITY COMPONENT:
    M2 = M2n/math.sin(beta-theta)

    return M2, p2op1, rho2orho1, t2ot1, deltasoR, p02op01, beta


# BETA-THETA-MACH RELATION (ANDERSON, FUNDAMENTALS OF DYNAMICS p.624)
def btm( M1, g, theta ):
    # BTM RESIDUAL:
    fun = lambda beta: abs(math.tan(theta) - (2*math.tan(beta)**(-1) * (M1 ** 2 * math.sin(beta) ** 2 - 1) / (M1 ** 2 * (g + math.cos(2 * beta)) + 2)))

    # MINIMIZE BTM RESIDUAL:
    beta_oblique = scipy.optimize.minimize_scalar(fun, bounds=(theta, math.pi/2-1e-6), method='bounded')

    # Check if M = 1. If equals one( or near 1), weird results happen.
    if (M1 == 1):
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
