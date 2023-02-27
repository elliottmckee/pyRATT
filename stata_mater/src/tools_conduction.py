import numpy as np



def get_new_wall_temps(Sim, i):
    """
    Calculate the temperature rates of change of each of the wall elements 
    and use these to propagate wall temperature forward in time

    Updates:
    --------
        - Sim.wall_temps[:,i+1], temps at next timestep
    """

    #Aliases
    Tvec_wall = Sim.wall_temps[:,i]
    q_net_in = Sim.q_net[i]


    #Initialize Zeros Vector
    dT_dt = np.zeros( (len(Sim.Aerosurface.elements),),  dtype=float)

    #For all of the Elements in the Aerosurface Stack
    for j, e in enumerate(Sim.Aerosurface.elements):

        # Outermost or Hot-wall Element
        if j == 0:

            #Parse Boundary Condition Types
            if Sim.wall_thermal_bcs[0] == "q_in_aerothermal":
                dT_dt[j] = 1 / (e.dy*e.rho*e.cp) * (q_net_in + e.k*(Tvec_wall[1] - Tvec_wall[0]) / e.dy)
            else:
                raise Exception('Only "q_in_aerothermal" type supported for first B.C.') 

        # Inner Wall
        elif j == len(Sim.Aerosurface.elements)-1:
            

            #Parse Boundary Condition Types
            if Sim.wall_thermal_bcs[1] == "q_in_aerothermal":
                dT_dt[j] = 1 / (e.dy*e.rho*e.cp) * (q_net_in + e.k*(Tvec_wall[j-1] - Tvec_wall[j]) / e.dy)
            elif Sim.wall_thermal_bcs[1] == "adiabatic":
                # No heat-flux. Accomplish by forcing the "internal" (i.e. inside the nosecone) temperature
                # to be in equilibrium with inner-most wall element 
                T_internal = Tvec_wall[-1] # Inner Wall BC

                dT_dt[j] = e.k / (e.rho*e.cp* e.dy**2) * (T_internal - 2*Tvec_wall[j] + Tvec_wall[j-1])
            else:
                raise Exception('Unsupported B.C type specified for second B.C.') 


        # #Middle Elements
        else:
            dT_dt[j] = e.k/(e.rho*e.cp*e.dy**2) * (Tvec_wall[j+1] - 2*Tvec_wall[j] + Tvec_wall[j-1])


    # Update Temperatures
    Sim.wall_temps[:,i+1] = Tvec_wall + dT_dt*Sim.t_step




def stability_criterion_check(Sim, i):
    """
    Stability criterion for the numerical stability of the solver. Will print warning to console
    if this criterion is not satisfied

    In my past experience this is a pretty accurate marker of when your timestep is too big,
    or your element size is too small.  

    Notes:
        TODO: odifications to Stability Criterion Check Needed when Ablative is added
    """

    """ Carryover code from Matlab, for future work
    If No Ablative, Structure is exposed
    dy = SurfE.dy
    rho_s = SurfE.rho
    Cp_s = SurfE.cp
    k_s = SurfE.k

    If Ablative is exposed, more annoying to deal with but yeah
    else:
        dy = Abl.deltaVec(i)/(Sim.N - 1);
        rho_s = Abl.rhoVec_tot(1,i);
        Cp_s  = interp1(Abl.cpLUTab.Var1,Abl.cpLUTab.Var2, Abl.TVec(1,i), 'linear', 'extrap');
        k_s = interp1(Abl.kLUTab.Var1,Abl.kLUTab.Var2, Abl.TVec(1,i),'linear', 'extrap');
    """

    #Aliasing
    SurfE   = Sim.Aerosurface.elements[0]
    h       = Sim.h_coeff[i] 
    dt      = Sim.t_step
    
    # Perform Stability Check 
    F_0 = (SurfE.k * dt) / (SurfE.rho * SurfE.cp * SurfE.dy**2)
    Bi = (h * SurfE.dy) / SurfE.k

    if ( F_0*(1+Bi) > .5):
        print('~~WARNING~~: Stability Criterion not met. Consider decreasing timestep or number of wall nodes)')

