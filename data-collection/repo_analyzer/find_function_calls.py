import ast


class FindFunctionCalls(ast.NodeVisitor):

    def __init__(self):
        self.calls = list()

    def visit_Call(self, node):
        call = dict()
        call['name'] = parse_call(node)
        call['params'] = parse_params(node.args, node.keywords)
        self.calls.append(call)
        self.generic_visit(node)


def parse_arg(arg):
    if isinstance(arg, ast.Str):
        return parse_str(arg)
    elif isinstance(arg, ast.Name):
        return parse_name(arg)
    elif isinstance(arg, ast.NameConstant):
        return parse_name_constant(arg)
    elif isinstance(arg, ast.Num):
        return parse_num(arg)
    elif isinstance(arg, ast.List):
        return parse_list(arg)
    elif isinstance(arg, ast.Tuple):
        return tuple(parse_list(arg))
    elif isinstance(arg, ast.Attribute):
        return parse_attribute(arg)
    elif isinstance(arg, ast.Call):
        return parse_call(arg)
    elif isinstance(arg, ast.UnaryOp):
        return parse_unary_op(arg)
    # elif isinstance(arg, ast.BinOp):
    #     return parse_bin_op(arg)
    else:
        return ast.dump(arg)


def parse_str(n):
    return n.s


def parse_name(n):
    value = None if n.id == "None" else n.id
    return value


def parse_name_constant(n):
    return n.value


def parse_num(n):
    return n.n


def parse_list(n):
    arg_list = []
    for elt in n.elts:
        arg_list.append(parse_arg(elt))
    return arg_list


def parse_attribute(n):
    value = parse_arg(n.value)
    return value + "." + n.attr
    # return (str(arg.value.attr) + "." + str(arg.attr))


def parse_unary_op(n):
    if isinstance(n.op, ast.USub):
        return -1 * arg.operand.n
    return arg.operand.n


def parse_bin_op(n):
    return "{} {} {}".format(n.left.id, n.op, n.right.n)


def parse_call(n):
    call = n.func
    if isinstance(call, ast.Name):
        value = None if call.id == "None" else call.id
        return value
    elif isinstance(call, ast.Attribute):
        value = parse_attribute(call)
        return value
        # if isinstance(value, ast.BinOp):
        #     print(value.left.id, value.op, value.right.n)
        # return value + "." + call.attr
    else:
        return call


def parse_params(args, keywords):
    params = {}
    for arg_idx in range(len(args)):
        arg = args[arg_idx]
        params[arg_idx] = parse_arg(arg)
    for keyword in keywords:
        params[keyword.arg] = parse_arg(keyword.value)
    return params
