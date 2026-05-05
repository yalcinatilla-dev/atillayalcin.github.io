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

# Domain kullanım sayacı (Vercel her uyandığında sıfırlanır, düşük yoğunluk için uygundur)
domain_usage = {}

@app.post("/api/v1/inference")
async def run_inference(email: str = Form(...), file: UploadFile = File(...)):
    try:
        domain = email.split('@')[1].lower()
        
        # 1. KOTA KONTROLÜ (Domain başına 3 dosya)
        if domain not in domain_usage:
            domain_usage[domain] = 0
            
        if domain_usage[domain] >= 3:
            return {"status": "limit_reached"}

        # 2. DOSYA VERİSİNİ OKUMA
        content = await file.read()
        
        # 3. DOĞRUDAN GMAIL HESABINIZA GÖNDERİM
        resend.api_key = os.environ.get("RESEND_API_KEY")
        
        resend.Emails.send({
            "from": "ATILLAYALCIN_AI_OS <info@atillayalcin.ai>",
            "to": "yalcin.atilla@gmail.com", # Burayı doğrudan Gmail adresiniz yaptık
            "subject": f"STRATEJİK ANALİZ TALEBİ: {email}",
            "html": f"""
            <h3>Yeni Analiz Dosyası Ulaştı</h3>
            <p><b>Gönderen:</b> {email}</p>
            <p><b>Şirket:</b> {domain}</p>
            <p><b>Kota Durumu:</b> {domain_usage[domain] + 1} / 3</p>
            <hr>
            <p>Bu dosya manuel analiz için gönderilmiştir. Analiz sonucunu doğrudan kullanıcıya iletebilirsiniz.</p>
            """,
            "attachments": [
                {
                    "filename": file.filename,
                    "content": list(content) # Dosyayı liste formatında eke ekler
                }
            ]
        })

        # İşlem başarılıysa sayacı artır
        domain_usage[domain] += 1

        return {"status": "success"}

    except Exception as e:
        return {"status": "error", "message": f"İletim Hatası: {str(e)}"}
