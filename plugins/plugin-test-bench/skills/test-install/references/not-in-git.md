# Plugin outside a git repository

Read when the plugin folder is not inside a git repository.

A copied install needs a commit to copy from. Offer the user two choices and wait for the answer:

1. **Make it a repository** (best when they plan to publish from git): they run `git init` and commit in the plugin's folder, then the test proceeds normally.
2. **Snapshot it for this test only**: copy the plugin folder into a fourth `mktemp -d` folder, `git init` there, `git add -A` and `git commit -m snapshot`, with the user's own git settings: never override their identity, signing or hooks. Signing may ask for a passphrase or a security key; if git refuses to commit, report the message and let the user choose. Use that folder as the repository root, with a `url` source. Say that the snapshot includes every file in the folder, including ones a future `.gitignore` would leave out, so step 5's comparison can't show what git would drop. Delete the snapshot folder in step 11.
