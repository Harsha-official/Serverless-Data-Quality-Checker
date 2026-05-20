import boto3, json, os

databrew = boto3.client('databrew')
sns = boto3.client('sns')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key    = event['Records'][0]['s3']['object']['key']

    run = databrew.start_job_run(Name=os.environ['JOB_NAME'])

    sns.publish(
        TopicArn=os.environ['SNS_ARN'],
        Subject="DQ Check Started",
        Message=f"File: {key}\nJob ID: {run['RunId']}"
    )
    return {'statusCode': 200}
