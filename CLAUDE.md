# CLAUDE.md

**Never run a paid video generation.** Do not run `python main.py` without `--test`, or anything that calls the Higgsfield API to upload or generate. Only `--test`, `--help` and `pytest` are allowed. When a generation is needed, write the exact command in the chat and let the user run it.

**Never push anything private to GitHub.** No local or Windows paths (`C:\...`, `C:/Users/...`), no real names or personal data, no local-only tools. Local-only files go into `.git/info/exclude`, not `.gitignore`, and are never mentioned in committed files. Before finishing, check what git would push.

All project rules, the project map and the workflow are in AGENTS.md:

@AGENTS.md
