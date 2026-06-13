import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
import tempfile
import os
import numpy as np

# Load whisper model once
model = whisper.load_model("base")

SAMPLE_RATE = 16000
recording = []
is_recording = False

def start_recording():
    print("I am recording ")
    global recording, is_recording
    recording = []
    is_recording = True

    def callback(indata, frames, time, status):
        if is_recording:
            recording.append(indata.copy())

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=callback
    )
    stream.start()
    return stream

def stop_recording(stream):
    global is_recording
    is_recording = False
    stream.stop()
    stream.close()

    if not recording:
        return None

    audio = np.concatenate(recording, axis=0)
    tmp = tempfile.NamedTemporaryFile(
        suffix=".wav", delete=False
    )
    audio_int16 = (audio * 32767).astype(np.int16)
    wav.write(tmp.name, SAMPLE_RATE, audio_int16)
    return tmp.name

def transcribe(audio_path):
    print(" I am transcribing ")
    if not audio_path:
        print("No audio to transcribe")
        return None
    try:
        result = model.transcribe(audio_path)
        os.unlink(audio_path)
        return result["text"].strip()
    except Exception as e:
        print("Exception during transcription:", e)
        return None