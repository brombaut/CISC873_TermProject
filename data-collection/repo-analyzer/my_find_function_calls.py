import ast


class MyFindFunctionCalls(ast.NodeVisitor):

    def __init__(self):
        self.calls = list()
        self.parent_function_def = None

    def visit_FunctionDef(self, node):
        prev_function_def = self.parent_function_def
        print("FunctionDef: {}".format(node.name))
        self.parent_function_def = node
        self.generic_visit(node)
        self.parent_function_def = prev_function_def

    def visit_Call(self, node):
        call = dict()
        call['name'] = self.parse_call(node)
        print("Call: {}".format(call['name']))
        call['parent_function'] = None if not self.parent_function_def else self.parent_function_def.name
        self.calls.append(call)
        self.generic_visit(node)

    def parse_call(self, node):
        call_func = node.func
        if isinstance(call_func, ast.Name):
            value = None if call_func.id == "None" else call_func.id
            return value
        elif isinstance(call_func, ast.Attribute):
            value = self.parse_attribute(call_func)
            return value
        else:
            raise Exception("Unknown ParseCall Instance: {}".format(node.__class__.__name__))

    def parse_attribute(self, node):
        if isinstance(node.value, ast.Name):
            value = None if node.value.id == "None" else node.value.id
            return value + "." + node.attr
        elif isinstance(node.value, ast.Attribute):
            value = self.parse_attribute(node.value)
            return value + "." + node.attr
        else:
            raise Exception("Unknown ParseAttribute Instance: {}".format(node.__class__.__name__))
