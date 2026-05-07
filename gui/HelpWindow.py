import tkinter as tk
from tkinter import ttk


class HelpWindow(tk.Toplevel):
    def __init__(self, master: tk.Widget) -> None:
        super().__init__(master)

        self.title("Instrukcja obsługi i Pomoc")
        self.geometry("700x550")
        self.minsize(500, 400)

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

        # Wpisywanie treści
        self._add_text("Krok 1: Rozpoczęcie pracy\n", "header")
        self._add_text("Aby rozpocząć pracę z programem, musisz najpierw wczytać dane sygnału.\n")
        self._add_text("1. Wybierz z górnego menu ", "bullet")
        self._add_text("Plik -> Otwórz", "bold")
        self._add_text(".\n")
        self._add_text("2. Wskaż obsługiwany plik na dysku komputera.\n", "bullet")
        self._add_text(
            "3. Po wczytaniu, na górnym pasku pojawią się informacje o pacjencie, a na środku wyrysują się wykresy EKG.\n",
            "bullet")

        self._add_text("Krok 2: Nawigacja po sygnale\n", "header")
        self._add_text("Na dole ekranu znajduje się panel sterowania, który pozwala przemieszczać się po zapisie:\n")
        self._add_text("⏮ ", "bold")
        self._add_text("- Przeskok na sam początek nagrania.\n", "bullet")
        self._add_text("⏪ ", "bold")
        self._add_text("- Skok do poprzedniej wyfiltrowanej adnotacji (centruje ekran na pobudzeniu).\n", "bullet")
        self._add_text("◀ ", "bold")
        self._add_text("- Przesunięcie widoku o jedną klatkę w lewo.\n", "bullet")
        self._add_text("▶ (Play/Pauza) ", "bold")
        self._add_text("- Automatyczne, płynne odtwarzanie sygnału.\n", "bullet")
        self._add_text("▶ (Klatka w prawo) ", "bold")
        self._add_text("- Przesunięcie widoku o jedną klatkę w prawo.\n", "bullet")
        self._add_text("⏩ ", "bold")
        self._add_text("- Skok do następnej wyfiltrowanej adnotacji.\n", "bullet")
        self._add_text("⏭ ", "bold")
        self._add_text("- Przeskok na sam koniec nagrania.\n", "bullet")
        self._add_text(
            "Możesz również wpisać konkretny czas w okienku po prawej stronie i kliknąć 'Idź', aby natychmiast przeskoczyć w wybrane miejsce.\n",
            "bullet")

        self._add_text("Krok 3: Analiza EKG i Widmo FFT\n", "header")
        self._add_text("Program pozwala na dynamiczną analizę wycinków sygnału:\n")
        self._add_text("• Zaznaczanie myszką: ", "bold")
        self._add_text(
            "Kliknij i przeciągnij lewym przyciskiem myszy po wykresie EKG, aby zaznaczyć interesujący Cię obszar (podświetli się na niebiesko).\n",
            "bullet")
        self._add_text("• Widmo częstotliwościowe (FFT): ", "bold")
        self._add_text(
            "Jeśli analiza jest włączona (opcja dostępna w menu 'Analiza'), na dole automatycznie wyrysuje się widmo dla zaznaczonego fragmentu.\n",
            "bullet")
        self._add_text("• Pełna analiza: ", "bold")
        self._add_text(
            "Wybierz z górnego menu 'Analiza -> Analiza dla całego pliku', aby program wygenerował widmo dla całości zapisu w ułamku sekundy.\n",
            "bullet")

        self._add_text("Krok 4: Panel Adnotacji (Prawa strona)\n", "header")
        self._add_text(
            "Panel po prawej stronie wyświetla listę wykrytych pobudzeń (adnotacji) dla aktualnie widocznego okna.\n")
        self._add_text("• Filtracja: ", "bold")
        self._add_text("Użyj rozwijanej listy, aby pokazać tylko konkretny typ adnotacji (np. 'V').\n", "bullet")
        self._add_text("• Wizualizacja na wykresie: ", "bold")
        self._add_text(
            "Wszystkie widoczne na liście adnotacje mają swoje małe zielone znaczniki na górnej krawędzi wykresu EKG.\n",
            "bullet")
        self._add_text("• Podświetlanie szczegółów: ", "bold")
        self._add_text(
            "Kliknięcie w dany wiersz na liście (lub użycie przycisków ⏪/⏩) narysuje czerwoną linię pionową na wykresie, dokładnie w miejscu wystąpienia tego zdarzenia.\n",
            "bullet")

        # Zablokowanie edycji tekstu przez użytkownika
        self.text_box.config(state=tk.DISABLED)

    def _add_text(self, text, tag=None):
        if tag:
            self.text_box.insert(tk.END, text, tag)
        else:
            self.text_box.insert(tk.END, text)