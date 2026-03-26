import tkinter as tk

class SettingsFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        btn_container = tk.Frame(self, bg=self['bg'])
        btn_container.pack(expand=True)

        self.previous_button = tk.Button(btn_container, text="<<<", cursor="hand2", command=None)
        self.move_left_button = tk.Button(btn_container, text="<", cursor="hand2", command=None)
        self.move_right_button = tk.Button(btn_container, text=">", cursor="hand2", command=None)
        self.next_button = tk.Button(btn_container, text=">>>", cursor="hand2", command=None)
        self.add_annotation_button = tk.Button(btn_container, text="+ Add annotation", cursor="hand2", background="lightblue", command=None)

        self.previous_button.pack(side=tk.LEFT, padx=2)
        self.move_left_button.pack(side=tk.LEFT, padx=2)
        self.move_right_button.pack(side=tk.LEFT, padx=2)
        self.next_button.pack(side=tk.LEFT, padx=2)
        self.add_annotation_button.pack(side=tk.LEFT, padx=(10))



