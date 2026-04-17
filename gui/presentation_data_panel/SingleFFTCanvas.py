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

        self.ax1 = self.figure.add_subplot(1, 2, 1)
        self.ax2 = self.figure.add_subplot(1, 2, 2)

    def update_chart(self, fft_data):
        """Metoda do rysowania drugiego zestawu danych (np. widma częstotliwościowego)"""
        self.ax1.clear()

        #if no analisys
        if not fft_data or len(fft_data) != 2:
            self.canvas.draw()
            return

        freqs, magnitudes = fft_data

        # Rysowanie linii wykresu (wybieramy np. ładny niebieski kolor dla odróżnienia od EKG)
        self.ax1.plot(freqs, magnitudes, color='#0052cc', linewidth=1)

        # Opcjonalnie: zacieniowanie obszaru pod wykresem
        self.ax1.fill_between(freqs, magnitudes, color='#0052cc', alpha=0.15)

        # Etykiety i tytuł
        self.ax1.set_title(f"{self.lead_name} - Widmo Amplitudowe (FFT)", fontsize=8, loc='left',
                     bbox=dict(facecolor='#E0E0E0', edgecolor='none', alpha=0.8, pad=4))

        self.ax1.set_ylabel("Amplituda widma")
        self.ax1.set_xlabel("Częstotliwość [Hz]")

        # FFT często rysuje się tylko dla wartości dodatnich, od zera w górę
        self.ax1.set_xlim(left=0, right=max(freqs) if len(freqs) > 0 else 1)
        self.ax1.set_ylim(bottom=0)  # Amplituda nie spada poniżej zera

        self.ax1.grid(True, linestyle=':', alpha=0.6)

        # Używamy twardych marginesów (zamiast tight_layout), żeby napisy się nie nakładały przy zoomie
        self.figure.subplots_adjust(left=0.1, right=0.98, top=0.85, bottom=0.25)
        self.canvas.draw_idle()

    def update_vector_chart(self, fft_data):
        """Metoda do rysowania drugiego zestawu danych (np. widma częstotliwościowego)"""
        self.ax2.clear()

        #if no analisys
        if not fft_data or len(fft_data) != 2:
            self.canvas.draw()
            return

        freqs, magnitudes = fft_data

        # Rysowanie linii wykresu (wybieramy np. ładny niebieski kolor dla odróżnienia od EKG)
        self.ax2.plot(freqs, magnitudes, color='#0052cc', linewidth=1)

        # Opcjonalnie: zacieniowanie obszaru pod wykresem
        self.ax2.fill_between(freqs, magnitudes, color='#0052cc', alpha=0.15)

        # Etykiety i tytuł
        self.ax2.set_title(f"{self.lead_name} - Widmo Amplitudowe (FFT)", fontsize=8, loc='left',
                     bbox=dict(facecolor='#E0E0E0', edgecolor='none', alpha=0.8, pad=4))

        self.ax2.set_ylabel("Amplituda widma")
        self.ax2.set_xlabel("Częstotliwość [Hz]")

        # FFT często rysuje się tylko dla wartości dodatnich, od zera w górę
        self.ax2.set_xlim(left=0, right=max(freqs) if len(freqs) > 0 else 1)
        self.ax2.set_ylim(bottom=0)  # Amplituda nie spada poniżej zera

        self.ax2.grid(True, linestyle=':', alpha=0.6)

        # Używamy twardych marginesów (zamiast tight_layout), żeby napisy się nie nakładały przy zoomie
        self.figure.subplots_adjust(left=0.1, right=0.98, top=0.85, bottom=0.25)
        self.canvas.draw_idle()

    def set_height(self, new_height_inches: float):
        pixel_height = int(new_height_inches * self.figure.dpi)
        self.canvas_widget.configure(height=pixel_height)
        self.canvas.draw_idle()