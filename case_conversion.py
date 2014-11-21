import sublime_plugin
import re
import sys

PYTHON = sys.version_info[0]

if 3 == PYTHON:
    # Python 3 and ST3
    from . import case_parse
    unicode = str
else:
    # Python 2 and ST2
    import case_parse


def to_snake_case(text):
    words, case, sep = case_parse.parseVariable(text)
    return '_'.join(map(unicode.lower, words))


def to_pascal_case(text):
    words, case, sep = case_parse.parseVariable(text)
    return ''.join(words)


def to_camel_case(text):
    words, case, sep = case_parse.parseVariable(text)
    words[0] = words[0].lower()
    return ''.join(words)


def to_dot_case(text):
    words, case, sep = case_parse.parseVariable(text, True)
    return '.'.join(words)


def to_dash_case(text):
    words, case, sep = case_parse.parseVariable(text, True)
    return '-'.join(words)


def to_slash(text):
    words, case, sep = case_parse.parseVariable(text, True)
    return '/'.join(words)


def to_separate_words(text):
    words, case, sep = case_parse.parseVariable(text)
    return ' '.join(words)


def toggle_case(text):
    words, case, sep = case_parse.parseVariable(text)
    if case == 'pascal' and not sep:
        return to_snake_case(text)
    elif case == 'lower' and sep == '_':
        return to_camel_case(text)
    elif case == 'camel' and not sep:
        return to_pascal_case(text)
    else:
        return text


def run_on_selections(view, edit, func):
    for s in view.sel():
        region = s if s else view.word(s)

        # TODO: preserve leading and trailing whitespace
        view.replace(edit, region, func(view.substr(region)))


class ToggleSnakeCamelPascalCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        run_on_selections(self.view, edit, toggle_case)


class ConvertToSnakeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        run_on_selections(self.view, edit, to_snake_case)


class ConvertToCamel(sublime_plugin.TextCommand):
    def run(self, edit):
        run_on_selections(self.view, edit, to_camel_case)


class ConvertToPascal(sublime_plugin.TextCommand):
    def run(self, edit):
        run_on_selections(self.view, edit, to_pascal_case)


class ConvertToDot(sublime_plugin.TextCommand):
    def run(self, edit):
        run_on_selections(self.view, edit, to_dot_case)


class ConvertToDash(sublime_plugin.TextCommand):
    def run(self, edit):
        run_on_selections(self.view, edit, to_dash_case)


class ConvertToSeparateWords(sublime_plugin.TextCommand):
    def run(self, edit):
        run_on_selections(self.view, edit, to_separate_words)


class ConvertToSlash(sublime_plugin.TextCommand):
    def run(self, edit):
        run_on_selections(self.view, edit, to_slash )