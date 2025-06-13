**NEVER** modify this document, this is for the human to edit to guide the work to be done.

## Instructions 
- Use the `docs/Requirements.md` as the authoritative source for the requirements of the  project. 
- Use the `docs/Design.md` as the authoritative source for the logical design project. 
- Use the `docs/task_list.md` used for project development tracking,
- Use the `docs/notes.md` for notable aspects of the project. no task tracking should be in the notes.
- Use the `docs/uml.txt` for reference for the code that exists in classes. use this when referencing existing code, so we don't duplicate code and we call classes and functions correctly.
- Use the `docs/module-functions.txt`  for code that is not in classes.  use this when referencing existing code, so we don't duplicate code and we call functions correctly.
- Use the `docs/tree-structure.txt` to see thefile layout of the project. use this to understand the files in the project.
- Use doc-tools tool to create the uml, module-functions and tree structure docs. These docs will not exist until there is code and  the tool has run.
- The folder `docs/conventions/` contains documents that describe the coding conventions used in this project for a number of differnt libraries.
- Use context7 tool to find usage and examples for many code libraries.
- Use the exa tool to search the web.

## Must adhere to
- Most importantly **NEVER** use `asyncio`, this causes massive problems when coding in python.
- **Always** use the `venv`, to load requirements, and launch the application.
- The tools run from where Cursor is running from do if you want to use a relative project path it might break some tools, this project is located `[PLACE PROJECT PATH HERE]`, if you use fully qualified paths you will get betterresults.
- Limit what we hard code, situations change in different environments.  While we see something in this environment, we need to be able to run the tool in many environments.
- Most importantly **NEVER** use `asyncio`, this causes massive problems when coding in python.
- Don't use `!` in bash scripts it don't work well with the tools.
