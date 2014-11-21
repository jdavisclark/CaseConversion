import sublime
import sublime_plugin
import re
import sys

PYTHON = sys.version_info[0]

if 3 == PYTHON:
    # Python 3 and ST3
    from . import case_parse
else:
    # Python 2 and ST2
    import case_parse


SETTINGS_FILE = "CaseConversion.sublime-settings"


def to_snake_case(text, useAcronyms, acronyms):
    words, case, sep = case_parse.parseVariable(text, useAcronyms, acronyms)
    return '_'.join([w.lower() for w in words])


def to_pascal_case(text, useAcronyms, acronyms):
    words, case, sep = case_parse.parseVariable(text, useAcronyms, acronyms)
    return ''.join(words)


def to_camel_case(text, useAcronyms, acronyms):
    words, case, sep = case_parse.parseVariable(text, useAcronyms, acronyms)
    words[0] = words[0].lower()
    return ''.join(words)


def to_dot_case(text, useAcronyms, acronyms):
    words, case, sep = case_parse.parseVariable(text, useAcronyms, acronyms, True)
    return '.'.join(words)


def to_dash_case(text, useAcronyms, acronyms):
    words, case, sep = case_parse.parseVariable(text, useAcronyms, acronyms, True)
    return '-'.join(words)


def to_slash(text, useAcronyms, acronyms):
    words, case, sep = case_parse.parseVariable(text, useAcronyms, acronyms, True)
    return '/'.join(words)


def to_separate_words(text, useAcronyms, acronyms):
    words, case, sep = case_parse.parseVariable(text, useAcronyms, acronyms)
    return ' '.join(words)


def toggle_case(text, useAcronyms, acronyms):
    words, case, sep = case_parse.parseVariable(text, useAcronyms, acronyms)
    if case == 'pascal' and not sep:
        return to_snake_case(text, useAcronyms, acronyms)
    elif case == 'lower' and sep == '_':
        return to_camel_case(text, useAcronyms, acronyms)
    elif case == 'camel' and not sep:
        return to_pascal_case(text, useAcronyms, acronyms)
    else:
        return text


def run_on_selections(view, edit, func):
    settings = sublime.load_settings(SETTINGS_FILE)
    useAcronyms = settings.get("use_acronyms", True)
    acronyms = settings.get("acronyms", [])

    for s in view.sel():
        region = s if s else view.word(s)

        # TODO: preserve leading and trailing whitespace
        view.replace(edit, region, func(view.substr(region), useAcronyms, acronyms))


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