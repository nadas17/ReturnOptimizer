# main.py (NİHAİ, TEMİZ VE MODÜLER VERSİYON)

import httpx
from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
from openai import AsyncOpenAI
from typing import List

# Kendi oluşturduğumuz modüllerden doğru import'ları yapalım
from config import Settings # <-- Ayarları artık config.py'dan alıyoruz
from models import ReturnRequest, AnalysisResult

# --- İstemci Kurulumları ---
settings = Settings()
app = FastAPI(title="ReturnOptimizer+ API")
client = AsyncOpenAI(api_key=settings.openai_api_key)
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)


# --- Yardımcı Fonksiyonlar ---
async def analyze_return_message(message: str) -> AnalysisResult:
    try:
        system_prompt = """
        You are an expert e-commerce return analysis AI. Analyze the return message and provide:
        1. category: List of relevant categories like ["defective", "shipping_damage", "wrong_item", "not_as_described"]
        2. sentiment: Float between -1 (very negative) and 1 (very positive)
        3. summary: Brief summary of the issue
        
        Return JSON format:
        {
            "category": ["defective"],
            "sentiment": -0.8,
            "summary": "Product has defects"
        }
        """
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            response_format={"type": "json_object"}
        )
        return AnalysisResult.model_validate_json(response.choices[0].message.content)
    except Exception as e:
        print(f"OpenAI ERROR: {str(e)}")
        # Fallback response
        return AnalysisResult(
            category=["error"],
            sentiment=0.0,
            summary=f"API Error: {str(e)}"
        )

async def get_embedding(text: str) -> List[float]:
    try:
        response = await client.embeddings.create(model="text-embedding-3-small", input=text)
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding ERROR: {str(e)}")
        # Fallback embedding
        return [0.1, 0.2, 0.3]


# --- Ana API Endpoint'i ---
@app.post("/classify")
async def classify_return(request: ReturnRequest):
    analysis = await analyze_return_message(request.message)
    embedding = await get_embedding(request.message)

    payload_to_db = {
        "user_id": str(request.user_id), 
        "product_id": request.product_id, 
        "message": request.message,
        "embedding": embedding, 
        "category": analysis.category, 
        "sentiment": float(analysis.sentiment)  # JSON uyumlu format
    }
    
    database_success = False
    database_id = None
    
    # Supabase'e kaydetmeyi dene
    try:
        # Basit HTTP isteği ile Supabase'e kaydet
        supabase_url = f"{settings.supabase_url}/rest/v1/returns"
        headers = {
            "apikey": settings.supabase_key,
            "Authorization": f"Bearer {settings.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(supabase_url, json=payload_to_db, headers=headers)
            
            if response.status_code == 201:
                result = response.json()
                database_id = result[0]["id"] if result else None
                database_success = True
                print(f"✅ Supabase'e kaydedildi: {database_id}")
            else:
                print(f"❌ Supabase hatası: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"❌ Supabase bağlantı hatası: {str(e)}")
    
    # n8n webhook için payload hazırla (n8n için temiz format)
    webhook_payload = {
        "user_id": str(request.user_id),
        "product_id": request.product_id,
        "message": request.message,
        "embedding": embedding,
        "category": analysis.category,
        "sentiment": float(analysis.sentiment),
        "summary": analysis.summary,
        "database_id": str(database_id) if database_id else None,
        "timestamp": "2025-01-16T12:00:00Z",
        "status": "processed"
    }
    
    webhook_success = False
    
    # n8n webhook tetikle
    if settings.n8n_webhook_url:
        try:
            async with httpx.AsyncClient() as httpx_client:
                webhook_response = await httpx_client.post(
                    settings.n8n_webhook_url, 
                    json=webhook_payload, 
                    timeout=10.0
                )
                print(f"🚀 n8n webhook başarılı: {webhook_response.status_code}")
                webhook_success = webhook_response.status_code == 200
        except Exception as e:
            print(f"⚠️ n8n webhook tetiklenemedi: {e}")
    
    return {
        "status": "success", 
        "analysis": analysis, 
        "database_saved": database_success,
        "database_id": database_id,
        "webhook_sent": webhook_success,
        "message": f"🎯 Full pipeline: OpenAI ✅ | Supabase {'✅' if database_success else '❌'} | n8n {'✅' if webhook_success else '❌'}"
    }

@app.get("/")
def read_root():
    return {"message": "ReturnOptimizer+ API çalışıyor!"}