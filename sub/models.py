from django.db import models

# Create your models here.

from django.contrib.auth.models import User

class UploadedVideo(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    bucket = models.CharField(max_length=500)
    obj_key= models.CharField(max_length=1000)

    def save(self,*args,**kwargs): 
        if UploadedVideo.objects.filter(obj_key=self.obj_key).exists():
            raise ValueError(f"The object with key: '{self.obj_key}' already exists!")
        super().save(*args,**kwargs)

class LangCode(models.Model): 
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self): 
        return f"{self.code}-{self.name}"

class TranscribeResult(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    uri=models.CharField(max_length=1000)
    redacted=models.BooleanField(default=False)
    language = models.ForeignKey(LangCode,on_delete=models.CASCADE)

class TranslateResult(models.Model): 
    transcript=models.ForeignKey(TranscribeResult,on_delete=models.CASCADE)
    uri = models.CharField(max_length=1000)
    target_lang=models.ForeignKey(LangCode,on_delete=models.CASCADE)

class PlainTranscribeResult(models.Model): 
    transcribe = models.OneToOneField(TranscribeResult,on_delete=models.CASCADE)
    uri = models.CharField(max_length=1000)
    
