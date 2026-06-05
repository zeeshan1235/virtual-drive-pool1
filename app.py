import os
import google.oauth2.credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import pickle
import json

SCOPES = ['https://www.googleapis.com/auth/drive']
CONFIG_FILE = 'accounts_config.json'

def load_accounts():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"accounts": []}

def save_accounts(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def add_new_account():
    print("\n[+] Adding a NEW Google Account to the Virtual Pool...")
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', 
        SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    print(f'\n[!] Open this URL:\n{auth_url}\n')
    code = input('[?] Enter code: ').strip()
    flow.fetch_token(code=code)
    creds = flow.credentials
    
    # ٹوکن کو اسٹرنگ میں تبدیل کرنا تاکہ JSON میں محفوظ ہو سکے
    creds_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }
    
    config = load_accounts()
    account_id = f"account_{len(config['accounts']) + 1}"
    config["accounts"].append({"id": account_id, "creds": creds_data})
    save_accounts(config)
    print(f"[✓] Successfully added {account_id} to the system!\n")

def get_drive_service(creds_data):
    creds = google.oauth2.credentials.Credentials(**creds_data)
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('drive', 'v3', credentials=creds)

def upload_to_virtual_drive(file_path):
    config = load_accounts()
    if not config["accounts"]:
        print("[X] Error: No accounts found. Please add an account first.")
        return
        
    if not os.path.exists(file_path):
        print("[X] Error: Local file not found.")
        return

    file_name = os.path.basename(file_path)
    
    # باری باری تمام اکاؤنٹس کو چیک کرنا
    for acc in config["accounts"]:
        try:
            service = get_drive_service(acc["creds"])
            about = service.about().get(fields="storageQuota").execute()
            quota = about.get('storageQuota', {})
            
            limit = int(quota.get('limit', 0)) / (1024**3)
            usage = int(quota.get('usage', 0)) / (1024**3)
            free = limit - usage
            
            print(f"\nChecking {acc['id']} -> Free Space: {free:.2f} GB")
            
            if free > 0.05:  # اگر 50 ایم بی سے زیادہ جگہ خالی ہے
                print(f"[+] Found space! Uploading '{file_name}' to {acc['id']}...")
                file_metadata = {'name': file_name}
                media = MediaFileUpload(file_path, resumable=True)
                uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                print(f"[✓] Upload Successful! Cloud ID: {uploaded_file.get('id')}\n")
                return
            else:
                print(f"[-] {acc['id']} is full, skipping to next...")
        except Exception as e:
            print(f"[X] Error reading {acc['id']}: {e}")
            
    print("[X] Error: All connected accounts are completely full! Please add a new account.")

if __name__ == '__main__':
    config = load_accounts()
    if not config["accounts"]:
        # پہلی بار رن ہونے پر اکاؤنٹ ایڈ کرے گا
        add_new_account()
    
    print("1. Upload a File")
    print("2. Add another Google Account (15GB Extra)")
    choice = input("Choose option (1/2): ").strip()
    
    if choice == '1':
        file_to_up = input("Enter file name to upload: ").strip()
        upload_to_virtual_drive(file_to_up)
    elif choice == '2':
        add_new_account()
