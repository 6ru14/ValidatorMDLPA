import configparser
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, Union
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape 
from packaging import version

class ConfigManager:
    """
    Handles the configuration loading and management.
    """
    def __init__(self, config_path: Optional[str] = None):
        # Creates an instance of the configparser
        self.config = configparser.ConfigParser()
        # The base path of the project
        self.base_path = Path(__file__).resolve().parent.parent
        # It checks if a config path has been used else it defaults to the preset path
        self.config_path = config_path or str(self.base_path / 'settings' / 'config.ini')
        # Checks the config file
        self.load_config()
    
    def load_config(self) -> None:
        """Checks if the configuration path / file exist."""
        if not Path(self.config_path).exists():
            raise FileNotFoundError(f"Config file not found at {self.config_path}")
        self.config.read(self.config_path)
    
    def get(self, section: str, key: str) -> str:
        """Gets a configuration value."""
        try:
            # Returns the configuration value
            return self.config[section][key]
        except KeyError:
            raise KeyError(f"Configuration key '{key}' not found in section '{section}'")

class CacheManager:
    """Manages the writing and retrieval of the access and refresh tokens"""
    
    def __init__(self, cache_path: Optional[str] = None):
        # The path of the version
        self.base_path = Path(__file__).resolve().parent.parent
        # The path of the cache file that has been used or it default to the preset path
        self.cache_path = cache_path or str(self.base_path / 'settings' / 'cache.json')
        
    def ensure_cache_file(self) -> None:
        """Ensures that the cache file exists with the proper structure."""
        if not Path(self.cache_path).exists():
            # It writes the cache file only if the file doesn't exist
            self._write_cache({"access_token": "", "refresh_token": ""})
    
    def _write_cache(self, data: Dict[str, str]):
        """Write data to cache file."""
        with open(self.cache_path, 'w') as f:
            json.dump(data, f)
    
    def _read_cache(self) -> Dict[str, str]:
        """Read cache file contents."""
        try:
            with open(self.cache_path, 'r') as f:
                data = json.load(f)
                if not all(k in data for k in ("access_token", "refresh_token")):
                    raise ValueError("Invalid cache structure")
                return data
        except (json.JSONDecodeError, ValueError):
            self._write_cache({"access_token": "", "refresh_token": ""})
            return {"access_token": "", "refresh_token": ""}
    
    def get_tokens(self) -> Tuple[str, str]:
        """Get cached tokens."""
        data = self._read_cache()
        return data["access_token"], data["refresh_token"]
    
    def update_tokens(self, access_token: str, refresh_token: str) -> None:
        """Update cached tokens."""
        self._write_cache({
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    
    def clear_cache(self) -> None:
        """Clear the cache."""
        self._write_cache({"access_token": "", "refresh_token": ""})

class AuthManager:
    """Handles authentication and token management."""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.cache = CacheManager()
        
    def _make_request(self, url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """Helper method for making HTTP requests."""
        try:
            response = requests.post(
                url=url,
                json=data,
                headers=headers or {},
                timeout=10
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API request failed: {str(e)}")
            
    def login(self, username: str, password: str) -> Optional[Tuple[str, str]]:
        """Perform user login and return tokens."""
        try:
            auth_url = self.config.get('PROVIDER', 'graphit') + self.config.get('LOGIN', 'auth')
            verify_url = self.config.get('PROVIDER', 'graphit') + self.config.get('LOGIN', 'verify')
            
            auth_data = {"email": username, "password": password}
            response = self._make_request(auth_url, auth_data)
            
            tokens = response.json()
            verify_data = {"token": tokens["access"]}
            self._make_request(verify_url, verify_data)
            
            self.cache.update_tokens(tokens["access"], tokens["refresh"])
            return tokens["access"], tokens["refresh"]
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return None
        
    def auto_login(self) -> Optional[Tuple[str, str]]:
        """
        Attempt automatic login using cached tokens.
        Returns (access_token, refresh_token) if successful, None otherwise.
        """
        try:
            access_token, refresh_token = self.cache.get_tokens()
            if access_token:
                verify_url = self.config.get('PROVIDER', 'graphit') + self.config.get('LOGIN', 'verify')
                try:
                    self._make_request(verify_url, {"token": access_token})
                    return access_token, refresh_token
                except:
                    # Token might be expired, try renewing
                    new_access_token = self.renew_token()
                    if new_access_token:
                        new_access_token, new_refresh_token = self.cache.get_tokens()
                        return new_access_token, new_refresh_token
            return None
        except Exception as e:
            print(f"Auto-login failed: {str(e)}")
            return None
            
    def renew_token(self) -> Optional[str]:
        """Renew access token using refresh token."""
        try:
            access_token, refresh_token = self.cache.get_tokens()
            if not refresh_token:
                return None
                
            refresh_url = self.config.get('PROVIDER', 'graphit') + self.config.get('LOGIN', 'refresh')
            verify_url = self.config.get('PROVIDER', 'graphit') + self.config.get('LOGIN', 'verify')
            
            # First try to verify current access token
            try:
                self._make_request(verify_url, {"token": access_token})
                return access_token
            except:
                pass
                
            # If verification fails, try refreshing
            refresh_data = {"refresh": refresh_token}
            response = self._make_request(refresh_url, refresh_data)
            
            new_tokens = response.json()
            self.cache.update_tokens(new_tokens["access"], new_tokens["refresh"])
            return new_tokens["access"]
            
        except Exception as e:
            print(f"Token renewal failed: {str(e)}")
            return None

class APIClient:
    """Handles API communication and data retrieval."""
    
    def __init__(self, config: ConfigManager, auth: AuthManager):
        self.config = config
        self.auth = auth
        self.base_url = self.config.get('PROVIDER', 'graphit')
        
    def _get_authorized(self, url: str) -> requests.Response:
        """Make authorized GET request."""
        token = self.auth.renew_token()
        if not token:
            raise PermissionError("Not authenticated")
            
        response = requests.get(
            url=url,
            headers={'Authorization': f'JWT {token}'},
            timeout=15
        )
        response.raise_for_status()
        return response
        
    def get_metadata(self, category: int) -> Tuple[pd.DataFrame, ...]:
        """Get validation metadata and reference data."""
        try:
            version = self.config.get('VALIDATOR', 'version')
            rules_url = (self.config.get('PROVIDER', 'graphit') + 
                        self.config.get('METADATA', 'rules').replace('V', version).replace('C', str(category)))
            
            # Define all endpoints to fetch
            endpoints = {
                'rules': rules_url,
                'zfzrs': self.base_url + self.config.get('METADATA', 'zfzrs'),
                'hilucs1': self.base_url + self.config.get('METADATA', 'hilucs1'),
                'hilucs2': self.base_url + self.config.get('METADATA', 'hilucs2'),
                'hilucs3': self.base_url + self.config.get('METADATA', 'hilucs3')
            }
            
            # Fetch all data in parallel (could be optimized further with async)
            responses = {name: self._get_authorized(url).json() for name, url in endpoints.items()}
            
            # Convert all responses to DataFrames
            dataframes = tuple(pd.json_normalize(responses[name]) for name in ['rules', 'zfzrs', 'hilucs1', 'hilucs2', 'hilucs3'])
            
            return dataframes
            
        except Exception as e:
            print(f"Failed to fetch metadata: {str(e)}")
            raise
            
    def get_geodata(self, siruta: str) -> Optional[gpd.GeoDataFrame]:
        """Get geographic data for a SIRUTA code."""
        try:
            uat_url = self.base_url + self.config.get('METADATA', 'uat') + siruta
            response = self._get_authorized(uat_url)
            geo_data = response.json()
            
            geometries = [shape(feature['geometry']) for feature in geo_data['features']]
            return gpd.GeoDataFrame(
                {'geometry': geometries},
                geometry='geometry',
                crs="EPSG:3844"
            )
            
        except Exception as e:
            print(f"Failed to fetch geodata for SIRUTA {siruta}: {str(e)}")
            return None
            
    def check_version(self) -> bool:
        """Check if current version is up-to-date."""
        try:
            current_version = self.config.get('VALIDATOR', 'version')
            version_url = self.base_url + self.config.get('METADATA', 'version')
            
            response = self._get_authorized(version_url)
            latest_version = response.json()[0]['definitie']
            
            return version.parse(latest_version) <= version.parse(current_version)
            
        except Exception as e:
            print(f"Version check failed: {str(e)}")
            return False
            
    def download_update(self, base_folder: Union[str, Path]) -> bool:
        """Download and install the latest version."""
        try:
            base_folder = Path(base_folder)
            version_url = self.base_url + self.config.get('METADATA', 'version')
            
            # Get download URL
            response = self._get_authorized(version_url)
            download_url = response.json()[0]['file']
            
            # Download to temporary file
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
                temp_path = Path(temp_file.name)
                with requests.get(download_url, stream=True) as r:
                    r.raise_for_status()
                    for chunk in r.iter_content(chunk_size=8192):
                        temp_file.write(chunk)
            
            # Extract to temporary directory
            extract_path = base_folder / "temp_extracted"
            extract_path.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            temp_path.unlink()  # Delete temp file
            
            # Find and move the resources
            extracted_folders = [f for f in extract_path.iterdir() if f.is_dir()]
            if extracted_folders:
                resources_path = extracted_folders[0] / 'resources'
                if resources_path.exists():
                    for item in resources_path.iterdir():
                        target = base_folder / item.name
                        if item.is_dir():
                            shutil.rmtree(target, ignore_errors=True)
                            shutil.move(str(item), str(target))
                        else:
                            target.unlink(missing_ok=True)
                            shutil.move(str(item), str(target))
            
            shutil.rmtree(extract_path)
            return True
            
        except Exception as e:
            print(f"Update failed: {str(e)}")
            # Clean up any temporary files/directories
            if 'extract_path' in locals() and extract_path.exists():
                shutil.rmtree(extract_path, ignore_errors=True)
            if 'temp_path' in locals() and temp_path.exists():
                temp_path.unlink(missing_ok=True)
            return False