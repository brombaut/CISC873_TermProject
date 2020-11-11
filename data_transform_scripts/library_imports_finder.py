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
            try:
                if isinstance(item, ast.Import):
                    if item.names[0].name in self.ml_libraries:
                        self.imports_ml_libraries = True
                        return
                if isinstance(item, ast.ImportFrom):
                    if item.level > 0:
                        # Relative imports
                        continue
                    for ml_lib in self.ml_libraries:
                        if ml_lib in item.module:
                            self.imports_ml_libraries = True
                            return
            except Exception as e:
                print("Error on {}: {}".format(self.file_name, item, e))
                continue
        self.imports_ml_libraries = False

    def file_imports_libraries(self):
        return self.imports_ml_libraries
