# Serverless Framework - Node.js API

## Project Structure
```
serverless-node-api/
├── src/
│   ├── handlers/          # Lambda handlers
│   ├── services/          # Business logic
│   ├── models/            # Data models
│   └── utils/             # Helper functions
├── tests/
├── serverless.yml
├── package.json
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
  runtime: nodejs18.x
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
```javascript
// Entry point: src/handlers/handlerName.functionName
exports.handler = async (event, context) => {
  try {
    // Business logic
    const result = await processRequest(event);
    
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify(result)
    };
  } catch (error) {
    console.error('Handler error:', error);
    
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        error: 'Internal server error',
        message: error.message 
      })
    };
  }
};
```

## Function Configuration
```yaml
functions:
  apiHandler:
    handler: src/handlers/api.handler
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
  - serverless-esbuild
  - serverless-offline
  - serverless-domain-manager
  - serverless-plugin-warmup
```

## Dependencies
```json
{
  "dependencies": {
    "@aws-sdk/client-dynamodb": "^3.x.x",
    "@aws-sdk/lib-dynamodb": "^3.x.x",
    "uuid": "^9.x.x"
  },
  "devDependencies": {
    "serverless": "^3.x.x",
    "serverless-esbuild": "^1.x.x",
    "serverless-offline": "^12.x.x",
    "jest": "^29.x.x"
  }
}
```

## Error Handling
```javascript
// Centralized error handler
const errorHandler = (error, statusCode = 500) => {
  console.error('Error:', error);
  
  return {
    statusCode,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    },
    body: JSON.stringify({
      error: error.message || 'Internal server error',
      statusCode
    })
  };
};

// Usage in handlers
exports.handler = async (event, context) => {
  try {
    // Business logic
    return successResponse(result);
  } catch (error) {
    return errorHandler(error);
  }
};
```

## Monitoring Configuration
```yaml
provider:
  logs:
    httpApi: true
  tracing:
    lambda: true
  environment:
    AWS_NODEJS_CONNECTION_REUSE_ENABLED: 1

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
  
  # ESBuild configuration
  esbuild:
    bundle: true
    minify: true
    target: node18
    exclude:
      - aws-sdk
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
- Use async/await instead of callbacks
- Implement proper error handling and logging
- Keep functions small and focused
- Use environment variables for configuration
- Separate business logic from handlers

### Performance
- Enable connection reuse with `AWS_NODEJS_CONNECTION_REUSE_ENABLED`
- Use AWS SDK v3 for better performance
- Configure appropriate timeout and memory settings
- Use bundling with esbuild for smaller packages

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