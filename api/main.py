from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import resend
import os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/api/v1/inference")
async def run_inference(email: str = Form(...), files: list[UploadFile] = File(...)):
    try:
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        resend.api_key = os.environ.get("RESEND_API_KEY")
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        file_names = [f.filename for f in files]
        prompt = f"Analiz raporu hazırla. Dosyalar: {file_names}"
        response = model.generate_content(prompt)

        # Profesyonel E-Posta Gönderimi (Resend)
        resend.Emails.send({
            "from": "ATILLAYALCIN_AI_OS <onboarding@resend.dev>", # Domain doğrulanınca info@atillayalcin.ai yapılacak
            "to": email,
            "subject": "Stratejik Analiz Raporu v16.0.4",
            "text": response.text
        })

        return {"status": "success", "message": "Analiz Resend üzerinden iletildi."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
