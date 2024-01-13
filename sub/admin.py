from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.UploadedVideo)
admin.site.register(models.TranscribeResult)
admin.site.register(models.LangCode)