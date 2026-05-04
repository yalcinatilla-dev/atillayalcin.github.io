from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import resend
import os, json, io, time

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/api/v1/inference")
async def run_inference(email: str = Form(...), file: UploadFile = File(...)):
    temp_path = f"/tmp/{file.filename}"
    try:
        content = await file.read()
        with open(temp_path, "wb") as f: f.write(content)

        # 1. Gemini 1.5 Flash ile Hızlı Analiz (Yeni Anahtar Gereklidir)
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        uploaded_gemini_file = genai.upload_file(path=temp_path)
        while uploaded_gemini_file.state.name == "PROCESSING":
            time.sleep(1)
            uploaded_gemini_file = genai.get_file(uploaded_gemini_file.name)

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([
            "Sen Atilla Yalçın'ın stratejik AI asistanısın. Bu dökümanı analiz et ve kurumsal rapor hazırla.",
            uploaded_gemini_file
        ])

        # 2. Resend ile Gönderim
        resend.api_key = os.environ.get("RESEND_API_KEY")
        resend.Emails.send({
            "from": "ATILLAYALCIN_AI_OS <info@atillayalcin.ai>",
            "to": email,
            "subject": f"Stratejik Analiz: {file.filename}",
            "html": f"<h3>Analiz Raporu v16.0.5</h3><div style='white-space: pre-wrap;'>{response.text}</div>"
        })

        # 3. Drive'a Sessiz Yedekleme (Arka Planda)
        try:
            info = json.loads(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"))
            creds = service_account.Credentials.from_service_account_info(info)
            drive_service = build('drive', 'v3', credentials=creds)
            file_metadata = {'name': file.filename, 'parents': ['1bRuquZUIbCe-6Rv3QX_favf8U00NXQT0']}
            media = MediaIoBaseUpload(io.BytesIO(content), mimetype=file.content_type)
            drive_service.files().create(body=file_metadata, media_body=media).execute()
        except: pass # Arşivleme hata verse de raporu etkilemez

        if os.path.exists(temp_path): os.remove(temp_path)
        return {"status": "success"}

    except Exception as e:
        if os.path.exists(temp_path): os.remove(temp_path)
        return {"status": "error", "message": f"Kritik Hata: {str(e)}"}
