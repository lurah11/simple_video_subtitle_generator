import boto3
from django.conf import settings 
from .utility import s3_get_input_file_uri
from datetime import datetime
import time


acc_key=settings.AWS_ACCESS_KEY
region=settings.AWS_REGION_NAME
secret=settings.AWS_SECRET_ACCESS_KEY
output_transcribe_bucket = settings.S3_TRANSCRIBE_OUTPUT_BUCKET
output_translate_bucket = settings.S3_TRANSLATE_OUTPUT_BUCKET

transcribe_client = boto3.client(service_name='transcribe',aws_access_key_id=acc_key,aws_secret_access_key=secret,region_name=region)


def start_transcript(transcribe_client,mediafileuri,job_name,mediaformat='mp4',language_code='en',redacted=False):
    kwargs = {
        'TranscriptionJobName':job_name,
        'MediaFormat':mediaformat,
        'Media':{'MediaFileUri':mediafileuri},
        'OutputBucketName':output_transcribe_bucket,
        'Subtitles' :{
            'Formats': ['srt'],
            'OutputStartIndex': 1
        }
    }
    if language_code == "detect_language": 
        kwargs['IdentifyLanguage'] = True
    else : 
        kwargs['LanguageCode'] = language_code
    if redacted : 
        kwargs["ContentRedaction"] = {
                'RedactionType': 'PII',
                'RedactionOutput': 'redacted_and_unredacted',
            }
        kwargs["ToxicityDetection"] = [
            {
            'ToxicityCategories': [
                'ALL',
                ]
            },
            ]
    response = transcribe_client.start_transcription_job(**kwargs)
    return response 


def submit_transcription_job(user,obj_key, language_code=None,redacted=False):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    job_name = f"{obj_key}_transcription_{timestamp}"

    media_file_uri = s3_get_input_file_uri(obj_key)

    

    try:
        response = start_transcript(transcribe_client,mediafileuri=media_file_uri, job_name=job_name,language_code=language_code,redacted=redacted)

        # Process the response or perform other actions upon successful submission
        print(f"Transcription job '{job_name}' submitted successfully.")
        response['job_name'] = job_name
        return response
    except Exception as e:
        print(f"Error: {e}")


def get_transcribe_job(job_name):
    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_transcription_job(TranscriptionJobName = job_name)
        job_status = job['TranscriptionJob']['TranscriptionJobStatus']
        if job_status in ['COMPLETED', 'FAILED']:
            print(f"Job {job_name} is {job_status}.")
            if job_status == 'COMPLETED':
                print(
                    f"Download the transcript from\n"
                    f"\t{job['TranscriptionJob']['Transcript']['TranscriptFileUri']}.")
                return job
        else:
            print(f"Waiting for {job_name}. Current status is {job_status}.")
        time.sleep(10)
    