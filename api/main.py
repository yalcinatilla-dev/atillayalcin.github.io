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
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Gemini doğrudan Drive ID'si üzerinden (veya döküman metni üzerinden) analiz yapar
        response = model.generate_content(f"Sistem: ATILLAYALCIN_AI_OS. Analiz edilecek dosya ID: {drive_file_id}. Lütfen stratejik bir rapor hazırla.")

        resend.api_key = os.environ.get("RESEND_API_KEY")
        resend.Emails.send({
            "from": "ATILLAYALCIN_AI_OS <info@atillayalcin.ai>",
            "to": email,
            "subject": "Stratejik Analiz Raporu v16.0.5",
            "text": response.text
        })
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
