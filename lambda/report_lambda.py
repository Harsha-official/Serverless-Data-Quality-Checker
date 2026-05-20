import boto3, json, os

sns = boto3.client('sns')

def lambda_handler(event, context):
    status = event['detail']['state']
    job    = event['detail']['jobName']
    icon   = "✅" if status == "SUCCEEDED" else "❌"

    sns.publish(
        TopicArn=os.environ['SNS_ARN'],
        Subject=f"{icon} Data Quality Report - {status}",
        Message=f"Job: {job}\nStatus: {status}\nResults at: s3://{os.environ['OUTPUT_BUCKET']}"
    )
    return {'statusCode': 200}