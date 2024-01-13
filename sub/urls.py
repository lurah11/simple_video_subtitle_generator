from django.urls import path
from . import views

urlpatterns=[
    path('',views.homeView,name='home-view'),
    path('proc',views.procView,name='proc-view'),
    path('upload',views.uploadView,name='upload-view'),
    path('result',views.resultView,name='result-view'),
    path('download_transcribe/<int:id>',views.downloadTranscribeView, name='download-transcribe-view'),
    path('translate/<int:id>',views.translateProcView,name='translate-proc-view'),
    path('translate_result/<int:id>',views.resultTranslateView,name='result-translate-view'),
    path('download_translate/<int:id>',views.downloadTranslateView,name='download-translate-view')
]