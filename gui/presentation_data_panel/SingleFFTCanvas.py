import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SingleFFTCanvas(tk.Frame):
    def __init__(self, master, lead_name: str, plot_height: float = 2.5, **kwargs):
        super().__init__(master, **kwargs)
        self.lead_name = lead_name

        self.figure = Figure(figsize=(6, plot_height), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        self.ax1 = self.figure.add_subplot(1, 2, 1)
        self.ax2 = self.figure.add_subplot(1, 2, 2)

    def update_chart(self, fft_data):
        self.ax1.clear()

        if not fft_data or len(fft_data) != 2:
            self.canvas.draw()
            return

        freqs, complex_vals = fft_data
        
        # Calculate magnitudes from complex numbers locally for the bar chart
        magnitudes = np.abs(complex_vals)

        if len(freqs) > 1:
            bar_width = (freqs[1] - freqs[0]) * 0.8
        else:
            bar_width = 1.0

        self.ax1.bar(freqs, magnitudes, width=bar_width, color='#0052cc', alpha=0.8)
        self.ax1.set_title(f"{self.lead_name} - Widmo Amplitudowe (FFT)", fontsize=8, loc='left',
                     bbox=dict(facecolor='#E0E0E0', edgecolor='none', alpha=0.8, pad=4))
        self.ax1.set_ylabel("Amplituda widma (log)")
        self.ax1.set_xlabel("Częstotliwość [Hz]")
        self.ax1.set_yscale('log')
        self.ax1.set_xlim(left=0, right=max(freqs) if len(freqs) > 0 else 1)
        self.ax1.set_ylim(bottom=1e-3) 
        self.ax1.grid(True, linestyle=':', alpha=0.6)

        self.figure.subplots_adjust(left=0.1, right=0.98, top=0.85, bottom=0.25)
        self.canvas.draw_idle()


    def update_vector_chart(self, fft_data):
        self.ax2.clear()

        if not fft_data or len(fft_data) != 2:
            self.canvas.draw()
            return

        freqs, complex_vals = fft_data

        # Pomijamy 0Hz i bierzemy kolejne 60 prążków FFT
        if len(freqs) > 2:
            freqs = freqs[2:62]
            complex_vals = complex_vals[2:62]

        # Ekstrakcja części rzeczywistej (X) i urojonej (Y)
        real_parts = np.real(complex_vals)
        imag_parts = np.imag(complex_vals)

        # Rysowanie wyższych częstotliwości innymi kolorami
        colors = plt.cm.viridis(np.linspace(0, 1, len(freqs)))

        # Rysowanie wektorów od punktu (0,0)
        for r, i, c in zip(real_parts, imag_parts, colors):
            self.ax2.plot([0, r], [0, i], color=c, alpha=0.7, linewidth=1.5)
            # Kropka na końcu wektora
            self.ax2.plot(r, i, marker='o', markersize=3, color=c)

        # Osie przechodzące przez punkt 0,0
        self.ax2.axhline(0, color='black', linewidth=0.8, linestyle='--')
        self.ax2.axvline(0, color='black', linewidth=0.8, linestyle='--')

        # Wymuszenie proporcji 1:1, żeby koło było okrągłe, a nie rozciągnięte w elipsę
        self.ax2.set_aspect('equal', adjustable='datalim')

        self.ax2.set_title(f"{self.lead_name} - Fazy (Wektory zespolone)", fontsize=8, loc='left',
                     bbox=dict(facecolor='#E0E0E0', edgecolor='none', alpha=0.8, pad=4))
        self.ax2.set_ylabel("Część Urojona (Imag)")
        self.ax2.set_xlabel("Część Rzeczywista (Real)")

        self.ax2.grid(True, linestyle=':', alpha=0.6)

        self.figure.subplots_adjust(left=0.1, right=0.98, top=0.85, bottom=0.25)
        self.canvas.draw_idle()

    def set_height(self, new_height_inches: float):
        pixel_height = int(new_height_inches * self.figure.dpi)
        self.canvas_widget.configure(height=pixel_height)
        self.canvas.draw_idle()
