import re
from typing import Dict, List, Optional, Tuple

import pandas as pd
import matplotlib.pyplot as plt

from rcv_dimensionality import perform_rcv_and_normalize


def evaluate_ballot_consistency(ballot: list, n :int) -> Tuple[bool, Optional[float]]:
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
        consistency_value = ballot[0] + 0.25
    else:
        consistency_value = ballot[0] - 0.25
    if len(ballot) < n:
        not_included = []
        for i in range(n):
            if i not in ballot and i > min(ballot) and i < max(ballot):
                not_included.append((abs(i - consistency_value), i))
        not_included = sorted(not_included)
        for c in not_included:
            ballot.append(c[1])

            
    for candidate in ballot:
        distance_list.append(abs(candidate - consistency_value))
    for i in range(len(distance_list) - 1):
        if distance_list[i] > distance_list[i + 1]:
            return (False, consistency_value)
    return (True, consistency_value)

    '''if(all(distance_list[i] <= distance_list[i + 1] for i in range(len(distance_list) -  1))):
        return (True, consistency_value)

    return (False, consistency_value)'''


def parse_election_data(filename: str, ignore_values: Optional[List[str]] = None) -> Tuple[Dict[Tuple[str, ...], int], List[str]]:
    """
    Parses a CSV file with election data.

    Parameters
    ----------
    filename : str
        The name of the file with election data.
    ignore_values : list, optional
        A list of values to ignore when reading the CSV file. Defaults to common non-candidate values.

    Returns
    -------
    tuple
        A tuple containing a dictionary that maps each ballot (a tuple of candidate names) to a corresponding count, 
        and a list of all the candidates.
    """

    # Default values to ignore when reading CSV
    if ignore_values is None:
        ignore_values = ['UWI', '(WRITE-IN)', 'WRITE-IN', 'writein', 'Write-In', 'Write-in', 'skipped', 'overvote', 'Undeclared', 'undervote', 'Write in']

    data = pd.read_csv(filename, low_memory=False)

    # Replace non-candidate values with None
    for ignore_value in ignore_values:
        data.replace(to_replace=re.compile(ignore_value), value=None, regex=True, inplace=True)

    # Initialize list of candidates and dictionary of ballots
    candidates = []
    ballots = {}

    # For each row in the data
    for i in range(len(data)):
        # Initialize an empty tuple for the ranking
        ranking = ()

        # Iterate over each rank
        j = 1
        while True:
            try:
                candidate = data.at[i, f"rank{j}"]

                # Add candidate to ranking if it's not None
                if candidate is not None:
                    if candidate not in ranking:
                        ranking += (candidate,)
                    if candidate not in candidates:
                        candidates.append(candidate)

                j += 1
            except KeyError:  # No more ranks
                break

        # Add ranking to ballots or increment count if it already exists
        if ranking not in ballots:
            ballots[ranking] = 0
        ballots[ranking] += 1

    return ballots, candidates


def calculate_ballot_consistency(filename: str, most_consistent_permutation: list, permutation_numbers: list) -> Dict[float, int]:
    """
    Reads a file with election data, converts the ballots from using candidate names to using corresponding numbers,
    checks the consistency of each ballot with respect to the most consistent permutation of candidates,
    and collects points based on this consistency.

    Parameters
    ----------
    filename : str
        The name of the file with election data.
    most_consistent_permutation : list
        A list of candidates in their most consistent permutation.
    permutation_numbers : list
        A list of numbers. Each number corresponds to a candidate in the 'most_consistent_permutation' list.

    Returns
    -------
    dict
        A dictionary that maps each point (representing a consistency value) to a corresponding count.
    """

    ballots, candidates = parse_election_data(filename)

    # Create a dictionary that maps each candidate to a corresponding number
    candidate_to_number_map = {candidate: number for candidate, number in zip(most_consistent_permutation, permutation_numbers)}

    # Convert the ballots from using candidate names to using corresponding numbers
    ballot_counts = {tuple(candidate_to_number_map[candidate] for candidate in ballot): count for ballot, count in ballots.items()}

    points = {}
    for ballot, count in ballot_counts.items():
        consistency_check = evaluate_ballot_consistency(ballot)
        if consistency_check[0] is True and consistency_check[1] is not None:
            consistency_value = consistency_check[1]
            if consistency_value not in points:
                points[consistency_value] = 0
            points[consistency_value] += count

    return points


def get_consistency_points(ballots, candidates, normalized_distances: dict) -> Dict[float, int]:
    """
    Performs RCV analysis and normalizes the distances of MDS-1D coordinates,
    then calculates the consistency of each ballot and collects points based on this consistency.

    Parameters
    ----------
    file : str
        The name of the file with election data.

    Returns
    -------
    tuple
        A tuple containing a dictionary that maps each point (representing a consistency value) to a corresponding count,
        a list of candidates in their most consistent permutation, and a list of mds-1d coordinates.
    """

    most_consistent_permutation = []
    permutation_numbers = []
    for candidate in normalized_distances:
        most_consistent_permutation.append(candidate)
        permutation_numbers.append(normalized_distances[candidate])
    
    points = {}

    equal = {}
    for i in range(len(most_consistent_permutation)):
        equal[most_consistent_permutation[i]] = i

    for ballot in ballots:
        equal_distances = []
        for candidate in ballot:
            equal_distances.append(equal[candidate])

        mds_distances = []
        for candidate in ballot:
            mds_distances.append(normalized_distances[candidate])

        #checking if the ballot is consistent with the mds permutation but assuming they are equaly distances 
        check_consistency = evaluate_ballot_consistency(equal_distances)
        if check_consistency[0] is True:

            #here we know that it is consistent assuming equal distances, and we get the point on the axis with respect
            #to mds distances 
            point = evaluate_ballot_consistency(mds_distances)[1]
            if point is not None:
                '''if len(ballot) > 1:
                    #if the point falls closer to the second choice, we push it back 
                    point = min(point, ((mds_distances[0] + mds_distances[1])/2 - ((mds_distances[0] + mds_distances[1])/(len(candidates) + 1))))'''
                if point not in points:
                    points[point] = 0
                points[point] += ballots[ballot]
    
    return points

def calculate_gamma(file, normalized_distances):

    ballots, candidates = parse_election_data(file)
    most_consistent_permutation = []
    permutation_numbers = []
    for candidate in normalized_distances:
        most_consistent_permutation.append(candidate)
        permutation_numbers.append(normalized_distances[candidate])

    candidate_to_number_map = {candidate: number for candidate, number in zip(most_consistent_permutation, permutation_numbers)}

    # Convert the ballots from using candidate names to using corresponding numbers
    ballot_counts = {tuple(candidate_to_number_map[candidate] for candidate in ballot): count for ballot, count in ballots.items()}
    consistent = 0
    total = 0

    for ballot in ballots:
        ballot_position = []
        for candidate in ballot:
            ballot_position.append(normalized_distances[candidate])
        if len(ballot) > 0:
            total += ballots[ballot]
            if evaluate_ballot_consistency(ballot_position)[0] is True:
                consistent += ballots[ballot]

    '''for ballot, count in ballot_counts.items():
        if len(ballot) > 0:
            total += count
            consistency_check = evaluate_ballot_consistency(ballot)
            if consistency_check[0] is True and consistency_check[1] is not None:
                consistent += count'''
    
    return consistent/total 


def plot_consistency_points(points: Dict[float, int], file: str) -> None:
    """
    Plots the consistency points.

    Parameters
    ----------
    points : dict
        A dictionary that maps each point (representing a consistency value) to a corresponding count.
    file : str
        The name of the file with election data.
    """

    plt.figure(figsize=(10, 6))
    plt.bar(points.keys(), points.values(), width=0.5, color='g')
    plt.xlabel("Consistency Value")
    plt.ylabel("Number of Ballots")
    plt.title(f"Consistency Points for {file}")
    plt.show()

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

def get_gamma(mds, ballots):
    mcp = []
    mcp_num = []
    for k in mds:
        mcp.append(k)
        mcp_num.append(mds[k])
    
    temp = {}
    j = 0
    for i in range(len(mcp)):
        temp[mcp[i]] = j
        j += 1
    c = 0
    total = 0
    for b in ballots:
        if len(b) > 0:
            total += ballots[b] 
            b_num = []
            for candidate in b:
                if candidate in mcp:
                    b_num.append(temp[candidate])
            if (evaluate_ballot_consistency(b_num, len(mds))[0] is True):
                c += ballots[b]
    
    return (c/total)

def freq(ballots, candidates):
    result_freq = {}
    result_first = {}

    frequency = {}
    first = {}
    empty = 0
    for c in candidates:
        frequency[c] = 0
        first[c] = 0
    
    for b in ballots:
        if len(b) > 0:
            first[b[0]] += ballots[b]
        else:
            empty += ballots[b]
        for c in b:
            frequency[c] += ballots[b]
    
    total = sum(ballots.values())
    total -= empty 
    for c in frequency:
        result_freq[c] = (frequency[c]/total) * 100
    for c in first:
        result_first[c] = (first[c]/total) * 100
    
   
    return result_freq, result_first
