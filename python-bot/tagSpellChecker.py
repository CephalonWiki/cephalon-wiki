# Taken from https://norvig.com/spell-correct.html

import string
from collections import Counter

import warframeWikiArticles
from CephalonWikiLogger import spell_checker


# will use lower case words for the dictionary
articles = warframeWikiArticles.load()
WORDS = Counter(articles.keys())

def P(word, N=sum(WORDS.values())):
    "Probability of `word`."
    return WORDS[word] / N

def correction(word):
    #90% of entries have length <= 21
    if len(word) > 30:
        return word

    suggested_correction = max(candidates(word.lower()), key=P)

    # if we actually make a correction, return title from dictionary
    if suggested_correction != word.lower():
        spell_checker.info("Spell checker corrected %s to %s", word.lower(), suggested_correction)
        return articles[suggested_correction]['title']
    else:
        spell_checker.info("No correction made for %s", word)
        return word

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
