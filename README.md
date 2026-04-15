# ECG_frequency_analysis
A university project involving group work to create a project for a client
Desktop application for reading and analyzing ECG files in WFDB format (.hea, .dat, .atr)

## Local run

1. Install requirements:
   pip install -r requirements.txt

2. Run main script:
   python main.py

## Build

Build consists of two phases:

1. EXE compilation:
   Run:
   ```
   python ./build_config/build.py
   ```
   select "Build Windows Executable (Bundled Folder)"
   
   Compiled executable will be located at: ./build_config/build/build_win32 (alongside required dependencies)

2. Installer compilation:
   [Inno Setup](https://jrsoftware.org/isdl.php) is needed for this part of build
   Open file ./build_config/installer_setup.iss in Inno Setup Compiler and press "Compile".
   
   Compiled installer will be located at: ./build_config/build/installer_win32