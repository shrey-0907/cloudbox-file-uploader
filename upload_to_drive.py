from tkinter import Tk, Label, Button, filedialog, messagebox
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

# Define the scope for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class CloudBoxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CloudBox File Uploader")
        self.root.geometry("400x200")

        # UI Components
        Label(root, text="CloudBox File Uploader", font=("Arial", 16)).pack(pady=10)
        Button(root, text="Authenticate Google Drive", command=self.authenticate_google_drive).pack(pady=5)
        Button(root, text="Select File", command=self.select_file).pack(pady=5)
        Button(root, text="Upload File", command=self.upload_file).pack(pady=5)

        self.status_label = Label(root, text="", fg="green")
        self.status_label.pack(pady=10)

        # Initialize variables
        self.file_path = None
        self.service = None
        self.folder_id = "1B0fzHUfaGcbnqFjhqaNcKvz9WAcTJQvy" 

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


if __name__ == "__main__":
    root = Tk()
    app = CloudBoxApp(root)
    root.mainloop()
