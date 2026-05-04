from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import resend
import os
import json
import io
import time

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/api/v1/inference")
async def run_inference(email: str = Form(...), drive_file_id: str = Form(...)):
    temp_path = f"/tmp/{drive_file_id}.pdf"
    try:
        # 1. Dosyayı Drive'dan Güvenli Çekme (Service Account ile)
        json_key = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not json_key:
            raise Exception("Vercel'de GOOGLE_SERVICE_ACCOUNT_JSON değişkeni eksik.")
            
        info = json.loads(json_key)
        creds = service_account.Credentials.from_service_account_info(info)
        drive_service = build('drive', 'v3', credentials=creds)

        request = drive_service.files().get_media(fileId=drive_file_id)
        with io.FileIO(temp_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()

        # 2. Gemini File API ile Derin Analiz
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        uploaded_file = genai.upload_file(path=temp_path)
        
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(2)
            uploaded_file = genai.get_file(uploaded_file.name)

        # KRİTİK YAMA: API'nin tanıdığı geçerli model ismi (latest eklendi)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content([
            "Sen Atilla Yalçın'ın otonom strateji asistanısın. Bu dökümanı profesyonelce analiz et ve yönetici raporu hazırla.",
            uploaded_file
        ])

        # 3. Resend Üzerinden Kurumsal Gönderim
        resend.api_key = os.environ.get("RESEND_API_KEY")
        resend.Emails.send({
            "from": "ATILLAYALCIN_AI_OS <info@atillayalcin.ai>",
            "to": email,
            "subject": "Stratejik Analiz Raporu v16.0.5",
            "html": f"<h3>Stratejik Analiz Raporu</h3><hr><div style='white-space: pre-wrap; line-height: 1.6;'>{response.text}</div>"
        })

        if os.path.exists(temp_path): os.remove(temp_path)
        return {"status": "success"}

    except Exception as e:
        if os.path.exists(temp_path): os.remove(temp_path)
        return {"status": "error", "message": f"Backend Çökmesi: {str(e)}"}
