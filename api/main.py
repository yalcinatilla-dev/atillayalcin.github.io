from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
import os

app = FastAPI()

# MASTER CORS - Tüm alt alan adlarına izin ver
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.atillayalcin.ai", "https://atillayalcin.ai", "http://atillayalcin.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/inference")
async def run_inference(email: str = Form(...), files: list[UploadFile] = File(...)):
    try:
        # API ve Email Değişkenleri Kontrolü
        api_key = os.environ.get("GEMINI_API_KEY")
        email_user = os.environ.get("EMAIL_ADDRESS")
        email_pass = os.environ.get("EMAIL_PASSWORD")

        if not api_key:
            return JSONResponse(status_code=500, content={"error": "Bilişsel Çekirdek (API Key) Bulunamadı."})

        # Gemini Altyapısını Hazırla
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash') # Hızlı analiz için Flash model
        
        # Dosya Analizi (İlk 1MB kısmını işleme alır)
        content = f"Kullanıcı: {email}\nAnaliz Edilecek Veri:\n"
        for file in files:
            data = await file.read()
            content += f"\n--- Dosya: {file.filename} ---\n"
            content += data.decode('utf-8', errors='ignore')[:50000] # Veri kırpma (Hız için)

        # Gemini Otonom Yanıt Üretimi
        prompt = f"Sen ATILLAYALCIN_AI_OS v16.0.4 Strateji Ajanısın. Şu veriyi analiz et: {content}"
        response = model.generate_content(prompt)
        report = response.text

        # E-Posta Gönderimi
        if email_user and email_pass:
            msg = MIMEText(f"ATILLAYALCIN_AI_OS Stratejik Analiz Raporu:\n\n{report}")
            msg['Subject'] = 'ATILLAYALCIN_AI_OS: Otonom Analiz Sonucu'
            msg['From'] = email_user
            msg['To'] = email
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(email_user, email_pass)
                server.send_message(msg)

        return {"status": "success", "message": "Analiz tamamlandı ve iletildi."}

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
