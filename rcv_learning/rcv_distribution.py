from typing import Dict, Optional, Tuple

import rcv_parser # TODO refactor or build in a way that this import is not needed and assumptions are shared between scripts
from rcv_dimensionality import perform_rcv_and_normalize


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
    ballots, candidates = rcv_parser.parser(filename)

    # Create a dictionary that maps each candidate to a corresponding number
    candidate_to_number_map = {candidate: number for candidate, number in zip(most_consistent_permutation, permutation_numbers)}

    # Convert the ballots from using candidate names to using corresponding numbers
    ballots = [[candidate_to_number_map[candidate] for candidate in ballot] for ballot in ballots]

    points = {}
    for ballot in ballots:
        consistency_check = calculate_ballot_consistency(ballot)
        if consistency_check[0] is True and consistency_check[1] is not None:
            consistency_value = consistency_check[1]
            if consistency_value not in points:
                points[consistency_value] = 0
            points[consistency_value] += ballots[ballot]
    
    return points


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
    dict
        A dictionary that maps each point (representing a consistency value) to a corresponding count.
    """
    most_common_order, mds_1d_coordinates, candidate_names = perform_rcv_and_normalize(file)

    # Create a dictionary that maps each candidate to a corresponding number
    candidate_to_number_map = {candidate: number for candidate, number in zip(most_common_order, mds_1d_coordinates)}

    return calculate_ballot_consistency(file, most_common_order, candidate_to_number_map)
