import noisereduce as nr
from scipy.io import wavfile
from noisereduce.generate_noise import band_limited_noise
import numpy as np


wav_loc = "STRIPS2_0+1_20150520_053500.wav"
rate, data = wavfile.read(wav_loc)

noise_len = 2
noise = band_limited_noise(
    min_freq=2000, max_freq=12000, samples = len(data), samplerate = rate) * 10

noise_stereo = np.array([noise,noise])
noise_stereo = np.transpose(noise_stereo)

noise_clip = noise[:rate * noise_len]
audio_clip_band_limited = data + noise_stereo

denoised = nr.reduce_noise(
    y = np.transpose(audio_clip_band_limited),
    sr = rate,
    y_noise = data[0:(24000*10),0], #noise_clip,
    stationary = True,
    tmp_folder = "temp_folder"
)

reduced = np.int16(denoised / np.max(np.abs(denoised)) * 32767 )

wavfile.write("clean_STRIPS2_0+1_20150520_053500.wav", rate, np.transpose(reduced) )
