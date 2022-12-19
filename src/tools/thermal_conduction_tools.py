import numpy as np



def get_new_wall_temps(Tvec_wall, q_net_in, Sim):

    #Get Temperature Rates of Change
    dT_dt = wall_temp_change(Tvec_wall, q_net_in, Sim.Aerosurface, Sim.initial_temp)

    # Update Temperatures
    return Tvec_wall + dT_dt*Sim.t_step



def wall_temp_change(Tvec_wall, q_net_in, Aerosurface, initial_temp):
    
    #Initialize Zeros Vector
    dT_dt = np.zeros( (len(Aerosurface.elements),),  dtype=float)

    #For all of the Elements in the Aerosurface Stack
    for i, e in enumerate(Aerosurface.elements):

        # Outermost or Hot-wall Element
        if i == 0:
            dT_dt[i] = 1 / (e.dy*e.rho*e.cp) * (q_net_in + e.k*(Tvec_wall[1] - Tvec_wall[0]) / e.dy)

        # Inner Wall
        elif i == len(Aerosurface.elements)-1:
            T_internal = Tvec_wall[-1] # Inner Wall BC
            dT_dt[i] = e.k / (e.rho*e.cp* e.dy**2) * (T_internal - 2*Tvec_wall[i] + Tvec_wall[i-1])

        # #Middle Elements
        else:
            dT_dt[i] = e.k/(e.rho*e.cp*e.dy**2) * (Tvec_wall[i+1] - 2*Tvec_wall[i] + Tvec_wall[i-1])

    return dT_dt



def stability_criterion_check(SurfE, h, dt):
    # From Ulsu-Simsek 
    # This is a stability criterion for the numerical stability of the solver
    # In my past experience this is a pretty good marker of when your timestep is too big. 

    #If No Ablative, Structure is exposed
    # dy = SurfE.dy
    # rho_s = SurfE.rho
    # Cp_s = SurfE.cp
    # k_s = SurfE.k

    #If Ablative is exposed, more annoying to deal with but yeah
    # else:
    #     dy = Abl.deltaVec(i)/(Sim.N - 1);
    #     rho_s = Abl.rhoVec_tot(1,i);
    #     Cp_s  = interp1(Abl.cpLUTab.Var1,Abl.cpLUTab.Var2, Abl.TVec(1,i), 'linear', 'extrap');
    #     k_s = interp1(Abl.kLUTab.Var1,Abl.kLUTab.Var2, Abl.TVec(1,i),'linear', 'extrap');
        
    # Perform Stability Check 
    F_0 = (SurfE.k * dt) / (SurfE.rho * SurfE.cp * SurfE.dy**2)
    Bi = (h * SurfE.dy) / SurfE.k

    if ( F_0*(1+Bi) > .5):
        print('Warning: Stability Criterion not met. Consider increasing time resolution (smaller time step) or \n decreasing the spatial wall resolution (decrease the number of wall nodes, Sim.N)')

