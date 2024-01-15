import boto3 
import os 
import logging 
from botocore.exceptions import ClientError
from django.conf import settings
import re
from .models import Video
from django.db.models.fields.files import FileField
from pathlib import Path
from io import BytesIO

acc_key=settings.AWS_ACCESS_KEY
region=settings.AWS_REGION_NAME
secret=settings.AWS_SECRET_ACCESS_KEY
input_bucket = settings.S3_INPUT_BUCKET
output_transcribe_bucket = settings.S3_TRANSCRIBE_OUTPUT_BUCKET
output_translate_bucket = settings.S3_TRANSLATE_OUTPUT_BUCKET

s3_client = boto3.client(service_name='s3',aws_access_key_id=acc_key,aws_secret_access_key=secret,region_name=region)

def upload_progress_callback(bytes_transferred):
    print(f"Bytes transferred: {bytes_transferred}")


def s3_upload_video(user,uploadedfile,video): 
    username = user.username
    # # video_file_path = os.path.join(settings.MEDIA_ROOT,f"user_{user.id}",uploadedfile.name)
    # video = Video.objects.get(filepath__path__name=uploadedfile.name)
    response = {}
    file_name = uploadedfile.name
    # input_file_path = Path(video.filepath.path)
    # posix_file_path = input_file_path.as_posix()
    object_name = f"{username}-{file_name}"

    input_file = Path(video.filepath.path).absolute()
    print(f"s3_input_file{input_file}")
       
    try :   
            s3_client.upload_file(input_file,input_bucket,object_name,Callback=upload_progress_callback)
            response['bucket'] = input_bucket
            response['obj_key'] = object_name
            response['success'] = True
    except ClientError as e:
        logging.error(e)
        return False
    return response




def s3_get_input_file_uri(obj_key): 
    s3_uri = f"s3://{input_bucket}/{obj_key}"
    return s3_uri

def download_s3_file(obj_key): 
     response = s3_client.get_object(Bucket=output_transcribe_bucket, Key=obj_key)
     return response 

def download_s3_file_translate(obj_key): 
     object_lists = s3_client.list_objects(Bucket=output_translate_bucket,Prefix=obj_key)
     for obj in object_lists['Contents']: 
          if "auxiliary" not in obj['Key'] :
               target_obj_key = obj['Key']
     print(target_obj_key)
     response = s3_client.get_object(Bucket=output_translate_bucket, Key=target_obj_key)
     return response 

# def s3_get_translate_input_file_uri(obj_key): 
#     response = f"s3://{output_transcribe_bucket}/{obj_key}"
#     return response

def s3_create_subtitle_obj_key(user,filename):
    foldername= re.sub('.srt','',filename)
    # subtitle_folder = f"{foldername}/subtitle"
    # plaintext_folder = f"{foldername}/plaintext"
    return f"{user}/{foldername}/{filename}"

def s3_copy_subtitle(source_uri,final_uri):
    s3_client.copy_object(
        Bucket=output_transcribe_bucket,
        CopySource={
            'Bucket':output_transcribe_bucket,
            'Key':source_uri
        },
        Key=final_uri
    )


def post_process_srt(response): 
    text = response.decode('utf-8')
    modified_text = re.sub(r'^(.*?)(\d+)(?:st|nd|rd|th)(.*?)$', r'\1\2\3', text, flags=re.MULTILINE)
    return modified_text.encode('utf-8')

