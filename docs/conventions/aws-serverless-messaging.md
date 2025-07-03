# AWS Serverless Messaging Services

## Environment Variables
```bash
PROJECT_NAME=my-awesome-app
STAGE=dev
REGION=us-east-1
OWNER=John doe abc123
LOG_LEVEL=INFO
```

## SQS (Simple Queue Service)

### Queue Configuration
```yaml
resources:
  Resources:
    TaskQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:custom.projectName}-${env:STAGE}-tasks
        VisibilityTimeoutSeconds: 300
        MessageRetentionPeriod: 1209600  # 14 days
        DelaySeconds: 0
        RedrivePolicy:
          deadLetterTargetArn: !GetAtt TaskDLQ.Arn
          maxReceiveCount: 3
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
            
    TaskDLQ:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:custom.projectName}-${env:STAGE}-tasks-dlq
        MessageRetentionPeriod: 1209600  # 14 days
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
```

### Lambda Integration
```yaml
functions:
  processTask:
    handler: src/handlers/queue.processTask
    events:
      - sqs:
          arn: !GetAtt TaskQueue.Arn
          batchSize: 10
          maximumBatchingWindowInSeconds: 5
          functionResponseType: ReportBatchItemFailures
```

### Best Practices
- Use dead letter queues for failed messages
- Set visibility timeout (6x function timeout)
- Use batch processing for better throughput
- Implement idempotent message processing
- Monitor queue depth and age of messages

## SNS (Simple Notification Service)

### Topic Configuration
```yaml
resources:
  Resources:
    NotificationTopic:
      Type: AWS::SNS::Topic
      Properties:
        TopicName: ${self:custom.projectName}-${env:STAGE}-notifications
        DisplayName: "Application Notifications"
        KmsMasterKeyId: alias/aws/sns
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
            
    EmailSubscription:
      Type: AWS::SNS::Subscription
      Properties:
        TopicArn: !Ref NotificationTopic
        Protocol: email
        Endpoint: admin@example.com
        
    SqsSubscription:
      Type: AWS::SNS::Subscription
      Properties:
        TopicArn: !Ref NotificationTopic
        Protocol: sqs
        Endpoint: !GetAtt ProcessingQueue.Arn
```

### Lambda Integration
```yaml
functions:
  handleNotification:
    handler: src/handlers/notification.handler
    events:
      - sns:
          arn: !Ref NotificationTopic
          filterPolicy:
            eventType:
              - order.created
              - order.updated
```

### Best Practices
- Use filter policies to route messages efficiently
- Enable server-side encryption
- Use FIFO topics for ordered message delivery
- Implement message deduplication for FIFO
- Set up appropriate retry policies

## EventBridge

### Custom Event Bus
```yaml
resources:
  Resources:
    CustomEventBus:
      Type: AWS::Events::EventBus
      Properties:
        Name: ${self:custom.projectName}-${env:STAGE}-events
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
```

### Event Rules
```yaml
functions:
  processOrderEvent:
    handler: src/handlers/events.processOrder
    events:
      - eventBridge:
          eventBus: !Ref CustomEventBus
          pattern:
            source:
              - "myapp.orders"
            detail-type:
              - "Order Created"
              - "Order Updated"
            detail:
              status:
                - "confirmed"
                - "shipped"
```

### Event Publishing Pattern
```python
import boto3
import json
from datetime import datetime

def publish_event(event_type, detail, source="myapp"):
    client = boto3.client('events')
    
    response = client.put_events(
        Entries=[
            {
                'Source': source,
                'DetailType': event_type,
                'Detail': json.dumps(detail),
                'EventBusName': os.environ['EVENT_BUS_NAME'],
                'Time': datetime.utcnow()
            }
        ]
    )
    return response
```

### Best Practices
- Use custom event buses for application events
- Implement event schemas for better governance
- Use event replay for debugging and recovery
- Monitor event processing with CloudWatch
- Use dead letter queues for failed events

## Cognito

### User Pool Configuration
```yaml
resources:
  Resources:
    CognitoUserPool:
      Type: AWS::Cognito::UserPool
      Properties:
        UserPoolName: ${self:custom.projectName}-${env:STAGE}-users
        UsernameAttributes:
          - email
        AutoVerifiedAttributes:
          - email
        Policies:
          PasswordPolicy:
            MinimumLength: 8
            RequireUppercase: true
            RequireLowercase: true
            RequireNumbers: true
            RequireSymbols: true
        MfaConfiguration: OPTIONAL
        EnabledMfas:
          - SOFTWARE_TOKEN_MFA
        UserPoolTags:
          Owner: ${env:OWNER}
          env: ${self:custom.projectName}
          stage: ${env:STAGE}
          
    CognitoUserPoolClient:
      Type: AWS::Cognito::UserPoolClient
      Properties:
        UserPoolId: !Ref CognitoUserPool
        ClientName: ${self:custom.projectName}-${env:STAGE}-client
        GenerateSecret: false
        ExplicitAuthFlows:
          - ADMIN_NO_SRP_AUTH
          - USER_PASSWORD_AUTH
        RefreshTokenValidity: 30
        AccessTokenValidity: 60
        IdTokenValidity: 60
```

### API Gateway Integration
```yaml
provider:
  httpApi:
    authorizers:
      cognitoAuthorizer:
        type: jwt
        identitySource: $request.header.Authorization
        issuerUrl: !GetAtt CognitoUserPool.ProviderURL
        audience:
          - !Ref CognitoUserPoolClient

functions:
  protectedEndpoint:
    handler: src/handlers/api.protected
    events:
      - httpApi:
          path: /protected
          method: get
          authorizer:
            name: cognitoAuthorizer
```

### Best Practices
- Use email as username for better UX
- Enable MFA for sensitive applications
- Configure password policies appropriately
- Use pre/post authentication triggers for custom logic
- Monitor authentication events

## Integration Patterns

### Fan-out with SNS + SQS
```yaml
resources:
  Resources:
    OrderTopic:
      Type: AWS::SNS::Topic
      Properties:
        TopicName: ${self:custom.projectName}-${env:STAGE}-orders
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
        
    # Multiple SQS queues for different processors
    InventoryQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:custom.projectName}-${env:STAGE}-inventory
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
        
    ShippingQueue:
      Type: AWS::SQS::Queue
      Properties:
        QueueName: ${self:custom.projectName}-${env:STAGE}-shipping
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
```

### Event-Driven Architecture
- Use EventBridge for loose coupling
- Implement event sourcing patterns
- Use event replay for system recovery
- Monitor event flows with distributed tracing

## Error Handling
- Implement dead letter queues for all async processing
- Use exponential backoff for retries
- Log all processing errors with context
- Set up alerts for high error rates
- Use circuit breaker patterns for external dependencies

## Monitoring & Observability
- Track message processing latency
- Monitor queue depths and DLQ messages
- Set up dashboards for messaging metrics
- Use X-Ray for distributed tracing
- Implement custom metrics for business logic