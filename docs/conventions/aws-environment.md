# Updated AWS Conventions with VPC Variables

## Environment Variables
```bash
PROJECT_NAME=my-awesome-app
STAGE=dev
REGION=us-east-1
OWNER=John Doe abc123
LOG_LEVEL=INFO
AWS_PROFILE=my-profile
VPC=vpc-1234567890abcdef0
PUBLIC_SUBNET=subnet-1234567890abcdef0
PRIVATE_SUBNET=subnet-0987654321fedcba0
```

## AWS Profile Configuration
```yaml
# Use when AWS_PROFILE is set
provider:
  name: aws
  runtime: python3.11
  stage: ${env:STAGE}
  region: ${env:REGION}
  profile: ${env:AWS_PROFILE, ''}
```

## ECS Fargate with External VPC
```yaml
# Task Definition - use existing VPC/subnets
ECSService:
  Type: AWS::ECS::Service
  Properties:
    ServiceName: ${self:custom.projectName}-${env:STAGE}-service
    Cluster: !Ref ECSCluster
    TaskDefinition: !Ref TaskDefinition
    DesiredCount: 2
    LaunchType: FARGATE
    NetworkConfiguration:
      AwsvpcConfiguration:
        SecurityGroups:
          - !Ref ECSSecurityGroup
        Subnets:
          - ${env:PRIVATE_SUBNET}
        AssignPublicIp: DISABLED

# ALB in public subnet
ApplicationLoadBalancer:
  Type: AWS::ElasticLoadBalancingV2::LoadBalancer
  Properties:
    Name: ${self:custom.projectName}-${env:STAGE}-alb
    Scheme: internet-facing
    Type: application
    SecurityGroups:
      - !Ref ALBSecurityGroup
    Subnets:
      - ${env:PUBLIC_SUBNET}

# Security groups for existing VPC
ECSSecurityGroup:
  Type: AWS::EC2::SecurityGroup
  Properties:
    GroupName: ${self:custom.projectName}-${env:STAGE}-ecs-sg
    GroupDescription: ECS Fargate Security Group
    VpcId: ${env:VPC}
    SecurityGroupIngress:
      - IpProtocol: tcp
        FromPort: 8000
        ToPort: 8000
        SourceSecurityGroupId: !Ref ALBSecurityGroup

ALBSecurityGroup:
  Type: AWS::EC2::SecurityGroup
  Properties:
    GroupName: ${self:custom.projectName}-${env:STAGE}-alb-sg
    GroupDescription: ALB Security Group
    VpcId: ${env:VPC}
    SecurityGroupIngress:
      - IpProtocol: tcp
        FromPort: 80
        ToPort: 80
        CidrIp: 0.0.0.0/0
      - IpProtocol: tcp
        FromPort: 443
        ToPort: 443
        CidrIp: 0.0.0.0/0
```

## Serverless Framework with External VPC
```yaml
service: ${self:custom.projectName}-${env:STAGE}

provider:
  name: aws
  runtime: python3.11
  stage: ${env:STAGE}
  region: ${env:REGION}
  profile: ${env:AWS_PROFILE, ''}
  vpc:
    securityGroupIds:
      - !Ref LambdaSecurityGroup
    subnetIds:
      - ${env:PRIVATE_SUBNET}

custom:
  projectName: ${env:PROJECT_NAME}

functions:
  apiHandler:
    handler: src/handlers/api.lambda_handler
    vpc:
      securityGroupIds:
        - !Ref LambdaSecurityGroup
      subnetIds:
        - ${env:PRIVATE_SUBNET}
    environment:
      VPC_ID: ${env:VPC}
      PRIVATE_SUBNET: ${env:PRIVATE_SUBNET}
      PUBLIC_SUBNET: ${env:PUBLIC_SUBNET}

resources:
  Resources:
    # Lambda Security Group for existing VPC
    LambdaSecurityGroup:
      Type: AWS::EC2::SecurityGroup
      Properties:
        GroupName: ${self:custom.projectName}-${env:STAGE}-lambda-sg
        GroupDescription: Lambda functions security group
        VpcId: ${env:VPC}
        SecurityGroupEgress:
          - IpProtocol: -1
            CidrIp: 0.0.0.0/0

    # RDS in existing VPC
    RDSSecurityGroup:
      Type: AWS::EC2::SecurityGroup
      Properties:
        GroupName: ${self:custom.projectName}-${env:STAGE}-rds-sg
        GroupDescription: RDS security group
        VpcId: ${env:VPC}
        SecurityGroupIngress:
          - IpProtocol: tcp
            FromPort: 5432
            ToPort: 5432
            SourceSecurityGroupId: !Ref LambdaSecurityGroup

    # RDS using existing subnet
    DBSubnetGroup:
      Type: AWS::RDS::DBSubnetGroup
      Properties:
        DBSubnetGroupName: ${self:custom.projectName}-${env:STAGE}-db-subnet
        DBSubnetGroupDescription: Subnet group for RDS
        SubnetIds:
          - ${env:PRIVATE_SUBNET}
```

## SQS with External VPC Access
```yaml
# SQS resources remain the same - no VPC dependency
ProcessingQueue:
  Type: AWS::SQS::Queue
  Properties:
    QueueName: ${self:custom.projectName}-${env:STAGE}-processing
    VisibilityTimeoutSeconds: 300
    MessageRetentionPeriod: 1209600
    DelaySeconds: 0
    ReceiveMessageWaitTimeSeconds: 20
    RedrivePolicy:
      deadLetterTargetArn: !GetAtt ProcessingDLQ.Arn
      maxReceiveCount: 3
    KmsMasterKeyId: alias/aws/sqs

# Lambda processing SQS in VPC
functions:
  processMessages:
    handler: src/handlers/queue.processMessages
    timeout: 50
    vpc:
      securityGroupIds:
        - !Ref LambdaSecurityGroup
      subnetIds:
        - ${env:PRIVATE_SUBNET}
    environment:
      QUEUE_URL: !Ref ProcessingQueue
    events:
      - sqs:
          arn: !GetAtt ProcessingQueue.Arn
          batchSize: 10
```

## AWS CLI Profile Usage
```bash
# When AWS_PROFILE is set
export AWS_PROFILE=${AWS_PROFILE}
aws sts get-caller-identity

# Deploy with profile
serverless deploy --stage ${STAGE} --aws-profile ${AWS_PROFILE}

# When AWS_PROFILE is empty (IAM role on EC2/ECS)
unset AWS_PROFILE
aws sts get-caller-identity
serverless deploy --stage ${STAGE}
```

## Key Changes Summary

### Environment Variables Added
- `AWS_PROFILE`: AWS credentials profile (empty for IAM role)
- `VPC`: Existing VPC ID to use
- `PUBLIC_SUBNET`: Public subnet for ALBs, NAT gateways
- `PRIVATE_SUBNET`: Private subnet for Lambda, ECS, RDS

### VPC Resources Removed
- No longer create VPC, subnets, IGW, NAT gateways
- Use existing infrastructure via environment variables
- All stages share the same VPC/subnets

### Security Groups Updated
- Reference existing VPC via `${env:VPC}`
- Maintain same security group patterns
- Use existing subnets via `${env:PRIVATE_SUBNET}` and `${env:PUBLIC_SUBNET}`

### Serverless Framework Changes
- Add profile configuration with fallback to empty
- Use existing VPC/subnet references
- Remove VPC creation resources
- Maintain same function patterns

### Benefits
- Faster deployments (no VPC creation)
- Consistent networking across stages
- Reduced costs (shared infrastructure)
- Simplified resource management