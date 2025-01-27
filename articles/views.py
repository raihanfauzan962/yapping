import os
import tempfile
import whisper
from difflib import SequenceMatcher
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Article, UserRecording
from .forms import UserRecordingForm
from gtts import gTTS  # Import gTTS for text-to-speech functionality

def article_list(request):
    """Display all articles."""
    articles = Article.objects.filter(is_published=True)
    return render(request, 'articles/article_list.html', {'articles': articles})

def article_detail(request, pk):
    """Display the detailed view of an article."""
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'articles/article_detail.html', {'article': article})

def calculate_pronunciation_score(transcript, article_content):
    """
    Calculate the pronunciation score based on the similarity
    between the transcript and the article content.
    """
    transcript_words = transcript.lower().split()
    article_words = article_content.lower().split()

    # Calculate the similarity ratio
    matcher = SequenceMatcher(None, article_words, transcript_words)
    similarity = matcher.ratio()

    # Convert similarity to a percentage score (0-100%) and round to the nearest whole number
    score = round(similarity * 100)
    return score

def generate_feedback(transcript, article_content):
    """
    Generate feedback identifying incorrect words and suggesting corrections.
    Also creates highlighted transcript and article content with errors and corrections.
    """
    transcript_words = transcript.lower().split()
    article_words = article_content.lower().split()

    matcher = SequenceMatcher(None, article_words, transcript_words)
    feedback = []
    highlighted_transcript = []
    highlighted_article = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            # Feedback for replacements
            feedback.append(f"Replace: {' '.join(transcript_words[j1:j2])} -> {' '.join(article_words[i1:i2])}")
            # Highlight errors in transcript (red) and corrections in article content (green)
            highlighted_transcript.append(f"<span style='color: red;'>{' '.join(transcript_words[j1:j2])}</span>")
            highlighted_article.append(f"<span style='color: green;'>{' '.join(article_words[i1:i2])}</span>")
        elif tag == 'delete':
            # Feedback for missing words
            feedback.append(f"Missing: {' '.join(article_words[i1:i2])}")
            # Highlight missing words in article content (green)
            highlighted_article.append(
                f"<span style='color: green;' onclick='playTTS(\"{' '.join(article_words[i1:i2])}\")'>{' '.join(article_words[i1:i2])}</span>"
            )
        elif tag == 'insert':
            # Feedback for extra words
            feedback.append(f"Extra: {' '.join(transcript_words[j1:j2])}")
            # Highlight extra words in transcript (red)
            highlighted_transcript.append(f"<span style='color: red;'>{' '.join(transcript_words[j1:j2])}</span>")
        else:
            # Add correctly matched words without styling
            highlighted_transcript.append(' '.join(transcript_words[j1:j2]))
            highlighted_article.append(' '.join(article_words[i1:i2]))

    # Join highlighted transcript and article content into strings
    highlighted_transcript_text = ' '.join(highlighted_transcript)
    highlighted_article_text = ' '.join(highlighted_article)

    # Return feedback, highlighted transcript, and highlighted article
    return "\n".join(feedback), highlighted_transcript_text, highlighted_article_text

def article_record(request, pk):
    """Page for recording audio for an article."""
    article = get_object_or_404(Article, pk=pk)

    if request.method == 'POST':
        form = UserRecordingForm(request.POST, request.FILES)

        if form.is_valid():
            user = request.user
            audio_file = form.cleaned_data['audio_file']

            # Create and save the UserRecording instance (without processing yet)
            user_recording = form.save(commit=False)
            user_recording.user = user
            user_recording.article = article

            # Save the uploaded file temporarily to disk
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                for chunk in audio_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            try:
                # Load Whisper model
                model = whisper.load_model("base")

                # Transcribe the audio file
                transcription_result = model.transcribe(temp_file_path)
                transcript = transcription_result['text']

                # Calculate pronunciation score
                article_content = article.content
                pronunciation_score = calculate_pronunciation_score(transcript, article_content)

                # Generate feedback and highlighted text
                feedback, highlighted_transcript, highlighted_article = generate_feedback(
                    transcript, article_content
                )

                # Update the UserRecording instance with the results
                user_recording.transcript = transcript
                user_recording.pronunciation_score = pronunciation_score
                user_recording.feedback = feedback
                user_recording.highlighted_transcript = highlighted_transcript  # Save the highlighted transcript
                user_recording.highlighted_article = highlighted_article  # Save the highlighted article
                user_recording.save()

                # Pass the highlighted content to the template dynamically
                return render(request, 'articles/user_recording_detail.html', {
                    'recording': user_recording,
                    'highlighted_transcript': highlighted_transcript,
                    'highlighted_article': highlighted_article
                })

            finally:
                # Ensure the temporary file is deleted
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

            return redirect('user_recording_detail', pk=user_recording.pk)
    else:
        form = UserRecordingForm()

    return render(request, 'articles/article_record.html', {'article': article, 'form': form})

def text_to_speech(request):
    """Generate audio for a given word or phrase using gTTS."""
    word = request.GET.get('word', '')  # Get the word to pronounce from the query parameter

    if not word:
        return HttpResponse("No word provided.", status=400)

    try:
        # Initialize gTTS and generate the audio
        tts = gTTS(text=word, lang='en')  # You can adjust the language if necessary (e.g., 'en', 'es')

        # Save audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
            temp_audio_path = temp_audio_file.name
            tts.save(temp_audio_path)  # Save the TTS output to the file

        # Serve the audio file as a response
        with open(temp_audio_path, 'rb') as audio_file:
            response = HttpResponse(audio_file.read(), content_type="audio/mpeg")
            response['Content-Disposition'] = f'inline; filename="{word}.mp3"'
        
        # Clean up temporary file
        os.remove(temp_audio_path)

        return response

    except Exception as e:
        # Handle errors and return a response
        return HttpResponse(f"Error generating speech: {str(e)}", status=500)

def user_recording_list(request):
    """Display a list of recordings made by the logged-in user."""
    recordings = UserRecording.objects.filter(user=request.user).order_by('-submitted_at')
    return render(request, 'articles/user_recording_list.html', {'recordings': recordings})

def user_recording_detail(request, pk):
    """Display the details of a specific recording, including scores and feedback."""
    recording = get_object_or_404(UserRecording, pk=pk, user=request.user)
    return render(request, 'articles/user_recording_detail.html', {'recording': recording})
