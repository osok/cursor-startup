**NEVER** modify this document, this is for the human to edit to guide the work to be done.

## Instructions 
- Use the `docs/Requirements.md` as the authoritative source for the requirements of the  project. 
- Use the `docs/Design.md` as the authoritative source for the logical design project. 
- Use the `docs/task_list.md` used for project development tracking,
- Use the `docs/notes.md` for notable aspects of the project. no task tracking should be in the notes.
- Use the `docs/uml.txt` for reference for the code that exists in classes. use this when referencing existing code, so we don't duplicate code and we call classes and functions correctly.
- Use the `docs/module-functions.txt`  for code that is not in classes.  use this when referencing existing code, so we don't duplicate code and we call functions correctly.
- Use the `docs/tree-structure.txt` to see the file layout of the project. use this to understand the files in the project.
- Use doc-tools tool to create the uml, module-functions and tree structure docs. These docs will not exist until there is code and  the tool has run.
- The folder `docs/conventions/` contains documents that describe the coding conventions used in this project for a number of different libraries.
- Use context7 tool to find usage and examples for many code libraries.
- Use the exa tool to search the web.

## Must adhere to
- Most importantly **NEVER** use `asyncio`, this causes massive problems when coding in python.
- **Always** use the `venv`, to load requirements, and launch the application.
- The tools run from where Cursor is running from do if you want to use a relative project path it might break some tools, this project is located `[PLACE PROJECT PATH HERE]`, if you use fully qualified paths you will get better results.
- Limit what we hard code, situations change in different environments.  While we see something in this environment, we need to be able to run the tool in many environments.
- Most importantly **NEVER** use `asyncio`, this causes massive problems when coding in python.
- Don't use `!` in bash scripts it don't work well with the tools.

## Workflow

### Start

When the user asks you to `start` or `initialize`, please do these steps:
- Read through the Design document, and Design UML  if it exists
- take a step back and think about how to construct this application
- develop an implementation plan, and document by creating a tasklist with dependancies, references and status.  Make sure the tasklist is in markdown and in a table so a user can easily review it looking for the current progress.
- If needed add important noes to the notes.md

### Continue

When the user asks you to `continue`, or `please continue`, do these steps:
- Read the default_prompt.md, this document
- Read the Task list to determine what has been done and what is next
- Read through the reference material, Design and Design UML
- Read the appropriate convention files.
- Then work on the solution, ensuring to not loose existing functionality, this is **IMPORTANT** do not loose existing functionality.
- Make sure to create test cases for the new functionality
- enter a break fix loop until the tests are working, making sure to fix the code to align with the designs intent
- Once a cycle is complete and we near 80 to 90% of the content in use, update the task list and notes
- Update the user on what was accomplished
