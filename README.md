Demo Link:
https://drive.google.com/file/d/1ekzIASPdSsE5UahkxbpwkamtgGKBLUgC/view?usp=drive_link
# 🔐 Emotion Cipher

**The world's first emotion-aware encryption system.**

Emotion Cipher combines AI emotion detection with AES-256 encryption to create messages that carry a hidden emotional fingerprint — a cryptographic signature of how you felt when you wrote them.

---

## ✨ Features

- 🧠 **AI Emotion Detection** — HuggingFace `j-hartmann/emotion-english-distilroberta-base` model
- 🔐 **AES-256-CBC Encryption** — Python `cryptography` library
- 🌊 **Emotion Aura Visualization** — Animated radial pulse based on detected emotion
- 📊 **Emotion Analytics Dashboard** — Donut, line, and bar charts via Chart.js
- ✍️ **Encryption Visualization** — Character-by-character transformation animation
- 📋 **Copy to Clipboard** — One-click copy for encrypted text and keys
- 🌙 **Dark Futuristic UI** — Orbitron + Share Tech Mono fonts, particle background
- 📱 **Fully Responsive** — Mobile-friendly design

---

## 📁 Project Structure

```
emotion-cipher/
├── frontend/
│   └── index.html          # Single-file full frontend (standalone)
├── backend/
│   ├── main.py             # FastAPI server
│   └── requirements.txt    # Python dependencies
└── README.md
```

---

## 🚀 Quick Start

### Option A — Standalone Frontend (No Backend Needed)

Just open `frontend/index.html` in a browser.

The frontend uses:
- **Web Crypto API** for AES-256-CBC encryption/decryption (native browser)
- **Anthropic Claude API** for emotion detection (via claude.ai embed)
- **Chart.js CDN** for dashboard charts
- **localStorage** for message history

---

### Option B — With Python Backend

#### 1. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### 2. Start the FastAPI server

```bash
uvicorn main:app --reload --port 8000
```

API will be live at: `http://localhost:8000`

#### 3. API Docs

Visit: `http://localhost:8000/docs`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/detect-emotion` | Detect emotions in text |
| POST | `/api/encrypt` | Encrypt + emotion detect |
| POST | `/api/decrypt` | Decrypt + recover emotions |
| POST | `/api/verify-signature` | Verify emotion signature |

### Encrypt Example

```bash
curl -X POST http://localhost:8000/api/encrypt \
  -H "Content-Type: application/json" \
  -d '{"message": "Feeling ecstatic about joining the new AI research team!"}'
```

**Response:**
```json
{
  "encrypted_payload": "EC_v1:9x@T!aZkP#...base64...:EMSIG_abc123",
  "key": "auto-generated-key",
  "emotion_signature": "EMSIG_abc123",
  "emotions": [
    {"name": "joy", "score": 0.85},
    {"name": "anxiety", "score": 0.35}
  ],
  "dominant_emotion": "joy"
}
```

### Decrypt Example

```bash
curl -X POST http://localhost:8000/api/decrypt \
  -H "Content-Type: application/json" \
  -d '{"encrypted_payload": "EC_v1:...", "key": "your-key"}'
```

---

## 🎨 Emotion Color Theme

| Emotion | Color | Emoji |
|---------|-------|-------|
| Joy | `#ffcc00` | 😄 |
| Sadness | `#4488ff` | 😢 |
| Anger | `#ff3344` | 😡 |
| Fear | `#aa44ff` | 😨 |
| Surprise | `#00ffaa` | 😲 |
| Disgust | `#88cc00` | 🤢 |
| Anxiety | `#ff8800` | 😰 |
| Love | `#ff006a` | ❤️ |
| Neutral | `#7ab8d4` | 😐 |

---

## 🔐 Encryption Format

```
EC_v1:{AES-256-CBC-Base64}:{EMSIG_EmotionSignature}
```

- **EC_v1** — Version prefix
- **AES-256-CBC-Base64** — IV prepended to ciphertext, base64 encoded
- **EMSIG_** — Base64-encoded emotion fingerprint with timestamp

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML5 + CSS3 + Vanilla JS |
| Encryption (Frontend) | Web Crypto API (AES-256-CBC) |
| Encryption (Backend) | Python `cryptography` (AES-256-CBC + PBKDF2) |
| AI Emotion Detection | HuggingFace `distilroberta-base` |
| Charts | Chart.js 4 |
| Animations | CSS keyframes + Canvas particles |
| Backend Framework | FastAPI + Uvicorn |
| Fonts | Orbitron, Rajdhani, Share Tech Mono |

---

## 📝 Sample Input/Output

### Example 1

**Input:**
> "Feeling ecstatic about joining the new AI research team, though a bit anxious about the deadlines ahead."

**Encrypted Output:**
```
EC_v1:base64EncodedCiphertext==:EMSIG_am95OjgyOmFueGlldHk6MzU...
```
**Detected Emotion:** Joy (82%) + Anxiety (35%)

---

### Example 2

**Input:**
> "I can't believe I failed that test again. I'm so disappointed and frustrated right now."

**Encrypted Output:**
```
EC_v1:base64EncodedCiphertext==:EMSIG_c2FkbmVzczo3Njphbmdlcjo1OA...
```
**Detected Emotion:** Sadness (76%) + Anger (58%)

---

## 📜 License

MIT — Feel free to fork, modify, and deploy.

---

*Built with ❤️ and encrypted with emotion.*
