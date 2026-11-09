# Troubleshoot installation and login

Fixes for command not found, PATH, permission, network and authentication errors when installing or signing in to Claude Code. This pruned copy keeps only step 4 of the login fix, which removes stored plugin sensitive values and MCP server logins.

## Contents

- [Login and authentication](#login-and-authentication)
  - [Not logged in or token expired](#not-logged-in-or-token-expired)
- [Documentation References](#documentation-references)

## Login and authentication

### Not logged in or token expired

**4. Log out and back in**

Once the Keychain is writable again, Claude Code moves the credentials back the next time it writes a credential. To force this immediately, run `/logout` and then `/login`.

Logging out removes all stored credentials, including the plaintext file's contents, saved MCP server logins, and plugin sensitive values. After logging out, expect to re-authorize MCP servers and re-enter plugin secrets. Logging in again stores the login in the Keychain.

## Documentation References

- Source page: https://code.claude.com/docs/en/troubleshoot-install — the full installation and login troubleshooting guide, including steps 1 to 3 of "Not logged in or token expired" that this pruned copy omits.
