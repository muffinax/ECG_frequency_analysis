import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MultipleLocator, FuncFormatter

import localisation

class SingleFFTCanvas(tk.Frame):
    def __init__(self, master, lead_name: str, plot_height: float = 2.5, **kwargs):
        super().__init__(master, **kwargs)
        self.lead_name = lead_name

        self.figure = Figure(figsize=(6, plot_height), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

    def update_chart(self, fft_data):
        """Metoda do rysowania drugiego zestawu danych (np. widma częstotliwościowego)"""
        self.figure.clear()

        #if no analisys
        if not fft_data or len(fft_data) != 2:
            self.canvas.draw()
            return

        freqs, magnitudes = fft_data

        ax = self.figure.add_subplot(1, 1, 1)

        # Rysowanie linii wykresu (wybieramy np. ładny niebieski kolor dla odróżnienia od EKG)
        ax.plot(freqs, magnitudes, color='#0052cc', linewidth=1)

        # Opcjonalnie: zacieniowanie obszaru pod wykresem
        ax.fill_between(freqs, magnitudes, color='#0052cc', alpha=0.15)

        # Etykiety i tytuł
        ax.set_title(f"{self.lead_name} - Widmo Amplitudowe (FFT)", fontsize=8, loc='left',
                     bbox=dict(facecolor='#E0E0E0', edgecolor='none', alpha=0.8, pad=4))

        ax.set_ylabel("Amplituda widma")
        ax.set_xlabel("Częstotliwość [Hz]")

        # FFT często rysuje się tylko dla wartości dodatnich, od zera w górę
        ax.set_xlim(left=0, right=max(freqs) if len(freqs) > 0 else 1)
        ax.set_ylim(bottom=0)  # Amplituda nie spada poniżej zera

        ax.grid(True, linestyle=':', alpha=0.6)

        # Używamy twardych marginesów (zamiast tight_layout), żeby napisy się nie nakładały przy zoomie
        self.figure.subplots_adjust(left=0.1, right=0.98, top=0.85, bottom=0.25)
        self.canvas.draw_idle()

    def set_height(self, new_height_inches: float):
        pixel_height = int(new_height_inches * self.figure.dpi)
        self.canvas_widget.configure(height=pixel_height)
        self.canvas.draw_idle()