import sublime
import re
import sys

PYTHON = sys.version_info[0]
if 3 == PYTHON: xrange = range


SETTINGS_FILE = "CaseConversion.sublime-settings"


"""
Parses a variable into a list of words.

Also returns the case type, which can be one of the following:

    - upper: All words are upper-case.
    - lower: All words are lower-case.
    - pascal: All words are title-case or upper-case. Note that the variable may still have separators.
    - camel: First word is lower-case, the rest are title-case or upper-case. Variable may still have separators.
    - mixed: Any other mixing of word casing. Never occurs if there are no separators.
    - unknown: Variable contains no words.

Also returns the first separator character, or False if there isn't one.
"""
def parseVariable(var, preserveCase=False):
    settings = sublime.load_settings(SETTINGS_FILE)
    useAcronyms = settings.get("use_acronyms", True)
    acronyms = list(map(unicode.upper, settings.get("acronyms", [])))

    # TODO: include unicode characters.
    lower  = re.compile('^[a-z0-9]$')
    upper  = re.compile('^[A-Z]$')
    sep    = re.compile('^[^a-zA-Z0-9]$')
    notsep = re.compile('^[a-zA-Z0-9]$')

    words = []
    hasSep = False

    # Index of current character. Initially 1 because we don't want to check
    # if the 0th character is a boundary.
    i = 1
    # Index of first character in a sequence
    s = 0
    # Previous character.
    p = var[0:1]

    # Treat an all-caps variable as lower-case, so that every letter isn't
    # counted as a boundary.
    wasUpper = False
    if var.isupper():
        var = var.lower()
        wasUpper = True

    # Iterate over each character, checking for boundaries, or places where
    # the variable should divided.
    while i <= len(var):
        c = var[i:i+1]

        split = False
        if i < len(var):
            # Detect upper-case letter as boundary.
            if upper.match(c):
                split = True
            # Detect transition from separator to not separator.
            elif notsep.match(c) and sep.match(p):
                split = True
            # Detect transition not separator to separator.
            elif sep.match(c) and notsep.match(p):
                split = True
        else:
            # The loop goes one extra iteration so that it can handle the
            # remaining text after the last boundary.
            split = True

        if split:
            if notsep.match(p):
                # Words only; do not include separators.
                words.append(var[s:i])
            else:
                # Variable contains at least one separator.
                # Use the first one as the variable's primary separator.
                if not hasSep: hasSep = var[s:s+1]
            s = i

        i = i + 1
        p = c

    if useAcronyms:
        # Check a run of words represented by the range [st[1], st[0]].
        def checkAcronym(st):
            # Combine each letter into single string.
            acstr = ''
            for j in xrange(st[1], st[0]):
                acstr += words[j]

            # List of ranges representing found acronyms.
            rangeList = []
            # Set of remaining letters.
            notRange = set(range(len(acstr)))

            # Search for each acronym in acstr.
            for acronym in acronyms:
                #TODO: Sanitize acronyms to include only letters.
                rac = re.compile(acronym)

                # Loop so that all instances of the acronym are found, instead
                # of just the first.
                n = 0
                while True:
                    m = rac.search(acstr, n)
                    if not m: break

                    a, b = m.start(), m.end()
                    n = b

                    # Make sure found acronym doesn't overlap with others.
                    ok = True
                    for r in rangeList:
                        if a < r[1] and b > r[0]:
                            ok = False
                            break

                    if ok:
                        rangeList.append((a, b))
                        for j in xrange(a, b):
                            notRange.remove(j)

            # Add remaining letters as ranges.
            for nr in notRange:
                rangeList.append((nr, nr+1))

            # No ranges will overlap, so it's safe to sort by lower bound,
            # which sort() will do by default.
            rangeList.sort()

            # Remove original letters in word list.
            for j in xrange(st[1], st[0]):
                del words[st[1]]

            # Replace them with new word grouping.
            for j in xrange(len(rangeList)):
                r = rangeList[j]
                words.insert(st[1]+j, acstr[r[0]:r[1]])

            st[0] = st[1] + 1
            st[1] = False
            st[2] = False

        st = [
            # Index of current word.
            0,
            # Index of first letter in run.
            False,
            # Previous word.
            False,
        ]

        # Find runs of single uppercase letters.
        while st[0] < len(words):
            word = words[st[0]]
            if upper.match(word):
                if not st[1]: st[1] = st[0]
                st[2] = st[0]
            elif st[2]:
                checkAcronym(st)

            st[0] += 1

        if st[2]: checkAcronym(st)

    # Determine case type.
    caseType = 'unknown'
    if wasUpper:
        caseType = 'upper'
    elif var.islower():
        caseType = 'lower'
    elif len(words) > 0:
        camelCase = words[0].islower()
        pascalCase = words[0].istitle() or words[0].isupper()

        if camelCase or pascalCase:
            for word in words[1:]:
                c = word.istitle() or word.isupper()
                camelCase &= c
                pascalCase &= c
                if not c: break

        if camelCase:
            caseType = 'camel'
        elif pascalCase:
            caseType = 'pascal'
        else:
            caseType = 'mixed'

    if preserveCase:
        if wasUpper:
            words = list(map(unicode.upper, words))
    else:
        # Normalize case of each word to PascalCase. From there, other cases
        # can be worked out easily.
        for i in xrange(len(words)):
            if useAcronyms and words[i].upper() in acronyms:
                words[i] = words[i].upper()
            else:
                words[i] = words[i].capitalize()

    return words, caseType, hasSep
