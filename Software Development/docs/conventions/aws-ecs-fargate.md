# ECS Fargate Conventions

## Environment Variables

View the `docs/conventions/aws-environment.md` for more about how the VPC, public and private subnets will be defined.

```bash
PROJECT_NAME=my-awesome-app
STAGE=dev
REGION=us-east-1
OWNER=John Doe abc123
LOG_LEVEL=INFO
VPC_CIDR=10.0.0.0/16
```

## ECS Cluster Configuration
```yaml
resources:
  Resources:
    ECSCluster:
      Type: AWS::ECS::Cluster
      Properties:
        ClusterName: ${self:custom.projectName}-${env:STAGE}
        CapacityProviders:
          - FARGATE
          - FARGATE_SPOT
        DefaultCapacityProviderStrategy:
          - CapacityProvider: FARGATE
            Weight: 1
        ClusterSettings:
          - Name: containerInsights
            Value: enabled
        Tags:
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
```

## Task Definition
```yaml
TaskDefinition:
  Type: AWS::ECS::TaskDefinition
  Properties:
    Family: ${self:custom.projectName}-${env:STAGE}-app
    NetworkMode: awsvpc
    RequiresCompatibilities:
      - FARGATE
    Cpu: 256
    Memory: 512
    ExecutionRoleArn: !Ref TaskExecutionRole
    TaskRoleArn: !Ref TaskRole
    ContainerDefinitions:
      - Name: app
        Image: ${env:DOCKER_IMAGE}:${env:STAGE}
        Essential: true
        PortMappings:
          - ContainerPort: 8000
            Protocol: tcp
        Environment:
          - Name: STAGE
            Value: ${env:STAGE}
          - Name: PROJECT_NAME
            Value: ${env:PROJECT_NAME}
        LogConfiguration:
          LogDriver: awslogs
          Options:
            awslogs-group: !Ref LogGroup
            awslogs-region: ${env:REGION}
            awslogs-stream-prefix: ecs
        HealthCheck:
          Command:
            - CMD-SHELL
            - curl -f http://localhost:8000/health || exit 1
          Interval: 30
          Timeout: 5
          Retries: 3
    Tags:
      - Key: Owner
        Value: ${env:OWNER}
      - Key: env
        Value: ${self:custom.projectName}
      - Key: stage
        Value: ${env:STAGE}
```

## ECS Service
```yaml
ECSService:
  Type: AWS::ECS::Service
  Properties:
    ServiceName: ${self:custom.projectName}-${env:STAGE}-service
    Cluster: !Ref ECSCluster
    TaskDefinition: !Ref TaskDefinition
    DesiredCount: 2
    LaunchType: FARGATE
    PlatformVersion: LATEST
    NetworkConfiguration:
      AwsvpcConfiguration:
        SecurityGroups:
          - !Ref ECSSecurityGroup
        Subnets:
          - !Ref PrivateSubnet1
          - !Ref PrivateSubnet2
        AssignPublicIp: DISABLED
    LoadBalancers:
      - TargetGroupArn: !Ref TargetGroup
        ContainerName: app
        ContainerPort: 8000
    HealthCheckGracePeriodSeconds: 300
    DeploymentConfiguration:
      MaximumPercent: 200
      MinimumHealthyPercent: 50
      DeploymentCircuitBreaker:
        Enable: true
        Rollback: true
    Tags:
      - Key: Owner
        Value: ${env:OWNER}
      - Key: env
        Value: ${self:custom.projectName}
      - Key: stage
        Value: ${env:STAGE}
```

## Application Load Balancer
```yaml
ApplicationLoadBalancer:
  Type: AWS::ElasticLoadBalancingV2::LoadBalancer
  Properties:
    Name: ${self:custom.projectName}-${env:STAGE}-alb
    Scheme: internet-facing
    Type: application
    SecurityGroups:
      - !Ref ALBSecurityGroup
    Subnets:
      - !Ref PublicSubnet1
      - !Ref PublicSubnet2
    Tags:
      - Key: Owner
        Value: ${env:OWNER}
      - Key: env
        Value: ${self:custom.projectName}
      - Key: stage
        Value: ${env:STAGE}

TargetGroup:
  Type: AWS::ElasticLoadBalancingV2::TargetGroup
  Properties:
    Name: ${self:custom.projectName}-${env:STAGE}-tg
    Port: 8000
    Protocol: HTTP
    TargetType: ip
    VpcId: !Ref VPC
    HealthCheckPath: /health
    HealthCheckIntervalSeconds: 30
    HealthyThresholdCount: 2
    UnhealthyThresholdCount: 5
    Tags:
      - Key: Owner
        Value: ${env:OWNER}
      - Key: env
        Value: ${self:custom.projectName}
      - Key: stage
        Value: ${env:STAGE}

Listener:
  Type: AWS::ElasticLoadBalancingV2::Listener
  Properties:
    DefaultActions:
      - Type: forward
        TargetGroupArn: !Ref TargetGroup
    LoadBalancerArn: !Ref ApplicationLoadBalancer
    Port: 80
    Protocol: HTTP
```

## IAM Roles
```yaml
TaskExecutionRole:
  Type: AWS::IAM::Role
  Properties:
    RoleName: ${self:custom.projectName}-${env:STAGE}-execution-role
    AssumeRolePolicyDocument:
      Statement:
        - Effect: Allow
          Principal:
            Service: ecs-tasks.amazonaws.com
          Action: sts:AssumeRole
    ManagedPolicyArns:
      - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
    Policies:
      - PolicyName: SecretsAccess
        PolicyDocument:
          Statement:
            - Effect: Allow
              Action:
                - secretsmanager:GetSecretValue
              Resource: !Sub "arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:${self:custom.projectName}/${env:STAGE}/*"

TaskRole:
  Type: AWS::IAM::Role
  Properties:
    RoleName: ${self:custom.projectName}-${env:STAGE}-task-role
    AssumeRolePolicyDocument:
      Statement:
        - Effect: Allow
          Principal:
            Service: ecs-tasks.amazonaws.com
          Action: sts:AssumeRole
    Policies:
      - PolicyName: ApplicationAccess
        PolicyDocument:
          Statement:
            - Effect: Allow
              Action:
                - dynamodb:Query
                - dynamodb:GetItem
                - dynamodb:PutItem
              Resource: !Sub "arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/${self:custom.projectName}-${env:STAGE}-*"
```

## Security Groups
```yaml
ECSSecurityGroup:
  Type: AWS::EC2::SecurityGroup
  Properties:
    GroupName: ${self:custom.projectName}-${env:STAGE}-ecs-sg
    GroupDescription: ECS Fargate Security Group
    VpcId: !Ref VPC
    SecurityGroupIngress:
      - IpProtocol: tcp
        FromPort: 8000
        ToPort: 8000
        SourceSecurityGroupId: !Ref ALBSecurityGroup
    Tags:
      - Key: Owner
        Value: ${env:OWNER}
      - Key: env
        Value: ${self:custom.projectName}
      - Key: stage
        Value: ${env:STAGE}

ALBSecurityGroup:
  Type: AWS::EC2::SecurityGroup
  Properties:
    GroupName: ${self:custom.projectName}-${env:STAGE}-alb-sg
    GroupDescription: ALB Security Group
    VpcId: !Ref VPC
    SecurityGroupIngress:
      - IpProtocol: tcp
        FromPort: 80
        ToPort: 80
        CidrIp: 0.0.0.0/0
      - IpProtocol: tcp
        FromPort: 443
        ToPort: 443
        CidrIp: 0.0.0.0/0
    Tags:
      - Key: Owner
        Value: ${env:OWNER}
      - Key: env
        Value: ${self:custom.projectName}
      - Key: stage
        Value: ${env:STAGE}
```

## Auto Scaling
```yaml
ServiceScalingTarget:
  Type: AWS::ApplicationAutoScaling::ScalableTarget
  Properties:
    MaxCapacity: 10
    MinCapacity: 2
    ResourceId: !Sub "service/${ECSCluster}/${ECSService.Name}"
    RoleARN: !Sub "arn:aws:iam::${AWS::AccountId}:role/aws-service-role/ecs.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_ECSService"
    ScalableDimension: ecs:service:DesiredCount
    ServiceNamespace: ecs

ServiceScalingPolicy:
  Type: AWS::ApplicationAutoScaling::ScalingPolicy
  Properties:
    PolicyName: ${self:custom.projectName}-${env:STAGE}-scaling-policy
    PolicyType: TargetTrackingScaling
    ScalingTargetId: !Ref ServiceScalingTarget
    TargetTrackingScalingPolicyConfiguration:
      PredefinedMetricSpecification:
        PredefinedMetricType: ECSServiceAverageCPUUtilization
      TargetValue: 70
      ScaleOutCooldown: 300
      ScaleInCooldown: 300
```

## CloudWatch Logs
```yaml
LogGroup:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: /ecs/${self:custom.projectName}-${env:STAGE}
    RetentionInDays: 14
    Tags:
      - Key: Owner
        Value: ${env:OWNER}
      - Key: env
        Value: ${self:custom.projectName}
      - Key: stage
        Value: ${env:STAGE}
```

## Best Practices
- Use Fargate for serverless container management
- Enable container insights for monitoring
- Implement health checks for all containers
- Use private subnets for ECS tasks
- Configure auto scaling based on CPU/memory
- Enable deployment circuit breaker for safety
- Use secrets manager for sensitive data
- Monitor with CloudWatch and X-Ray
- Implement proper security group rules
- Use target tracking scaling policies