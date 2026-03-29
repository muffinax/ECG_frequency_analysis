import tkinter as tk
import sys
import os
from gui import MainWindow

def main() -> None:
    root = tk.Tk()
    app = MainWindow(master=root)

    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        if os.path.exists(target_file):
            app.file_manager.open_file(target_file)
            app.update()

    root.mainloop()

if __name__ == "__main__":
    main()