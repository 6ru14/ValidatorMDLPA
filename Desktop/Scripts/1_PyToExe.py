import os
import shutil
import logging
from pathlib import Path
import hashlib
import subprocess
import sys
from typing import Tuple, Optional, List

class PyExe:
    def __init__(self):
        # Configure logging
        self._setup_logging()
        
        # Initialize paths
        self.base_dir = Path(__file__).resolve().parent.parent
        self.test_path = self.base_dir / "Test"
        self.middleware_path = self.base_dir / "Middleware"
        
        # Ensure directories exist
        self._ensure_directory_exists(self.test_path)
        self._ensure_directory_exists(self.middleware_path)
        
        try:
            logo_path = self.move_logo()
            file_path = self.check_moved()
            if file_path and logo_path:
                self.compile_file(file_path=file_path, logo_path=logo_path)
            else:
                logging.error("Required files not found for compilation")
        except Exception as e:
            logging.exception("Failed to create executable")
            raise

    def _setup_logging(self):
        """Configure logging for the application."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('pyexe.log')
            ]
        )

    def _ensure_directory_exists(self, path: Path):
        """Ensure a directory exists, create if it doesn't."""
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logging.error(f"Failed to create directory {path}: {e}")
            raise

    def move_logo(self) -> Optional[Path]:
        """Move logo file from test to middleware directory."""
        logo_name = 'logo.ico'
        logo_path = self.test_path / logo_name
        to_path = self.middleware_path / logo_name
        
        if not logo_path.exists():
            logging.error(f"Source logo file not found at {logo_path}")
            return None
            
        try:
            if to_path.exists():
                logging.info("Logo file already exists in target location")
            else:
                shutil.copy(logo_path, to_path)
                logging.info(f"Logo file copied to {to_path}")
            return to_path
        except IOError as e:
            logging.error(f"Failed to copy logo file: {e}")
            return None

    def check_exists(self) -> Tuple[bool, Optional[Path], Optional[Path]]:
        """Check if main.py exists in test directory."""
        file_name = "main.py"
        file_path = self.test_path / file_name
        to_path = self.middleware_path / file_name
        
        if file_path.exists():
            logging.info(f'File "{file_name}" exists at {file_path}')
            return True, file_path, to_path
        else:
            logging.error(f'File "{file_name}" not found at {file_path}')
            return False, None, None

    def get_file_hash(self, filepath: Path) -> Optional[str]:
        """Calculate SHA256 hash of a file."""
        if not filepath.exists():
            return None
            
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(4096):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except IOError as e:
            logging.error(f"Failed to calculate file hash for {filepath}: {e}")
            return None

    def check_moved(self) -> Optional[Path]:
        """Check if main.py is properly moved to middleware directory."""
        status, src_path, dest_path = self.check_exists()
        
        if not status or not src_path or not dest_path:
            return None
            
        try:
            src_hash = self.get_file_hash(src_path)
            dest_hash = self.get_file_hash(dest_path)
            
            if src_hash and dest_hash:
                if src_hash == dest_hash:
                    logging.info("File already exists with matching hash")
                else:
                    shutil.copy(src_path, dest_path)
                    logging.info("File copied with updated content")
            else:
                shutil.copy(src_path, dest_path)
                logging.info("File copied (hash check unavailable)")
                
            return dest_path
        except IOError as e:
            logging.error(f"Failed to copy file: {e}")
            return None

    def compile_file(self, file_path: Path, logo_path: Path):
        """Compile the Python file to executable using PyInstaller."""
        # Hidden imports configuration
        hidden_imports = [
            'customtkinter',
            'filetype',
            'fiona',
            'geopandas',
            'pandas',
            'pillow',
            'requests',
            'shapely'
        ]
        
        # Additional PyInstaller options
        pyinstaller_options = {
            'onefile': True,
            'name': 'Validator',
            'noconsole': True,
            'icon': str(logo_path),
            'distpath': '.',
            'clean': True  # Clean cache and temporary files
        }

        try:
            # Change to middleware directory
            os.chdir(self.middleware_path)
            logging.info(f"Working directory: {os.getcwd()}")

            # Build PyInstaller command
            pyinstaller_cmd = ["pyinstaller"]
            
            # Add standard options
            if pyinstaller_options['onefile']:
                pyinstaller_cmd.append("--onefile")
            if pyinstaller_options['noconsole']:
                pyinstaller_cmd.append("--noconsole")
            if pyinstaller_options['clean']:
                pyinstaller_cmd.append("--clean")
                
            pyinstaller_cmd.extend([
                f"--name={pyinstaller_options['name']}",
                f"--icon={pyinstaller_options['icon']}",
                "--distpath", pyinstaller_options['distpath'],
                str(file_path)
            ])
            
            # Add hidden imports
            for hidden_import in hidden_imports:
                pyinstaller_cmd.append(f"--hidden-import={hidden_import}")
            
            logging.info(f"Running PyInstaller command: {' '.join(pyinstaller_cmd)}")
            
            # Run PyInstaller with timeout (60 seconds)
            result = subprocess.run(
                pyinstaller_cmd,
                check=True,
                text=True,
                capture_output=True
            )
            
            logging.info("Executable created successfully")
            logging.debug(f"PyInstaller output:\n{result.stdout}")
            
            # Clean up temporary files
            self.cleanup()

        except subprocess.TimeoutExpired:
            logging.error("PyInstaller command timed out")
        except subprocess.CalledProcessError as e:
            logging.error(f"PyInstaller failed with exit code {e.returncode}")
            logging.error(f"Error output:\n{e.stderr}")
        except FileNotFoundError as e:
            logging.error(f"File not found: {e}")
        except Exception as e:
            logging.error(f"Unexpected error during compilation: {e}")
        finally:
            # Return to original directory
            os.chdir(self.base_dir)

    def cleanup(self):
        """Remove temporary PyInstaller files."""
        try:
            build_dir = self.middleware_path / "build"
            spec_file = self.middleware_path / "Validator.spec"
            
            if build_dir.exists():
                shutil.rmtree(build_dir)
                logging.info("Removed build directory")
            if spec_file.exists():
                spec_file.unlink()
                logging.info("Removed spec file")
                
            logging.info("Cleanup completed")
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
        
        
if __name__ == '__main__':
    try:
        PyExe()
    except Exception as e:
        logging.critical(f"Application failed: {e}")
        sys.exit(1)