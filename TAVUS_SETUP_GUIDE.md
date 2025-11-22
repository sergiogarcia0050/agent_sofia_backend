# Tavus Avatar Setup Guide for Sofia

## ✅ Code Changes Completed

The following code changes have been implemented:

1. ✅ Added `livekit-plugins-elevenlabs>=1.3.3` to `pyproject.toml`
2. ✅ Updated `agent/agent.py` with:
   - Correct imports (elevenlabs, RoomOutputOptions, logging)
   - Fixed initialization order
   - Added TTS configuration with ElevenLabs
   - Added `ctx.connect()` call
   - Added `RoomOutputOptions(audio_enabled=True)`
   - Added detailed logging for debugging

## 🔧 Manual Steps Required

### Step 1: Install Dependencies

Run this command to install the new ElevenLabs dependency:

```bash
cd /home/juanse/Developer/Hackathons/agent_sofia_backend
uv sync
```

Or if using pip:

```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Create or update your `.env` file in the project root with the following:

```bash
# Existing variables (keep these)
OPENAI_API_KEY=your_openai_key
DEEPGRAM_API_KEY=your_deepgram_key
TAVUS_API_KEY=your_tavus_key
LIVEKIT_API_KEY=your_livekit_key
LIVEKIT_API_SECRET=your_livekit_secret
LIVEKIT_URL=your_livekit_url

# NEW: Add ElevenLabs API key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

**How to get your ElevenLabs API key:**
1. Go to https://elevenlabs.io/
2. Sign up or log in
3. Navigate to Profile Settings → API Keys
4. Copy your API key

### Step 3: Configure Tavus Persona (CRITICAL)

Your Tavus persona **MUST** be configured with specific settings for LiveKit integration.

**Option A: Create a new persona via API (Recommended)**

```bash
curl --request POST \
  --url https://tavusapi.com/v2/personas \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_TAVUS_API_KEY" \
  -d '{
    "layers": {
        "transport": {
            "transport_type": "livekit"
        }
    },
    "persona_name": "Sofia-Avatar-LiveKit",
    "pipeline_mode": "echo"
}'
```

**Important:** Save the `persona_id` from the response and update it in `agent/agent.py` line 92.

**Option B: Update existing persona (if supported by Tavus API)**

If you want to keep using persona `p8c8cc770700`, you need to verify/update it with:
- `pipeline_mode: "echo"`
- `transport.transport_type: "livekit"`

Check Tavus documentation for PATCH/PUT endpoints to update personas.

**Option C: Use Tavus Dashboard**

1. Log in to https://tavus.io/dashboard
2. Navigate to Personas
3. Either create a new persona or edit `p8c8cc770700`
4. Ensure these settings:
   - **Pipeline Mode**: `echo`
   - **Transport Type**: `livekit`

### Step 4: Verify Persona Configuration

To verify your persona is configured correctly, you can query the Tavus API:

```bash
curl --request GET \
  --url https://tavusapi.com/v2/personas/p8c8cc770700 \
  -H "x-api-key: YOUR_TAVUS_API_KEY"
```

Look for:
```json
{
  "persona_id": "p8c8cc770700",
  "pipeline_mode": "echo",
  "layers": {
    "transport": {
      "transport_type": "livekit"
    }
  }
}
```

### Step 5: Optional - Choose a Different Spanish Voice

The code currently uses ElevenLabs voice `21m00Tcm4TlvDq8ikWAM` (Rachel).

To use a different Spanish voice:

1. Go to https://elevenlabs.io/voice-library
2. Browse Spanish voices
3. Copy the voice ID
4. Update line 78 in `agent/agent.py`:

```python
tts=elevenlabs.TTS(
    voice_id="YOUR_VOICE_ID_HERE",  # Replace with your chosen voice
    model="eleven_turbo_v2_5",
    language="es",
),
```

Popular Spanish voices on ElevenLabs:
- Rachel (`21m00Tcm4TlvDq8ikWAM`) - Multilingual, clear
- You can also clone a custom voice in ElevenLabs dashboard

## 🧪 Testing the Integration

### Step 1: Run the Agent

```bash
cd /home/juanse/Developer/Hackathons/agent_sofia_backend
python main.py dev
```

### Step 2: Check the Logs

You should see these log messages in order:

```
✅ Connected to room
✅ Session created with TTS
✅ Avatar created
✅ Avatar started and connected to room
✅ Session started with agent - Sofia is ready!
```

### Step 3: Verify in LiveKit Dashboard

1. Open your LiveKit dashboard
2. Navigate to the room
3. **Expected behavior:**
   - ✅ Only ONE participant visible: "Sofia-Avatar"
   - ✅ Avatar video is visible
   - ✅ Avatar shows lip movement when speaking
   - ✅ Audio comes from the avatar participant
   - ✅ Avatar responds to user speech

### Step 4: Common Issues and Solutions

**Issue: Two participants appear**
- ❌ Cause: Persona not configured with `pipeline_mode: "echo"`
- ✅ Solution: Follow Step 3 above to configure persona correctly

**Issue: Avatar appears but doesn't speak**
- ❌ Cause: Missing `audio_enabled=True` or no TTS configured
- ✅ Solution: Already fixed in the code - verify ElevenLabs API key is set

**Issue: No avatar video**
- ❌ Cause: Invalid replica_id or persona_id
- ✅ Solution: Verify IDs in Tavus dashboard

**Issue: Avatar doesn't lip-sync**
- ❌ Cause: Persona not in "echo" mode
- ✅ Solution: Configure persona with `pipeline_mode: "echo"`

## 🔍 Debugging Commands

### Check if ElevenLabs is working:

```python
# Test script
from livekit.plugins import elevenlabs
import os
from dotenv import load_dotenv

load_dotenv()
tts = elevenlabs.TTS(voice_id="21m00Tcm4TlvDq8ikWAM")
print("✅ ElevenLabs initialized successfully")
```

### Check Tavus API connection:

```bash
curl --request GET \
  --url https://tavusapi.com/v2/personas \
  -H "x-api-key: YOUR_TAVUS_API_KEY"
```

## 📋 Final Checklist

Before going live, verify:

- [ ] `uv sync` or `pip install` completed successfully
- [ ] `.env` file has `ELEVENLABS_API_KEY`
- [ ] Tavus persona configured with `pipeline_mode: "echo"` and `transport_type: "livekit"`
- [ ] Agent starts without errors
- [ ] Only ONE participant appears in LiveKit room
- [ ] Avatar video is visible
- [ ] Avatar speaks and lip-syncs correctly
- [ ] Avatar responds to user speech
- [ ] Audio quality is good

## 🎯 What Changed and Why

### Before (Broken):
```python
# ❌ No ctx.connect()
# ❌ No TTS in session
# ❌ Wrong parameter names
avatar = tavus.AvatarSession(
    persona_id="...",
    replica_id="...",
    avatar_participant_identity="...",  # Wrong param
)
```

### After (Fixed):
```python
# ✅ Connect first
await ctx.connect()

# ✅ TTS configured
session = AgentSession(
    stt=...,
    llm=...,
    tts=elevenlabs.TTS(...),  # Required!
    vad=...,
)

# ✅ Correct parameters
avatar = tavus.AvatarSession(
    replica_id="...",
    persona_id="...",
    avatar_participant_name="...",
)

# ✅ Start avatar with session
await avatar.start(session, room=ctx.room)

# ✅ Audio enabled
await session.start(
    room=ctx.room,
    agent=assistant,
    room_output_options=RoomOutputOptions(audio_enabled=True)
)
```

## 📚 References

- [LiveKit Tavus Plugin Docs](https://docs.livekit.io/agents/models/avatar/plugins/tavus/)
- [Tavus API Documentation](https://docs.tavus.io/)
- [ElevenLabs Voice Library](https://elevenlabs.io/voice-library)
- [LiveKit Agents Python SDK](https://docs.livekit.io/agents/)

## 🆘 Need Help?

If you encounter issues:

1. Check the logs for error messages
2. Verify all API keys are correct
3. Confirm Tavus persona configuration
4. Test ElevenLabs API separately
5. Check LiveKit dashboard for participant status

Good luck! 🚀

