# Tools to Read in RAS Files, both the .CDX1 file, and the trajectory .CSV

import pandas

from ..common.conversions import *



def RAS_CDX1_Parse(CDX1_filepath):
    #Pull as much geometry about the Rocket as possible- nosecone angle, chamfers, etc

    print("BLAH E OOP SPLURGY")







def RAS_traj_CSV_Parse(trajectory_filepath):

    #Parse the Trajectory CSV file for Mach, Alt, Time, etc.
    df = pandas.read_csv(trajectory_filepath, usecols=['Time (sec)', 'Mach Number', 'Altitude (ft)'])

    # Rename Columns
    df = df.rename(columns={"Time (sec)": "time", "Mach Number": "mach", "Altitude (ft)": "alt"})

    #Convert Altitude to Meters
    df['alt']= df['alt'] * FT2M

    
    return df













