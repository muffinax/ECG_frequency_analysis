import tkinter as tk

from gui.AnnotationFrame import AnnotationFrame
from gui.ECGFrame import ECGFrame
from gui.SettingsFrame import SettingsFrame


class MainWindow:
    def __init__(self, master):
        self.master = master

        self.master.state('zoomed')
        self.master.title("ECG frequency analysis")
        self.__create_menu()

        self.frame_annotations = AnnotationFrame(self.master, width=250)
        self.frame_annotations.pack_propagate(False)
        self.frame_annotations.pack(side=tk.RIGHT, fill=tk.Y)

        self.frame_buttons = SettingsFrame(self.master, height=80)
        self.frame_buttons.pack_propagate(False)
        self.frame_buttons.pack(side=tk.BOTTOM, fill=tk.X)

        self.frame_ecg = ECGFrame(self.master)
        self.frame_ecg.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def __create_menu(self):
        menu_bar=tk.Menu(self.master)

        menu_file = tk.Menu(menu_bar,tearoff=0)
        menu_bar.add_cascade(label='File', menu=menu_file)
        menu_file.add_command(label='Open..', command=None)
        menu_file.add_command(label='Save', command=None)
        menu_file.add_command(label='Save as...', command=None)
        menu_file.add_separator()
        menu_file.add_command(label='Exit', command=self.master.destroy)

        menu_analysis = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label='Analysis', menu=menu_analysis)
        menu_analysis.add_command(label='perform an ECG analysis', command=None)

        self.master.config(menu=menu_bar)
