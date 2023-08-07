import pandas as pd 
import numpy as np
from typing import Dict, List, Optional, Tuple
import re

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
        ignore_values = ['UWI', '(WRITE-IN)', 'WRITE-IN', 'writein', 'Write-In', 'Write-in', 'skipped', 'overvote', 'Undeclared', 'undervote']

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

