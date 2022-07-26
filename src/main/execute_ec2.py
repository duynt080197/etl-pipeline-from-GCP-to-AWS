import time
import json
import boto3
import os
import requests


def get_parameter_store(name):
    client = boto3.client('ssm')
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

def start_ec2_instance():
    client = boto3.client("ec2", region_name="ap-southeast-1")
    instance_id = get_parameter_store('instance_id')
    responses = client.start_instances(
    InstanceIds=[
        instance_id
    ],
    DryRun=False # Make it False to test
    )   
    
def lambda_handler(event, context):
    try:
        ssm = boto3.client("ssm", region_name="ap-southeast-1")
        start_ec2_instance()
        response = ssm.send_command(
            DocumentName="AWS-RunShellScript", # One of AWS' preconfigured documents
            Parameters={'commands': ["cd /home/ec2-user", "pwd", "aws s3 cp s3://mentoringwarehouse/cleaning-data.csv ohyeah3.csv", "ls"]},
            InstanceIds=['i-04e50a0e647f62b1f'],
        )
        time.sleep(5)
        command_id = response['Command']['CommandId']
        output = ssm.get_command_invocation(CommandId=command_id, InstanceId='i-04e50a0e647f62b1f')
        print('Result: ', output['StandardOutputContent'])
        send_alert("Move data to EC2 Success!", "🤩", ":cloud:", "😎", ':ghost:')
    except Exception:
        send_alert("Move data to EC2! Error!", "😕","💩", "☹️", "☠️")
    