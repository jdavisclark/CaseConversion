import re
import sys

PYTHON = sys.version_info[0]
if 3 == PYTHON: xrange = range


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
def parseVariable(var, detectAcronyms=True, acronyms=[], preserveCase=False):
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
                words.append(var[s:i])
            else:
                # Variable contains at least one separator.
                # Use the first one as the variable's primary separator.
                if not hasSep: hasSep = var[s:s+1]

                # Use None to indicate a separator in the word list.
                words.append(None)
                # If separators weren't included in the list, then breaks
                # between upper-case sequences ("AAA_BBB") would be
                # disregarded; the letter-run detector would count them as one
                # sequence ("AAABBB").
            s = i

        i = i + 1
        p = c

    if detectAcronyms:
        if acronyms:
            # Use advanced acronym detection with list

            # Sanitize acronyms list by discarding invalid acronyms and
            # normalizing valid ones to upper-case.
            validacronym = re.compile('^[a-zA-Z0-9]+$')
            unsafeacronyms = acronyms
            acronyms = []
            for a in unsafeacronyms:
                if validacronym.match(a):
                    acronyms.append(a.upper())
                else:
                    print("Case Conversion: acronym '%s' was discarded for being invalid" % a)

            # Check a run of words represented by the range [s, i]. Should
            # return last index of new word groups.
            def checkAcronym(s, i):
                # Combine each letter into single string.
                acstr = ''.join(words[s:i])

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
                for j in xrange(s, i): del words[s]

                # Replace them with new word grouping.
                for j in xrange(len(rangeList)):
                    r = rangeList[j]
                    words.insert(s+j, acstr[r[0]:r[1]])

                return s+len(rangeList)-1
        else:
            # Fallback to simple acronym detection.
            def checkAcronym(s, i):
                # Combine each letter into a single string.
                acronym = ''.join(words[s:i])

                # Remove original letters in word list.
                for j in xrange(s, i): del words[s]

                # Replace them with new word grouping.
                words.insert(s,''.join(acronym))

                return s

        # Letter-run detector

        # Index of current word.
        i = 0
        # Index of first letter in run.
        s = None

        # Find runs of single upper-case letters.
        while i < len(words):
            word = words[i]
            if word != None and upper.match(word):
                if s == None: s = i
            elif s != None:
                i = checkAcronym(s, i) + 1
                s = None

            i += 1

        if s != None:
            checkAcronym(s, i)

    # Separators are no longer needed, so they can be removed. They *should*
    # be removed, since it's supposed to be a *word* list.
    words = [w for w in words if w != None]

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
            words = [w.upper() for w in words]
    else:
        # Normalize case of each word to PascalCase. From there, other cases
        # can be worked out easily.
        for i in xrange(len(words)):
            if detectAcronyms:
                if acronyms:
                    if words[i].upper() in acronyms:
                        # Convert known acronyms to upper-case.
                        words[i] = words[i].upper()
                    else:
                        # Capitalize everything else.
                        words[i] = words[i].capitalize()
                else:
                    # Fallback behavior: Preserve case on upper-case words.
                    if not words[i].isupper():
                        words[i] = words[i].capitalize()
            else:
                words[i] = words[i].capitalize()

    return words, caseType, hasSep
