import whisper
import pyaudio
import wave
import numpy as np
import threading
import queue
import time
import requests
import json
from datetime import datetime

# Configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5  # Process audio every 5 seconds
SILENCE_THRESHOLD = 500  # Adjust based on your environment

class RealtimeSpeechToText:
    def __init__(self, model_size="base", webhook_url=None):
        """
        Initialize the Whisper model
        model_size options: tiny, base, small, medium, large
        webhook_url: URL to send transcribed text (optional)
        """
        print(f"Loading Whisper {model_size} model...")
        self.model = whisper.load_model(model_size)
        print("Model loaded successfully!")
        
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.webhook_url = webhook_url
        
        if self.webhook_url:
            print(f"Webhook enabled: {self.webhook_url}\n")
        
    def record_audio(self):
        """Record audio from microphone"""
        p = pyaudio.PyAudio()
        
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)
        
        print("* Recording started. Speak into your microphone...")
        print("* Press Ctrl+C to stop\n")
        
        frames = []
        frame_count = 0
        target_frames = int(RATE / CHUNK * RECORD_SECONDS)
        
        while self.is_recording:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
                frame_count += 1
                
                # Process audio chunk every RECORD_SECONDS
                if frame_count >= target_frames:
                    audio_data = b''.join(frames)
                    self.audio_queue.put(audio_data)
                    frames = []
                    frame_count = 0
                    
            except Exception as e:
                print(f"Error recording: {e}")
                break
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("* Recording stopped")
    
    def process_audio(self):
        """Process audio chunks and transcribe"""
        while self.is_recording or not self.audio_queue.empty():
            try:
                audio_data = self.audio_queue.get(timeout=1)
                
                # Convert bytes to numpy array
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Check if there's actual sound (not silence)
                if np.abs(audio_np).mean() * 32768 > SILENCE_THRESHOLD:
                    print("Processing audio...")
                    
                    # Transcribe using Whisper")
                        
                        # Send to webhook if configured
                        if self.webhook_url:
                            self.send_to_webhook(text)
                        print(
                    result = self.model.transcribe(audio_np, fp16=False, language='en')
                    text = result['text'].strip()
                    
                    if text:
                        print(f"Transcription: {text}\n")
                else:
                    print("Silence detected, skipping...\n")
                    
         end_to_webhook(self, text):
        """Send transcribed text to webhook"""
        try:
            payload = {
                "text": text,
                "timestamp": datetime.now().isoformat(),
                "source": "whisper-realtime-stt"
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✓ Sent to webhook successfully")
            else:
                print(f"⚠ Webhook response: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⚠ Webhook timeout")
      Configure your webhook URL here (n8n, Zapier, Make.com, or any custom endpoint)
    # Example: "https://your-n8n-instance.com/webhook/speech-to-text"
    WEBHOOK_URL = None  # Set to your webhook URL or leave None to disable
    
    # Prompt for webhook URL if not set
    if not WEBHOOK_URL:
        webhook_input = input("Enter webhook URL (or press Enter to skip): ").strip()
        if webhook_input:
            WEBHOOK_URL = webhook_input
    
    # Initialize with base model (you can change to: tiny, base, small, medium, large)
    stt = RealtimeSpeechToText(model_size="base", webhook_url=WEBHOOK_URL
    
    def s   except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing audio: {e}")
    
    def start(self):
        """Start real-time transcription"""
        self.is_recording = True
        
        # Start recording thread
        record_thread = threading.Thread(target=self.record_audio)
        record_thread.start()
        
        # Start processing thread
        process_thread = threading.Thread(target=self.process_audio)
        process_thread.start()
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\nStopping transcription...")
            self.is_recording = False
            record_thread.join()
            process_thread.join()
            print("Done!")

if __name__ == "__main__":
    # Initialize with base model (you can change to: tiny, base, small, medium, large)
    stt = RealtimeSpeechToText(model_size="base")
    stt.start()
