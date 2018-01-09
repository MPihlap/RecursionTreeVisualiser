import traceback
import sys
import anytree


def peegelda(element):
    if isinstance(element, tuple):
        return (peegelda(element[1]),peegelda(element[0]))
    return element

def rek(n, m):
    if n == 0:
        return 0
    return n + rek(n - 1, m)

def run_function(function, params: list):
    sys.settrace(trace_functions)
    function(*params)

def print_info(func_name, locals, co, frame):
    print("Function " + func_name + " was called.")
    print("Function " + func_name + " parameters: " + str(locals))
    print("Co varnames " + str(co.co_varnames))
    print("Co names " + str(co.co_names))
    print("Function was called by: "+str(frame.f_back.f_code.co_name))
    print()

def trace_functions(frame, event, arg):
    global depth
    global nodes
    co = frame.f_code
    locals = frame.f_locals
    func_name = co.co_name
    if func_name != observable_function: # Only trace the function we actually care about
        return
    if event == "call":
        print_info(func_name, locals, co, frame)
        depth += 1
        nodes += 1
        node_dict[nodes] = anytree.Node(nodes, parent=node_dict.get(depth - 1))
        return trace_functions
    elif event == "return":
        depth -= 1
        print("Function " + func_name + " returned " + str(arg))

node_dict = {}
depth = 0
nodes = 0
observable_function = "peegelda"
run_function(peegelda, [(("a","b"),("c","d"))])
print(anytree.RenderTree(node_dict.get(1)))
#print(peegelda(("a","b")))
#print(peegelda((("a","b"),("c","d"))))
