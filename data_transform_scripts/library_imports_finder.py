import ast


class LibraryImportsFinder:

    def __init__(self, source, file_name, libraries):
        self.source = source
        self.file_name = file_name
        self.imports_ml_libraries = False
        self.ml_libraries = libraries

    def parse(self):
        tree = ast.parse(self.source)
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

    def file_imports_libraries(self):
        return self.imports_ml_libraries
