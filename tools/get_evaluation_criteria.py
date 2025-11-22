# tools/get_evaluation_criteria.py
from typing import Dict, Any, List
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

print("Supabase client initialized for get_evaluation_criteria tool.")


@function_tool
async def get_evaluation_criteria() -> Dict[str, Any]:
    """
    Obtiene las preguntas de evaluación desde la base de datos.
    
    Returns:
        Dict con las preguntas organizadas por área (topic)
    """
    try:
        # Obtener todas las preguntas ordenadas
        response = supabase.table("evaluation_criteria").select("*").order("difficulty").execute()
        
        if not response.data:
            return {
                "success": False,
                "error": "no_questions_found",
                "message": "No se encontraron preguntas en la base de datos"
            }
        
        # Organizar preguntas por área (topic)
        questions_by_area = {
            "React": [],
            "Next.js": [],
            "TanStack": []
        }
        
        for question in response.data:
            area = question.get("topic", "").lower()
            
            if area in questions_by_area:
                questions_by_area[area].append({
                    "id": question.get("id"),
                    "question": question.get("question"),
                    "order": question.get("difficulty"),
                })
        
        # Contar total de preguntas
        total_questions = sum(len(questions) for questions in questions_by_area.values())
        
        return {
            "success": True,
            "questions": questions_by_area,
            "total_questions": total_questions,
            "message": f"Se cargaron {total_questions} preguntas exitosamente"
        }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error al obtener preguntas: {str(e)}"
        }