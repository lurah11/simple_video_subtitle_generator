import boto3
import time
import re
from datetime import datetime
from django.conf import settings

acc_key=settings.AWS_ACCESS_KEY
region=settings.AWS_REGION_NAME
secret=settings.AWS_SECRET_ACCESS_KEY
output_transcribe_bucket = settings.S3_TRANSCRIBE_OUTPUT_BUCKET
output_translate_bucket = settings.S3_TRANSLATE_OUTPUT_BUCKET
data_access_role = settings.DATA_ACCESS_ROLE
translate_client = boto3.client('translate', aws_access_key_id=acc_key, aws_secret_access_key=secret, region_name=region)

def modify_jobname(original_string):
    # Substitute "transcription" with "translation"
    modified_string = re.sub('_transcription', '_translation', original_string)
    # Get the current timestamp in the format YYYYMMDDHHMMSS
    current_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # Substitute with current_timestamp
    modified_string = re.sub(r'_\d{14}', f'_{current_timestamp}', modified_string)
    # modified_foldername = re.sub(r'.srt','',modified_string)
    return modified_string

def get_input_uri(uri):
    # get only path until foldername
    parts = uri.split('/')
    desired_substring = '/'.join(parts[:-1])
    return desired_substring

def get_translation_object_key(uri): 
    bucket_name_uri = "s3://{output_translate_bucket}/"
    output_object_key = re.sub(bucket_name_uri,'',uri)
    return output_object_key


def translate_job(transcribe_obj,target_lang):    
    job_name = modify_jobname(transcribe_obj.uri)

    uri = f's3://{output_transcribe_bucket}/{transcribe_obj.uri}'
    input_uri = get_input_uri(uri)
    output_uri = f's3://{output_translate_bucket}/{job_name}'

    
    response = translate_client.start_text_translation_job(
    JobName=job_name,
    InputDataConfig={
        'S3Uri': input_uri,
        'ContentType': 'text/plain'
    },
    OutputDataConfig={
        'S3Uri': output_uri
    },
    SourceLanguageCode=transcribe_obj.language.code,
    TargetLanguageCodes=[target_lang],
    DataAccessRoleArn=data_access_role
    )

    job_id = response['JobId']

    # Check the status in a loop
    max_timeout = 3600

    while True:
        job = translate_client.describe_text_translation_job(JobId=job_id)
        job_status = job['TextTranslationJobProperties']['JobStatus']
        output_job_uri = job['TextTranslationJobProperties']['OutputDataConfig']['S3Uri']
        output_object_key = get_translation_object_key(output_job_uri)
        
        print(f"Job Status: {job_status}")

        if job_status not in ['IN_PROGRESS', 'SUBMITTED']:
            break

        # Wait for some time before checking again (e.g., every 5 seconds)
        time.sleep(10)
        max_timeout -= 10
        if max_timeout <= 0 : 
            break

  
    if job_status == 'COMPLETED':
        print("Translation job completed successfully!")
        return output_object_key
    else :
        print("Translation job not completed or failed! oh no.....!!!")
  
