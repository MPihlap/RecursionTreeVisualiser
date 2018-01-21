# RecursionTreeVisualiser
# A tool to visualize the steps of recursive functions
# Author - Meelis Pihlap

import sys
import anytree
from typing import Callable


class function_info:

    # Class for keeping the relevant information about a single function call
    def __init__(self, func_name: str, node: anytree.Node, parent_function):
        self.func_name = func_name
        self.func_args = {}
        self.return_value = None
        self.local_variables = {}
        self.node = node
        self.parent_function = parent_function
        self.has_returned = False

    def print_on_call(self):
        # Function to print the on-call info of a function
        print("Function " + self.func_name + " was called.")
        print("Function " + self.func_name + " parameters: " + str(self.func_args))
        if self.parent_function != None:
            print("Function parent node: " + str(self.parent_function.node))
        print()

    def print_on_return(self):
        # Function to print the on-return info of a function
        print("Function " + self.func_name + " local variables before returning: " + str(self.local_variables))
        print("Function " + self.func_name + " returned " + str(self.return_value))


class recursion_tree_visualizer:
    # Class to trace and print tree of recursive function
    # Usage:
    # Let foo(bar, car) be a recursive function
    # Then to print the recursion tree simply create object like so:
    # recursion_tree_visualizer(foo, [1, 2]) where [1, 2] are the function arguments

    def __init__(self, observable_function: Callable, args: list = None, ignore_list: list = None):
        # Constructor
        # Parameters:
        #   observable_function - function variable of function we want to observe
        #   args - arguments to be passed to the function
        #   ignore_list - str list of function names to be ignored

        self.nodes_amount = 0  # Tracks how many nodes we have
        self.parent_function = None  # The parent function of the current observed function
        self.func_info_dict = {}  # Dictionary for keeping function_info objects. key = name of the anytree node stored inside
        self.observed_function_name = observable_function.__name__
        self.function_args = args
        self.parent_function = None
        self.return_order = [] # LIFO list to track the order in which the functions return
        # Names of functions to be ignored while tracking
        # Can be added to using parameter ignore_list
        self.naughty_list = ["__init__", "run_function"]
        if ignore_list != None:
            for i in ignore_list:
                if not isinstance(i, str):
                    raise TypeError("Please pass ignorable function names as strings")
                self.naughty_list.append(i)


        self.run_function(observable_function, args)

    def run_function(self, function, params: list):
        # Runs a function and sets the trace
        print("Running function: " + function.__name__)
        sys.settrace(self.trace_functions)
        if params != None:
            function(*params)
        else:
            function()

    def trace_functions(self, frame, event, arg):
        # Trace function, analyses each event to see if it relates to a function we are tracking
        co = frame.f_code
        locals = frame.f_locals
        func_name = co.co_name

        # Checks if function is built-in or a part of the visualizer, if so, it is ignored
        if frame.f_builtins.get(func_name) != None or func_name in self.naughty_list:
            return
        if event == "call":
            self.nodes_amount += 1
            if self.parent_function == None:  # If first call of function, create root node
                self.func_info_dict[self.nodes_amount] = function_info(func_name, anytree.Node(self.nodes_amount), None)
            else:   # Create node with parent
                self.func_info_dict[self.nodes_amount] = \
                    function_info(func_name, anytree.Node(self.nodes_amount, parent=self.parent_function.node),
                                  self.parent_function)
            current_info = self.func_info_dict.get(self.nodes_amount)
            self.return_order.append(current_info) # on call, add node to LIFO queue to track returns
            current_info.func_args = locals # Set local variables
            self.parent_function = current_info  # set new parent function
            #self.func_info_dict.get(self.nodes_amount).print_on_call()
            self.print_tree()
            return self.trace_functions
        elif event == "return":
            func_info = self.return_order.pop() # Get next function to return from LIFO list
            func_info.return_value = arg
            func_info.has_returned = True
            func_info.local_variables = locals
            self.parent_function = self.parent_function.parent_function
            #self.func_info_dict.get(self.nodes_amount).print_on_return()
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

def a(n): # For testing multiple functions
    if n < 1:
        return
    b(n-1)

def b(n):
    a(n-1)

strange_counter = 0
def strange_rek(): # For testing 0 parameter function
    global strange_counter
    if strange_counter == 5:
        return
    strange_counter += 1
    strange_rek()

def input_rek(): # For testing unpredictable function
    a = input()
    if a == "":
        return
    input_rek()

# Test runs
recursion_tree_visualizer(peegelda, [(("a", "b"), ("c", "d"))])
recursion_tree_visualizer(rek, [5, 6])
recursion_tree_visualizer(a, [5], ignore_list=["b"])
recursion_tree_visualizer(strange_rek)
# TODO: Find a way to get rid of 'getstate' and 'decode' functions automatically...
recursion_tree_visualizer(input_rek, ignore_list=["getstate","decode"])
