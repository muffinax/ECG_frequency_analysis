import tkinter as tk
from gui import MainWindow

def main() -> None:
    root = tk.Tk()
    app = MainWindow(master=root)
    root.mainloop()

if __name__ == "__main__":
    main()