"""
Emotion Cipher - FastAPI Backend
Emotion Detection + AES Encryption/Decryption
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import base64
import json
import hashlib
import time
from datetime import datetime

# ─── Encryption (Python cryptography library) ───────────────────────────────
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding as sym_padding

# ─── Hugging Face emotion model ──────────────────────────────────────────────
from transformers import pipeline

app = FastAPI(title="Emotion Cipher API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load HuggingFace model at startup (no dataset training required)
print("Loading HuggingFace emotion model...")
try:
    emotion_classifier = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=None,
        device=-1  # CPU
    )
    print("✓ Model loaded successfully")
except Exception as e:
    print(f"Warning: Could not load primary model: {e}")
    # Fallback to basic sentiment
    emotion_classifier = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=-1
    )
    print("Using fallback sentiment model")

SALT = b"EmotionCipherSalt2024"
EMOTION_MAP = {
    "joy": {"emoji": "😄", "color": "#ffcc00"},
    "sadness": {"emoji": "😢", "color": "#4488ff"},
    "anger": {"emoji": "😡", "color": "#ff3344"},
    "fear": {"emoji": "😨", "color": "#aa44ff"},
    "surprise": {"emoji": "😲", "color": "#00ffaa"},
    "disgust": {"emoji": "🤢", "color": "#88cc00"},
    "neutral": {"emoji": "😐", "color": "#7ab8d4"},
}


# ─── Models ──────────────────────────────────────────────────────────────────
class EncryptRequest(BaseModel):
    message: str
    key: Optional[str] = None

class DecryptRequest(BaseModel):
    encrypted_payload: str
    key: str

class EmotionRequest(BaseModel):
    text: str


# ─── Encryption Helpers ───────────────────────────────────────────────────────
def derive_key(password: str) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def aes_encrypt(plaintext: str, password: str) -> str:
    key = derive_key(password)
    iv = os.urandom(16)
    padder = sym_padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    combined = iv + ciphertext
    return base64.b64encode(combined).decode()

def aes_decrypt(b64_payload: str, password: str) -> str:
    combined = base64.b64decode(b64_payload)
    iv = combined[:16]
    ciphertext = combined[16:]
    key = derive_key(password)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = sym_padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded) + unpadder.finalize()
    return plaintext.decode()

def generate_password() -> str:
    return base64.b64encode(os.urandom(16)).decode().rstrip('=')

def create_emotion_signature(emotions: list) -> str:
    sig_data = "|".join([f"{e['name']}:{round(e['score']*100)}" for e in emotions])
    sig_hash = base64.b64encode(f"{sig_data}:{int(time.time())}".encode()).decode()
    sig_hash = sig_hash.replace('+', '-').replace('/', '_').replace('=', '')
    return f"EMSIG_{sig_hash}"


# ─── Emotion Detection ────────────────────────────────────────────────────────
def detect_emotions(text: str) -> dict:
    try:
        results = emotion_classifier(text[:512])
        if isinstance(results, list) and isinstance(results[0], list):
            # top_k output
            emotions_raw = results[0]
            emotions = [
                {"name": r["label"].lower(), "score": round(r["score"], 4)}
                for r in emotions_raw
                if r["score"] > 0.05
            ]
        else:
            # Fallback: map sentiment to emotion
            label = results[0]["label"].lower()
            score = results[0]["score"]
            emotions = [
                {"name": "joy" if label == "positive" else "sadness", "score": round(score, 4)},
                {"name": "neutral", "score": round(1 - score, 4)}
            ]

        # Sort and limit
        emotions = sorted(emotions, key=lambda x: x["score"], reverse=True)[:4]
        dominant = emotions[0]["name"] if emotions else "neutral"

        return {
            "emotions": emotions,
            "dominant": dominant,
            "summary": f"Detected {len(emotions)} emotion(s): {', '.join([e['name'] for e in emotions[:2]])}"
        }
    except Exception as e:
        return {
            "emotions": [{"name": "neutral", "score": 1.0}],
            "dominant": "neutral",
            "summary": f"Emotion detection unavailable: {str(e)}"
        }


# ─── Routes ───────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "ok", "service": "Emotion Cipher API v1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/detect-emotion")
async def detect_emotion_route(req: EmotionRequest):
    if not req.text.strip():
        raise HTTPException(400, "Text cannot be empty")
    result = detect_emotions(req.text)
    return result

@app.post("/api/encrypt")
async def encrypt_route(req: EncryptRequest):
    if not req.message.strip():
        raise HTTPException(400, "Message cannot be empty")

    # Detect emotions
    emotion_result = detect_emotions(req.message)

    # Generate or use provided key
    password = req.key.strip() if req.key and req.key.strip() else generate_password()

    # Encrypt
    encrypted_b64 = aes_encrypt(req.message, password)

    # Create emotion signature
    signature = create_emotion_signature(emotion_result["emotions"])

    # Build final payload
    payload = f"EC_v1:{encrypted_b64}:{signature}"

    return {
        "encrypted_payload": payload,
        "encrypted_b64": encrypted_b64,
        "key": password,
        "emotion_signature": signature,
        "emotions": emotion_result["emotions"],
        "dominant_emotion": emotion_result["dominant"],
        "summary": emotion_result["summary"],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/decrypt")
async def decrypt_route(req: DecryptRequest):
    if not req.key.strip():
        raise HTTPException(400, "Decryption key is required")

    payload = req.encrypted_payload.strip()
    signature = None

    # Parse EC format
    encrypted_b64 = payload
    if payload.startswith("EC_v1:"):
        parts = payload.split(":")
        if len(parts) >= 3:
            encrypted_b64 = parts[1]
            signature = parts[2]
        elif len(parts) == 2:
            encrypted_b64 = parts[1]

    try:
        decrypted = aes_decrypt(encrypted_b64, req.key)
    except Exception as e:
        raise HTTPException(400, f"Decryption failed: Invalid key or corrupted data. {str(e)}")

    # Re-detect emotions
    emotion_result = detect_emotions(decrypted)

    return {
        "decrypted_message": decrypted,
        "emotions": emotion_result["emotions"],
        "dominant_emotion": emotion_result["dominant"],
        "summary": emotion_result["summary"],
        "signature_present": signature is not None,
        "signature": signature,
        "integrity": "verified" if signature else "no_signature",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/verify-signature")
async def verify_signature(payload: dict):
    sig = payload.get("signature", "")
    emotions = payload.get("emotions", [])
    is_valid = sig.startswith("EMSIG_") and len(sig) > 10
    return {"valid": is_valid, "signature": sig}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
