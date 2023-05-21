
import tkinter
import tkinter.messagebox
import customtkinter

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("CustomTkinter complex_example.py")
        self.geometry(f"{1100}x{1100}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        #self.grid_columnconfigure((2, 3), weight=0)
        
        #self.grid_rowconfigure((0, 1, 2), weight=1)



        ### -------------------- create sidebar frame with widgets ------------------
        self.sidebar_frame = customtkinter.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar_frame.grid(row=1, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
   
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="PyRatt Rocket GUI", font=customtkinter.CTkFont(size=25, weight="bold"))
        self.logo_label.grid(row=1, column=0, padx=20, pady=(20, 10))

        self.instructions_label = customtkinter.CTkTextbox(self.sidebar_frame, width=250)
        self.instructions_label.grid(row=2, column=0, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.instructions_label.insert("0.0", "Instructions")
        self.instructions_label.configure(state="disabled")

        self.instructions_block = customtkinter.CTkTextbox(self.sidebar_frame, width=250)
        self.instructions_block.grid(row=2, column=0, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.instructions_block.insert("0.0", "CTkTextbox\n\n" + "Lorem ipsum dolor sit amet")
        self.instructions_block.configure(state="disabled")

        self.contact = customtkinter.CTkTextbox(self.sidebar_frame, width=250)
        self.contact.grid(row=3, column=0, padx=(20, 20), pady=(20, 20), sticky="s")
        self.contact.insert("0.0", "Bother me if need info")
        self.contact.configure(state="disabled")


        ### -------------------- Main Column frame with widgets ------------------

        #-----

        self.ras_label = customtkinter.CTkLabel(self, text="RAS Trajectory Input", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.ras_label.grid(row=1, column=1, padx=20, pady=(20, 10), sticky="nw")

        self.ras_entry = customtkinter.CTkEntry(self, placeholder_text="RASAero File Input")
        self.ras_entry.grid(row=2, column=1, columnspan=1, padx=(20, 0), pady=(20, 20), sticky="nsew")

        self.ras_entry_browse = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.ras_entry_browse.grid(row=2, column=2, padx=(0, 0), pady=(20, 20), sticky="nsew")

        #-----

        self.aerosurf_label = customtkinter.CTkLabel(self, text="Aerosurface Inputs", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.aerosurf_label.grid(row=3, column=1, padx=20, pady=(0, 0), sticky="nw")

        self.geom_type = customtkinter.CTkSegmentedButton(self)
        self.geom_type.grid(row=3, column=2, padx=(20, 10), pady=(10, 10), sticky="n")
        self.geom_type.configure(values=["Nosecone Wall", "Fin Wall", "Nosecone Tip"])
        self.geom_type.set("Nosecone Wall")

        # Fin Input Frame
        self.fin_frame = customtkinter.CTkFrame(self, width=300, corner_radius=5)
        self.fin_frame.grid(row=4, column=1, rowspan=1, columnspan=1, sticky="nsew")
        self.fin_frame.grid_rowconfigure((1,2,3), weight=1)
        self.fin_frame.grid_columnconfigure((1,2), weight=1)


        self.x_len_lab = customtkinter.CTkLabel(self.fin_frame, text="Distance from LE: ", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.x_len_lab.grid(row=1, column=1, padx=20, pady=(5, 5), sticky="w")

        self.x_len = customtkinter.CTkTextbox(self.fin_frame, width=250, height=12)
        self.x_len.grid(row=1, column=2, padx=(20, 20), pady=(5, 5), sticky="nsew")
        self.x_len.insert("0.0", "Number")


        self.wall_thick_lab = customtkinter.CTkLabel(self.fin_frame, text="Wall Thick: ", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.wall_thick_lab.grid(row=3, column=1, padx=20, pady=(5, 5), sticky="w")

        self.wall_thick = customtkinter.CTkTextbox(self.fin_frame, width=250, height=12)
        self.wall_thick.grid(row=3, column=2, padx=(20, 20), pady=(5, 5), sticky="nsew")
        self.wall_thick.insert("0.0", "Number")


        self.mat_combo_lab = customtkinter.CTkLabel(self.fin_frame, text="Wall Material: ", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.mat_combo_lab.grid(row=4, column=1, padx=20, pady=(5, 5), sticky="w")

        self.mat_combo = customtkinter.CTkComboBox(self.fin_frame, values=["ALU-342", "Balls", "Value Long..."])
        self.mat_combo.grid(row=4, column=2, padx=20, pady=(5, 5))
        self.mat_combo.set("ALU-342")


        #-----
        self.sim_in_label = customtkinter.CTkLabel(self, text="Simulation Config", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.sim_in_label.grid(row=5, column=1, padx=20, pady=(20, 10), sticky="nw")
        # Sim Input Frame

        self.sim_frame = customtkinter.CTkFrame(self, width=300, corner_radius=5)
        self.sim_frame.grid(row=6, column=1, rowspan=1, columnspan=1, sticky="nsew")
        self.sim_frame.grid_rowconfigure((1,2,3,4), weight=1)
        self.sim_frame.grid_columnconfigure((1,2), weight=1)


        self.wall_node_lab = customtkinter.CTkLabel(self.sim_frame, text="Wall Nodes: ", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.wall_node_lab.grid(row=1, column=1, padx=20, pady=(5, 5), sticky="w")

        self.wall_node = customtkinter.CTkTextbox(self.sim_frame, width=250, height=12)
        self.wall_node.grid(row=1, column=2, padx=(20, 20), pady=(5, 5), sticky="nsew")
        self.wall_node.insert("0.0", "Number")


        self.t_step_lab = customtkinter.CTkLabel(self.sim_frame, text="Timestep (s): ", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.t_step_lab.grid(row=2, column=1, padx=20, pady=(5, 5), sticky="w")

        self.t_step = customtkinter.CTkTextbox(self.sim_frame, width=250, height=12)
        self.t_step.grid(row=2, column=2, padx=(20, 20), pady=(5, 5), sticky="nsew")
        self.t_step.insert("0.0", "Number")


        self.time_vec_lab = customtkinter.CTkLabel(self.sim_frame, text="Sim End Time(s): ", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.time_vec_lab.grid(row=3, column=1, padx=20, pady=(5, 5), sticky="w")

        self.time_vec = customtkinter.CTkTextbox(self.sim_frame, width=250, height=12)
        self.time_vec.grid(row=3, column=2, padx=(20, 20), pady=(5, 5), sticky="nsew")
        self.time_vec.insert("0.0", "Number")


        #-----
        self.run_lab = customtkinter.CTkLabel(self, text="Run", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.run_lab.grid(row=7, column=1, padx=20, pady=(20, 10), sticky="nw")

        self.run_button = customtkinter.CTkButton(self, text="Run")#command=self.sidebar_button_event)
        self.run_button.grid(row=8, column=1, padx=20, pady=10)




        # self.main_button_1 = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        # self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")




        









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




