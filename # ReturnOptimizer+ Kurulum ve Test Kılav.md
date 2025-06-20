# ReturnOptimizer+ Kurulum ve Test Kılavuzu

Bu kılavuz, projeyi sıfırdan kurup test etmeniz için gereken tüm adımları içermektedir.

---
### **Gereksinimler**
- Python 3.10+
- Git
- Postman (API testi için)
- (Opsiyonel) Telegram hesabı (bildirimleri almak için)

---
### **Adım 1: Projeyi ve Ortamı Hazırlama (Lokal Makine)**

1.  **Projeyi Klonlayın:**
    ```bash
    git clone https://github.com/senin-kullanici-adin/ReturnOptimizer.git
    cd ReturnOptimizer
    ```
2.  **Sanal Ortam Kurun ve Aktif Edin:**
    ```bash
    python -m venv venv && source venv/bin/activate
    # Windows için: python -m venv venv && .\venv\Scripts\activate
    ```
3.  **Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```
---
### **Adım 2: Servisleri Kurma (Supabase & n8n)**

1.  **Supabase Kurulumu (1 Dakika):**
    -   Supabase.io'da yeni bir proje oluşturun.
    -   Proje içerisindeki **SQL Editor**'e gidin.
    -   Bu repodaki **`supabase_setup.sql`** dosyasının içeriğini kopyalayıp SQL Editor'e yapıştırın ve **"RUN"** butonuna basın. Veritabanınız, tablolarınız ve fonksiyonlarınız hazır.
    -   **Table Editor** -> **`users`** tablosuna gidip **`+ Insert row`** ile en az bir test kullanıcısı oluşturun.

2.  **n8n Kurulumu (2 Dakika):**
    -   n8n.io/cloud üzerinden ücretsiz bir hesap oluşturun veya kendi sunucunuzda n8n'i başlatın.
    -   Yeni, boş bir iş akışı ("workflow") oluşturun.
    -   Bu repodaki **`n8n_workflow.json`** dosyasını bir metin editöründe açıp içeriğinin tamamını kopyalayın.
    -   n8n'deki boş iş akışı tuvaline bu içeriği yapıştırın (`CTRL+V` veya `CMD+V`). Tüm iş akışı sihirli bir şekilde yüklenecektir.

---
### **Adım 3: Konfigürasyon - Anahtarları Bağlama**

1.  **`.env` Dosyasını Oluşturun:**
    -   Proje ana dizininde **`.env.example`** dosyasını kopyalayıp adını **`.env`** olarak değiştirin.
    -   Aşağıdaki değerleri kendi bilgilerinizle doldurun:
        -   `OPENAI_API_KEY`: Kendi OpenAI API anahtarınız.
        -   `SUPABASE_URL` ve `SUPABASE_KEY`: Supabase projenizin Ayarlar -> API bölümündeki bilgiler.
        -   `n8n_webhook_url`: Aşağıdaki adımı tamamladıktan sonra burayı doldurun.

2.  **n8n Kimlik Bilgilerini ve URL'yi Ayarlayın:**
    -   n8n arayüzünde, az önce yüklediğiniz iş akışındaki **`Supabase`**, **`OpenAI Chat Model`** ve **`Telegram`** nodlarına tıklayın.
    -   Her birinin "Credentials" (Kimlik Bilgileri) bölümünde "Create New" diyerek kendi API anahtarlarınızı/bağlantılarınızı tanımlayın.
    -   **`Webhook`** noduna tıklayın. Ayarlarından **`POST`** metodunu seçtiğinizden emin olun. **`Production`** URL'sini kopyalayın.
    -   Kopyaladığınız bu Production URL'sini, `.env` dosyanızdaki `n8n_webhook_url` değişkeninin değeri olarak yapıştırın.
    -   n8n iş akışını sağ üstten **Active** hale getirin.

---
### **Adım 4: Sistemi Çalıştır ve Test Et!**

1.  **FastAPI Sunucusunu Başlatın:**
    ```bash
    uvicorn main:app --reload
    ```
2.  **Postman ile Test Edin:**
    -   Yeni bir `POST` isteği oluşturun: `http://127.0.0.1:8000/classify`
    -   **Body** -> **raw** -> **JSON** seçin ve aşağıdaki gibi bir veri gönderin. (`user_id`'yi kendi test kullanıcınızın ID'si ile değiştirmeyi unutmayın):
      ```json
      {
          "user_id": "supabase-den-kopyaladigin-gercek-id",
          "product_id": "SUPER-CAMERA-X1",
          "message": "Bu kamera ikinci kez bozuk geliyor, lenste yine bir çizik var. Bu seride kesinlikle bir problem var."
      }
      ```
3.  **Sonuçları İzleyin:** FastAPI terminalindeki logları, Telegram'a düşen bildirimi ve Supabase `flags` tablosundaki yeni kaydı kontrol edin.