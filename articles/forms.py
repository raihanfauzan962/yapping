from django import forms
from .models import UserRecording

class UserRecordingForm(forms.ModelForm):
    class Meta:
        model = UserRecording
        fields = ['audio_file', 'article']

