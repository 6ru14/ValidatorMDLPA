import os 
import re
import sys
import importlib.util

class Application():
    def __init__(self, py_file: str, resources_folder: str, app_folder: str):
        # the base dir will depend if the file is .exe or .py type and this is accounted here
        if getattr(sys, 'frozen', False):
            # Runs as an exe
            base_dir = os.path.dirname(sys.executable)
        else:
            # Runs as .py script
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        # Path of the resources folder
        self.resources_path = os.path.join(base_dir, resources_folder) 
        # The path for the newest version of the code 
        app_path = os.path.join(self.resources_path, self.version(), app_folder)
        # For the app to run correctly
        sys.path.append(app_path)
        # Loads and runs the application
        spec = importlib.util.spec_from_file_location(app_folder, os.path.join(app_path, py_file))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.UserInterface()
    
    def version(self):
        # The list of all the version folders
        version_folders = [v for v in os.listdir(self.resources_path) if re.match(r'^\d+\.\d+\.\d+$', v)]
        # Sorts and gets the latest version
        latest_version = sorted(version_folders, key=lambda v: tuple(map(int, v.split('.'))))[-1]
        # Returns the latest version
        return latest_version
    
if __name__ == '__main__':
    Application(
        py_file = 'UI.py',
        resources_folder = 'resources',
        app_folder = 'app'
        ) 