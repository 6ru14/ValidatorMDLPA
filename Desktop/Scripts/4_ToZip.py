import os
import shutil
import logging
from pathlib import Path
from typing import List, Optional
import zipfile
import sys

class ArchiveValidator:
    def __init__(self):
        self._setup_logging()
        self.base_dir = Path(__file__).resolve().parent.parent
        self.dist_path = self.base_dir / "Dist"
        self.archives_path = self.base_dir / "Archives"
        self._ensure_directories_exist()

    def _setup_logging(self):
        """Configure logging for the application."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('archive_validator.log')
            ]
        )
        logging.info("Initializing ArchiveValidator")

    def _ensure_directories_exist(self):
        """Ensure all required directories exist."""
        for path in [self.dist_path, self.archives_path]:
            try:
                path.mkdir(parents=True, exist_ok=True)
                logging.debug(f"Directory exists: {path}")
            except OSError as e:
                logging.error(f"Failed to create directory {path}: {e}")
                raise

    def find_validator_folders(self) -> List[Path]:
        """Find all validator version folders in Dist directory.
        
        Returns:
            List of Path objects to validator version folders
        """
        try:
            # Find folders matching pattern validator_*
            validator_folders = [
                f for f in self.dist_path.iterdir() 
                if f.is_dir() and f.name.startswith("Validator_")
            ]
            
            if not validator_folders:
                logging.warning("No validator folders found in Dist directory")
                return []
                
            logging.info(f"Found {len(validator_folders)} validator folders")
            return validator_folders
            
        except Exception as e:
            logging.error(f"Error finding validator folders: {e}")
            return []

    def _create_zip_archive(self, source_folder: Path, zip_path: Path) -> bool:
        """Create a zip archive with the source folder contents inside a Validator folder.
        
        Args:
            source_folder: Path to the folder to be archived
            zip_path: Path where the zip file should be created
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logging.info(f"Creating archive {zip_path} from {source_folder}")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Walk through all files in the source folder
                for root, dirs, files in os.walk(source_folder):
                    for file in files:
                        file_path = Path(root) / file
                        
                        # Create relative path that starts with "Validator"
                        rel_path = Path("Validator") / file_path.relative_to(source_folder)
                        
                        # Add file to zip with new path
                        zipf.write(file_path, rel_path)
                        logging.debug(f"Added {file_path} as {rel_path} to archive")
            
            logging.info(f"Successfully created archive {zip_path}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to create zip archive: {e}")
            return False

    def archive_validator_versions(self) -> bool:
        """Archive all validator versions found in Dist folder.
        
        Returns:
            True if all archives were created successfully, False otherwise
        """
        try:
            validator_folders = self.find_validator_folders()
            if not validator_folders:
                return False
                
            success = True
            
            for folder in validator_folders:
                version = folder.name.replace("Validator_", "")
                zip_name = f"Validator_{version}.zip"
                zip_path = self.archives_path / zip_name
                
                # Skip if archive already exists
                if zip_path.exists():
                    logging.warning(f"Archive {zip_name} already exists, skipping")
                    continue
                
                # Create the zip archive
                if not self._create_zip_archive(folder, zip_path):
                    success = False
                    continue
                
                # Remove the original folder after successful archiving
                try:
                    shutil.rmtree(folder)
                    logging.info(f"Removed original folder {folder}")
                except Exception as e:
                    logging.error(f"Failed to remove original folder {folder}: {e}")
                    success = False
            
            return success
            
        except Exception as e:
            logging.exception("Error during archiving process")
            return False

if __name__ == '__main__':
    try:
        archiver = ArchiveValidator()
        success = archiver.archive_validator_versions()
        sys.exit(0 if success else 1)
    except Exception as e:
        logging.critical(f"Application failed: {e}")
        sys.exit(1)