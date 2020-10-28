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
        call['name'] = self._parse_call(node)
        print("Call: {}".format(call['name']))
        call['parent_function'] = None if not self.parent_function_def else self.parent_function_def.name
        self.calls.append(call)
        self.generic_visit(node)

    def _parse_call(self, node):
        call_func = node.func
        if isinstance(call_func, ast.Name):
            return self._parse_name(call_func)
        elif isinstance(call_func, ast.Attribute):
            return self._parse_attribute(call_func)
        else:
            raise Exception("Unknown ParseCall Instance: {}".format(node.__class__.__name__))

    def _parse_attribute(self, node):
        if isinstance(node.value, ast.Name):
            return self._parse_name(node.value) + "." + node.attr
        elif isinstance(node.value, ast.Attribute):
            return self._parse_attribute(node.value) + "." + node.attr
        else:
            raise Exception("Unknown ParseAttribute Instance: {}".format(node.__class__.__name__))

    def _parse_name(self, node):
        return None if node.id == "None" else node.id
