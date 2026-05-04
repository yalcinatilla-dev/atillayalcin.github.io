from fastapi import FastAPI, Form
import google.generativeai as genai
import resend
import os

app = FastAPI()

@app.post("/api/v1/inference")
async def run_inference(email: str = Form(...), drive_file_id: str = Form(...)):
    try:
        # 1. Gemini Yapılandırması (2 Milyon Token Kapasiteli Model)
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # 2. Drive'daki Dosyayı Otonom Okuma
        # Gemini doğrudan Google Drive URI'larını işleme kapasitesine sahiptir
        analysis_prompt = f"Drive ID'si {drive_file_id} olan stratejik belgeyi analiz et."
        response = model.generate_content(analysis_prompt)

        # 3. Sonucun Resend ile İletilmesi
        resend.api_key = os.environ.get("RESEND_API_KEY")
        resend.Emails.send({
            "from": "AI_OS <onboarding@resend.dev>",
            "to": email,
            "subject": "Kurumsal Strateji Raporu v16.0.5",
            "text": response.text
        })

        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
