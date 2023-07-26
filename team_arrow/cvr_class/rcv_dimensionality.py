from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numba import njit
from sklearn.manifold import MDS
from sklearn.utils import check_random_state


@njit
def calculate_pair_mentions(ballots: np.ndarray, num_candidates: int, num_ballots: int, num_ranks: int) -> np.ndarray:
    """
    Calculate the number of times each pair of candidates is mentioned together in the ballots.

    Parameters
    ----------
    ballots : numpy.ndarray
        An array representing the ranked votes. Each row is a ballot, with candidates represented by their indices.
    num_candidates : int
        The total number of unique candidates.
    num_ballots : int
        The total number of ballots.
    num_ranks : int
        The total number of ranks in each ballot.

    Returns
    -------
    numpy.ndarray
        A square matrix where the entry at row i and column j represents the number of times candidate i and candidate j are mentioned together in the ballots.
    """
    
    # Initialize a zero matrix to store the counts of pair mentions
    pair_mentions = np.zeros((num_candidates, num_candidates))
    
    # For each ballot
    for i in range(num_ballots):
        # For each rank in the ballot
        for j in range(num_ranks):
            # For each other rank in the ballot
            for k in range(num_ranks):
                # Increment the count for the pair
                pair_mentions[ballots[i, j] - 1, ballots[i, k] - 1] += 1
    
    return pair_mentions


def plot_rcv_analysis(mds_1d_coordinates: dict, mds_2d_coordinates, most_common_order: tuple, all_order_frequencies: list, candidate_names: list) -> None:
    """
    Plot the ranked-choice-voting (RCV) analysis results.

    This function creates two plots:
    1. A bar plot showing the frequencies of candidate orders.
    2. A scatter plot showing the average MDS-1D coordinates for the most common order.

    Parameters
    ----------
    avg_1d_values_dict : dict
        A dictionary mapping candidate order to average MDS-1D coordinates.
    most_common_order : tuple
        A tuple representing the most common order of candidates.
    all_order_frequencies : list
        A list of tuples, each containing a candidate order and its frequency.
    candidate_names : list
        A list of candidate names.

    Returns
    -------
    None
    """

    # Plot frequencies of all orders
    plt.figure(figsize=(10, 6))
    orders, frequencies = zip(*all_order_frequencies)
    orders = ["-".join(candidate_names[list(order)]) for order in orders]
    plt.barh(orders, frequencies)
    plt.xlabel("Frequency")
    plt.title("Frequencies of Candidate Orders")
    plt.show()

    # Plot average MDS-1D coordinates for most common order
    mds_1d_coordinates = mds_1d_coordinates[most_common_order]
    plt.figure(figsize=(10, 6))
    plt.scatter(np.zeros_like(mds_1d_coordinates), mds_1d_coordinates)
    for i in range(len(candidate_names)):
        plt.text(0.2, mds_1d_coordinates[i], candidate_names[most_common_order[i]])
    plt.axis([-1, 1.5, mds_1d_coordinates.min() * 1.2, mds_1d_coordinates.max() * 1.2])
    plt.ylabel("MDS-1D Coordinate")
    plt.title("Average MDS-1D Coordinates for Most Common Order")
    plt.show()


def perform_rcv_analysis(csv_file: str, n_runs: int, random_state: Optional = None, ignore_values: Optional = None, metric: bool = True) -> Tuple[Dict, Tuple, List, List]:
    """
    Perform ranked-choice-voting (RCV) analysis on a CSV file of ballots.

    Parameters
    ----------
    csv_file : str
        The path to the CSV file containing ballots.
    n_runs : int
        The number of MDS runs to perform.
    random_state : int, RandomState instance or None, default=None
        Determines random number generation for centroid initialization. Use an int to make the randomness deterministic.
    ignore_values : list, optional
        A list of values to ignore when reading the CSV file. Defaults to common non-candidate values.
    metric : bool, default=True
        If True, perform metric MDS; otherwise, perform nonmetric MDS.

    Returns
    -------
    tuple
        A tuple containing the following elements:
        - mds_1d_coordinates : A dictionary mapping candidate order to average MDS coordinates.
        - mds_2d_coordinates : A dictionary mapping candidate order to average MDS coordinates for 2 dimensions. (TODO)
        - most_common_order : The most common order of candidates.
        - order_frequencies : A list of tuples, each containing a candidate order and its frequency.
        - candidate_names : A list of candidate names.
    """

    # Default values to ignore when reading CSV
    if ignore_values is None:
        ignore_values = ['(WRITE-IN)', 'writein', 'Write-In', 'Write-in', 'skipped', 'overvote', 'Undeclared', 'undervote']

    # Load the CSV file and filter to keep only the 'rank' columns
    df = pd.read_csv(csv_file)
    df = df.filter(regex='^rank')

    # Filter out rows that contain non-candidate values
    df = df[~df.isin(ignore_values)].dropna()

    # Create a list of all candidate names and convert names to integer codes
    raw_ballots = df.values.tolist()
    candidate_names = pd.unique(df.values.ravel())
    candidate_dict = {name: i for i, name in enumerate(candidate_names)}
    num_candidates = len(candidate_names)

    # Convert ballots to integers representing candidates
    ballots = [[candidate_dict[candidate] for candidate in ballot] for ballot in raw_ballots]
    ballots = np.array(ballots)

    # Count up frequencies of consecutive-pair ballot choices
    num_ballots, num_ranks = ballots.shape
    counts = np.zeros((num_candidates, num_candidates))
    for i in range(num_ballots):
        for j in range(num_ranks - 1):
            counts[ballots[i, j], ballots[i, j+1]] += 1

    # Calculate pair mentions and normalize to frequencies relative to votes cast for the two candidates
    mentioned_together = calculate_pair_mentions(ballots, num_candidates, num_ballots, num_ranks)
    frequencies = counts / mentioned_together

    # Combine frequencies in either direction to create symmetric matrix
    freq_upper_triangle = np.zeros((num_candidates, num_candidates))
    for i in range(num_candidates):
        for j in range(i+1, num_candidates):
            freq_upper_triangle[i, j] = (frequencies[i, j] + frequencies[j, i]) / 2
            freq_upper_triangle[j, i] = freq_upper_triangle[i, j]

    # Compute distance metric
    min_freq = np.min(freq_upper_triangle[freq_upper_triangle > 0])
    distance = 1 / np.sqrt(freq_upper_triangle)
    distance[np.isnan(distance)] = 2 / min_freq
    distance[np.isinf(distance)] = 2 / min_freq
    np.fill_diagonal(distance, 0)

    # Initialize random state
    random_state = check_random_state(random_state)

    # Initialize containers for multiple MDS runs
    all_orders = defaultdict(lambda: 0)
    mds_1d_coordinates = defaultdict(list)
    mds_2d_coordinates = defaultdict(list)

    # Run multidimensional scaling multiple times
    for _ in range(n_runs):

        # Perform nonmetric multidimensional scaling
        mds_1d = MDS(n_components=1, metric=metric, max_iter=1000, random_state=random_state, dissimilarity='precomputed', normalized_stress='auto')
        mds_2d = MDS(n_components=2, metric=metric, max_iter=1000, random_state=random_state, dissimilarity='precomputed', normalized_stress='auto')

        # Fit and transform the distance matrix
        values_1d = mds_1d.fit_transform(distance)
        values_2d = mds_2d.fit_transform(distance)

        # Identify orders in 1D and 2D TODO Procrustes alignment for 2d ordering
        order_1d = tuple(np.argsort(values_1d.flatten()))
        order_2d = tuple(np.lexsort(values_2d.T))

        # Store orders and MDS coordinates
        all_orders[tuple(order_1d)] += 1
        mds_1d_coordinates[order_1d].append(values_1d.flatten()[np.array(order_1d)])
        mds_2d_coordinates[order_2d].append(values_2d.flatten()[np.array(order_2d)])

    # Find most common order and frequencies of all orders along single dimension
    temporary_orders = list(all_orders.keys())
    for order in temporary_orders:
        reversed_order = tuple(reversed(order))
        if reversed_order in all_orders:
            all_orders[order] += all_orders[reversed_order]
            del all_orders[reversed_order]
    order_counter = Counter(all_orders)
    most_common_order = order_counter.most_common(1)[0][0]
    order_frequencies = order_counter.most_common()

    # Calculate average MDS coordinates for each unique order
    mds_1d_coordinates = {order: np.mean(values, axis=0) for order, values in mds_1d_coordinates.items()}

    return mds_1d_coordinates, mds_2d_coordinates, most_common_order, order_frequencies, candidate_names


def get_distances_normalized(most_common_order: tuple, mds_1d_coordinates: Dict[tuple, np.ndarray], candidate_names: List[str]) -> Dict[str, float]:
    """
    Normalize the distances of MDS-1D coordinates for the most common order to start from 0 and ends at the number of candidates.
    Return a dictionary with candidate names as keys and normalized distances as values.

    Parameters
    ----------
    most_common_order : tuple
        A tuple representing the most common order of candidates.a
    mds_1d_coordinates : dict
        A dictionary mapping candidate order to average MDS-1D coordinates.
    candidate_names : list
        A list of candidate names.

    Returns
    -------
    dict
        A dictionary mapping candidate names to normalized MDS-1D coordinates.
    """
    
    # Extract the MDS-1D coordinates for the most common order
    mds_1d_coordinates_common_order = mds_1d_coordinates[most_common_order]
    
    # Compute the min and max of the MDS-1D coordinates
    min_val = np.min(mds_1d_coordinates_common_order)
    max_val = np.max(mds_1d_coordinates_common_order)

    # Compute the normalized MDS-1D coordinates (shifted so that they start from 0 and end at the number of candidates)
    mds_1d_coordinates_common_order_normalized = ((mds_1d_coordinates_common_order - min_val) / (max_val - min_val)) * (len(candidate_names) - 1)
    
    # Create a dictionary with candidate names as keys and normalized distances as values
    normalized_coordinates_dict = {candidate_names[most_common_order[i]]: mds_1d_coordinates_common_order_normalized[i] for i in range(len(most_common_order))}
    
    return normalized_coordinates_dict


def perform_rcv_and_normalize(csv_file: str, n_runs: int = 1000) -> Dict[str, float]:
    """
    Perform the ranked-choice-voting (RCV) analysis and normalize the distances of MDS-1D coordinates.
    Return a dictionary with candidate names as keys and normalized distances as values.

    Parameters
    ----------
    csv_file : str
        The name of the CSV file to perform the RCV analysis on.
    n_runs : int
        The number of runs for the RCV analysis.

    Returns
    -------
    dict
        A dictionary mapping candidate names to normalized MDS-1D coordinates.
    """
    
    # Perform the RCV analysis
    mds_1d_coordinates, mds_2d_coordinates, most_common_order, order_frequencies, candidate_names = perform_rcv_analysis(csv_file, n_runs)
    
    # Normalize the distances
    normalized_coordinates_dict = get_distances_normalized(most_common_order, mds_1d_coordinates, candidate_names)
    
    return normalized_coordinates_dict
