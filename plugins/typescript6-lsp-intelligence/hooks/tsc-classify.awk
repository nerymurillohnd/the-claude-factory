# Sorts one `tsc --listFiles --extendedDiagnostics` run for hooks/tsc-check.sh. File 1 lists the
# group's changed files (physical paths), file 2 is tsc's output. Variables: folder, the folder
# tsc ran from; base, the project folder; project, 1 when tsc ran under a tsconfig.json.
# Prints one line per finding:
#   M <file>:<line>:<col>  <code>  <message>   an error in a changed file
#   O <file>:<line>:<col>  <code>  <message>   an error in another file, or a file-less error
#   N <file>                                   a changed file missing from --listFiles
#   B                                          no "Check time" line: the type checker did not run
#   U <line>                                   a line tsc printed that matches none of these
# POSIX awk, for the awk of macOS and Linux.

function norm(path,   n, i, parts, out, k) {
  n = split(path, parts, "/")
  k = 0
  for (i = 1; i <= n; i++) {
    if (parts[i] == "" || parts[i] == ".") continue
    if (parts[i] == "..") { if (k > 0) k--; continue }
    out[++k] = parts[i]
  }
  path = ""
  for (i = 1; i <= k; i++) path = path "/" out[i]
  return path == "" ? "/" : path
}

function shown(path) {
  return index(path, base "/") == 1 ? substr(path, length(base) + 2) : path
}

NR == FNR { changed[$0] = 1; order[++count] = $0; next }

/^Check time:/ { checked = 1; next }

# --extendedDiagnostics statistics, such as "Files:  83" or "I/O read:  0.01s".
/^[A-Za-z][A-Za-z\/ ().-]*: +[0-9]/ { next }

# Continuation lines of the previous error, and blank lines.
/^[ \t]/ || /^$/ { next }

/^error TS[0-9]+: / { print "O\t" $0; next }

index($0, "): error TS") > 0 {
  i = index($0, "): error TS")
  head = substr($0, 1, i - 1)
  rest = substr($0, i + 3)
  p = 0
  for (j = length(head); j > 0; j--) if (substr(head, j, 1) == "(") { p = j; break }
  path = substr(head, 1, p - 1)
  split(substr(head, p + 1), at, ",")
  code = substr(rest, 7, index(rest, ":") - 7)
  text = substr(rest, index(rest, ": ") + 2)
  file = norm(substr(path, 1, 1) == "/" ? path : folder "/" path)
  print (file in changed ? "M" : "O") "\t" shown(file) ":" at[1] ":" at[2] "  " code "  " text
  next
}

/^\// { listed[$0] = 1; next }

{ print "U\t" $0 }

END {
  if (project == "1") for (i = 1; i <= count; i++) if (!(order[i] in listed)) print "N\t" shown(order[i])
  if (!checked) print "B"
}
