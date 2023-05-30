"""
I am just thwomping all of my large strings here to keep them from clogging up the gui scripts
"""


INSTRUCTIONS = "This GUI showcases a few applications of PyRATT. \
\n\n\
You point it to a exported RASAero .csv trajectory, tell it a bit about the rocket geometry you're looking to analyze, \
and add a few additional simulation parameters and it should tell you how hot your thing (nosecone wall, fin, etc.) is going to get.\
\n\n\
Hover over the input boxes for more information about each.\
\n\n\
WIP. If people actually end up using this, I will be more much motivated to put more time into building out more functionality here. \
so please let me know if you have any feedback or questions!\
"


RAS_FILE_INPUT = """Path to RASAeroII .csv trajectory file.

Either copy/paste the absolute filepath into the box, or use the browse button.

Instructions to export this .csv from RASAeroII:
    - From the Simulation window, hit 'View Data'
    - In the plotting window, in the top left, hit 
    file->export->CSV. 
        -The time resolution doesn't matter a whole
         lot, it all gets interpolated anyway. 
         0.10 seconds is what I would reccomend.
    - I reccomend putting that export .csv 
    somewhere in this PyRATT directory, so 
    it is easy to find, but do you.
"""


ANGLE = "\
For Nosecones, this should be the Nosecone half angle.\
\n\n\
For Fins, this should be the fin chamfer angle.\
"

X_LOCATION = \
"Ideally, this should be the boundary layer running length from the leading edge of interest \
(think of putting a string along the nosecone/fin, starting at the stagnation point and ending \
at the point you are analyzing, and measuring its length). \
But in reality, the axial coordinate works fine since nosecone/chamfer angles are small.\
\n\n\
For 'Nosecone Wall' analyses, this is the distance from the nosecone tip to the point you are looking to analyze. \
\n\n\
For 'Fin Wall' analyses, this is the distance rom the fin leading edge to the point you \
are looking to analze, measured parallel to the body axis. \
\n\n\
Message me if this is confusing. A picture really would help here."


WALL_THICK = "How thick is the wall at the point you are looking to analyze?"


WALL_MAT = "\
What is the wall made of?\
\n\n\
If you need to add a new material, you simply need to add a dictionary entry to pyRATT/src/materials_solid.py\
\n\n\
Only single-material walls are supported in GUI, but PyRATT can handle multi-material stackups (see examples)."


WALL_NODES = "\
This tells PyRATT how many nodes to divide the through-wall thickness up into. \
These nodes are then used to solve the transient conduction through the wall specified.\
\n\n\
Less nodes is generally quicker to run, but *technically* less accurate,\n\
Too many nodes can cause numerical instability (PyRATT will throw a warning at runtime if detected). \
\n\n\
The optimal number of nodes depends on wall thickness, timestep, etc. I would reccomend using the \
default value and then adjusting as needed.\
"


TIME_STEP = "\
This tells PyRATT how big of timesteps to use when integrating solutions forward in time. \
\n\n\
Smaller timesteps are *technically* more accurate, but takes longer to run. \
Too large of timesteps will lead to numerical instability (PyRATT will throw a warning at runtime if detected). \
\n\n\
The optimal timestep depends on wall thickness, node count, etc. I would reccomend using the \
default value and then adjusting as needed. \
"


INIT_TEMP = "\
Initial wall temperature at the beginning of the simulation.\
\n\n\
TODO: make this just use the STDATM S.L. value, or RADEQ if left un-specified? \
"

TIME_END = "\
By default, PyRATT will simulate 60.0 seconds. \
\n\n\
However, the peak aeroheating likely occurs in the first few seconds of flight, so simulating this long may be unnessecary. \
\n\n\
If you want to cut the simulation short (i.e. just simulate ascent), you can specify the end time here. \
\n\n\
TODO: Make it so the default behavior is to run entire RASAero Sim, or just ascent or something"











