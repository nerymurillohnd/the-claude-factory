# Prints standard input as one JSON string literal: quotes, backslashes and control characters
# escaped, lines joined with \n. POSIX awk; run it with LC_ALL=C, so text is read as bytes.

BEGIN {
	for (i = 1; i < 32; i++) {
		escaped[sprintf("%c", i)] = sprintf("\\u%04x", i)
	}
	escaped["\t"] = "\\t"
	escaped["\r"] = "\\r"
	escaped["\""] = "\\\""
	escaped["\\"] = "\\\\"
	out = ""
}

{
	if (NR > 1) {
		out = out "\\n"
	}
	line = $0
	for (i = 1; i <= length(line); i++) {
		c = substr(line, i, 1)
		out = out ((c in escaped) ? escaped[c] : c)
	}
}

END { printf "\"%s\"", out }
