import ast, math, operator
_BIN={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.FloorDiv:operator.floordiv,ast.Mod:operator.mod,ast.Pow:operator.pow}
_UNARY={ast.UAdd:operator.pos,ast.USub:operator.neg}
_FUNCS={"sqrt":math.sqrt,"sin":math.sin,"cos":math.cos,"tan":math.tan,"log":math.log,"log10":math.log10,"abs":abs,"round":round,"ceil":math.ceil,"floor":math.floor}

def _eval(node):
    if isinstance(node,ast.Expression): return _eval(node.body)
    if isinstance(node,ast.Constant) and isinstance(node.value,(int,float)) and not isinstance(node.value,bool): return node.value
    if isinstance(node,ast.BinOp) and type(node.op) in _BIN:
        left,right=_eval(node.left),_eval(node.right)
        if isinstance(node.op,ast.Pow) and abs(right)>10: raise ValueError("Exponent too large")
        return _BIN[type(node.op)](left,right)
    if isinstance(node,ast.UnaryOp) and type(node.op) in _UNARY: return _UNARY[type(node.op)](_eval(node.operand))
    if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in _FUNCS and not node.keywords:
        return _FUNCS[node.func.id](*[_eval(x) for x in node.args])
    raise ValueError("Only numeric arithmetic and approved math functions are allowed")

def calculate(expression: str):
    try:
        if not isinstance(expression,str) or len(expression)>200: raise ValueError("Expression must be a string under 200 characters")
        tree=ast.parse(expression,mode="eval")
        result=_eval(tree)
        if isinstance(result,float) and not math.isfinite(result): raise ValueError("Result is not finite")
        return {"status":"success","expression":expression,"result":result}
    except Exception as exc: return {"status":"failed","expression":expression,"error":str(exc)}
