import json
import boto3
from time import time
import os
import requests


def get_parameter_store(name):
    client = boto3.client('ssm', region_name='us-east-1')
    return client.get_parameter(Name=name)['Parameter']['Value']

def get_client_s3_for_gcs():
    google_access_key_id = get_parameter_store('google_access_key_id')#'GOOGUI56JGZ2LKUKWI2LGML3'
    google_access_key_secret = get_parameter_store('google_access_key_secret')#'GD+WGJ2aFlFUAYybf3Yrb41X/URbE6eG3Jr4LMyI'
    gcs_client = boto3.client('s3',
                    region_name="auto",
                    endpoint_url="https://storage.googleapis.com",
                    aws_access_key_id=google_access_key_id,
                    aws_secret_access_key=google_access_key_secret
                    )
    return gcs_client

#send alert region
def get_current_log_group_name():
    log_group_name = os.environ['AWS_LAMBDA_LOG_GROUP_NAME']
    return log_group_name
    
def get_current_region():
    region = os.environ['AWS_REGION']
   
    return region
    
def get_current_log_stream_name():
    log_stream_name = os.environ['AWS_LAMBDA_LOG_STREAM_NAME']
   
    return log_stream_name

def send_alert(detail, *args):
    region = str(get_current_region())
    print(region)
    log_group_name_encode = str(get_current_log_group_name()).replace('/', '$252F')
    log_stream_name_encode = str(get_current_log_stream_name()).replace('$', '$2524').replace('[', '$255B').replace(']', '$255D').replace('/', '$252F')
    log_stream_url = f"https://console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/{log_group_name_encode}/log-events/{log_stream_name_encode}"
    web_hook = get_parameter_store('web_hook')
    header = { "Content-Type": "application/json" }
    payload = { "icon_emoji": ":sloth:",
                "color": "#ba181b",
                "type": "mrkdwn",
                "text": f"Have a new event 🖕\n{args[0]} {args[1]} {args[2]}\n {detail} {args[3]} <{log_stream_url}|Detail!> :fire:"}
    requests.post(url=web_hook, data=json.dumps(payload), headers=header)
    return 'success'

def get_object_from_gcs_to_s3(s3_bucket, gc_bucket):
    s3_client = boto3.client('s3')
    gcs_client = get_client_s3_for_gcs()
    s3_bucket = s3_bucket#get_parameter_store("s3_bucket")
    gc_bucket = gc_bucket#get_parameter_store("gc_bucket")
    paginator = gcs_client.get_paginator('list_objects_v2')
    gcs_data = paginator.paginate(Bucket=gc_bucket)
    print(gcs_data)
    for page in gcs_data:
        for i in page['Contents']:
            print(f"Copying gcs file: [{i['Key']}] to AWS S3 bucket: [{s3_bucket}]")
            file_to_transfer = gcs_client.get_object(Bucket=gc_bucket, Key=i['Key'])
            s3_client.upload_fileobj(file_to_transfer['Body'], s3_bucket, Key=i['Key'])   
    
def lambda_handler(event, context):
    try:
        get_object_from_gcs_to_s3('duynt71', 'raw_data_duynt')
        print('== Upload file DONE')
        send_alert("Upload file success!", "🤩", ":cloud:", "😎", ':ghost:')
    except Exception: 
        send_alert("Error!", "😕","💩", "☹️", "☠️")
        print("Error")
