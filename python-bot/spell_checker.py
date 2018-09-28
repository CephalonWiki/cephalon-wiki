# Taken from https://norvig.com/spell-correct.html

import string
from collections import Counter
import all_articles

# mapping from lower case article titles to titles with correct captilization
case_dict = {w.lower():w for w in all_articles.article_title_list}

# will use lower case words for the dictionary
WORDS = Counter(map(lambda w: w.lower(), all_articles.article_title_list))

def P(word, N=sum(WORDS.values())):
    "Probability of `word`."
    return WORDS[word] / N

def correction(word):
    "Most probable spelling correction for word."
    suggested_correction = max(candidates(word.lower()), key=P)

    # if we actually make a correction, return word with proper capitalization using the case_dict
    if suggested_correction != word:
        return case_dict[suggested_correction]
    else:
        return suggested_correction

def candidates(word):
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words):
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = string.printable.replace(string.ascii_uppercase,"")
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))
