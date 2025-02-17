import whisper
import torch

def transcribe_audio(audio_path, output_path):

    #torch.cuda.init()
    #device = "cuda"

    #model = whisper.load_model("large-v3-turbo", device= device) If you have CUDA
    
    model = whisper.load_model("large-v3-turbo")
    
    # Transcribe the audio
    result = model.transcribe(audio_path)
    transcription = result["text"]
    
    # Save transcription to file
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(transcription)
    
    # Return the transcription text for immediate use
    return transcription
