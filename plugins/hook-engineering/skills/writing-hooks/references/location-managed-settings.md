# Managed settings hooks

Read this in step 4 when an organization's administrator deploys the hook through managed policy settings.

## Role

You write a policy hook for an administrator: it must hold on every managed machine, and users must not be able to turn it off.

## Knowledge

- Scope: every machine and account the organization deploys the policy to.
- Delivery: a `managed-settings.json` file (with an optional `managed-settings.d/` folder) in the system directory: `/Library/Application Support/ClaudeCode/` on macOS, `/etc/claude-code/` on Linux and WSL, `C:\Program Files\ClaudeCode\` on Windows. It can also arrive as an MDM profile, a Windows registry value, or server-managed settings from the claude.ai console.
- Cloud: only server-managed settings reach a cloud session; a managed file or MDM profile on a device does not.
- Precedence: managed hooks always run beside the others; `disableAllHooks` outside managed settings can't disable them.
- Lockdown: managed `allowManagedHooksOnly` runs only managed hooks, Agent SDK hooks and hooks of plugins managed settings force-enable. `strictPluginOnlyCustomization` with `hooks` keeps only plugin and managed hooks.
- HTTP hooks: `allowedHttpHookUrls` and `httpHookAllowedEnvVars` apply to hooks from every source, managed ones included.
- Docs: `### Hook locations` and `### Disable or remove hooks` in `hooks`, `managed-settings`, and `### allowManagedHooksOnly` in `settings-reference`.

## Gotchas

- A script the managed hook calls must already be on every machine: managed settings carry configuration, not files. To ship scripts with the policy, use a plugin the managed settings force-enable (`references/location-plugin.md`).
- `/status` shows `Enterprise managed settings` in its `Setting sources` line only when a managed source is in force: check it before you debug a hook that seems ignored.

## Rules

- Write a guard as a gate: `onFailure: "block"` where the docs allow it, and exit 2 on input it cannot read.
- Reference scripts by absolute paths that exist on every managed machine, per platform.
- Hand the administrator the JSON and the deployment path; never write to a system directory yourself.

## Structure

- File: `managed-settings.json` in the system directory above, or the administrator's delivery mechanism.
- Template: `assets/project-settings.json`, with `command` changed to the absolute script path.
