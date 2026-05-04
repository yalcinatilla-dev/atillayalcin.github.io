from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import resend
import os
import json
import io

app = FastAPI()

# CORS Ayarları (Failed to fetch hatasını çözer)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/inference")
async def run_inference(email: str = Form(...), file: UploadFile = File(...)):
    try:
        # 1. Google Drive Yetkilendirme (Service Account)
        json_key = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not json_key:
            return {"status": "error", "message": "Service Account JSON eksik!"}
            
        info = json.loads(json_key)
        creds = service_account.Credentials.from_service_account_info(info)
        drive_service = build('drive', 'v3', credentials=creds)

        # 2. Drive'a Otonom Yükleme
        folder_id = '1yQ9oI17e7_Xp59Nsh09X-h33yM99P6l-'
        file_metadata = {'name': file.filename, 'parents': [folder_id]}
        
        content = await file.read()
        media = MediaIoBaseUpload(io.BytesIO(content), mimetype=file.content_type)
        drive_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        # 3. Gemini 1.5 Pro Analizi
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(f"Drive ID: {drive_file.get('id')}. Belgeyi Atilla Yalçın standartlarında analiz et.")

        # 4. Resend ile Rapor Gönderimi
        resend.api_key = os.environ.get("RESEND_API_KEY")
        resend.Emails.send({
            "from": "ATILLAYALCIN_AI_OS <info@atillayalcin.ai>",
            "to": email,
            "subject": f"Stratejik Analiz: {file.filename}",
            "text": response.text
        })

        return {"status": "success", "drive_id": drive_file.get('id')}
    except Exception as e:
        return {"status": "error", "message": str(e)}
