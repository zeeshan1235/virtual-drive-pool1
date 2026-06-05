import os
import json
import google.oauth2.credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView

CONFIG_FILE = 'accounts_config.json'

class VirtualDriveApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.lbl = Label(text="Virtual Cloud Drive Uploader", size_hint_y=0.1, font_size=20)
        self.layout.add_widget(self.lbl)
        
        self.file_chooser = FileChooserIconView(path="/sdcard")
        self.layout.add_widget(self.file_chooser)
        
        self.btn = Button(text="Upload Selected File", size_hint_y=0.15, background_color=(0, 0.7, 0, 1))
        self.btn.bind(on_press=self.start_upload)
        self.layout.add_widget(self.btn)
        return self.layout

    def start_upload(self, instance):
        selected = self.file_chooser.selection
        if not selected:
            self.lbl.text = "⚠️ Please select a file first!"
            return
            
        file_path = selected[0]
        file_name = os.path.basename(file_path)
        self.lbl.text = f"Uploading: {file_name}..."
        
        if not os.path.exists(CONFIG_FILE):
            self.lbl.text = "X Error: accounts_config.json missing!"
            return
            
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            
        if not config.get("accounts"):
            self.lbl.text = "X Error: No accounts linked!"
            return

        for acc in config["accounts"]:
            try:
                creds = google.oauth2.credentials.Credentials(**acc["creds"])
                if not creds.valid and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                service = build('drive', 'v3', credentials=creds)
                
                file_metadata = {'name': file_name}
                media = MediaFileUpload(file_path, resumable=True)
                uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                self.lbl.text = f"✓ Uploaded to {acc['id']}!"
                return
            except Exception as e:
                continue
        self.lbl.text = "X All accounts full or failed!"

if __name__ == '__main__':
    VirtualDriveApp().run()
