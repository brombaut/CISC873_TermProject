import ast
import os
import json
from pprint import pprint
from find_function_calls import FindFunctionCalls


class FileFunctionCallsParser():
    def __init__(self, file, repo):
        self.abs_file = file
        self.file = os.path.basename(self.abs_file)
        self.repo = repo
        self.ffc = FindFunctionCalls()
        self.function_calls = list()

    def find_all(self):
        with open(self.abs_file, "r") as source:
            source_code = [line for line in source.readlines()]
        with open(self.abs_file, "r") as source:
            tree = ast.parse(source.read())
        self.ffc.visit(tree)
        self.function_calls = list()
        for call in self.ffc.calls:
            self.function_calls.append(self.add_file_data(call))
        pprint(self.function_calls)

    def export_to_json(self):
        with open('./data/calls@{}@{}.json'.format(self.repo.replace('/', '@'), self.file), 'w') as f:
            json.dump(self.function_calls, f)

    def add_file_data(self, call):
        call['abs_file_path'] = self.abs_file
        call['file_name'] = self.file
        call['repo'] = self.repo
        return call
