import os
import sys
import filecmp
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import animation



'''---------------------------------------------------------------------------
This file contains a good few kinda boilerplate plots I got tired of making over and over.

This isn't as useful now that I added the Post GUI, but I am keeping it here 
nonetheless, because I really hate making plots from scratch in python.

I am not going to go through the effort of cleaning it up though

plot_results basically calls most of the plots you'd want below. Just use that one.
---------------------------------------------------------------------------'''


def plot_results(Sim):
    """
    Plotting function for a few of the main "boilerplate" plots you'd want after running a sim
    """

    #Wall Temp v Time
    plot_wall_temps(Sim)

    #Plot Wall Temperature Distribution when y=0.0 hits its max temp
    plot_wall_temp_dist_at_maxtemp(Sim, sim_name="Sim")

    # Heat Fluxes (conv, rad, tot)
    plot_heat_fluxes(Sim)

    # Heat Transfer Coeff and BL State
    plot_h_blstate(Sim)

    #Trajectory
    plot_trajectory(Sim)

    #Total, Total Edge, Recovery Temps
    plot_air_temperatures(Sim)

    plt.show()

    


    

def plot_wall_temps(Sim, sim_name="Sim"):
    #Temperature vs Time
   
    plt.figure()

    plt.plot(Sim.t_vec, Sim.wall_temps[0,:],      label = sim_name + " - y=0.0 Wall",  color='red') 
    plt.plot(Sim.t_vec, Sim.wall_temps[-1,:],     label = sim_name + " - y=max(y) Wall", color='cyan')  

    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("Temeperature, K")
    plt.title("Temperature vs. Time Trace")


def plot_wall_temp_dist_at_maxtemp(Sim, sim_name="Sim"):
    """ Get the time index where the first element hits the max temp, and plot the 
    through-wall temperature distribution"""

    # Get index where external wall is at its max temp
    maxtemp_Idx = np.argmax( Sim.wall_temps[0,:] ) 


    plt.figure()

    plt.plot(Sim.y_coords, Sim.wall_temps[:,maxtemp_Idx],      label = sim_name + "Temperature Distribution",  color='red') 

    plt.legend()
    plt.xlabel("Through-Wall Coordinate (m)")
    plt.ylabel("Temeperature, K")
    plt.title("Through-Wall Temperature Distribution Sampled at Max Surface Temp")





def plot_heat_fluxes(Sim, sim_name="Sim"):
    #Heat Fluxes w/ Time

    plt.figure()

    plt.plot(Sim.t_vec, Sim.q_conv,    label ="q_conv",  color='red') 
    plt.plot(Sim.t_vec, Sim.q_rad,     label = "q_rad",  color='cyan')  
    plt.plot(Sim.t_vec, Sim.q_net,     label = "q_net", color='mediumpurple')  

    plt.legend()
    plt.xlabel("Time (s)")
    plt.ylabel("q, [W?]")
    plt.title("Heat Fluxes vs. Time")



def plot_h_blstate(Sim, sim_name="Sim"):
    #Plot Heat Transfer Coeff and BL state

    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Heat Transfer Coeff', color=color)
    ax1.plot(Sim.t_vec, Sim.h_coeff, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('BL State (1 if Turb)', color=color)
    ax2.plot(Sim.t_vec, Sim.bl_state, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title("h coeff and BL State v. Time")
    fig.tight_layout()




def plot_trajectory(Sim, sim_name="Sim"):
    #Plot Mach, Alt, Re, qBar vs. time

    ##### Mach and Altitude
    #plt.figure()
    fig, ax1 = plt.subplots()

    color = 'tab:blue'
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Altitude (ft)', color=color)
    ax1.plot(Sim.t_vec, Sim.alt, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:red'
    ax2.set_ylabel('Mach', color=color)
    ax2.plot(Sim.t_vec, Sim.mach, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title("Mach and Alt v. Time")
    fig.tight_layout()


    ##### Reynolds and qBar
    #plt.figure()
    fig2, ax3 = plt.subplots()

    color = 'tab:blue'
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Reynolds No.', color=color)
    ax3.plot(Sim.t_vec, Sim.Re_inf, color=color)
    ax3.tick_params(axis='y', labelcolor=color)

    ax4 = ax3.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:red'
    ax4.set_ylabel('Dynamic Pressure (Pa?)', color=color)
    ax4.plot(Sim.t_vec, Sim.qbar_inf, color=color)
    ax4.tick_params(axis='y', labelcolor=color)

    plt.title("Re and qBar v. Time")
    fig.tight_layout()

    


def plot_air_temperatures(Sim, sim_name="Sim"):
    """ Various Air temperatures vs. time"""

    #First Plot: Free-Stream Temp, Edge Temperature
    plt.figure()

    # Freestream Temp
    plt.plot(Sim.t_vec, Sim.T_inf, label="T_inf", color="blue")
    # Edge Temp
    plt.plot(Sim.t_vec, Sim.T_e, label="T_e", color="salmon")

    plt.xlabel('Time (s)')
    plt.ylabel('Temp (K)')
    plt.title("Static Temps v. Time")
    plt.legend()
    plt.tight_layout()



    #Second Plot: Total Temp, Total Temp at Edge, Recovery Temp
    plt.figure()

    # Total Temp
    plt.plot(Sim.t_vec, Sim.T_t, label="T_tot", color="red")
    # Edge Total Temp
    plt.plot(Sim.t_vec, Sim.T_te, label="T_tot,edge", color="salmon")
    # Recovery Temp
    plt.plot(Sim.t_vec, Sim.T_recovery, label="T_recovery", color="blue")

    plt.xlabel('Time (s)')
    plt.ylabel('Temp (K)')
    plt.title("Flow Total Temps v. Time")
    plt.legend()
    plt.tight_layout()



