# test_supabase.py (Düzeltilmiş ve Basitleştirilmiş Versiyon)

import os
import random
import json
# 'dotenv' kütüphanesini import edelim
try:
    from dotenv import load_dotenv
except ImportError:
    print("!!! HATA: 'dotenv' kütüphanesi bulunamadı.")
    print("Lütfen terminale 'pip install python-dotenv' yazarak kurun.")
    exit()

# 'supabase' kütüphanesini import edelim
try:
    from supabase import create_client, Client
except ImportError:
    print("!!! HATA: 'supabase' kütüphanesi bulunamadı.")
    print("Lütfen terminale 'pip install supabase' yazarak kurun.")
    exit()

# --- 1. AYARLARI YÜKLEME ---
print("Test başlatıldı...")
load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("!!! HATA: .env dosyanızda SUPABASE_URL veya SUPABASE_KEY değişkenleri bulunamadı veya boş.")
    print("Lütfen .env dosyanızı kontrol edin.")
    exit()

print(">>> Ayarlar başarıyla yüklendi.")


# --- 2. SUPABASE BAĞLANTISI ---
try:
    print("Supabase istemcisi oluşturuluyor...")
    supabase: Client = create_client(supabase_url, supabase_key)
    print(">>> Supabase istemcisi başarıyla oluşturuldu.")
except Exception as e:
    print(f"!!! İstemci oluşturulurken bir hata oluştu: {e}")
    exit()

# --- 3. TEST PARAMETRELERİNİ HAZIRLAMA ---
# Gerçek bir embedding vektörüne benzer, 1536 elemanlı rastgele bir liste oluşturalım.
test_embedding = [random.uniform(-0.1, 0.1) for _ in range(1536)]
# Eşleşme eşiği ve sayacı için değerler tanımlayalım
match_threshold = 0.8
match_count = 5
# test_supabase.py dosyasındaki bu bölümü güncelle

test_params = {
    'p_query_embedding': test_embedding,   # <-- 'p_' eklendi
    'p_match_threshold': match_threshold, # <-- 'p_' eklendi
    'p_match_count': match_count        # <-- 'p_' eklendi
}
print("\n'match_returns' fonksiyonu test parametreleriyle çağrılacak...")


# --- 4. FONKSİYONU ÇAĞIRMA (RPC) ---
try:
    # Fonksiyonu çağıralım
    response = supabase.rpc('match_returns', test_params).execute()

    print("\n-------------------------------------------")
    print(">>> FONKSİYON BAŞARIYLA ÇALIŞTIRILDI!")
    print(">>> Supabase'den gelen yanıt:")
    print(json.dumps(response.data, indent=2))
    print("-------------------------------------------")

except Exception as e:
    print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!! HATA: Fonksiyon çağrılırken bir sorun oluştu!")
    print(f">>> Hatanın Türü: {type(e).__name__}")
    print(">>> Hatanın Tam Metni:")
    print(e)
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")