from scipy.optimize import linprog
import seaborn as sns

from scipy.stats import kurtosis, skew
import pandas as pd
from rcv_distribution import *
from voting_rules import *



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
        

    
def get_permissive_gamma(ballots, normalized_distances):
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
        

# from here we are going to implement the "strict" definition of consistency

def evaluate_ballot_consistency(ballot: list, n :int, normalized_distances) -> Tuple[bool, Optional[float]]:
    """
    Evaluates the consistency of a ballot.

    A ballot is consistent if it fulfills a certain condition defined in the code. 
    If the ballot is consistent, the function returns True and a certain value 'consistency_value'. 
    If the ballot is not consistent, the function returns False and 'consistency_value'. 
    If the ballot is empty, the function returns True and None.

    Parameters
    ----------
    ballot : list
        A list of numbers representing a ballot.

    Returns
    -------
    tuple
        A tuple containing a boolean that indicates whether the ballot is consistent or not, 
        and a number 'consistency_value' which is calculated based on the ballot.
    """

    if len(ballot) == 0: 
        return (True, None) 
    if len(ballot) == 1:
        return (True, ballot[0]) 

    '''consistency_value = 0 
    adjustment_factor = 0.25
    ballot_index = 1
    while (ballot_index < len(ballot)):
        if ballot[ballot_index] < ballot[ballot_index - 1]:
            consistency_value -= (adjustment_factor * min(abs(ballot[ballot_index] - ballot[0]), abs(ballot[ballot_index] - ballot[ballot_index - 1])))
        else:
            consistency_value += (adjustment_factor * min(abs(ballot[ballot_index] - ballot[0]), abs(ballot[ballot_index] - ballot[ballot_index - 1])))
        adjustment_factor *= 0.5
        ballot_index += 1

    distance_list = []
    if abs(consistency_value) >= 0.5 or consistency_value == 0:
        return (False, consistency_value + ballot[0]) '''

    distance_list = []
    if (ballot[1] > ballot[0]):
        consistency_value = ballot[0] + 0.25*(ballot[1] - ballot[0])
    else:
        consistency_value = ballot[0] - 0.25*(ballot[0] - ballot[1])
    if len(ballot) < n:
        not_included = []
        for candidate in normalized_distances:
            i = normalized_distances[candidate]
            """if i not in ballot and i > min(ballot) and i < max(ballot):
                not_included.append((abs(i - consistency_value), i))
        not_included = sorted(not_included)
        for c in not_included:
            ballot.append(c[1])"""
            if i not in ballot and i > min(ballot) and i < max(ballot):
                return False, None

            
    for candidate in ballot:
        distance_list.append(abs(candidate - consistency_value))
    for i in range(len(distance_list) - 1):
        if distance_list[i] > distance_list[i + 1]:
            return (False, None)
    return (True, consistency_value)

    '''if(all(distance_list[i] <= distance_list[i + 1] for i in range(len(distance_list) -  1))):
        return (True, consistency_value)

    return (False, consistency_value)'''

def get_strict_gamma(ballots, normalized_distances):
    
    candidates = list(normalized_distances.keys())
    total = 0
    consistent = 0
    for ballot in ballots:
        if len(ballot) > 0:
            total += ballots[ballot]
        ballot_num = []
        for c in ballot:
            ballot_num.append(normalized_distances[c])
        if evaluate_ballot_consistency(ballot_num, len(candidates), normalized_distances)[0] is True:
            consistent += ballots[ballot]
    
    return consistent/total

    