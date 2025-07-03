# cursor-startup

These are the startup files I use in my cursor environment.

## docs/

- `Design.md` : I use Sonnet to create a design document that I place here
- `notes.md` : the cursor rules spell out what and how to store project related memories in the notes file.
- `task_list.md` : this is the task list that I have cursor process the design, create an implementation plan and then create a `task_list.md`.  This helps keep the AI on track.
- `conventions/` : this directory covers library specific conventions to be used to keep projects built to a standard.  **Only include the convention files that apply to your specific project** - others can be left out.

## Convention Files

**Note:** Only add the convention files that are relevant to your project's technology stack. Each file provides specific coding standards and patterns for that technology.

### API & Web Framework Conventions
- `api-design.md` - REST API design patterns, request/response formats, OpenAPI documentation standards, and GraphQL schema conventions
- `fastapi.md` - FastAPI project structure, Pydantic models, dependency injection, authentication, and async patterns
- `flask.md` - Flask application factory pattern, blueprints, request validation, and service layer organization
- `next-js.md` - Next.js App Router conventions, server/client components, API routes, and performance optimization patterns

### Frontend Conventions
- `react.md` - React component patterns, hooks, context management, state handling, and performance optimization techniques

### Backend & Database Conventions
- `python.md` - Python project structure, type hints, error handling, configuration management, and code organization standards
- `sqlAlchemy.md` - SQLAlchemy models, repository patterns, session management, migrations, and query optimization techniques
- `pgVector-postgres.md` - PostgreSQL with pgVector setup, vector similarity search, hybrid search patterns, and performance indexing

### Cloud & Infrastructure Conventions
- `aws-serverless-core.md` - AWS Lambda, API Gateway, DynamoDB, S3, CloudWatch configuration and resource tagging standards
- `aws-serverless-messaging.md` - SQS, SNS, EventBridge, and Cognito integration patterns for serverless messaging architectures
- `aws-serverless-orchestration.md` - Step Functions workflow patterns, state machine configurations, and service orchestration best practices
- `serverless-framework-python.md` - Serverless Framework conventions for Python Lambda functions, resource definitions, and deployment patterns
- `serverless-framework-node.md` - Serverless Framework conventions for Node.js Lambda functions, API Gateway integration, and monitoring setup

### Development & Deployment Conventions
- `docker.md` - Docker containerization patterns, multi-stage builds, docker-compose configurations, and production deployment strategies
- `testing.md` - Testing strategies, pytest fixtures, unit/integration/e2e test patterns, and performance testing approaches
- `websocket.md` - WebSocket connection management, authentication, message handling, and real-time communication patterns

### AI & Machine Learning Conventions
- `langchain.md` - LangChain and LangGraph conventions for AI workflows, prompt management, agent patterns, and memory implementations

## .cursor/

- `mcp.json` : this is project related tools, I keep the file-system mcp tool here so I can set its permissions to only the project directory.

## .cursor/rules
- 001-project-organization.mdc - Project organization and file usage guidelines (Rule Type: Manual)
- 002-development-workflow.mdc - Task management and workflow rules (Rule Type: Always)
- 003-testing-guidelines.mdc - Testing workflow and conventions (Rule Type: Manual)
- 004-context7-integration.mdc - Context7 integration settings (Rule Type: Always)
- 005-coding-conventions.mdc - this explains how to use the files in the convention directory
- 010-documentation-usage.mdc - this explains how to use the mcp server to create uml and other project docs (*NOTE See: https://github.com/osok/mcp-support-docs)

## Other files

- `github.sh` : should reside outside the project directory and only needs to be set up once.  in your `~/.cursor` dir is a good place for it.
- `cursor-mcp.json` : goes in the IDE cursor settings.

## Sample Environment Configuration

The convention files reference various environment variables. Create a `.env` file in your project root with the variables relevant to your technology stack:

```bash
# Project Configuration
PROJECT_NAME=my-awesome-app
STAGE=dev
REGION=us-east-1
OWNER="John Doe abc123"
LOG_LEVEL=INFO
NODE_ENV=development
ENVIRONMENT=development

# API Configuration
API_VERSION=v1
API_BASE_URL=https://api.example.com
PORT=8000
HOST=0.0.0.0
CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]
RATE_LIMIT_REQUESTS=1000

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379

# Authentication & Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Next.js Configuration (if using Next.js)
NEXT_PUBLIC_PROJECT_NAME=my-awesome-app
NEXT_PUBLIC_STAGE=dev
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# React Configuration (if using React)
REACT_APP_PROJECT_NAME=my-app
REACT_APP_STAGE=dev
REACT_APP_API_URL=http://localhost:3001

# AI/ML Configuration (if using LangChain)
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key
LANGCHAIN_API_KEY=your-langchain-api-key
LANGCHAIN_TRACING_V2=true
PINECONE_API_KEY=your-pinecone-api-key

# WebSocket Configuration (if using WebSockets)
WEBSOCKET_URL=ws://localhost:8000/ws
MAX_CONNECTIONS_PER_USER=5
MESSAGE_RATE_LIMIT=100

# Docker/Production Configuration (if using Docker)
SSL_EMAIL=admin@yourdomain.com
DOMAIN=yourdomain.com

# Testing Configuration
DATABASE_URL_TEST=postgresql://test_user:test_pass@localhost:5432/test_db
SECRET_KEY_TEST=test-secret-key-not-for-production
```

**Note**: 
- Only include variables relevant to your project's technology stack
- Replace placeholder values with your actual configuration
- Use different `.env` files for different environments (`.env.local`, `.env.staging`, `.env.production`)
- Never commit `.env` files containing sensitive data to version control
- Add `.env` to your `.gitignore` file

## Usage Instructions

1. **Select Relevant Conventions**: Only copy the convention files from the `conventions/` directory that match your project's technology stack
2. **Configure Environment**: Create a `.env` file with only the variables needed for your selected conventions
3. **Customize as Needed**: Adapt the conventions to match your specific project requirements
4. **Keep Updated**: Regularly review and update conventions as your project evolves
5. **Team Alignment**: Ensure all team members understand and follow the established conventions

## Tools

- `filesystem` : allows access to project files so it can read / write files on your behalf.
- `github` : interact with github
- `exa-mcp` : allows AI to search the web to find updated information.
- `context7` : provides up to date documentation on a number of libraries, so the AI knows how to properly code.
- `docs-generator` : creates text based UML for all OO, module-functions doc that describes the methods in non OO code, and a tree structure for the project. This keeps cursor from duplicating code or getting lost in the project.