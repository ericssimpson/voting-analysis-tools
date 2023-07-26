import parser 
import pandas as pd
import itertools
import numpy as np
import os 
import matplotlib.pyplot as plt
import seaborn as sns
from voting_rules import voting_rules as vr
import rcv_dimensionality
from sklearn.linear_model import LinearRegression

def is_consistent(ballot):
    if len(ballot) == 0: 
        return (True, None) 
    if len(ballot) == 1:
        return (True, ballot[0]) 
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
    if abs(x) >= (ballot[1] - ballot[0])/2 or x == 0:
        return (False, x + ballot[0]) 
    x += ballot[0]
    for c in ballot:
        l.append(abs(c - x))
    if(all(l[i] <= l[i + 1] for i in range(len(l) -  1))):
        return (True, x)
    return (False, x)


def points(filename, mcp, mcp_num):

    ballots, candidates = parser.parser(filename)
    election = vr(ballots, candidates)
    print (election.irv())
    #plotting based on consistency based on the distances of the candiates
    points = {}
    temp = {}
    for i in range(len(mcp)):
        temp[mcp[i]] = mcp_num[i]
    
    for b in ballots:
        b_num = []
        for c in b:
            b_num.append(temp[c])
        
        t = is_consistent(b_num)
        if t[0] is True and t[1] is not None:
            x = t[1] 
            if x not in points:
                points[x] = 0
            points[x] += ballots[b]
    return points


def get_points(file):
    
    d = rcv_dimensionality.perform_rcv_and_normalize(file)
    mcp = []
    mcp_num = []
    for k in d:
        mcp.append(k)
        mcp_num.append(d[k])
    
    return points(file, mcp, mcp_num)