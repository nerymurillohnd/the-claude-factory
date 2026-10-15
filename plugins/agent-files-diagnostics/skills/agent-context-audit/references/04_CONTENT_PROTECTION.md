# Phase 4: Content protection (steps)

1. Make a private working copy of each audited source, and of the evidence-only managed-policy `CLAUDE.md`, in the approved location, and have auditors read the copies, not the originals.
2. Mask each copy line by line, replacing only the matched text with `[REDACTED]`:
   - every line of a private-key block, from a `-----BEGIN ... PRIVATE KEY-----` line to its `-----END ... PRIVATE KEY-----` line, both included;
   - the user and password of a URL: `scheme://user:password@host` becomes `scheme://[REDACTED]@host`;
   - the value of a dotenv-style assignment whose name is in capitals and contains `KEY`, `SECRET`, `TOKEN`, `PASSWORD`, `PASSWD`, or `CREDENTIAL` (`API_KEY=value`, `export DB_PASSWORD="value"`), quoted or not;
   - the value of an `Authorization: Bearer` or `Authorization: Basic` header;
   - a token that starts with a prefix its vendor documents and continues with at least 20 characters of `[A-Za-z0-9_]`: the GitHub prefixes `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`, and `github_pat_`; and an AWS access key ID, which is `AKIA` or `ASIA` followed by at least 12 capital letters or digits.

   A value ends at whitespace, a quote, or a backtick, and that closing character stays. Propose at Gate 1 any other vendor format that the user wants masked. Masking is best effort: the reviewers redact whatever it misses.
3. Preserve line numbers while masking. Check that each copy has the same number of lines as its original (`wc -l`).
4. Make sure masking does not alter ordinary words, such as branch names. Anchor every pattern on a word boundary or on the delimiters above, then compare each copy with its original (`diff`) and check that only the matched text changed.
5. Compute the hash of each original source with `shasum -a 256` (`sha256sum` where `shasum` is missing) and keep the results in the hash table. Phase 13.1 uses the same command.
6. Never read `.env` files, private keys, or credential files.
