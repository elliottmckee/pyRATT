
import tkinter
import tkinter.messagebox
import customtkinter

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
#customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("src_gui/theme.json")

from src_gui.tooltip_ctk import CreateToolTip

import src_gui.gui_text as gui_text

# #Internal Modules
from src.simulate_network import TransientThermalSim
from src.thermal_network import  ThermalNetwork
from src.tools_aero import ShockList
from src.loadings_aerothermal import AerothermalLoading
from src.obj_flight import FlightProfile
from src.materials_gas import AirModel
from src.materials_solid import MATERIALS_DICT

### FONT FILE: "https://tobiasjung.name/profont/" , the TTF one

### HEX TOOL: https://htmlcolorcodes.com/color-picker/

### 3 Color gradient (fo visualization?) https://mycolor.space/gradient3?ori=to+right&hex=%2301D1FE&hex2=%23FF8000&hex3=%23FF3544&submit=submit

### Sidebar Frame
class SideBarFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Define Master Grid
        self.grid(row=1, column=1, rowspan=4, padx = (5, 20), pady=(5,5), sticky="nsew")
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)
   
        # Title
        self.logo_label = customtkinter.CTkLabel(self, text="PyRATT - Rocket GUI", font=customtkinter.CTkFont(size=27, weight="bold"), text_color="#ff3544")
        self.logo_label.grid(row=1, column=1, padx=30, pady=(25, 20), sticky="nsew")

        # Instructions
        self.InsFrame = customtkinter.CTkFrame(self, corner_radius=0)
        self.InsFrame.grid(row=2, column=1, sticky="nsew")
        self.InsFrame.grid_rowconfigure(1, weight=0)
        self.InsFrame.grid_rowconfigure(2, weight=1)
        self.InsFrame.grid_columnconfigure(1, weight=1)

        self.instruct_label = customtkinter.CTkLabel(self.InsFrame, text="Instructions", font=customtkinter.CTkFont(size=22, weight="bold"), text_color="#ff8000")
        self.instruct_label.grid(row=1, column=1, padx=20, pady=(20,0), sticky="w")

        self.instructions_block = customtkinter.CTkTextbox(self.InsFrame, wrap="word")
        self.instructions_block.grid(row=2, column=1, padx=17, pady=(0, 5), sticky="nsew")
        self.instructions_block.insert("0.0", gui_text.INSTRUCTIONS)
        self.instructions_block.configure(state="disabled")

        # Contact
        self.ContFrame = customtkinter.CTkFrame(self, corner_radius=0)
        self.ContFrame.grid(row=3, column=1, sticky="sew")
        self.ContFrame.grid_rowconfigure(1, weight=0)
        self.ContFrame.grid_rowconfigure(2, weight=0)
        self.ContFrame.grid_columnconfigure(1, weight=1)

        self.cont_label = customtkinter.CTkLabel(self.ContFrame, text="Contact", font=customtkinter.CTkFont(size=22, weight="bold"), text_color="#01d1fe")
        self.cont_label.grid(row=1, column=1, padx=20, pady=(13,0), sticky="nw")

        self.cont_block = customtkinter.CTkTextbox(self.ContFrame, height=50)
        self.cont_block.grid(row=2, column=1, padx=17, pady=(0, 7), sticky="sew")
        
        self.cont_block.insert("0.0", "github: elliottmckee \nemail:  elliott.mckee@proton.me")
        self.cont_block.configure(state="disabled")




### RASAero Frame
class RASAeroFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Define dict of entries to add to (entryname: entry_widget)
        self.entrydict = {}

        # Define Master Grid
        self.grid(row=1, column=2, rowspan=1, columnspan=2, padx = (0, 5), pady=(5,0), sticky="nsew")
        self.grid_rowconfigure((1,2), weight=1)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        # Header
        self.ras_label = customtkinter.CTkLabel(self, text="RASAero Trajectory Input", font=customtkinter.CTkFont(size=22, weight="bold"))
        self.ras_label.grid(row=1, column=1, padx=13, pady=(5, 5), sticky="nw")

        # File Entry
        self.ras_entry = customtkinter.CTkEntry(self, placeholder_text="Path to RASAero .csv output", corner_radius=0, text_color="#ff3544")
        self.ras_entry.grid(row=2, column=1, columnspan=1, padx=(13, 0), pady=(0, 13), sticky="sew")
        self.ras_entry_tip = CreateToolTip(self.ras_entry, gui_text.RAS_FILE_INPUT, width=477, height=320)
        #self.entrylist.append(self.ras_entry)
        self.entrydict["ras_entry"] = self.ras_entry

        self.ras_entry_browse = customtkinter.CTkButton(self, text="Browse...",  width = 230/2, border_width=1, corner_radius=0,\
                                                                                fg_color="#9f212b", hover_color="#ff3544", text_color=("gray10", "#FFFFFF"), \
                                                                                command=self.browse_window)
        self.ras_entry_browse.grid(row=2, column=2, padx=(13, 13), pady=(0, 13), sticky="se")

        
    def browse_window(self):
        file = tkinter.filedialog.askopenfile(mode='r', filetypes=[('RASAeroII Exports', '*.csv')])

        self.ras_entry.insert(0, file.name)

        self.ras_entry.xview(tkinter.END)

    def get_entries(self):
        entry_dict = {}
        for entry_name in self.entrydict:
            entry_dict[entry_name] = self.entrydict[entry_name].get()
        return entry_dict


### Aerosurface Frame

class AeroSurfaceFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Define dict of entries to add to (entryname: entry_widget)
        self.entrydict = {}

        # Define Master Grid
        self.grid(row=2, column=2, rowspan=1, columnspan=2, padx = (0, 5), pady=0, sticky="nsew")
        self.grid_rowconfigure((1,2), weight=1)
        self.grid_rowconfigure((3,4,5), weight=0)
        self.grid_columnconfigure((1,2), weight=1)

        # Header 
        self.aerosurf_label = customtkinter.CTkLabel(self, text="Aerosurface Specification", font=customtkinter.CTkFont(size=22, weight="bold"))
        self.aerosurf_label.grid(row=1, column=1, padx=14, pady=(5, 5), sticky="nw")

        # Geometry Tab Selector
        self.geom_type = customtkinter.CTkSegmentedButton(self, corner_radius=0, border_width=1 ,font=customtkinter.CTkFont(size=16))
        self.geom_type.grid(row=2, column=2, padx=15, pady=0,sticky="ne")
        self.geom_type.configure(values=["Nosecone Wall", "Fin", "Nosecone Tip"], state = "enabled")
        self.geom_type.set("Nosecone Wall")
        self.entrydict["geom_type"] = self.geom_type


        # Angle 
        self.angle_lab = customtkinter.CTkLabel(self, text="Deflection Angle (deg): ")
        self.angle_lab.grid(row=3, column=1, padx=13, sticky="w")
        self.angle = customtkinter.CTkEntry(self, placeholder_text="10.0", text_color="#ff8000", corner_radius=0, width = 230)
        self.angle.grid(row=3, column=2, columnspan=1, padx=13, pady=[5,0], sticky="e")
        self.angle_tip = CreateToolTip(self.angle, gui_text.ANGLE, width= 400, height=400)
        self.entrydict["angle"] = self.angle

        # X_Location 
        self.x_len_lab = customtkinter.CTkLabel(self, text="Distance from LE (m): ")
        self.x_len_lab.grid(row=4, column=1, padx=13, sticky="w")
        self.x_len = customtkinter.CTkEntry(self, placeholder_text="0.1", text_color="#ff8000", corner_radius=0, width = 230)
        self.x_len.grid(row=4, column=2, columnspan=1, padx=13, pady=5, sticky="e")
        self.x_len_tip = CreateToolTip(self.x_len, gui_text.X_LOCATION, width= 400, height=100)
        self.entrydict["x_len"] = self.x_len

        # Wall Thickness
        self.wall_thick_lab = customtkinter.CTkLabel(self, text="Wall Thick (m): ")
        self.wall_thick_lab.grid(row=5, column=1, padx=(13,0), sticky="w")
        self.wall_thick = customtkinter.CTkEntry(self, placeholder_text="0.025", text_color="#ff8000", corner_radius=0, width = 230)
        self.wall_thick.grid(row=5, column=2, columnspan=1, padx=13, pady=0, sticky="e")
        self.wall_thick_tip = CreateToolTip(self.wall_thick, gui_text.WALL_THICK, width= 400, height=50)
        self.entrydict["wall_thick"] = self.wall_thick

        # Material Select
        self.mat_combo_lab = customtkinter.CTkLabel(self, text="Wall Material: ")
        self.mat_combo_lab.grid(row=6, column=1, padx=13, pady=(5,13), sticky="w")
        self.mat_combo = customtkinter.CTkComboBox(self, values=list(MATERIALS_DICT.keys()), corner_radius=0, width = 230)
        self.mat_combo.grid(row=6, column=2, padx=13, pady=(5,13), sticky="e")
        self.mat_combo.set("")
        self.mat_combo_tip = CreateToolTip(self.mat_combo, gui_text.WALL_MAT, width= 400, height=200)
        self.entrydict["mat_combo"] = self.mat_combo


    def get_entries(self):
        entry_dict = {}
        for entry_name in self.entrydict:
            entry_dict[entry_name] = self.entrydict[entry_name].get()
        return entry_dict




### Sim Configuration Tab
class ConfigurationFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Define dict of entries to add to (entryname: entry_widget)
        self.entrydict = {}

        # Define Master Grid
        self.grid(row=3, column=2, rowspan=1, columnspan=2, padx = (0, 5), pady=0, sticky="nsew")
        self.grid_rowconfigure((1), weight=1)
        self.grid_rowconfigure((2,3,4), weight=0)
        self.grid_columnconfigure((1,2), weight=1)


        # Label
        self.sim_in_label = customtkinter.CTkLabel(self, text="Simulation Configuration", font=customtkinter.CTkFont(size=22, weight="bold"))
        self.sim_in_label.grid(row=1, column=1, padx=13, pady=(5,5), sticky="w")
        

        # Wall Nodes
        self.wall_nodes_lab = customtkinter.CTkLabel(self, text="Wall Nodes (integer): ")
        self.wall_nodes_lab.grid(row=2, column=1, padx=13, pady=0, sticky="w")
        self.wall_nodes = customtkinter.CTkEntry(self, placeholder_text="15", text_color="#01d1fe", corner_radius=0, width = 230)
        self.wall_nodes.grid(row=2, column=2, columnspan=1, padx=13, pady=5, sticky="e")
        self.wall_nodes_tip = CreateToolTip(self.wall_nodes, gui_text.WALL_NODES, width= 400, height=300)
        self.entrydict["wall_nodes"] = self.wall_nodes

        # Time Step
        self.time_step_lab = customtkinter.CTkLabel(self, text="Timestep (s): ")
        self.time_step_lab.grid(row=3, column=1, padx=13, pady=0, sticky="w")
        self.time_step = customtkinter.CTkEntry(self, placeholder_text="0.005", text_color="#01d1fe", corner_radius=0, width = 230)
        self.time_step.grid(row=3, column=2, columnspan=1, padx=13, pady=0, sticky="e")
        self.time_step_tip = CreateToolTip(self.time_step, gui_text.TIME_STEP, width= 400, height=300)
        self.entrydict["time_step"] = self.time_step

        # Initial Temp
        self.initial_temp_lab = customtkinter.CTkLabel(self, text="Initial Temperature (K): ")
        self.initial_temp_lab.grid(row=4, column=1, padx=13, pady=[5,0], sticky="w")
        self.initial_temp = customtkinter.CTkEntry(self, placeholder_text="290.0", text_color="#01d1fe", corner_radius=0, width = 230)
        self.initial_temp.grid(row=4, column=2, columnspan=1, padx=13, pady=[5,0], sticky="e")
        self.initial_temp_tip = CreateToolTip(self.initial_temp, gui_text.INIT_TEMP, width= 400, height=300)
        self.entrydict["initial_temp"] = self.initial_temp

        # Time End
        self.time_end_lab = customtkinter.CTkLabel(self, text="Sim End Time (s): ")
        self.time_end_lab.grid(row=5, column=1, padx=13, pady=(5,13), sticky="w")
        self.time_end = customtkinter.CTkEntry(self, placeholder_text="60.0", text_color="#01d1fe", corner_radius=0, width = 230)
        self.time_end.grid(row=5, column=2, columnspan=1, padx=13, pady=(5,13), sticky="e")
        self.time_end_tip = CreateToolTip(self.time_end, gui_text.TIME_END, width= 400, height=300)
        self.entrydict["time_end"] = self.time_end


    def get_entries(self):
        entry_dict = {}
        for entry_name in self.entrydict:
            entry_dict[entry_name] = self.entrydict[entry_name].get()
        return entry_dict




### Actions Tab
class ActionsFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Define Grid
        self.grid(row=4, column=2, rowspan=1, columnspan=2, padx = (0, 5), pady=(0,5), sticky="nsew")
        self.grid_rowconfigure((1), weight=1)
        self.grid_columnconfigure((1,2,3), weight=1)

        #Actions Label
        self.actions_lab = customtkinter.CTkLabel(self, text="Actions", font=customtkinter.CTkFont(size=22, weight="bold"))
        self.actions_lab.grid(row=1, column=1, padx=13, pady=(5,5), sticky="w")

        # Run Button
        self.run_button = customtkinter.CTkButton(self, text="Run", corner_radius=0, \
                                                                            height=100, fg_color="#9f212b", \
                                                                            hover_color="#ff3544", border_color="#FFFFFF",\
                                                                            command=self.master.run_simulation)
        self.run_button.grid(row=2, column=1, padx=(13,5), pady=(5,13), sticky='nesw')


        # Plot Button
        self.plot_button = customtkinter.CTkButton(self, text="Plot Results", corner_radius=0, \
                                                                            fg_color="#9f5000", hover_color = "#ff8000", border_color="#FFFFFF",  \
                                                                            command=self.master.plot_results)
        self.plot_button.grid(row=2, column=2, padx=5, pady=(5,13), sticky='nesw')

        # Save Button
        self.save_button = customtkinter.CTkButton(self, text="Save Results", corner_radius=0, \
                                                                            fg_color="#01839f", border_color="#FFFFFF", \
                                                                            command=self.master.save_results)
        self.save_button.grid(row=2, column=3, padx=(5,13), pady=(5,13), sticky='nesw')








class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("PyRATT - Rocket GUI")
        self.geometry(f"{1000}x{700}")

        self.grid_rowconfigure((1,2,3,4), weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.inputframedict = {}

        ### -------------------- create sidebar frame with widgets ------------------
        self.sidebar_list = SideBarFrame(self)

        self.RasFrame = RASAeroFrame(self)
        self.inputframedict["RasFrame"]=self.RasFrame

        self.AeroFrame = AeroSurfaceFrame(self) 
        self.inputframedict["AeroFrame"]=self.AeroFrame
        #self.input_frame_list.append("AeroFrame")

        self.ConfigFrame = ConfigurationFrame(self)
        self.inputframedict["ConfigFrame"]=self.ConfigFrame
        #self.input_frame_list.append("ConfigFrame")
        
        self.ActionFrame = ActionsFrame(self)


    def get_inputs(self):
        """Pulls inputs from all frames (stupid-recursively)"""
        inputs = {}
        for frame in self.inputframedict:
            inputs.update( self.inputframedict[frame].get_entries() )
        return inputs


    def run_simulation(self):

        # Get GUI Inputs
        inputs = self.get_inputs()

        # Define input structs
        Shocks                   = ShockList( ["oblique"], [float(inputs["angle"])] )
        Flight                    = FlightProfile( inputs["ras_entry"].strip('\"').strip("\'") )
        GasModel                = AirModel()
        AeroThermLoading    = AerothermalLoading( float(inputs["x_len"]),
                                                                    Flight, 
                                                                    Shocks, 
                                                                    GasModel, 
                                                                    aerothermal_model="flat-plate",
                                                                    boundary_layer_model="turbulent") 

        # Build Thermal Network
        TG = ThermalNetwork()
        TG.addComponent_1D( inputs["mat_combo"], total_thickness=float(inputs["wall_thick"]), n_nodes=int(inputs["wall_nodes"]))
        TG.add_thermal_loading(nodeID = 0, ThermLoading= AeroThermLoading)

        # Run Simulation
        self.Sim = TransientThermalSim( TG,  float(inputs["initial_temp"]),  float(inputs["time_step"]), t_start = 0.0, t_end = float(inputs["time_end"]))
        self.Sim_Status = self.Sim.run()



    def plot_results(self):
        if self.Sim:
            print("Plotting things beep boop")
        else:
            print("No Simulation Found. Need to Run Simulation First")


    def save_results(self):
        if self.Sim:
            print("Saving things beep boop")
        else:
            print("No Simulation Found. Need to Run Simulation First")







if __name__ == "__main__":
    app = App()
    app.mainloop()




