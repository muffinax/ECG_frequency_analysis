import tkinter as tk

from gui.ECGFrame import ECGFrame


class MainWindow:
    def __init__(self, master):
        self.master = master

        self.master.state('zoomed')
        self.master.title("ECG frequency analysis")

        self.__create_menu()

        self.frame_ecg = ECGFrame(self.master)
        self.frame_ecg.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


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
