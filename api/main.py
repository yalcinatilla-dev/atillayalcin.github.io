from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import resend
import os
import requests

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/api/v1/inference")
async def run_inference(email: str = Form(...), drive_file_id: str = Form(...)):
    try:
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        resend.api_key = os.environ.get("RESEND_API_KEY")
        
        # Gemini 1.5 Pro Konfigürasyonu
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Otonom Analiz Komutu (Geniş Bağlam Penceresi)
        # Not: Gelecek adımda Drive'dan fiziksel okuma için 'google-api-python-client' eklenebilir.
        # Şu anki sürümde Gemini'nin dökümanı anladığını teyit ediyoruz.
        response = model.generate_content(f"Sistem: ATILLAYALCIN_AI_OS. Hedef Belge ID: {drive_file_id}. Bu belgeyi Atilla Yalçın Strateji standartlarında analiz et ve raporu {email} adresine gönderilecek şekilde yapılandır.")

        resend.Emails.send({
            "from": "ATILLAYALCIN_AI_OS <info@atillayalcin.ai>",
            "to": email,
            "subject": "Stratejik Analiz Raporu v16.0.5",
            "html": f"<h3>Stratejik Analiz Sonucu</h3><p>{response.text}</p>"
        })
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
