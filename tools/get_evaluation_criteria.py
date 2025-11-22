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
    Obtiene las preguntas de evaluación activas desde la base de datos.
    
    Returns:
        Dict con las preguntas organizadas por área (topic) y ordenadas por dificultad
    """
    try:
        # Obtener solo preguntas activas, ordenadas por dificultad
        response = supabase.table("evaluation_criteria") \
            .select("*") \
            .eq("is_active", True) \
            .order("difficulty", desc=False) \
            .execute()
        
        if not response.data:
            return {
                "success": False,
                "error": "no_questions_found",
                "message": "No se encontraron preguntas activas en la base de datos"
            }
        
        # Organizar preguntas por área (topic)
        questions_by_topic = {}
        
        for question in response.data:
            topic = question.get("topic", "Unknown")
            
            # Crear la lista para el topic si no existe
            if topic not in questions_by_topic:
                questions_by_topic[topic] = []
            
            questions_by_topic[topic].append({
                "id": question.get("id"),
                "question": question.get("question"),
                "difficulty": question.get("difficulty"),
                "topic": topic
            })
        
        # Contar total de preguntas
        total_questions = len(response.data)
        
        # Crear resumen por topic
        topics_summary = {topic: len(questions) for topic, questions in questions_by_topic.items()}
        
        return {
            "success": True,
            "questions": questions_by_topic,
            "total_questions": total_questions,
            "topics_summary": topics_summary,
            "message": f"Se cargaron {total_questions} preguntas activas exitosamente. Topics: {', '.join([f'{t} ({c})' for t, c in topics_summary.items()])}"
        }
            
    except Exception as e:
        print(f"❌ Error en get_evaluation_criteria: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Error al obtener preguntas: {str(e)}"
        }