import os
import tempfile
import requests  # New dependency for downloading from URL
import librosa
import numpy as np
from mutagen.mp3 import MP3
from mutagen.wave import WAVE

class ForensicService:
    def __init__(self):
        # No longer need AWS keys here, as we receive a pre-authorized URL
        pass

    def analyze_audio(self, file_url: str, original_filename: str = "unknown") -> dict:
        """
        Main entry point. 
        1. Downloads file from the Presigned URL.
        2. Runs forensics.
        3. Cleans up.
        """
        temp_path = None
        try:
            # 1. Download to Temp File from URL
            print(f"⬇️ Downloading from Presigned URL...")
            temp_path = self._download_from_url(file_url)

            # 2. Run Analysis
            print(f"🔍 Analyzing Forensics for: {original_filename}")
            report = self._analyze_signal_integrity(temp_path)
            
            # Add context to the report
            report['source_file'] = original_filename
            
            return report

        except Exception as e:
            print(f"❌ Forensic Error: {str(e)}")
            return {
                "error": str(e),
                "is_suspicious": False,
                "risk_score": 0,
                "flags": [f"Analysis failed: {str(e)}"]
            }
        
        finally:
            # 3. Cleanup (Critical for worker memory management)
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
                print("🧹 Temp file cleaned up.")

    def _download_from_url(self, url: str) -> str:
        """Helper to safely download file from URL to local temp storage."""
        # Attempt to guess extension from URL, default to .mp3 if hidden
        suffix = ".mp3"
        if ".wav" in url.lower().split('?')[0]: # Split to ignore query params
            suffix = ".wav"
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            # Stream download to avoid loading huge files into RAM
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=8192): 
                    tmp.write(chunk)
            return tmp.name

    def _analyze_signal_integrity(self, file_path: str) -> dict:
        """
        The Core Forensic Logic (Metadata + Signal Processing)
        """
        report = {
            "is_suspicious": False,
            "risk_score": 0,
            "flags": [],
            "details": {}
        }

        # --- A. METADATA CHECK ---
        try:
            audio = None
            # Mutagen requires a file path, which we now have (temp_path)
            if file_path.endswith('.mp3'):
                audio = MP3(file_path)
            elif file_path.endswith('.wav'):
                audio = WAVE(file_path)
            
            if audio:
                # Convert all metadata to string for searching
                meta_str = str(audio.pprint()).lower()
                suspicious_tools = ['lavf', 'adobe', 'audacity', 'soundforge', 'pro tools']
                found = [t for t in suspicious_tools if t in meta_str]
                
                if found:
                    report['flags'].append(f"Metadata indicates editing software: {', '.join(found)}")
                    report['risk_score'] += 30
        except Exception as e:
            report['details']['metadata_error'] = str(e)

        # --- B. SILENCE / SPLICING DETECTION ---
        try:
            # Load audio with librosa (sr=None ensures native sampling rate)
            y, sr = librosa.load(file_path, sr=None)
            
            # Short-Term Energy Calculation
            frame_length = 2048
            hop_length = 512
            
            # Calculate energy using list comprehension (efficient for short clips)
            energy = np.array([
                sum(abs(y[i:i+frame_length]**2))
                for i in range(0, len(y), hop_length)
            ])
            
            # Detect "Digital Zero" (Absolute Silence = Splicing Artifact)
            # Normal recordings have noise floor; absolute 0 often means cut/paste.
            zero_energy_frames = np.where(energy < 1e-9)[0]
            
            if len(zero_energy_frames) > 5:
                report['flags'].append("Artificial digital silence detected (High probability of splicing)")
                report['risk_score'] += 40
                report['details']['silent_frames'] = int(len(zero_energy_frames))
        
        except Exception as e:
            report['details']['signal_error'] = str(e)

        # --- C. FINAL SCORING ---
        if report['risk_score'] > 50:
            report['is_suspicious'] = True

        return report

# Singleton instance
forensic_analyzer = ForensicService()