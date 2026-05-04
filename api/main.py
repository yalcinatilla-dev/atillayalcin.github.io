import os, json, resend
from fastapi import FastAPI, Form, UploadFile, File
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

app = FastAPI()

@app.post("/api/v1/inference")
async def run_inference(email: str = Form(...), file: UploadFile = File(...)):
    try:
        # 1. Drive Servis Hesabı Yetkilendirme
        info = json.loads(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"))
        creds = service_account.Credentials.from_service_account_info(info)
        drive_service = build('drive', 'v3', credentials=creds)

        # 2. Dosyayı Drive'a Otonom Yükleme
        folder_id = '1yQ9oI17e7_Xp59Nsh09X-h33yM99P6l-' # Doğru ID (9oI)
        file_metadata = {'name': file.filename, 'parents': [folder_id]}
        media = MediaIoBaseUpload(io.BytesIO(await file.read()), mimetype=file.content_type)
        drive_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        # 3. Gemini 1.5 Pro Analizi
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(f"Drive ID: {drive_file.get('id')}. Belgeyi Atilla Yalçın standartlarında analiz et.")

        # 4. Kurumsal Mail Gönderimi
        resend.api_key = os.environ.get("RESEND_API_KEY")
        resend.Emails.send({
            "from": "ATILLAYALCIN_AI_OS <info@atillayalcin.ai>",
            "to": email,
            "subject": "Stratejik Analiz Raporu v16.0.5",
            "text": response.text
        })
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
