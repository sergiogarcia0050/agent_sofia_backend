import requests
from typing import Dict, Any
from livekit.agents import function_tool


@function_tool
async def evaluation_question(response: str, topic: str) -> Dict[str, Any]:
    """
    Evalúa la respuesta del usuario enviándola al webhook de evaluación.
    
    Args:
        response: La respuesta del usuario a evaluar
        topic: El tema o tópico relacionado (ej: "React", "JavaScript", etc)
        
    Returns:
        Dict con la respuesta del webhook que incluye el mensaje a mostrar al usuario
        
    Raises:
        Exception: Si hay un error en la comunicación con el webhook
    """
    # webhook_url = "https://workflow.failfast.com.co/webhook-test/sofia_ai"
    webhook_url = "https://workflow.failfast.com.co/webhook/sofia_ai"
    
    payload = {
        "response": response,
        "topic": topic
    }
    
    try:
        # Realizar la petición POST al webhook
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30  # Timeout de 30 segundos
        )
        
        # Verificar que la petición fue exitosa
        response.raise_for_status()
        
        # Retornar la respuesta del webhook
        return response.json()
        
    except requests.exceptions.Timeout:
        raise Exception("Timeout al conectar con el servicio de evaluación")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error al evaluar la respuesta: {str(e)}")
    except ValueError:
        raise Exception("Error al procesar la respuesta del servicio de evaluación")


if __name__ == "__main__":
    # Ejemplo de uso
    import asyncio
    
    async def test():
        try:
            result = await evaluation_question(
                "useCallback se usa para memorizar funciones y useMemo para valores computados",
                "React"
            )
            print("Resultado de la evaluación:")
            print(result)
        except Exception as e:
            print(f"Error: {e}")
    
    asyncio.run(test())

