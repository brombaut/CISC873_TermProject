import os
import ast


class FindMLLibraryImports:

    def __init__(self, file_name, ml_libs):
        self.file_name = file_name
        self.imports_ml_libraries = False
        self.ml_libraries = ml_libs

    def parse(self):
        try:
            source = open(self.file_name, "r")
        except:
            raise SystemExit("The file doesn't exist or it isn't a Python script ...")
        tree = ast.parse(source.read())
        tree_body = tree.body
        for item in tree_body:
            if isinstance(item, ast.Import):
                if item.names[0].name in self.ml_libraries:
                    self.imports_ml_libraries = True
                    return
            if isinstance(item, ast.ImportFrom):
                for ml_lib in self.ml_libraries:
                    if ml_lib in item.module:
                        self.imports_ml_libraries = True
                        return
        self.imports_ml_libraries = False

    def file_imports_ml_libraries(self):
        return self.imports_ml_libraries
