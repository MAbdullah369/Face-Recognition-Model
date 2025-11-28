import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading

class RegisterWindow:
    def __init__(self, parent, auth_system, on_back):
        self.parent = parent
        self.auth_system = auth_system
        self.on_back = on_back
        
        self.setup_ui()
        self.setup_camera()
    
    def setup_ui(self):
        """Setup the registration interface"""
        # Main frame
        self.main_frame = ttk.Frame(self.parent, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="Register New User", 
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # User info frame
        info_frame = ttk.LabelFrame(self.main_frame, text="User Information", padding="10")
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20), padx=(0, 10))
        
        ttk.Label(info_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(info_frame, textvariable=self.username_var, width=20)
        self.username_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(info_frame, text="Full Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.fullname_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.fullname_var, width=20).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        ttk.Label(info_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.email_var, width=20).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Camera frame
        camera_frame = ttk.LabelFrame(self.main_frame, text="Face Capture", padding="10")
        camera_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        self.video_label = ttk.Label(camera_frame)
        self.video_label.grid(row=0, column=0)
        
        # Status
        self.status_var = tk.StringVar(value="Ready to register...")
        status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        status_label.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.register_btn = ttk.Button(
            button_frame, 
            text="Register User", 
            command=self.register_user,
            state="normal"
        )
        self.register_btn.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="Back to Login", 
            command=self.on_back
        ).grid(row=0, column=1, padx=(10, 0))
        
        # Configure grid weights
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        info_frame.columnconfigure(1, weight=1)
        camera_frame.columnconfigure(0, weight=1)
        camera_frame.rowconfigure(0, weight=1)
    
    def setup_camera(self):
        """Initialize camera and start video stream"""
        if not self.auth_system.initialize_camera():
            messagebox.showerror("Error", "Could not initialize camera")
            return
        
        self.update_camera()
    
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
                self.status_var.set("✅ Face detected - Ready to register")
                self.register_btn.config(state="normal")
            elif face_count > 1:
                self.status_var.set("❌ Multiple faces detected")
                self.register_btn.config(state="disabled")
            else:
                self.status_var.set("👤 Position your face in frame")
                self.register_btn.config(state="disabled")
        
        # Schedule next update
        self.parent.after(50, self.update_camera)
    
    def register_user(self):
        """Register new user"""
        username = self.username_var.get().strip()
        
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        self.register_btn.config(state="disabled")
        self.status_var.set("🔄 Registering user...")
        
        def register_thread():
            # First register user in database
            success, message = self.auth_system.register_user(
                username, 
                self.fullname_var.get(), 
                self.email_var.get()
            )
            
            if not success:
                self.parent.after(0, lambda: self.registration_complete(False, message))
                return
            
            # Then capture and register face
            success, message = self.auth_system.capture_and_register_face(username)
            self.parent.after(0, lambda: self.registration_complete(success, message))
        
        threading.Thread(target=register_thread, daemon=True).start()
    
    def registration_complete(self, success, message):
        """Handle registration completion"""
        if success:
            self.status_var.set("✅ Registration successful!")
            messagebox.showinfo("Success", message)
            self.on_back()
        else:
            self.status_var.set(f"❌ {message}")
            messagebox.showerror("Registration Failed", message)
            self.register_btn.config(state="normal")
    
    def cleanup(self):
        """Clean up resources"""
        self.auth_system.release_camera()