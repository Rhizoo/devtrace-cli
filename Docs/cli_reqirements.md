### Requirements

- Centralized config => lives in repo with code owner function github.
- Decentralized config => local settings etc.

- start [TKT] => keeps the ticket id in cache
- git commit -m "something" => checked by hoock and auto adds [TKT] in commit according to the specified format
- dt switch =>
  1. stash current [TKT]
  2. switch to the [TKT]
  3. apply stash for it
  4. Also take acc of the branch.
- dt status => gives jira status
- dt jira => opens [TKT] in browser
- dt log => logs in jira

pyinstaller --onefile --name devtrace --clean --console src/devtrace/main.py
pyinstaller devtrace.spec --clean
