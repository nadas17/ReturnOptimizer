-- Supabase'de match_returns fonksiyonu oluşturmak için
-- Bu SQL kodunu Supabase Dashboard > SQL Editor'da çalıştırın

-- 1. pgvector extension'ı etkinleştirin (eğer etkin değilse)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. returns tablosunda embedding sütunu varsa vector tipine çevirin
-- ALTER TABLE returns ALTER COLUMN embedding TYPE vector(1536);

-- 3. returns tablosunun yapısını kontrol etmek için basit sorgu
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'returns';

-- 4. match_returns fonksiyonunu oluşturun (dinamik tip çözümü ile)
DROP FUNCTION IF EXISTS match_returns(vector, double precision, integer);
DROP FUNCTION IF EXISTS match_returns(vector(1536), double precision, integer);
CREATE OR REPLACE FUNCTION match_returns(
  p_query_embedding vector(1536),
  p_match_threshold float DEFAULT 0.78,
  p_match_count int DEFAULT 10
)
RETURNS TABLE (
  id text,
  user_id text,
  product_id text,
  message text,
  category text,
  sentiment float,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    returns.id::text,
    returns.user_id::text,
    returns.product_id::text,
    returns.message::text,
    array_to_string(returns.category, ',') AS category,  -- text[] -> text dönüşümü
    returns.sentiment::float,
    (returns.embedding <#> p_query_embedding) * -1 AS similarity
  FROM returns
  WHERE returns.embedding <#> p_query_embedding < -p_match_threshold
  ORDER BY returns.embedding <#> p_query_embedding
  LIMIT p_match_count;
END;
$$;

-- 4. RLS (Row Level Security) politikası oluşturun (isteğe bağlı)
-- ALTER TABLE returns ENABLE ROW LEVEL SECURITY;

-- 5. Genel erişim politikası (test için)
-- CREATE POLICY "Enable read access for all users" ON returns FOR SELECT USING (true);
-- CREATE POLICY "Enable insert access for all users" ON returns FOR INSERT WITH CHECK (true);
