import os
import pandas as pd

from typing import List, Tuple
from fuzzywuzzy import process

def get_race_id(file_path: str) -> List[str]:
    """Extracts the RaceID from a given CSV file."""
    df = pd.read_csv(file_path, usecols=["RaceID"])
    return df["RaceID"].dropna().values.tolist()

def find_closest_match(file_paths: List[str], race_id_list: List[str]) -> dict:
    """
    Finds the closest match for each filename in file_paths within the race_id_list.
    Returns a dictionary with file paths as keys and a tuple (closest match, match score) as values.
    """
    matches = {}
    for file_path in file_paths:
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        closest_match = process.extractOne(file_name.lower(), race_id_list)
        if closest_match:
            matches[file_path] = (closest_match[0], closest_match[1])
        else:
            matches[file_path] = (None, None)
    return matches

def get_file_paths(dir_path: str) -> List[str]:
    """Returns a list of file paths from the given directory."""
    return [os.path.join(dir_path, file) for file in os.listdir(dir_path)]

def match(csv_path: str, dir_path: str) -> pd.DataFrame:
    """
    Performs the matching operation between the RaceID in the given CSV file and filenames in the directory.
    Returns a DataFrame containing the matches.
    """
    race_id_list = get_race_id(csv_path)
    file_paths = get_file_paths(dir_path)
    matches = find_closest_match(file_paths, race_id_list)
    return pd.DataFrame(list(matches.values()), columns=["race_id", "score"], index=list(matches.keys()))

# Replace with your local paths
main_dir_path = 'team_arrow/rcv_elections_database'
output_path = 'team_arrow/rcv_elections_database/MatchedElections.csv'

# Define subdirectories and corresponding CSV files
sub_dirs = ['proportional', 'sequential', 'single']
csv_files = ['ProportionalRCV.csv', 'SequentialRCV.csv', 'SingleWinnerRCV.csv']

# Match and save
df = pd.concat([match(os.path.join(main_dir_path, csv_file), os.path.join(main_dir_path, sub_dir)) 
                for csv_file, sub_dir in zip(csv_files, sub_dirs)])

# Split the Filename into main_dir_path, sub_dir_path, and filename
df.reset_index(inplace=True)
df[['main_dir_path', 'sub_dir_path', 'filename']] = df['index'].str.rsplit(os.sep, 2, expand=True)
df.drop(columns='index', inplace=True)

# Reorder columns
df = df[['main_dir_path', 'sub_dir_path', 'filename', 'race_id', 'score']]

# Save to CSV
df.to_csv(output_path, index=False)