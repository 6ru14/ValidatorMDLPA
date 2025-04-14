import os
import re
import shutil
import logging
from pathlib import Path
from typing import List, Optional, Tuple
import sys

class MoveDist:
    def __init__(self):
        # Configure logging
        self._setup_logging()
        
        # Initialize paths using Path objects
        self.base_dir = Path(__file__).resolve().parent.parent
        self.dist_path = self.base_dir / "Dist"
        self.review_path = self.base_dir / "Review"
        
        # Ensure directories exist
        self._ensure_directories_exist()
        
        try:
            self.copy_files()
        except Exception as e:
            logging.exception("Failed to distribute files")
            raise

    def _setup_logging(self):
        """Configure logging for the application."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('move_dist.log')
            ]
        )
        logging.info("Initializing MoveDist")

    def _ensure_directories_exist(self):
        """Ensure all required directories exist."""
        for path in [self.dist_path, self.review_path]:
            try:
                path.mkdir(parents=True, exist_ok=True)
                logging.debug(f"Directory exists: {path}")
            except OSError as e:
                logging.error(f"Failed to create directory {path}: {e}")
                raise

    def newest_version(self, folder_path: Path) -> Optional[str]:
        """Find the newest version folder based on semantic versioning.
        
        Args:
            folder_path: Path to the directory containing version folders
            
        Returns:
            The latest version string (e.g., '1.2.3') or None if no valid versions found
        """
        try:
            version_folders = [
                v.name for v in folder_path.iterdir() 
                if v.is_dir() and re.match(r'^\d+\.\d+\.\d+$', v.name)
            ]
            
            if not version_folders:
                logging.warning(f"No version folders found in {folder_path}")
                return None
                
            # Sort by semantic version (major.minor.patch)
            latest = sorted(
                version_folders,
                key=lambda v: tuple(map(int, v.split('.')))
            )[-1]
            
            logging.info(f"Latest version found: {latest}")
            return latest
            
        except Exception as e:
            logging.error(f"Error finding newest version: {e}")
            return None

    def _find_exe_file(self) -> Optional[Tuple[Path, str]]:
        """Locate the executable file in the review directory.
        
        Returns:
            Tuple of (path_to_exe, base_name_without_extension) or None if not found
        """
        try:
            exe_files = list(self.review_path.glob('*.exe'))
            if not exe_files:
                logging.error("No .exe file found in Review directory")
                return None
                
            if len(exe_files) > 1:
                logging.warning(f"Multiple .exe files found, using first one: {exe_files[0]}")
                
            exe_path = exe_files[0]
            return exe_path, exe_path.stem
        except Exception as e:
            logging.error(f"Error locating .exe file: {e}")
            return None

    def _prepare_destination(self, base_name: str, version: str) -> Optional[Path]:
        """Prepare the destination folder for distribution.
        
        Args:
            base_name: Name of the executable (without extension)
            version: Version string (e.g., '1.2.3')
            
        Returns:
            Path to the created destination folder or None if failed
        """
        try:
            dest_folder_name = f"{base_name}_{version}"
            dest_folder_path = self.dist_path / dest_folder_name
            
            # Create destination directory
            dest_folder_path.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created destination folder: {dest_folder_path}")
            
            # Create resources directory inside destination
            resources_path = dest_folder_path / "resources"
            resources_path.mkdir(exist_ok=True)
            logging.info(f"Created resources folder: {resources_path}")
            
            return dest_folder_path
        except Exception as e:
            logging.error(f"Failed to create destination folder: {e}")
            return None

    def _copy_versioned_resources(self, src_path: Path, dest_path: Path) -> bool:
        """Copy versioned resources from source to destination.
        
        Args:
            src_path: Path to source version folder
            dest_path: Path to destination version folder (inside resources)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if dest_path.exists():
                logging.info(f"Removing existing destination folder: {dest_path}")
                shutil.rmtree(dest_path)
                
            logging.info(f"Copying resources from {src_path} to {dest_path}")
            shutil.copytree(src_path, dest_path)
            return True
        except Exception as e:
            logging.error(f"Failed to copy resources: {e}")
            return False

    def copy_files(self) -> bool:
        """Main method to copy executable and resources to distribution folder.
        
        Returns:
            True if operation was successful, False otherwise
        """
        try:
            # Find the executable file
            exe_info = self._find_exe_file()
            if not exe_info:
                return False
                
            exe_src, base_name = exe_info
            
            # Check for resources folder
            resources_path = self.review_path / "resources"
            if not resources_path.exists():
                logging.error("No resources folder found in Review directory")
                return False
                
            # Find newest version folder in resources
            latest_version = self.newest_version(resources_path)
            if not latest_version:
                return False
                
            version_src = resources_path / latest_version
            
            # Prepare destination folder (will create resources subfolder)
            dest_folder_path = self._prepare_destination(base_name, latest_version)
            if not dest_folder_path:
                return False
                
            # Copy the executable to the main version folder
            exe_dest = dest_folder_path / exe_src.name
            logging.info(f"Copying {exe_src.name} to {dest_folder_path}")
            shutil.copy2(exe_src, exe_dest)
            
            # Copy the version folder into the resources subfolder
            version_dest = dest_folder_path / "resources" / latest_version
            if not self._copy_versioned_resources(version_src, version_dest):
                return False
            
            logging.info("Distribution completed successfully")
            return True
            
        except Exception as e:
            logging.exception("Error during distribution")
            return False

if __name__ == '__main__':
    try:
        mover = MoveDist()
        sys.exit(0 if mover.copy_files() else 1)
    except Exception as e:
        logging.critical(f"Application failed: {e}")
        sys.exit(1)