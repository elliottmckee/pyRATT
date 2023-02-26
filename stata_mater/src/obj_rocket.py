
"""
           ) (   (      (   (         )    )                                  
  *   ) ( /( )\ ))\ )   )\ ))\ )   ( /( ( /(   *   )                          
` )  /( )\()|()/(()/(  (()/(()/(   )\()))\())` )  /(                          
 ( )(_)|(_)\ /(_))(_))  /(_))(_)) ((_)\((_)\  ( )(_))                         
(_(_()) _((_|_))(_))   (_))(_))    _((_) ((_)(_(_())                          
|_   _|| || |_ _/ __|  |_ _/ __|  | \| |/ _ \|_   _|                          
  | |  | __ || |\__ \   | |\__ \  | .` | (_) | | |                            
  |_|  |_||_|___|___/  |___|___/  |_|\_|\___/  |_|                            
 (      *    (   (          *           )           (           )             
 )\ ) (  `   )\ ))\ )     (  `       ( /(   *   )   )\ )     ( /(      *   )  
(()/( )\))( (()/(()/( (   )\))(  (   )\())` )  /(( (()/(     )\())(  ` )  /(  
 /(_)|(_)()\ /(_))(_)))\ ((_)()\ )\ ((_)\  ( )(_))\ /(_))   ((_)\ )\  ( )(_)) 
(_)) (_()((_|_))(_)) ((_)(_()((_|(_) _((_)(_(_()|(_|_))_   __ ((_|(_)(_(_())  
|_ _||  \/  | _ \ |  | __|  \/  | __| \| ||_   _| __|   \  \ \ / / __|_   _|  
 | | | |\/| |  _/ |__| _|| |\/| | _|| .` |  | | | _|| |) |  \ V /| _|  | |    
|___||_|  |_|_| |____|___|_|  |_|___|_|\_|  |_| |___|___/    |_| |___| |_|    
                                                                              

(this is not implemented yet)
"""




class Rocket:
    """
    Class to represent the high-level geometrical parameters of a Rocket Vehicle
    
    Example
    ----------

    Attributes
    ----------
    nosecone_angle_deg : float
        angle of nosecone half angle, in deg
    nosecone_angle_rad : float
        angle of nosecone half angle, in rad
    nosecone_tip_radius : float
        nosecone tip radius (i assume in m but i haven't implemented yet)
    nosecone_surface_roughness : float
        nosecone surface roughness (not yet implemented)
    
    Methods
    -------

    Notes
    -------
    -
    """

    #High-level geometrical specification of Rocket shape n whatnot
    def __init__(self, nosecone_half_angle_deg, RAS_Filename: Optional[str] = None, nosecone_tip_radius: Optional[float] = None, nosecone_surface_roughness: Optional[float] = None):

        print("NOT YET IMPLEMENTED")

        self.nosecone_angle_deg     = nosecone_half_angle_deg                           #Degrees
        self.nosecone_angle_rad     = nosecone_half_angle_deg * constants.DEG2RAD     #Radians
        self.nosecone_tip_radius    = nosecone_tip_radius
        self.nosecone_surface_roughness = nosecone_surface_roughness

        #Automatic-Parsing of CDX1 File example here
        if RAS_Filename is not None:
            raise NotImplementedError("RAS CDX1 Parsing not yet implemented")
            #self.nosecone_angle, etc. = self.parse_RAS(RAS_Filename)

    # def parse_RAS(RAS_Filename):
    #     raise NotImplementedError()

