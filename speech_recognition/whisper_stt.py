import whisper
from pydub import AudioSegment
import speech_recognition as sr
import os
import io

def record_audio():
    r = sr.Recognizer()

    r.dynamic_energy_threshold = False
    r.energy_threshold = 400

    with sr.Microphone() as source:
        try:
            audio = r.listen(source, timeout=5.0)

        except sr.WaitTimeoutError:
            audio = 0

        if audio:
            data = io.BytesIO(audio.get_wav_data())
            audio_clip = AudioSegment.from_file(data)
            filename = os.path.join(f"temp_speech.wav")
            audio_clip.export(filename, format="wav")

record_audio()

model = whisper.load_model("base")

# load audio and pad/trim it to fit 30 seconds
audio = whisper.load_audio("temp_speech.wav")
audio = whisper.pad_or_trim(audio)

# make log-Mel spectrogram and move to the same device as the model
mel = whisper.log_mel_spectrogram(audio).to(model.device)

# detect the spoken language
_, probs = model.detect_language(mel)
detected_lang = max(probs, key=probs.get)
print(detected_lang)

def transcribe():
    if detected_lang == "en":
        options = whisper.DecodingOptions(fp16=False)
        result = whisper.decode(model, mel, options)
        return result
    else:
        return 0

result = transcribe()

os.remove("temp_speech.wav")

def transcribed_text(result):
    try:
        return result.text
    except:
        return 0

print(transcribed_text(result))