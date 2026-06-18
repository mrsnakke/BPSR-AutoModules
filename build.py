import os
import sys
import PyInstaller.__main__

def build_app():
    print("Starting PyInstaller build process...")
    
    # Define files and folders to include
    # On Windows, PyInstaller uses ';' to separate source and destination paths
    assets = [
        ('gui/images', 'gui/images'),
        ('cpp_extension/module_optimizer_cpp.cp314-win_amd64.pyd', 'cpp_extension'),
    ]
    
    # Construct PyInstaller arguments
    args = [
        'gui/main_window.py',                     # Entry point
        '--name=BPSR_Module_Optimizer',           # Output executable name
        '--onefile',                              # Build as a single executable file
        '--noconsole',                            # Do not show terminal window
        '--icon=icon.ico',                        # Executable icon
        '--paths=.',                              # Include current directory in import search path
        '--clean',                                # Clean PyInstaller cache before building
    ]
    
    # Add data files/folders
    for src, dest in assets:
        if os.path.exists(src):
            args.append(f'--add-data={src};{dest}')
            print(f"Bundling asset: {src} -> {dest}")
        else:
            print(f"Warning: Asset {src} not found!")

    print(f"Running PyInstaller with arguments: {' '.join(args)}")
    PyInstaller.__main__.run(args)
    print("Build completed successfully!")

if __name__ == '__main__':
    build_app()
