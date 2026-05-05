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

# Domain kullanım sayacı (Serverless Memory)
domain_usage = {}

@app.post("/api/v1/inference")
async def run_inference(email: str = Form(...), file: UploadFile = File(...)):
    try:
        domain = email.split('@')[1].lower()
        
        # 1. KOTA KONTROLÜ (Maksimum 3)
        if domain not in domain_usage:
            domain_usage[domain] = 0
            
        if domain_usage[domain] >= 3:
            return {"status": "limit_reached"}

        # 2. DOSYAYI OKUMA
        content = await file.read()
        
        # 3. DOSYAYI SİZE E-POSTA EKİ OLARAK GÖNDERME
        resend.api_key = os.environ.get("RESEND_API_KEY")
        
        resend.Emails.send({
            "from": "ATILLAYALCIN_AI_OS <info@atillayalcin.ai>",
            "to": "caio@atillayalcin.ai", # Dosya doğrudan sizin bu adresinize düşecek
            "subject": f"YENİ ANALİZ TALEBİ: {email}",
            "html": f"""
            <h3>Manuel Analiz Talebi</h3>
            <p><b>Gönderen Kullanıcı:</b> {email}</p>
            <p><b>Şirket Domaini:</b> {domain}</p>
            <p><b>Kullanılan Ücretsiz Hak:</b> {domain_usage[domain] + 1} / 3</p>
            <hr>
            <p>Kullanıcının gönderdiği şartname/log dosyası bu e-postanın ekindedir. Analizi yaptıktan sonra doğrudan bu mail adresine dönüş yapabilirsiniz.</p>
            """,
            "attachments": [
                {"filename": file.filename, "content": list(content)} # Dosya eke eklendi
            ]
        })

        # İşlem başarılıysa sayacı artır
        domain_usage[domain] += 1

        return {"status": "success"}

    except Exception as e:
        return {"status": "error", "message": f"Sistem İletim Hatası: {str(e)}"}
