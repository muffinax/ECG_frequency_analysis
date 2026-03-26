import tkinter as tk

from gui.MainWindow import MainWindow


def main():
    root=tk.Tk()
    app=MainWindow(root)

    test_time = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    test_amplitude = [0.0, 0.2, 1.5, -0.4, 0.1, 0.0]
    app.frame_ecg.update_chart(test_time, test_amplitude)

    root.mainloop()


if __name__=="__main__":
    main()