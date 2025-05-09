import os
import json
import boto3
from datetime import datetime
import urllib3

def lambda_handler(event, context):
    # Initialize AWS clients
    s3 = boto3.client('s3')
    sns = boto3.client('sns')
    dynamodb = boto3.resource('dynamodb')
    
    # Get environment variables
    slack_webhook = os.environ['SLACK_WEBHOOK_URL']
    sns_topic_arn = os.environ['SNS_TOPIC_ARN']
    ddb_table_name = os.environ['DDB_TABLE_NAME']
    
    # Process each file uploaded
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        size = record['s3']['object']['size']
        event_time = record['eventTime']
        
        # Create message
        message = f"New file uploaded:\n\n• File: {key}\n• Size: {size} bytes\n• Bucket: {bucket}\n• Time: {event_time}"
        
        # Send to Slack
        http = urllib3.PoolManager()
        slack_data = {'text': message}
        http.request('POST', slack_webhook, body=json.dumps(slack_data).encode('utf-8'),
                     headers={'Content-Type': 'application/json'})
        
        # Send email via SNS
        sns.publish(
            TopicArn=sns_topic_arn,
            Subject="New File Uploaded",
            Message=message
        )
        
        # Store in DynamoDB
        table = dynamodb.Table(ddb_table_name)
        table.put_item(
            Item={
                'fileName': key,
                'uploadTimestamp': event_time,
                'fileSize': size,
                's3Bucket': bucket
            }
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete')
    }
