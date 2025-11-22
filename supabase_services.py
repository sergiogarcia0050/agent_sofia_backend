from fastapi import FastAPI
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Cargar archivo .env
load_dotenv()

# Leer variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

app = FastAPI()

# Crear cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

@app.get("/")
def read_root():
    return {"message": "FastAPI + Supabase OK"}

@app.get("/users")
def get_users():
    """Ejemplo: obtener datos de la tabla users'"""
    data = supabase.table("users").select("*").execute()
    return data.data
