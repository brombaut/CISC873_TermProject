import unittest
from ..function_calls_collector import FunctionCallsCollector


class TestFunctionCallsCollector(unittest.TestCase):
    file = 'test_file.py'
    repo = 'brombaut/test'
    repo_version = '0.0.1'
    output_dir = './'
    file_path_in_repo = 'test_file.py'

    def test_find_simple_call(self):
        source = '''
func()
        '''
        collector = FunctionCallsCollector(self.file, self.repo, self.repo_version, source, self.output_dir, self.file_path_in_repo)
        collector.find_all()
        expected = [
            {
                "name": "func",
                "params": {},
                "parent_function": None,
                "file": self.file,
                "file_in_repo": self.file_path_in_repo,
                "repo": self.repo,
                "repo_version": self.repo_version
            }
        ]
        result = collector.function_calls
        self.assertCountEqual(expected, result)

    def test_find_call_with_params(self):
        source = '''
func_with_params(a, 4)
        '''
        collector = FunctionCallsCollector(self.file, self.repo, self.repo_version, source, self.output_dir, self.file_path_in_repo)
        collector.find_all()
        expected = [
            {
                "name": "func_with_params",
                "params": {0: 'a', 1: '4'},
                "parent_function": None,
                "file": self.file,
                "file_in_repo": self.file_path_in_repo,
                "repo": self.repo,
                "repo_version": self.repo_version
            }
        ]
        result = collector.function_calls
        self.assertCountEqual(expected, result)

    def test_find_call_with_parent(self):
        source = '''
def parent_func():       
    func_with_parent()
        '''
        collector = FunctionCallsCollector(self.file, self.repo, self.repo_version, source, self.output_dir, self.file_path_in_repo)
        collector.find_all()
        expected = [
            {
                "name": "func_with_parent",
                "params": {},
                "parent_function": "parent_func",
                "file": self.file,
                "file_in_repo": self.file_path_in_repo,
                "repo": self.repo,
                "repo_version": self.repo_version
            }
        ]
        result = collector.function_calls
        self.assertCountEqual(expected, result)

    def test_find_two_calls(self):
        source = '''
def tensor_shapes_match(a, b):
    return tf.shape(a).shape == tf.shape(b).shape
        '''
        collector = FunctionCallsCollector(self.file, self.repo, self.repo_version, source, self.output_dir, self.file_path_in_repo)
        collector.find_all()
        expected = [
            {
                "name": "tf.shape",
                "params": {0: 'a'},
                "parent_function": "tensor_shapes_match",
                "file": self.file,
                "file_in_repo": self.file_path_in_repo,
                "repo": self.repo,
                "repo_version": self.repo_version
            },
            {
                "name": "tf.shape",
                "params": {0: 'b'},
                "parent_function": "tensor_shapes_match",
                "file": self.file,
                "file_in_repo": self.file_path_in_repo,
                "repo": self.repo,
                "repo_version": self.repo_version
            }
        ]
        result = collector.function_calls
        self.assertCountEqual(expected, result)

    def test_find_call_with_attr_name(self):
        source = '''
func.attr()
def shape_as_list(t):
    return t.shape.as_list()
        '''
        collector = FunctionCallsCollector(self.file, self.repo, self.repo_version, source, self.output_dir, self.file_path_in_repo)
        collector.find_all()
        expected = [
            {
                "name": "func.attr",
                "params": {},
                "parent_function": None,
                "file": self.file,
                "file_in_repo": self.file_path_in_repo,
                "repo": self.repo,
                "repo_version": self.repo_version
            },
            {
                "name": "t.shape.as_list",
                "params": {},
                "parent_function": "shape_as_list",
                "file": self.file,
                "file_in_repo": self.file_path_in_repo,
                "repo": self.repo,
                "repo_version": self.repo_version
            }
        ]
        result = collector.function_calls
        self.assertCountEqual(expected, result)

    def test_find_call_from_param(self):
        source = '''
def func_1():       
    func_2(func_3())
        '''
        collector = FunctionCallsCollector(self.file, self.repo, self.repo_version, source, self.output_dir, self.file_path_in_repo)
        collector.find_all()
        expected = [
            {
                "name": "func_2",
                "params": {0: "func_3()"},
                "parent_function": "func_1",
                "file": self.file,
                "file_in_repo": self.file_path_in_repo,
                "repo": self.repo,
                "repo_version": self.repo_version
            },
            {
                "name": "func_3",
                "params": {},
                "parent_function": "func_1",
                "file": self.file,
                "file_in_repo": self.file_path_in_repo,
                "repo": self.repo,
                "repo_version": self.repo_version
            }
        ]
        result = collector.function_calls
        self.assertCountEqual(expected, result)

    def test_find_calls_with_call_params(self):
        source = '''
tf.reshape(tf.reduce_sum(tensor, axis=axis))
        '''
        collector = FunctionCallsCollector(self.file, self.repo, self.repo_version, source, self.output_dir, self.file_path_in_repo)
        collector.find_all()
        self.maxDiff = None
        expected = [
            {
                "name": "tf.reshape",
                "params": {0: "tf.reduce_sum(tensor,axis=axis)"},
                "parent_function": None,
                "file": self.file,
                "file_in_repo": self.file_path_in_repo,
                "repo": self.repo,
                "repo_version": self.repo_version
            },
            {
                "name": "tf.reduce_sum",
                "params": {0: "tensor", "axis": "axis"},
                "parent_function": None,
                "file": self.file,
                "file_in_repo": self.file_path_in_repo,
                "repo": self.repo,
                "repo_version": self.repo_version
            },
        ]
        result = collector.function_calls
        self.assertCountEqual(expected, result)

    def test_find_complicated_calls(self):
        source = '''
def unbroadcast_tfe_to(tensor, shape):
    axis = utils.create_unbroadcast_axis(shape, shape_as_list(tensor))
    return tf.reshape(tf.reduce_sum(tensor, axis=axis), shape)
        '''
        collector = FunctionCallsCollector(self.file, self.repo, self.repo_version, source, self.output_dir, self.file_path_in_repo)
        collector.find_all()
        self.maxDiff = None
        expected = [
            {
                "name": "utils.create_unbroadcast_axis",
                "params": {0: "shape", 1: "shape_as_list(tensor)"},
                "parent_function": "unbroadcast_tfe_to",
                "file": self.file,
                "file_in_repo": self.file_path_in_repo,
                "repo": self.repo,
                "repo_version": self.repo_version
            },
            {
                "name": "shape_as_list",
                "params": {0: "tensor"},
                "parent_function": "unbroadcast_tfe_to",
                "file": self.file,
                "file_in_repo": self.file_path_in_repo,
                "repo": self.repo,
                "repo_version": self.repo_version
            },
            {
                "name": "tf.reshape",
                "params": {0: "tf.reduce_sum(tensor,axis=axis)", 1: "shape"},
                "parent_function": "unbroadcast_tfe_to",
                "file": self.file,
                "file_in_repo": self.file_path_in_repo,
                "repo": self.repo,
                "repo_version": self.repo_version
            },
            {
                "name": "tf.reduce_sum",
                "params": {0: "tensor", "axis": "axis"},
                "parent_function": "unbroadcast_tfe_to",
                "file": self.file,
                "file_in_repo": self.file_path_in_repo,
                "repo": self.repo,
                "repo_version": self.repo_version
            },
        ]
        result = collector.function_calls
        self.assertCountEqual(expected, result)

    def test_different_call_params(self):
        source = '''
func(d[4], f['g'], (1, 2, 3), [4, 5, 6], 1 + 2)
        '''
        collector = FunctionCallsCollector(self.file, self.repo, self.repo_version, source, self.output_dir, self.file_path_in_repo)
        collector.find_all()
        self.maxDiff = None
        expected = [
            {
                "name": "func",
                "params": {0: "d[4]", 1: "f['g']", 2: '(1,2,3)', 3: "[4,5,6]", 4: 'UNKNOWN_ARG_TYPE=BinOp'},
                "parent_function": None,
                "file": self.file,
                "file_in_repo": self.file_path_in_repo,
                "repo": self.repo,
                "repo_version": self.repo_version
            },
        ]
        result = collector.function_calls
        self.assertCountEqual(expected, result)
