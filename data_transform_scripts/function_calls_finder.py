import ast


class FunctionCallsFinder(ast.NodeVisitor):

    def __init__(self):
        self.calls = list()
        self.parent_function_def = None

    def visit_FunctionDef(self, node):
        prev_function_def = self.parent_function_def
        self.parent_function_def = node
        self.generic_visit(node)
        self.parent_function_def = prev_function_def

    def visit_Call(self, node):
        try:
            call = dict()
            call['name'] = self._parse_func(node.func)
            # call['params'] = self._parse_params(node.args, node.keywords)
            call['params'] = None
            call['parent_function'] = self._parent_func_name()
            self.calls.append(call)
            self.generic_visit(node)
        except Exception as e:
            print(e)

    def _parse_params(self, args, keywords):
        params = {}
        arg_idx = 0
        for arg in args:
            params[arg_idx] = self._parse_arg(arg)
            arg_idx += 1
        for keyword in keywords:
            params[keyword.arg] = self._parse_arg(keyword.value)
        return params

    def _parent_func_name(self):
        return None if not self.parent_function_def else self.parent_function_def.name

    def _parse_func(self, func):
        if isinstance(func, ast.Name):
            return self._parse_name(func)
        elif isinstance(func, ast.Attribute):
            return self._parse_attribute(func)
        elif isinstance(func, ast.Call):
            return self._parse_call(func)
        elif isinstance(func, ast.Subscript):
            return self._parse_subscript(func)
        else:
            # return "Unknown ParseCall Instance: {}".format(func.__class__.__name__)
            raise Exception("Unknown ParseCall Instance: {}".format(func.__class__.__name__))

    def _parse_args(self, args):
        result = list()
        arg_idx = 0
        for arg in args:
            s = self._parse_arg(arg)
            result.append(s)
        return result

    def _parse_keywords(self, keywords):
        result = list()
        for keyword in keywords:
            s = '{}={}'.format(keyword.arg, self._parse_arg(keyword.value))
            result.append(s)
        return result

    def _parse_arg(self, arg):
        if isinstance(arg, ast.Name):
            s = self._parse_name(arg)
        elif isinstance(arg, ast.Attribute):
            s = self._parse_attribute(arg)
        elif isinstance(arg, ast.Constant):
            s = self._parse_constant(arg)
        elif isinstance(arg, ast.Call):
            s = self._parse_call(arg)
        elif isinstance(arg, ast.Tuple):
            s = self._parse_tuple(arg)
        elif isinstance(arg, ast.List):
            s = self._parse_list(arg)
        elif isinstance(arg, ast.Subscript):
            s = self._parse_subscript(arg)
        else:
            s = "UNKNOWN_ARG_TYPE={}".format(arg.__class__.__name__)
        return s

    def _parse_attribute(self, n_attr):
        if isinstance(n_attr.value, ast.Name):
            return self._parse_name(n_attr.value) + "." + n_attr.attr
        elif isinstance(n_attr.value, ast.Attribute):
            return self._parse_attribute(n_attr.value) + "." + n_attr.attr
        elif isinstance(n_attr.value, ast.Call):
            return self._parse_call(n_attr.value)
        elif isinstance(n_attr.value, ast.Constant):
            return self._parse_constant(n_attr.value)
        elif isinstance(n_attr.value, ast.Subscript):
            return self._parse_subscript(n_attr.value)
        else:
            raise Exception("Unknown ParseAttribute Instance: {}".format(n_attr.value.__class__.__name__))

    def _parse_name(self, n_name):
        return None if n_name.id == "None" else n_name.id

    def _parse_constant(self, n_constant):
        if isinstance(n_constant, ast.Str):
            return self._parse_str(n_constant)
        elif isinstance(n_constant, ast.Num):
            return self._parse_num(n_constant)
        elif isinstance(n_constant, ast.Constant):
            return self._parse_constant(n_constant.value)
        elif isinstance(n_constant, ast.Name):
            return self._parse_name(n_constant)
        elif isinstance(n_constant, bool):
            return n_constant
        elif n_constant is None:
            return n_constant
        else:
            print("ParseConstant: Unknown n_constant={}".format(n_constant.__class__.__name__))
            print("{}".format(n_constant))
            return self._parse_arg(n_constant)
            # raise Exception("Unknown ParseConstant Instance: {}".format(n_constant.__class__.__name__))

    def _parse_str(self, n_str):
        return "'{}'".format(n_str.value)

    def _parse_num(self, n_num):
        return "{}".format(n_num.value)

    def _parse_call(self, n_call):
        func = self._parse_func(n_call.func)
        args = self._parse_args(n_call.args)
        keywords = self._parse_keywords(n_call.keywords)
        args.extend(keywords)
        return "{}({})".format(func, ','.join(args))

    def _parse_tuple(self, n_tuple):
        arg_list = self._parse_args(n_tuple.elts)
        return "({})".format(",".join(arg_list))

    def _parse_list(self, n_list):
        arg_list = self._parse_args(n_list.elts)
        return "[{}]".format(",".join(arg_list))

    def _parse_subscript(self, n_subscript):
        if isinstance(n_subscript.value, ast.Name):
            val = self._parse_name(n_subscript.value)
        elif isinstance(n_subscript.value, ast.Attribute):
            val = self._parse_attribute(n_subscript.value)
        else:
            print("ParseSubscript: Unknown n_subscript.value={}".format(n_subscript.value.__class__.__name__))
            val = n_subscript.value.__class__.__name__

        sub_slice = self._parse_slice(n_subscript.slice)
        return "{}[{}]".format(val, sub_slice)

    def _parse_slice(self, n_slice):
        if isinstance(n_slice, ast.Index):
            return self._parse_index(n_slice)
        elif isinstance(n_slice, ast.Slice):
            lower = self._parse_arg(n_slice.lower)
            upper = self._parse_arg(n_slice.upper)
            return "{}:{}".format(lower, upper)
        elif isinstance(n_slice, ast.Name):
            return self._parse_name(n_slice)
        elif isinstance(n_slice, ast.Constant):
            return self._parse_constant(n_slice)
        else:
            print("ParseSlice: Unknown n_slice={}".format(n_slice.__class__.__name__))
            return "UNKNOWN={}".format(n_slice.__class__.__name__)

    def _parse_index(self, n_index):
        if isinstance(n_index.value, ast.Constant):
            return self._parse_constant(n_index.value)
        elif isinstance(n_index.value, ast.Name):
            return self._parse_name(n_index.value)
        elif isinstance(n_index.value, ast.Attribute):
            return self._parse_attribute(n_index.value)
        else:
            print("ParseIndex: Unknown n_index.value={}".format(n_index.__class__.__name__))
            return n_index.value.__class__.__name__
