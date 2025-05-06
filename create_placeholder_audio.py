"""
Create a placeholder audio file for the farewell feature.
This script generates a simple tone as MP3 to serve as a placeholder.
"""

import os
from pathlib import Path
import numpy as np
from scipy.io import wavfile
try:
    import simpleaudio as sa
except ImportError:
    sa = None

def create_beep_sound(filename, duration=1.0, freq=440.0, sample_rate=44100):
    """Create a simple beep sound and save as WAV file."""
    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Generate sine wave
    note = np.sin(freq * 2 * np.pi * t)
    
    # Ensure audio data is in the range [-1, 1]
    audio = note * 0.5
    
    # Convert to 16-bit data
    audio = (audio * 32767).astype(np.int16)
    
    # Save file
    wavfile.write(filename, sample_rate, audio)
    print(f"✓ Created audio file: {filename}")

def main():
    """Main function to create the audio file."""
    # Create the directory if it doesn't exist
    os.makedirs('assets/farewell', exist_ok=True)
    
    # File paths
    wav_file = 'assets/farewell/postNleft.wav'
    mp3_file = 'assets/farewell/postNleft.mp3'
    
    # Create WAV file
    create_beep_sound(wav_file, duration=1.0, freq=880.0)
    
    # Try to convert WAV to MP3 if ffmpeg is available
    try:
        import subprocess
        result = subprocess.run(
            ['ffmpeg', '-i', wav_file, '-codec:a', 'libmp3lame', '-qscale:a', '2', mp3_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            print(f"✓ Converted to MP3: {mp3_file}")
            # Remove WAV file
            try:
                os.remove(wav_file)
                print(f"✓ Removed temporary WAV file")
            except Exception as e:
                print(f"! Error removing WAV file: {e}")
        else:
            print(f"! Error converting to MP3: {result.stderr.decode()}")
            print("! Using WAV file instead")
            # Rename WAV to MP3 as fallback
            os.rename(wav_file, mp3_file)
            print(f"✓ Renamed WAV to MP3 as fallback")
    except Exception as e:
        print(f"! Error with ffmpeg: {e}")
        print("! Using WAV file instead")
        # Rename WAV to MP3 as fallback
        os.rename(wav_file, mp3_file)
        print(f"✓ Renamed WAV to MP3 as fallback")
    
    print("\nNOTE: This is a placeholder audio file. Replace it with your desired audio.")
    print(f"Audio file created at: {mp3_file}")

if __name__ == "__main__":
    main()