# Solution graph
# Node: unknown/variable

# Dianmu Zhang Apr 2017

# Copyright 2017 University of Washington

# Developed by Dianmu Zhang and Blake Hannaford
# BioRobotics Lab, University of Washington

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import unittest
import sympy as sp
from ik_classes import *
import kin_cl as kc
from matching import *
import itertools as itt

((th_1, th_2, th_3, th_4, th_5, th_6)) = sp.symbols(('th_1', 'th_2', 'th_3', 'th_4', 'th_5', 'th_6'))
((d_1, d_2, d_3, d_4, d_5, d_6)) = sp.symbols(('d_1', 'd_2', 'd_3', 'd_4', 'd_5', 'd_6'))
((a_2, a_3)) = sp.symbols(('a_2', 'a_3'))

possible_unkns = set([th_1, th_2, th_3, th_4, th_5, th_6, d_1, d_2, d_3, d_4, d_5, d_6]) #didn't count th_XY

global notation_graph

def find_node(nodes, symbol): #equivlent function -> find_obj in helper
    for node in nodes:
        if node.symbol == symbol:
            return node

def goal_search(start, parent_notations, graph):
    '''modified BFS'''
    q = []
    q.append(start)
    
    while(len(q) > 0):
        curr = q[0]
        del q[0]
        if curr in parent_notations:
            return curr
        else:
            next_steps = find_edge(curr, graph)
            q.extend(next_steps)
            
    return None
        
def find_edge(child, graph):
    next_level = []
    for edge in graph:
        if edge.child == child:
            next_level.append(edge.parent)
            
    return next_level
    
def related(start_node, end_node):
    '''DFS: return True if a path exists, for Node types'''
    
    s = []
    s.append(start_node)
    
    #ancestors = set()
    
    while(len(s) > 0):
        curr = s[-1]
        del s[-1]
        
        if curr == end_node:
            return True
        else:
            next_steps = curr.parents
            s.extend(next_steps)
    return False


def back_track(curr_node):
    # find all ancestors of curr_node
    curr = curr_node
    ancestors_stack = []
    i = 0
    while (len(curr.parents) > 0):
        ancestors_stack.extend(curr.parents)
        curr = ancestors_stack[i]
        i += 1

    return ancestors_stack


def find_common_ancestor(node1, node2):
    #pass

    # this is only in effect when two nodes are not directly related
    # directly related: a path exists between those two
    common_ancestor = None
    if len(node1.parents) == 0:
        return node1
    elif len(node2.parents) == 0:
        return node2

    # closest ancestors are in the front, root at the end
    ancestors_stack1 = back_track(node1)
    ancestors_stack2 = back_track(node2)







    
class Node:
    '''Node is a temp class, will be integrate into unknown/variable, or inhirit from it'''
    def __init__(self, unk):
        self.symbol = unk.symbol
        self.argument = unk.argument
        self.solvemethod = unk.solvemethod
        self.eqnlist = []
        self.nsolutions = 0
        self.solutions = []
        self.assumption = []
        self.sol_notations = set() 
        self.parents = []
        self.solution_with_notations = {} # self.notation : kequation
        self.arguments = {}  # argument needing domain testing
        self.solveorder = -1 
        # upper level parent nodes
        self.upper_level_parents = []
    
    def __lt__(self, other):   # for sorting Nodes
        return self.solveorder < other.solveorder 
    
    def __eq__(self, other): #equal judgement, also hashing in python 3.x
        if other != None:
            return self.symbol == other.symbol
        return False
        
    def __hash__(self): #hash function "inherits" from symbol 
        return self.symbol.__hash__()
        
    def __repr__(self): # string representation
        return self.symbol.__repr__()
        
    def detect_parent(self, R):
        if not len(self.solutions) == 0:
            eqn = self.solutions[0] #solutions is a list of keqn
            print eqn
            elements = eqn.atoms(sp.Symbol) # get only symbol elements
            for elem in elements:
                if elem in R.variables_symbols: #swap possible_unkns to unknows symbols
                    parent = find_node(R.solution_nodes, elem)
                    self.parents.append(parent)
                     
            # detect redundancy and eliminate higher order parent
            if len(self.parents) > 1:
                self.upper_level_parents = set()
                for par in self.parents:
                    for other_par in self.parents:
                        if par != other_par and related(par, other_par):
                            # need to add the case that thxy and thx is related
                            # even if thxy and thx were seperatly solved
                            self.upper_level_parents.add(other_par)
                # convert to list
                self.upper_level_parents = list(self.upper_level_parents)
                for node in self.upper_level_parents:
                    self.parents.remove(node)
                

                    
    def generate_notation(self, R):
        #pass #TODO: generate individual notation
        #  bh change "footnote" to "subscript"
        #  bh: "notation" means indices eg:  th_2011
        #global notation_graph
        
        # TODO: debug the situation where parents are not related
        # but at different levels
        if len(self.parents) == 0: #root node special case
            if self.nsolutions < 2:
                self.sol_notations.add(self.symbol)
                R.notation_graph.add(Edge(self.symbol, -1))
                R.notation_collections.append([self.symbol])
                print '//////////////////////// 1 sol'
                print 'curr: ', self.symbol
                self.solution_with_notations[self.symbol] = kc.kequation(\
                        self.symbol, self.solutions[0])
                self.arguments[self.symbol] = self.argument
            else:
                for i in range(1, self.nsolutions + 1):
                    curr = str(self.symbol) + 's' + str(i) #convert to str, then to symbol?
                    curr = sp.var(curr)
                    self.sol_notations.add(curr)
                    R.notation_graph.add(Edge(curr, -1))
                    R.notation_collections.append([curr]) # add into subgroup

                    curr_solution = self.solutions[i-1]
                    self.solution_with_notations[curr] = kc.kequation(curr, curr_solution)
                    print '//////////////////////// > 1 sol'
                    print 'curr: ', curr
                    print self.argument
                    self.arguments[curr] = self.argument # simple because root
                    

        else:    # Non-root node
            # (find the deepest level of parents and) get product of parents
            # getting the product is safe here because we already
            # trimmed the infeasible pairs from last step (redundency detection)
            

            # parents_notation_list = []
            
            
            # if len(self.parents) == 1: 
            #     # convert to single symbol to list
            #     for one_sym in self.parents[0].sol_notations:
            #         parents_notation_list.append([one_sym])
            # elif len(self.parents) == 2:
            #     parents_notation_list = itt.product(self.parents[0].sol_notations, \
            #                             self.parents[1].sol_notations)
            # elif len(self.parents) == 3:
            #     parents_notation_list = itt.product(self.parents[0].sol_notations, \
            #                             self.parents[1].sol_notations, \
            #                             self.parents[2].sol_notations)
            # elif len(self.parents) == 4:
            #     parents_notation_list = itt.product(self.parents[0].sol_notations, \
            #                             self.parents[1].sol_notations, \
            #                             self.parents[2].sol_notations, \
            #                             self.parents[3].sol_notations)
            # elif len(self.parents) == 5:
            #     parents_notation_list = itt.product(self.parents[0].sol_notations, \
            #                             self.parents[1].sol_notations, \
            #                             self.parents[2].sol_notations, \
            #                             self.parents[3].sol_notations, \
            #                             self.parents[4].sol_notations)
            
            # need to write new parents notation list finding that works with common-ancestor



            isub = 1


            for parents_tuple in parents_notation_list:
                # find all parents notations, this is done outside of
                # the solution loop because multiple solutions share the same parents
                parents_notations = []
                # look for higher level parent notation connected to this parent
                for parent_sym in parents_tuple:
                    parents_notations.append(parent_sym)    
                    for higher_parent in self.upper_level_parents:
                        goal_notation = goal_search(parent_sym, \
                            higher_parent.sol_notations, R.notation_graph)
                        if goal_notation is not None:
                            parents_notations.append(goal_notation)

                for curr_solution in self.solutions:
                    # creat new symbols and link to graph
                    curr = str(self.symbol) + 's' + str(isub)
                    curr = sp.var(curr)
                    self.sol_notations.add(curr)
                                   

                    #R.notation_collections.append(curr)
                    isub = isub + 1
                    # link to graph
                    for parent_sym in parents_tuple:
                        R.notation_graph.add(Edge(curr, parent_sym))
                    # substitute for solutions
                    rhs = curr_solution

                    expr_notation_list= [curr]
                    for parent in (self.parents + self.upper_level_parents):
                        curr_parent = None

                        for parent_sym in parents_notations:
                            if parent_sym in parent.sol_notations:
                                curr_parent = parent_sym
                                expr_notation_list.append(curr_parent)
                        try:
                            rhs = rhs.subs(parent.symbol, curr_parent)
                            tmp_arg = self.argument.subs(parent.symbol, curr_parent) # also sub the arg
                        except:
                            print "problmematic step: ", parent.symbol
                            print "solution: ", rhs
                            print "parents notations"
                            print parents_notation_list

                    R.notation_collections.append(expr_notation_list)
                        #parents_notations.remove(curr_parent) 
                        # can't remove here, or won't be able to generate solution for
                        # multiple solution case

                    self.solution_with_notations[curr] = kc.kequation(curr, rhs)
                    self.arguments[curr] = tmp_arg   
                        

    def generate_solutions(self, R):
        '''generate solutions with notation(subscript)'''
        pass
       
            

class Edge:
    def __init__(self, child, parent):
        '''child and parent are notation with subscript type'''
        self.child = child
        self.parent = parent
        
    def __repr__(self):
        return "Edge from child: " + str(self.child) + " to parent: " + str(self.parent)
        
    def __eq__(self, other):
        return self.child == other.child and self.parent == other.parent
        
    def __hash__(self):
        return self.child.__hash__() * self.parent.__hash__() + self.child.__hash__()



class SolutionGraphV2Tests(unittest.TestCase):
    # the tests were designed for v1 (independent module), not suitable for v2
    def test_mock(self):
        print "place holder for real test: solution_graph_v2"

                            
if __name__ == '__main__':
    #notation_graph = set()
    #unittest.main() 
    
    print '\n\n===============  Test solution_graph_v2 ====================='
    #testsuite = unittest.TestLoader().loadTestsFromTestCase(SolutionGraphV2Tests)  # replace TEMPLATE 
    #unittest.TextTestRunner(verbosity=2).run(testsuite)
    unittest.main()
   
