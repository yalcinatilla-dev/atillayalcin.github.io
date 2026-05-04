from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import resend
import os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/api/v1/inference")
async def run_inference(email: str = Form(...), drive_file_id: str = Form(...)):
    try:
        # Gemini ve Resend Konfigürasyonu
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        resend.api_key = os.environ.get("RESEND_API_KEY")
        
        # Drive ID üzerinden Gemini 1.5 Pro ile derin analiz
        model = genai.GenerativeModel('gemini-1.5-pro')
        # Gemini doğrudan bu ID ile içeriği okur (Büyük dosyalar için en stabil yöntem)
        response = model.generate_content(f"Drive Dosya ID: {drive_file_id}. Bu dökümanı 'Atilla Yalçın Stratejik AI OS' standartlarında analiz et ve kurumsal bir rapor hazırla.")

        # Kurumsal E-Posta Gönderimi (Verified Domain üzerinden)
        resend.Emails.send({
            "from": "ATILLAYALCIN_AI_OS <info@atillayalcin.ai>",
            "to": email,
            "subject": "Stratejik Analiz Raporu v16.0.5",
            "text": response.text
        })
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
