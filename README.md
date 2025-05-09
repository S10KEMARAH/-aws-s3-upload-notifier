# -aws-s3-upload-notifier
[File Upload]  
      ↓  
  [S3 Bucket]
      ↓  
[Lambda Function]  
      ├── [Slack Webhook] → Posts to #aws-alerts  
      ├── [Amazon SNS] → Sends email  
      └── [DynamoDB] → Stores metadata  
     1. S3 Bucket
Role:
Acts as the file storage system that triggers the entire workflow when new files are uploaded
Stores all uploaded files securely with versioning and encryption

How It Works:
When a file is uploaded (PUT operation), it automatically triggers the connected Lambda function
Maintains version history if files are modified

Challenges:
Permission errors: If the bucket policy doesn't allow Lambda invocation
Encryption conflicts: KMS key mismatches if encryption settings are misconfigured

 2. Lambda Function
Role:
The brain of the operation that processes upload events and coordinates all actions

How It Works:
Receives S3 event payload (bucket name, file key, size, etc.)
Sends alerts to Slack via webhook
Publishes notifications to SNS (emails)
Stores metadata in DynamoDB

Challenges:
Timeout errors: If Slack/SNS/DynamoDB calls take too long (solution: increase timeout)
Environment variables: Forgetting to set SLACK_WEBHOOK_URL, SNS_TOPIC_ARN, etc.
Permission issues: Lambda role missing dynamodb:PutItem or sns:Publish

3. SNS (Simple Notification Service)
Role:
Distributes email notifications to subscribed users

How It Works:
Lambda publishes a message to the SNS topic
SNS forwards it to all subscribed email addresses

Challenges:
Unconfirmed subscriptions: Emails stuck in "Pending Confirmation" state
Spam filters: Notifications might land in spam/junk folders
4. Slack Webhook

Role:
Provides real-time alerts in a Slack channel
How It Works:
Lambda makes an HTTP POST request to Slack's incoming webhook URL
Message appears in the configured #aws-alerts channel

Challenges:
Expired webhooks: Slack apps need reauthorization if inactive
Rate limiting: Too many rapid requests may get throttled

5. DynamoDB
Role:
Stores metadata about uploaded files (filename, timestamp, bucket name)

Challenges:
Incorrect keys: Wrong partition/sort key configuration
Throttling: If provisioned capacity is exceeded (use on-demand mode)

How All Components Work Together
User uploads file → S3 detects PUT event
S3 triggers Lambda → Sends event data to function
Lambda executes:
Formats notification message
POSTs to Slack webhook
Publishes to SNS topic (emails)
Writes metadata to DynamoDB
End results:
Instant Slack alert
Email notification
Persistent metadata record
