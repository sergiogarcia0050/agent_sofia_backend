# 🚀 Quick Start - Tavus Avatar Integration

## ✅ Code Changes: COMPLETE

All code has been fixed and is ready to use!

## 🔧 4 Steps to Get Running

### 1️⃣ Install Dependencies (30 seconds)
```bash
cd /home/juanse/Developer/Hackathons/agent_sofia_backend
uv sync
```

### 2️⃣ Add ElevenLabs API Key (1 minute)
Add to your `.env` file:
```bash
ELEVENLABS_API_KEY=your_api_key_here
```
Get key from: https://elevenlabs.io/app/settings/api-keys

### 3️⃣ Configure Tavus Persona (2 minutes)
```bash
export TAVUS_API_KEY='your_tavus_key'
./configure_tavus_persona.sh
```
**Important:** Copy the returned `persona_id` and update line 92 in `agent/agent.py`

### 4️⃣ Test It! (30 seconds)
```bash
python main.py dev
```

## ✅ Success Indicators

You should see these logs:
```
✅ Connected to room
✅ Session created with TTS
✅ Avatar created
✅ Avatar started and connected to room
✅ Session started with agent - Sofia is ready!
```

In LiveKit dashboard:
- ✅ Only ONE participant: "Sofia-Avatar"
- ✅ Avatar video visible
- ✅ Avatar speaks with lip-sync
- ✅ Responds to user speech

## 🐛 Problems?

See `TAVUS_SETUP_GUIDE.md` for detailed troubleshooting.

Quick fixes:
- **Two participants?** → Persona needs `pipeline_mode: "echo"`
- **No audio?** → Check `ELEVENLABS_API_KEY` in `.env`
- **No video?** → Verify `replica_id` and `persona_id`

## 📚 Full Documentation

- `IMPLEMENTATION_SUMMARY.md` - What was changed and why
- `TAVUS_SETUP_GUIDE.md` - Complete setup and troubleshooting
- `configure_tavus_persona.sh` - Automated persona setup script

---

**Total time to complete:** ~5 minutes

