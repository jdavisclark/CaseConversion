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


def to_snake_case(text, detectAcronyms, acronyms):
    words, case, sep = case_parse.parseVariable(text, detectAcronyms, acronyms)
    return '_'.join([w.lower() for w in words])


def to_pascal_case(text, detectAcronyms, acronyms):
    words, case, sep = case_parse.parseVariable(text, detectAcronyms, acronyms)
    return ''.join(words)


def to_camel_case(text, detectAcronyms, acronyms):
    words, case, sep = case_parse.parseVariable(text, detectAcronyms, acronyms)
    words[0] = words[0].lower()
    return ''.join(words)


def to_dot_case(text, detectAcronyms, acronyms):
    words, case, sep = case_parse.parseVariable(text, detectAcronyms, acronyms)
    return '.'.join([w.lower() for w in words])


def to_dash_case(text, detectAcronyms, acronyms):
    words, case, sep = case_parse.parseVariable(text, detectAcronyms, acronyms)
    return '-'.join([w.lower() for w in words])


def to_slash(text, detectAcronyms, acronyms):
    words, case, sep = case_parse.parseVariable(text, detectAcronyms, acronyms, True)
    return '/'.join(words)


def to_separate_words(text, detectAcronyms, acronyms):
    words, case, sep = case_parse.parseVariable(text, detectAcronyms, acronyms, True)
    return ' '.join(words)


def toggle_case(text, detectAcronyms, acronyms):
    words, case, sep = case_parse.parseVariable(text, detectAcronyms, acronyms)
    if case == 'pascal' and not sep:
        return to_snake_case(text, detectAcronyms, acronyms)
    elif case == 'lower' and sep == '_':
        return to_camel_case(text, detectAcronyms, acronyms)
    elif case == 'camel' and not sep:
        return to_pascal_case(text, detectAcronyms, acronyms)
    else:
        return text


def run_on_selections(view, edit, func):
    settings = sublime.load_settings(SETTINGS_FILE)
    detectAcronyms = settings.get("detect_acronyms", True)
    useList = settings.get("use_acronyms_list", True)
    if useList:
        acronyms = settings.get("acronyms", [])
    else:
        acronyms = False

    for s in view.sel():
        region = s if s else view.word(s)

        text = view.substr(region)
        # Preserve leading and trailing whitespace
        leading = text[:len(text)-len(text.lstrip())]
        trailing = text[len(text.rstrip()):]
        text = func(text.strip(), detectAcronyms, acronyms)
        view.replace(edit, region, leading + text + trailing)


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