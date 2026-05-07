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
    file: UploadFile = File(None), # Kritik: Artık dosya gelmese de hata vermez
    is_audit: str = Form("false"),
    model: str = Form("N/A"),
    usage: str = Form("N/A"),
    privacy: str = Form("N/A")
):
    try:
        resend.api_key = os.environ.get("RESEND_API_KEY")
        
        # Konu Başlığı Belirleme
        subject = f"GPU VERİMLİLİK DENETİMİ: {email}" if is_audit == "true" else f"STRATEJİK ANALİZ TALEBİ: {email}"
        
        # Mail Gövdesini Oluşturma (Anket Verileri Dahil)
        body_content = f"""
        <h3>Atilla Yalçın - Yeni Talep Bildirimi</h3>
        <p><b>Gönderen:</b> {email}</p>
        <p><b>İşlem Türü:</b> {"GPU Verimlilik Denetimi" if is_audit == "true" else "Genel Stratejik Analiz"}</p>
        """
        
        if is_audit == "true":
            body_content += f"""
            <hr>
            <h4>Stratejik Anket Verileri:</h4>
            <ul>
                <li><b>Mevcut Model:</b> {model}</li>
                <li><b>Aylık Tüketim:</b> {usage}</li>
                <li><b>Gizlilik Hassasiyeti:</b> {privacy}</li>
            </ul>
            """
        
        body_content += "<hr><p>Yüklenen döküman varsa e-posta ekindedir.</p>"

        attachments = []
        if file:
            content = await file.read()
            attachments.append({"filename": file.filename, "content": list(content)})

        resend.Emails.send({
            "from": "ATILLAYALCIN_AI_OS <contact@atillayalcin.ai>",
            "to": "contact@atillayalcin.ai",
            "subject": subject,
            "html": body_content,
            "attachments": attachments
        })

        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
