import tkinter as tk
import sys
import os

from gui.MainWindow import MainWindow


def main() -> None:
    root = tk.Tk()

    app = MainWindow(master=root)

    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        if os.path.exists(target_file):
            app.open_file_dialog(target_file)

    root.mainloop()


if __name__ == "__main__":
    main()