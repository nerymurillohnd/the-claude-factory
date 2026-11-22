class StreamMark:
    name: object
    index: int
    line: int
    column: int

class YAMLError(Exception): ...

class MarkedYAMLError(YAMLError):
    context: str | None
    context_mark: StreamMark | None
    problem: str | None
    problem_mark: StreamMark | None
    note: str | None
