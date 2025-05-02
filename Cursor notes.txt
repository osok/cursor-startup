I'll create a nicely formatted Markdown document based on the provided text. Here's the content organized in a clear, structured format:

# Project Setup Guidelines

## Pre-Design Consultation
- Have a conversation with AI about your tech stack before requesting a design document
- Consider continuing the same conversation thread when requesting the design document after finalizing your tech stack

## Key Points for Design Document

### Technology Specifications
- Specify your tech stack (recommendation: Python 3.10+, Flask for websites at minimum)
- For Python projects:
  - Specify virtual environment preference (venv, conda, etc.)
  - Note if you plan to use Read the Docs or push to PyPI
  - Avoid using `async` - choose Celery if asynchronous processing is required
  - Always create a Virtual Environment (venv) before coding
- For Docker projects:
  - Specify which Docker Compose version you have installed
- Request common design patterns in your implementation

### Project Files
Include these essential files in your project:
- `design.md` - Design documentation
- `tasklist.md` - Task tracking
- `notes.md` - General notes
- `.cursorrules` - Rules for Cursor AI

Get template files from: https://github.com/osok/cursor-startup

## Communication Tips
- Take screenshots to communicate UI issues or error messages
- Include simple notes about what you're providing in screenshots

## Tools Integration
- **Github**: Useful but consumes many tool slots (you have 40 tool slots)
- **EXA**: Enables Cursor to research from the web
- **Context7**: Keeps updated technical documentation
- **Filesystem**: Gives Cursor full access to the project directory

## Context7 Integration Rules

```json
{
  "context7Integration": {
    "usage": [
      "This configuration ensures Context7 is used by default for most coding tasks",
      "Context7 provides up-to-date documentation from official sources",
      "These rules help prevent outdated code suggestions and API usage"
    ],
    "behaviorRules": [
      "1. APPEND 'use context7' to code-related queries automatically",
      "2. PRIORITIZE current documentation over training data for libraries",
      "3. UTILIZE Context7 for all package implementation questions",
      "4. INFORM user when Context7 is being used to retrieve information",
      "5. ALLOW override with explicit 'no context7' statement"
    ],
    "applicationScopes": {
      "languages": [
        "JavaScript/TypeScript: Always use for npm packages",
        "Python: Use for libraries with significant version changes",
        "Any language: Use for rapidly evolving frameworks and libraries"
      ],
      "frameworks": [
        "Next.js",
        "React",
        "Vue",
        "Angular",
        "Tailwind",
        "Express",
        "Django",
        "Flask"
      ]
    },
    "activationTriggers": {
      "explicitTriggers": [
        "Any query containing 'use context7'",
        "Questions about library implementation",
        "Requests for code generation"
      ],
      "implicitTriggers": [
        "Queries ending with question marks",
        "Queries containing: implement, create, build, generate, code",
        "Requests related to API usage"
      ],
      "overrideTriggers": [
        "Queries containing 'no context7'",
        "Historical code analysis requests",
        "Theoretical language questions"
      ]
    },
    "priorityGuidelines": [
      "Always prefer Context7's up-to-date documentation over potentially outdated training data",
      "For rapidly evolving libraries (Next.js, React, etc.), Context7 should always be used",
      "When version-specific implementation is needed, Context7 is mandatory",
      "Balance performance with accuracy by using Context7 when most beneficial"
    ]
  }
}
```
