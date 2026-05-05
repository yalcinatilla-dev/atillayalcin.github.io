import os, json, io, time
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import resend

app = FastAPI()

# GÜÇLENDİRİLMİŞ CORS AYARI (403 ENGELİ İÇİN)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/inference")
async def run_inference(email: str = Form(...), file: UploadFile = File(...)):
    temp_path = f"/tmp/{file.filename}"
    try:
        content = await file.read()
        with open(temp_path, "wb") as f: f.write(content)

        # 1. Gemini Yapılandırması
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        
        uploaded_file = genai.upload_file(path=temp_path)
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(2)
            uploaded_file = genai.get_file(uploaded_file.name)

        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([
            "Sen Atilla Yalçın'ın stratejik asistanısın. Bu dökümanı profesyonelce analiz et.",
            uploaded_file
        ])

        # 2. Resend Rapor Gönderimi
        resend.api_key = os.environ.get("RESEND_API_KEY")
        resend.Emails.send({
            "from": "ATILLAYALCIN_AI_OS <info@atillayalcin.ai>",
            "to": email,
            "subject": f"Stratejik Analiz: {file.filename}",
            "html": f"<div style='font-family:sans-serif; line-height:1.6;'>{response.text.replace(chr(10), '<br>')}</div>"
        })

        # 3. Drive'a Arşivleme (Sessiz Çalışır)
        try:
            drive_creds = service_account.Credentials.from_service_account_info(json.loads(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")))
            drive_service = build('drive', 'v3', credentials=drive_creds)
            file_metadata = {'name': file.filename, 'parents': ['1bRuquZUIbCe-6Rv3QX_favf8U00NXQT0']}
            media = MediaIoBaseUpload(io.BytesIO(content), mimetype=file.content_type)
            drive_service.files().create(body=file_metadata, media_body=media).execute()
        except: pass

        if os.path.exists(temp_path): os.remove(temp_path)
        return {"status": "success"}

    except Exception as e:
        if os.path.exists(temp_path): os.remove(temp_path)
        return {"status": "error", "message": str(e)}
