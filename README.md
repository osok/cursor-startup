# cursor-startup

This repository contains startup configurations and templates for Cursor IDE with dual capabilities:

- **Software Development**: Complete development workflow with design documents, task management, and coding conventions
- **Security Code Review**: Comprehensive security audit framework with vulnerability assessment tools and methodologies

Choose the appropriate capability folder based on your project needs, or use both for projects requiring development and security review phases.

## Project Structure

### Software Development/
Contains all files and configurations for software development projects:
- `docs/Design.md` - Project design documentation
- `docs/notes.md` - Development notes and decisions
- `docs/task_list.md` - Development task tracking
- `docs/conventions/` - Coding conventions for various frameworks
- `docs/default_prompt.md` - Development workflow instructions

### Security Code Review/
Contains all files and configurations for security audit projects:
- `docs/Security_review.md` - Security audit objectives and methodology
- `docs/task_list.md` - Security review task tracking
- `docs/notes.md` - Security findings and analysis notes
- `docs/output/` - Generated security reports and findings
- `docs/default_prompt.md` - Security review workflow instructions


## Documentation Structure (Per Capability)

Each capability folder contains its own `docs/` directory with the following structure:

**For Software Development:**
- `docs/Design.md` - Project design documentation and architecture decisions
- `docs/notes.md` - Development notes, decisions, and project memories
- `docs/task_list.md` - Development task tracking with dependencies and status
- `docs/default_prompt.md` - Development workflow and AI instructions
- `docs/conventions/` - Coding conventions for various frameworks (**Only include relevant files**)

**For Security Code Review:**
- `docs/Security_review.md` - Security audit objectives, methodology, and checklist
- `docs/task_list.md` - Security review task tracking and audit progress
- `docs/notes.md` - Security findings, analysis notes, and concerns
- `docs/default_prompt.md` - Security review workflow and AI instructions
- `docs/output/` - Generated security reports, findings, and coverage documentation

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

## Configuration Files

### MCP Configuration
- Each capability folder can include its own `mcp.json` for project-specific tool configurations
- The filesystem MCP tool permissions should be set to the specific project directory
- Configuration is capability-specific to optimize for development vs security review workflows

### Cursor Rules (Embedded in Capabilities)
Both capability folders include embedded cursor rules:
- **001-project-organization** - Project organization and file usage guidelines (Always Applied)
- **002-development-workflow** - Task management and workflow rules (Always Applied) 
- **003-testing-guidelines** - Testing workflow and conventions (Manual)
- **004-context7-integration** - Context7 integration settings (Always Applied)
- **005-coding-conventions** - Framework-specific coding convention usage (Manual)
- **010-documentation-usage** - MCP documentation tool usage guidelines (Always Applied)

### External Files
- `github.sh` : Should reside outside the project directory (recommended: `~/.cursor/`)
- `cursor-mcp.json` : Goes in the IDE cursor settings for global MCP configuration

## Usage Instructions

### Getting Started

1. **Choose Your Capability**: 
   - Copy the `Software Development/` folder for development projects
   - Copy the `Security Code Review/` folder for security audits
   - Copy both folders if you need both capabilities

2. **Setup Your Project**:
   - Copy the chosen capability folder(s) to your project root
   - Rename the folder(s) as needed (e.g., remove the capability prefix)
   - Follow the specific setup instructions for each capability below

### Software Development Setup

1. **Select Relevant Conventions**: Only copy the convention files from the `conventions/` directory that match your project's technology stack
2. **Customize as Needed**: Adapt the conventions to match your specific project requirements
3. **Create Design Document**: Use Sonnet to create your project design in `docs/Design.md`
4. **Initialize Task List**: Process the design to create an implementation plan in `docs/task_list.md`
5. **Configure MCP Tools**: Set up the documentation generation tools for UML and module functions
6. **Team Alignment**: Ensure all team members understand and follow the established conventions

### Security Code Review Setup

1. **Define Scope**: Update `docs/Security_review.md` with your specific audit objectives
2. **Configure Project Path**: Update the project path in `docs/default_prompt.md` to match your target codebase
3. **Generate Documentation**: Use MCP doc-tools to create UML, module functions, and tree structure
4. **Create Task Plan**: Generate a comprehensive security review task list based on the security checklist
5. **Setup Output Structure**: Ensure the `docs/output/` directory exists for findings and reports

### Workflow Commands

**For Software Development:**
- `continue` - Resume development work based on task list
- Follow the checkpoint system for quality gates
- Update notes and task list regularly

**For Security Code Review:**
- `start` - Initialize security review with documentation generation and task planning
- `continue` - Proceed with next security review tasks
- `finish` - Complete review with final analysis and true positive validation

## Tools and MCP Configuration

### Core Tools (Used by Both Capabilities)

- `filesystem` : Allows access to project files for reading and writing
- `docs-generator` (MCP): Creates UML diagrams, module-functions documentation, and tree structures
- `exa-mcp` : Web search capability for finding updated information
- `context7` : Provides up-to-date documentation for libraries and frameworks

### Development-Specific Tools

- `github` : GitHub integration for repository management
- Supports all major development frameworks and libraries
- Automated testing and quality gate enforcement

### Security Review-Specific Tools

- Static analysis integration (Bandit, Semgrep, CodeQL)
- Vulnerability scanning capabilities
- CVSS scoring and MITRE categorization
- Comprehensive security checklist automation

### MCP Configuration Files

Each capability includes its own MCP configuration:
- **Software Development**: Optimized for development workflows, code generation, and project management
- **Security Code Review**: Configured for security analysis, vulnerability detection, and audit reporting

The MCP tools automatically generate documentation that prevents code duplication and helps maintain project context across both development and security review phases.