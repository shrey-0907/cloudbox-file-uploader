from tkinter import Tk, Label, Button, filedialog, messagebox, Canvas
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from PIL import Image, ImageTk
import os
import pickle

# Define the scope for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class CloudBoxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CloudBox File Uploader")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Canvas for background
        self.canvas = Canvas(root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Load and set background image
        self.bg_image = Image.open("image.jpg")  # Ensure this file exists in the same directory
        self.bg_photo = None  # Initialize to None
        self.background = None  # Initialize to None

        # UI Components
        self.title_label = Label(root, text="CloudBox File Uploader", font=("Arial", 20, "bold"), bg="#ffffff", fg="#333333")
        self.authenticate_button = Button(root, text="Authenticate Google Drive", command=self.authenticate_google_drive, font=("Arial", 12), bg="#4caf50", fg="white")
        self.select_button = Button(root, text="Select File", command=self.select_file, font=("Arial", 12), bg="#2196f3", fg="white")
        self.upload_button = Button(root, text="Upload File", command=self.upload_file, font=("Arial", 12), bg="#f44336", fg="white")
        self.status_label = Label(root, text="", font=("Arial", 12), bg="#ffffff")

        # Place components in the center
        self.update_positions()

        # Bind resizing to adjust the background image
        root.bind("<Configure>", self.resize_background)

        # Initialize variables
        self.file_path = None
        self.service = None
        self.folder_id = "1swELAYudL3yHLppgK2lu9BYwSn4HGRnv"  # Replace with your actual CloudBox folder ID

        # Initial call to display the resized background correctly
        self.resize_background()

    def update_positions(self):
        """Update positions of all UI components."""
        self.title_label.place(relx=0.5, rely=0.2, anchor="center")
        self.authenticate_button.place(relx=0.5, rely=0.4, anchor="center")
        self.select_button.place(relx=0.5, rely=0.5, anchor="center")
        self.upload_button.place(relx=0.5, rely=0.6, anchor="center")
        self.status_label.place(relx=0.5, rely=0.7, anchor="center")

    def resize_background(self, event=None):
        """Resize the background image dynamically."""
        new_width = self.root.winfo_width()
        new_height = self.root.winfo_height()
        resized_image = self.bg_image.resize((new_width, new_height), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized_image)
        if self.background:
            self.canvas.itemconfig(self.background, image=self.bg_photo)
        else:
            self.background = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

    def authenticate_google_drive(self):
        """Authenticate the app with Google Drive."""
        try:
            creds = None
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)

                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)

            self.service = build('drive', 'v3', credentials=creds)
            messagebox.showinfo("Authentication", "Google Drive authenticated successfully!")
            self.status_label.config(text="Google Drive authenticated.", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"Authentication failed: {e}")
            self.status_label.config(text="Authentication failed.", fg="red")

    def select_file(self):
        """Open file dialog to select a file."""
        self.file_path = filedialog.askopenfilename(title="Select a file to upload")
        if self.file_path:
            self.status_label.config(text=f"File selected: {os.path.basename(self.file_path)}", fg="blue")
        else:
            self.status_label.config(text="No file selected.", fg="red")

    def upload_file(self):
        """Upload the selected file to Google Drive."""
        if not self.file_path:
            messagebox.showwarning("No File", "Please select a file to upload.")
            return
        
        if not os.path.exists(self.file_path):
            messagebox.showerror("File Not Found", f"The file '{self.file_path}' does not exist.")
            self.status_label.config(text="File not found.", fg="red")
            return

        if not self.service:
            messagebox.showwarning("Not Authenticated", "Please authenticate with Google Drive first.")
            return

        try:
            # Create metadata for the file
            file_name = os.path.basename(self.file_path)
            file_metadata = {'name': file_name, 'parents': [self.folder_id]}

            # Upload the file
            media = MediaFileUpload(self.file_path, resumable=True)
            file = self.service.files().create(
                body=file_metadata, media_body=media, fields='id').execute()

            messagebox.showinfo("Success", f"File uploaded successfully! File ID: {file.get('id')}")
            self.status_label.config(text="File uploaded successfully!", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"File upload failed: {e}")
            self.status_label.config(text="File upload failed.", fg="red")

    def verify_folder_access(self):
        """Verify access to the folder."""
        if not self.service:
            messagebox.showwarning("Not Authenticated", "Please authenticate with Google Drive first.")
            return
        try:
            # Try to list the files in the folder
            results = self.service.files().list(
                q=f"'{self.folder_id}' in parents", fields="files(id, name)").execute()
            items = results.get('files', [])
            if not items:
                messagebox.showinfo("Folder Empty", "The folder is empty.")
            else:
                file_list = "\n".join([f"{file['name']} (ID: {file['id']})" for file in items])
                messagebox.showinfo("Files in Folder", f"Files in folder:\n{file_list}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to access the folder: {e}")

if __name__ == "__main__":
    root = Tk()
    app = CloudBoxApp(root)
    root.mainloop()
