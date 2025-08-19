# SQS Conventions

## Environment Variables

View the `docs/conventions/aws-environment.md` for more about how the VPC, public and private subnets will be defined.

```bash
PROJECT_NAME=my-awesome-app
STAGE=dev
REGION=us-east-1
OWNER=John Doe abc123
LOG_LEVEL=INFO
```

## Standard Queue Configuration
```yaml
resources:
  Resources:
    ProcessingQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:custom.projectName}-${env:STAGE}-processing
        VisibilityTimeoutSeconds: 300  # 6x function timeout
        MessageRetentionPeriod: 1209600  # 14 days
        DelaySeconds: 0
        ReceiveMessageWaitTimeSeconds: 20  # Long polling
        RedrivePolicy:
          deadLetterTargetArn: !GetAtt ProcessingDLQ.Arn
          maxReceiveCount: 3
        KmsMasterKeyId: alias/aws/sqs
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    ProcessingDLQ:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:custom.projectName}-${env:STAGE}-processing-dlq
        MessageRetentionPeriod: 1209600  # 14 days
        KmsMasterKeyId: alias/aws/sqs
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
```

## FIFO Queue Configuration
```yaml
resources:
  Resources:
    OrderQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:custom.projectName}-${env:STAGE}-orders.fifo
        FifoQueue: true
        ContentBasedDeduplication: true
        DeduplicationScope: messageGroup
        FifoThroughputLimit: perMessageGroupId
        VisibilityTimeoutSeconds: 300
        MessageRetentionPeriod: 1209600
        RedrivePolicy:
          deadLetterTargetArn: !GetAtt OrderDLQ.Arn
          maxReceiveCount: 3
        KmsMasterKeyId: alias/aws/sqs
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    OrderDLQ:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:custom.projectName}-${env:STAGE}-orders-dlq.fifo
        FifoQueue: true
        MessageRetentionPeriod: 1209600
        KmsMasterKeyId: alias/aws/sqs
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
```

## Lambda Integration
```yaml
functions:
  processMessages:
    handler: src/handlers/queue.processMessages
    timeout: 50  # Less than visibility timeout
    reservedConcurrency: 5
    environment:
      QUEUE_URL: !Ref ProcessingQueue
    events:
      - sqs:
          arn: !GetAtt ProcessingQueue.Arn
          batchSize: 10
          maximumBatchingWindowInSeconds: 5
          functionResponseType: ReportBatchItemFailures
          maximumConcurrency: 5

  processFifoMessages:
    handler: src/handlers/queue.processFifoMessages
    timeout: 50
    environment:
      FIFO_QUEUE_URL: !Ref OrderQueue
    events:
      - sqs:
          arn: !GetAtt OrderQueue.Arn
          batchSize: 1  # FIFO requires sequential processing
          functionResponseType: ReportBatchItemFailures
```

## Message Publishing Patterns

### Python
```python
import boto3
import json
from uuid import uuid4
from datetime import datetime

sqs = boto3.client('sqs')

def send_message(queue_url, message_body, delay_seconds=0):
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message_body),
        DelaySeconds=delay_seconds,
        MessageAttributes={
            'source': {
                'StringValue': 'api',
                'DataType': 'String'
            },
            'timestamp': {
                'StringValue': datetime.utcnow().isoformat(),
                'DataType': 'String'
            }
        }
    )
    return response

def send_fifo_message(queue_url, message_body, group_id, deduplication_id=None):
    if not deduplication_id:
        deduplication_id = str(uuid4())
    
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message_body),
        MessageGroupId=group_id,
        MessageDeduplicationId=deduplication_id
    )
    return response

def send_batch_messages(queue_url, messages):
    entries = []
    for i, message in enumerate(messages):
        entries.append({
            'Id': str(i),
            'MessageBody': json.dumps(message),
            'MessageAttributes': {
                'source': {
                    'StringValue': 'batch',
                    'DataType': 'String'
                }
            }
        })
    
    response = sqs.send_message_batch(
        QueueUrl=queue_url,
        Entries=entries
    )
    return response
```

### Node.js
```javascript
const { SQSClient, SendMessageCommand, SendMessageBatchCommand } = require('@aws-sdk/client-sqs');

const sqs = new SQSClient({ region: process.env.AWS_REGION });

const sendMessage = async (queueUrl, messageBody, delaySeconds = 0) => {
  const command = new SendMessageCommand({
    QueueUrl: queueUrl,
    MessageBody: JSON.stringify(messageBody),
    DelaySeconds: delaySeconds,
    MessageAttributes: {
      source: {
        StringValue: 'api',
        DataType: 'String'
      },
      timestamp: {
        StringValue: new Date().toISOString(),
        DataType: 'String'
      }
    }
  });
  
  return await sqs.send(command);
};

const sendFifoMessage = async (queueUrl, messageBody, groupId, deduplicationId) => {
  const command = new SendMessageCommand({
    QueueUrl: queueUrl,
    MessageBody: JSON.stringify(messageBody),
    MessageGroupId: groupId,
    MessageDeduplicationId: deduplicationId || require('uuid').v4()
  });
  
  return await sqs.send(command);
};
```

## Message Processing Patterns

### Python Handler
```python
import json
import logging

logger = logging.getLogger(__name__)

def process_messages(event, context):
    failed_records = []
    
    for record in event['Records']:
        try:
            # Parse message
            message_body = json.loads(record['body'])
            receipt_handle = record['receiptHandle']
            
            # Process message
            result = process_single_message(message_body)
            logger.info(f"Processed message: {result}")
            
        except Exception as error:
            logger.error(f"Failed to process message: {error}", exc_info=True)
            failed_records.append({
                'itemIdentifier': record['messageId']
            })
    
    # Return failed records for retry
    return {
        'batchItemFailures': failed_records
    }

def process_single_message(message_body):
    # Implement idempotent processing logic
    message_id = message_body.get('id')
    
    # Check if already processed (idempotency)
    if is_already_processed(message_id):
        logger.info(f"Message {message_id} already processed")
        return
    
    # Process business logic
    result = handle_business_logic(message_body)
    
    # Mark as processed
    mark_as_processed(message_id)
    
    return result
```

### Node.js Handler
```javascript
exports.processMessages = async (event, context) => {
  const failedRecords = [];
  
  for (const record of event.Records) {
    try {
      const messageBody = JSON.parse(record.body);
      const receiptHandle = record.receiptHandle;
      
      const result = await processSingleMessage(messageBody);
      console.log('Processed message:', result);
      
    } catch (error) {
      console.error('Failed to process message:', error);
      failedRecords.push({
        itemIdentifier: record.messageId
      });
    }
  }
  
  return {
    batchItemFailures: failedRecords
  };
};
```

## Queue Monitoring
```yaml
resources:
  Resources:
    QueueDepthAlarm:
      Type: AWS::CloudWatch::Alarm
      Properties:
        AlarmName: ${self:custom.projectName}-${env:STAGE}-queue-depth
        AlarmDescription: Queue depth too high
        MetricName: ApproximateNumberOfVisibleMessages
        Namespace: AWS/SQS
        Statistic: Average
        Period: 300
        EvaluationPeriods: 2
        Threshold: 100
        ComparisonOperator: GreaterThanThreshold
        Dimensions:
          - Name: QueueName
            Value: !GetAtt ProcessingQueue.QueueName
        AlarmActions:
          - !Ref SNSTopicArn

    DLQAlarm:
      Type: AWS::CloudWatch::Alarm
      Properties:
        AlarmName: ${self:custom.projectName}-${env:STAGE}-dlq-messages
        AlarmDescription: Messages in DLQ
        MetricName: ApproximateNumberOfVisibleMessages
        Namespace: AWS/SQS
        Statistic: Sum
        Period: 300
        EvaluationPeriods: 1
        Threshold: 1
        ComparisonOperator: GreaterThanOrEqualToThreshold
        Dimensions:
          - Name: QueueName
            Value: !GetAtt ProcessingDLQ.QueueName
```

## IAM Permissions
```yaml
provider:
  iamRoleStatements:
    - Effect: Allow
      Action:
        - sqs:SendMessage
        - sqs:SendMessageBatch
      Resource: 
        - !GetAtt ProcessingQueue.Arn
        - !GetAtt OrderQueue.Arn
    - Effect: Allow
      Action:
        - sqs:ReceiveMessage
        - sqs:DeleteMessage
        - sqs:GetQueueAttributes
      Resource:
        - !GetAtt ProcessingQueue.Arn
        - !GetAtt OrderQueue.Arn
    - Effect: Allow
      Action:
        - kms:Encrypt
        - kms:Decrypt
        - kms:ReEncrypt*
        - kms:GenerateDataKey*
        - kms:DescribeKey
      Resource: !Sub "arn:aws:kms:${AWS::Region}:${AWS::AccountId}:alias/aws/sqs"
```

## Best Practices
- Use dead letter queues for failed messages
- Set visibility timeout to 6x function timeout
- Enable long polling (20 seconds)
- Use batch processing for better throughput
- Implement idempotent message processing
- Use FIFO queues for ordered processing
- Enable server-side encryption with KMS
- Monitor queue depth and DLQ messages
- Use message attributes for filtering
- Implement proper error handling and retries
- Use reserved concurrency to prevent throttling
- Return batch item failures for partial success