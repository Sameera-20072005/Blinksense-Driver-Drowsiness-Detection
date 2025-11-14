import numpy as np
import wave

def create_alarm_sound():
    # Parameters
    sample_rate = 44100
    duration = 2.0  # 2 seconds
    
    # Create time array
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create alarm sound with multiple frequencies
    freq1 = 800  # Hz
    freq2 = 1200  # Hz
    
    # Generate alternating tones
    tone1 = np.sin(2 * np.pi * freq1 * t[:len(t)//2])
    tone2 = np.sin(2 * np.pi * freq2 * t[len(t)//2:])
    
    # Combine tones
    alarm = np.concatenate([tone1, tone2])
    
    # Add envelope to avoid clicks
    envelope = np.ones_like(alarm)
    fade_samples = int(0.1 * sample_rate)  # 0.1 second fade
    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
    
    alarm = alarm * envelope * 0.3  # Reduce volume
    
    # Convert to 16-bit integers
    alarm_int = (alarm * 32767).astype(np.int16)
    
    # Save as WAV file
    with wave.open('alarm.wav', 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(alarm_int.tobytes())
    
    print("Alarm sound created: alarm.wav")

if __name__ == "__main__":
    create_alarm_sound()