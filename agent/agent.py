import os
import logging
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import Agent, AgentSession, RoomOutputOptions
from livekit.plugins import openai, deepgram, elevenlabs, silero, tavus

# Importar el system prompt
from prompts.sofia_prompt import SOFIA_SYSTEM_PROMPT

# Importar la tool de registro
from tools.get_evaluation_criteria import get_evaluation_criteria

load_dotenv()

# Configure logging
logger = logging.getLogger("sofia-agent")
logger.setLevel(logging.INFO)


class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions=SOFIA_SYSTEM_PROMPT,
            tools=[
                # register_candidate, deprecated
                get_evaluation_criteria,
            ]
        )


async def entrypoint(ctx: agents.JobContext):
    """
    Entrypoint for the Tavus avatar agent.
    
    Correct initialization order for Tavus:
    1. Connect to room (required for ctx.room to be available)
    2. Create session with TTS (required for Tavus)
    3. Create avatar
    4. Start avatar with session (avatar connects as separate participant)
    5. Start session with agent
    
    The agent worker connects but the avatar publishes on its behalf,
    so only the avatar appears as the visible participant.
    """
    
    # Connect to the room first (required for ctx.room to be available)
    await ctx.connect()
    logger.info("🚀 Starting Tavus avatar agent...")
    
    # Create the assistant agent
    assistant = Assistant()
    
    # Configure VAD for Spanish speech detection
    vad = silero.VAD.load(
        min_speech_duration=0.2,    # Menor valor = más sensible
        min_silence_duration=0.6,   # Menor valor = responde más rápido
        padding_duration=0.2        # Tiempo de relleno alrededor del habla
    )

    # Step 1: Create session WITH TTS (required for Tavus avatar)
    # The TTS generates audio that Tavus will lip-sync to
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
        
        # TTS: ElevenLabs with Spanish voice
        # The avatar will lip-sync to this audio output
        tts=elevenlabs.TTS(
            voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice (supports Spanish)
            model="eleven_turbo_v2_5",
            language="es",
            api_key=os.getenv("ELEVENLABS_API_KEY"),  # Read from ELEVENLABS_API_KEY env var
        ),
        
        vad=vad,
        allow_interruptions=True,
    )
    logger.info("✅ Session created with TTS")

    # Step 2: Create Tavus avatar session
    # Note: persona_id must be configured with pipeline_mode="echo" and transport_type="livekit"
    avatar = tavus.AvatarSession(
        # replica_id="r6ae5b6efc9d",
        persona_id="p36ab36ac8f8",  # Must have echo mode and livekit transport
        avatar_participant_name="Sofia-Avatar",
        replica_id="r9fa0878977a"
    )
    logger.info("✅ Avatar created")
    
    # Step 3: Start the avatar with the session
    # This connects the AVATAR as a participant (not the agent worker)
    # The avatar will be the only visible participant in the room
    await avatar.start(session, room=ctx.room)
    logger.info("✅ Avatar started and connected to room as 'Sofia-Avatar'")

    try:
        # Step 4: Start the agent session
        # The agent worker runs in the background, not visible in the room
        # The avatar will output both video and audio
        await session.start(
            room=ctx.room,
            agent=assistant,
            room_output_options=RoomOutputOptions(
                audio_enabled=True  # Critical: enables audio routing to avatar
            )
        )
        logger.info("✅ Session started with agent - Sofia is ready!")
        # El saludo inicial lo hará Sofía según su prompt

    finally:
        try:
            await session.stop()
            logger.info("Session stopped")
        except Exception as e:
            logger.error(f"Error stopping session: {e}")
