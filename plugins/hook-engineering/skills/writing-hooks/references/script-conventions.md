# Script conventions for hook scripts

Read this in step 3. It sets only three things for a hook script: its shebang, its opening lines and its permissions. Everything inside the script comes from the docs for that hook.

## Contents

- [Rules](#rules)
- [Pick the interpreter](#pick-the-interpreter)
- [Bash opening lines by the hook's role](#bash-opening-lines-by-the-hooks-role)
- [Permissions](#permissions)

## Rules

- Start every shebang with `/usr/bin/env`, unless a documented deployment requirement names a fixed path.
- Set no minimum interpreter version: the shebang takes the first interpreter on the user's PATH.
- Bash, Python and Node are the preferred languages, not the only ones: use another when the hook needs it, with the same rules.
- When an official docs example uses another shebang (they use `#!/bin/bash`), keep these conventions.

## Pick the interpreter

Pick the first case that fits and start the file with exactly its block.

**Direct, single-purpose logic** (default): reads a field or two with `jq`, runs one tool, exits.

```bash
#!/usr/bin/env bash
set -euo pipefail
```

**Where Bash may be missing**, such as minimal containers:

- Use no Bash features: no arrays, `[[ ]]` or `${var,,}`.
- Leave out `pipefail`: Ubuntu's `dash` 0.5.12 rejects `set -o pipefail` (observed).

```sh
#!/usr/bin/env sh
set -eu
```

- On an event that can block, a hook that is not a gate must not exit 2 by accident, and `sh` has no `ERR` trap: `dash` exits 2 both on a failing `grep` under `set -e` and on an unset variable under `set -u` (observed). Run the logic in a subshell and map 2 to 1:

  ```sh
  #!/usr/bin/env sh
  set -eu
  main() {
    : # the hook's logic
  }
  set +e
  (
    set -e
    main "$@"
  )
  status=$?
  [ "${status}" -eq 2 ] && status=1
  exit "${status}"
  ```

**Complex or deterministic logic**: many checks, branching, state. Import only the standard library.

```python
#!/usr/bin/env python3
```

**Python that needs third-party packages**, when the working directory is not a Python project with its own `.venv` or `uv.lock`:

- Keep `dependencies` even when empty.
- Not for minimal containers: BusyBox installs its `env` as `/usr/bin/env` without `-S`, so `#!/usr/bin/env sh` works there and this shebang doesn't (reported, not re-tested here).

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///
```

**Node**, when the project already runs on Node or the hook benefits from it:

- Save the script as `.mjs`, never `.ts`.
- Run it as `"command": "node"` with the script path in `args` (`assets/node-exec-handler.json`): exec form with `node` works on every system, Windows included.
- `NODE_PATH` reaches `require` but not `import` in an ES module: `import` fails with `ERR_MODULE_NOT_FOUND` (tested with Node 26.13.1). Import a dependency outside the script's own `node_modules` by absolute path, or load it with `createRequire`, and test it in step 7.

```js
#!/usr/bin/env node
```

**A mod's hooks module and the files it imports**: no shebang; mode 100644.

## Bash opening lines by the hook's role

Exit code 2 blocks the action on the events that can block (`#### Exit code 2 behavior per event` in the docs), and a failing command inside the script passes its own exit code on: `grep` exits 2 on an error. Choose the opening lines by what the hook is for:

- **A hook on an event that can block, that is not a gate** (it advises, logs or adds context): turn any unexpected failure into exit 1, a non-blocking error. `-E` makes the trap apply inside functions too; without it a function's failure still exits 2 (both observed).

  ```bash
  #!/usr/bin/env bash
  set -Eeuo pipefail
  trap 'exit 1' ERR
  ```

- **A gate** (it must block what it cannot judge): keep the default opening lines, exit 2 with the reason on stderr on any input it cannot read, and set `onFailure: "block"` on its handler where the docs allow it. Check in step 4.7 that the user's version has `onFailure`: without it, a hook that times out, can't start or crashes before its own checks lets the action through, so make the script fail closed on everything it controls and tell the user what still passes.
- **Any other hook**: the default opening lines.

Exit codes to recognize when you verify:

- 127: an unset variable under `set -u`.
- 141: a pipeline whose reader closed early under `pipefail`, such as `yes | head -1`.

To drop a `set` flag the script cannot work with, write the reason on that line:

```bash
set -eo pipefail  # no -u: <reason>
```

To limit a script's run time, set `timeout` on its handler instead of calling the `timeout` command, which macOS doesn't ship (reported, not verified).

## Permissions

1. Before `git add`, set the executable bit so git records mode 100755:

   ```bash
   chmod +x <script>
   ```

2. If git already tracks the file, set the mode in the index:

   ```bash
   git update-index --chmod=+x <script>
   ```

3. In the hook handler, run the script by its path, so the shebang picks the interpreter.
