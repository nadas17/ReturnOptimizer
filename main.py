# main.py dosyası (Nihai Versiyon)

import httpx
from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
from openai import AsyncOpenAI
from typing import List

# Kendi oluşturduğumuz modüllerden doğru import'ları yapalım
from config import settings
from models import ReturnRequest, AnalysisResult

# --- İstemci Kurulumları ---
app = FastAPI(title="ReturnOptimizer+ API")
client = AsyncOpenAI(api_key=settings.openai_api_key)
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

# --- Yardımcı Fonksiyonlar ---
async def analyze_return_message(message: str) -> AnalysisResult:
    system_prompt = """
    You are an expert e-commerce return analysis AI. Your task is to analyze the customer's return message and provide a structured JSON output.
    The JSON must contain these keys:
    - 'category': A list of strings from ["ürün hasarı", "yanlış ürün", "ürün kalitesi", "beden uyuşmazlığı", "renk uyuşmazlığı", "geç teslimat", "diğer"].
    - 'sentiment': A float between -1.0 (very negative) and 1.0 (very positive).
    - 'summary': A one-sentence Turkish summary of the problem.
    You must reply with only the JSON object, nothing else.
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

async def get_embedding(text: str) -> List[float]:
    response = await client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding

# --- Ana API Endpoint'i ---
@app.post("/classify")
async def classify_return(request: ReturnRequest):
    analysis = await analyze_return_message(request.message)
    embedding = await get_embedding(request.message)

    payload_to_db = {
        "user_id": str(request.user_id), "product_id": request.product_id, "message": request.message,
        "embedding": embedding, "category": analysis.category, "sentiment": analysis.sentiment
    }
    
    db_response = supabase.table('returns').insert(payload_to_db).execute()

    if not db_response.data:
        raise HTTPException(status_code=500, detail="Veri Supabase'e kaydedilemedi.")
    
    inserted_return = db_response.data[0]
    
    n8n_payload_to_send = {
        **payload_to_db,
        "id": inserted_return['id'],
        "created_at": inserted_return['created_at']
    }
    
    if settings.n8n_webhook_url:
        try:
            async with httpx.AsyncClient() as httpx_client:
                await httpx_client.post(settings.n8n_webhook_url, json=n8n_payload_to_send, timeout=10.0)
        except Exception as e:
            print(f"UYARI: n8n webhook tetiklenemedi: {e}")

    return {"status": "success", "analysis": analysis}

@app.get("/")
def read_root():
    return {"message": "ReturnOptimizer+ API çalışıyor!"}