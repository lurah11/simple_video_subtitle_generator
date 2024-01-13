from django import forms 

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import BaseUserCreationForm

def validate_video_file(value):
    import os
    from django.core.exceptions import ValidationError

    ext = os.path.splitext(value.name)[1]  # Get the file extension
    valid_extensions = ['.mp4', '.avi', '.mkv', '.mov']  # Add or modify the list based on allowed video file extensions

    if not ext.lower() in valid_extensions:
        raise ValidationError(_('File type not supported. Please upload a valid video file.'))


class UploadFileForm(forms.Form):
    uploadedFile=forms.FileField(validators=[validate_video_file])


class UserCreationForm(BaseUserCreationForm):
    pass

class SubmitTranscribeJobForm(forms.Form): 
    input_video=forms.CharField(max_length=2000)
    input_language=forms.CharField(max_length=20)
    redacted = forms.CharField(max_length=20)

class SubmitTranslateJobForm(forms.Form): 
    target_lang = forms.CharField(max_length=100)
    

