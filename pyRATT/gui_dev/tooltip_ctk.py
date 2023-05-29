""" 
tk_ToolTip_class101.py
gives a Tkinter widget a tooltip as the mouse is above the widget
tested with Python27 and Python34  by  vegaseat  09sep2014
www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter

Modified to include a delay time by Victor Zaccardo, 25mar16
https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter

Modified by me (elliottmckee) for cTk objects, and to fit ****aesthetics***
"""

import tkinter as tk
import customtkinter as CTk

CTk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
#customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
CTk.set_default_color_theme("gui_dev/theme.json")

class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget tooltip info', width= None, height=None):
        """
        If width or height unspecified, pull from parent widget
        """
        
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

        if width: self.width = width
        else: self.width = self.widget.cget("width") - 5

        if height: self.height = height
        else: self.height = self.widget.cget("height")

        # Pull Colors from original widget
        self.bg_color = widget.cget("bg_color")[1]
        self.fg_color = widget.cget("fg_color")
        self.text_color = widget.cget("text_color")
        


    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip_ctk)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    # def showtip(self, event=None):
    #     x = y = 0
    #     x, y, cx, cy = self.widget.bbox("insert")
    #     x += self.widget.winfo_rootx() + 25
    #     y += self.widget.winfo_rooty() + 20
    #     # creates a toplevel window
    #     self.tw = tk.Toplevel(self.widget)
    #     # Leaves only the label and removes the app window
    #     self.tw.wm_overrideredirect(True)
    #     self.tw.wm_geometry("+%d+%d" % (x, y))
    #     label = tk.Label(self.tw, text=self.text, justify='left',
    #                    background=self.fg_color, relief='solid', borderwidth=1,
    #                    wraplength = self.wraplength)
    #     label.pack(ipadx=1)


    def showtip_ctk(self, event=None):
        
        # Creates a toplevel window
        self.tw = CTk.CTkToplevel(self.widget)

        # Creates a Frame because Formatting
        self.tw_frame = CTk.CTkFrame(self.tw )
        self.tw_frame.grid(row=1, column=1, padx=0, sticky="w")

        # get location of window, offset tip window
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx()
        y += self.widget.winfo_rooty() + self.widget.cget("height")

        
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        # label = tk.Label(self.tw, text=self.text, justify='left',
        #                background=self.fg_color, relief='solid', borderwidth=1,
        #                wraplength = self.wraplength)
        
        # self.label =  CTk.CTkLabel(self.tw_frame, text="insert james burger", text_color="grey10", width = self.widget.cget("width"))
        # self.label.grid(row=1, column=1, padx=5, sticky="w")


        self.textbox =  CTk.CTkTextbox(self.tw_frame, wrap="word", text_color=self.widget.cget("text_color"), \
                                                            width = self.width, activate_scrollbars=False, \
                                                                height = self.height)
        self.textbox.grid(row=1, column=1, padx=2, pady=2, sticky="nw")
        self.textbox.insert("0.0", self.text)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()



# testing ...
# if __name__ == '__main__':
#     root = tk.Tk()
#     btn1 = tk.Button(root, text="button 1")
#     btn1.pack(padx=10, pady=5)
#     button1_ttp = CreateToolTip(btn1, \
#    'Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, '
#    'consectetur, adipisci velit. Neque porro quisquam est qui dolorem ipsum '
#    'quia dolor sit amet, consectetur, adipisci velit. Neque porro quisquam '
#    'est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit.')

#     btn2 = tk.Button(root, text="button 2")
#     btn2.pack(padx=10, pady=5)
#     button2_ttp = CreateToolTip(btn2, \
#     "First thing's first, I'm the realest. Drop this and let the whole world "
#     "feel it. And I'm still in the Murda Bizness. I could hold you down, like "
#     "I'm givin' lessons in  physics. You should want a bad Vic like this.")
#     root.mainloop()


