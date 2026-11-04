# Labels

The forms and templates apply labels that must exist. The repository's labels win; `<skill-dir>/assets/labels.json` is the model for a group of labels the repository lacks.

1. Run `<skill-dir>/scripts/labels-diff.py --repo <owner>/<repo> --labels <skill-dir>/assets/labels.json`. It prints the labels `missing`, `extra` and `different` as JSON, and exits 1 when anything is missing or different.
2. From the missing labels, keep only the ones the forms and templates you wrote apply, and the groups the repository needs. Name them in the repository's existing style.
3. Check that every label in every form's `labels:` is either in the repository or among the labels you will create: GitHub skips a missing label without warning.
4. Show the user the labels to create. Creating or changing a label changes the repository: ask first.
5. After approval, create each one with `gh label create "<name>" --color <hex> --description "<text>"`. Leave existing labels as they are unless the user asks. When the repository already has a label-sync file, update that file instead.
6. Read the labels again (`gh label list`) and confirm nothing approved is still missing.
