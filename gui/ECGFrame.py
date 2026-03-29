import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ECGFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.figure = Figure(figsize=(6, 4), dpi=100)

        self.ax = self.figure.add_subplot(111)
        self.ax.clear()
        self.__format_ax()

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas_widget = self.canvas.get_tk_widget()

        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

    def __format_ax(self):
        # self.ax.spines['top'].set_visible(False)
        # self.ax.spines['right'].set_visible(False)
        # self.ax.spines['bottom'].set_visible(False)
        # self.ax.spines['left'].set_visible(False)
        self.ax.set_title("ECG signal graph", fontsize=12)
        self.ax.set_xlabel("Time [s]")
        self.ax.set_ylabel("Amplitude [mV]")
        self.ax.grid(True, linestyle='--', alpha=0.7)

    def update_chart(self, t, a):     #t - time, a - amplitude
        self.ax.clear()
        self.ax.plot(t, a, color='black', linewidth=1)
        self.__format_ax()
        self.canvas.draw()
