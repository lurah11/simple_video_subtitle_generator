from django.shortcuts import render,redirect,reverse
from django.http import JsonResponse, HttpResponse
from allauth.account.decorators import verified_email_required
from .forms import UploadFileForm, SubmitTranscribeJobForm, SubmitTranslateJobForm
from .utility import s3_upload_video,download_s3_file,s3_create_subtitle_obj_key,s3_copy_subtitle, download_s3_file_translate, post_process_srt
import boto3
from .models import UploadedVideo, LangCode, TranscribeResult, TranslateResult, Video
from .transcribe import submit_transcription_job,get_transcribe_job
from django.conf import settings 
from .translate import translate_job
import time
from django.db.models.fields.files import FileField


acc_key=settings.AWS_ACCESS_KEY
region=settings.AWS_REGION_NAME
secret=settings.AWS_SECRET_ACCESS_KEY


def homeView(request): 
    return render(request,'sub/home.html')



########### HANDLE TRANSCRIPTION ########################################3
@verified_email_required
def procView(request): 
    # initialize context 
    user = request.user
    videos = user.uploadedvideo_set.all()
    languages = LangCode.objects.all()
    context = {
        'videos':videos,
        'languages':languages
    }
    job_name =""
    if request.method == 'POST': 
        form = SubmitTranscribeJobForm(request.POST)
        if form.is_valid(): 
            obj_key = form.cleaned_data['input_video']
            input_lang = form.cleaned_data['input_language']

            lang_obj = LangCode.objects.get(code=input_lang)

            redacted_text = form.cleaned_data['redacted']
            redacted = True if redacted_text == "redacted" else False

            transcribe_job = submit_transcription_job(user,obj_key,language_code=input_lang,redacted=redacted)

            try:
                job_name=transcribe_job['job_name']
                response = get_transcribe_job(job_name)
                full_uri = response['TranscriptionJob']['Subtitles']['SubtitleFileUris'][0]
                file_uri = full_uri.rsplit('/', 1)[-1]
                final_uri = s3_create_subtitle_obj_key(user,file_uri)
                TranscribeResult.objects.create(user=user,uri=final_uri,redacted=redacted,language=lang_obj)
                s3_copy_subtitle(file_uri,final_uri)
            except Exception as e :
                print("Errror happend while try to get the transcribe uri ")
                print(e)
            
            finally:
                return redirect(reverse('result-view'))
                
            

    return render(request,'sub/proc.html',context=context)

@verified_email_required
def resultView(request):
    user = request.user
    transcribe_results = TranscribeResult.objects.filter(user=user)
    context = {
        'transcribe_results': transcribe_results
    }
    return render(request,'sub/results.html',context=context)

@verified_email_required
def uploadView(request):
    if request.method == 'POST': 
        user = request.user
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid(): 
            uploaded_file = form.cleaned_data['uploadedFile']
            video = Video.objects.create(user=user,filepath=uploaded_file) 
            print(f"userrr---{video.user}---{video.user.id}")  
            # max_timeout = 600
            # while True : 
            response=s3_upload_video(user,uploaded_file,video)
                    # if not response : 
                    #     time.sleep(3)
                    #     max_timeout -= 3 
                    # if max_timeout <= 0 : 
                    #     break             
            if response['success']: 
                try:
                    UploadedVideo.objects.create(user=user,bucket=response['bucket'],obj_key=response['obj_key'])
                    return JsonResponse({'status':'Success'})
                except:
                    print("The obj_key might have exists")   
            else: 
                return JsonResponse({'status':'Failed during uploading'})
    return render(request,'sub/upload.html')


@verified_email_required
def downloadTranscribeView(request,id):
    result = TranscribeResult.objects.get(id=id)
    response = download_s3_file(result.uri)
    print(result.uri)
    text = response['Body'].read()

    response = HttpResponse(text, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{result.uri}"'   
    return response

####################HANDLE TRANSLATION#############################################

@verified_email_required
def translateProcView(request,id): 
    transcrib_obj = TranscribeResult.objects.get(id=id)
    languages = LangCode.objects.all()
    if request.method == 'POST': 
        form = SubmitTranslateJobForm(request.POST)
        if form.is_valid():
            target_lang = form.cleaned_data['target_lang']
            target_lang_obj = LangCode.objects.get(code=target_lang)
            s3_output_object_key = translate_job(transcrib_obj,target_lang)
            try: 
                TranslateResult.objects.create(transcript=transcrib_obj,uri=s3_output_object_key,target_lang=target_lang_obj)
            except Exception as e:
                print(f'Failed to save to db , the error is {e}')
            return HttpResponse('Berhasil')
    context = {
        'transcrib_obj':transcrib_obj,
        'languages':languages
    }
    return render(request,'sub/trans.html',context)

@verified_email_required
def resultTranslateView(request,id):
    transcrib_obj = TranscribeResult.objects.get(id=id)
    translate_objs = TranslateResult.objects.filter(transcript=transcrib_obj)
    context = {
        'transcribe_obj':transcrib_obj,
        'translate_objs':translate_objs
    }
    return render(request,'sub/trans_results.html',context=context)

@verified_email_required
def downloadTranslateView(request,id):
    result = TranslateResult.objects.get(id=id)
    response = download_s3_file_translate(result.uri)
    text = response['Body'].read()
    final_text = post_process_srt(text)

    response = HttpResponse(final_text, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="translation_result.srt"'   
    return response