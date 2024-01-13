import boto3 
import os 
import logging 
from botocore.exceptions import ClientError
from django.conf import settings
import re

acc_key=settings.AWS_ACCESS_KEY
region=settings.AWS_REGION_NAME
secret=settings.AWS_SECRET_ACCESS_KEY
input_bucket = settings.S3_INPUT_BUCKET
output_transcribe_bucket = settings.S3_TRANSCRIBE_OUTPUT_BUCKET
output_translate_bucket = settings.S3_TRANSLATE_OUTPUT_BUCKET

s3_client = boto3.client(service_name='s3',aws_access_key_id=acc_key,aws_secret_access_key=secret,region_name=region)

def s3_upload_video(user,filepath): 
    username = user.username
    response = {}
    file_path = filepath.temporary_file_path()
    object_name = f"{username}-{filepath.name}"
    

    try : 
        s3_client.upload_file(file_path,input_bucket,object_name)
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
     print(obj_key)
     response = s3_client.get_object(Bucket=output_translate_bucket, Key=obj_key)
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




