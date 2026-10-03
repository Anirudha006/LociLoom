"""
LociLoom Text-To-Speech (TTS) Engine
Provides resilient audio narration for memory palace stories.
Attempts gTTS generation with graceful offline browser speechSynthesis fallback.
Audio is strictly optional; errors are caught and never crash the application.
"""
import io
import html
from typing import Optional, Tuple

_GTTS_AVAILABLE = False
try:
    from gtts import gTTS
    _GTTS_AVAILABLE = True
except ImportError:
    _GTTS_AVAILABLE = False

def generate_speech_audio(text: str, lang: str = "en") -> Tuple[Optional[bytes], str]:
    """
    Attempts to generate MP3 audio bytes using gTTS.
    Returns: (audio_bytes or None, status_message)
    """
    if not text or not text.strip():
        return (None, "Empty text provided.")

    if not _GTTS_AVAILABLE:
        return (None, "gTTS library is not installed; using browser speech synthesis fallback.")

    # Map language codes
    lang_code = "en"
    if lang.lower().startswith("hi"):
        lang_code = "hi"
    elif lang.lower().startswith("kn"):
        lang_code = "kn"

    try:
        clean_text = text.replace("**", "").replace("*", "").strip()[:800] # Safe speech limit
        tts = gTTS(text=clean_text, lang=lang_code, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return (fp.read(), "Audio generated successfully.")
    except Exception as e:
        # Offline or connection error
        return (None, f"Offline mode: falling back to browser speech synthesis ({str(e)}).")

def get_browser_speech_html(text: str, voice_speed: float = 1.0, lang: str = "en") -> str:
    """
    Returns a lightweight, safe HTML/JavaScript button that invokes the client's
    built-in browser SpeechSynthesis API. Works 100% offline with zero dependencies.
    """
    clean_text = html.escape(text.replace("\n", " ").replace("'", "\\'").replace('"', '\\"'))
    lang_tag = "en-US"
    if lang.startswith("hi"):
        lang_tag = "hi-IN"
    elif lang.startswith("kn"):
        lang_tag = "kn-IN"

    return f"""
    <div style="margin: 10px 0;">
        <button id="speak-btn" onclick="speakStory()" style="
            background-color: #5B6CFF;
            color: white;
            border: none;
            padding: 8px 18px;
            font-size: 14px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 2px 6px rgba(91, 108, 255, 0.3);
        ">
            🔊 Read Aloud (Browser Voice)
        </button>
        <button id="stop-btn" onclick="window.speechSynthesis.cancel()" style="
            background-color: #F4F6FB;
            color: #1F2937;
            border: 1px solid #D1D5DB;
            padding: 8px 14px;
            font-size: 14px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            margin-left: 8px;
        ">
            ⏹️ Stop
        </button>
        <script>
            function speakStory() {{
                if (!('speechSynthesis' in window)) {{
                    alert('Browser speech synthesis is not supported on this device.');
                    return;
                }}
                window.speechSynthesis.cancel();
                const utter = new SpeechSynthesisUtterance("{clean_text}");
                utter.rate = {voice_speed};
                utter.lang = "{lang_tag}";
                window.speechSynthesis.speak(utter);
            }}
        </script>
    </div>
    """
