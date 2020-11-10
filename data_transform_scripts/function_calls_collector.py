import ast
import os
import json
from .function_calls_finder import FunctionCallsFinder


class FunctionCallsCollector:
    def __init__(self, file, repo, source):
        self.abs_file = file
        self.file = os.path.basename(self.abs_file)
        self.repo = repo
        self.source = source
        self.fcf = FunctionCallsFinder()
        self.function_calls = list()

    def find_all(self):
        tree = ast.parse(self.source)
        self.fcf.visit(tree)
        self.function_calls = list()
        for call in self.fcf.calls:
            self.function_calls.append(self._add_file_data(call))

    def export_to_json(self):
        with open('../data/calls@{}@{}.json'.format(self.repo.replace('/', '@'), self.file), 'w') as f:
            json.dump(self.function_calls, f)

    def _add_file_data(self, call):
        call['abs_file_path'] = self.abs_file
        call['file_name'] = self.file
        call['repo'] = self.repo
        return call
