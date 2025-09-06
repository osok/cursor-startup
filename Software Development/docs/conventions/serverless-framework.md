# Serverless Framework VPC Conventions

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

## VPC Configuration
```yaml
service: ${self:custom.projectName}-${env:STAGE}

provider:
  name: aws
  runtime: python3.11
  stage: ${env:STAGE}
  region: ${env:REGION}
  vpc:
    securityGroupIds:
      - !Ref LambdaSecurityGroup
    subnetIds:
      - !Ref PrivateSubnet1
      - !Ref PrivateSubnet2

custom:
  projectName: ${env:PROJECT_NAME}
  vpcCidr: ${env:VPC_CIDR, '10.0.0.0/16'}
```

## VPC Resources
```yaml
resources:
  Resources:
    # VPC
    VPC:
      Type: AWS::EC2::VPC
      Properties:
        CidrBlock: ${self:custom.vpcCidr}
        EnableDnsHostnames: true
        EnableDnsSupport: true
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-vpc
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    # Internet Gateway
    InternetGateway:
      Type: AWS::EC2::InternetGateway
      Properties:
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-igw
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    InternetGatewayAttachment:
      Type: AWS::EC2::VPCGatewayAttachment
      Properties:
        InternetGatewayId: !Ref InternetGateway
        VpcId: !Ref VPC

    # Public Subnets
    PublicSubnet1:
      Type: AWS::EC2::Subnet
      Properties:
        VpcId: !Ref VPC
        AvailabilityZone: !Select [0, !GetAZs '']
        CidrBlock: !Select [0, !Cidr [!Ref VPC, 4, 8]]
        MapPublicIpOnLaunch: true
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-public-1
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    PublicSubnet2:
      Type: AWS::EC2::Subnet
      Properties:
        VpcId: !Ref VPC
        AvailabilityZone: !Select [1, !GetAZs '']
        CidrBlock: !Select [1, !Cidr [!Ref VPC, 4, 8]]
        MapPublicIpOnLaunch: true
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-public-2
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    # Private Subnets
    PrivateSubnet1:
      Type: AWS::EC2::Subnet
      Properties:
        VpcId: !Ref VPC
        AvailabilityZone: !Select [0, !GetAZs '']
        CidrBlock: !Select [2, !Cidr [!Ref VPC, 4, 8]]
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-private-1
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    PrivateSubnet2:
      Type: AWS::EC2::Subnet
      Properties:
        VpcId: !Ref VPC
        AvailabilityZone: !Select [1, !GetAZs '']
        CidrBlock: !Select [3, !Cidr [!Ref VPC, 4, 8]]
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-private-2
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    # NAT Gateways
    NatGateway1EIP:
      Type: AWS::EC2::EIP
      DependsOn: InternetGatewayAttachment
      Properties:
        Domain: vpc
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-nat-eip-1
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    NatGateway2EIP:
      Type: AWS::EC2::EIP
      DependsOn: InternetGatewayAttachment
      Properties:
        Domain: vpc
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-nat-eip-2
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    NatGateway1:
      Type: AWS::EC2::NatGateway
      Properties:
        AllocationId: !GetAtt NatGateway1EIP.AllocationId
        SubnetId: !Ref PublicSubnet1
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-nat-1
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    NatGateway2:
      Type: AWS::EC2::NatGateway
      Properties:
        AllocationId: !GetAtt NatGateway2EIP.AllocationId
        SubnetId: !Ref PublicSubnet2
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-nat-2
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    # Route Tables
    PublicRouteTable:
      Type: AWS::EC2::RouteTable
      Properties:
        VpcId: !Ref VPC
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-public-rt
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    DefaultPublicRoute:
      Type: AWS::EC2::Route
      DependsOn: InternetGatewayAttachment
      Properties:
        RouteTableId: !Ref PublicRouteTable
        DestinationCidrBlock: 0.0.0.0/0
        GatewayId: !Ref InternetGateway

    PublicSubnet1RouteTableAssociation:
      Type: AWS::EC2::SubnetRouteTableAssociation
      Properties:
        RouteTableId: !Ref PublicRouteTable
        SubnetId: !Ref PublicSubnet1

    PublicSubnet2RouteTableAssociation:
      Type: AWS::EC2::SubnetRouteTableAssociation
      Properties:
        RouteTableId: !Ref PublicRouteTable
        SubnetId: !Ref PublicSubnet2

    PrivateRouteTable1:
      Type: AWS::EC2::RouteTable
      Properties:
        VpcId: !Ref VPC
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-private-rt-1
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    DefaultPrivateRoute1:
      Type: AWS::EC2::Route
      Properties:
        RouteTableId: !Ref PrivateRouteTable1
        DestinationCidrBlock: 0.0.0.0/0
        NatGatewayId: !Ref NatGateway1

    PrivateSubnet1RouteTableAssociation:
      Type: AWS::EC2::SubnetRouteTableAssociation
      Properties:
        RouteTableId: !Ref PrivateRouteTable1
        SubnetId: !Ref PrivateSubnet1

    PrivateRouteTable2:
      Type: AWS::EC2::RouteTable
      Properties:
        VpcId: !Ref VPC
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-private-rt-2
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    DefaultPrivateRoute2:
      Type: AWS::EC2::Route
      Properties:
        RouteTableId: !Ref PrivateRouteTable2
        DestinationCidrBlock: 0.0.0.0/0
        NatGatewayId: !Ref NatGateway2

    PrivateSubnet2RouteTableAssociation:
      Type: AWS::EC2::SubnetRouteTableAssociation
      Properties:
        RouteTableId: !Ref PrivateRouteTable2
        SubnetId: !Ref PrivateSubnet2
```

## Security Groups
```yaml
resources:
  Resources:
    # Lambda Security Group
    LambdaSecurityGroup:
      Type: AWS::EC2::SecurityGroup
      Properties:
        GroupName: ${self:custom.projectName}-${env:STAGE}-lambda-sg
        GroupDescription: Lambda functions security group
        VpcId: !Ref VPC
        SecurityGroupEgress:
          - IpProtocol: -1
            CidrIp: 0.0.0.0/0
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-lambda-sg
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    # RDS Security Group
    RDSSecurityGroup:
      Type: AWS::EC2::SecurityGroup
      Properties:
        GroupName: ${self:custom.projectName}-${env:STAGE}-rds-sg
        GroupDescription: RDS security group
        VpcId: !Ref VPC
        SecurityGroupIngress:
          - IpProtocol: tcp
            FromPort: 5432
            ToPort: 5432
            SourceSecurityGroupId: !Ref LambdaSecurityGroup
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-rds-sg
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    # ALB Security Group
    ALBSecurityGroup:
      Type: AWS::EC2::SecurityGroup
      Properties:
        GroupName: ${self:custom.projectName}-${env:STAGE}-alb-sg
        GroupDescription: ALB security group
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
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-alb-sg
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
```

## VPC Endpoints
```yaml
resources:
  Resources:
    # S3 VPC Endpoint
    S3VPCEndpoint:
      Type: AWS::EC2::VPCEndpoint
      Properties:
        VpcId: !Ref VPC
        ServiceName: !Sub com.amazonaws.${AWS::Region}.s3
        VpcEndpointType: Gateway
        RouteTableIds:
          - !Ref PrivateRouteTable1
          - !Ref PrivateRouteTable2

    # DynamoDB VPC Endpoint
    DynamoDBVPCEndpoint:
      Type: AWS::EC2::VPCEndpoint
      Properties:
        VpcId: !Ref VPC
        ServiceName: !Sub com.amazonaws.${AWS::Region}.dynamodb
        VpcEndpointType: Gateway
        RouteTableIds:
          - !Ref PrivateRouteTable1
          - !Ref PrivateRouteTable2

    # Lambda VPC Endpoint
    LambdaVPCEndpoint:
      Type: AWS::EC2::VPCEndpoint
      Properties:
        VpcId: !Ref VPC
        ServiceName: !Sub com.amazonaws.${AWS::Region}.lambda
        VpcEndpointType: Interface
        SubnetIds:
          - !Ref PrivateSubnet1
          - !Ref PrivateSubnet2
        SecurityGroupIds:
          - !Ref VPCEndpointSecurityGroup
        PolicyDocument:
          Statement:
            - Effect: Allow
              Principal: '*'
              Action:
                - lambda:InvokeFunction
              Resource: '*'

    # VPC Endpoint Security Group
    VPCEndpointSecurityGroup:
      Type: AWS::EC2::SecurityGroup
      Properties:
        GroupName: ${self:custom.projectName}-${env:STAGE}-vpce-sg
        GroupDescription: VPC Endpoint security group
        VpcId: !Ref VPC
        SecurityGroupIngress:
          - IpProtocol: tcp
            FromPort: 443
            ToPort: 443
            SourceSecurityGroupId: !Ref LambdaSecurityGroup
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-vpce-sg
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
```

## Function Configuration
```yaml
functions:
  apiHandler:
    handler: src/handlers/api.handler
    vpc:
      securityGroupIds:
        - !Ref LambdaSecurityGroup
      subnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
    environment:
      VPC_ID: !Ref VPC
      PRIVATE_SUBNET_1: !Ref PrivateSubnet1
      PRIVATE_SUBNET_2: !Ref PrivateSubnet2

  databaseFunction:
    handler: src/handlers/database.handler
    vpc:
      securityGroupIds:
        - !Ref LambdaSecurityGroup
      subnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
    environment:
      DB_HOST: !GetAtt RDSInstance.Endpoint.Address
```

## RDS in VPC
```yaml
resources:
  Resources:
    DBSubnetGroup:
      Type: AWS::RDS::DBSubnetGroup
      Properties:
        DBSubnetGroupName: ${self:custom.projectName}-${env:STAGE}-db-subnet
        DBSubnetGroupDescription: Subnet group for RDS
        SubnetIds:
          - !Ref PrivateSubnet1
          - !Ref PrivateSubnet2
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-db-subnet
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}

    RDSInstance:
      Type: AWS::RDS::DBInstance
      Properties:
        DBInstanceIdentifier: ${self:custom.projectName}-${env:STAGE}
        DBInstanceClass: db.t3.micro
        Engine: postgres
        MasterUsername: admin
        MasterUserPassword: !Ref DBPassword
        AllocatedStorage: 20
        VPCSecurityGroups:
          - !Ref RDSSecurityGroup
        DBSubnetGroupName: !Ref DBSubnetGroup
        BackupRetentionPeriod: 7
        MultiAZ: false
        PubliclyAccessible: false
        StorageEncrypted: true
        Tags:
          - Key: Name
            Value: ${self:custom.projectName}-${env:STAGE}-db
          - Key: Owner
            Value: ${env:OWNER}
          - Key: env
            Value: ${self:custom.projectName}
          - Key: stage
            Value: ${env:STAGE}
```

## Outputs
```yaml
resources:
  Outputs:
    VPCId:
      Value: !Ref VPC
      Export:
        Name: ${self:custom.projectName}-${env:STAGE}-vpc-id

    PrivateSubnet1Id:
      Value: !Ref PrivateSubnet1
      Export:
        Name: ${self:custom.projectName}-${env:STAGE}-private-subnet-1

    PrivateSubnet2Id:
      Value: !Ref PrivateSubnet2
      Export:
        Name: ${self:custom.projectName}-${env:STAGE}-private-subnet-2

    PublicSubnet1Id:
      Value: !Ref PublicSubnet1
      Export:
        Name: ${self:custom.projectName}-${env:STAGE}-public-subnet-1

    PublicSubnet2Id:
      Value: !Ref PublicSubnet2
      Export:
        Name: ${self:custom.projectName}-${env:STAGE}-public-subnet-2

    LambdaSecurityGroupId:
      Value: !Ref LambdaSecurityGroup
      Export:
        Name: ${self:custom.projectName}-${env:STAGE}-lambda-sg
```

## Best Practices
- Always use private subnets for Lambda functions
- Configure VPC endpoints to reduce NAT Gateway costs
- Use separate security groups for different services
- Enable DNS resolution and hostnames in VPC
- Use multiple AZs for high availability
- Implement proper CIDR block planning
- Tag all resources for cost tracking
- Use NAT Gateways in each AZ for redundancy
- Configure proper route tables for traffic flow
- Monitor VPC Flow Logs for security analysis
- Use least privilege security group rules
- Implement proper network ACLs if needed