import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

from livekit import agents
from livekit.agents import Agent, AgentSession, WorkerOptions, cli
from livekit.plugins import silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv()


class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="Eres un asistente de voz bilingüe (español e inglés). Responde en el idioma del usuario y mantén un tono amistoso."
        )
        self.openai_client: AsyncOpenAI | None = None

    async def setup(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.openai_client = AsyncOpenAI(api_key=api_key)
            print("OpenAI client configurado.")
        else:
            print("OPENAI_API_KEY no configurada")


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()
    
    assistant = Assistant()
    await assistant.setup()

    session = AgentSession(
        stt="assemblyai/universal-streaming",
        llm="openai/gpt-4o-mini",
        tts="cartesia/sonic-3:5ef98b2a-68d2-4a35-ac52-632a2d288ea6",
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    try:
        await session.start(room=ctx.room, agent=assistant)
        await session.say("Hola, soy tu asistente de voz. ¿En qué puedo ayudarte?")
    finally:
        try:
            await session.stop()
        except Exception:
            pass


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
    
# uv run python agent.py dev



	