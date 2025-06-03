# cursor-startup

These are the startup files I use in my cursor environment.

## docs/

- `Design.md` : I use Sonnet to create a design document that I place here
- `notes.md` : the cursor rules spell out what and how to store project related memories i nthe notes file.
- `task_list.md` : this is the task list that I have cursor process the design, create an implementation plan and then create a `task_list.md`.  This helps kep the AI on track.
- `conventions/` : this directory covers library specific conventions to be used to keep projects built to a standard.  Only include the libraries that you plan to use in your project.

## .cursor/

- `mcp.json` : this is project realated tools, I keep the file-system mcp tool here so I can set its permissions to only the project directory.

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

## Tools

- `filesystem` : allows access to project files so it can read / write files on your behalf.
- `github` : interact with github
- `exa-mcp` : allows AI to search the web to find updated information.
- `context7` : provides upto date documentation on a number of libraries, so the AI knows how to properly code.
- `docs-generator` : creates text based UML for all OO, module-functions doc that describes the methods in non OO code, and a tree structure for the project. This keeps cursor from duplicating code or getting lost in the project.
