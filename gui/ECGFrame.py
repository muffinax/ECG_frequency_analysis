import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MultipleLocator, FuncFormatter

import localisation
from gui.display_data.DisplayManager import DisplayManager


class ECGFrame(tk.Frame):
    def __init__(self, master, display_manager: DisplayManager ,**kwargs):
        super().__init__(master, **kwargs)
        self.display_manager = display_manager

        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

    def _apply_ecg_grid(self, ax, duration):
        ax.xaxis.set_major_locator(MultipleLocator(0.2))
        ax.yaxis.set_major_locator(MultipleLocator(0.5))
        ax.grid(which='major', color='#ffb3b3', linestyle='-', linewidth=1.0)

        if duration <= 5.0:
            ax.xaxis.set_minor_locator(MultipleLocator(0.04))
            ax.yaxis.set_minor_locator(MultipleLocator(0.1))
            ax.grid(which='minor', color='#ffe6e6', linestyle='-', linewidth=0.5)
        else:
            ax.minorticks_off()

        def time_formatter(x, pos):
            if abs(x - round(x)) < 0.01:
                return f"{int(round(x))}"
            return ""

        ax.xaxis.set_major_formatter(FuncFormatter(time_formatter))

    def update_charts(self, time_axis, signals_dict, overlap_sec=0.0, is_first=False, is_last=False):
        self.figure.clear()

        leads_to_draw = self.display_manager.displayed_leads    #Later will be added frequency leads
        num_of_plots = len(leads_to_draw)
        if num_of_plots == 0 or len(time_axis) == 0:
            self.canvas.draw()
            return

        for x, lead in enumerate(leads_to_draw):
            ax = self.figure.add_subplot(num_of_plots, 1, x + 1)
            amplitude = signals_dict.get(lead)

            if amplitude is not None and len(amplitude) == len(time_axis):
                ax.plot(time_axis, amplitude, color='black', linewidth=1)
                ax.set_xlim([time_axis[0], time_axis[-1]])

                if overlap_sec > 0.0:
                    if not is_first:
                        start_time = time_axis[0]
                        ax.axvspan(start_time, start_time + overlap_sec, color='gray', alpha=0.15)

                    if not is_last:
                        end_time = time_axis[-1]
                        ax.axvspan(end_time - overlap_sec, end_time, color='gray', alpha=0.15)

                ax.set_title(
                    f"{localisation.name_resolver.get("ECG_chart_title")}{lead.to_string()}",
                    fontsize=8,
                    loc='left',
                    bbox=dict(
                        facecolor='#E0E0E0',
                        edgecolor='none',
                        alpha=0.8,
                        pad=4
                    )
                )

                ax.set_ylabel(localisation.name_resolver.get("frame_annotationframe_table_amplitude_label"))
                ax.grid(True, linestyle='--', alpha=0.7)

                window_duration = time_axis[-1] - time_axis[0]
                self._apply_ecg_grid(ax, window_duration)

                if x == num_of_plots - 1:
                    ax.set_xlabel(localisation.name_resolver.get("frame_annotationframe_table_time_label"))

        self.figure.tight_layout()
        self.canvas.draw()
