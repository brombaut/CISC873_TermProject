import unittest
from library_imports_finder import LibraryImportsFinder
from source_imports_parser import ImportsParser


class TestLibraryImportsFinder(unittest.TestCase):
    file = 'test_file.py'
    libraries = [
        'tensorflow',
        'torch'
    ]

    def test_library_is_imported(self):
        source = '''
import x
import y
import tensorflow as tf
        '''
        finder = LibraryImportsFinder(source, self.file, self.libraries)
        finder.parse()
        self.assertTrue(finder.file_imports_libraries())

    def test_library_is_not_imported(self):
        source = '''
import x
import y
        '''
        finder = LibraryImportsFinder(source, self.file, self.libraries)
        finder.parse()
        self.assertFalse(finder.file_imports_libraries())


class TestFileImportsParser(unittest.TestCase):
    file = 'test_file.py'
    repo = 'brombaut/test'
    version = '0.0.0'
    output_dir = './'
    file_path_in_repo = 'test_file.py'

    def test_bare_import_statement(self):
        source = '''
import x
import y
        '''
        parser = ImportsParser(source, self.file, self.repo, self.version, self.output_dir, self.file_path_in_repo)
        parser.parse()

        expected = {
            'file': 'test_file.py',
            'file_in_repo': 'test_file.py',
            'repo': 'brombaut/test',
            'repo_version': '0.0.0',
            'imports': [
                {'name': 'x', 'asname': None, 'module': None},
                {'name': 'y', 'asname': None, 'module': None}
            ]
        }
        result = parser.as_json()
        self.assertDictEqual(expected, result)

    def test_import_as_statement(self):
        source = '''
import x
import tensorflow as tf
        '''
        parser = ImportsParser(source, self.file, self.repo, self.version, self.output_dir, self.file_path_in_repo)
        parser.parse()

        expected = {
            'file': 'test_file.py',
            'file_in_repo': 'test_file.py',
            'repo': 'brombaut/test',
            'repo_version': '0.0.0',
            'imports': [
                {'name': 'x', 'asname': None, 'module': None},
                {'name': 'tensorflow', 'asname': 'tf', 'module': None}
            ]
        }
        result = parser.as_json()
        self.assertDictEqual(expected, result)

    def test_import_from_module_statement(self):
        source = '''
import x
from tensorflow.python.ops import resource_variable_ops
        '''
        parser = ImportsParser(source, self.file, self.repo, self.version, self.output_dir, self.file_path_in_repo)
        parser.parse()

        expected = {
            'file': 'test_file.py',
            'file_in_repo': 'test_file.py',
            'repo': 'brombaut/test',
            'repo_version': '0.0.0',
            'imports': [
                {'name': 'x', 'asname': None, 'module': None},
                {'name': 'resource_variable_ops', 'asname': None, 'module': 'tensorflow.python.ops'}
            ]
        }
        result = parser.as_json()
        self.assertDictEqual(expected, result)

    def test_import_combinations(self):
        source = '''
import x
from tensorflow.python.ops import resource_variable_ops as rf
        '''
        parser = ImportsParser(source, self.file, self.repo, self.version, self.output_dir, self.file_path_in_repo)
        parser.parse()

        expected = {
            'file': 'test_file.py',
            'file_in_repo': 'test_file.py',
            'repo': 'brombaut/test',
            'repo_version': '0.0.0',
            'imports': [
                {'name': 'x', 'asname': None, 'module': None},
                {'name': 'resource_variable_ops', 'asname': 'rf', 'module': 'tensorflow.python.ops'}
            ]
        }
        result = parser.as_json()
        self.assertDictEqual(expected, result)


if __name__ == "__main__":
    unittest.main()
