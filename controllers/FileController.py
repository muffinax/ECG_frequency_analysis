import traceback
from tkinter import messagebox
import localisation
from processor.preproc_manager import PreprocManager


class FileController:
    def __init__(self, main_controller):
        self.main_controller = main_controller

        # Local references for easier access
        self.file_manager = main_controller.file_manager
        self.display_manager = main_controller.display_manager
        self.navigation_manager = main_controller.navigation_manager
        self.analysis_manager = main_controller.analysis_manager

    def cmd_open_file(self, filepath: str | None = None):
        """
        Opening file and preparing everything for it
        """
        try:
            if filepath:
                self.file_manager.open_file(filepath=filepath)
            else:
                self.file_manager.open_file_system_gui()

            if self.file_manager.opened() and self.file_manager.signals:
                fs = self.file_manager.sampling_frequency

                #creating new PreprocManager
                self.main_controller.preproc_manager = PreprocManager(fs)

                self.display_manager.reset_to_defaults(self.file_manager.get_available_leads())
                self.display_manager.show_frequency_analysis = True

                self.navigation_manager.reset_for_new_file(fs=fs, total_samples=self.file_manager.get_total_samples())
                self.analysis_manager.reset_to_defaults()

                if self.main_controller.view:
                    self.main_controller.view.reset_ui_state()

                self.main_controller.refresh_view()

        except Exception as error_obj:
            traceback.print_exc()
            messagebox.showerror(
                title=localisation.name_resolver.get("messagebox_error"),
                message=f"Błąd: {str(error_obj)}"
            )

    def cmd_save_file(self):
        """
        Saving file
        """
        try:
            self.file_manager.save_file(self.file_manager.filepath)
        except Exception as error_obj:
            messagebox.showerror(localisation.name_resolver.get("messagebox_error"), str(error_obj))

    def cmd_save_file_as(self):
        """
        Saving file as
        """
        try:
            self.file_manager.save_file_system_gui()
        except Exception as error_obj:
            messagebox.showerror(localisation.name_resolver.get("messagebox_error"), str(error_obj))