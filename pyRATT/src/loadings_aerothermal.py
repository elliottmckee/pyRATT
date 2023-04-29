"""
Contains all the tools, models, etc. for the convection and radiation 
portions of thermal heat transfer. 

"""

# Standard Modules
import numpy as np
from math import pow, sqrt, log10, isnan

#Internal Modules
from . import constants
from . import tools_aero




class AerothermalLoading:

    def __init__(self, x_location, Flight, ShockTrain, GasModel, aerothermal_model, boundary_layer_model):
        #Call to set all of the config parameters 
        # TODO: 
        #   -Add Key-value pair overriding of default parameters

        self.x_location = x_location
        self.Flight     = Flight 
        self.GasModel = GasModel
        self.ShockTrain = ShockTrain

        if aerothermal_model in ["flat-plate", "fay_riddell","covingtonArcJet"]:
            self.aerothermal_model = aerothermal_model
        else: raise ValueError("Error in aerothermal_model Specification")
            
        if boundary_layer_model in ["turbulent","laminar","transition"]:
            self.boundary_layer_model = boundary_layer_model
        else: raise ValueError("Error in Boundary Layer/Transition Model Specification")

        

        #Constant Config Parameters
        

    def get_q_in(self, elem, time):
    
        return self.flat_plate_heating(elem.T,
                                                    self.Flight.mach_sim_time[time],
                                                    self.Flight.alt_sim_time[time])


    def fay_riddell_heating(self):
        pass

    def covington_arcjet_heating(self):
        pass


    def flat_plate_heating(self, T_wall, mach_inf, alt):
        # alias exposed hot-wall surface temperature
       
        # get freestream gas state
        p_inf, T_inf, _, u_inf                                  = tools_aero.get_freestream(self.GasModel, alt, mach_inf)
        rho_inf, cp_inf, k_inf, mu_inf, pr_inf, Re_inf  = tools_aero.complete_aero_state(p_inf, T_inf, u_inf, self.x_location, self.GasModel)
 
        # calculate gas state at boundary layer edge (post-shock(s))
        p_e, rho_e, T_e, T_te, m_e, u_e, cp_e, k_e, mu_e, pr_e, Re_e = tools_aero.get_edge_state(p_inf, T_inf, mach_inf, self.x_location,  self.GasModel, self.ShockTrain)

        # check boundary layer state (laminar/turbulent)
        bl_state = tools_aero.get_bl_state(Re_inf, mach_inf, self.boundary_layer_model)
        

        # calculate recovery factor, temperature
        r   = recovery_factor(bl_state, pr_e)
        T_r = recovery_temperature(T_e, T_te, T_wall, r)

        # calculate Eckert reference temperature
        T_ref = eckert_ref_temperature(T_e, T_te, T_wall, r)

        # Get complete fluid properties evaluated at reference temperature
        rho_ref, cp_ref, k_ref, mu_ref, pr_ref, Re_ref = tools_aero.complete_aero_state( p_e, T_ref, u_e, self.x_location, self.GasModel)


        # Flat Plate Heating Model WITHOUT BLOWING CORRECTION, properties evaluated at reference temperature
        q_conv_unblown, h_unblown, lambda_fac = flat_plate_heat_transfer(self.x_location, T_wall, T_r, k_ref, Re_ref, pr_ref, bl_state)

                                
        return q_conv_unblown







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












def get_net_heat_flux(Sim, i):
    """
    High-level driver for determining the net heat flux to hand into the conduction solver,
    for a simulation at a given timestep

    Inputs:
        Sim:    Simulation Object
        i:      Simulation Timestep
    Outputs:
        
    Updates:
        Sim.q_rad[i],   float, radiative heatflux in W/m^2. Positive if heat is going into the wall
        Sim.q_conv[i],  float, convective heatflux in W/m^2. Positive if heat is going into the wall
        Sim.q_net[i],   float, net heatflux in W/m^2. Positive if heat is going into the wall

    TODO:
        Ideally, make it so all updated variables return up to this funciton. 
        I kinda want all Sim.value[i] updates to be no more than 1 (2 at max) functions deep, 
        so we are not setting values silently super deep, in a nested chain of functions
        but may be a non-issue since you can search all files for where things get written

    """

    # Get Convective Heatflux
    Sim.q_conv[i] = aerothermal_heatflux(Sim, i)

    # Radiative Heat Flux
    Sim.q_rad[i] = radiative_heatflux(Sim, i)

    # Net Heat Flux
    Sim.q_net[i] = Sim.q_conv[i] + Sim.q_rad[i]



def radiative_heatflux(Sim, i):
    """
    High level wrapper for the radiative thermal models that are implmemented/can be used.

    Inputs:
        Sim:    Simulation Object
        i:      Simulation Timestep
    Outputs:
        q_rad:  float, radiative heatflux in W/m^2. Positive if heat is going into the wall
    """

    # Just the plain ole black body radiation equation. Nothing fancy here. 

    #Another Workaround here
    if hasattr(Sim, "LUMPEDMASS"):
        return constants.SB_CONST * Sim.LumpedMass.elements[0].emis * ((Sim.T_inf[i])**4 - Sim.wall_temps[0,i]**4)

    else:
        return constants.SB_CONST * Sim.Aerosurface.elements[0].emis * ((Sim.T_inf[i])**4 - Sim.wall_temps[0,i]**4)




def aerothermal_heatflux(Sim, i):
    '''
    High level wrapper/driver for the aerothermal convective models that are 
    implmemented and can be used. 

    Inputs:
        Sim:    Simulation Object
        i:      Simulation Timestep
    Updates:
        T_e:        float, edge temperature [K]
        T_te:       float, edge total temperature [K]
        T_recovery: float, recovery temperature [K]
        h_coeff:    float, heat transfer coefficient
    Outputs:
        q_conv:  float, convective heatflux in [W/m^2]. Positive if heat is going into the wall
    '''

    # Implemented Aerothermal Models
    # ------------------------------
    # 1) default: This is the correlation used in the Ulsu [1] paper. Arnas is who is referenced there,  
    # but it is not who actually developed these correlations. However, after long while of running into 
    # paywalls trying to find original source because I am not a student anymore, I give up. Fuck publishers.

    # Dictionary containing all models and their corresponding function calls
    valid_aerothermal_models     = ["default", "fay_riddell","covingtonArcJet"]

    if Sim.aerothermal_model not in valid_aerothermal_models:
        raise ValueError("Error in aerothermal_model Specification")

    # aerothermal_model_dict = {  "default": ulsu_simsek_heating(Sim, i),
    #                             "covingtonArcJet": covington_pyro(Sim, i) }

    # if Sim.aerothermal_model not in aerothermal_model_dict.keys():
    #     raise ValueError("Error in Aerothermal Model Specification")

    
    # Implemented Boundary Layer Models
    # ------------------------------
    # 1) turbulent: fully turbulent flow
    # 2) laminar: fully laminar flow
    # 3) transition: flow transitions using a modified Re correlation described in Ulsu [1], but
    #                 real source is: 
    #                 Quinn, R. D., and L. Gong. 2000. A method for calculating transient surface temperatures 
    #                 and surface heating rates for high-speed aircraft. NASA/TP-2000-209034. Washington, DC: NASA.
    
    valid_boundarylayer_models     = ["turbulent","laminar","transition"]

    if Sim.bound_layer_model not in valid_boundarylayer_models:
        raise ValueError("Error in Boundary Layer/Transition Model Specification")


    # Call Aerothermal Model
    # ------------------------------
    if Sim.aerothermal_model == "default":
        q_conv = ulsu_simsek_heating(Sim, i)

    elif Sim.aerothermal_model == "fay_riddell":
        q_conv =  fay_riddell_stagnation_heating(Sim , i) #aerothermal_model_dict[Sim.aerothermal_model]

    elif Sim.aerothermal_model == "covingtonArcJet":
        q_conv = covington_pyro(Sim, i) #aerothermal_model_dict[Sim.aerothermal_model]

    return q_conv




def covington_pyro(Sim, i):


    lam=0.4

    
    # Calculate Unblown Convective Flux
    q_unblown = arcjet_flux(Sim, i, 1.0)


    # Get boundary layer injection  pyrolysis gas generation (updates ablative densities)
    mDot_pyro = get_pyrolysis_mdot(Sim, i)

    # Get boundary layer injection from surface recession rate 
    mDot_recess, delta_recess = get_recession_mdot(Sim, i, q_unblown)

    mDot_tot = mDot_pyro + mDot_recess


    # Calculate Adiabatic-Wall and Wall Enthalpy
    # Assuming Adiabatic Wall Enthalpy == Total Enthalpy
    h_aw = 29.5e6


    #Air Enthalpy Evaluated at Wall Temp Mean of data is default if out or range interpolation
    # h_w = interp1(Sim.hLUTair.T,Sim.hLUTair.h, TVec(1),'spline', mean(Sim.hLUTair.h));
    # h_w = interp1(Sim.hLUT(:,1), Sim.hLUT(:,2), Abl.TVec(1,i),'linear', 'extrap');
    h_w = 1396000 #[J/Kg], just ballparking this from https://www.engineeringtoolbox.com/air-properties-d_1257.html

    # Phi
    Phi = (2*lam*mDot_tot*(h_aw - h_w)) / q_unblown


    # Blowing Factor
    eta = Phi / (np.exp(Phi) - 1)



    if Sim.t_vec[i] < 15.0:
        q_flux = arcjet_flux(Sim, i, eta)
    else:
        q_flux = 0


    #Update Wall thicknesses
    Sim.Aerosurface.update_thicknesses(delta_recess)


    return q_flux




def arcjet_flux(Sim, i, eta):

    #Constants
    Q_CW = 5.8e6 #[W/M2]
    H_TOT = 29.5e6 #[W/M2]
    PRES = 45596.25 #[PA], 0.45 Atm to Pa

    T_INF = 290.0 #[K], ASSUMPTION

    CP_AIR = 1200.0 #[J/KgK], No idea if this is what it means by Cp

    #Surface Temperature
    T_w = Sim.wall_temps[0,i]


    #Return Convective Flux
    return eta*Q_CW * (1 - (CP_AIR * T_w)/H_TOT)







def ulsu_simsek_heating(Sim, i):
    """ 
    Driver script for the heating model outline in Ulsu [1] to determine the convective heatflux.

    This is the high-level computational flow outlined in Ulsu [1], to determine the convective
    heatflux. If you're confused about anything here, I *highly* reccomend reading that paper.
    Honestly, just go read it now. Like right now. Do it. 
    
    Inputs:
        Sim:    Simulation Object
        i:      Simulation Timestep
    Updates:
        T_inf
        Re_inf
        qbar_inf
        T_t
        T_e
        T_te
        T_recovery
        h_coeff
    Outputs:
        q_conv: float, Convective Heat Flux [W/m^2]

    """
    
    # alias exposed hot-wall surface temperature
    T_w = Sim.wall_temps[0,i]

    # Get Freestream Properties
    p_inf, T_inf, u_inf, m_inf, rho_inf, cp_inf, k_inf, mu_inf, pr_inf, Re_inf = tools_aero.get_freestream_complete(Sim, i)

    # calculate boundary layer edge properties (post-shock)
    p_e, rho_e, T_e, T_te, m_e, u_e, cp_e, k_e, mu_e, pr_e, Re_e = tools_aero.get_edge_state(p_inf, T_inf, m_inf, Sim)

    # check boundary layer state (laminar/turbulent)
    bl_state = tools_aero.get_bl_state(Sim, Re_inf, m_inf)
    
    # calculate recovery factor, temperature
    r   = recovery_factor(bl_state, pr_e)
    T_r = recovery_temperature(T_e, T_te, T_w, r)

    # calculate Eckert reference temperature
    T_ref = eckert_ref_temperature(T_e, T_te, T_w, r)

    # Get complete fluid properties evaluated at reference temperature
    rho_ref, cp_ref, k_ref, mu_ref, pr_ref, Re_ref = tools_aero.complete_aero_state( p_e, T_ref, u_e, Sim.x_location, Sim.AirModel)


    # Flat Plate Heating Model WITHOUT BLOWING CORRECTION, properties evaluated at reference temperature
    q_conv_unblown, h_unblown, lambda_fac = flat_plate_heat_transfer(Sim.x_location, T_w, T_r, k_ref, Re_ref, pr_ref, bl_state)


    # If not a Lumped Mass (workaround)
    if not hasattr(Sim, "LUMPEDMASS"):

        eta = ablation_model(Sim, i, q_conv_unblown, h_unblown, lambda_fac)

    else:
        eta = 1.0

    # # Get boundary layer injection  pyrolysis gas generation (updates ablative densities)
    # mDot_pyro = get_pyrolysis_mdot(Sim, i)

    # # Get boundary layer injection from surface recession rate 
    # mDot_recess = get_recession_mdot(Sim, i, q_conv_unblown)

    # mDot_tot = mDot_pyro + mDot_recess 


    # # Correct Heat flux for ablation
    # eta = convective_blowing_correction(Sim, i, h_unblown, lambda_fac, mDot_tot)


    # Re-Calculate Convective Heat Flux
    h_corrected = eta * h_unblown 
    q_conv_corrected = h_corrected*(T_r - T_w)


    # Update/Pass values out of sim
    Sim.T_inf[i] = T_inf
    Sim.Re_inf[i] = Re_inf
    Sim.qbar_inf[i] = 0.5*rho_inf*u_inf**2
    Sim.T_t[i] = tools_aero.total_temperature(T_inf, m_inf, Sim.AirModel.gam)

    Sim.bl_state[i] = bl_state

    Sim.T_e[i] = T_e
    Sim.T_te[i] = T_te
    Sim.T_recovery[i] = T_r
    Sim.h_coeff[i] = h_corrected
    

    return q_conv_corrected

    


def recovery_factor(isTurbulent, pr_e):
    """ 
    Returns the recovery factor of a gas

    TODO put a source, and prandtl 
    limits/checks for the applicability of this
    """
    if isTurbulent:
        return pow(pr_e, 1.0/3.0)
    else:
        return pow(pr_e, 1.0/2.0)


def recovery_temperature(T_e, T_te, T_w, r): 
    """ 
    Returns the recovery temperature of a flow.
    
    TODO: Prandtl number applicability limits
    Source: Bertin Hypersonic Aerothermodynamics
    """
    return r * (T_te - T_e) + T_e
    

def eckert_ref_temperature(T_e, T_te, T_w, r):
    """
    Calculate Eckert Reference Temperature of a high-speed boundary layer

    Notes:
    -The Recovery Factor is a function of the local air properties at a given
    point. However, we cannot calculate Eckert's Reference temperature until
    we have it. Currently using Free-stream Prandtl for this Calculation.
    -TODO: Prandtl number applicability limits

    Source:
    - Bertin, Hypersonic Aerothermodynamics
    """

    #Eckert Reference Temperature 
    return 0.5*(T_e + T_w) + 0.22*r*(T_te - T_e)


def flat_plate_heat_transfer(x, T_w, T_r, k_ref, Re_ref, pr_ref, isTurbulent):
    """ 
    Flat plate Nusselt-number/heating correlations.

    Source:
    -Ill find the root source at some point lol, but these are super common
    """

    #Get Heat Transfer Coefficient
    if isTurbulent:
        #Turbulent Heat Transfer Coeff
        h =  (k_ref/x) * 0.02914 * pow(Re_ref, 4.0/5.0) * pow(pr_ref, 1.0/3.0)
        lambda_fac = .4
    else:
        #Laminar Heat Transfer Coeff
        h = (k_ref/x) * 0.33206 * pow(Re_ref, 1.0/2.0) * pow(pr_ref, 1.0/3.0)
        lambda_fac = .5
        
    # Heat Flux
    q_conv = h*(T_r - T_w)

    return q_conv, h, lambda_fac 




def fay_riddell_stagnation_heating(Sim , i):
    """
    TODO: Work through example with this 
    """

    # Override Shock Type
    if Sim.shock_type != "normal":
        print("Overwriting shock_type to 'normal'")
        Sim.shock_type = "normal"


    # alias exposed hot-wall surface temperature
    T_w = Sim.wall_temps[0,i]

    # Get Freestream Properties
    p_inf, T_inf, u_inf, m_inf, rho_inf, cp_inf, k_inf, mu_inf, pr_inf, Re_inf = tools_aero.get_freestream_complete(Sim, i)

    # calculate boundary layer edge properties (post-shock)
    p_e, rho_e, T_e, T_te, m_e, u_e, cp_e, k_e, mu_e, pr_e, Re_e = tools_aero.get_edge_state(p_inf, T_inf, m_inf, Sim, shock_override="normal")

    # Additional Properties
    rho_w = p_e / (Sim.AirModel.R * T_w)
    mu_w = Sim.AirModel.thermal_conductivity(T_w)
    h_0_e = Sim.AirModel.specific_heat(T_e) * T_e + (u_e**2) / 2.0
    h_w = Sim.AirModel.specific_heat(T_w) * T_w


    # Calculate Heat Flux
    q_w = fay_riddell_stagnation_flux( Sim.nose_radius, p_e, p_inf, rho_e, mu_e, rho_w, mu_w, h_0_e, h_w, axisymmetric=Sim.axisymmetric)

    return q_w



#Fay-Riddell Stagnation Point Heating
def fay_riddell_stagnation_flux( Rn, p_e, p_inf, rho_e, mu_e, rho_w, mu_w, h_0_e, h_w, axisymmetric=True):
    """

    ASSUMING DISASSOCIATION SMALL, SO F = 1
    """
    F = 1

    # Get Velocity Gradient from Nose Radius
    dUe_dx = (1/Rn) * sqrt( 2 * (p_e - p_inf) / rho_e) 


    # Convective Heatflux

    if axisymmetric:
        C = 0.763
    else:
        C = 0.57

    q_w = C * (rho_e * mu_e)**0.4 * (rho_w * mu_w)**0.1 * (h_0_e - h_w) * sqrt( dUe_dx )


    return q_w







def sutton_graves(V, rho, Rn):
    """
    I'm really lazy so i/m just pulling values from here:
    https://tfaws.nasa.gov/TFAWS12/Proceedings/Aerothermodynamics%20Course.pdf
    """

    k = 1.7415e-4


    q_s = k * sqrt(rho/Rn) * V**3



#Flat-Plate Heating Correlations
def tauber_flat_plate_heating():
    pass

def tauber_cone_heating():
    pass




def ablation_model(Sim, i, q_conv_unblown, h_unblown, lambda_fac):


    # Check if exposed element is ablative. If not, return one
    if Sim.Aerosurface.elements[0].type != "ablative":
        return 1.0


    # Pyrolysis Analysis
    mDot_pyro = get_pyrolysis_mdot(Sim, i)


    # Surface Recession Mass Exchange
    mDot_recess, delta_recess = get_recession_mdot(Sim, i, q_conv_unblown)


    # Total Mass Injection
    mDot_tot = mDot_pyro + mDot_recess


    # Get Blowing Factor
    return convective_blowing_correction(Sim, i, h_unblown, lambda_fac, mDot_tot)













def get_pyrolysis_mdot(Sim, i):

    mDot_pyro = 0.0

    for j, elem in enumerate(Sim.Aerosurface.elements):

        #If ablative component
        if elem.type == "ablative":
            mDot_pyro += elem.arrhenious_decomp( Sim.wall_temps[j, i], Sim.t_step)[0]

    return mDot_pyro



def get_recession_mdot(Sim, i, q_conv_no_blowing):

    # Get Surface Element
    surf_el = Sim.Aerosurface.elements[0]

    #Update QStar value based on non-blowing q_flux
    surf_el.update_Qstar(q_conv_no_blowing)


    # Calculate Surface Recession
    if  Sim.wall_temps[0, i] > surf_el.ablation_temp_threshold:
        #Get Surface Recession
        sDot = -q_conv_no_blowing/(surf_el.rho * surf_el.Qstar)
    else:
        sDot = 0

    #Make sure you don't get un-recession 
    if sDot > 0:
        print('Warning: Negative Recession Rate Calculated')
        sDot = 0
        

    # Amount of Recession at Timestep
    delta_recess = -sDot * Sim.t_step

    # Rate that mass is recessing
    mDot_recess = -surf_el.rho*sDot 

    return mDot_recess, delta_recess

 

def convective_blowing_correction(Sim, i, h_unblown, lambda_fac, mDot_tot):

    # Phi
    Phi = (2.0*lambda_fac*mDot_tot) / h_unblown

    # Blowing Factor
    eta = Phi / (np.exp(Phi) - 1)

    # stupid indeterminate forms or something
    if isnan(eta):
        eta = 1

    return eta









# #Incopera Flat-Plate Heating Correlations
# def incopera_heating_correlations():
#     # Source:  Bergman, T. L., & Incropera, F. P.. Fundamentals of heat and mass transfer (Sixth edition.). Wiley. 
#     # Page: 455, Summary of Convection Heat Transfer Correlations for External Flow

#     # THERE ARE ALSO AVERAGE NUSSELT NUMBER CORRELATIONS - POSSIBLY USEFUL FOR LUMPED SUM?

#     # These are so close to the Ulsu simsek flat plate heating values lol, i dont need to implement

#     raise NotImplementedError()

#     #Nusselt Number Correlations
#     if "flat_plate":
        
#         if "laminar":
#             Nu_x = 0.332 * pow(Re_x, 1.0/2.0) * pow(Pr, 1.0/3.0)
#         if "turbulent":
#             Nu_x = 0.0296 * pow(Re_x, 4.0/5.0) * pow(Pr, 1.0/3.0)
#     if "cylinder":
#         #This is just a reminder that these are in the Incopera tables referenced, if we want them for body tube heating
#         pass


