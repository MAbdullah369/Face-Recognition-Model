import gradio as gr
import numpy as np
import cv2
from face_auth import AuthManager
import os

# Initialize Auth Manager
auth_manager = AuthManager()

def register_user(name, image):
    """Handle user registration"""
    if image is None:
        return "Please capture an image first"
    
    # Convert Gradio image to numpy array
    img_array = np.array(image)
    result = auth_manager.register_user(name, img_array)
    return result["message"]

def authenticate_user(image):
    """Handle user authentication"""
    if image is None:
        return "Please capture an image first"
    
    img_array = np.array(image)
    result = auth_manager.authenticate_user(img_array)
    return result["message"]

def get_users():
    """Get list of registered users"""
    users = auth_manager.get_registered_users()
    if users:
        return "\n".join([f"• {user}" for user in users])
    else:
        return "No registered users"

def delete_user(username):
    """Delete a user"""
    if not username:
        return "Please enter a username"
    
    result = auth_manager.delete_user(username.strip())
    return result["message"]

# Create Gradio interface
with gr.Blocks(theme=gr.themes.Soft(), title="FaceAuth - Facial Recognition System") as demo:
    gr.Markdown(
        """
        # 🪪 FaceAuth - Facial Recognition System
        **Secure, password-free authentication using facial recognition technology**
        """
    )
    
    with gr.Tab("👤 Register"):
        with gr.Row():
            with gr.Column():
                reg_name = gr.Textbox(
                    label="Enter your username",
                    placeholder="e.g., john_doe",
                    max_lines=1
                )
                reg_camera = gr.Image(
                    sources=["webcam"],
                    label="Face Camera",
                    type="pil",
                    height=300
                )
                reg_button = gr.Button("Register User", variant="primary")
            
            with gr.Column():
                reg_output = gr.Textbox(
                    label="Registration Status",
                    interactive=False,
                    lines=3
                )
        
        reg_button.click(
            fn=register_user,
            inputs=[reg_name, reg_camera],
            outputs=reg_output
        )
    
    with gr.Tab("🔐 Login"):
        with gr.Row():
            with gr.Column():
                auth_camera = gr.Image(
                    sources=["webcam"], 
                    label="Look at the camera to login",
                    type="pil",
                    height=300
                )
                auth_button = gr.Button("Authenticate", variant="primary")
            
            with gr.Column():
                auth_output = gr.Textbox(
                    label="Authentication Status",
                    interactive=False,
                    lines=3
                )
        
        auth_button.click(
            fn=authenticate_user,
            inputs=[auth_camera],
            outputs=auth_output
        )
    
    with gr.Tab("👥 Manage Users"):
        with gr.Row():
            with gr.Column():
                refresh_button = gr.Button("Refresh User List", variant="secondary")
                users_list = gr.Textbox(
                    label="Registered Users",
                    interactive=False,
                    lines=8
                )
            
            with gr.Column():
                delete_username = gr.Textbox(
                    label="Username to delete",
                    placeholder="Enter username to remove",
                    max_lines=1
                )
                delete_button = gr.Button("Delete User", variant="stop")
                delete_output = gr.Textbox(
                    label="Deletion Status",
                    interactive=False,
                    lines=2
                )
        
        refresh_button.click(
            fn=get_users,
            outputs=users_list
        )
        
        delete_button.click(
            fn=delete_user,
            inputs=[delete_username],
            outputs=delete_output
        ).then(
            fn=get_users,
            outputs=users_list
        )
    
    gr.Markdown(
        """
        ---
        ### 🚀 How to Use:
        1. **Register**: Enter username and capture face image in the Register tab
        2. **Login**: Use the Login tab to authenticate with your face
        3. **Manage**: View and delete users in the Manage Users tab
        
        **Note**: Ensure good lighting and clear face visibility for best results.
        """
    )

# Launch application
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Set to True for public URL
        debug=True
    )