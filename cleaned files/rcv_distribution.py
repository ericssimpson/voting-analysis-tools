import re
from typing import Dict, List, Optional, Tuple
from consistency import *
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from MDS_analysis import perform_rcv_and_normalize


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

        ballot_num = ballot_to_num(ballot, normalized_distances)
        #checking if the ballot is consistent with the mds permutation but assuming they are equaly distances 
        check_consistency = evaluate_ballot_consistency(ballot_num, len(candidates), normalized_distances)
        point = check_consistency[1]
        if check_consistency[0] is True:

            if point is not None:
                '''if len(ballot) > 1:
                    #if the point falls closer to the second choice, we push it back 
                    point = min(point, ((mds_distances[0] + mds_distances[1])/2 - ((mds_distances[0] + mds_distances[1])/(len(candidates) + 1))))'''
                if point not in points:
                    points[point] = 0
                points[point] += ballots[ballot]
    
    return points


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


def distribute_points(interval, num_points=1000):
    min_val, max_val = interval
    return np.linspace(min_val, max_val, num_points)

def plot_KDE(ballots, normalized_distances):
    
    distributed_points = []
    for b in ballots:
        if len(b) > 0:
            b_num = ballot_to_num(b, normalized_distances)
            if len(b) > 1:    
                success, interval = solve_lp(b_num, len(normalized_distances))
                if success:
                    points = distribute_points(interval, ballots[b])
                    distributed_points.extend(points)
            else:
                success = True
                interval = (b_num, b_num)
                points = distribute_points(interval, ballots[b])
                distributed_points.extend(points)
        
    distributed_points = np.array(distributed_points, dtype=float)
    normalized_points = []
    normalized_names = []
    for name in normalized_distances:
        normalized_names.append(name)
        normalized_points.append(normalized_distances[name])
    plt.figure(figsize=(10, 6))
    sns.kdeplot(distributed_points, fill=True)
    plt.title('Kernel Density Estimation of Data')
    plt.xticks(normalized_points, normalized_names, rotation=45)
    plt.xlabel('Value')
    plt.ylabel('Density')
    plt.grid(True)
    plt.show()

