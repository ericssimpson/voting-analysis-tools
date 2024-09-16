"""
This script processes raw election data to create a unified, queryable database.

It performs the following main task:
-   Matches raw election data files (e.g., from `data/raw/rcv_proportional`)
    with their corresponding metadata from the `rcv_database` directory.
-   It uses an exact match between the filename (without extension) and the `RaceID`
    in the metadata CSVs.

The script outputs two files into the `data/processed` directory:
1.  `elections_database.csv`: A master CSV file containing all successfully matched
    elections, linking each `RaceID` to its election type and the filepath of the
    raw ballot data.
2.  `unmatched_files.log`: A log file listing all the raw data files that could
    not be matched to a `RaceID`.

Usage:
    python process_data.py
"""

import os
from typing import Dict, List, Tuple

import pandas as pd

# --- Constants and Configuration ---

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Raw and processed data directories
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

# Output filenames
ELECTIONS_DB_FILENAME = "elections_database.csv"
UNMATCHED_LOG_FILENAME = "unmatched_files.log"

# Defines the relationship between metadata files and the directories containing
# the corresponding raw ballot data.
ELECTION_SOURCES = {
    "proportional": ("ProportionalRCV.csv", "rcv_proportional"),
    "single": ("SingleWinnerRCV.csv", "rcv_single"),
    "sequential": ("OtherMultiWinnerRCV.csv", "rcv_sequential"),
}

# --- Function Definitions ---


def get_race_ids(csv_path: str) -> List[str]:
    """
    Extracts a unique list of RaceIDs from a given metadata CSV file.

    Args:
        csv_path (str): The full path to the metadata CSV file.

    Returns:
        List[str]: A list of unique, non-null RaceIDs.
    """
    try:
        df = pd.read_csv(csv_path, usecols=["RaceID"])
        return df["RaceID"].dropna().unique().tolist()
    except FileNotFoundError:
        print(f"Warning: Metadata file not found at {csv_path}")
        return []
    except Exception as e:
        print(f"Error reading RaceIDs from {csv_path}: {e}")
        return []


def get_election_filepaths(dir_path: str) -> List[str]:
    """
    Returns a list of all CSV file paths within a given directory.

    Args:
        dir_path (str): The full path to the directory containing election data.

    Returns:
        List[str]: A list of full file paths to the CSV files.
    """
    if not os.path.isdir(dir_path):
        return []
    return [
        os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith(".csv")
    ]


def match_elections_exact(
    metadata_csv_path: str, data_dir_path: str
) -> Tuple[List[Dict], List[str]]:
    """
    Performs an exact match between RaceIDs in a metadata file and the filenames
    in a corresponding data directory.

    Args:
        metadata_csv_path (str): Path to the metadata CSV file.
        data_dir_path (str): Path to the directory with raw ballot data.

    Returns:
        Tuple[List[Dict], List[str]]: A tuple containing:
        - A list of matched race dictionaries.
        - A list of filepaths that could not be matched.
    """
    race_ids = get_race_ids(metadata_csv_path)
    race_id_set = set(race_ids)
    filepaths = get_election_filepaths(data_dir_path)

    matched_races = []
    unmatched_filepaths = []

    for path in filepaths:
        # Extract the filename without extension to match against RaceID
        filename = os.path.splitext(os.path.basename(path))[0]
        if filename in race_id_set:
            matched_races.append({"filepath": path, "race_id": filename})
        else:
            unmatched_filepaths.append(path)

    return matched_races, unmatched_filepaths


# --- Main Execution ---


def main():
    """
    Main function to orchestrate the data processing pipeline.
    """
    print("--- Starting Data Processing ---")

    # Ensure the processed data directory exists
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    print(f"Processed data will be saved to: {PROCESSED_DATA_DIR}")

    all_matched_races = []
    all_unmatched_files = []

    # Process each defined election source
    for election_type, (metadata_filename, data_dirname) in ELECTION_SOURCES.items():
        print(f"\n--- Processing {election_type} elections ---")

        metadata_path = os.path.join(RAW_DATA_DIR, "rcv_database", metadata_filename)
        data_path = os.path.join(RAW_DATA_DIR, data_dirname)

        matched, unmatched = match_elections_exact(metadata_path, data_path)

        # Add the election type to the matched data for better categorization
        for race in matched:
            race["election_type"] = election_type

        all_matched_races.extend(matched)
        all_unmatched_files.extend(unmatched)

        print(f"Found {len(matched)} matched elections.")
        print(f"Found {len(unmatched)} unmatched files.")

    # Create and save the final elections database
    if all_matched_races:
        elections_df = pd.DataFrame(all_matched_races)
        # Reorder columns for clarity
        elections_df = elections_df[["race_id", "election_type", "filepath"]]
        output_path = os.path.join(PROCESSED_DATA_DIR, ELECTIONS_DB_FILENAME)
        elections_df.to_csv(output_path, index=False)
        print(f"\nSuccessfully created elections database at: {output_path}")
    else:
        print("\nNo matched elections found. The database file was not created.")

    # Create and save the log of unmatched files
    if all_unmatched_files:
        log_path = os.path.join(PROCESSED_DATA_DIR, UNMATCHED_LOG_FILENAME)
        with open(log_path, "w") as f:
            f.write(
                "# The following files from data/raw could not be matched to a "
                "RaceID.\n"
            )
            for filepath in all_unmatched_files:
                f.write(f"{filepath}\n")
        print(f"Log of unmatched files saved at: {log_path}")
    else:
        print("No unmatched files found.")

    print("\n--- Data Processing Complete ---")


if __name__ == "__main__":
    main()
