
from typing import Dict, Any
from livekit.agents import function_tool
from supabase import Client
import os
from dotenv import load_dotenv
from supabase import create_client

# tools
# agent.py

load_dotenv()

# Cliente Supabase global
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


@function_tool
async def register_candidate(
    candidate_name: str,
    candidate_email: str,
) -> Dict[str, Any]:
    """
    Registra un nuevo candidato al inicio de la entrevista.
    
    Args:
        candidate_name: Nombre completo del candidato
        candidate_email: Correo electrónico del candidato
    
    Returns:
        Dict con el resultado de la operación incluyendo candidate_id
    """
    try:
        # Datos del candidato
        candidate_data = {
            "name": candidate_name,
            "email": candidate_email,
            "status": "pending",
            "approved": False
        }
        
        # Insertar en Supabase
        response = supabase.table("candidates").insert(candidate_data).execute()
        
        if response.data and len(response.data) > 0:
            candidate = response.data[0]
            return {
                "success": True,
                "candidate_id": candidate["id"],
                "name": candidate["name"],
                "email": candidate["email"],
                "status": candidate["status"],
                "message": f"Candidato {candidate_name} registrado exitosamente con ID: {candidate['id']}"
            }
        else:
            return {
                "success": False,
                "error": "No se pudo crear el candidato",
                "message": "Error al insertar en la base de datos"
            }
            
    except Exception as e:
        error_message = str(e)
        
        # Manejo específico de errores comunes
        if "duplicate key value violates unique constraint" in error_message:
            return {
                "success": False,
                "error": "duplicate_email",
                "message": f"El email {candidate_email} ya está registrado en el sistema"
            }
        
        return {
            "success": False,
            "error": error_message,
            "message": f"Error al registrar candidato: {error_message}"
        }
