from scipy.optimize import linprog
import seaborn as sns

from scipy.stats import kurtosis, skew
import pandas as pd
from rcv_distribution import *
from rcv_dimensionality import *
from voting_rules import *
import os


def calculate_intervals(numbers):
    midpoints = []
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            midpoints.append((numbers[i] + numbers[j])/2)

    intervals = []
    midpoints = sorted(midpoints)
    for i in range(len(midpoints)):
        for j in range(i + 1, len(midpoints)):
            intervals.append((midpoints[i], midpoints[j]))
    return midpoints, intervals

def ballot_to_num(ballot, normalized_distances):
    b_num = []
    for c in ballot:
        b_num.append(normalized_distances[c])
    return b_num

def solve_lp(b_num, midpoints, intervals, n):
    
    obj = [1]
    lhs_ineq = []
    rhs_ineq = []
    e = 0.000000001
    for i in range(len(b_num)):
        for j in range(i + 1, len(b_num)):
            mid = (b_num[i]+b_num[j])/2
            if (b_num[i] > b_num[j]):
                lhs_ineq.append([-1])
                rhs_ineq.append(-(e+mid))
            if (b_num[i] < b_num[j]):
                lhs_ineq.append([1])
                rhs_ineq.append(e+mid)
    bnd = [0, n-1]
    opt = linprog(c=obj, A_ub=lhs_ineq, b_ub=rhs_ineq, bounds=bnd,
              method="revised simplex")
    return (opt["success"] is True)
        

    
def get_interval_consistent_ballots(ballots, normalized_distances):
    """
    Args:
        ballots: a dictionary of ballots paired with the number of voters voting fo that ranking.
        normalized_distances: 
    Return:
        consistent_ballots: a dictionary of all consistent ballots.
        gamma: the fraction of the consistent ballots.
        
    """
    midpoints, intervals = calculate_intervals(list(normalized_distances.values()))

    total = 0
    consistent = 0
    consistent_ballots = {}
    for b in ballots:
        if (len(b) != 0):
            total += ballots[b]
            if (len(b) <= 2):
                consistent += ballots[b]
                consistent_ballots[b] = ballots[b]
            else:
                b_num = ballot_to_num(b, normalized_distances)
                lp = solve_lp(b_num, midpoints, intervals, len(normalized_distances))
                if (lp):
                    consistent_ballots[b] = ballots[b]
                    consistent += ballots[b]
    
    gamma = consistent/total
    return consistent_ballots, gamma
