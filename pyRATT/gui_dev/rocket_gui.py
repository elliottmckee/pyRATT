
import tkinter
import tkinter.messagebox
import customtkinter

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

customtkinter.set_default_color_theme("gui_dev/theme.json")


### FONT FILE: "https://tobiasjung.name/profont/" , the TTF one

### HEX TOOL: https://htmlcolorcodes.com/color-picker/



### Sidebar Frame
class SideBarFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Define Master Grid
        self.grid(row=1, column=1, rowspan=8, padx = (5, 20), pady=(5,5), sticky="nsew")
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

        self.instructions_block = customtkinter.CTkTextbox(self.InsFrame)
        self.instructions_block.grid(row=2, column=1, padx=17, pady=(0, 5), sticky="nsew")
        self.instructions_block.insert("0.0", "Your balls will explode on the  34th day of the 7th month of the thirdy-first year of the 21rd Epoch...")
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

        self.ras_entry_browse = customtkinter.CTkButton(self, text="Browse...",  width = 230/2, border_width=1, fg_color="#9f212b", text_color=("gray10", "#FFFFFF"), corner_radius=0)
        self.ras_entry_browse.grid(row=2, column=2, padx=(13, 13), pady=(0, 13), sticky="se")



### Aerosurface Frame

class AeroSurfaceFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

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
        self.geom_type.configure(values=["Nosecone Wall", "Fin Wall", "Nosecone Tip"], state = "enabled")
        self.geom_type.set("Nosecone Wall")

        # X_Location 
        self.x_len_lab = customtkinter.CTkLabel(self, text="Distance from LE (m): ")
        self.x_len_lab.grid(row=3, column=1, padx=13, sticky="w")
        self.x_len = customtkinter.CTkEntry(self, placeholder_text="0.1", text_color="#ff8000", corner_radius=0, width = 230)
        self.x_len.grid(row=3, column=2, columnspan=1, padx=13, pady=5, sticky="e")

        # Wall Thickness
        self.wall_thick_lab = customtkinter.CTkLabel(self, text="Wall Thick (m): ")
        self.wall_thick_lab.grid(row=4, column=1, padx=(13,0), sticky="w")
        self.wall_thick = customtkinter.CTkEntry(self, placeholder_text="0.025", text_color="#ff8000", corner_radius=0, width = 230)
        self.wall_thick.grid(row=4, column=2, columnspan=1, padx=13, pady=0, sticky="e")

        # Material Select
        self.mat_combo_lab = customtkinter.CTkLabel(self, text="Wall Material: ")
        self.mat_combo_lab.grid(row=5, column=1, padx=13, sticky="w")
        self.mat_combo = customtkinter.CTkComboBox(self, values=["ALU-342", "Balls", "Value Long..."], corner_radius=0, width = 230)
        self.mat_combo.grid(row=5, column=2, padx=13, pady=(5,13), sticky="e")
        self.mat_combo.set("")



### Sim Configuration Tab
class ConfigurationFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)


        # Define Master Grid
        self.grid(row=3, column=2, rowspan=1, columnspan=2, padx = (0, 5), pady=0, sticky="nsew")
        self.grid_rowconfigure((1), weight=1)
        self.grid_rowconfigure((2,3,4), weight=0)
        self.grid_columnconfigure((1,2), weight=1)


        # Label
        self.sim_in_label = customtkinter.CTkLabel(self, text="Simulation Configuration", font=customtkinter.CTkFont(size=22, weight="bold"))
        self.sim_in_label.grid(row=1, column=1, padx=13, pady=(5,5), sticky="w")
        

        # Wall Nodes
        self.wall_nodes_lab = customtkinter.CTkLabel(self, text="Wall Nodes: ")
        self.wall_nodes_lab.grid(row=2, column=1, padx=13, pady=0, sticky="w")
        self.wall_nodes = customtkinter.CTkEntry(self, placeholder_text="15", text_color="#01d1fe", corner_radius=0, width = 230)
        self.wall_nodes.grid(row=2, column=2, columnspan=1, padx=13, pady=5, sticky="e")

        # Time Step
        self.time_step_lab = customtkinter.CTkLabel(self, text="Timestep (s): ")
        self.time_step_lab.grid(row=3, column=1, padx=13, pady=0, sticky="w")
        self.time_step = customtkinter.CTkEntry(self, placeholder_text="0.005", text_color="#01d1fe", corner_radius=0, width = 230)
        self.time_step.grid(row=3, column=2, columnspan=1, padx=13, pady=0, sticky="e")

        # Time End
        self.time_end_lab = customtkinter.CTkLabel(self, text="Sim End Time (s): ")
        self.time_end_lab.grid(row=4, column=1, padx=13, pady=0, sticky="w")
        self.t_end = customtkinter.CTkEntry(self, placeholder_text="optional", text_color="#01d1fe", corner_radius=0, width = 230)
        self.t_end.grid(row=4, column=2, columnspan=1, padx=13, pady=(5,13), sticky="e")



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
        self.run_button = customtkinter.CTkButton(self, text="Run", corner_radius=0, height=100, fg_color="#ff3544", border_color="#FFFFFF")#command=self.sidebar_button_event)
        self.run_button.grid(row=2, column=1, padx=(13,5), pady=(5,13), sticky='nesw')

        # View Button
        self.run_button = customtkinter.CTkButton(self, text="View Results", corner_radius=0, fg_color="#ff8000", border_color="#FFFFFF")#command=self.sidebar_button_event)
        self.run_button.grid(row=2, column=2, padx=5, pady=(5,13), sticky='nesw')

        # Save Button
        self.run_button = customtkinter.CTkButton(self, text="Save Results", corner_radius=0, fg_color="#01d1fe", border_color="#FFFFFF")#command=self.sidebar_button_event)
        self.run_button.grid(row=2, column=3, padx=(5,13), pady=(5,13), sticky='nesw')














class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("PyRATT - Rocket GUI")
        self.geometry(f"{1000}x{575}")

        self.grid_rowconfigure((1,2,3,4,5,6,7,8,9), weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)




        ### -------------------- create sidebar frame with widgets ------------------
        self.SideBar = SideBarFrame(self)

        self.RasFrame = RASAeroFrame(self)

        self.AeroFrame = AeroSurfaceFrame(self) 

        self.ConfigFrame = ConfigurationFrame(self)
        
        self.ActionFrame = ActionsFrame(self)




        






        









    # def open_input_dialog_event(self):
    #     dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
    #     print("CTkInputDialog:", dialog.get_input())

    # def change_appearance_mode_event(self, new_appearance_mode: str):
    #     customtkinter.set_appearance_mode(new_appearance_mode)

    # def change_scaling_event(self, new_scaling: str):
    #     new_scaling_float = int(new_scaling.replace("%", "")) / 100
    #     customtkinter.set_widget_scaling(new_scaling_float)

    # def sidebar_button_event(self):
    #     print("sidebar_button click")


if __name__ == "__main__":
    app = App()
    app.mainloop()




