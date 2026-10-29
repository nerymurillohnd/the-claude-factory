# Discussions: start, answer, close

Start a discussion in the right category, or answer one. Installing discussion forms is `setup/templates.md`.

## 1. Choose

| Signal | Category slug | Form |
| :-- | :-- | :-- |
| An idea still open, not ready to track | `ideas` | `ideas.yml` |
| "How do I…?" with no defect | `q-a` | `q-a.yml` |
| Sharing a setup or a result | `show-and-tell` | `show-and-tell.yml` |
| A hard-to-reverse decision to debate | `rfc` | `rfc.yml` |

1. Something is broken: open a bug issue instead (`authoring/issue.md`).
2. The idea is concrete and ready to track: open an issue.
3. A small, clear change needs no RFC: go to an issue or a PR.
4. Use the repository's form in `.github/DISCUSSION_TEMPLATE/` when it has one; with none, the plugin's in `<skill-dir>/assets/DISCUSSION_TEMPLATE/`.

## 2. Start a discussion

Check the live MCP tool list for a discussion create tool first. Without one, pick a path.

**Path A, hand it to the user:** draft the answers for each form field in order, and give the user the link `https://github.com/<owner>/<repo>/discussions/new?category=<slug>` with the drafted answers to paste.

**Path B, create it through the API:**

1. Get the repository id and the category ids:

   ```bash
   gh api graphql -f query='query { repository(owner:"<owner>", name:"<repo>") { id discussionCategories(first:25) { nodes { id slug name } } } }'
   ```

2. Pick the category whose `slug` matches the form.
3. Write the body to a file outside the repository, mirroring the form fields in order with one `### <field label>` heading each: the API applies no form.
4. Show the user the exact title and body. Create it only after approval:

   ```bash
   gh api graphql \
     -f query='mutation($r:ID!,$c:ID!,$t:String!,$b:String!){createDiscussion(input:{repositoryId:$r,categoryId:$c,title:$t,body:$b}){discussion{url}}}' \
     -f r=<repository id> -f c=<category id> -f t='<title>' -F b=@<body file>
   ```

5. Report the URL.

For every path: follow the form's fields and order; for an RFC, fill context, proposal, alternatives, consequences and a decide-by date, facts first; remove secrets, personal data and customer names.

## 3. Answer or close one

1. Read the discussion with MCP `get_discussion` and `get_discussion_comments`, or GraphQL on `repository.discussion(number:)`.
2. Show the user the reply. Post it only after approval, with MCP `discussion_comment_write`, or the GraphQL `addDiscussionComment` mutation (`discussionId`, `body`, optional `replyToId`).
3. Keep the reply short and concrete, and link the docs, issue or PR that settle it.
4. When an RFC is accepted, link the decision record in the closing comment.
5. When a Q&A turns out to be a defect, open a bug issue and link it.

## 4. Limits

- Forms are read from the default branch only, and `required: true` is enforced only in public repositories.
- Discussion forms have no polls.
- No mutation creates a category: categories are created by hand in **Settings → Discussions**.
