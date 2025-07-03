# Serverless Framework - Python API

## Project Structure
```
serverless-api/
├── src/
│   ├── handlers/          # Lambda handlers
│   ├── services/          # Business logic
│   ├── models/            # Data models
│   └── utils/             # Helper functions
├── tests/
├── serverless.yml
├── requirements.txt
├── .env
└── README.md
```

## Environment Variables
```bash
PROJECT_NAME=my-awesome-app
STAGE=dev
REGION=us-east-1
OWNER=John Doe abc123
LOG_LEVEL=INFO
```

## Serverless Configuration
```yaml
service: ${self:custom.projectName}-${env:STAGE}

provider:
  name: aws
  runtime: python3.11
  stage: ${env:STAGE}
  region: ${env:REGION}
  environment:
    STAGE: ${env:STAGE}
    PROJECT_NAME: ${env:PROJECT_NAME}
    LOG_LEVEL: ${env:LOG_LEVEL}

custom:
  projectName: ${env:PROJECT_NAME}
  stage: ${env:STAGE}
  region: ${env:REGION}
```

## Handler Patterns
```python
# Entry point: src/handlers/handler_name.function_name
import json
import logging

logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    try:
        # Business logic
        result = process_request(event)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
    except Exception as error:
        logger.error(f'Handler error: {error}', exc_info=True)
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(error)
            })
        }

def process_request(event):
    # Business logic implementation
    return {'message': 'Success'}
```

## Function Configuration
```yaml
functions:
  apiHandler:
    handler: src/handlers/api.lambda_handler
    memorySize: 256
    timeout: 30
    environment:
      TABLE_NAME: ${self:custom.projectName}-${env:STAGE}-table
    events:
      - httpApi:
          path: /api/{proxy+}
          method: ANY
    iamRoleStatements:
      - Effect: Allow
        Action:
          - dynamodb:Query
          - dynamodb:GetItem
        Resource: !GetAtt DynamoTable.Arn
```

## API Gateway Configuration
```yaml
provider:
  httpApi:
    cors:
      allowedOrigins:
        - https://example.com
      allowedHeaders:
        - Content-Type
        - Authorization
      allowedMethods:
        - GET
        - POST
        - PUT
        - DELETE
    authorizers:
      jwtAuthorizer:
        type: jwt
        identitySource: $request.header.Authorization
        issuerUrl: https://cognito-idp.us-east-1.amazonaws.com/us-east-1_example
        audience:
          - client-id
```

## Resource Configuration
```yaml
resources:
  Resources:
    DynamoTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:custom.projectName}-${env:STAGE}-table
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: id
            AttributeType: S
        KeySchema:
          - AttributeName: id
            KeyType: HASH
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
```

## Package Configuration
```yaml
package:
  include:
    - src/**
  exclude:
    - tests/**
    - node_modules/**
    - .env
    - README.md
```

## Plugins
```yaml
plugins:
  - serverless-python-requirements
  - serverless-offline
  - serverless-domain-manager
  - serverless-plugin-warmup

custom:
  pythonRequirements:
    dockerizePip: true
    slim: true
    strip: false
    noDeploy:
      - boto3
      - botocore
```

## Dependencies
```txt
# requirements.txt
boto3>=1.26.0
pydantic>=2.0.0
requests>=2.28.0
python-dotenv>=1.0.0
```

## Error Handling
```python
# Centralized error handler
import json
import logging

logger = logging.getLogger(__name__)

def error_handler(error, status_code=500):
    logger.error(f'Error: {error}', exc_info=True)
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'error': str(error),
            'statusCode': status_code
        })
    }

# Usage in handlers
def lambda_handler(event, context):
    try:
        # Business logic
        return success_response(result)
    except ValidationError as e:
        return error_handler(e, 400)
    except Exception as e:
        return error_handler(e, 500)
```

## Monitoring Configuration
```yaml
provider:
  logs:
    httpApi: true
  tracing:
    lambda: true

resources:
  Resources:
    LogGroup:
      Type: AWS::Logs::LogGroup
      Properties:
        LogGroupName: /aws/lambda/${self:service}-${env:STAGE}
        RetentionInDays: 14
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
```

## IAM Permissions
```yaml
provider:
  iamRoleStatements:
    - Effect: Allow
      Action:
        - dynamodb:Query
        - dynamodb:GetItem
        - dynamodb:PutItem
        - dynamodb:UpdateItem
        - dynamodb:DeleteItem
      Resource: 
        - !GetAtt DynamoTable.Arn
        - !Sub "${DynamoTable.Arn}/index/*"
    - Effect: Allow
      Action:
        - logs:CreateLogGroup
        - logs:CreateLogStream
        - logs:PutLogEvents
      Resource: !Sub "arn:aws:logs:${AWS::Region}:${AWS::AccountId}:*"
```

## Custom Variables
```yaml
custom:
  projectName: ${env:PROJECT_NAME}
  stage: ${env:STAGE}
  region: ${env:REGION}
  
  # Stage-specific configurations
  dev:
    memorySize: 128
    timeout: 30
  prod:
    memorySize: 512
    timeout: 30
  
  # Python requirements configuration
  pythonRequirements:
    dockerizePip: true
    slim: true
    strip: false
    noDeploy:
      - boto3
      - botocore
```

## Deployment
```bash
# Deploy to specific stage
serverless deploy --stage dev

# Deploy with verbose output
serverless deploy --stage prod --verbose

# Rollback deployment
serverless rollback --timestamp 2024-01-01T12:00:00.000Z --stage prod

# Remove service
serverless remove --stage dev
```

## Best Practices

### Code Organization
- Keep functions small and focused
- Use proper Python module structure
- Implement proper error handling and logging
- Use environment variables for configuration
- Separate business logic from handlers

### Performance
- Use `dockerizePip: true` for native dependencies
- Enable `slim: true` for smaller packages
- Configure appropriate timeout and memory settings
- Use layers for shared dependencies

### Security
- Use least privilege IAM permissions
- Store sensitive data in AWS Systems Manager
- Implement proper CORS configuration
- Validate and sanitize all inputs
- Regular security updates for dependencies

### Monitoring
- Enable X-Ray tracing for debugging
- Configure CloudWatch alarms for errors
- Use structured logging with correlation IDs
- Monitor cold start times and memory usage

### Deployment
- Use separate stages for dev, qa, prod
- Version control serverless.yml configurations
- Implement proper rollback strategies
- Use custom domains for production APIs