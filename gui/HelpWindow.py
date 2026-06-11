import tkinter as tk
from tkinter import ttk
import localisation


class HelpWindow(tk.Toplevel):
    def __init__(self, master: tk.Widget) -> None:
        super().__init__(master)

        self.title(localisation.name_resolver.get("help_window_title"))
        self.geometry("750x650")
        self.minsize(550, 500)

        # Ustawiamy okno tak, by nie blokowało programu (użytkownik może czytać i klikać w tle)
        self.transient(master)

        # Główny kontener
        main_frame = tk.Frame(self, bg="#ffffff")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tytuł
        lbl_title = tk.Label(main_frame, text=localisation.name_resolver.get("help_window_guide_title"), font=("Arial", 16, "bold"), bg="#ffffff")
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
        btn_close = ttk.Button(main_frame, text=localisation.name_resolver.get("help_window_close_btn"), command=self.destroy)
        btn_close.pack(pady=(10, 0))

        self._insert_content()

    def _insert_content(self):
        # Konfiguracja stylów (tagów) dla tekstu
        self.text_box.tag_configure("header", font=("Arial", 14, "bold"), spacing1=15, spacing3=5, foreground="#2c3e50")
        self.text_box.tag_configure("bold", font=("Arial", 11, "bold"))
        self.text_box.tag_configure("bullet", lmargin1=20, lmargin2=35, spacing1=3)

        # Krok 1
        self._add_text(localisation.name_resolver.get("help_window_step1_header"), "header")
        self._add_text(localisation.name_resolver.get("help_window_step1_text1"))
        self._add_text(localisation.name_resolver.get("help_window_step1_menu_path"), "bold")
        self._add_text(localisation.name_resolver.get("help_window_step1_text2"))

        # Używamy tych samych kodów co w SettingsFrame
        self._add_text("\u23EE / \u23ED ", "bold")
        self._add_text(localisation.name_resolver.get("help_window_step1_bullet1"), "bullet")

        self._add_text("\u23EA / \u23E9 ", "bold")
        self._add_text(localisation.name_resolver.get("help_window_step1_bullet2"), "bullet")

        self._add_text("\u25C0 / \u25B6 ", "bold")
        self._add_text(localisation.name_resolver.get("help_window_step1_bullet3"), "bullet")

        self._add_text("\u25B6 / \u23F8 ", "bold")
        self._add_text(localisation.name_resolver.get("help_window_step1_bullet4"), "bullet")

        self._add_text(localisation.name_resolver.get("help_window_step1_bullet5"), "bullet")
        self._add_text(localisation.name_resolver.get("help_window_step1_zoom_lbl"), "bold")
        self._add_text(localisation.name_resolver.get("help_window_step1_zoom_text"), "bullet")

        # Krok 2
        self._add_text(localisation.name_resolver.get("help_window_step2_header"), "header")
        self._add_text(localisation.name_resolver.get("help_window_step2_text1"))
        self._add_text(localisation.name_resolver.get("help_window_step2_menu_path"), "bold")
        self._add_text(localisation.name_resolver.get("help_window_step2_text2"))
        self._add_text(localisation.name_resolver.get("help_window_step2_bullet1_lbl"), "bold")
        self._add_text(localisation.name_resolver.get("help_window_step2_bullet1_text"), "bullet")
        self._add_text(localisation.name_resolver.get("help_window_step2_bullet2_lbl"), "bold")
        self._add_text(localisation.name_resolver.get("help_window_step2_bullet2_text"), "bullet")

        # Krok 3
        self._add_text(localisation.name_resolver.get("help_window_step3_header"), "header")
        self._add_text(localisation.name_resolver.get("help_window_step3_text1"))
        self._add_text(localisation.name_resolver.get("help_window_step3_bullet1_lbl"), "bold")
        self._add_text(localisation.name_resolver.get("help_window_step3_bullet1_text"), "bullet")

        self._add_text(localisation.name_resolver.get("help_window_step3_bullet2_lbl"), "bold")
        self._add_text(localisation.name_resolver.get("help_window_step3_bullet2_text1"), "bullet")
        self._add_text(localisation.name_resolver.get("help_window_step3_menu_path"), "bold")
        self._add_text(localisation.name_resolver.get("help_window_step3_bullet2_text2"), "bullet")

        self._add_text(localisation.name_resolver.get("help_window_step3_fft_lbl"), "bold")
        self._add_text(localisation.name_resolver.get("help_window_step3_fft_text"), "bullet")

        self._add_text(localisation.name_resolver.get("help_window_step3_action_lbl"), "bold")
        self._add_text(localisation.name_resolver.get("help_window_step3_action_text"), "bullet")

        self._add_text(localisation.name_resolver.get("help_window_step3_extra_lbl"), "bold")
        self._add_text(localisation.name_resolver.get("help_window_step3_edit_lbl"), "bold")
        self._add_text(localisation.name_resolver.get("help_window_step3_edit_text"), "bullet")
        self._add_text(localisation.name_resolver.get("help_window_step3_bulk_lbl"), "bold")
        self._add_text(localisation.name_resolver.get("help_window_step3_bulk_text"), "bullet")

        self._add_text(localisation.name_resolver.get("help_window_step4_header"), "header")
        self._add_text(localisation.name_resolver.get("help_window_step4_text1"))
        self._add_text(localisation.name_resolver.get("help_window_step4_menu_save"), "bold")
        self._add_text(localisation.name_resolver.get("help_window_step4_text_or"))
        self._add_text(localisation.name_resolver.get("help_window_step4_menu_save_as"), "bold")
        self._add_text(localisation.name_resolver.get("help_window_step4_text2"))

        self._add_text(localisation.name_resolver.get("help_window_step4_bullet1"), "bullet")
        self._add_text(localisation.name_resolver.get("help_window_step4_bullet2"), "bold")
        self._add_text(localisation.name_resolver.get("help_window_step4_bullet3"))

        self.text_box.config(state=tk.DISABLED)

    def _add_text(self, text, tag=None):
        if tag:
            self.text_box.insert(tk.END, text, tag)
        else:
            self.text_box.insert(tk.END, text)