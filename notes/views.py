from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import speech_recognition as sr
import os
import subprocess
from django.shortcuts import render


def index(request):
    """
    Render the main HTML page.
    """
    return render(request, 'notes/index.html')


@csrf_exempt
def speech_to_text(request):
    """
    Handle audio file upload and convert speech to text.
    Supports multiple languages based on user selection.
    """
    if request.method == 'POST':
        audio_file = request.FILES.get('audio')  # Get the uploaded audio file
        language = request.POST.get('language', 'en-US')  # Get selected language, default to English

        if not audio_file:
            return JsonResponse({'error': 'No audio file provided'}, status=400)

        # Define temporary file paths
        audio_path = 'temp_audio.webm'
        wav_path = 'temp_audio.wav'

        try:
            # Save the uploaded audio file
            with open(audio_path, 'wb+') as temp_file:
                for chunk in audio_file.chunks():
                    temp_file.write(chunk)

            # Convert .webm to .wav using FFmpeg
            subprocess.run(['ffmpeg', '-i', audio_path, wav_path], check=True)

            # Initialize recognizer and transcribe audio
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio = recognizer.record(source)  # Read the entire audio file
                text = recognizer.recognize_google(audio, language=language)  # Use selected language

        except sr.UnknownValueError:
            text = "Could not understand the audio."
        except sr.RequestError as e:
            text = f"Google Speech Recognition error: {e}"
        except subprocess.CalledProcessError:
            return JsonResponse({'error': 'Error converting audio file.'}, status=500)
        finally:
            # Clean up temporary files
            for file in [audio_path, wav_path]:
                if os.path.exists(file):
                    os.remove(file)

        return JsonResponse({'text': text})

    # Return default message for GET or unsupported methods
    return JsonResponse({'message': 'Welcome to the Voice to Text API'})