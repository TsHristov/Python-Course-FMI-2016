import re
import ast
from collections import defaultdict


class CodeErrors:
    def line_too_long(self, actual, allowed):
        if actual > allowed:
            return 'line too long ({} > {})'.format(actual, allowed)

    def multiple_expressions(self):
        return 'multiple expressions on the same line'

    def nesting_too_deep(self, actual, allowed):
        if actual > allowed:
            return 'nesting too deep ({} > {})'.format(actual, allowed)

    def indentation(self, actual, allowed):
        if actual > allowed:
            return 'indentation is {} instead of {}'.format(actual, allowed)

    def too_many_methods_in_class(self, actual, allowed):
        pass

    def too_many_arguments(self, actual, allowed):
        pass

    def trailing_whitespace(self):
        pass

    def too_many_lines(self, actual, allowed):
        pass


class CodeAnalyzer:
    # Set of rules with default values
    # that apply to the code under inspection.
    RULES = {
        'line_length': 79,
        'forbid_semicolons': True,
        'max_nesting': None,
        'indentation_size': 4,
        'methods_per_class': None,
        'max_arity': None,
        'forbid_trailing_whitespace': True,
        'max_lines_per_function': None
    }

    def __init__(self, code, rules=None):
        self.parsed_code = ast.parse(code)
        self.code = code
        self.rules = rules
        # Keys are the line numbers
        # at which errors were found.
        self.issues = defaultdict(set)
        self.code_errors = CodeErrors()

    @classmethod
    def get_instance_methods(cls):
        """Return set of all instance methods."""
        return {method for method in
                dir(cls) if
                callable(getattr(cls, method)) and not
                method.startswith('__')}

    def analyze(self):
        """Inpect the code and call all instance
           methods on it.
        """
        if not self.rules:
            methods = self.get_instance_methods()
            methods.discard('analyze')
            methods.discard('get_instance_methods')
            for method in methods:
                # Call each method:
                getattr(type(self), method)(self)
        return self.issues

    def line_length(self):
        """Inspect the code for too long lines."""
        default_length = self.RULES['line_length']
        for lineno, line in enumerate(self.code.splitlines()):
            length = len(line)
            if length > default_length:
                self.issues[lineno+1].add(
                    self.code_errors.line_too_long(length, default_length)
                    )

    def forbid_semicolons(self):
        """Inspect the code for semicolon separated statements."""
        for lineno, line in enumerate(self.code.splitlines()):
            if re.search('(;)', line):
                self.issues[lineno+1].add(
                    self.code_errors.multiple_expressions()
                )

    def max_nesting(self):
        """Inspect the code for too much nesting."""
        max_nesting_level = 3  # max_nesting
        nesting_level = 0
        # Traverse the nodes and find those that are nested
        # (have 'body' attribute).
        nodes = [node for node in ast.walk(self.parsed_code.body[0])
                 if 'body' in node._fields]
        nesting_level = len(nodes)
        if nesting_level > max_nesting_level:
            # The line number where the error was found
            # is the next one.
            lineno = nodes[len(nodes)-1].lineno + 1
            self.issues[lineno].add(
                self.code_errors.nesting_too_deep(
                    nesting_level, max_nesting_level
                )
            )

    def indentation_size(self):
        """Inspect the code for indentation size errors."""
        # Use the previous line offset
        # as a guide for the next line indentation.
        last_offset = 0
        indent = self.RULES['indentation_size']
        for node in ast.walk(self.parsed_code):
            if 'body' in node._fields:
                lineno = node.body[0].lineno
                col_offset = node.body[0].col_offset
                if col_offset > last_offset + indent:
                    offset = col_offset - last_offset
                    self.issues[lineno].add(
                        self.code_errors.indentation(offset, indent)
                    )
                last_offset = col_offset

    def methods_per_class(self):
        pass

    def max_arity(self):
        pass

    def forbid_trailing_whitespace(self):
        pass

    def max_lines_per_function(self):
        pass


def critic(code, **rules):
    return CodeAnalyzer(code).analyze()