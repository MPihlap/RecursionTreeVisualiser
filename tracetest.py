import sys
import anytree
from typing import Callable


class function_info:
    def __init__(self, func_name: str, node: anytree.Node, parent_function):
        self.func_name = func_name
        self.func_args = {}
        self.return_value = None
        self.local_variables = {}
        self.node = node
        self.parent_function = parent_function
        self.has_returned = False

    def print_on_call(self):
        print("Function " + self.func_name + " was called.")
        print("Function " + self.func_name + " parameters: " + str(self.func_args))
        if self.parent_function != None:
            print("Function parent node: " + str(self.parent_function.node))
        print()

    def print_on_return(self):
        print("Function " + self.func_name + " local variables before returning: " + str(self.local_variables))
        print("Function " + self.func_name + " returned " + str(self.return_value))


class recursion_tree_visualizer:
    def __init__(self, observable_function: Callable, args: list = []):
        self.nodes_amount = 0  # Tracks how many nodes we have
        self.parent_function = None  # The parent function of the current observed function
        self.func_info_dict = {}  # Dictionary for keeping function_info objects. key = name of the anytree node stored inside
        self.observed_function_name = observable_function.__name__
        self.function_parameters = args
        self.parent_function = None
        self.return_order = []

        self.run_function(observable_function, args)

    def run_function(self, function, params: list):
        sys.settrace(self.trace_functions)
        function(*params)

    def trace_functions(self, frame, event, arg):
        co = frame.f_code
        locals = frame.f_locals
        func_name = co.co_name

        if func_name != self.observed_function_name:  # Only trace the function we actually care about
            return
        if event == "call":
            self.nodes_amount += 1
            if self.parent_function == None:  # If first call of function, create root node
                self.func_info_dict[self.nodes_amount] = function_info(func_name, anytree.Node(self.nodes_amount), None)
            else:
                self.func_info_dict[self.nodes_amount] = \
                    function_info(func_name, anytree.Node(self.nodes_amount, parent=self.parent_function.node),
                                  self.parent_function)
            self.return_order.append(self.func_info_dict.get(self.nodes_amount))
            self.func_info_dict.get(self.nodes_amount).func_args = locals
            self.parent_function = self.func_info_dict.get(self.nodes_amount)  # set new parent function
            self.print_tree()
            return self.trace_functions
        elif event == "return":
            func_info = self.return_order.pop()
            func_info.return_value = arg
            func_info.has_returned = True
            func_info.local_variables = locals
            self.parent_function = self.parent_function.parent_function
            self.print_tree()

    def print_tree(self):
        for pre, _, node in anytree.RenderTree(self.func_info_dict.get(1).node):
            func_info = self.func_info_dict.get(node.name)
            if func_info.has_returned:
                print("%s%s" % (pre, "<-- " + str(func_info.return_value) + " " + func_info.func_name +
                                str(func_info.func_args)))
            else:
                print("%s%s" % (pre, func_info.func_name + str(func_info.func_args)))
        print()


def peegelda(element):
    if isinstance(element, tuple):
        return (peegelda(element[1]), peegelda(element[0]))
    return element


def rek(n, m):
    if n == 0:
        return 0
    return n + rek(n - 1, m)


recursion_tree_visualizer(peegelda, [(("a", "b"), ("c", "d"))])
recursion_tree_visualizer(rek, [5, 6])
