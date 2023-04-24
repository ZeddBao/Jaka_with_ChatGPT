import whisper

model = whisper.load_model("base")
result = model.transcribe(r"temp.mp3")
print(result["text"])
