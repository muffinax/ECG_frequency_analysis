import sys
import os
import subprocess
import venv

# Enforce Windows only
if sys.platform != "win32":
    sys.exit("Error: This build script is strictly for Windows.")

# =====================================================================
# BUILD CONFIG
# =====================================================================
# App specification
APP_NAME: str = "ECG Analyzer"
VERSION: str = "0.4.0"
AUTHOR: str = "Marta Witkowska, Filip Romanowski, Aleksander Dziągwa, Kacper Bytner, Wojciech Biskup"
DESCRIPTION: str = "ECG Frequency Analysis Tool"
EXECUTABLE_NAME: str = "ecg_analyzer.exe"

# Directories
BUILD_DIR: str = os.path.dirname(os.path.abspath(__file__))  # build base directory
ROOT_DIR: str = os.path.abspath(os.path.join(BUILD_DIR, ".."))  # project base directory
TARGET_BUILD_DIR: str = os.path.join(BUILD_DIR, "build")  # build target directory

# Key files/dirs
MAIN_SCRIPT: str = os.path.join(ROOT_DIR, "main.py")  # main executable
RUNTIME_RESOURCES_DIR: str = os.path.join(ROOT_DIR, "resources")  # bundled resources


# Build specification for .exe
BUILD_EXE_OPTIONS: dict = {
    "packages": ["tkinter"],
    "include_files": [(RUNTIME_RESOURCES_DIR, "resources")] if os.path.exists(RUNTIME_RESOURCES_DIR) else [],
    "excludes": [
        "PyQt5", "PyQt6", "PySide2", "PySide6",
        "setuptools", "wheel", "_distutils_hack", "pip",
        "unittest", "curses", "xmlrpc",
        "sqlite3",
        "requests", "urllib3", "certifi", "idna", "charset_normalizer"
    ],
    "optimize": 2,
    "build_exe": os.path.join(TARGET_BUILD_DIR, "build_win32")
}

# Build venv specification
VENV_DIR: str = os.path.join(TARGET_BUILD_DIR, "venv_win32")
VENV_PYTHON: str = os.path.join(VENV_DIR, "Scripts", "python.exe")

# =====================================================================
# BUILD VENV SETUP
# =====================================================================

current_python: str = os.path.normcase(os.path.normpath(path=sys.executable))
target_python: str = os.path.normcase(os.path.normpath(path=VENV_PYTHON))

if current_python != target_python:
    print("--- Bootstrapping Build Environment (Windows) ---")

    if not os.path.exists(path=VENV_DIR):
        print(f"Creating isolated virtual environment at: {VENV_DIR}")
        try:
            venv.create(env_dir=VENV_DIR, with_pip=True)
        except Exception as e:
            print(f"Error creating venv: {e}")
            print("\n[Hint] Ensure Python is installed and added to PATH.")
            print("If you see 'scripts are disabled', run PowerShell as Admin and type:")
            print("\tSet-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser")
            sys.exit(1)

        main_req_file: str = os.path.join(ROOT_DIR, "requirements.txt")
        build_req_file: str = os.path.join(BUILD_DIR, "requirements-build.txt")

        for req_file in [main_req_file, build_req_file]:
            if os.path.exists(path=req_file):
                print(f"Installing dependencies from {req_file}...")
                subprocess.run(
                    args=[VENV_PYTHON, "-m", "pip", "install", "-r", req_file],
                    check=True
                )
            else:
                print(f"Notice: {req_file} not found. Skipping.")

    # Re-launch this script using the venv's Python, passing along any arguments (like 'build_exe')
    sys.exit(subprocess.call(args=[VENV_PYTHON, __file__] + sys.argv[1:]))

# =====================================================================
# BUILD MENU
# =====================================================================
if len(sys.argv) == 1:
    def run_interactive_menu() -> None:
        print("\n=== ECG Analyzer Build ===")
        print("[1] Build Windows Executable (Bundled Folder)")
        print("[0] Cancel and Exit")

        user_choice: str = input("\nSelect a build target: ").strip()

        if user_choice == "0":
            print("Exiting.")
            sys.exit(0)

        elif user_choice == "1":
            selected_command = [sys.executable, __file__, "build_exe"]
            print(f"\n>>> Executing: {' '.join(selected_command)}\n")
            try:
                subprocess.run(args=selected_command, check=True)
                print("\n=== Build Completed Successfully! ===")
            except subprocess.CalledProcessError:
                print("\n=== Build Failed! ===")
        else:
            print("Invalid choice. Exiting.")
            sys.exit(1)


    run_interactive_menu()
    sys.exit(0)

# =====================================================================
# CX_FREEZE BUILD CONFIG
# =====================================================================
sys.path.insert(0, ROOT_DIR)

from cx_Freeze import setup, Executable

setup(
    name=APP_NAME,
    version=VERSION,
    author=AUTHOR,
    description=DESCRIPTION,
    options={
        "build_exe": BUILD_EXE_OPTIONS,
    },
    executables=[
        Executable(
            script=MAIN_SCRIPT,
            base="gui",
            target_name=EXECUTABLE_NAME,
        )
    ]
)