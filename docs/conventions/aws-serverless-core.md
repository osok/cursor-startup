# AWS Serverless Core Services

## Environment Variables
```bash
PROJECT_NAME=my-awesome-app
STAGE=dev
REGION=us-east-1
OWNER=John Doe abc123
LOG_LEVEL=INFO
```

## Lambda Functions

### Serverless.yml Pattern
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

custom:
  projectName: ${env:PROJECT_NAME}
    
functions:
  apiFunction:
    handler: src/handlers/api.handler
    memorySize: 256
    timeout: 30
    environment:
      TABLE_NAME: ${self:custom.tableName}
    events:
      - httpApi:
          path: /api/{proxy+}
          method: ANY
```

### Configuration Standards
- Runtime: `python3.11` or `nodejs18.x`
- Memory: 128MB minimum, scale based on workload
- Timeout: 30s for API, 15min for batch processing
- Environment variables for configuration
- Reserved concurrency for critical functions
- Enable X-Ray tracing for debugging

## API Gateway

### HTTP API Configuration
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
      cognitoAuthorizer:
        type: jwt
        identitySource: $request.header.Authorization
        issuerUrl: !GetAtt CognitoUserPool.ProviderURL
        audience:
          - !Ref CognitoUserPoolClient
```

### Custom Domain
- Use `serverless-domain-manager` plugin
- Configure certificate in ACM
- Set up Route 53 records
- Enable compression and caching

## DynamoDB

### Table Configuration
```yaml
resources:
  Resources:
    UsersTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:custom.projectName}-${env:STAGE}-users
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: id
            AttributeType: S
        KeySchema:
          - AttributeName: id
            KeyType: HASH
        StreamSpecification:
          StreamViewType: NEW_AND_OLD_IMAGES
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
```

### Best Practices
- Use single table design when possible
- Enable point-in-time recovery for production
- Use Global Secondary Indexes sparingly
- Configure streams for change data capture
- Use composite keys for complex queries

## S3 Storage

### Bucket Configuration
```yaml
resources:
  Resources:
    S3Bucket:
      Type: AWS::S3::Bucket
      Properties:
        BucketName: ${self:custom.projectName}-${env:STAGE}-storage
        VersioningConfiguration:
          Status: Enabled
        PublicAccessBlockConfiguration:
          BlockPublicAcls: true
          BlockPublicPolicy: true
          IgnorePublicAcls: true
          RestrictPublicBuckets: true
        NotificationConfiguration:
          LambdaConfigurations:
            - Event: s3:ObjectCreated:*
              Function: !GetAtt ProcessFileFunction.Arn
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
```

### Best Practices
- Block public access by default
- Enable versioning for important data
- Use lifecycle policies for cost optimization
- Configure event notifications for processing
- Use presigned URLs for secure access

## CloudWatch

### Log Groups
```yaml
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

### Alarms
```yaml
resources:
  Resources:
    ErrorAlarm:
      Type: AWS::CloudWatch::Alarm
      Properties:
        AlarmName: ${self:service}-${env:STAGE}-errors
        AlarmDescription: Lambda function errors
        MetricName: Errors
        Namespace: AWS/Lambda
        Statistic: Sum
        Period: 300
        EvaluationPeriods: 2
        Threshold: 5
        ComparisonOperator: GreaterThanThreshold
        Dimensions:
          - Name: FunctionName
            Value: !Ref ApiFunction
```

## EFS (Elastic File System)

### Configuration
```yaml
resources:
  Resources:
    EFSFileSystem:
      Type: AWS::EFS::FileSystem
      Properties:
        FileSystemTags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-efs
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
        
    EFSAccessPoint:
      Type: AWS::EFS::AccessPoint
      Properties:
        FileSystemId: !Ref EFSFileSystem
        PosixUser:
          Uid: 1000
          Gid: 1000
        RootDirectory:
          Path: /lambda
          CreationInfo:
            OwnerUid: 1000
            OwnerGid: 1000
            Permissions: 755
```

### Lambda Integration
```yaml
functions:
  processFiles:
    handler: src/handlers/files.handler
    fileSystemConfig:
      localMountPath: /mnt/efs
      arn: !GetAtt EFSAccessPoint.Arn
    vpc:
      securityGroupIds:
        - !Ref EFSSecurityGroup
      subnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
```

## Resource Tagging Standards
All resources must include these tags:
- `Owner: ${env:OWNER}`
- `env: ${self:custom.projectName}`
- `service: ${self:service}`
- `stage: ${env:STAGE}`

## IAM Best Practices
- Use least privilege principle
- Create specific roles for each function type
- Use managed policies when possible
- Resource-level permissions with ARN patterns
- Regular review and cleanup of unused permissions

## Monitoring & Observability
- Enable X-Ray tracing for all functions
- Create custom metrics for business logic
- Set up CloudWatch alarms for critical metrics
- Use structured logging with correlation IDs
- Implement health check endpoints

## Security
- Use AWS Systems Manager Parameter Store for secrets
- Enable encryption at rest and in transit
- Configure VPC endpoints for private communication
- Regular security audits and dependency updates
- Use AWS Config for compliance monitoring