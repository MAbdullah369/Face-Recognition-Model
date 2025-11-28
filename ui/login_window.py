import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading

class LoginWindow:
    def __init__(self, parent, auth_system, on_login_success, on_register_click):
        self.parent = parent
        self.auth_system = auth_system
        self.on_login_success = on_login_success
        self.on_register_click = on_register_click
        
        self.setup_ui()
        self.setup_camera()
    
    def setup_ui(self):
        """Setup the login interface"""
        # Main frame
        self.main_frame = ttk.Frame(self.parent, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="FaceAuth - Login", 
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Camera frame
        self.camera_frame = ttk.LabelFrame(self.main_frame, text="Camera Preview", padding="10")
        self.camera_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.video_label = ttk.Label(self.camera_frame)
        self.video_label.grid(row=0, column=0)
        
        # Status
        self.status_var = tk.StringVar(value="Ready to authenticate...")
        status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        status_label.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.login_btn = ttk.Button(
            button_frame, 
            text="Authenticate", 
            command=self.authenticate,
            state="normal"
        )
        self.login_btn.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="Register New User", 
            command=self.on_register_click
        ).grid(row=0, column=1, padx=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Admin Panel",
            command=self.show_admin
        ).grid(row=0, column=2, padx=(10, 0))
        
        # Configure grid weights
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
    
    def setup_camera(self):
        """Initialize camera and start video stream"""
        if self.auth_system.initialize_camera():
            self.update_camera()
        else:
            messagebox.showerror("Error", "Could not initialize camera")
    
    def update_camera(self):
        """Update camera feed"""
        frame, face_count = self.auth_system.get_camera_frame()
        
        if frame is not None:
            # Convert to PhotoImage
            image = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image=image)
            
            self.video_label.configure(image=photo)
            self.video_label.image = photo
            
            # Update status based on face detection
            if face_count == 1:
                self.status_var.set("✅ Face detected - Ready to authenticate")
                self.login_btn.config(state="normal")
            elif face_count > 1:
                self.status_var.set("❌ Multiple faces detected")
                self.login_btn.config(state="disabled")
            else:
                self.status_var.set("👤 Position your face in frame")
                self.login_btn.config(state="disabled")
        
        # Schedule next update
        self.parent.after(50, self.update_camera)
    
    def authenticate(self):
        """Perform authentication"""
        self.login_btn.config(state="disabled")
        self.status_var.set("🔄 Authenticating...")
        
        # Run authentication in thread to avoid blocking UI
        def auth_thread():
            success, message, confidence, username = self.auth_system.authenticate_user()
            
            # Update UI in main thread
            self.parent.after(0, lambda: self.auth_complete(success, message, username))
        
        threading.Thread(target=auth_thread, daemon=True).start()
    
    def auth_complete(self, success, message, username):
        """Handle authentication completion"""
        if success:
            self.status_var.set(f"✅ {message}")
            messagebox.showinfo("Success", message)
            self.on_login_success(username)
        else:
            self.status_var.set(f"❌ {message}")
            messagebox.showerror("Authentication Failed", message)
        
        self.login_btn.config(state="normal")
    
    def show_admin(self):
        """Show admin panel"""
        from ui.admin_window import AdminWindow
        
        admin_window = tk.Toplevel(self.parent)
        AdminWindow(admin_window, self.auth_system)
    
    def cleanup(self):
        """Clean up resources"""
        self.auth_system.release_camera()