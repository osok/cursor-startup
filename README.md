# cursor-startup

These are the startup files I use in my cursor environment.

## docs/

- `Design.md` : I use Sonnet to create a design document that I place here
- `notes.md` : the cursor rules spell out what and how to store project related memories i nthe notes file.
- `task_list.md` : this is the task list that I have cursor process the design, create an implementation plan and then create a `task_list.md`.  This helps kep the AI on track.

## .cursorrules

This is depercated, but it stil works.  These rules tell the AI how to use the `Design.md`, `notes.md` and `task_list.md`

## .cursor/

- `mcp.json` : this is project realated tools, I keep the file-system mcp tool here so I can set its permissions to only the project directory.

## Other files

`github.sh` : should reside outside the project directory and only needs to be set up once.  in your `~/.cursor` dir is a good place for it.

`cursor-mcp.json` : goes in the IDE cursor settings.

## Tools

`filesystem` : allows access to project files so it can read / write files on your behalf.
`github` : interact with github
`exa-mcp` : allows AI to search the web to find updated information.
1context7` : provides upto date documentation on a number of libraries, so the AI knows how to properly code.
