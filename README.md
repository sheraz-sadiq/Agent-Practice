# Real-time Speech-to-Text with Whisper

This project implements real-time speech-to-text transcription using OpenAI's Whisper model in a Docker container.

## Features

- Real-time audio capture from microphone
- Automatic transcription using Whisper
- Configurable model size (tiny, base, small, medium, large)
- Silence detection to skip empty audio
- Dockerized for easy deployment

## Setup and Run

### Option 1: Run with Docker

1. **Build the Docker image:**
```bash
docker build -t whisper-stt .
```

2. **Run the container (Linux/Mac):**
```bash
docker run -it --rm --device /dev/snd whisper-stt
```

3. **Run the container (Windows):**
Note: Docker on Windows has limited audio support. It's recommended to run locally instead.

### Option 2: Run Locally (Recommended for Windows)

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the script:**
```bash
python realtime_stt.py
```

## Configuration

Edit `realtime_stt.py` to customize:

- **Model size:** Change `model_size` in `RealtimeSpeechToText("base")` to:
  - `tiny` - Fastest, least accurate
  - `base` - Good balance (default)
  - `small` - Better accuracy
  - `medium` - High accuracy
  - `large` - Best accuracy, slowest

- **Processing interval:** Adjust `RECORD_SECONDS` (default: 5 seconds)
- **Silence threshold:** Adjust `SILENCE_THRESHOLD` based on your environment

## Usage

1. Start the script
2. Speak into your microphone
3. Transcriptions will appear in real-time
4. Press Ctrl+C to stop

## Requirements

- Python 3.8+
- Microphone access
- ~1GB disk space for model
- CUDA GPU (optional, for faster processing)

## Troubleshooting

**No audio input:**
- Check microphone permissions
- Verify microphone is set as default input device

**Slow transcription:**
- Use a smaller model (tiny or base)
- Enable GPU support if available

**PyAudio installation issues on Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```
