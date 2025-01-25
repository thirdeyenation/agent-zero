import librosa
import librosa.display
import numpy as np

# Generate a sine wave
sr = 22050
duration = 5
freq = 440
t = np.linspace(0, duration, int(sr * duration), endpoint=False)
sine_wave = 0.5 * np.sin(2 * np.pi * freq * t)

# Extract MFCCs
mfccs = librosa.feature.mfcc(y=sine_wave, sr=sr, n_mfcc=13)

print(f"MFCCs shape: {mfccs.shape}")