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
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/inference")
async def run_inference(email: str = Form(...), file: UploadFile = File(...)):
    temp_path = f"/tmp/{file.filename}"
    try:
        content = await file.read()
        with open(temp_path, "wb") as f:
            with io.BytesIO(content) as buffer:
                f.write(buffer.getbuffer())

        # 1. Drive'a Arşivleme (Corporate Memory)
        json_key = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        info = json.loads(json_key)
        creds = service_account.Credentials.from_service_account_info(info)
        drive_service = build('drive', 'v3', credentials=creds)

        folder_id = '1yQ9oI17e7_Xp59Nsh09X-h33yM99P6l-' # Doğru ID (Büyük I)
        file_metadata = {'name': file.filename, 'parents': [folder_id]}
        media = MediaIoBaseUpload(io.BytesIO(content), mimetype=file.content_type)
        drive_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        # 2. Gemini File API'ye Yükleme (Analiz İçin)
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        uploaded_gemini_file = genai.upload_file(path=temp_path, display_name=file.filename)
        
        # Dosya işlenene kadar bekle (Kritik adım)
        while uploaded_gemini_file.state.name == "PROCESSING":
            time.sleep(1)
            uploaded_gemini_file = genai.get_file(uploaded_gemini_file.name)

        # 3. Gemini 1.5 Pro Analizi
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content([
            "Sistem: ATILLAYALCIN_AI_OS. Sen stratejik bir iş ortağısın. "
            "Bu dökümanı derinlemesine analiz et ve kurumsal bir rapor hazırla.",
            uploaded_gemini_file
        ])

        # 4. Resend ile Gönderim
        resend.api_key = os.environ.get("RESEND_API_KEY")
        resend.Emails.send({
            "from": "ATILLAYALCIN_AI_OS <info@atillayalcin.ai>",
            "to": email,
            "subject": f"Stratejik Analiz: {file.filename}",
            "html": f"<h3>Analiz Raporu v16.0.5</h3><div style='white-space: pre-wrap;'>{response.text}</div>"
        })

        # Temizlik
        if os.path.exists(temp_path): os.remove(temp_path)
        
        return {"status": "success", "drive_id": drive_file.get('id')}

    except Exception as e:
        if os.path.exists(temp_path): os.remove(temp_path)
        return {"status": "error", "message": str(e)}
