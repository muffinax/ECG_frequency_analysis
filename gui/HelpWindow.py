import tkinter as tk
from tkinter import ttk


class HelpWindow(tk.Toplevel):
    def __init__(self, master: tk.Widget) -> None:
        super().__init__(master)

        self.title("Instrukcja obsługi i Pomoc")
        self.geometry("700x600")
        self.minsize(500, 450)

        # Ustawiamy okno tak, by nie blokowało programu (użytkownik może czytać i klikać w tle)
        self.transient(master)

        # Główny kontener
        main_frame = tk.Frame(self, bg="#ffffff")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tytuł
        lbl_title = tk.Label(main_frame, text="Przewodnik po aplikacji EKG", font=("Arial", 16, "bold"), bg="#ffffff")
        lbl_title.pack(pady=(0, 10))

        # Pole tekstowe z paskiem przewijania
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_box = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                                font=("Arial", 11), bg="#f9f9f9", padx=15, pady=15)
        self.text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_box.yview)

        # Przycisk Zamknij
        btn_close = ttk.Button(main_frame, text="Zrozumiałem, zamknij", command=self.destroy)
        btn_close.pack(pady=(10, 0))

        self._insert_content()

    def _insert_content(self):
        # Konfiguracja stylów (tagów) dla tekstu
        self.text_box.tag_configure("header", font=("Arial", 14, "bold"), spacing1=15, spacing3=5, foreground="#2c3e50")
        self.text_box.tag_configure("bold", font=("Arial", 11, "bold"))
        self.text_box.tag_configure("bullet", lmargin1=20, lmargin2=35, spacing1=3)

        # Krok 1
        self._add_text("Krok 1: Wczytywanie pliku i Nawigacja\n", "header")
        self._add_text("Aby rozpocząć pracę, wybierz z górnego menu ")
        self._add_text("Plik -> Otwórz", "bold")
        self._add_text(". Po wczytaniu pliku użyj dolnego panelu do poruszania się po sygnale:\n")
        self._add_text("⏮ / ⏭ ", "bold")
        self._add_text("- Przeskok na sam początek / koniec nagrania.\n", "bullet")
        self._add_text("⏪ / ⏩ ", "bold")
        self._add_text("- Skok do poprzedniej / następnej adnotacji. Strzałki nawigują po tej tabeli z prawego panelu, która była ostatnio używana.\n", "bullet")
        self._add_text("◀ / ▶ ", "bold")
        self._add_text("- Przesunięcie widoku okna w lewo / prawo.\n", "bullet")
        self._add_text("▶ / ⏸ ", "bold")
        self._add_text("- Automatyczne odtwarzanie (Play) i zatrzymywanie (Pauza) sygnału.\n", "bullet")
        self._add_text("Możesz również wpisać konkretny czas w sekundach w polu po prawej i kliknąć 'Idź'.\n", "bullet")

        # Krok 2
        self._add_text("Krok 2: Ustawienia widoku (Parametry)\n", "header")
        self._add_text("Możesz swobodnie przybliżać sygnał i zmieniać zakres widoku. Wybierz z menu ")
        self._add_text("Analiza -> Parametry", "bold")
        self._add_text(":\n")
        self._add_text("• Rozmiar okna: ", "bold")
        self._add_text("Zmienia ilość sekund aktualnie wyświetlanych na ekranie (oś X).\n", "bullet")
        self._add_text("• Amplituda: ", "bold")
        self._add_text("Zmienia zakres wykresu w pionie (oś Y). Pozwala to na przybliżenie sygnału.\n", "bullet")
        self._add_text("Uwaga: Wykres automatycznie się przeskaluje zachowując proporcje medycznej siatki EKG!\n", "bullet")

        # Krok 3
        self._add_text("Krok 3: Analiza AI i Tabele Adnotacji\n", "header")
        self._add_text("Panel po prawej stronie zawiera dwie tabele, które grupują wykryte zdarzenia.\n")
        self._add_text("• Górna tabela (Adnotacje Czasowe): ", "bold")
        self._add_text("Zwykłe znaczniki punktowe. Kliknięcie w nie narysuje czerwoną linię pionową w miejscu zdarzenia i wyczyści widma FFT.\n", "bullet")
        self._add_text("• Dolna tabela (Adnotacje AI): ", "bold")
        self._add_text("Aby je wygenerować, użyj menu ", "bullet")
        self._add_text("Analiza -> Analiza dla całego pliku", "bold")
        self._add_text(". Sztuczna inteligencja przeanalizuje sygnał i uzupełni dolną listę.\n")
        self._add_text("Kliknięcie w adnotację z AI zaznaczy na niebiesko cały przedział sygnału i automatycznie wyświetli dla niego widmo częstotliwościowe (FFT).\n", "bullet")

        # Krok 4
        self._add_text("Krok 4: Zapisywanie zmian\n", "header")
        self._add_text("Aby zachować wyniki, wybierz z górnego menu ")
        self._add_text("Plik -> Zapisz", "bold")
        self._add_text(" lub ")
        self._add_text("Zapisz jako", "bold")
        self._add_text(".\n")
        self._add_text("Plik zostanie zapisany na dysku. Będzie on zawierał wszystkie wygenerowane przez sztuczną inteligencję adnotacje, dzięki czemu nie musisz powtarzać analizy przy ponownym otwarciu pliku.\n", "bullet")

        # Zablokowanie edycji tekstu przez użytkownika
        self.text_box.config(state=tk.DISABLED)

    def _add_text(self, text, tag=None):
        if tag:
            self.text_box.insert(tk.END, text, tag)
        else:
            self.text_box.insert(tk.END, text)