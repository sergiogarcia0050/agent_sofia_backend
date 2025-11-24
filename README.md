# Sofia - AI Technical Interview Agent 🎯

Sofia is an intelligent avatar-based technical interview agent built with LiveKit, Tavus, and OpenAI. She conducts automated technical interviews for junior frontend developer positions at FailFast, evaluating candidates across HTML, CSS, JavaScript, and development tools.

## 🌟 Features

- **AI-Powered Avatar**: Uses Tavus for realistic avatar video with lip-sync
- **Multilingual Support**: Optimized for Spanish language interactions
- **Real-time Audio/Video**: Built on LiveKit's WebRTC infrastructure
- **Structured Evaluation**: Systematic assessment across multiple technical areas
- **Automated Scoring**: Tool-based evaluation system with configurable thresholds
- **Natural Conversations**: Voice Activity Detection (VAD) with interruption support
- **Professional Feedback**: Detailed, empathetic feedback for candidates

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────────────────┐
│                  LiveKit Room                        │
│  ┌────────────────────┐  ┌──────────────────────┐  │
│  │   Sofia Agent      │  │   Tavus Avatar       │  │
│  │   (Background)     │◄─┤   (Visible)          │  │
│  │                    │  │                      │  │
│  │ - GPT-4o-mini      │  │ - Video Output       │  │
│  │ - Deepgram STT     │  │ - Lip-sync           │  │
│  │ - ElevenLabs TTS   │  │ - Audio Output       │  │
│  └────────────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Technology Stack

- **Agent Framework**: LiveKit Agents SDK
- **LLM**: OpenAI GPT-4o-mini
- **STT**: Deepgram Nova 3 (Spanish optimized)
- **TTS**: ElevenLabs Turbo v2.5 (Rachel voice)
- **Avatar**: Tavus AvatarSession
- **VAD**: Silero Voice Activity Detection
- **Language**: Python 3.8+

## 📋 Prerequisites

- Python 3.8 or higher
- LiveKit Cloud account or self-hosted server
- OpenAI API key
- Deepgram API key
- ElevenLabs API key
- Tavus API key with configured persona

## 🚀 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd sofia-agent
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root:

```env
# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# OpenAI Configuration
OPENAI_API_KEY=your_openai_key

# Deepgram Configuration
DEEPGRAM_API_KEY=your_deepgram_key

# ElevenLabs Configuration
ELEVENLABS_API_KEY=your_elevenlabs_key

# Tavus Configuration
TAVUS_API_KEY=your_tavus_key
```

## 🎮 Usage

### Running the Agent

```bash
python agent.py
```

### Configuration Options

#### Voice Activity Detection (VAD)

Adjust sensitivity in `agent.py`:

```python
vad = silero.VAD.load(
    min_speech_duration=0.2,    # Lower = more sensitive
    min_silence_duration=0.6,   # Lower = faster response
    padding_duration=0.2        # Audio padding
)
```

#### Tavus Avatar

Configure your avatar in `agent.py`:

```python
avatar = tavus.AvatarSession(
    persona_id="your_persona_id",  # Must use echo mode + livekit transport
    avatar_participant_name="Sofia-Avatar",
    replica_id="your_replica_id"
)
```

**Important**: Your Tavus persona must be configured with:
- `pipeline_mode="echo"`
- `transport_type="livekit"`

## 🔧 Project Structure

```
sofia-agent/
├── agent.py                    # Main entry point
├── prompts/
│   └── sofia_prompt.py        # System prompt and interview logic
├── tools/
│   ├── get_evaluation_criteria.py
│   └── evaluation_question.py
├── requirements.txt
├── .env
└── README.md
```

## 📚 Interview Flow

### 1. Initial Greeting
Sofia introduces herself and confirms the candidate is ready to begin.

### 2. Evaluation Setup
Calls `get_evaluation_criteria()` to retrieve:
- Technical questions by area
- Evaluation criteria and scoring scales
- Pass/fail thresholds
- Area weights

### 3. Technical Assessment
Evaluates across four areas:
- **HTML**: Semantic markup, accessibility, best practices
- **CSS**: Layouts, responsive design, selectors
- **JavaScript**: Core concepts, ES6+, async programming
- **Tools**: Git, build tools, debugging

For each question:
1. Sofia asks the question
2. Candidate responds
3. `evaluation_question()` tool scores the response
4. Sofia provides feedback
5. Continues to next question

### 4. Completion
- Calls `complete_evaluation()` with full interview data
- Calls `update_candidate_status()` with pass/fail decision
- Provides detailed, empathetic final feedback

## 🎯 Evaluation System

### Scoring Scale (0-100)

As defined by `get_evaluation_criteria()`:
- **90-100**: Exceptional understanding
- **75-89**: Strong knowledge
- **60-74**: Adequate comprehension
- **40-59**: Partial understanding
- **0-39**: Insufficient knowledge

### Pass Criteria

Candidates must meet thresholds defined in the database for:
- Individual area scores
- Weighted average across all areas
- Critical concept mastery

## 🛠️ Available Tools

### `get_evaluation_criteria()`
Retrieves complete evaluation configuration from database:
- Questions organized by technical area
- Scoring criteria and scales
- Pass/fail thresholds
- Area weights

### `evaluation_question(response: str, topic: str)`
Evaluates a candidate's response:
- **Parameters**:
  - `response`: Complete candidate answer
  - `topic`: Technical area (HTML, CSS, JavaScript, Tools)
- **Returns**: Feedback message and quality assessment

## 🤖 Agent Behavior

### Communication Style
- Professional, warm, and empathetic
- Never uses negative language ("wrong", "incorrect", "error")
- Provides encouraging feedback
- Maintains conversational pace
- Natural interruption handling

### Interview Management
- One question at a time
- Active listening without interruption
- 10-15 minute duration
- 12-16 questions total
- Balanced across all areas

## 🔐 Security Considerations

- Store API keys in `.env` file (never commit)
- Use environment-specific configurations
- Implement rate limiting for production
- Secure WebRTC connections via LiveKit

## 🐛 Troubleshooting

### Common Issues

**Avatar not connecting:**
- Verify Tavus persona is configured with echo mode
- Check `transport_type="livekit"` is set
- Ensure room is connected before avatar creation

**No audio output:**
- Verify `audio_enabled=True` in `RoomOutputOptions`
- Check ElevenLabs API key and voice ID
- Confirm TTS is created before avatar

**VAD too sensitive/insensitive:**
- Adjust `min_speech_duration` and `min_silence_duration`
- Test with different `padding_duration` values

**Tool calls failing:**
- Verify all tools are properly registered in `Assistant.__init__`
- Check tool function signatures match expected parameters
- Review logs for specific error messages

## 📊 Logging

The agent uses Python's logging module:

```python
import logging
logger = logging.getLogger("sofia-agent")
logger.setLevel(logging.INFO)
```

Key log events:
- Room connection
- Session creation
- Avatar initialization
- Tool invocations
- Session lifecycle

## 🚦 Development Roadmap

- [ ] Multi-language support (English, Portuguese)
- [ ] Advanced analytics dashboard
- [ ] Custom evaluation criteria per position
- [ ] Video recording and playback
- [ ] Integration with ATS systems
- [ ] Real-time interview monitoring

## 📝 License

[Specify your license here]

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

For issues, questions, or suggestions:
- Open an issue in the repository
- Contact: [your-email@example.com]

## 🙏 Acknowledgments

- **LiveKit** for real-time infrastructure
- **Tavus** for avatar technology
- **OpenAI** for language capabilities
- **Deepgram** for speech recognition
- **ElevenLabs** for natural voice synthesis

---

Built with ❤️ for FailFast technical recruitment
