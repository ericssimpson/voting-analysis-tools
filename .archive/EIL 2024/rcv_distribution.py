import re
from typing import Dict, List, Optional, Tuple
from consistency import *
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from MDS_analysis import perform_rcv_and_normalize
import seaborn as sns



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
    if ignore_values is not None:
        ignore_values.extend(['UWI', '(WRITE-IN)', 'WRITE-IN', 'writein', 'Write-In', 'Write-in', 'skipped', 'overvote', 'Undeclared', 'undervote', 'Write in'])
    else:
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

def plot_KDE(ballots, normalized_distances, filename=None, ignore=False, save=False, directory=None):
    
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
    if save == False:
        plt.show()
    else:
        if ignore == False:
            if directory is None:
                file_path = "KDE/" + filename[0:-4] + ".png"
                plt.savefig(file_path,  dpi=600, bbox_inches='tight')
                np.save('np_data/' + filename[0:-4] + ".npy", distributed_points)
                plt.close()
            else:
                file_path = directory + "/" + filename[0:-4] + ".png"
                plt.savefig(file_path,  dpi=600, bbox_inches='tight')
                np.save('np_data_new/' + filename[0:-4] + ".npy", distributed_points)
                plt.close()

        else:
            file_path = "ignored_KDE/" + filename[0:-4] + ".png"
            plt.savefig(file_path,  dpi=600, bbox_inches='tight')
            np.save('ignored_np_data/' + filename[0:-4] + ".npy", distributed_points)
            plt.close()



def get_frequency(ballots, candidates):

    freqs = {}
    total = 0
    for b in ballots:
        if len(b) > 0:
            total += ballots[b]
            first_candidate = b[0]
            if first_candidate not in freqs:
                freqs[first_candidate] = 0
            freqs[first_candidate] += ballots[b]
    for candidate in freqs:
        freqs[candidate] /= total

    return freqs



def plot_median_and_winner(filename):

    #filename = "Maine_11062018_CongressionalDistrict2.npy"
    #file = "np_data/Maine_11062018_CongressionalDistrict2.npy"
    winners = pd.read_csv("diff.csv")
    winner = (winners.loc[winners["filename"]==(filename+".csv"), "IRV1"]).tolist()[0]

    df = pd.read_csv("null_elections/" + filename + ".csv")

    distributed_points = np.load("np_data/" + filename + ".npy")
    median_value = np.median(distributed_points)
    #df['normalized_position'] = (df['position'] - min_position) / (max_position - min_position)
    winner_position = (df.loc[df["candidate"]==winner, "position"]).tolist()[0]


    plt.figure(figsize=(10, 6))
    sns.kdeplot(distributed_points, fill=True)
    plt.title('Kernel Density Estimation of Data')
    #plt.xticks(normalized_points, normalized_names, rotation=45)
    plt.xlabel('Value')
    plt.ylabel('Density')
    plt.grid(True)

    plt.axvline(median_value, color='red', linestyle='dashed', linewidth=1)
    plt.text(median_value, plt.gca().get_ylim()[1]*0.95, f'Median: {median_value:.2f}', color='red', ha='center')

    plt.axvline(winner_position, color='blue', linestyle='dashed', linewidth=1)
    plt.text(winner_position, plt.gca().get_ylim()[1]*0.95, f'Winner: {winner_position:.2f}', color='blue', ha='center')

    plt.show()



def plot_median_and_winner_normalized(filename, show=False):
    #filename that you pass here should be without the .csv or .npy

    # Load the winner's data
    winners = pd.read_csv("diff.csv")
    winner = winners.loc[winners["filename"] == (filename + ".csv"), "IRV1"].tolist()[0]

    # Load the positions data
    df = pd.read_csv("null_elections/" + filename + ".csv")

    # Load the distributed points
    distributed_points = np.load("np_data_new/" + filename + ".npy")

    # Normalize the distributed points
    min_position = np.min(distributed_points)
    max_position = np.max(distributed_points)
    normalized_points = (distributed_points - min_position) / (max_position - min_position)

    # Calculate the median of the normalized points
    median_value = np.median(normalized_points)

    # Normalize the positions in the dataframe
    df['normalized_position'] = (df['position'] - min_position) / (max_position - min_position)

    # Get the winner's normalized position
    winner_position = df.loc[df["candidate"] == winner, "normalized_position"].tolist()[0]

    # Plot the data
    plt.figure(figsize=(10, 6))
    sns.kdeplot(normalized_points, fill=True)
    plt.title('Kernel Density Estimation of Normalized Data')
    plt.xlabel('Normalized Value')
    plt.ylabel('Density')
    plt.grid(True)

    # Mark the median on the x-axis
    plt.axvline(median_value, color='red', linestyle='dashed', linewidth=1)
    plt.text(median_value, plt.gca().get_ylim()[1] * 0.95, f'Median: {median_value:.2f}', color='red', ha='center')

    # Mark the winner on the x-axis
    plt.axvline(winner_position, color='blue', linestyle='dashed', linewidth=1)
    plt.text(winner_position, plt.gca().get_ylim()[1] * 0.90, f'Winner: {winner_position:.2f}', color='blue', ha='center')

    if show is False:
        plt.close()
    else:
        plt.show()
    return winner_position, median_value

# Example usage:
# plot_median_and_winner("Alaska_08162022_HouseofRepresentativesSpecial")


def get_median_voter_distances(filename):
    #filename without .npy or .csv

    candidate_positions_file = pd.read_csv("null_elections/" + filename + ".csv")
    positions = pd.Series(candidate_positions_file['position'].values, index=candidate_positions_file['candidate']).to_dict()

    n = len(positions)
    normalized_positions = {key: value / (n - 1) for key, value in positions.items()}

    winner_position, median_voter_position = plot_median_and_winner_normalized(filename, show=False)

    items = normalized_positions.items()
    closest_candidate, closest_candiate_position = min(items, key=lambda item: abs(item[1] - median_voter_position))

    median_voter_distance = abs(winner_position - median_voter_position)
    median_voter_preference_distance = abs(winner_position - closest_candiate_position)

    return median_voter_distance, median_voter_preference_distance
    