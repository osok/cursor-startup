# AWS Serverless Orchestration

## Environment
```bash
PROJECT_NAME=my-app
STAGE=dev
REGION=us-east-1
OWNER=John Doe abc123
LOG_LEVEL=INFO
```

## Step Functions

### State Machine Configuration
```yaml
resources:
  Resources:
    OrderProcessingStateMachine:
      Type: AWS::StepFunctions::StateMachine
      Properties:
        StateMachineName: ${self:custom.projectName}-${env:STAGE}-order-processing
        DefinitionString: !Sub |
          {
            "StartAt": "ValidateOrder",
            "States": {
              "ValidateOrder": {
                "Type": "Task",
                "Resource": "arn:aws:states:::lambda:invoke",
                "Parameters": {
                  "FunctionName": "${ValidateOrderFunction}",
                  "Payload.$": "$"
                },
                "Next": "ProcessPayment",
                "Catch": [{"ErrorEquals": ["States.ALL"], "Next": "HandleError"}]
              },
              "ProcessPayment": {
                "Type": "Task",
                "Resource": "arn:aws:states:::lambda:invoke",
                "Parameters": {
                  "FunctionName": "${ProcessPaymentFunction}",
                  "Payload.$": "$"
                },
                "Next": "UpdateInventory",
                "Retry": [{
                  "ErrorEquals": ["States.ALL"],
                  "IntervalSeconds": 2,
                  "MaxAttempts": 3,
                  "BackoffRate": 2.0
                }]
              },
              "UpdateInventory": {
                "Type": "Task",
                "Resource": "arn:aws:states:::lambda:invoke",
                "End": true
              },
              "HandleError": {
                "Type": "Task",
                "Resource": "arn:aws:states:::lambda:invoke",
                "End": true
              }
            }
          }
        RoleArn: !GetAtt StepFunctionRole.Arn
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
```

### IAM Role
```yaml
StepFunctionRole:
  Type: AWS::IAM::Role
  Properties:
    AssumeRolePolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Principal:
            Service: states.amazonaws.com
          Action: sts:AssumeRole
    Policies:
      - PolicyName: StepFunctionExecutionPolicy
        PolicyDocument:
          Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action: lambda:InvokeFunction
              Resource: 
                - !GetAtt ValidateOrderFunction.Arn
                - !GetAtt ProcessPaymentFunction.Arn
```

## Workflow Patterns

### Sequential Processing
```json
{
  "StartAt": "Step1",
  "States": {
    "Step1": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Next": "Step2"
    },
    "Step2": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "End": true
    }
  }
}
```

### Parallel Processing
```json
{
  "StartAt": "ParallelProcessing",
  "States": {
    "ParallelProcessing": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "ProcessA",
          "States": {
            "ProcessA": {"Type": "Task", "Resource": "arn:aws:states:::lambda:invoke", "End": true}
          }
        },
        {
          "StartAt": "ProcessB",
          "States": {
            "ProcessB": {"Type": "Task", "Resource": "arn:aws:states:::lambda:invoke", "End": true}
          }
        }
      ],
      "Next": "CombineResults"
    }
  }
}
```

### Map State (Bulk Processing)
```json
{
  "ProcessItems": {
    "Type": "Map",
    "ItemsPath": "$.items",
    "MaxConcurrency": 5,
    "Iterator": {
      "StartAt": "ProcessItem",
      "States": {
        "ProcessItem": {
          "Type": "Task",
          "Resource": "arn:aws:states:::lambda:invoke",
          "End": true
        }
      }
    },
    "End": true
  }
}
```

### Choice State (Conditional)
```json
{
  "CheckCondition": {
    "Type": "Choice",
    "Choices": [
      {
        "Variable": "$.orderType",
        "StringEquals": "premium",
        "Next": "PremiumProcessing"
      }
    ],
    "Default": "StandardProcessing"
  }
}
```

## Error Handling

### Retry Configuration
```json
{
  "Retry": [
    {
      "ErrorEquals": ["Lambda.ServiceException", "Lambda.AWSLambdaException"],
      "IntervalSeconds": 2,
      "MaxAttempts": 3,
      "BackoffRate": 2.0
    }
  ]
}
```

### Catch Errors
```json
{
  "Catch": [
    {
      "ErrorEquals": ["CustomError.ValidationFailed"],
      "Next": "HandleValidationError",
      "ResultPath": "$.error"
    },
    {
      "ErrorEquals": ["States.ALL"],
      "Next": "HandleGenericError",
      "ResultPath": "$.error"
    }
  ]
}
```

## Service Integrations

### EventBridge Integration
```yaml
WorkflowEventRule:
  Type: AWS::Events::Rule
  Properties:
    EventBusName: !Ref CustomEventBus
    EventPattern:
      source: ["myapp.orders"]
      detail-type: ["Order Created"]
    Targets:
      - Arn: !Ref OrderProcessingStateMachine
        Id: "OrderProcessingTarget"
        RoleArn: !GetAtt EventBridgeRole.Arn
```

### SQS Integration
```yaml
functions:
  processSQSMessage:
    handler: src/handlers/sqs.processMessage
    events:
      - sqs:
          arn: !GetAtt WorkflowQueue.Arn
          batchSize: 1
    environment:
      STATE_MACHINE_ARN: !Ref OrderProcessingStateMachine
```

## Wait States

### Fixed Duration
```json
{
  "WaitForProcessing": {
    "Type": "Wait",
    "Seconds": 30,
    "Next": "CheckStatus"
  }
}
```

### Until Timestamp
```json
{
  "WaitUntilScheduled": {
    "Type": "Wait",
    "TimestampPath": "$.scheduledTime",
    "Next": "ExecuteScheduledTask"
  }
}
```

## Data Management

### Input/Output Processing
```json
{
  "ProcessData": {
    "Type": "Task",
    "Resource": "arn:aws:states:::lambda:invoke",
    "Parameters": {
      "FunctionName": "ProcessDataFunction",
      "Payload": {
        "input.$": "$.data",
        "config.$": "$.config"
      }
    },
    "ResultPath": "$.result",
    "Next": "NextStep"
  }
}
```

### Pass State (Data Transformation)
```json
{
  "TransformData": {
    "Type": "Pass",
    "Result": {
      "processedAt.$": "$$.State.EnteredTime",
      "status": "processed"
    },
    "ResultPath": "$.metadata",
    "Next": "NextStep"
  }
}
```

## Monitoring

### Logging Configuration
```yaml
resources:
  Resources:
    StateMachineLogGroup:
      Type: AWS::Logs::LogGroup
      Properties:
        LogGroupName: /aws/stepfunctions/${self:custom.projectName}-${env:STAGE}
        RetentionInDays: 14
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
        
    OrderProcessingStateMachine:
      Type: AWS::StepFunctions::StateMachine
      Properties:
        LoggingConfiguration:
          Level: ALL
          IncludeExecutionData: true
          Destinations:
            - CloudWatchLogsLogGroup:
                LogGroupArn: !GetAtt StateMachineLogGroup.Arn
```

### CloudWatch Metrics
- Monitor execution success/failure rates
- Track execution duration and costs
- Set up alarms for failed executions
- Enable X-Ray tracing for workflow visibility

## Best Practices

### Design Patterns
- Use Express Workflows for high-volume, short-duration tasks
- Keep workflow definitions modular and reusable
- Use Map state for parallel processing of arrays
- Implement proper error handling with Catch and Retry

### Performance & Cost
- Monitor workflow costs and optimize for performance
- Use appropriate wait states for polling operations
- Implement circuit breaker patterns for external dependencies
- Version control your state machine definitions

### Observability
- Enable logging and tracing for debugging
- Monitor state transition metrics
- Track performance across state transitions
- Use input/output processing to shape data between states