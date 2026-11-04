# Discussion forms: design them for the repository

Write the content of each discussion form you chose in `setup/templates.md`, section 3, from its model in `<skill-dir>/assets/DISCUSSION_TEMPLATE/`, so each category asks for what the repository's community needs.

## 1. Keep discussions and issues apart

Write each form's description so it sends people to the right place:

- Something is broken: a bug issue, not a discussion.
- An idea that is concrete and ready to track: an issue.
- A small, clear change needs no RFC: an issue or a pull request.

## 2. Adapt the fields

1. Name the file after the category's slug, as the repository spells it.
2. Keep the model's fields and their order, and replace generic options with the repository's components, versions and environments.
3. For `rfc.yml`, keep the fields for context, proposal, alternatives, consequences and a decide-by date, and name the place where accepted decisions are recorded in the repository.
4. Mark a field `required: true` only when a post is useless without it.
5. Remove fields that do not apply to the repository.

## 3. How a submitted form reads

GitHub writes a submitted form as one `### <field label>` heading per field, in order. Write field labels that read well as headings.
