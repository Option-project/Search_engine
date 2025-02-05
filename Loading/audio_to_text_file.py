import whisper
import torch

def transcribe_audio(audio_path, output_path):

    #torch.cuda.init()
    #device = "cuda"

    #model = whisper.load_model("large-v3-turbo", device= device) If you have CUDA
    
    model = whisper.load_model("large-v3-turbo")
    
    result = model.transcribe(audio_path)
    transcription = result["text"]

    with open(output_path, 'w') as file:
        file.write(transcription)
