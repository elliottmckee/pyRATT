import sys
import os
import itertools
import pickle
import pandas as pd
import PySimpleGUI as sg


from pathlib import Path



import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt 

sys.path.append(os.path.dirname(os.getcwd())) # This is another goofy workaround because I am bad at modules/imports


"""
I really hate making plots in Python, so I made a GUI tool to handle what I need. It kinda sucks,
but it helps with quick data visualization, and also lets you see what variables you have access to.

This definitely isn't perfect, and will break if you do things wrong, but yeah. Hope it helps



Notes:
-I was having issues with the plots displaying before switching backend to TkAgg
- The only wall quantity that is maintined/supported is wall_temps


I am leveraging this Dr Adam Luke Baskerville's work here: 
    https://adambaskerville.github.io/posts/PythonGUIPlotter/

As well as the examples given in PySimpleGui:
    https://www.pysimplegui.org/en/latest/cookbook/

"""


def draw_plot(SimList, SimNames, values, MAXPLOTS):
    """
    Generates plots based on the user inputs into the GUI

    Notes:
    -Sets X Label Based on First Input. Should probably enforce common X axis but wont break things, so leaving to the user(TM)
    """

    #Will loop through these if multiple files are being plotted 
    lineSpecList = ['-', '--', '-.', ':','-', '--', '-.', ':','-', '--', '-.', ':']


    #ax1.set_xlabel('time (s)')
    #ax1.set_ylabel('exp', color=color)
    #ax1.plot(t, data1, color=color)
    #ax1.tick_params(axis='y', labelcolor=color)

    #ax2.set_ylabel('sin', color=color)  # we already handled the x-label with ax1
    #ax2.plot(t, data2, color=color)
    #ax2.tick_params(axis='y', labelcolor=color)

    #Create Figure
    fig, ax1 = plt.subplots()

    #If any enabled plots have "R" enabled, if so, create second axis
    for k in range(MAXPLOTS):
        if values[f'-enab{k}-']==1 and values[f'-lr{k}-'] == "R":
            ax2 = ax1.twinx()
    

    #For Each of the Plots
    for i in range(MAXPLOTS):

        #If Enable Box Checked
        if values[f'-enab{i}-']:

            # For each of the files selected
            for j in range(len(SimList)):

                # If Vector data, need to get Wall Y location index
                if values[f'-yvar{i}-'] == "wall_temps":

                    y_index = SimList[j].Aerosurface.y_e.index(values[f'-yloc{i}-'])

                    plot_yvar = getattr(SimList[j], values[f'-yvar{i}-'])[y_index, :]

                else:
                    plot_yvar = getattr(SimList[j], values[f'-yvar{i}-'])


                # Left or Right Y Axis
                if values[f'-lr{i}-'] == "L":
                    #Plot, pulling variables from those specified by user in GUI
                    ax1.plot(   getattr(SimList[j], values[f'-xvar{i}-']), 
                                plot_yvar,
                                lineSpecList[j],
                                label =values[f'-yvar{i}-']+"- "+SimNames[j],  color=values[f'-col{i}-']) 
                else:
                    #Plot, pulling variables from those specified by user in GUI
                    ax2.plot(   getattr(SimList[j], values[f'-xvar{i}-']), 
                                plot_yvar, 
                                lineSpecList[j],
                                label =values[f'-yvar{i}-']+"- "+SimNames[j]+values[f'-yvar{i}-'],  color=values[f'-col{i}-']) 


    fig.legend()
    ax1.set_xlabel(values[f'-xvar{0}-'])
    #fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show(block=False)




def load_sim_files(FILES):
    """
    Takes in the FILES value output from the file browse GUI, unpickles the Sim objects,
    puts them into a list. Also returns a list of Sim variable names

    Also Rounds Y coordinate Data!

    Notes:
    -NEED TO FILTER OUT/FLAG NON-TIME-SERIES DATA, CLASS ATTRIBUTES
    -Uses first Sim object to get names. Assumes all else have corresponding variables. 

    """
    #print("Note - in load_sim_files: Rounding Y data to 4 digits of precision. This shouldn't cause issues but just letting ya know.")
    
    #List of Simulation Objects
    SimList = []
    #List of Simulation names (filenames without path, or extension)
    SimNames = []

    #For Each File Selected by User
    for filepath in FILES.split(";"):

        #Get Filename without path or extension
        SimNames.append(Path(filepath).stem)
        
        #Open the Sim Pickle File
        with open(filepath, "rb") as f:
            Sim = pickle.load(f)

        #Round Y location data to 4 sig figs
        #Sim.y_coords = [round(num, 4) for num in Sim.y_coords]
        
        #Append SimList
        SimList.append(Sim)

    # Get All Attributes of the Sim Object (ju) (NEED TO FILTER OUT/FLAG NON-TIME-SERIES DATA)
    plotVars = list(SimList[0].__dict__.keys())

    return SimList, SimNames, plotVars




############################################################################################################
############################################### MAIN #######################################################
############################################################################################################


if __name__ == "__main__":


    ############################ CONFIGURATION SETTINGS #####################################
    # Just setting this to 8 for now- if you need more than 8 plots on a figure get help
    MAXPLOTS = 8

    # Set the theme for PysimpleGUI
    sg.theme('DarkAmber') 

    # List the available colours for the plots
    matplotlib_colours = ["dodgerblue", "indianred", "gold", "steelblue", "tomato", "slategray", "plum", "seagreen", "gray"]

    # List the line-styles when using multiple files
    matplotlib_linestyles = ["solid", "dashed", "dashdot", "dotted"]




    ############################ LARGE WALLS OF TEXT #####################################

    instructions = """*If this GUI is too big for your screen, run "python3 gui_post -s" to make it scrollable*

    Instructions:

    - Use the browser below to point to one or more "pickled" FlightSimulation objects. These should be saved out to .sim files when 
    running w/ the gui. Code for outputting these files from a script are included in the examples.

    - To plot the wall temperatures, you need to select "wall_temps" as the Y-variable. Additionally, you need to specify the through-
    wall location, as you need to tell it *where* in the wall you want the temperature. Inner surface? Outer surface? etc.
        - For Nosecone simulations, y=0.0 is the exposed/skin/hot-wall, and max(y) is the inner-wall. 
        - For Fin simulations, both y=0.0 and max(y) will be fin exposed surfaces, and halfway between these will be the fin centerline.

    - I haven't cleaned up the selectable variables fully, and theyres some that wont work if you try and plot them. But
    hopefully they're labelled in a way that makes sense. 

    - Multiple Input File implementation: If you load multiple files and select a plot below, it'll automatically pull the correponding values 
    from all loaded files. I.E. if you load 3 files and only enable Plot 1 with Mach v. Time,  you'll get 3 lines labelled according to each input 
    file. This is useful for doing things like comparing between different materials, motor configs, plotting multiple locations along the body, etc.

        - Note, if you have different wall thicknesses/spacings between the files, the Thru-wall thicknesses may not line up correctly and cause things
            to break

    - As always, feel free to reach out to me if you have any questions/issues. 

        github: elliottmckee
        email: elliott.mckee@proton.me
    """



    ############################ LAYOUT #####################################

    headings = ['', 'Enable', 'Yaxis?', 'X Variable',  'Y Variable', 'Thru-wall Location', 'Color', 'Legend Prefix']
    h_spacings = [8, 6, 8, 22, 22, 23, 20]


    layout = [
                [sg.Text('-'  * 150, size=(150, 1))], #--------------------------
                [sg.Text('------ pyRATT GUI POST -------', size=(150, 1))], #--------------------------
                [sg.Text('-'  * 150, size=(150, 1))], #--------------------------
                [sg.Text(instructions)],
                [sg.Text('-'  * 150, size=(150, 1))], #--------------------------
                
                [sg.Text('Load File(s): ')],

                [sg.Input(key='_FILES_', enable_events=True), sg.FilesBrowse()], 
                [sg.Text('Note, select multiple files by holding ctrl and clicking the number required.')],

                [sg.Text('Files Loaded: (only shows first 5, should be handle up to 12, only limited by my bad implementation in draw_plot())')],

                #*[ [sg.Text(str(i+1) + ") "+  name, key='-filesloaded-')] for i, name in enumerate(fnames) ],
                [sg.Text(size=(25,5), key='-loadedfiles-')],
                

                [sg.Text('-'  * 150, size=(150, 1))], #--------------------------

                [sg.Text('Select Time Series Data: ')],
                
                
                [sg.Text(h, size=(s,1)) for h, s in zip(headings, h_spacings)],  # build header layout


                #Loop for Defining Each of the plot instances
                *[[ 
                    sg.Text(f'Plot {i}: ', size=(10, 1)), 
                    
                    # Enable Plot
                    sg.Checkbox('', default= i==0, key=f'-enab{i}-', size=(2, 1)),

                    # Select Left or Right Y axis
                    sg.InputCombo(values=(['L','R']), default_value='L', key=f'-lr{i}-', size=(2, 1)),

                    #Spacing
                    sg.Text(' '), 
                    
                    # X Variable
                    sg.InputCombo(values=[""], default_value='t_vec', size=(20, 1), key=f'-xvar{i}-'),
                    
                    # Y Variable
                    sg.InputCombo(values=[""], default_value='', size=(20, 1), key=f'-yvar{i}-', enable_events=True),

                    # Through Wall Position
                    sg.InputCombo(values=[""], size=(20, 1), key=f'-yloc{i}-', disabled=True),
                    
                    # Color 
                    sg.InputCombo(values=(matplotlib_colours), size=(20, 1), default_value="dodgerblue", key=f'-col{i}-'),
                    
                    # Linespec
                    #sg.InputCombo(values=(matplotlib_linestyles), size=(25, 1),          key=f'-lspc{i}-'),
                    
                    #sg.InputText('NotImplemented Legend Prefix', size=(20, 1)),
                ] for i in range(MAXPLOTS)],
                
                
                [sg.Text('-'  * 150, size=(150, 1))], #--------------------------
                [sg.Button('Plot'), sg.Text(' '  * 130, size=(130, 1)), sg.Button('Quit')],
            ]






    ############################ WINDOW CONFIGURATION #####################################

    if len(sys.argv) > 1: 
            if sys.argv[1] == "-s":
                #Scrollable Window
                window = sg.Window('pyRATT gui_post', [[sg.Column(layout, scrollable=True, size=(1280, 720))]], size = (1280, 720), resizable = True)
            else:
                raise Exception("Invalid Arguments Input")
    else:
        #Better Looking resizable one
        window = sg.Window('pyRATT gui_post', layout, resizable = True)





    ############################ MAIN WINDOW/EVENT CONTROL LOOP #####################################
    while True:
        event, values = window.read()


        ## QUIT
        if event in (sg.WIN_CLOSED, 'Quit'):
            window.close()
            break

        ## NEW FILE LOAD
        elif event == '_FILES_':
            #Load Sim Objects
            SimList, SimNames, plotVars = load_sim_files(values["_FILES_"])

            window[f'-loadedfiles-'].update(value='\n'.join(SimNames))

            #For each of the Plot Entry Elements
            for i in range(MAXPLOTS):
                #Update Variables
                window[f'-xvar{i}-'].update(values=plotVars)
                window[f'-xvar{i}-'].update(value="t_vec")
                window[f'-yvar{i}-'].update(values=plotVars)
                #Update Coordinates
                window[f'-yloc{i}-'].update(values=SimList[0].Aerosurface.y_e)


        # NEW VARIABLE SELECTED (used to enable the y-location Combo box)
        elif "-yvar" in event:
            #For each entry row
            for i in range(MAXPLOTS):
                #If "wall_temps" selected
                if values[f'-yvar{i}-'] == "wall_temps":
                    #Enable the Combo
                    window[f'-yloc{i}-'].update(disabled=False)
                else:
                    window[f'-yloc{i}-'].update(value='')
                    window[f'-yloc{i}-'].update(disabled=True)



        
        # PLOT
        elif event == 'Plot':

            draw_plot(SimList, SimNames, values, MAXPLOTS)
        




