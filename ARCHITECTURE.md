# Architecture Overview

This document provides a technical overview of Oread's system architecture, data flow, and technology stack.

---

## Table of Contents
- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Component Breakdown](#component-breakdown)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Directory Structure](#directory-structure)
- [Key Design Decisions](#key-design-decisions)

---

## System Overview

Oread uses a **hybrid architecture** combining Node.js (backend API) and Python (AI inference) for optimal performance:

- **Frontend:** Vanilla JavaScript + HTML5 + SCSS (compiled via webpack)
- **Backend API:** Node.js + Express
- **Inference Service:** Python + llama-cpp-python
- **Data Storage:** Encrypted JSON files (local filesystem)
- **Memory:** ChromaDB vector database (optional)
- **Web Search:** MCP (Model Context Protocol) client to Brave API (optional)

This separation allows Python to handle computationally intensive LLM operations while Node.js manages HTTP requests, session handling, and file serving.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER BROWSER                            │
│                    (https://localhost:9000)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Static Files)                      │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │ index.html │  │ settings.html│  │ Assets (CSS/JS/Images) │  │
│  └────────────┘  └──────────────┘  └────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Fetch API Calls
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              NODE.JS BACKEND (Express Server)                    │
│                  Port: 9000 (127.0.0.1)                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      API ROUTES                           │   │
│  │  • /api/chat         - Send message, get response        │   │
│  │  • /api/profiles     - CRUD for character profiles       │   │
│  │  • /api/user-settings- User settings & preferences       │   │
│  │  • /api/auth         - Login, password changes           │   │
│  │  • /api/starters     - Generate conversation starters    │   │
│  │  • /api/favorites    - Save/retrieve favorite messages   │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  CORE SERVICES                            │   │
│  │  • HybridChatbot     - Orchestrates message processing   │   │
│  │  • CharacterLoader   - Loads/caches character profiles   │   │
│  │  • ProfileStorage    - Encrypted file I/O                │   │
│  │  • SessionManager    - Session & encryption key mgmt     │   │
│  │  • InferenceClient   - HTTP client to Python service     │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP (127.0.0.1:9001)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│           PYTHON INFERENCE SERVICE (FastAPI)                     │
│                  Port: 9001 (127.0.0.1)                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   API ENDPOINTS                           │   │
│  │  • /health           - Service health check              │   │
│  │  • /infer/emotion    - Emotion detection                 │   │
│  │  • /infer/llm/context- Generate text response            │   │
│  │  • /infer/memory/save- Save conversation to vector DB    │   │
│  │  • /cancel           - Cancel ongoing generation         │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    PROCESSORS                             │   │
│  │  • EmotionDetector   - RoBERTa model for emotion         │   │
│  │  • LLMProcessor      - llama.cpp inference               │   │
│  │  • PromptBuilder     - Dynamic prompt construction       │   │
│  │  • ContextManager    - Memory + web search context       │   │
│  │  • LorebookGenerator - Personality trait expansion       │   │
│  │  • ResponseCleaner   - Format/clean LLM output           │   │
│  │  • CrisisDetector    - Safety intervention detection     │   │
│  │  • AgeDetector       - Age-related content detection     │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────┬─────────────────────────────┬────────────────────────────┘
       │                             │
       │                             │
       ▼                             ▼
┌──────────────────┐        ┌───────────────────────────┐
│  LLAMA.CPP LLM   │        │   OPTIONAL SERVICES       │
│   (GGUF Model)   │        │  ┌─────────────────────┐  │
│                  │        │  │ ChromaDB (Memory)   │  │
│  • Loaded in RAM │        │  │  - Vector embeddings│  │
│  • Metal/CUDA GPU│        │  │  - Semantic search  │  │
│  • Streaming     │        │  └─────────────────────┘  │
│                  │        │  ┌─────────────────────┐  │
│                  │        │  │ Brave Search (MCP)  │  │
│                  │        │  │  - Web search API   │  │
│                  │        │  │  - Real-time facts  │  │
│                  │        │  └─────────────────────┘  │
└──────────────────┘        └───────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   LOCAL FILESYSTEM                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  data/                                                    │   │
│  │    ├── profiles/         - Encrypted character profiles  │   │
│  │    │    ├── *.json       - AES-256-GCM encrypted         │   │
│  │    │    └── *.txt        - Legacy plaintext (deprecated) │   │
│  │    ├── user-settings.json- Encrypted user data           │   │
│  │    ├── active-character.json - Current character         │   │
│  │    ├── conversations/    - Chat history (optional)       │   │
│  │    ├── favorites/        - Saved messages                │   │
│  │    └── uploads/avatars/  - Character images              │   │
│  │  models/                                                  │   │
│  │    └── *.gguf            - LLM model files               │   │
│  │  inference/chroma_db/    - Vector database (optional)    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### Frontend Layer

**Location:** `/frontend/src/`

**Purpose:** User interface and client-side logic

**Key Files:**
- `index.html` - Main chat interface
- `settings.html` - Character/profile management
- `assets/js/chat.js` - Chat message handling, streaming, favorites
- `assets/js/settings.js` - Profile editing, user settings
- `assets/scss/` - Modular SCSS stylesheets (compiled to CSS)

**Technologies:**
- Vanilla JavaScript (no framework)
- Webpack for bundling and SCSS compilation
- Fetch API for backend communication
- Local Storage for minimal client-side caching

---

### Backend API Layer (Node.js)

**Location:** `/backend/src/`

**Purpose:** HTTP API server, session management, file I/O

#### Core Components

**1. HybridChatbot** (`core/chatbotHybrid.js`)
- Orchestrates message processing
- Calls Python inference service
- Manages conversation history
- Handles emotion detection and response building

**2. CharacterLoader** (`core/characterLoader.js`)
- Loads character profiles from encrypted files
- Caches active character to avoid repeated disk reads
- Merges user settings with character data

**3. ProfileStorage** (`services/ProfileStorage.js`)
- Encrypts/decrypts profiles using AES-256-GCM
- PBKDF2 key derivation from user password
- Handles profile versioning (v2.0 format)
- Manages re-encryption during password changes

**4. SessionManager** (`services/sessionManager.js`)
- Express session middleware
- Stores encryption keys in session memory
- Prevents unauthorized access to profiles

**5. InferenceClient** (`clients/inferenceClient.js`)
- HTTP client to Python inference service
- Health checking and automatic reconnection
- Request/response serialization

#### API Routes

**Authentication** (`routes/auth.js`)
- `POST /api/login` - Verify password, create session
- `POST /api/change-password` - Re-encrypt all profiles
- `POST /api/logout` - Clear session

**Chat** (`routes/chat.js`)
- `POST /api/chat` - Send message, get AI response
- `POST /api/regenerate` - Regenerate last message with custom instructions
- `GET /api/starters` - Generate conversation starter

**Profiles** (`routes/profiles.js`)
- `GET /api/profiles` - List all character profiles
- `GET /api/profiles/:name` - Get specific profile
- `POST /api/profiles/:name` - Save/update profile
- `DELETE /api/profiles/:name` - Delete profile
- `POST /api/profiles/active` - Switch active character
- `POST /api/profiles/:name/avatar` - Upload character image

**User Settings** (`routes/profiles.js`)
- `GET /api/user-settings` - Get user profile data
- `POST /api/user-settings` - Save user data
- `GET /api/export-data` - Download encrypted backup

**Favorites** (`routes/favorites.js`)
- `GET /api/favorites/:character` - Get favorite messages
- `POST /api/favorites/:character` - Save favorite message
- `DELETE /api/favorites/:character/:id` - Remove favorite

---

### Inference Service Layer (Python)

**Location:** `/inference/`

**Purpose:** AI model inference, emotion detection, context management

#### Core Processors

**1. EmotionDetector** (`processors/emotion_detector.py`)
- Uses fine-tuned RoBERTa ONNX model
- Classifies emotions: joy, sadness, anger, fear, love, surprise, neutral
- Returns confidence scores and intensity levels

**2. LLMProcessor** (`processors/llm_processor.py`)
- Loads GGUF model via llama-cpp-python
- Generates text responses with context
- Handles cancellation requests
- Manages GPU/Metal acceleration
- Implements safety interventions (crisis detection, age checks)

**3. PromptBuilder** (`processors/prompt_builder.py`)
- Constructs prompts from character profiles
- Integrates conversation history
- Injects lorebook entries dynamically
- Time-aware messaging (greetings based on time of day)
- Emotional guidance adjustments

**4. ContextManager** (`processors/context_manager.py`)
- Fetches relevant memories from ChromaDB
- Triggers web searches based on query patterns
- Formats context for inclusion in prompts

**5. LorebookGenerator** (`processors/lorebook_generator.py`)
- Generates personality trait descriptions from tags
- Creates example dialogues
- Produces dynamic context chunks

**6. ResponseCleaner** (`processors/response_cleaner.py`)
- Removes LLM artifacts (incomplete sentences, repetition)
- Strips formatting errors
- Ensures clean output

**7. CrisisDetector** (`processors/crisis_detector.py`)
- Pattern matching for self-harm/suicidal content
- Returns crisis resources (988 hotline)
- Blocks generation when detected

**8. AgeDetector** (`processors/age_detector.py`)
- Detects mentions of underage individuals
- Triggers age redirection (characters aged to 25+)

---

## Data Flow

### Message Processing Flow

```
1. USER sends message
   ↓
2. FRONTEND (chat.js)
   - Displays user message bubble
   - Shows typing indicator
   - POST /api/chat
   ↓
3. BACKEND (chatbotHybrid.js)
   - Load character profile (cached)
   - Load user settings
   - Merge into enriched character object
   - HTTP POST to inference service /infer/llm/context
   ↓
4. PYTHON INFERENCE (llm_processor.py)
   Step 1: Emotion Detection
   - POST /infer/emotion internally
   - EmotionDetector → RoBERTa model
   - Returns emotion + confidence

   Step 2: Context Fetching
   - ContextManager.fetch_memory_context()
     → ChromaDB semantic search (if enabled)
   - ContextManager.fetch_web_context()
     → MCP client → Brave Search API (if enabled)

   Step 3: Crisis/Age Safety Checks
   - CrisisDetector.detect()
   - AgeDetector.detect()
   - Return intervention message if needed

   Step 4: Prompt Construction
   - PromptBuilder.build_prompt()
   - Integrates: character bio, conversation history,
     lorebook chunks, emotional guidance, search results

   Step 5: LLM Generation
   - llama.cpp inference
   - Streaming output (token by token)
   - Responds to cancellation

   Step 6: Response Cleaning
   - ResponseCleaner.clean()
   - Removes artifacts
   ↓
5. PYTHON returns JSON response
   {
     "text": "cleaned response",
     "tokens_generated": 150
   }
   ↓
6. BACKEND (chatbotHybrid.js)
   - Append to conversation history
   - Save to ChromaDB (background, non-blocking)
   - Return response to frontend
   ↓
7. FRONTEND (chat.js)
   - Hide typing indicator
   - Display AI message bubble
   - Apply emotion styling
   - Enable regenerate button
```

---

## Technology Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| HTML5 | Page structure |
| SCSS → CSS | Styling (modular, compiled) |
| Vanilla JavaScript | Client-side logic |
| Webpack | Bundling, SCSS compilation |
| Fetch API | HTTP requests |

### Backend (Node.js)
| Technology | Version | Purpose |
|------------|---------|---------|
| Node.js | 18+ | Runtime |
| Express | 4.x | HTTP server |
| express-session | 1.x | Session management |
| multer | 1.x | File uploads (avatars) |
| helmet | 7.x | Security headers |
| cors | 2.x | CORS handling |

### Inference (Python)
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Runtime |
| FastAPI | 0.100+ | HTTP API framework |
| llama-cpp-python | 0.2.x | LLM inference |
| transformers | 4.x | RoBERTa emotion model |
| onnxruntime | 1.x | Optimized emotion inference |
| chromadb | 0.4.x | Vector database (optional) |
| httpx | 0.24+ | Async HTTP client |
| mcp | 0.9.x | Model Context Protocol (web search) |

### Security
| Technology | Purpose |
|------------|---------|
| crypto (Node.js) | AES-256-GCM encryption |
| pbkdf2 | Password-based key derivation |
| Self-signed SSL | HTTPS for localhost |
| express-session | Secure session cookies |

---

## Directory Structure

```
echo/
├── backend/
│   ├── src/
│   │   ├── routes/          # Express route handlers
│   │   │   ├── auth.js
│   │   │   ├── chat.js
│   │   │   ├── profiles.js
│   │   │   └── favorites.js
│   │   ├── core/            # Business logic
│   │   │   ├── chatbotHybrid.js
│   │   │   ├── characterLoader.js
│   │   │   └── config.js
│   │   ├── services/        # Support services
│   │   │   ├── ProfileStorage.js
│   │   │   ├── ProfileCache.js
│   │   │   └── sessionManager.js
│   │   ├── clients/         # HTTP clients
│   │   │   └── inferenceClient.js
│   │   ├── controllers/     # Route controllers
│   │   │   └── ProfileController.js
│   │   ├── processors/      # Response building
│   │   │   └── responseBuilder.js
│   │   ├── config/          # Configuration
│   │   │   └── multerConfig.js
│   │   └── server.js        # Express app entry point
│   ├── .env                 # Backend config
│   ├── package.json
│   └── package-lock.json
│
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   │   ├── css/         # Compiled CSS (generated)
│   │   │   ├── scss/        # Source SCSS files
│   │   │   │   ├── base/
│   │   │   │   ├── components/
│   │   │   │   ├── layout/
│   │   │   │   └── styles.scss
│   │   │   ├── js/
│   │   │   │   ├── chat.js
│   │   │   │   ├── settings.js
│   │   │   │   ├── config.js
│   │   │   │   └── auth.js
│   │   │   ├── images/      # Logo, icons
│   │   │   └── audio/       # Ambient music files
│   │   ├── index.html       # Main chat page
│   │   ├── settings.html    # Settings/profiles page
│   │   └── login.html       # Login page
│   ├── webpack.config.js    # Webpack configuration
│   ├── package.json
│   └── package-lock.json
│
├── inference/
│   ├── processors/
│   │   ├── emotion_detector.py
│   │   ├── llm_processor.py
│   │   ├── llm_inference.py
│   │   ├── prompt_builder.py
│   │   ├── context_manager.py
│   │   ├── lorebook_generator.py
│   │   ├── response_cleaner.py
│   │   ├── crisis_detector.py
│   │   └── age_detector.py
│   ├── web_search/
│   │   ├── client.py        # MCP client
│   │   └── servers/
│   │       └── search_server.py  # Brave API MCP server
│   ├── main.py              # FastAPI app entry point
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Inference config
│
├── data/                    # User data (local only)
│   ├── profiles/
│   │   ├── Echo.json        # Default character (not encrypted)
│   │   ├── Kairos.json      # Default character (not encrypted)
│   │   └── *.json           # User characters (encrypted)
│   ├── user-settings.json   # Encrypted user profile
│   ├── active-character.json
│   ├── conversations/       # Optional chat logs
│   ├── favorites/
│   │   └── *.json           # Favorite messages per character
│   └── uploads/
│       └── avatars/         # Character images
│
├── models/                  # LLM model files (not in repo)
│   ├── *.gguf               # GGUF format models
│   └── roberta_emotions_onnx/  # Emotion detection model
│
├── scripts/
│   └── start-oread.sh       # Startup script
│
├── docs/                    # Documentation
│   └── screenshots/
│
├── README.md
├── ARCHITECTURE.md          # This file
├── INSTALLATION.md
├── FAQ.md
├── SECURITY_ETHICS_SAFETY.md
└── LICENSE
```

---

## Key Design Decisions

### 1. Hybrid Python + Node.js Architecture

**Decision:** Use Python for inference, Node.js for API server.

**Rationale:**
- Python's llama-cpp-python bindings are faster than Node.js equivalents
- Node.js excels at handling HTTP requests and file I/O
- Separation of concerns: API logic vs. AI inference
- Easier to scale/replace components independently

**Trade-offs:**
- Extra HTTP hop (Node → Python)
- Two processes to manage
- More complex deployment

**Mitigation:**
- localhost-only communication (minimal latency)
- Single startup script (`start-oread.sh`)
- Automatic health checking

---

### 2. Encrypted Profiles with Session Keys

**Decision:** Encrypt character/user profiles at rest using password-derived keys stored in session memory.

**Rationale:**
- Protects privacy even if filesystem is accessed
- Session-based keys prevent unauthorized access
- User controls encryption via password

**Trade-offs:**
- Password changes require re-encryption of all files
- Cache invalidation complexity
- Potential data loss if re-encryption fails partway

**Mitigation:**
- Idempotent re-encryption (can resume after failure)
- Export/backup functionality
- Default characters unencrypted for easy onboarding

---

### 3. Optional Memory & Web Search

**Decision:** Disable ChromaDB memory and web search by default.

**Rationale:**
- Performance overhead on slower systems
- Privacy concerns (web search exposes queries)
- Not essential for core functionality
- ChromaDB adds startup time and RAM usage

**Trade-offs:**
- Less contextually aware by default
- Users must opt-in to advanced features

**Mitigation:**
- Clear UI toggles in settings
- Documentation explaining benefits/costs
- Graceful degradation if services unavailable

---

### 4. Lorebook Generation from Tags

**Decision:** Generate lorebook entries dynamically from personality tags instead of requiring manual lorebook authoring.

**Rationale:**
- Lowers barrier to entry (no lorebook knowledge needed)
- Consistent personality trait descriptions
- Faster character creation

**Trade-offs:**
- Less control than manual lorebooks
- Generated content may be generic
- Effectiveness varies by model

**Mitigation:**
- Users can still manually edit character profiles
- Future enhancement: manual lorebook editing UI

---

### 5. Frontend Webpack Build Process

**Decision:** Migrate from inline CSS to SCSS with webpack compilation.

**Rationale:**
- Better code organization (modular styles)
- Maintainability (variables, nesting, mixins)
- Production optimizations (minification, autoprefixing)

**Trade-offs:**
- Added build step
- Development complexity

**Mitigation:**
- Watch mode for development
- Pre-built CSS committed to repo (no build required for users)

---

### 6. Crisis & Age Detection

**Decision:** Implement pattern-based safety interventions in Python inference layer.

**Rationale:**
- Ethical responsibility to provide crisis resources
- Prevent inappropriate age-related content
- License requirement (cannot be disabled)

**Trade-offs:**
- Pattern matching can have false positives
- May break immersion
- Adds latency to generation

**Mitigation:**
- Conservative thresholds
- Graceful messaging
- Only triggers on high-confidence matches

---

## Performance Considerations

### Optimization Strategies

1. **Character Profile Caching**
   - Profiles cached after first load
   - Avoids repeated disk I/O and decryption
   - Invalidated on profile updates

2. **Conversation History Trimming**
   - Max 20 messages in context (configurable)
   - Prevents context overflow
   - Older messages pruned automatically

3. **GPU Acceleration**
   - Metal (Apple Silicon), CUDA (NVIDIA), ROCm (AMD)
   - Offloads all model layers to GPU (-1 flag)
   - 5-10x faster than CPU-only

4. **Model Quantization**
   - Q4_K_M quantization recommended
   - 4-bit weights, ~4GB RAM for 12B model
   - Minimal quality loss vs. F16

5. **Async Memory Saving**
   - ChromaDB writes happen in background
   - Don't block response return
   - Fire-and-forget with error logging

6. **Streaming Responses** (Future)
   - Currently: full response returned at once
   - Planned: token-by-token streaming to frontend
   - Improves perceived responsiveness

---

## Security Architecture

### Defense Layers

1. **Network Isolation**
   - localhost-only binding (127.0.0.1)
   - No external network access (except optional web search)
   - Self-signed SSL cert for HTTPS

2. **Encryption at Rest**
   - AES-256-GCM (authenticated encryption)
   - PBKDF2 key derivation (100,000 iterations)
   - Unique salt per file

3. **Session Security**
   - HttpOnly cookies
   - Encryption keys in memory only
   - No keys persisted to disk
   - Session expiration on logout

4. **Input Validation**
   - File path sanitization
   - Profile name validation
   - Max length checks
   - Type checking

5. **Safety Interventions**
   - Crisis detection
   - Age verification
   - Consent requirements
   - Anti-violence filters

See [SECURITY_ETHICS_SAFETY.md](SECURITY_ETHICS_SAFETY.md) for complete details.

---

## Future Architecture Improvements

### Planned Enhancements

1. **Streaming Responses**
   - WebSocket connection for token streaming
   - Real-time typing animation
   - Cancellation support

2. **Multi-User Support**
   - User ID-based profile isolation
   - Per-user encryption keys
   - Role-based access control

3. **Plugin System**
   - Custom emotion models
   - Third-party lorebook generators
   - Alternative LLM backends

4. **Mobile Apps**
   - React Native or Flutter
   - Same backend API
   - Offline-first architecture

5. **Model Management UI**
   - In-app model downloader
   - Model switching without restart
   - Quantization on-the-fly

---

## Developer Notes

### Running Services Individually

**Backend:**
```bash
cd backend
npm start
# Runs on http://localhost:9000
```

**Inference:**
```bash
cd inference
python main.py
# Runs on http://localhost:9001
```

**Frontend (development):**
```bash
cd frontend
npm run build:watch
# Recompiles SCSS on changes
```

### Environment Variables

**Backend (`.env`):**
```
PORT=9000
INFERENCE_URL=http://127.0.0.1:9001
SESSION_SECRET=<random-secret>
```

**Inference (`.env`):**
```
INFERENCE_HOST=127.0.0.1
INFERENCE_PORT=9001
LLM_MODEL_PATH=models/MN-Violet-Lotus-12B.Q4_K_M.gguf
EMOTION_MODEL_PATH=models/roberta_emotions_onnx
LLM_N_GPU_LAYERS=-1
LLM_N_CTX=4096
```

### Adding New API Routes

1. Create route file in `backend/src/routes/`
2. Import in `backend/src/server.js`
3. Mount with `app.use('/api/endpoint', router)`
4. Add authentication middleware if needed
5. Update this documentation

### Adding New Python Processors

1. Create processor in `inference/processors/`
2. Import in `llm_processor.py` or `main.py`
3. Integrate into inference pipeline
4. Add tests (future enhancement)

---

## Questions?

See [FAQ.md](FAQ.md) or [open an issue](https://github.com/YOUR_USERNAME/oread/issues).
