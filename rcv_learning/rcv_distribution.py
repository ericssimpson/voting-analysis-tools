from typing import Dict, List, Optional, Tuple

import pandas as pd
import matplotlib.pyplot as plt

from rcv_dimensionality import perform_rcv_and_normalize


def parse_election_data(filename: str) -> Tuple[Dict[Tuple[str, ...], int], List[str]]:
    """
    Parses a CSV file with election data.

    Parameters
    ----------
    filename : str
        The name of the file with election data.

    Returns
    -------
    tuple
        A tuple containing a dictionary that maps each ballot (a tuple of candidate names) to a corresponding count, 
        and a list of all the candidates.
    """

    data = pd.read_csv(filename, low_memory=False)

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

                # Add candidate to ranking if it's not skipped, a write-in, an overvote, or an undervote
                if candidate != "skipped" and candidate != "Write-in" and candidate[:5].lower() != "write" and candidate != "overvote" and candidate != "undervote":
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


def evaluate_ballot_consistency(ballot: list) -> Tuple[bool, Optional[float]]:
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

    consistency_value = 0 
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
    if abs(consistency_value) >= (ballot[1] - ballot[0])/2 or consistency_value == 0:
        return (False, consistency_value + ballot[0]) 

    consistency_value += ballot[0]
    for candidate in ballot:
        distance_list.append(abs(candidate - consistency_value))

    if(all(distance_list[i] <= distance_list[i + 1] for i in range(len(distance_list) -  1))):
        return (True, consistency_value)

    return (False, consistency_value)


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


def get_consistency_points(file: str) -> Dict[float, int]:
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

    rcv_and_normalized_results = perform_rcv_and_normalize(file)
    most_consistent_permutation = []
    permutation_numbers = []
    for candidate in rcv_and_normalized_results:
        most_consistent_permutation.append(candidate)
        permutation_numbers.append(rcv_and_normalized_results[candidate])

    return calculate_ballot_consistency(file, most_consistent_permutation, permutation_numbers)
