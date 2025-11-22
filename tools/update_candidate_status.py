# tools/candidate_tools.py
from typing import Dict, Any
from livekit.agents import function_tool
from supabase import Client
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Cliente Supabase global
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


@function_tool
async def update_candidate_status(
    candidate_id: str,
    approved: bool,
    final_notes: str = None,
) -> Dict[str, Any]:
    """
    Actualiza el estado de aprobación del candidato después de la entrevista.
    
    Args:
        candidate_id: UUID del candidato
        approved: True si el candidato aprobó la entrevista
        final_notes: Notas finales opcionales sobre la decisión
    
    Returns:
        Dict con el resultado de la actualización
    """
    try:
        # Determinar el nuevo status basado en aprobación
        new_status = "approved" if approved else "rejected"
        
        # Datos a actualizar
        update_data = {
            "approved": approved,
            "status": new_status,
        }
        
        if final_notes:
            update_data["overall_notes"] = final_notes
        
        # Actualizar en Supabase
        response = supabase.table("candidates").update(update_data).eq("id", candidate_id).execute()
        
        if response.data and len(response.data) > 0:
            candidate = response.data[0]
            return {
                "success": True,
                "candidate_id": candidate["id"],
                "approved": candidate["approved"],
                "status": candidate["status"],
                "message": f"Candidato actualizado: {'APROBADO' if approved else 'NO APROBADO'}"
            }
        else:
            return {
                "success": False,
                "error": "candidate_not_found",
                "message": f"No se encontró el candidato con ID: {candidate_id}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error al actualizar candidato: {str(e)}"
        }