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
            T_internal = initial_temp # No Temp change for now
            dT_dt[i] = e.k / (e.rho*e.cp* e.dy**2) * (T_internal - 2*Tvec_wall[i] + Tvec_wall[i-1])

        # #Middle Elements
        else:
            dT_dt[i] = e.k/(e.rho*e.cp*e.dy**2) * (Tvec_wall[i+1] - 2*Tvec_wall[i] + Tvec_wall[i-1])

    return dT_dt


  
    










    





def stability_criterion_check():
    pass 


