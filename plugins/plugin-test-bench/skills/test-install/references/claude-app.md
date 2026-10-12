# Testing in the Claude app

Read in step 11, before cleaning up, when the plugin is meant to work in the Claude app (claude.ai on the web and the desktop app) as well as in Claude Code. Cleaning up deletes a snapshot folder, so build the zip first.

Only an install on the user's claude.ai account reaches the app. Docs: <https://claude.com/docs/plugins/build> and <https://claude.com/docs/plugins/overview>.

1. Build a zip of the committed plugin, with the plugin's contents at the archive root:

   ```bash
   git -C <repo root> archive --format=zip -o <zip path> HEAD:<plugin path>
   ```

   For a plugin at the repository root, use `HEAD` alone. Put the zip somewhere the user can find it, such as their Downloads folder, and tell them the path. The zip is theirs to keep or delete.
2. The user uploads it in the app: **Customize** → **Plugins** → **Add** → **Upload plugin**.
3. They run the same realistic requests there. Where the app can't run the plugin's agents, hooks or local MCP servers, it skips them, so the skill alone must still give a useful answer.
4. Afterwards they remove the uploaded copy (the plugin's menu → **Remove**). An upload also reaches Claude Code as `<name>@synced`; a plugin with the same name installed in Claude Code loads instead of it.

You can't see the app: report this part as "not tested" until the user tells you what happened.
