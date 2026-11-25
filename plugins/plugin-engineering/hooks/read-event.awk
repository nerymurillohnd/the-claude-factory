# Reads one Claude Code hook event (a JSON object) on standard input and prints the fields
# validate-plugin.sh needs, one per line as "<path>\t<value>": tool_name and
# tool_input.file_path. A string that holds a newline, a tab or a carriage return is left out:
# it can't be a field of one line, and no path the hook checks has one. Exits 3, printing
# nothing, when the input is not one JSON object. POSIX awk; run it with LC_ALL=C, so text is
# read and written as bytes.

BEGIN {
	scalar["tool_name"] = 1
	scalar["tool_input.file_path"] = 1
	hexdigits = "0123456789abcdef"
}

{ text = text $0 "\n" }

END {
	pos = 1
	n = length(text)
	ws()
	if (substr(text, pos, 1) != "{" || !value("")) {
		exit 3
	}
	ws()
	if (pos <= n) {
		exit 3
	}
	printf "%s", out
}

function ws() {
	while (pos <= n && index(" \t\n\r", substr(text, pos, 1)) > 0) {
		pos++
	}
}

function keep(path, text_value) {
	if ((path in scalar) && text_value !~ /[\n\t\r]/) {
		out = out path "\t" text_value "\n"
	}
}

# Parses the value at pos; path names it ("a.b", "a.b[]" for an element). 1 on success.
function value(path,    c) {
	ws()
	c = substr(text, pos, 1)
	if (c == "{") {
		pos++
		ws()
		if (substr(text, pos, 1) == "}") {
			pos++
			return 1
		}
		for (;;) {
			ws()
			if (substr(text, pos, 1) != "\"" || !string(1)) {
				return 0
			}
			key = str
			ws()
			if (substr(text, pos, 1) != ":") {
				return 0
			}
			pos++
			if (!value(path == "" ? key : (path "." key))) {
				return 0
			}
			ws()
			c = substr(text, pos, 1)
			pos++
			if (c == "}") {
				return 1
			}
			if (c != ",") {
				return 0
			}
		}
	}
	if (c == "[") {
		pos++
		ws()
		if (substr(text, pos, 1) == "]") {
			pos++
			return 1
		}
		for (;;) {
			if (!value(path "[]")) {
				return 0
			}
			ws()
			c = substr(text, pos, 1)
			pos++
			if (c == "]") {
				return 1
			}
			if (c != ",") {
				return 0
			}
		}
	}
	if (c == "\"") {
		if (!string((path in scalar) ? 1 : 0)) {
			return 0
		}
		keep(path, str)
		return 1
	}
	if (match(substr(text, pos, 64), /^-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][-+]?[0-9]+)?/)) {
		pos += RLENGTH
		return 1
	}
	if (substr(text, pos, 4) == "true" || substr(text, pos, 4) == "null") {
		pos += 4
		return 1
	}
	if (substr(text, pos, 5) == "false") {
		pos += 5
		return 1
	}
	return 0
}

# Parses the string that starts at pos (on its opening quote), into str when build is 1; with
# build 0 it only moves past it, so long values the hook never reads, such as a Write's
# content, cost no copying. 1 on success.
function string(build,    chunk, at, c, code, low) {
	str = ""
	pos++
	for (;;) {
		if (pos > n) {
			return 0
		}
		chunk = substr(text, pos, 512)
		at = match(chunk, /["\\\n]/)
		if (at == 0) {
			if (build) {
				str = str chunk
			}
			pos += length(chunk)
			continue
		}
		if (build) {
			str = str substr(chunk, 1, at - 1)
		}
		pos += at - 1
		c = substr(text, pos, 1)
		if (c == "\"") {
			pos++
			return 1
		}
		if (c == "\n") {
			return 0
		}
		c = substr(text, pos + 1, 1)
		pos += 2
		if (!build) {
			if (c == "u") {
				if (hex4(substr(text, pos, 4)) < 0) {
					return 0
				}
				pos += 4
			} else if (c == "" || index("\"\\/bfnrt", c) == 0) {
				return 0
			}
		} else if (c == "\"" || c == "\\" || c == "/") {
			str = str c
		} else if (c == "b") {
			str = str "\b"
		} else if (c == "f") {
			str = str "\f"
		} else if (c == "n") {
			str = str "\n"
		} else if (c == "r") {
			str = str "\r"
		} else if (c == "t") {
			str = str "\t"
		} else if (c == "u") {
			code = hex4(substr(text, pos, 4))
			if (code < 0) {
				return 0
			}
			pos += 4
			if (code >= 55296 && code < 56320 && substr(text, pos, 2) == "\\u") {
				low = hex4(substr(text, pos + 2, 4))
				if (low >= 56320 && low < 57344) {
					code = 65536 + (code - 55296) * 1024 + (low - 56320)
					pos += 6
				}
			}
			str = str utf8(code)
		} else {
			return 0
		}
	}
}

# The value of four hexadecimal digits, or -1.
function hex4(digits,    i, d, total) {
	if (length(digits) != 4) {
		return -1
	}
	total = 0
	for (i = 1; i <= 4; i++) {
		d = index(hexdigits, tolower(substr(digits, i, 1)))
		if (d == 0) {
			return -1
		}
		total = total * 16 + d - 1
	}
	return total
}

# The UTF-8 bytes of a code point.
function utf8(code) {
	if (code < 128) {
		return sprintf("%c", code)
	}
	if (code < 2048) {
		return sprintf("%c%c", 192 + int(code / 64), 128 + code % 64)
	}
	if (code < 65536) {
		return sprintf("%c%c%c", 224 + int(code / 4096), 128 + int(code / 64) % 64, 128 + code % 64)
	}
	return sprintf("%c%c%c%c", 240 + int(code / 262144), 128 + int(code / 4096) % 64, 128 + int(code / 64) % 64, 128 + code % 64)
}
