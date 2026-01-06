import whisper
import pyaudio
import wave
import numpy as np
import threading
import queue
import time
import requests
from datetime import datetime

# Configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
SILENCE_THRESHOLD = 500  # Adjust based on your environment
WEBHOOK_URL = "http://localhost:5678/webhook-test/sst"
PAUSE_DURATION = 1.5  # Seconds of silence before processing speech

class RealtimeSpeechToText:
    def __init__(self, model_size="base"):
        """
        Initialize the Whisper model
        model_size options: tiny, base, small, medium, large
        """
        print(f"Loading Whisper {model_size} model...")
        self.model = whisper.load_model(model_size)
        print("Model loaded successfully!")
        
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.is_speaking = False
        self.speech_frames = []
        self.silence_chunks = 0
        
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
        
        silence_chunks_threshold = int(RATE / CHUNK * PAUSE_DURATION)
        
        while self.is_recording:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_np = np.frombuffer(data, dtype=np.int16)
                audio_level = np.abs(audio_np).mean()
                
                # Check if there's sound above threshold
                if audio_level > SILENCE_THRESHOLD:
                    if not self.is_speaking:
                        print("🎤 Speech detected...")
                        self.is_speaking = True
                        self.speech_frames = []
                    
                    self.speech_frames.append(data)
                    self.silence_chunks = 0
                    
                elif self.is_speaking:
                    # Still in speaking mode but current chunk is silent
                    self.speech_frames.append(data)
                    self.silence_chunks += 1
                    
                    # Check if silence duration reached
                    if self.silence_chunks >= silence_chunks_threshold:
                        # Process the accumulated speech
                        audio_data = b''.join(self.speech_frames)
                        self.audio_queue.put(audio_data)
                        
                        # Reset
                        self.is_speaking = False
                        self.speech_frames = []
                        self.silence_chunks = 0
                        print("⏸ Pause detected, processing...\n")
                    
            except Exception as e:
                print(f"Error recording: {e}")
                break
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("* Recording stopped")
    
    def send_to_webhook(self, text):
        """Send transcribed text to n8n webhook"""
        try:
            payload = {
                "message": text,
                "time": datetime.now().isoformat()
            }
            response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"✓ Sent to webhook: {text}\n")
            else:
                print(f"✗ Webhook error: {response.status_code}\n")
        except Exception as e:
            print(f"✗ Failed to send to webhook: {e}\n")
    
    def process_audio(self):
        """Process audio chunks and transcribe"""
        while self.is_recording or not self.audio_queue.empty():
            try:
                audio_data = self.audio_queue.get(timeout=1)
                
                # Convert bytes to numpy array
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Transcribe using Whisper
                result = self.model.transcribe(audio_np, fp16=False, language='en')
                text = result['text'].strip()
                
                if text:
                    print(f"📝 Transcription: {text}")
                    self.send_to_webhook(text)
                    
            except queue.Empty:
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