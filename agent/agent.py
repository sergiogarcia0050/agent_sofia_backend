# agent.py
import os
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import Agent, AgentSession
from livekit.plugins import openai, deepgram, cartesia, silero

# Importar el system prompt
from prompts.sofia_prompt import SOFIA_SYSTEM_PROMPT

# Importar la tool de registro
from tools.register_candidate import register_candidate

load_dotenv()


class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions=SOFIA_SYSTEM_PROMPT,
            tools=[
                register_candidate,
                # Aquí irán las demás tools cuando las agregues
            ]
        )


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()
    
    assistant = Assistant()
    
    vad = silero.VAD.load(
        min_speech_duration=0.2,    # Menor valor = más sensible
        min_silence_duration=0.6,   # Menor valor = responde más rápido
        padding_duration=0.2        # Tiempo de relleno alrededor del habla
    )

    session = AgentSession(
        # STT: Deepgram Nova 3 - excelente para español
        stt=deepgram.STT(
            model="nova-3",
            language="es",
        ),
        
        # LLM: GPT-4o mini - muy bueno en español
        llm=openai.LLM(
            model="gpt-4o-mini",
            temperature=0.8,
        ),
        
        # TTS: Cartesia con voz femenina española
        tts=cartesia.TTS(
            model="sonic-multilingual",
            voice="248be419-c632-4f23-adf1-5324ed7dbf1d",
            language="es",
        ),
        
        vad=vad,
        allow_interruptions=True,
    )

    try:
        await session.start(room=ctx.room, agent=assistant)
        # El saludo inicial lo hará Sofía según su prompt
    finally:
        try:
            await session.stop()
        except Exception:
            pass
