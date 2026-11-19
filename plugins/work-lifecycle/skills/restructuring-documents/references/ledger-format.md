# Ledger format

The ledger says where every line of every source file goes. The script reads it as tab-separated text: one row per line, comments start with `#`, and blank lines are ignored.

## Columns

| Column | Holds |
| :-- | :-- |
| kind | `move`, `struct`, `drop`, `split` or `edit` |
| source | the source file, relative to the baseline folder |
| start, end | the first and last line of the range, inclusive, in the baseline |
| dest | for `move`, the destination file, relative to the current folder; otherwise `-` |
| note | why the lines may disappear; required for `struct`, `drop` and `edit`; the parts for `split` |

## Kinds

- **move**: the lines go to `dest` unchanged. Include the blank lines between ranges, so each source line belongs to one row.
- **struct**: a title, a blank line or a contents entry that each new file replaces with its own. Use it only after reading the line: a sentence that states a rule, a fact or an instruction is content, even inside an intro.
- **drop**: a duplicate the requester approved removing. The note names the file that keeps the fact.
- **split**: one line whose parts go to different places, such as an intro that describes the file and then states a rule. The note lists the parts in order, separated by ` ||| `, each as `destination|text`, with `struct` as the destination of a part that each new file replaces. The parts must join back to the original line.
- **edit**: a line reworded on purpose, such as a pointer that now names a new file. A file with only `edit` rows is edited in place and needs no other rows; inside a moved range, give the edited line its own row.

## Example

````text
# kind	source	start	end	dest	note
struct	guide.md	1	2	-	old title; each new file has its own
split	guide.md	3	3	-	struct|Covers setup and use. ||| setup.md|Run every command from the project root.
move	guide.md	4	20	setup.md
drop	guide.md	21	21	-	same rule as setup.md line 7
move	guide.md	22	60	usage.md
edit	index.md	12	12	-	link now points to setup.md and usage.md
````

Here `guide.md` splits into `setup.md` and `usage.md`. Its intro's rule moves to `setup.md`, one duplicate is dropped, and `index.md` is edited in place to point at the new files.
