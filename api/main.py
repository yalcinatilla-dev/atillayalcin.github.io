from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
import os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/api/v1/inference")
async def run_inference(email: str = Form(...), files: list[UploadFile] = File(...)):
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        email_user = os.environ.get("EMAIL_ADDRESS")
        email_pass = os.environ.get("EMAIL_PASSWORD")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # PDF Dosyaları için Basitleştirilmiş Analiz (Çökmeyi Önler)
        file_names = [f.filename for f in files]
        prompt = f"Kullanıcı {email} şu dosyaları yükledi: {file_names}. Lütfen bu dosyalar üzerinden Atilla Yalçın'ın stratejik altyapı hizmetlerini özetleyen bir karşılama raporu hazırla."
        
        response = model.generate_content(prompt)
        report = response.text

        # E-Posta Gönderimi
        msg = MIMEText(f"ATILLAYALCIN_AI_OS v16.0.4 Analiz Raporu:\n\n{report}")
        msg['Subject'] = 'ATILLAYALCIN_AI_OS: Otonom Analiz Raporu'
        msg['From'] = email_user
        msg['To'] = email
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_user, email_pass)
            server.send_message(msg)

        return {"status": "success", "message": "Analiz tamamlandı."}

    except Exception as e:
        print(f"HATA DETAYI: {str(e)}") # Vercel Logs'a yazdırır
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
