import json
import pandas as pd
import numpy as np
import boto3
from io import StringIO
import os
import requests


def get_parameter_store(name):
    client = boto3.client('ssm', region_name='ap-southeast-1')
    return client.get_parameter(Name=name)['Parameter']['Value']

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

def s3_client():
    return boto3.client("s3")

def get_list_object_from_s3(bucket_s3):
    client = boto3.client("s3")
    return client.list_objects_v2(Bucket=bucket_s3)

def read_object_to_df(bucket_s3):
    s3_client = boto3.client("s3")
    obj_list = get_list_object_from_s3(bucket_s3)
    columns_name = []
    data = []
    print(obj_list)
    for obj in obj_list['Contents']:
        key = obj['Key']
        print(key)
        body = s3_client.get_object(Bucket=bucket_s3, Key=key)['Body']
        csv_string = body.read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_string),  delimiter=';')#,index_col=0
        if len(columns_name) == 0:
            columns_name = df.columns.values.tolist()
            print(columns_name)
        data.extend(df.values.tolist())
        print(data)
    
    df = pd.DataFrame(data=data, columns=columns_name)
    return df

def delete_duplicate(df):
    bool_series = df.duplicated()
    df = df[~bool_series]
    return df 

def replace_nan_value_in_country_col(df):
    df['country'].replace(to_replace=np.nan, value = 'Unknown', inplace=True)

def lambda_handler(event, context):
    # TODO implement
    try:
        bucket_s3 = 'mentoringwarehouse'
        s3_client = boto3.client("s3")
        
        #gather all file in a df
        df = read_object_to_df(bucket_s3)
        
        #delete duplicate
        df = delete_duplicate(df)
        
        #replace nan value in country column
        replace_nan_value_in_country_col(df)
        
        #update wrong country name
        temp_country = 'temp_country'
        for country in sorted(df['country'].unique()):
            if temp_country in country:
                df['country'].replace(to_replace=country, value = temp_country, inplace=True)
                continue
            temp_country = country
        
        bucket = get_parameter_store('bucket_warehouse')
        csv_df = StringIO()
        df.to_csv(csv_df, index=False)
        s3_resource = boto3.resource('s3')
        s3_resource.Object(bucket, 'cleaning-data.csv').put(Body=csv_df.getvalue())
        print('Success!')
        #send_alert("Cleaning data success!", "🤩", ":cloud:", "😎", ':ghost:')
    except Exception:
        #send_alert("Cleaning data! Error!", "😕","💩", "☹️", "☠️")
        print("Error")
print(get_parameter_store('s3_bucket'))