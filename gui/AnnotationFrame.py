import tkinter as tk

class AnnotationFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.label = tk.Label(self, text="Detected Annotations", font=("Arial", 14, "bold"))
        self.label.pack(pady=10)
