#!/usr/bin/env python3

import graph


def get_clauses(G, k):
    """Append all clauses needed to find a correct solution for the graph coloring problem
     in the 'clauses' list.

    Minisat variables are represented with integers with index start by 1. As such you should use
    an integer index for variables in your model. The index of variables v_i_j in your model should
    be translated to Minisat model as follow: 
        index(v_i_j) = (i-1) * k + j such that i is the node index and j is color index.
    Note that node index and color index start from 1.
    Example: With k = 6. The index for variables 
        index(v_1_1) = (1-1) * 6 + 1 = 1
        index(v_5_4) = (5-1) * 6 + 4 = 28
    
    You could see more about Minisat utilisation in the file minisat.py
    
    """

    clauses = []
    # Put your code here!

    return clauses
