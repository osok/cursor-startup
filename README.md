# cursor-startup

This repository contains startup configurations and templates for Cursor IDE with dual capabilities:

- **Software Development**: Complete development workflow with design documents, task management, and coding conventions
- **Security Code Review**: Comprehensive security audit framework with vulnerability assessment tools and methodologies

Choose the appropriate capability folder based on your project needs, or use both for projects requiring development and security review phases. 

## Instruction for use:

### Software Development

#### Setup
- Create a new project folder
- Copy the `docs/` and `.cursor/` into the project directory.
- Edit the mcp.json in the .cusror dir to the filesystem has access to your project folder and any other folders on your system that you want to interact with.  This project specific, which is why it is here.
- Create a Design document, I use AI to do this.  Copy the resilts formated as markdown to the docs/Design.md
- Create UML in mermaid format that represents the implementation of the above Design.  you should use the same chat session as above to create these.  Include
   - Class Diagrams
   - Sequence Diagrams for the major workflows
   - State and activity diagrams
   - Component Diagrams.
- Review the `docs/conventions` remove anything that doesn't relate to your project.  IF you have new convention files, use the existing ones and AI to develop new files.  These will be added to the context if needed so they need to be short and concise.
- Start Cursor and open the new folder. 
- modify the Default_promt.md, to include the project working directory. About halfway down you should see `[PLACE PROJECT PATH HERE]`
- you do not need a requirements document, Sometimes I do and latelyt I have been changing that to Design UML.md
- make sure the filesystem and project-docs tool are active.

#### Starting
- Select the model or use Auto, I personally like Sonnet-4, and use an API key.  This gives me the best esults but can cost $20+ a day.
- set the default_prompt in the chat box  where you see the `@`.  This gets added to the context immediately.
- then just type `start`, this will create the task_list and notes.

#### Coding
- Create a new chart session, reference the default_prompt.md in the chat next to the `@`, this needs to be done with every new chat.
- then type `continue`, this will kick off the coding workflow.
- when you get to 80% of the context used, start anew session.  Using sonnet max allows up to a 1 Million token context, I try not to use that becaue it increases the daily coding cost when you are sending large context over and over.

#### Notable
- As cursor codes, it should be creating unit test.  This allows it to entera break fix cycle which gets the code right.  
- You want to ensure you have an 85% or better coverage.  Before you finsh the project you should ask it to caculate the testing coverage, and adjust until you get 85% or better coverage.
- I have been asking cursor to create comprehensive delvoper documents at the end of every project.  It dshould include UML based on the actual code.  Then I review that and spot check to make sure its accurate.  Since I didn't code the project it helps me understand exactly what it did.

### Secure Code Review

#### Setup
- Create a new project folder
- Copy the `docs/` and `.cursor/` into the project directory.
- Edit the mcp.json in the .cusror dir to the filesystem has access to your project folder and any other folders on your system that you want to interact with.  This project specific, which is why it is here.
- modify the Default_promt.md, to include the project working directory. About halfway down you should see `[PLACE PROJECT PATH HERE]`
- make sure the filesystem and project-docs tool are active.

#### Start
- Select the model or use Auto, I personally like Sonnet-4, and use an API key.  This gives me the best esults but can cost $20+ a day.
- set the default_prompt in the chat box  where you see the `@`.  This gets added to the context immediately.
- then just type `start`, this will create the task_list and notes.

#### Testing
- Create a new chart session, reference the default_prompt.md in the chat next to the `@`, this needs to be done with every new chat.
- then type `continue`, this will kick off the testing workflow
- when you get to 80% of the context used, start anew session.  Using sonnet max allows up to a 1 Million token context, I try not to use that becaue it increases the daily coding cost when you are sending large context over and over.

#### Finish
- Create a new chart session, reference the default_prompt.md in the chat next to the `@`, this needs to be done with every new chat.
- then type `finish`, this will kick off the testing workflow.
- this will wwrap up the testing and create more documentation based on the findings.



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

## Repository Files

### Software Development Files

1. **Select Relevant Conventions**: Only copy the convention files from the `conventions/` directory that match your project's technology stack
2. **Customize as Needed**: Adapt the conventions to match your specific project requirements
3. **Create Design Document**: Use Sonnet to create your project design in `docs/Design.md`
4. **Initialize Task List**: Process the design to create an implementation plan in `docs/task_list.md`
5. **Configure MCP Tools**: Set up the documentation generation tools for UML and module functions
6. **Team Alignment**: Ensure all team members understand and follow the established conventions

### Security Code Review Files

1. **Define Scope**: Update `docs/Security_review.md` with your specific audit objectives
2. **Configure Project Path**: Update the project path in `docs/default_prompt.md` to match your target codebase
3. **Generate Documentation**: Use MCP doc-tools to create UML, module functions, and tree structure
4. **Create Task Plan**: Generate a comprehensive security review task list based on the security checklist
5. **Setup Output Structure**: Ensure the `docs/output/` directory exists for findings and reports


## Tools and MCP Configuration

### Core Tools (Used by Both Capabilities)

- `filesystem` : **Optional** Allows access to project files for reading and writing
- `project-docs` (MCP): **Required** -Creates UML diagrams, module-functions documentation, and tree structures [Project Docs](https://github.com/osok/project-docs) 
- `exa-mcp` : **Optional** Web search capability for finding updated information 
- `context7` : **Optional** Provides up-to-date documentation for libraries and frameworks

### Development-Specific Tools

- `github` : **Optional** GitHub integration for repository management, simplifes git work, but cursor can do so form the commandline as well.  this has a lot of tools, which eats up many of the limited 40 tools available in cursor.  I'm not using this unless my repo gets messed up.
- Supports all major development frameworks and libraries
- Automated testing and quality gate enforcement
