# test_supabase.py
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

print(f"URL: {SUPABASE_URL}")
print(f"Key: {SUPABASE_ANON_KEY[:20]}...")

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Listar todas las tablas disponibles
try:
    # Intentar obtener datos
    response = supabase.table("tech").select("*").limit(1).execute()
    print(f"✅ Conexión exitosa. Datos: {response.data}")
except Exception as e:
    print(f"❌ Error: {e}")