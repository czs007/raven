import sys
import re
from collections import Counter

################ ReleaseNote Generate

useful_keys = {
        "feat": "Features",
        "fix" : "BugFixes",
        "enhance":"Improvements",
        "abandon":"Abandons (DO NOT include in ReleaseNote)",
}

abandon_keys = [
    "test",
    "doc",
    "auto",
    "[automated]",
    "automated",
]

summary = "This passage provides an overall introduction to the modifications introduced in this version."
print_orders = ["feat", "enhance", "fix", "abandon"]

def parse_group(line):
    c_index = line.find(':') + 1
    my_key = line[0: c_index].lower()
    correct_my_key =  correction(my_key)
    for key in useful_keys:
        if correct_my_key.startswith(key):
            return key

    for key in abandon_keys:
        if line.startswith(key):
            return key 
    return ""

def is_valid(line):
    line = line.strip()
    pattern = r"(\(#\d+\))"
    matches = re.findall(pattern, line)
    return bool(matches)

def trim_line(line):
    line = line.strip()
    pattern = r"(\(#\d+\))"
    matches = re.findall(pattern, line)
    if not is_valid(line):
        return line, False

    line = line[line.find(' ') + 1:]
    c_index = line.find(':') + 1
    v_index = line[0:c_index].rfind(' ') + 1
    line = line[v_index:]
    return line, True

def group_lines(pr_lines):
    ret = {}
    for line in pr_lines:
        line, valid = trim_line(line)
        if not line:
            continue
        if not valid:
            group = "abandon"
        else:
            group = parse_group(line)
            if group:
               line = line[len(group) + 1:].strip()

            line = line.capitalize()

            if not group or group in abandon_keys:
                group = "abandon"

        if group not in ret:
            ret[group] = []

        ret[group].append(line)
    return ret

prefix_url ="https://github.com/milvus-io/milvus/pull/"
commit_prefix_url = "https://github.com/milvus-io/milvus/commit/"

def compose_lines(commit_lines):
    ret = []
    for line in commit_lines:
        fmt = "[{}]({}{})"
        if is_valid(line):
            pattern = r"(\(#\d+\))"
            matches = re.findall(pattern, line)
            for match in matches[0:-1]:
                line = line.replace(match, '')
            match = matches[-1]
            number = match[2:-1]
            sharp_number = "#" + number
            new_sub = "(" + fmt.format(sharp_number, prefix_url, number) + ")"
            new_line = line.replace(match, new_sub)
        else:
            commit = line[0:line.find(' ')]
            new_sub = "(" + fmt.format(commit, commit_prefix_url, commit) + ")"
            new_line = line.replace(commit, new_sub)

        ret.append("- %s"%new_line)
    return ret

def generate_text(commit_lines):
    group_result = group_lines(commit_lines)
    ret_lines = [summary]
    for key in print_orders:
        results = group_result.get(key, [])
        if results:
            title = "## %s"%useful_keys[key]
            ret_lines.append(title)
            ret = compose_lines(results)
            ret_lines.extend(ret)

    return "\n".join(ret_lines)

################ ReleaseNote Generate

################ Spelling Corrector 
"""Spelling Corrector in Python 3; see http://norvig.com/spell-correct.html
"""

WORDS = Counter()
for k in set(useful_keys)|set(abandon_keys):
    WORDS[k] = 100

def P(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return WORDS[word] / N

def correction(word): 
    "Most probable spelling correction for word."
    return max(candidates(word), key=P)

def candidates(word): 
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

################ Spelling Corrector 

if __name__ == "__main__":
    commit_lines = [ l for l in sys.stdin]
    print(generate_text(commit_lines))
