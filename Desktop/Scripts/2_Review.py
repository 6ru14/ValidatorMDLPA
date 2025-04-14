import os
import re
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import sys

class MovePreview:
    # File content verification patterns
    CONTENT_PATTERNS: Dict[str, List[str]] = {
        ".py": ["import", "def ", "class "],
        ".json": ["{", "}"],
        ".ini": ["[", "]"],
        ".txt": [],  # No content verification for plain text
        ".md": [],   # No content verification for markdown
    }
    
    # Binary file extensions (skip content verification)
    BINARY_EXTENSIONS = {".ico", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".exe", ".dll"}

    def __init__(self):
        # Configure logging
        self._setup_logging()
        
        # Initialize paths using Path objects
        self.base_dir = Path(__file__).resolve().parent.parent
        self.test_path = self.base_dir / "Test"
        self.review_path = self.base_dir / "Review"
        self.middleware_path = self.base_dir / "Middleware"
        
        # Ensure directories exist
        self._ensure_directories_exist()
        
        try:
            self.move_exe()
            self.move_resources()
        except Exception as e:
            logging.exception("Failed to move preview files")
            raise

    def _setup_logging(self):
        """Configure logging for the application."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('move_preview.log')
            ]
        )

    def _ensure_directories_exist(self):
        """Ensure all required directories exist."""
        for path in [self.test_path, self.review_path, self.middleware_path]:
            try:
                path.mkdir(parents=True, exist_ok=True)
                logging.debug(f"Directory exists: {path}")
            except OSError as e:
                logging.error(f"Failed to create directory {path}: {e}")
                raise

    def move_exe(self):
        """Move the executable file from middleware to review directory."""
        exe_name = 'Validator.exe'
        exe_path = self.middleware_path / exe_name
        to_path = self.review_path / exe_name
        
        if not exe_path.exists():
            logging.error(f"Source executable not found at {exe_path}")
            return False
            
        try:
            # Copy with metadata preservation
            shutil.copy2(exe_path, to_path)
            logging.info(f"Executable moved to {to_path}")
            return True
        except (IOError, shutil.SameFileError) as e:
            logging.error(f"Failed to move executable: {e}")
            return False

    def newest_version(self, folder_path: Path) -> Optional[str]:
        """Find the newest version folder based on semantic versioning."""
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
            
            logging.debug(f"Latest version found: {latest}")
            return latest
            
        except Exception as e:
            logging.error(f"Error finding newest version: {e}")
            return None

    def verify_file_content(self, file_path: Path) -> bool:
        """Verify file content meets requirements for its type."""
        ext = file_path.suffix.lower()
        
        # Skip verification for binary files
        if ext in self.BINARY_EXTENSIONS:
            return True
            
        # Skip if no patterns defined for this extension
        if ext not in self.CONTENT_PATTERNS or not self.CONTENT_PATTERNS[ext]:
            return True
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for all required patterns
                return all(
                    pattern in content 
                    for pattern in self.CONTENT_PATTERNS[ext] 
                    if pattern
                )
        except UnicodeDecodeError:
            logging.warning(f"Could not read {file_path} as text - skipping content check")
            return False
        except IOError as e:
            logging.error(f"Failed to read {file_path}: {e}")
            return False

    def copy_files(self, src_folder: Path, dest_folder: Path) -> Tuple[int, int]:
        """Recursively copy files with validation, returning success/failure counts."""
        success = 0
        skipped = 0
        
        for item in src_folder.rglob('*'):
            if item.is_dir():
                continue
                
            relative_path = item.relative_to(src_folder)
            target_path = dest_folder / relative_path
            
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            if self.verify_file_content(item):
                try:
                    shutil.copy2(item, target_path)
                    logging.info(f"Copied: {item} -> {target_path}")
                    success += 1
                except IOError as e:
                    logging.error(f"Failed to copy {item}: {e}")
                    skipped += 1
            else:
                logging.warning(f"Skipped: {item} (content check failed)")
                skipped += 1
                
        return success, skipped

    def move_resources(self):
        """Move resources from test to review directory."""
        resources_folder = 'resources'
        resources_path = self.test_path / resources_folder
        resources_to = self.review_path / resources_folder
        
        if not resources_path.exists():
            logging.error(f"Resources folder not found at {resources_path}")
            return False
            
        # Create target directory if needed
        resources_to.mkdir(exist_ok=True)
        
        # Find newest version
        newest_version = self.newest_version(resources_path)
        if not newest_version:
            return False
            
        newest_version_path = resources_path / newest_version
        newest_version_to = resources_to / newest_version
        
        # Create version directory if needed
        newest_version_to.mkdir(exist_ok=True)
        
        # Copy files with validation
        success, skipped = self.copy_files(newest_version_path, newest_version_to)
        
        logging.info(
            f"Resource copy completed: {success} files copied, {skipped} files skipped"
        )
        return success > 0  # Return True if at least one file was copied

if __name__ == '__main__':
    try:
        MovePreview()
    except Exception as e:
        logging.critical(f"Application failed: {e}")
        sys.exit(1)