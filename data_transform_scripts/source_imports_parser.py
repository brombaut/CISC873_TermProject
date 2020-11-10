import ast
import os
import json


class ImportsParser:
    def __init__(self, source, file, repo, version, output_dir, file_path_in_repo):
        self.source = source
        self.abs_file = file
        self.file_path_in_repo = file_path_in_repo
        self.file = os.path.basename(self.abs_file)
        self.repo = repo
        self.version = version
        self.output_dir = output_dir
        self.imports = list()

    def parse(self):
        tree = ast.parse(self.source)
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
            json.dump(self.as_json(), f)

    def as_json(self):
        result = dict()
        result['file'] = self.file
        result['file_in_repo'] = self.file_path_in_repo
        result['repo'] = self.repo
        result['repo_version'] = self.version
        result['imports'] = self.imports
        return result
