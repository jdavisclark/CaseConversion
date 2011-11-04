import sublime_plugin
import re


def to_snake_case(text):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def strip_wrapping_underscores(text):
    return re.sub("^(_*)(.*?)(_*)$", r'\2', text)


def get_indexes(text, char):
    indexlist = []
    last = 0
    while last != -1:
        pos = text.find(char, last)
        if pos == -1:
            break
        else:
            indexlist.append(pos)
            last = pos + 1
    return indexlist


def to_pascal_case(text):
    if "_" in text:
        callback = lambda pat: pat.group(1).lower() + pat.group(2).upper()
        text = re.sub("(\w)_(\w)", callback, text)
        if text[0].islower():
            text = text[0].upper() + text[1:]
        return text
    return text[0].upper() + text[1:]


def to_camel_case(text):
    text = to_pascal_case(text)
    return text[0].lower() + text[1:]


def run_on_selections(view, edit, func):
    for s in view.sel():
        region = view.word(s)
        text = strip_wrapping_underscores(view.substr(region))
        view.replace(edit, region, func(text))


class ConvertToSnakeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        run_on_selections(self.view, edit, to_snake_case)


class ConvertToCamel(sublime_plugin.TextCommand):
    def run(self, edit):
        run_on_selections(self.view, edit, to_camel_case)


class ConvertToPascal(sublime_plugin.TextCommand):
    def run(self, edit):
        run_on_selections(self.view, edit, to_pascal_case)
