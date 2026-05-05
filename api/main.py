import os, json, io
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/inference")
async def run_inference(email: str = Form(...), file: UploadFile = File(...)):
    try:
        # 1. Drive Yetkilendirme (Service Account)
        json_key = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not json_key:
            return {"status": "error", "message": "Sistem hatası: Drive yetkisi eksik."}
        
        info = json.loads(json_key)
        creds = service_account.Credentials.from_service_account_info(info)
        drive_service = build('drive', 'v3', credentials=creds)

        # 2. Dosya Hazırlığı (Email bilgisini dosya adına ekliyoruz)
        content = await file.read()
        folder_id = '1bRuquZUIbCe-6Rv3QX_favf8U00NXQT0'
        
        # Dosya adı formatı: [email] Orijinal_Dosya_Adi.pdf
        new_filename = f"[{email}] {file.filename}"
        
        file_metadata = {
            'name': new_filename,
            'parents': [folder_id],
            'description': f"Gönderen Kullanıcı: {email}"
        }
        
        media = MediaIoBaseUpload(io.BytesIO(content), mimetype=file.content_type)
        
        # 3. Drive'a Otonom Yükleme
        drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        return {"status": "success"}

    except Exception as e:
        return {"status": "error", "message": f"İletim Hatası: {str(e)}"}
