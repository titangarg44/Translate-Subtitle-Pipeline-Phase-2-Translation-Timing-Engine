# 🎬 AI Dubbing Pipeline — Phase 2: Translation & Timing Engine

An asynchronous FastAPI microservice that extracts audio from uploaded video files, transcribes spoken text using `faster-whisper`, translates dialogue across languages, and calculates timing/character metrics for AI dubbing voice sync.

---

## 📌 What's New in Phase 2

- **Cross-Lingual Translation:** Translates transcribed speech into any target language (e.g., Spanish, French, German, Japanese) using `deep-translator`.
- **Single-Payload Batch Processing:** Combines transcript segments into a unified payload for zero rate-limiting and instant translation.
- **Speech Duration & Timing Analysis:** Tracks character count per segment and evaluates character density against duration ($~17\text{ chars/sec}$) to flag dialogue segments that may require speech compression during dubbing synthesis.
- **Multilingual Subtitle Generation:** Automatically formats and exports translated `.srt` subtitle files (e.g., `video_es.srt`).
- **Flexible REST Endpoints:** Standalone transcription, standalone translation, and combined video-to-translated-transcript workflows.

---

## 📁 Repository Structure

```text
ai_dubber_p1/
├── .gitignore          # Ignores venv, pycache, media outputs, and temp files
├── README.md           # Project documentation
├── requirements.txt    # Project dependencies
├── main.py             # FastAPI routing and request schemas
├── core.py             # Audio extraction, Whisper transcription, and SRT builder
└── translator.py       # Batch translation engine and timing/character analyzer
```

---

## ⚙️ Prerequisites & Installation

### 1. Requirements
- **Python 3.10+**
- **FFmpeg:** Ensure FFmpeg is installed and added to your system PATH for audio extraction.

### 2. Setup Project & Virtual Environment
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-dubber-phase2.git
cd ai-dubber-phase2

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Running the API Server

Launch the development server using Uvicorn or Python directly:

```bash
python main.py
```
*Or via Uvicorn:*
```bash
uvicorn main:app --reload
```

The interactive API interface will be accessible at:
👉 **`http://127.0.0.1:8000/docs`**

---

## 🧪 REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/transcribe` | Extracts audio and generates timestamped transcription & `.srt` |
| `POST` | `/translate` | Translates raw JSON transcript segments with timing metrics |
| `POST` | `/transcribe-and-translate` | Ingests video, transcribes, translates, and returns translated `.srt` |

---

## 📊 Sample API Response (`POST /transcribe-and-translate`)

```json
{
  "filename": "interview.mp4",
  "target_lang": "es",
  "translated_srt_file": "interview.mp4_es.srt",
  "data": [
    {
      "start": 0.0,
      "end": 2.5,
      "duration": 2.5,
      "original_text": "Welcome to our AI dubbing project!",
      "translated_text": "¡Bienvenidos a nuestro proyecto de doblaje con IA!",
      "char_count": 51,
      "is_too_long": false
    },
    {
      "start": 3.0,
      "end": 4.0,
      "duration": 1.0,
      "original_text": "This is phase two of the pipeline.",
      "translated_text": "Esta es la fase dos de la canalización de procesamiento.",
      "char_count": 57,
      "is_too_long": true
    }
  ]
}
```

---

## 📄 License

Distributed under the MIT License.
