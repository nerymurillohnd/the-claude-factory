# Discussion forms

1. Discussions must be on. When they are off, tell the user: enabling them is a repository setting and needs approval.
2. Get each category's slug: GitHub names a form file after it. Use the first route that works:
   - `gh api graphql`, which also says whether Discussions is on (`hasDiscussionsEnabled: false` is the case in step 1):

     ```bash
     gh api graphql -f owner=<owner> -f name=<repo> -f query='
       query($owner: String!, $name: String!) {
         repository(owner: $owner, name: $name) {
           hasDiscussionsEnabled
           discussionCategories(first: 25) { nodes { name slug } }
         }
       }'
     ```

   - When GraphQL is unavailable or fails, ask the user to open each category in the repository's Discussions tab and paste its URL: the slug is the last part of `https://github.com/<owner>/<repo>/discussions/categories/<slug>`.

   The MCP `list_discussion_categories` tool lists the categories' names and IDs, which helps to ask about them, but returns no slug. Never derive a slug from a category's name: GitHub does not document the rule.
3. Choose a model from `<skill-dir>/assets/DISCUSSION_TEMPLATE/` for each category the repository uses:

   | Category use | Model |
   | :-- | :-- |
   | Ideas still open, not ready to track | `ideas.yml` |
   | "How do I…?" questions with no defect | `q-a.yml` |
   | Sharing a setup or a result | `show-and-tell.yml` |
   | Hard-to-reverse decisions to debate | `rfc.yml` |

4. Write each chosen form to `.github/DISCUSSION_TEMPLATE/<category slug>.yml`, with the slug spelled as the repository spells it:
   - Keep the model's fields and their order, and replace generic options with the repository's components, versions and environments.
   - For `rfc.yml`, keep the fields for context, proposal, alternatives, consequences and a decide-by date, and name the place where the repository records accepted decisions.
   - Mark a field `required: true` only when a post is useless without it, and remove the fields that do not apply.
   - Write field labels that read well as headings: a submitted form becomes one `### <field label>` heading per field.
   - Write each description so it sends people to the right place: something broken is a bug issue; a concrete idea ready to track is an issue; a small, clear change needs no RFC.
5. Run `<skill-dir>/scripts/check-forms.py --kind discussion .github/DISCUSSION_TEMPLATE/*.yml` from the repository's root. Fix every finding and run it again; move on only when it exits 0.
6. After the merge, ask the user to open `https://github.com/<owner>/<repo>/discussions/new/choose` signed in.

Limits:

- `required: true` is enforced only in public repositories.
- Discussion forms have no polls.
- No mutation creates a category: a form whose category does not exist, such as `rfc`, needs the user to create it in **Settings → Discussions** first.
