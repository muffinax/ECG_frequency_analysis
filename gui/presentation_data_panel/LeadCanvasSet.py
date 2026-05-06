import tkinter as tk

from gui.presentation_data_panel.SingleECGCanvas import SingleECGCanvas
from gui.presentation_data_panel.SingleFFTCanvas import SingleFFTCanvas


class LeadCanvasSet(tk.Frame):
    def __init__(self, master, lead_name: str, plot_height: float = 2.5, click_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.lead_name = lead_name

        self.ecg_canvas = SingleECGCanvas(self, lead_name, plot_height, click_callback=click_callback)
        self.fft_canvas = SingleFFTCanvas(self, lead_name, plot_height)

        self.ecg_canvas.pack(fill=tk.X, expand=False, pady=(0, 5))

    def toggle_secondary_canvas(self, show: bool):
        is_packed = bool(self.fft_canvas.winfo_manager())
        if show and not is_packed:
            self.fft_canvas.pack(fill=tk.X, expand=False, pady=(0, 0))
        elif not show and is_packed:
            self.fft_canvas.pack_forget()

    def update_set_data(self, time_axis, amplitude_data, fft_data, overlap_sec=0.0, is_first=False,
                        is_last=False, analysis_start=-1.0, analysis_end=-1.0, analysis_overlap=0.0, is_analysis_active=False):

        vis_start = analysis_start
        vis_end = analysis_end
        fft_data_to_pass = None

        if fft_data is not None:
            if len(fft_data) == 4:
                freqs, magnitudes, snapped_start, snapped_end = fft_data
                fft_data_to_pass = (freqs, magnitudes)
                
                if snapped_start >= 0 and snapped_end >= 0:
                    vis_start = snapped_start
                    vis_end = snapped_end
            else:
                fft_data_to_pass = fft_data

        self.ecg_canvas.is_analysis_enabled = is_analysis_active
        
        self.ecg_canvas.update_chart(time_axis, amplitude_data, overlap_sec, is_first, is_last, vis_start, vis_end, analysis_overlap)
        
        if fft_data_to_pass is not None:
            self.fft_canvas.update_chart(fft_data_to_pass)
            self.fft_canvas.update_vector_chart(fft_data_to_pass)


    def set_height(self, new_height: float):
        self.ecg_canvas.set_height(new_height)
        self.fft_canvas.set_height(new_height)