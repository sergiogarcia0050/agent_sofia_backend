# tools/register_candidate.py
from typing import Dict, Any
from livekit.agents import function_tool
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Cargar archivo .env
load_dotenv()

# Leer variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")


# Crear cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

print("Supabase client initialized for register_candidate tool.")

@function_tool
async def get_evaluation_criteria(
) -> Dict[str, Any]:
    """
    OBTIENE INFORMACIÓN DE EVALUACIÓN (obligatorio antes de evaluar):
   - LLAMA: get_evaluation_criteria()
   - Esta tool te devolverá en UN SOLO LLAMADO toda la información que necesitas:
     * Las preguntas específicas organizadas por área (HTML, CSS, JavaScript, Tools)
     * Los criterios de evaluación que debes aplicar
     * Los pesos de cada área
     * Los umbrales de aprobación (thresholds) para cada área
     * La escala de puntajes a usar (0-100 con sus descripciones)
     * Las respuestas esperadas o guías de evaluación
     * Cualquier instrucción adicional sobre cómo evaluar
   - Usa EXACTAMENTE estas preguntas, criterios y escala de puntajes para toda la entrevista
   - NO inventes preguntas, criterios ni escalas propias

    """