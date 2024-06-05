import parser 
import pandas as pd
import itertools
import numpy as np
import os 
import matplotlib.pyplot as plt
import seaborn as sns
from voting_rules import voting_rules as vr
import rcv_dimensionality
import statistics
import rcv_distribution


def is_consistent(ballot):
    if len(ballot) == 0 or len(ballot) == 1:
        return True
    x = 0 
    v = 0.25
    i = 1
    while (i < len(ballot)):
        if ballot[i] < ballot[i - 1]:
            x -= (v * min(abs(ballot[i] - ballot[0]), abs(ballot[i] - ballot[i - 1])))
        else:
            x += (v * min(abs(ballot[i] - ballot[0]), abs(ballot[i] - ballot[i - 1])))
        v *= 0.5
        i += 1
    l = []
    if abs(x) >= 0.5 or x == 0:
        return False 
    x += ballot[0]
    for c in ballot:
        l.append(abs(c - x))
    if(all(l[i] <= l[i + 1] for i in range(len(l) -  1))):
        return True 
    return False

def perform_brute_force_analysis(ballots, candidates):
    perms = list(itertools.permutations(candidates))
    #most consistant permutation
    mcp = None
    c_mcp = 0
    x = len(candidates)
    l = [i for i in range(1, x + 1)]
    
    for perm in perms:
        temp = {}
        i = 1
        for candidate in perm:
            temp[candidate] = i
            i += 1
        c = 0
        total = 0
        for b in ballots:
            if len(b) > 0:
                total += ballots[b]
                b_num = []
                for candidate in b:
                    b_num.append(temp[candidate])
                if (is_consistent(b_num)):
                    c += ballots[b]
            if mcp is None or c > c_mcp:
                c_mcp = c
                mcp = perm
    return (c_mcp/total), mcp