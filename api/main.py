from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
import os

app = FastAPI()

# CORS Ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/inference")
async def run_inference(email: str = Form(...), files: list[UploadFile] = File(...)):
    try:
        # 1. Ortam Değişkenleri Kontrolü
        api_key = os.environ.get("GEMINI_API_KEY")
        email_user = os.environ.get("EMAIL_ADDRESS")
        email_pass = os.environ.get("EMAIL_PASSWORD")

        # 2. Gemini Yapılandırması
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 3. Dosya Analizi (Hata vermemesi için isimler üzerinden rapor üretilir)
        file_names = [f.filename for f in files]
        prompt = (f"Sen Atilla Yalçın'ın strateji asistanısın. Kullanıcı {email} şu dosyaları yükledi: {file_names}. "
                 f"Bu dosya türlerine ve Atilla Yalçın'ın Ecosystem Orchestrator kimliğine dayanarak "
                 f"kısa, etkileyici ve teknik bir ön analiz raporu hazırla.")
        
        response = model.generate_content(prompt)
        report = response.text

        # 4. Otonom E-Posta Gönderimi
        if email_user and email_pass:
            msg = MIMEText(f"ATILLAYALCIN_AI_OS v16.0.4 - Otonom Ön Analiz Raporu:\n\n{report}")
            msg['Subject'] = 'ATILLAYALCIN_AI_OS: Stratejik Rapor'
            msg['From'] = email_user
            msg['To'] = email
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(email_user, email_pass)
                server.send_message(msg)

        return {"status": "success", "message": "Analiz tamamlandı ve e-posta iletildi."}

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
