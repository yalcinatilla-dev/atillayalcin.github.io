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
    file: UploadFile = File(None), # İsteğe bağlı (None)
    is_audit: str = Form("false"),
    model: str = Form("N/A"),
    usage: str = Form("N/A"),
    privacy: str = Form("N/A")
):
    try:
        resend.api_key = os.environ.get("RESEND_API_KEY")
        
        # Dinamik Konu Başlığı
        subject = f"GPU VERİMLİLİK DENETİMİ: {email}" if is_audit == "true" else f"STRATEJİK ANALİZ TALEBİ: {email}"
        
        # HTML İçeriği (Anket verilerini buraya gömüyoruz)
        body_content = f"""
        <div style="font-family:sans-serif; color:#333;">
            <h2 style="color:#00d2ff;">Yeni Talep Bildirimi</h2>
            <p><b>Gönderen:</b> {email}</p>
            <p><b>İşlem Türü:</b> {"GPU Verimlilik Denetimi" if is_audit == "true" else "Genel Stratejik Analiz"}</p>
        """
        
        if is_audit == "true":
            body_content += f"""
            <div style="background:#f9f9f9; padding:15px; border-radius:8px; border:1px solid #eee;">
                <h4 style="margin-top:0;">Stratejik Anket Cevapları:</h4>
                <p><b>Mevcut Model:</b> {model}</p>
                <p><b>Aylık Tüketim:</b> {usage}</p>
                <p><b>Gizlilik Hassasiyeti:</b> {privacy}</p>
            </div>
            """
        
        body_content += "<hr><p style='font-size:12px; color:#999;'>Döküman eklendiyse bu e-postanın ekindedir.</p></div>"

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
