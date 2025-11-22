import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

# Cargar variables de entorno
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

def create_topic_index(collection_name: str = "sofia_ai"):
    """
    Crea un índice para el campo 'topic' en una colección existente de Qdrant.
    """
    print(f"\n[INFO] Conectando a Qdrant...\n")
    
    qdrant = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        port=443,
        timeout=10.0
    )
    
    try:
        # Verificar que la colección existe
        collection_info = qdrant.get_collection(collection_name)
        print(f"[INFO] Colección encontrada: {collection_name}")
        print(f"[INFO] Puntos en la colección: {collection_info.points_count}\n")
        
        # Crear el índice para el campo 'topic'
        print(f"[INFO] Creando índice para el campo 'topic'...\n")
        qdrant.create_payload_index(
            collection_name=collection_name,
            field_name="topic",
            field_schema=qmodels.PayloadSchemaType.KEYWORD
        )
        
        print(f"[SUCCESS] ✓ Índice creado exitosamente para el campo 'topic'\n")
        
    except Exception as e:
        print(f"[ERROR] Error al crear el índice: {e}\n")
        return False
    
    return True


if __name__ == "__main__":
    import sys
    
    # Permitir pasar el nombre de la colección como argumento
    collection = "sofia_ai"
    if len(sys.argv) > 1:
        collection = sys.argv[1]
    
    print(f"[INFO] Creando índice en la colección: {collection}\n")
    create_topic_index(collection)

