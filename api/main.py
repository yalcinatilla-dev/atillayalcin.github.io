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

        # 1. Gemini Yapılandırması
        api_key = os.environ.get("GEMINI_API_KEY")
        # DİKKAT: models/ önekini ve tam model adını kullanarak v1beta hatasını baypas ediyoruz
        genai.configure(api_key=api_key)
        
        # Dosyayı Gemini File API'ye yükle
        uploaded_gemini_file = genai.upload_file(path=temp_path)
        
        # İşlenme durumunu kontrol et
        while uploaded_gemini_file.state.name == "PROCESSING":
            time.sleep(1)
            uploaded_gemini_file = genai.get_file(uploaded_gemini_file.name)

        # ÇÖZÜM: GenerativeModel ismini 'models/gemini-1.5-flash' olarak tam tanımlıyoruz
        model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
        
        # Analiz Talimatı
        response = model.generate_content([
            "Sen Atilla Yalçın'ın stratejik AI asistanısın. Bu dökümanı derinlemesine analiz et ve profesyonel bir yönetici raporu hazırla.",
            uploaded_gemini_file
        ])

        # 2. Resend ile Rapor Gönderimi
        resend.api_key = os.environ.get("RESEND_API_KEY")
        resend.Emails.send({
            "from": "ATILLAYALCIN_AI_OS <info@atillayalcin.ai>",
            "to": email,
            "subject": f"Stratejik Analiz: {file.filename}",
            "html": f"<h3>Stratejik Analiz Raporu v16.0.5</h3><hr><div style='white-space: pre-wrap; font-family: sans-serif; line-height: 1.6;'>{response.text}</div>"
        })

        # 3. Drive Arşivleme (Sessiz Çalışır)
        try:
            info = json.loads(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"))
            creds = service_account.Credentials.from_service_account_info(info)
            drive_service = build('drive', 'v3', credentials=creds)
            file_metadata = {'name': file.filename, 'parents': ['1bRuquZUIbCe-6Rv3QX_favf8U00NXQT0']}
            media = MediaIoBaseUpload(io.BytesIO(content), mimetype=file.content_type)
            drive_service.files().create(body=file_metadata, media_body=media).execute()
        except Exception as drive_err:
            print(f"Drive yedekleme atlandı: {drive_err}")

        if os.path.exists(temp_path): os.remove(temp_path)
        return {"status": "success"}

    except Exception as e:
        if os.path.exists(temp_path): os.remove(temp_path)
        return {"status": "error", "message": f"Sistem Analiz Hatası: {str(e)}"}
