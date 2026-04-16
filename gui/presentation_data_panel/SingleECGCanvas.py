import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MultipleLocator, FuncFormatter

import localisation

#Drawing chart
class SingleECGCanvas(tk.Frame):
    def __init__(self, master, lead_name: str, plot_height: float = 2.5, click_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.lead_name = lead_name

        self.click_callback = click_callback

        # click and drag variables
        self.is_dragging = False
        self.drag_start_x = -1.0
        self.is_analysis_enabled = False

        self.figure = Figure(figsize=(6, plot_height), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        self.canvas.mpl_connect('button_press_event', self._on_press)
        self.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.canvas.mpl_connect('button_release_event', self._on_release)

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

    def update_chart(self, time_axis, amplitude, overlap_sec=0.0, is_first=False, is_last=False, analysis_start=-1.0, analysis_end=-1.0, analysis_overlap=0.0):
        self.figure.clear()

        if amplitude is None or len(time_axis) == 0:
            self.canvas.draw()
            return

        ax = self.figure.add_subplot(1, 1, 1)

        ax.plot(time_axis, amplitude, color='black', linewidth=1)
        ax.set_xlim([time_axis[0], time_axis[-1]])

        if overlap_sec > 0.0:
            if not is_first:
                start_time = time_axis[0]
                ax.axvspan(start_time, start_time + overlap_sec, color='gray', alpha=0.15)
            if not is_last:
                end_time = time_axis[-1]
                ax.axvspan(end_time - overlap_sec, end_time, color='gray', alpha=0.15)

        ax.set_title(f"{self.lead_name} - EKG", fontsize=8, loc='left',
                     bbox=dict(facecolor='#E0E0E0', edgecolor='none', alpha=0.8, pad=4))

        ax.set_ylabel(localisation.name_resolver.get("frame_annotationframe_table_amplitude_label"))
        ax.set_xlabel(localisation.name_resolver.get("frame_annotationframe_table_time_label"))
        ax.grid(True, linestyle='--', alpha=0.7)

        window_duration = time_axis[-1] - time_axis[0]
        self._apply_ecg_grid(ax, window_duration)

        self.apply_analysis(analysis_start, analysis_end, analysis_overlap)

        self.figure.subplots_adjust(left=0.1, right=0.98, top=0.85, bottom=0.25)
        self.canvas.draw()

    def set_height(self, new_height_inches: float):
        pixel_height = int(new_height_inches * self.figure.dpi)
        self.canvas_widget.configure(height=pixel_height)
        self.canvas.draw_idle()

    def apply_analysis(self, analysis_start=-1.0, analysis_end=-1.0, analysis_overlap=0.0):
        if not self.figure.axes:
            return

        if hasattr(self, 'analysis_visual_elements'):
            for element in self.analysis_visual_elements:
                try:
                    element.remove()
                except Exception:
                    pass

        self.analysis_visual_elements = []

        ax = self.figure.axes[0]

        if analysis_start >= 0:
            if analysis_end < 0:
                line = ax.axvline(x=analysis_start, color='blue', linewidth=2.0, linestyle='--')
                self.analysis_visual_elements.append(line)
            else:
                start = min(analysis_start, analysis_end)
                end = max(analysis_start, analysis_end)

                line1 = ax.axvline(x=start, color='blue', linewidth=2.0, linestyle='--')
                line2 = ax.axvline(x=end, color='blue', linewidth=2.0, linestyle='--')
                span_main = ax.axvspan(start, end, color='blue', alpha=0.15)
                self.analysis_visual_elements.extend([line1, line2, span_main])

                if analysis_overlap > 0.0:
                    span_left = ax.axvspan(start - analysis_overlap, start, color='dodgerblue', alpha=0.35)
                    span_right = ax.axvspan(end, end + analysis_overlap, color='dodgerblue', alpha=0.35)
                    self.analysis_visual_elements.extend([span_left, span_right])

        self.canvas.draw_idle()

    def _on_press(self, event):
        if not self.is_analysis_enabled:
            return

        if event.inaxes is not None and event.xdata is not None:
            self.is_dragging = True
            self.drag_start_x = float(event.xdata)

    def _on_motion(self, event):
        if not self.is_analysis_enabled:
            return

        if self.is_dragging and event.inaxes is not None and event.xdata is not None:
            current_x = float(event.xdata)
            self.apply_analysis(self.drag_start_x, current_x)

    def _on_release(self, event):
        if not self.is_analysis_enabled or not self.is_dragging:
            return

        self.is_dragging = False

        if event.xdata is not None:
            drag_end_x = float(event.xdata)
        else:
            drag_end_x = self.drag_start_x

        if abs(drag_end_x - self.drag_start_x) < 0.05:
            # user clicked
            if self.click_callback:
                self.click_callback(self.lead_name, self.drag_start_x, -1.0)
        else:
            #user clicked and dragged
            start = min(self.drag_start_x, drag_end_x)
            end = max(self.drag_start_x, drag_end_x)
            if self.click_callback:
                self.click_callback(self.lead_name, start, end)