import os
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import resend

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

domain_usage = {}

@app.post("/api/v1/inference")
async def run_inference(
    email: str = Form(...), 
    file: UploadFile = File(...), 
    is_audit: str = Form("false"),
    model: str = Form("N/A"),
    usage: str = Form("N/A"),
    privacy: str = Form("N/A"),
    budget: str = Form("Belirtilmedi"), # YENİ OPSİYONEL ALAN
    infra: str = Form("Belirtilmedi")   # YENİ OPSİYONEL ALAN
):
    try:
        domain = email.split('@')[1].lower()
        if domain not in domain_usage: 
            domain_usage[domain] = 0
        if domain_usage[domain] >= 3: 
            return {"status": "limit_reached"}

        resend.api_key = os.environ.get("RESEND_API_KEY")
        
        subject = f"PYTHON BENCHMARK TALEBİ: {email}" if is_audit == "true" else f"ANALİZ TALEBİ: {email}"
        
        body_content = f"""
        <div style="font-family:sans-serif; color:#222;">
            <h2 style="color:#00d2ff;">Yeni Stratejik Talep</h2>
            <p><b>Kurumsal E-posta:</b> {email}</p>
            <p><b>İşlem Türü:</b> {"Maliyet Denetimi & Python Script Talebi" if is_audit == "true" else "Genel Stratejik Analiz"}</p>
        """
        
        if is_audit == "true":
            body_content += f"""
            <div style="background:#f4f4f4; padding:15px; border-left:4px solid #00d2ff; margin-top:15px;">
                <h4 style="margin-top:0;">Adım 1: Temel Veriler</h4>
                <p><b>Kullanılan Model:</b> {model}</p>
                <p><b>Aylık Tüketim:</b> {usage}</p>
                <p><b>Gizlilik Hassasiyeti:</b> {privacy}</p>
                
                <h4 style="margin-top:15px;">Adım 2: Stratejik (Opsiyonel) Veriler</h4>
                <p><b>Mevcut Altyapı:</b> {infra}</p>
                <p><b>Aylık GPU/Cloud Bütçesi:</b> {budget}</p>
            </div>
            """
        
        attachments = []
        
        if file.filename != "sistem_otomatik_dosya_yok.txt":
            body_content += "<hr><p style='font-size:12px; color:#777;'>Kullanıcının ilettiği döküman ektedir.</p></div>"
            content = await file.read()
            attachments.append({"filename": file.filename, "content": list(content)})
        else:
            body_content += "<hr><p style='font-size:12px; color:#777;'>Bu talebe herhangi bir dosya eklenmemiştir.</p></div>"

        resend.Emails.send({
            "from": "ATILLAYALCIN_AI_OS <contact@atillayalcin.ai>",
            "to": "contact@atillayalcin.ai",
            "subject": subject,
            "html": body_content,
            "attachments": attachments
        })

        domain_usage[domain] += 1
        return {"status": "success"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
