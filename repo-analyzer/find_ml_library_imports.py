import os
import ast


class FindMLLibraryImports:

    def __init__(self, file_name):
        self.imports_ml_libraries = False
        self._read_file_source(file_name)

    def _read_file_source(self, file_name):
        try:
            self.source = open(file_name, "r")
        except:
            raise SystemExit("The file doesn't exist or it isn't a Python script ...")

    def parse(self):
        tree = ast.parse(self.source.read())
        tree_body = tree.body
        for item in tree_body:
            if isinstance(item, ast.Import):
                if item.names[0].name == "keras":
                    self.imports_ml_libraries = True
                    return
                elif item.names[0].name == "tensorflow":
                    self.imports_ml_libraries = True
                    return
            if isinstance(item, ast.ImportFrom):
                if "keras" in item.module:
                    self.imports_ml_libraries = True
                    return
                elif "tensorflow" in item.module:
                    self.imports_ml_libraries = True
                    return
        self.imports_ml_libraries = False

    def file_imports_ml_libraries(self):
        return self.imports_ml_libraries
