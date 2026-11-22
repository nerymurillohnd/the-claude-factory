# Local type stubs for the parts of ruamel.yaml 0.19.1 the maintainer scripts use.
# ruamel.yaml ships py.typed, but annotates these members with names it defines only under
# `if False:` (StreamTextType) or as Any (CommentedBase.lc), so basedpyright sees them as
# unknown. These stubs describe the real runtime types; update them with the uv.lock pin.
from ruamel.yaml.main import YAML as YAML
