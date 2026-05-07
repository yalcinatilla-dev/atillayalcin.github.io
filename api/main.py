import os, json, io
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import resend

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

domain_usage = {}

@app.post("/api/v1/inference")
async def run_inference(
    email: str = Form(...), 
    file: UploadFile = File(...),
    is_audit: str = Form("false"),
    model: str = Form("N/A"),
    usage: str = Form("N/A"),
    privacy: str = Form("N/A")
):
    try:
        domain = email.split('@')[1].lower()
        if domain not in domain_usage: domain_usage[domain] = 0
        if domain_usage[domain] >= 3: return {"status": "limit_reached"}

        content = await file.read()
        resend.api_key = os.environ.get("RESEND_API_KEY")
        
        # Dinamik Konu ve İçerik Belirleme
        subject = f"GPU VERİMLİLİK DENETİMİ: {email}" if is_audit == "true" else f"STRATEJİK ANALİZ TALEBİ: {email}"
        
        audit_details = f"""
        <hr>
        <h4>GPU Denetim Detayları:</h4>
        <p><b>Mevcut Model:</b> {model}</p>
        <p><b>Tahmini Tüketim:</b> {usage}</p>
        <p><b>Gizlilik Hassasiyeti:</b> {privacy}</p>
        """ if is_audit == "true" else ""

        resend.Emails.send({
            "from": "ATILLAYALCIN_AI_OS <info@atillayalcin.ai>",
            "to": "caio@atillayalcin.ai",
            "subject": subject,
            "html": f"""
            <h3>Yeni Talep Alındı</h3>
            <p><b>Gönderen:</b> {email}</p>
            {audit_details}
            <hr>
            <p>Yüklenen dosya ektedir. Analizi manuel yaparak kullanıcıya dönüş yapabilirsiniz.</p>
            """,
            "attachments": [{"filename": file.filename, "content": list(content)}]
        })

        domain_usage[domain] += 1
        return {"status": "success"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
