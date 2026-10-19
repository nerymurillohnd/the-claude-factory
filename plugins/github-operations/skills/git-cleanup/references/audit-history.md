# Audit: the whole history, the object store, secrets by name, deferred work

Read-only, like the rest of the audit (see `audit.md` for the ground rules, the scratch folder and the `GIT_OPTIONAL_LOCKS=0` rule). Every query below covers the first commit to now. History-wide queries use `--exclude=refs/stash --all`, because stash internals are not history. On a large repository, write each output to a file in the scratch folder and aggregate; do not print it.

## Shape of the history

```sh
git rev-list --count --exclude=refs/stash --all                                    # commits
git rev-list --max-parents=0 --exclude=refs/stash --all                            # root commits: more than one means unrelated or orphan histories
git log --exclude=refs/stash --all --max-parents=0 --format='%H %ad %an %s' --date=short
git rev-list --merges --count --exclude=refs/stash --all                           # merge commits
git log --exclude=refs/stash --all --format='%ad' --date=format:%Y-%m | sort | uniq -c   # activity per month
git shortlog -sne --exclude=refs/stash --all                                       # authors: the same person under two names or e-mails needs a .mailmap
```

Merge style: many `Merge pull request` or `Merge branch` subjects mean merge commits; a straight line of one-parent commits with `(#123)` subjects means squash merges.

## Noise inside the history

```sh
git log --exclude=refs/stash --all --format='%H %s' | grep -iE '^[0-9a-f]{40} (wip|fixup!|squash!|tmp|temp|\.+$|asdf|stuff$|misc$)'
git log --exclude=refs/stash --all --no-merges --name-only --format='%x01%H' | awk 'BEGIN{RS="\001"} NF==1{print $1}'   # empty commits
git log --exclude=refs/stash --all --format='%H %ct' | awk -v now="$(date +%s)" '$2>now'                               # commits dated in the future
```

If `git config commit.gpgsign` is true, count the unsigned commits (the repository signs, so an unsigned one stands out):

```sh
git rev-list --exclude=refs/stash --all --format=raw | awk '/^commit /{c=$2; s[c]=0} /^gpgsig /{s[c]=1} END{for(c in s) if(!s[c]) n++; print n+0 " unsigned of " length(s)}'
```

Rewriting noisy history that is already published is not a cleanup shortcut: report it. It becomes a plan only through `history-rewrite` (see `plan.md`).

## Object store

```sh
git count-objects -vH                                                              # loose objects, packs, garbage
cat "$(git rev-parse --git-path objects/info/alternates)" 2>/dev/null              # shared object stores
git fsck --connectivity-only --no-progress                                         # is everything reachable that must be
git fsck --no-reflogs --unreachable --no-progress | awk '$2=="commit"{print $3}'   # commits no ref or reflog reaches
```

For each unreachable commit, describe it without printing content: `git log -1 --format='%H %an %ad %s' --date=short <sha>`. These are candidates for lost work; preserving one is a `prep` action (`git branch rescue/lost-<short sha> <sha>`). Never use `fsck --lost-found` (it writes into the repository). Reflog entries expire (90 days, 30 if unreachable) and `gc` prunes unreachable objects after `gc.pruneExpire` (2 weeks): never promise recovery from either.

Need for `gc`: compare the loose-object count and pack count with the repository's own `git config gc.auto` (default 6700) and `git config gc.autoPackLimit` (default 50). Do not read or edit `packed-refs` directly; `for-each-ref` covers loose and packed refs.

### Large blobs across all history

This works even in a repository that never ran `gc` (the `verify-pack` route needs packs):

```sh
git rev-list --objects --exclude=refs/stash --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | awk '$1=="blob"' | sort -k3 -n -r | head -40 > largest-blobs.txt
git ls-tree -r --name-only HEAD | sort > head-files.txt           # which of them still exist in HEAD
```

A large blob whose path is not in `head-files.txt` is dead weight that only history keeps. Report the path and size. A rewrite is the only way to remove it from history.

## Secrets: names only

Never print contents. List the secret-like names that were ever committed, and whether each still exists:

```sh
git log --exclude=refs/stash --all --name-only --diff-filter=A --format= | sort -u \
  | grep -iE '(^|/)(\.env(\..+)?|.+\.(pem|key|p12|pfx|keystore|kdbx|tfstate)|id_(rsa|dsa|ecdsa|ed25519)|\.netrc|\.npmrc|\.pypirc|\.git-credentials|\.htpasswd|credentials(\..+)?|secrets?(\..+)?|terraform\.tfvars)$' \
  | grep -viE '\.(example|sample|template|dist|pub)$' > secret-names.txt
git ls-tree -r --name-only HEAD | grep -Fxf secret-names.txt          # the ones still tracked
```

A name in `secret-names.txt` that is absent from HEAD is a credential that was removed but still lives in history, and in every clone and fork. Treat it as exposed: the report tells the user to rotate it. The skill never handles the credential itself. If the repository or the machine already has a secret scanner (`gitleaks`, `trufflehog`), the user may allow it; run it only with redaction on (`gitleaks detect --redact`) and quote its findings, never the secret.

## Deferred work

```sh
git grep -nIE '\b(TODO|FIXME|HACK|XXX)\b' > deferred.txt; wc -l deferred.txt
cut -d: -f1 deferred.txt | sort | uniq -c | sort -rn | head -20                    # files with the most markers
git grep -nIE '(@pytest\.mark\.(skip|xfail)|\b(xit|xdescribe|xtest)\(|\b(it|test|describe)\.(skip|todo)\b|@Ignore|\bt\.Skip\()' > skipped-tests.txt
git blame -L <line>,<line> --date=short -- <file>                                  # how old a marker is, for the worst files
```

Age comes from `blame` (plain). Dead code is judged only through the project's own tools when they exist (for example `knip`, `vulture`, `ruff`'s unused rules), quoting their output. Do not invent language analysis.
