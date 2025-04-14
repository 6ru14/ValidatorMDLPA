import os
import sys
import json
import shutil
import threading
import configparser
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import zipfile
import tempfile
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from extras.database import CacheManager, AuthManager, APIClient, ConfigManager
from extras.writer import REPORT_PATH
from extras.validation import Validation

class AppSettings:
    """Handles application settings and configurations."""
    
    def __init__(self):
        self.base_path = Path(__file__).resolve().parent.parent
        self.load_settings()
        
    def load_settings(self) -> None:
        """Load all required settings from files."""
        try:
            # Load login settings
            with open(self.base_path / "settings" / "login.json", 'r') as f:
                self.login_settings = json.load(f)
            
            # Load validation settings
            with open(self.base_path / "settings" / "validate.json", 'r') as f:
                self.validate_settings = json.load(f)
            
            # Load config
            self.config = configparser.ConfigParser()
            self.config.read(self.base_path / "settings" / "config.ini")
            
        except FileNotFoundError as e:
            raise RuntimeError(f"Configuration file missing: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON in settings file: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading settings: {e}")

class BaseFrame(ctk.CTkFrame):
    """Base frame class with common functionality."""
    
    def __init__(self, master: ctk.CTk, settings: Dict[str, Any], **kwargs):
        super().__init__(
            master=master,
            fg_color=settings["FrameClass"]["fg_color"],
            corner_radius=settings["FrameClass"]["corner_radius"],
            **kwargs
        )
        self.settings = settings
        self.base_path = Path(__file__).resolve().parent.parent
        
    def create_label(self, parent: ctk.CTkFrame, key: str, **kwargs) -> ctk.CTkLabel:
        """Create a standardized label."""
        label_settings = self.settings["Labels"].get(key, {})

        return ctk.CTkLabel(
            master=parent,
            text=label_settings.get("text", ""),
            font=(
                label_settings.get("font_family", "DefaultFont"), 
                label_settings.get("font_size", 12)
            ),
            text_color=label_settings.get("text_color", "black"),
            **kwargs
        )
        
    def create_button(self, parent: ctk.CTkFrame, key: str, command=None, **kwargs) -> ctk.CTkButton:
        """Create a standardized button."""
        button_settings = self.settings["Buttons"].get(key, {})

        return ctk.CTkButton(
            master=parent,
            text=button_settings.get("text", ""),
            text_color=button_settings.get("text_color", "black"),
            font=(
                button_settings.get("font_family", "DefaultFont"), 
                button_settings.get("font_size", 12)
            ),
            width=button_settings.get("width", 100),
            height=button_settings.get("height", 30),
            corner_radius=button_settings.get("corner_radius", 5),
            fg_color=button_settings.get("fg_color", "gray"),
            hover_color=button_settings.get("hover_color", "lightgray"),
            command=command,
            **kwargs
        )

class LoginFrame(BaseFrame):
    """Login window frame."""
    
    def __init__(self, master: ctk.CTk, on_login: callable, settings: Dict[str, Any], auto_login_callback: callable):
        super().__init__(master, settings)
        self.on_login = on_login  # Now expects tokens as an argument
        self.auto_login_callback = auto_login_callback
        self.tokens = None  # Store tokens for later use
        self.setup_ui()
        self.attempt_auto_login()
        
    def setup_ui(self) -> None:
        """Setup the login UI components."""
        self.place(
            anchor=self.settings["FrameClass"]["anchor"],
            relx=self.settings["FrameClass"]["relx"],
            rely=self.settings["FrameClass"]["rely"],
            relheight=self.settings["FrameClass"]["relheight"],
            relwidth=self.settings["FrameClass"]["relwidth"] 
        )
        
        # Main container frames
        main_frame = ctk.CTkFrame(
            master=self,
            corner_radius=self.settings["Frames"]["main"]["corner_radius"],
            fg_color=self.settings["Frames"]["main"]["fg_color"]
        )
        
        image_frame = ctk.CTkFrame(
            master=main_frame,
            corner_radius=self.settings["Frames"]["image"]["corner_radius"],
            fg_color=self.settings["Frames"]["image"]["fg_color"]
        )
        
        auth_frame = ctk.CTkFrame(
            master=main_frame,
            corner_radius=self.settings["Frames"]["auth"]["corner_radius"],
            fg_color=self.settings["Frames"]["auth"]["fg_color"]
        )
        
        # Load and display image
        image_path = self.base_path / "images" / "image.png"
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found at {image_path}")
            
        image = Image.open(image_path)
        header_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=(800, 600)
        )
        
        image_label = ctk.CTkLabel(
            master=image_frame,
            text="",
            image=header_image
        )
        
        # Authentication components
        inner_auth_frame = ctk.CTkFrame(
            master=auth_frame,
            corner_radius=self.settings["Frames"]["inner_auth"]["corner_radius"],
            fg_color=self.settings["Frames"]["inner_auth"]["fg_color"]
        )
        
        # Create form elements
        self.create_auth_form(inner_auth_frame)
        
        # Layout frames
        main_frame.place(relx=0.5, rely=0.5, relwidth=1.0, relheight=1.0, anchor="center")
        auth_frame.place(relx=0.83, rely=0.5, relwidth=0.34, relheight=1.0, anchor="center")
        image_frame.place(relx=0.5, rely=0.5, relwidth=1.0, relheight=1.0, anchor="center")
        inner_auth_frame.place(relx=0.5, rely=0.5, relwidth=0.8, relheight=0.8, anchor="center")
        image_label.pack(anchor="center", expand="True")
        
    def create_auth_form(self, parent: ctk.CTkFrame) -> None:
        """Create the authentication form elements."""
        # Label frame
        label_frame = ctk.CTkFrame(
            master=parent,
            corner_radius=self.settings["Frames"]["label"]["corner_radius"],
            fg_color=self.settings["Frames"]["label"]["fg_color"]
        )
        
        # Username frame
        username_frame = ctk.CTkFrame(
            master=parent,
            corner_radius=self.settings["Frames"]["username"]["corner_radius"],
            fg_color=self.settings["Frames"]["username"]["fg_color"]
        )
        
        # Password frame
        password_frame = ctk.CTkFrame(
            master=parent,
            corner_radius=self.settings["Frames"]["password"]["corner_radius"],
            fg_color=self.settings["Frames"]["password"]["fg_color"]
        )
        
        # Button frame
        button_frame = ctk.CTkFrame(
            master=parent,
            corner_radius=self.settings["Frames"]["button"]["corner_radius"],
            fg_color=self.settings["Frames"]["button"]["fg_color"]
        )
        
        # Invalid credentials frame
        self.invalid_frame = ctk.CTkFrame(
            master=parent,
            corner_radius=self.settings["Frames"]["invalid"]["corner_radius"],
            fg_color=self.settings["Frames"]["invalid"]["fg_color"]
        )
        
        # Create and pack labels
        auth_label = self.create_label(label_frame, "auth")
        username_label = self.create_label(username_frame, "username", anchor="w")
        password_label = self.create_label(password_frame, "password", anchor="w")
        
        self.invalid_label = ctk.CTkLabel(
            master=self.invalid_frame,
            text=self.settings["Labels"]["invalid"]["text"],
            font=(self.settings["Labels"]["invalid"]["font_family"], 
                 self.settings["Labels"]["invalid"]["font_size"]),
            text_color=self.settings["Labels"]["invalid"]["text_color_neutral"]
        )
        
        # Create entry boxes
        self.username_entrybox = ctk.CTkEntry(
            master=username_frame,
            text_color=self.settings["Entryboxes"]["username"]["text_color"],
            font=(self.settings["Entryboxes"]["username"]["font_family"], 
                 self.settings["Entryboxes"]["username"]["font_size"]),
            width=self.settings["Entryboxes"]["username"]["width"],
            height=self.settings["Entryboxes"]["username"]["height"],
            corner_radius=self.settings["Entryboxes"]["username"]["corner_radius"],
            border_color=self.settings["Entryboxes"]["username"]["border_color"],
            fg_color=self.settings["Entryboxes"]["username"]["fg_color"],
        )
        
        self.password_entrybox = ctk.CTkEntry(
            master=password_frame,
            text_color=self.settings["Entryboxes"]["password"]["text_color"],
            font=(self.settings["Entryboxes"]["password"]["font_family"], 
                 self.settings["Entryboxes"]["password"]["font_size"]),
            width=self.settings["Entryboxes"]["password"]["width"],
            height=self.settings["Entryboxes"]["password"]["height"],
            corner_radius=self.settings["Entryboxes"]["password"]["corner_radius"],
            border_color=self.settings["Entryboxes"]["password"]["border_color"],
            fg_color=self.settings["Entryboxes"]["password"]["fg_color"],
            show="*"
        )
        
        # Create login button
        login_button = self.create_button(
            button_frame, 
            "login", 
            command=self.login_function
        )
        
        # Bind Enter key to login function
        self.username_entrybox.bind("<Return>", self.login_function)
        self.password_entrybox.bind("<Return>", self.login_function)
        
        # Pack all components (modified order)
        label_frame.pack(fill='x', pady=(0, 50))
        username_frame.pack(fill='x')
        password_frame.pack(fill='x')
        self.invalid_frame.pack(fill='x')
        button_frame.pack(fill='x', pady=(20, 0))
        
        auth_label.pack(anchor='center')
        username_label.pack(anchor='w')
        password_label.pack(anchor='w')
        self.invalid_label.pack(anchor='w')
        
        self.username_entrybox.pack(fill='x')
        self.password_entrybox.pack(fill='x')
        login_button.pack(anchor='w')
        
    def login_function(self, event=None) -> None:
        """Handle login attempt and token caching."""
        username = self.username_entrybox.get()
        password = self.password_entrybox.get()
        
        if not username or not password:
            self.show_invalid_credentials()
            return
            
        try:
            auth_manager = AuthManager(ConfigManager())
            cache_manager = CacheManager()
            
            tokens = auth_manager.login(username, password)
            if tokens:
                self.tokens = tokens  # Store tokens
                cache_manager.update_tokens(*tokens)  # Cache tokens by default
                self.on_login(tokens)  # Pass tokens to callback
            else:
                self.show_invalid_credentials()
        except Exception as e:
            messagebox.showerror("Login Error", f"Failed to login: {str(e)}")
            self.show_invalid_credentials()
            
    def show_invalid_credentials(self) -> None:
        """Display invalid credentials message."""
        self.invalid_label.configure(
            text_color=self.settings["Labels"]["invalid"]["text_color_invalid"]
        )
    
    def attempt_auto_login(self) -> None:
        """Attempt automatic login based on cached tokens."""
        self.auto_login_callback()

class ValidationFrame(BaseFrame):
    """Main validation window frame."""
    
    def __init__(self, master: ctk.CTk, on_logout: callable, settings: Dict[str, Any], tokens: Tuple[str, str]):
        super().__init__(master, settings)
        self.on_logout = on_logout
        self.tokens = tokens  # Store tokens for later use
        self.file_path = ""
        self.validation_type = None
        self.setup_ui()
        
    def setup_ui(self) -> None:
        """Setup the validation UI components."""
        self.place(
            anchor=self.settings["FrameClass"]["anchor"],
            relx=self.settings["FrameClass"]["relx"],
            rely=self.settings["FrameClass"]["rely"],
            relheight=self.settings["FrameClass"]["relheight"],
            relwidth=self.settings["FrameClass"]["relwidth"] 
        )
        
        # Header image
        image_path = self.base_path / "images" / "head.png"
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found at {image_path}")
            
        image = Image.open(image_path)
        header_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=(1024*0.5, 110*0.5)
        )
        
        # Main frames
        main_frame = ctk.CTkFrame(
            master=self,
            width=self.settings["Frames"]["main"]["width"],
            corner_radius=self.settings["Frames"]["main"]["corner_radius"],
            fg_color=self.settings["Frames"]["main"]["fg_color"],
            border_width=self.settings["Frames"]["main"]["border_width"],
            border_color=self.settings["Frames"]["main"]["border_color"]
        )
        
        image_frame = ctk.CTkFrame(
            master=self,
            corner_radius=self.settings["Frames"]["image"]["corner_radius"],
            fg_color=self.settings["Frames"]["image"]["fg_color"]
        )
        
        box_frame = ctk.CTkFrame(
            master=main_frame,
            corner_radius=self.settings["Frames"]["box"]["corner_radius"],
            fg_color=self.settings["Frames"]["box"]["fg_color"],
            border_width=self.settings["Frames"]["box"]["border_width"],
            border_color=self.settings["Frames"]["box"]["border_color"]
        )
        
        # Create and layout header image
        image_label = ctk.CTkLabel(
            master=image_frame,
            text="",
            image=header_image
        )
        
        # Create form sections
        self.create_title_section(box_frame)
        self.create_file_selection(box_frame)
        self.create_validation_type(box_frame)
        self.create_validation_controls(box_frame)
        self.create_footer()
        
        # Layout main frames
        image_frame.place(anchor="n", relx=0.5, rely=0)
        image_label.pack(pady=(10, 0))
        main_frame.pack(expand=True, pady=(50, 0))
        box_frame.pack(expand=True)
        
    def create_title_section(self, parent: ctk.CTkFrame) -> None:
        """Create the title section."""
        title_frame = ctk.CTkFrame(
            master=parent,
            corner_radius=self.settings["Frames"]["title"]["corner_radius"],
            fg_color=self.settings["Frames"]["title"]["fg_color"],
            border_width=self.settings["Frames"]["title"]["border_width"],
            border_color=self.settings["Frames"]["title"]["border_color"]
        )
        
        title_label = self.create_label(title_frame, "title")
        
        title_frame.pack(fill="x")
        title_label.pack(pady=1.5, padx=1.5)
        
    def create_file_selection(self, parent: ctk.CTkFrame) -> None:
        """Create file selection controls."""
        choose_frame = ctk.CTkFrame(
            master=parent,
            corner_radius=self.settings["Frames"]["choose"]["corner_radius"],
            fg_color=self.settings["Frames"]["choose"]["fg_color"],
            border_width=self.settings["Frames"]["choose"]["border_width"],
            border_color=self.settings["Frames"]["choose"]["border_color"]
        )
        
        choose_label = self.create_label(choose_frame, "choose", anchor="w")
        
        self.choose_entrybox = ctk.CTkEntry(
            master=choose_frame,
            text_color=self.settings["Entryboxes"]["choose"]["text_color"],
            font=(self.settings["Entryboxes"]["choose"]["font_family"], 
                 self.settings["Entryboxes"]["choose"]["font_size"]),
            width=self.settings["Entryboxes"]["choose"]["width"],
            height=self.settings["Entryboxes"]["choose"]["height"],
            corner_radius=self.settings["Entryboxes"]["choose"]["corner_radius"],
            border_color=self.settings["Entryboxes"]["choose"]["border_color"],
            fg_color=self.settings["Entryboxes"]["choose"]["fg_color"],
            bg_color=self.settings["Entryboxes"]["choose"]["bg_color"]
        )
        
        self.choose_button = self.create_button(
            choose_frame,
            "choose",
            command=self.browse_files
        )
        
        choose_frame.pack(fill='x', padx=0.75)
        choose_label.pack(pady=1.5, padx=(10, 1), anchor="w")
        self.choose_entrybox.pack(side='left', pady=(0, 10), padx=(10, 1))
        self.choose_button.pack(side="left", pady=(0, 10), padx=(0, 20))
        
    def create_validation_type(self, parent: ctk.CTkFrame) -> None:
        """Create validation type selection controls."""
        type_frame = ctk.CTkFrame(
            master=parent,
            corner_radius=self.settings["Frames"]["type"]["corner_radius"],
            fg_color=self.settings["Frames"]["type"]["fg_color"],
            border_width=self.settings["Frames"]["type"]["border_width"],
            border_color=self.settings["Frames"]["type"]["border_color"]
        )
        
        type_label = self.create_label(type_frame, "type", anchor="w")
        
        self.pug_button = self.create_button(
            type_frame,
            "pug",
            command=lambda: self.set_validation_type(1)
        )
        
        self.pud_button = self.create_button(
            type_frame,
            "pud",
            command=lambda: self.set_validation_type(2),
            state="disabled"
        )
        
        self.puz_button = self.create_button(
            type_frame,
            "puz",
            command=lambda: self.set_validation_type(3)
        )
        
        self.patj_button = self.create_button(
            type_frame,
            "patj",
            command=lambda: self.set_validation_type(4),
            state="disabled"
        )
        
        type_frame.pack(fill='x', padx=0.75)
        type_label.pack(pady=1.5, padx=(10, 0), anchor="w")
        
        buttons = [self.pug_button, self.pud_button, self.puz_button, self.patj_button]
        for i, button in enumerate(buttons):
            button.pack(
                side="left",
                pady=(0, 10),
                padx=(10 if i == 0 else 5, 5 if i < len(buttons) - 1 else 0)
            )
        
    def create_validation_controls(self, parent: ctk.CTkFrame) -> None:
        """Create validation action controls."""
        validate_frame = ctk.CTkFrame(
            master=parent,
            corner_radius=self.settings["Frames"]["validate"]["corner_radius"],
            fg_color=self.settings["Frames"]["validate"]["fg_color"],
            border_width=self.settings["Frames"]["validate"]["border_width"],
            border_color=self.settings["Frames"]["validate"]["border_color"]
        )
        
        validate_label = self.create_label(validate_frame, "validate", anchor="w")
        
        inner_validate_frame = ctk.CTkFrame(
            master=validate_frame,
            corner_radius=self.settings["Frames"]["inner_validate"]["corner_radius"],
            fg_color=self.settings["Frames"]["inner_validate"]["fg_color"]
        )
        
        in_progress_frame = ctk.CTkFrame(
            master=validate_frame,
            corner_radius=self.settings["Frames"]["in_progress"]["corner_radius"],
            fg_color=self.settings["Frames"]["in_progress"]["fg_color"]
        )
        
        progress_frame = ctk.CTkFrame(
            master=validate_frame,
            corner_radius=self.settings["Frames"]["progress"]["corner_radius"],
            fg_color=self.settings["Frames"]["progress"]["fg_color"]
        )
        
        self.validate_button = self.create_button(
            inner_validate_frame,
            "validate",
            command=self.execute_validation,
            state="disabled"
        )
        
        self.raport_button = self.create_button(
            inner_validate_frame,
            "raport",
            command=self.save_report,
            state="disabled"
        )
        
        self.in_progress_label = ctk.CTkLabel(
            master=in_progress_frame,
            text=""
        )
        
        self.progressbar = ctk.CTkProgressBar(
            master=progress_frame,
            mode=self.settings["Progressbar"]["mode"],
            corner_radius=self.settings["Progressbar"]["corner_radius"],
            width=self.settings["Progressbar"]["width"],
            height=self.settings["Progressbar"]["height"],
            border_width=self.settings["Progressbar"]["border_width"],
            border_color=self.settings["Progressbar"]["border_color"],
            fg_color=self.settings["Progressbar"]["fg_color"],
            bg_color=self.settings["Progressbar"]["bg_color"],
            progress_color=self.settings["Progressbar"]["inactive"]
        )
        
        validate_frame.pack(fill='x', padx=0.75)
        validate_label.pack(pady=(1.5, 0), padx=(10, 0), anchor="w")
        inner_validate_frame.pack(fill='x', padx=1.5)
        in_progress_frame.pack(fill='x', ipady=0, padx=(0.75, 10))
        progress_frame.pack(fill='x', padx=1.5, pady=1.5)
        
        self.validate_button.pack(anchor="w", side="left", pady=1.5, padx=(10, 0))
        self.raport_button.pack(anchor="w", side="left", pady=1.5, padx=(5, 0))
        self.in_progress_label.pack(anchor='w', side="left", padx=(10, 0))
        self.progressbar.pack(anchor="w", pady=(0, 10), padx=(10, 10))
        
    def create_footer(self) -> None:
        """Create footer elements (version info and logout)"""
        # Create a frame for the footer
        footer_frame = ctk.CTkFrame(
            master=self,
            corner_radius=self.settings["Frames"]["logout"]["corner_radius"],
            fg_color=self.settings["Frames"]["logout"]["fg_color"]
        )
        
        # Version label at bottom left
        version_label = self.create_label(self, "version")
        
        # Logout button at bottom right
        self.log_out_button = self.create_button(
            footer_frame,
            "log_out",
            command=self.login_off
        )
        
        # Place the footer frame at the bottom
        footer_frame.pack(side="bottom", fill="x", padx=1.5, pady=1.5)
        
        # Position version label at bottom left
        version_label.place(anchor="sw", relx=0.01, rely=1.0)
        
        # Pack logout button to the right within the footer frame
        self.log_out_button.pack(side="right", pady=5, padx=5)
        
    def browse_files(self) -> None:
        """Open file dialog to select a file for validation."""
        file_path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")])
        if file_path:
            self.file_path = file_path
            self.choose_entrybox.delete(0, tk.END)
            self.choose_entrybox.insert(0, file_path)
            self.update_validate_button_state()
        else:
            self.choose_entrybox.delete(0, tk.END)
            self.update_validate_button_state()
    
    def set_validation_type(self, validation_type: int) -> None:
        """Set the type of validation to perform."""
        self.validation_type = validation_type
        self.update_validate_button_state()
    
    def update_validate_button_state(self) -> None:
        """Update the validate button state based on current selections."""
        if self.file_path and self.validation_type is not None:
            self.validate_button.configure(state="normal")
        else:
            self.validate_button.configure(state="disabled")
    
    def execute_validation(self) -> None:
        if not self.file_path or self.validation_type is None:
            return
        thread = threading.Thread(target=self.run_validation)
        thread.start()
    
    def run_validation(self) -> None:
        self.set_ui_state(False)
        try:
            api_client = APIClient(ConfigManager(), AuthManager(ConfigManager()))
            metadata, zfzrs_data, hilucs1_data, hilucs2_data, hilucs3_data = (
                api_client.get_metadata(category=self.validation_type)
            )
            
            validator = Validation(
                tip_validare=self.validation_type,
                zipfilepath=self.file_path,
                metadata=metadata,
                zfzrs=zfzrs_data,
                hilucs1=hilucs1_data,
                hilucs2=hilucs2_data,
                hilucs3=hilucs3_data,
            )
            
            validation_passed = validator.validate()
            self.handle_validation_result(validation_passed)
            
        except Exception as e:
            messagebox.showerror("Validation Error", f"Validation failed: {str(e)}")
            self.set_ui_state(True)
    
    def set_ui_state(self, enabled: bool) -> None:
        """Enable or disable UI elements during validation."""
        state = "normal" if enabled else "disabled"
        self.choose_button.configure(state=state)
        self.pug_button.configure(state=state)
        self.puz_button.configure(state=state)
        self.validate_button.configure(state=state)
        self.raport_button.configure(state=state)
        self.log_out_button.configure(state=state)
        
        if enabled:
            self.progressbar.stop()
        else:
            self.progressbar.configure(
                progress_color=self.settings["Progressbar"]["active_color"],
                fg_color=self.settings["Progressbar"]["fg_active_color"]
            )
            self.progressbar.start()
            
            self.in_progress_label.configure(
                text=self.settings["Labels"]["in_progress"]["active_text"],
                text_color=self.settings["Labels"]["in_progress"]["active_text_color"]
            )
    
    def reset_ui(self) -> None:
        """Reset the UI to its initial state after validation."""
        # Reset validation type
        self.validation_type = None
        self.update_validate_button_state()  # Disable validate button if needed
        
        # Reset button states
        self.validate_button.configure(state="normal")
        self.raport_button.configure(state="normal")
        self.choose_button.configure(state="normal")
        self.pug_button.configure(state="normal")
        self.puz_button.configure(state="normal")
        # Keep disabled buttons (pud, patj) as they were initially disabled
        
        # Ensure logout button remains active
        self.log_out_button.configure(state="normal")
    
    def handle_validation_result(self, success: bool) -> None:
        """Update UI based on validation result."""
        self.set_ui_state(True)
        
        if success:
            self.in_progress_label.configure(
                text=self.settings["Labels"]["in_progress"]["pass_text"],
                text_color=self.settings["Labels"]["in_progress"]["pass_text_color"]
            )
            self.progressbar.configure(
                progress_color=self.settings["Progressbar"]["pass_color"],
                fg_color=self.settings["Progressbar"]["fg_pass_color"]
            )
            self.raport_button.configure(state="normal")
        else:
            self.in_progress_label.configure(
                text=self.settings["Labels"]["in_progress"]["fail_text"],
                text_color=self.settings["Labels"]["in_progress"]["fail_text_color"]
            )
            self.progressbar.configure(
                progress_color=self.settings["Progressbar"]["fail_color"],
                fg_color=self.settings["Progressbar"]["fg_fail_color"]
            )

        self.after(0, self.reset_ui)
    
    def save_report(self) -> None:
        """Save the validation report to a user-selected location."""
        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        shutil.copy(REPORT_PATH, save_path)
        
        # if save_path:
        #     try:
        #         shutil.copy(REPORT_PATH, save_path)
        #         messagebox.showinfo("Success", "Report saved successfully")
        #     except Exception as e:
        #         messagebox.showerror("Error", f"Failed to save report: {str(e)}")
    
    def login_off(self) -> None:
        """Handle logout process."""
        self.on_logout()

class CTkProgressWindow(ctk.CTkToplevel):
    def __init__(self, master, title: str = "Descarcare Update"):
        super().__init__(master)
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Make the window modal
        self._set_window_icon()
        self._center_window()
        self.grab_set()
        self.configure(fg_color = "white")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        
        # Create widgets
        self.label = ctk.CTkLabel(self, text="Actualizarea se descarca...", font=("Arial", 14), text_color="black")
        self.label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        self.progress = ctk.CTkProgressBar(self, orientation="horizontal", mode="determinate", corner_radius=0, height=40, progress_color='#324AB2', fg_color='#E0E0E0')
        self.progress.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.progress.set(0)
        
        self.details = ctk.CTkLabel(self, text="", font=("Arial", 12), text_color="black")
        self.details.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        self.cancel_button = ctk.CTkButton(self, text="Anuleaza", command=self.cancel, width=56, height=28, fg_color="#324AB2", hover_color="#1a1f71")
        self.cancel_button.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.cancelled = False
    
    def _set_window_icon(self):
        """Windows-only reliable icon solution"""
        try:
            icon_path = Path(__file__).resolve().parent.parent / "images" / "logo.ico"
            if icon_path.exists():
                # This is the most reliable method for Windows
                self.iconbitmap(default=str(icon_path))
                
                # Workaround to prevent CTk from resetting it
                self.tk.call('wm', 'iconbitmap', self._w, str(icon_path))
        except Exception as e:
            print(f"Could not set window icon: {e}")
            
    def _center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
        self._set_window_icon()
    
    def _close_application(self):
        """Close the entire application by destroying the root window."""
        self.master.destroy()
    
    def cancel(self):
        self.cancelled = True
        self.label.configure(text="Actualizarea se opreste...")
        self.cancel_button.configure(state="disabled")
    
    def update_progress(self, value: float, message: str, detail: Optional[str] = None):
        if not self.cancelled:
            self.progress.set(value)
            self.label.configure(text=message)
            if detail:
                self.details.configure(text=detail)
            
            self._set_window_icon()
            self.update_idletasks()
    
    def complete(self, success: bool, message: str):
        if success:
            self.progress.set(1.0)
            self.label.configure(text=message)
            self.details.configure(text="Aplicatia a fost actualizata.")
            self.cancel_button.configure(text="Ok", command=self._close_application)
        else:
            self.progress.set(0)
            self.label.configure(text="Actualizarea a esuat")
            self.details.configure(text=message)
            self.cancel_button.configure(text="Ok", command=self.destroy)
        
        self._set_window_icon()
        self.update_idletasks()
class CTkMessageBox(ctk.CTkToplevel):
    """Custom message box using plain Tkinter with CTk widgets."""
    
    def __init__(self, parent, title, message, yes_text="Yes", no_text="No"):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Set icon immediately
        self._set_window_icon()
        
        # Use CTkFrame as main container
        main_frame = ctk.CTkFrame(self, fg_color="white")
        main_frame.pack(fill="both", expand=True)
        
        # Configure grid
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure((0, 1, 2), weight=1)
        
        # Message label
        self.label = ctk.CTkLabel(
            main_frame,
            text=message,
            font=("Arial", 14),
            wraplength=250,
            justify="left",
            text_color="black"
        )
        self.label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Button frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Yes/No buttons
        self.yes_button = ctk.CTkButton(
            button_frame,
            text=yes_text,
            command=lambda: self.set_result(True),
            width=100,
            fg_color="#324AB2",
            hover_color="#1a1f71"
        )
        self.yes_button.pack(side="left", padx=(20, 10))
        
        self.no_button = ctk.CTkButton(
            button_frame,
            text=no_text,
            command=lambda: self.set_result(False),
            width=100,
            fg_color="#E0E0E0",
            hover_color="#B0B0B0",
            text_color="black"
        )
        self.no_button.pack(side="right", padx=(10, 20))
        
        # Center the window
        self._center_window()
        
        # Set up periodic icon checks
        self._icon_check_counter = 0
        self._check_icon_periodically()
        
        self.result = None
    
    def _set_window_icon(self):
        """Set window icon reliably using both methods."""
        try:
            icon_path = Path(__file__).resolve().parent.parent / "images" / "logo.ico"
            if icon_path.exists():
                # First method - works on Windows
                self.after(10, lambda: self.iconbitmap(default=str(icon_path)))
                
                # Second method - works cross-platform (convert ICO to PNG first)
                try:
                    img = Image.open(str(icon_path))
                    photo = ImageTk.PhotoImage(img)
                    self.after(20, lambda: self.tk.call('wm', 'iconphoto', self._w, photo))
                    # Keep reference to prevent garbage collection
                    self._icon_photo = photo
                except Exception as e:
                    print(f"Couldn't convert icon to PhotoImage: {e}")
        except Exception as e:
            print(f"Could not set window icon: {e}")
    
    def _check_icon_periodically(self):
        """Periodically check and reset the icon to prevent CTk from overriding it."""
        self._set_window_icon()
        self._icon_check_counter += 1
        
        # Stop checking after 10 attempts (2 seconds)
        if self._icon_check_counter < 10:
            self.after(200, self._check_icon_periodically)
    
    def _center_window(self):
        """Center the window on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")
    
    def set_result(self, value):
        self.result = value
        self.destroy()

def ask_question_tk(parent, title, message, yes_text="Yes", no_text="No"):
    """Helper function to show custom Tk message box."""
    dialog = CTkMessageBox(parent, title, message, yes_text, no_text)
    dialog.wait_window()
    return dialog.result

class UserInterface(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        try:
            self.settings = AppSettings()
            self.setup_window()
            self.tokens = None
            auth_manager = AuthManager(ConfigManager())
            tokens = auth_manager.auto_login()
            if tokens:
                self.tokens = tokens
                self.show_validation_window()
            else:
                self.show_login_window()
            self.mainloop()
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to start application: {str(e)}")
            self.destroy()
    
    def setup_window(self) -> None:
        """Configure the main window settings."""
        self.title(f"{self.settings.login_settings['Window']['title']} V{self.settings.login_settings['Window']['version']}")
        self.center_window()
        self.resizable(height=False, width=False)
        
        icon_path = self.settings.base_path / "images" / "logo.ico"
        if icon_path.exists():
            self.iconbitmap(str(icon_path))
    
    def center_window(self) -> None:
        """Center the window on screen."""
        self.update_idletasks()
        width, height = self.settings.login_settings['Window']['geometry'].split('x')
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x = (screen_width - int(width)) // 2
        y = (screen_height - int(height)) // 2
        
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def show_login_window(self) -> None:
        self.login_frame = LoginFrame(
            master=self,
            on_login=self.on_login_success,
            settings=self.settings.login_settings,
            auto_login_callback=self.try_auto_login
        )
    
    def try_auto_login(self) -> None:
        auth_manager = AuthManager(ConfigManager())
        tokens = auth_manager.auto_login()
        if tokens:
            self.tokens = tokens
            self.on_login_success(tokens)
    
    def show_validation_window(self) -> None:
        self.validation_frame = ValidationFrame(
            master=self,
            on_logout=self.log_off,
            settings=self.settings.validate_settings,
            tokens=self.tokens
        )
        self.title(f"{self.settings.validate_settings['Window']['title']} V{self.settings.validate_settings['Window']['version']}")
        self.after(500, self.check_for_updates)
    
    def on_login_success(self, tokens: Tuple[str, str]) -> None:
        self.tokens = tokens
        if hasattr(self, 'login_frame'):
            self.login_frame.destroy()
        self.show_validation_window()
    
    def log_off(self) -> None:
        if hasattr(self, 'validation_frame'):
            self.validation_frame.destroy()
        CacheManager().clear_cache()
        self.tokens = None
        self.show_login_window()
            
    def check_for_updates(self) -> None:
        try:
            api_client = APIClient(ConfigManager(), AuthManager(ConfigManager()))
            if not api_client.check_version():
                # Use custom CTk message box
                response = ask_question_tk(
                    self,  # Parent window
                    "Actualizare",
                    "O noua versiune este disponibila.\nDoriti sa faceti actualizarea?",
                    yes_text="Actualizare",
                    no_text="Anulare"
                )
                
                if response:  # True if "Actualizare" clicked
                    self.progress_window = CTkProgressWindow(self, "Actualizare aplicatie")
                    threading.Thread(
                        target=self._perform_update,
                        args=(api_client,),
                        daemon=True
                    ).start()
                    
        except Exception as e:
            # Fallback to tkinter messagebox on error
            messagebox.showerror("Update Error", f"Failed to check for updates: {str(e)}")

    def _perform_update(self, api_client):
        """Perform update in background thread with progress updates."""
        try:
            self.progress_window.update_progress(0, "Starting update...")
            
            base_folder = self.settings.base_path.parent
            version_url = api_client.base_url + api_client.config.get('METADATA', 'version')

            # Get download URL
            self.progress_window.update_progress(0.1, "Se verifica versiune...")
            response = api_client._get_authorized(version_url)
            download_url = response.json()[0]['file']

            # Download to temporary file
            self.progress_window.update_progress(0.2, "Actualizarea se descarca...")
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
                temp_path = Path(temp_file.name)
                with requests.get(download_url, stream=True) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get('content-length', 0))
                    downloaded = 0
                    
                    for chunk in r.iter_content(chunk_size=8192):
                        if self.progress_window.cancelled:
                            raise Exception("Actualizarea a fost anulata!")
                        
                        temp_file.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress (20-70% range for download)
                        progress = 0.2 + (0.5 * (downloaded / total_size))
                        self.progress_window.update_progress(
                            progress,
                            "Actualizarea se descarca...",
                            f"{downloaded/1024/1024:.1f}MB / {total_size/1024/1024:.1f}MB"
                        )

            # Extract files (70-90% range for extraction)
            self.progress_window.update_progress(0.7, "Fisierele se extrag...")
            extract_path = base_folder / "temp_extracted"
            extract_path.mkdir(exist_ok=True)
            with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                total_files = len(zip_ref.infolist())
                for i, file in enumerate(zip_ref.infolist()):
                    zip_ref.extract(file, extract_path)
                    progress = 0.7 + (0.2 * (i / total_files))
                    self.progress_window.update_progress(
                        progress,
                        "Fisierele se extrag...",
                        f"File {i+1} of {total_files}"
                    )

            temp_path.unlink()

            # Install files (90-100% range for installation)
            self.progress_window.update_progress(0.9, "Actualizarea se instaleaza...")
            extracted_folders = [f for f in extract_path.iterdir() if f.is_dir()]
            if extracted_folders:
                resources_path = extracted_folders[0] / 'resources'
                if resources_path.exists():
                    total_items = len(list(resources_path.iterdir()))
                    for i, item in enumerate(resources_path.iterdir()):
                        target = base_folder / item.name
                        if item.is_dir():
                            shutil.rmtree(target, ignore_errors=True)
                            shutil.move(str(item), str(target))
                        else:
                            target.unlink(missing_ok=True)
                            shutil.move(str(item), str(target))
                        
                        progress = 0.9 + (0.1 * (i / total_items))
                        self.progress_window.update_progress(
                            progress,
                            "Actualizarea se instaleaza...",
                            f"Installing {item.name}"
                        )

            shutil.rmtree(extract_path)
            self.progress_window.complete(True, "Actulizarea a fost descarcata cu succes!")
            
            # Close application after a short delay
            # self.after(2000, self.destroy)

        except Exception as e:
            print(f"Update failed: {str(e)}")  # Debug output
            if 'extract_path' in locals() and extract_path.exists():
                shutil.rmtree(extract_path, ignore_errors=True)
            if 'temp_path' in locals() and temp_path.exists():
                temp_path.unlink(missing_ok=True)
            
            error_msg = str(e)
            if "cancelled" in error_msg.lower():
                error_msg = "Actualizarea a fost oprita de utilizator!"
            self.progress_window.complete(False, error_msg)