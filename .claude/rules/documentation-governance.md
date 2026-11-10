# Documentation governance

- A plugin's `README.md` and `CHANGELOG.md` are each written only by the agent that owns them. If you are not that agent, do not write or edit them: a hook denies the write.
- Before any documentation work, and whenever a hook reports a pending documentation chain, load the `documentation-governance` skill and follow it. It says which chain an event sets off and how to run it.
- If you are an owning agent, this rule does not restrict you: write your document as your contract says.
