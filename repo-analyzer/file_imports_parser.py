import ast
import os
import json
from pprint import pprint


class FileImportsParser():
    def __init__(self, file, repo, version, output_dir):
        self.abs_file = file
        self.file = os.path.basename(self.abs_file)
        self.repo = repo
        self.version = version
        self.output_dir = output_dir
        self.imports = list()

    def parse(self):
        try:
            source = open(self.abs_file, "r")
        except:
            raise SystemExit("The file doesn't exist or it isn't a Python script ...")
        tree = ast.parse(source.read())
        tree_body = tree.body
        for item in tree_body:
            if isinstance(item, ast.Import):
                for i in item.names:
                    new_import = dict()
                    new_import['name'] = i.name
                    new_import['asname'] = i.asname
                    new_import['module'] = None
                    self.imports.append(new_import)
            if isinstance(item, ast.ImportFrom):
                for i in item.names:
                    new_from_import = dict()
                    new_from_import['name'] = i.name
                    new_from_import['asname'] = i.asname
                    new_from_import['module'] = item.module
                    self.imports.append(new_from_import)

    def write_to_json(self):
        output_file = "{}imports/imports@{}@{}@{}.json".format(self.output_dir, self.repo.replace('/', '$'), self.version, self.file)
        with open(output_file, 'w') as f:
            json.dump(self._build_file_output(), f)

    def _build_file_output(self):
        result = dict()
        result['file'] = self.file
        result['repo'] = self.repo
        result['repo_version'] = self.version
        result['imports'] = self.imports
        return result
