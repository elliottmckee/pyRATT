import sys
import os
import itertools
import pickle
import time
from pathlib import Path

import pandas as pd
import PySimpleGUI as sg

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt 

sys.path.append(os.path.dirname(os.getcwd())) # This is another goofy workaround because I am bad at modules/imports

from stata_mater.src.materials_solid import MATERIALS_DICT
from src.obj_simulation import Thermal_Sim_1D
from src.obj_flightprofile import FlightProfile
from src.obj_wallcomponents import WallStack
from src.materials_gas import AirModel


"""
Notes:
-I was having issues with the plots displaying before changing to TkAgg matplotlib backend


I started out by using Dr Adam Luke Baskerville's work as a reference, here: 
    https://adambaskerville.github.io/posts/PythonGUIPlotter/

As well as the examples given in PySimpleGui:
    https://www.pysimplegui.org/en/latest/cookbook/

"""


def gui_run_simulation(values):
    """ Takes in GUI values object, creates, runs, and outputs/pickles a Simulation """
    
    print("Note: I should probably add some input validation in gui_run_simulation()")
    print("Note: Also add initial temperature setting from STDatm if not specified. Currently defaults to 290K")

    #Alias and convert variables 
    #Im kinda just wrapping things in additional brackets because things are getting treated weirdly
    inFiles         = [values["_INFILES_"]]
    outFiles        = [values["_OUTFILES_"]]
    n_nodes         = [int(i) for i in [values["-n_nodes-"]]]
    t_step          = [float(i) for i in [values["-t_step-"]]]
    try:
        t_end       = [float(i) for i in [values["-t_end-"]]]
    except:
        print("Note: No t_end override enabled, or invalid specification.")
        t_end       = [None for i in [values["-t_end-"]]]
    
    x_location      = [float(i) for i in [values["-x_location-"]]]
    wallmaterial    = [values["-wallmaterial-"]]
    wallthick       = [float(i) for i in [values["-wallthick-"]]]
    deflection      = [float(i) for i in [values["-deflection-"]]]
    aerosurf        = [values["-aerosurf_type-"]]         
    
    
    
    #For Each input RAS Simulation file
    for i, file in enumerate(inFiles):
    
        print(f"Initializing Simulation{i+1}: ")

        #Define Aerosurface Object
        AeroSurf = WallStack(materials=wallmaterial[i], thicknesses=wallthick[i], node_counts = n_nodes[i])

        #Get RAS Flight Data
        Flight    = FlightProfile( inFiles[i] )

        # Get Relevant boundary conditions for the different Aerosurface Types
        if aerosurf[i] == "Nosecone":
            thermal_bcs = ["q_in_aerothermal","adiabatic"]
        elif aerosurf[i] == "Fin":
            thermal_bcs = ["q_in_aerothermal","q_in_aerothermal"]
        else: raise Exception("Error in Aerosurface/BC specification")
        
        #Initialized Simulation
        MySimulation= Thermal_Sim_1D(AeroSurf, Flight, AirModel(),
                                    x_location              = x_location[i], 
                                    deflection_angle_deg    = deflection[i], 
                                    t_step                  = t_step[i],
                                    t_end                   = t_end[i],
                                    boundary_layer_model    = 'transition',
                                    wall_thermal_bcs        = thermal_bcs)


        #Time Entire Simulation
        start = time.time()

        #Run Simulation
        print("Running Simulation...")
        MySimulation.run()

        end = time.time()
        print("Time to Simulate: ", end - start)

        #Export Files
        MySimulation.export_data_to_csv(out_filename = outFiles[i]+".csv")
        #Pickle output to outFile
        with open(outFiles[i]+".sim", "wb") as f: pickle.dump(MySimulation, f)





############################################################################################################
############################################### MAIN #######################################################
############################################################################################################

##### Theme Settings (most important part)
text_HEX    = '#bd93f9'
input_HEX   = '#44475a'
back_HEX    = '#282A36'

custom_theme = {'BACKGROUND': back_HEX, 
                'TEXT': text_HEX, 
                'INPUT': input_HEX, 
                'TEXT_INPUT': "#8be9fd", 
                'SCROLL': input_HEX, 
                'BUTTON': (back_HEX, text_HEX), 
                'PROGRESS': (text_HEX, input_HEX), 
                'BORDER': 1, 
                'SLIDER_DEPTH': 0, 
                'PROGRESS_DEPTH': 0}
# Add your dictionary to the PySimpleGUI themes
sg.theme_add_new('customTheme', custom_theme)
# Switch your theme to use the newly added one. You can add spaces to make it more readable
sg.theme('customTheme')
# Call a popup to show what the theme looks like
#sg.popup_get_text('This how the MyNewTheme custom theme looks') 



##### Large Blocks of Text

main_instructions = """Instructions:

1) Use the browser below to point to a RASAeroII (can add support for other formats, but RAS likely most useful) flight sim .CSV export file. 
    - To generate this output data file from RASAeroII Sim:
        - From the Simulation window within RASAeroII, hit "View Data," and in the plotting window, in the top left, hit file->export->CSV. The time resolution 
        doesn't matter a whole lot, it all gets interpolated anyway. 0.10 seconds is probably what I would reccomend, as additional resolution is likely insignificant, and just makes files bigger.
        - I reccomend putting that export .csv somewhere in pyRATT main directory, so it is easy to find.
2) Input all the required inputs below. See individual items for descriptions 
3) Hit "Run Simulation"
    - The Simulation *should* run, and you can check by looking at your terminal. It will output things like "SIMULATION PROGRESS..." and will print the timestep it is at, every ~5 seconds.
        - Keep an eye out for any warnings/error. However, not all of them will be critical- I sometimes use print statements as TODO's and may have left a couple in lol.   
4) Once the Simulation is complete, close the window and either:
    - run gui_post from your terminal, and load in the .sim file you just created to plot and view results quickly.
    - use the .csv output data to manipulate the output data as you please

- I created this GUI to make this a bit more user friendly, but that obviously comes at the cost of control. There are more things you can tune and play with if running from an actual standalone 
    script (see examples), but I made this in the pursuit of accessibility/usability. I will try and keep the inputs as minimal as possible here, and put reccomended default values where applicable.
- Some of the functionality that cannot be accessed through this gui include: multi-material walls, shock-type selection (normal/default:oblique/conical), and more.  
- [NOT TESTED FULLY] Multiple File Implementation: I want to be able to point to multiple RAS files, for example, if you want to compare thermal loading under different motor configurations. 
- As always, feel free to reach out to me if you have any questions/issues. 
    email: elliott.mckee@proton.me
    github: elliottmckee"""

timespace_instructions = """- Background: This uses a 1D Finite Difference model for thermal conduction, which is integrated forward in time to get the through-wall temperature distribution as a function of time. 
    - Long story short, it requires discretizations of both the wall structure (number of discrete elements in the through-wall direction), and time (timestep). 
- Solver Instability: Due to unfortunate consequences of math, discretization, etc., there are criterion that need to be satisfied for the solver to be stable and not blow up. A warning will be 
  thrown and the current simulation might break if such instability occurs, but the data will be junk regardless lol
    *** If you are running into solver stability issues, try decreasing the number of wall nodes, and/or decreasing the simulation timestep. ***"""

aerosurf_type_instructions = """- This selects what type of physical geometry you're simulating. Only Nosecones and Fins supported right now. """

time_instructions = """- Smaller timesteps are more accurate, theoretically, but will take longer to simulate. Values that are too high will cause instabilities in the solver.
    - Values in the ballpark of 0.001-0.005 seconds are what i've used, but this depends pretty strongly on wall nodes/spacing and total wall thickness."""

wallnode_instructions = """- Number of nodes that the wall is divided into, in the through-wall direction. More nodes == more resolution, but longer sim times, and possibly instability.
    - Very roughly, I tend to keep this around 15-25ish, but play with this as needed."""

simulation_endtime_instructions = """- By default, the simulation will go until the end of the trajectory file. Use this if you want to cut the simulation short (i.e. only simulate ascent)"""

along_body_instructions = """- This should *ideally* be the boundary layer running length of the point you are looking to analyze. In other words, the length from the stagnation point to 
    the point you are looking to analyze, as measured along the body (think of it as putting a string between these two points and measuring its length).
    - However, in most cases, because nosecone and fin chamfer angles are small, you can just use axial coordinates/distances and get close enough.
        - For Nosecones, this distance is referenced from the nosecone tip. i.e. a value of 0.2 is 0.2 meters downstream of the nosecone tip.
        - For Fins, this is the distance (axially) from the fin leading edge. i.e. a value of 0.2 is 0.2 meters downstream of the fin leading edge.
    """


wall_mat_instructions = """- Uses to set wall material properties. If you need to add another material not shown here, simply add an entry to the material database in src/materials_solid.py"""

wall_thickness_instructions = """- Total wall thickness at the point you're looking to analyze"""

deflection_angle_instructions = """- Deflection angle of the flow. For Nosecones, use the half-angle. For Fins, use the chamfer angle."""


# Define Layout

layout = [
            [sg.Text('-'  * 200, size=(200, 1))], #--------------------------
            [sg.Text('------ pyRATT GUI_RUN -------', size=(150, 1))],
            [sg.Text('-'  * 200, size=(200, 1))], #--------------------------
            
            [sg.Text(main_instructions)],
            
            [sg.Text('-'  * 150, size=(150, 1))], #--------------------------

              
            [sg.Text('Input RASAeroII Flight Simulation CSV: '), sg.Input(key='_INFILES_', enable_events=True), sg.FilesBrowse()],

            #[sg.Text('                                         Input File Loaded:'), sg.Text(size=(200,1), key='-loadedfiles-')], 


            [sg.Text("Sim Output Filename:                   "), sg.InputText("mysimulation", s=25, key='_OUTFILES_'), sg.Text("(defaults to saving in main directory. automatically appends .sim to the pickled sim object, and .csv for data output file)")], 
            #[sg.InputText("mysimulation.sim", s=25, key='_OUTFILES_')],
            #(defaults to saving in main directory. extension/location doesn't really matter though):

            ### SIMULATION CONFIGURATION ###
            [sg.Text('-'  * 200, size=(200, 1))], #--------------------------
            [sg.Text('Simulation Configuration: ')],
            [sg.Text(timespace_instructions)],

            # Simulation Geometry
            [sg.Text('Aerosurface Type:'), sg.InputCombo(values=["Nosecone","Fin"], default_value='Nosecone', size=(20, 1), key=f'-aerosurf_type-'), sg.Text(aerosurf_type_instructions)],
            

            #Wall Node Count
            [sg.Text('Node Count (integer): ') , sg.InputText("20", s=8, key='-n_nodes-'), sg.Text(wallnode_instructions)],

            #Timestep Size
            [sg.Text('Timestep Size (s): ') , sg.InputText("0.001", s=8, key='-t_step-'), sg.Text(time_instructions)],

            #Simulation End Time Override
            [sg.Text('Simulation End Time (s): ') , sg.InputText("optional", s=8, key='-t_end-'), sg.Text(simulation_endtime_instructions) ],



            ### SIM CONFIG PARAMETERS ###
            #[sg.Text('-'  * 150, size=(150, 1))], #--------------------------
            #[sg.Text('Simulation Configuration: ')],

            [sg.Text('Along-body location to simulate (m):'), sg.InputText("0.0", size=(8, 1), key=f'-x_location-'), sg.Text(along_body_instructions)],
            ######


            
            ### PHYSICAL ROCKET PARAMETERS ###
            [sg.Text('-'  * 200, size=(200, 1))], #--------------------------
            [sg.Text('Rocket Physical Parameters: ')],

            # Wall Material
            [sg.Text('Wall Material:'), sg.InputCombo(values=list(MATERIALS_DICT.keys()), default_value='', size=(20, 1), key=f'-wallmaterial-'), sg.Text(wall_mat_instructions)],
            
            # Wall Thickness
            [sg.Text('Wall Thickness (m):'), sg.InputText("0.0", size=(8, 1), key=f'-wallthick-'), sg.Text(wall_thickness_instructions)],

            # Deflection Angle
            [sg.Text('Deflection Angle (deg):'), sg.InputText("0.0", size=(8, 1), key=f'-deflection-'), sg.Text(deflection_angle_instructions)], 
            ######
            

            ######
            [sg.Text('-'  * 200, size=(200, 1))], #--------------------------
            [sg.Button('Run Simulation'), sg.Text(' '  * 130, size=(130, 1))],
         ]






# Define Plot Control Window
window = sg.Window('pyRATT gui_run', layout)

# Generate persistent plot control window 
while True:

    event, values = window.read()

    #Quit
    if event == sg.WIN_CLOSED:
        window.close()
        break

    # New File Load Event
    elif event == '_INFILES_':
        
        #Split Filenames
        ras_files = values['_INFILES_'].split(";")

        #Update window with loaded files
        #window[f'-loadedfiles-'].update(value=', '.join( ras_files))

    
    # Plot Event
    elif event == 'Run Simulation':
        gui_run_simulation(values)
    




