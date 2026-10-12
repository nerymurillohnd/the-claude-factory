# Issue reply templates

Saved replies for `/triage-issues`. Personalize every reply: use the reporter's handle, reference their details, and replace every `<…>`. English only. Never promise dates.

## Needs more information

~~~markdown
Thanks for the report, @<user>! 🙏 To reproduce this we need a bit more detail:

- [ ] Output of `claude --version`
- [ ] Output of `claude plugin details <plugin>`
- [ ] Anything listed in `/plugin` → **Errors**
- [ ] <specific missing detail>

We'll pick it back up as soon as you reply.
~~~

## Confirmed bug

~~~markdown
Thanks @<user> — confirmed and reproduced. 🐞 <one-sentence root cause, if known>.

**Workaround until the fix ships:** <workaround or "none yet">.

We'll link the release here when the fix is out.
~~~

## Accepted feature or plugin idea

~~~markdown
Great idea, @<user> — thank you! ✨ <why it fits / what problem it solves>.

We've added it to the roadmap. 👍 reactions from others help us prioritize. We'll update this issue when it ships.
~~~

## Released

~~~markdown
Fixed in **<plugin> <version>** 🚀 — [release notes](https://github.com/nerymurillohnd/the-claude-factory/releases/tag/<plugin>--v<version>).

Update with:

```bash
claude plugin update <plugin>@the-claude-factory
```

Then run `/reload-plugins`. Thanks again for reporting it, @<user>!
~~~

## Working as intended

~~~markdown
Thanks for raising this, @<user>. This is working as designed: <explanation>. <How to achieve their goal instead, with a link to the README section>.

Closing for now — feel free to reopen if we missed something.
~~~

## Duplicate

~~~markdown
Thanks @<user>! This is tracked in #<n> — please follow and 👍 that issue for updates. Closing as a duplicate.
~~~

## Upstream (Claude Code or third party)

~~~markdown
Thanks for the detailed report, @<user>. The cause is in <Claude Code / service>, not in the plugin: <evidence>.

Please report it at <https://github.com/anthropics/claude-code/issues or vendor link> and link it here — we'll adapt the plugin if a workaround becomes possible.
~~~

## Question answered

~~~markdown
Hi @<user>! <direct answer>.

More details: <link to README section or docs page>. Closing since this is answered — reopen anytime if you need more help.
~~~

## Security issue posted publicly

~~~markdown
Thank you for reporting this, @<user>. To protect users, please resubmit it privately through [Report a vulnerability](https://github.com/nerymurillohnd/the-claude-factory/security/advisories/new). We've hidden the details here and will follow up there.
~~~

## Stale (no reply to needs-info after 14 days)

~~~markdown
Closing because we didn't get the details needed to reproduce. @<user>, reply with them anytime and we'll reopen. Thanks!
~~~
