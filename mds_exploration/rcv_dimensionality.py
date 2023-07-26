from collections import Counter, defaultdict
from typing import Dict, Tuple, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.utils import check_random_state
from sklearn.manifold import MDS


def calculate_mentioned_together(ballots: np.ndarray, num_candidates: int, num_ballots: int, num_ranks: int) -> np.ndarray:
    """
    Calculate how often each pair of candidates is mentioned together on ballots.

    The function uses Numba to accelerate the computation.

    Parameters
    ----------
    ballots : np.ndarray
        The 2D array representing the ballots. Each row represents a ballot and each column a rank.
    num_candidates : int
        The number of candidates.
    num_ballots : int
        The number of ballots.
    num_ranks : int
        The number of ranks in each ballot.

    Returns
    -------
    np.ndarray
        A 2D array where the element at index (i, j) represents the number of times candidate i and candidate j are mentioned together on ballots.
    """
    mentioned_together = np.zeros((num_candidates, num_candidates))
    for i in range(num_ballots):
        for j in range(num_ranks):
            for k in range(num_ranks):
                if ballots[i, j] <= num_candidates and ballots[i, k] <= num_candidates:
                    mentioned_together[ballots[i, j] - 1, ballots[i, k] - 1] += 1
    return mentioned_together


def plot_rcv_analysis(avg_1d_values_dict: dict, most_common_order: tuple, all_order_frequencies: list, candidate_names: list) -> None:
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
    mds_1d_coordinates = avg_1d_values_dict[most_common_order]
    plt.figure(figsize=(10, 6))
    plt.scatter(np.zeros_like(mds_1d_coordinates), mds_1d_coordinates)
    for i in range(len(candidate_names)):
        plt.text(0.2, mds_1d_coordinates[i], candidate_names[most_common_order[i]])
    plt.axis([-1, 1.5, mds_1d_coordinates.min() * 1.2, mds_1d_coordinates.max() * 1.2])
    plt.ylabel("MDS Dimension 1")
    plt.title("Average 1D MDS of Candidates")
    plt.show()

    # Plot 2D MDS coordinates
    plt.figure(figsize=(10, 8))
    plt.scatter(mds_2d_coordinates[:, 0], mds_2d_coordinates[:, 1])
    for i, txt in enumerate(candidate_names):
        plt.annotate(txt, (mds_2d_coordinates[i, 0], mds_2d_coordinates[i, 1]))
    plt.xlabel("MDS Dimension 1")
    plt.ylabel("MDS Dimension 2")
    plt.title("2D MDS of Candidates")
    plt.show()


def perform_rcv_analysis(
    csv_file: str, 
    n_runs: int, 
    random_state=None, 
    ignore_values=None, 
    metric=True
) -> Tuple[Dict, Tuple, List, List]:
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
        - avg_y_values_dict : A dictionary mapping candidate order to average MDS coordinates.
        - most_common_order : The most common order of candidates.
        - all_order_frequencies : A list of tuples, each containing a candidate order and its frequency.
        - candidate_names : A list of candidate names.
    """
    # Default values to ignore when reading CSV
    if ignore_values is None:
        ignore_values = ['(WRITE-IN)', 'writein', 'Write-In', 'Write-in', 'skipped', 'overvote', 'Undeclared']

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

    # Calculate 'mentioned_together' and normalize to frequencies relative to votes cast for the two candidates
    mentioned_together = calculate_mentioned_together(ballots, num_candidates, num_ballots, num_ranks)
    frequencies = counts / mentioned_together

    # Combine frequencies in either direction to create symmetric matrix
    freq_upper_triangle = np.zeros((num_candidates, num_candidates))
    for i in range(num_candidates):
        for j in range(i+1, num_candidates):
            freq_upper_triangle[i, j] = (frequencies[i, j] + frequencies[j, i]) / 2
            freq_upper_triangle[j, i] = freq_upper_triangle[i, j]

    # Compute 'd' (distance metric)
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
    mds_2d_coordinates = None

    # Run MDS multiple times
    for _ in range(n_runs):

        # Perform nonmetric MDS for 1 dimension
        mds_1d = MDS(n_components=1, metric=metric, max_iter=1000, random_state=random_state, dissimilarity='precomputed', normalized_stress='auto')
        values_1d = mds_1d.fit_transform(distance)

        # Identify order in 1D
        order_1d = tuple(np.argsort(values_1d.flatten()))

        # Store orders and MDS coordinates
        all_orders[tuple(order_1d)] += 1
        mds_1d_coordinates[order_1d].append(values_1d.flatten()[np.array(order_1d)])

    # Find most common order and frequencies of all orders along single dimension
    temporary_orders = list(all_orders.keys())
    for order in temporary_orders:
        reversed_order = tuple(reversed(order))
        if reversed_order in all_orders:
            all_orders[order] += all_orders[reversed_order]
            del all_orders[reversed_order]
    order_counter = Counter(all_orders)
    most_common_order = order_counter.most_common(1)[0][0]
    all_order_frequencies = order_counter.most_common()

    # Calculate average MDS coordinates for each unique order
    avg_1d_values_dict = {order: np.mean(values, axis=0) for order, values in mds_1d_coordinates.items()}

    return avg_1d_values_dict, most_common_order, all_order_frequencies, candidate_names

'''

# Test the function with the provided CSV file
maine = perform_rcv_analysis(f"Maine_11062018_CongressionalDistrict2.csv", n_runs=1000)
avg_y_values_dict, most_common_order, all_order_frequencies, candidate_names = maine

# Call the plotting function
plot_rcv_analysis(avg_y_values_dict, most_common_order, all_order_frequencies, candidate_names)

'''