# Discussion forms

MCP tools are named `mcp__<server>__<tool>`; find `<server>` as [github-access.md](github-access.md#order-of-routes) says.

1. Discussions must be on: `has_discussions` from step 1. When they are off, tell the user: enabling them is a repository setting and needs approval.
2. Get each category's slug: GitHub names a form file after it. Use the first route that works ([github-access.md](github-access.md)):
   - `gh api graphql`, the only API that returns slugs:

     ```bash
     gh api graphql -f owner=<owner> -f name=<repo> -f query='
       query($owner: String!, $name: String!) {
         repository(owner: $owner, name: $name) {
           discussionCategories(first: 25) { nodes { name slug } }
         }
       }'
     ```

   - When GraphQL is blocked or fails, list the categories with the MCP tool `mcp__<server>__list_discussion_categories` (names and IDs, no slug), then ask the user to open each one in the repository's Discussions tab and paste its URL: the slug is the last part of `https://github.com/<owner>/<repo>/discussions/categories/<slug>`.

   Never derive a slug from a category's name: GitHub does not document the rule.
3. Choose a model for each category the repository uses:

   | Category use | Model |
   | :-- | :-- |
   | Ideas still open, not ready to track | `assets/DISCUSSION_TEMPLATE/ideas.yml` |
   | "How do I…?" questions with no defect | `assets/DISCUSSION_TEMPLATE/q-a.yml` |
   | Sharing a setup or a result | `assets/DISCUSSION_TEMPLATE/show-and-tell.yml` |
   | Hard-to-reverse decisions to debate | `assets/DISCUSSION_TEMPLATE/rfc.yml` |

4. Write each chosen form to `.github/DISCUSSION_TEMPLATE/<category slug>.yml`, with the slug spelled as the repository spells it. A form whose category does not exist yet, such as `rfc`, needs the user to create the category first ([github-access.md](github-access.md#what-has-no-api)):
   - A discussion form takes only `title`, `labels` and `body`: no `name` or `description`.
   - Keep the model's fields and their order, and replace generic options with the repository's components, versions and environments.
   - For `rfc.yml`, keep the fields for context, proposal, alternatives, consequences and a decide-by date, and name the place where the repository records accepted decisions.
   - Mark a field `required: true` only when a post is useless without it, and remove the fields that do not apply.
   - Write field labels that read well as headings: a submitted form becomes one `### <field label>` heading per field.
   - Write each description so it sends people to the right place: something broken is a bug issue; a concrete idea ready to track is an issue; a small, clear change needs no RFC.
5. Run `check-forms.py --kind discussion` on `.github/DISCUSSION_TEMPLATE/*.yml` from the repository's root, with the command in the Scripts table of `SKILL.md`. Fix every finding and run it again; move on only when its summary reads `check-forms: pass`. When it exits 2 for a missing requirement, check the forms by hand as [issue-forms.md](issue-forms.md#validate) says.
6. After the merge, ask the user to open `https://github.com/<owner>/<repo>/discussions/new/choose` signed in.

Discussion forms have no polls.
