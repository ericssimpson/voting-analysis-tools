"""
This script processes raw election data to create a unified, queryable database.

It performs the following main task:
-   Matches raw election data files (e.g., from `data/raw/rcv_proportional`)
    with their corresponding metadata from the `rcv_database` directory.
-   It uses an exact match between the filename (without extension) and the `RaceID`
    in the metadata CSVs.
-   If an exact match is not found, it uses fuzzy matching to suggest possible
    `RaceID`s to the user, allowing them to select one or more matches interactively.

The script outputs two to three files into the `data/processed` directory:
1.  `elections_database.csv`: A master CSV file containing all successfully matched
    elections, linking each `RaceID` to its election type and the filepath of the
    raw ballot data.
2.  `unmatched_files.log`: A log file listing all the raw data files that could
    not be matched to a `RaceID`.
3.  `manual_matches.log`: A log file that records any manual matches made by the user
    during the fuzzy matching process.

Usage:
    python process_data.py
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd
from rapidfuzz import fuzz, process


@dataclass
class MatchResults:
    """Holds the results of the matching process."""

    newly_matched: List[Dict]
    still_unmatched: List[str]
    manual_matches_log: List[str]


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


def _get_user_fuzzy_match_choice(
    top_matches: List[Tuple[str, float, int]], page: int, page_size: int
) -> Tuple[str, int]:
    """
    Displays fuzzy matching suggestions and captures the user's choice.

    Args:
        top_matches (List[Tuple[str, float, int]]): A list of top fuzzy matches.
        page (int): The current page number for pagination.
        page_size (int): The number of items to show per page.

    Returns:
        Tuple[str, int]: A tuple containing the user's input and the next page number.
    """
    start_index = page * page_size
    end_index = start_index + page_size

    # Display the current page of matches
    for i in range(start_index, min(end_index, len(top_matches))):
        race_id, score, _ = top_matches[i]
        print(f"  {i + 1}: {race_id} (Score: {score:.2f})")

    print("\nOptions:")
    print("  - Enter comma-separated numbers to select matches (e.g., 1, 3, 5)")
    print("  - Press [Enter] to see more suggestions")
    print("  - Enter 0 to skip this file")

    raw_input = input("Your choice: ")

    if raw_input.strip() == "":  # User wants more suggestions
        page += 1
        if page * page_size >= len(top_matches):
            print("No more suggestions available.")
            page -= 1  # Do not advance past the end

    return raw_input, page


def _process_user_choice(
    raw_input: str,
    top_matches: List[Tuple[str, float, int]],
    path: str,
    match_results: MatchResults,
) -> bool:
    """
    Processes the user's choice for fuzzy matching.

    Args:
        raw_input (str): The raw input from the user.
        top_matches (List[Tuple[str, float, int]]): Top fuzzy matches.
        path (str): The filepath of the file being matched.
        match_results (MatchResults): An object holding the lists for matched,
                                    unmatched, and logged results.

    Returns:
        bool: True if the loop for the current file should break, False otherwise.
    """
    try:
        if raw_input.strip() == "0":
            match_results.still_unmatched.append(path)
            print(f"Skipped file: {os.path.basename(path)}")
            return True

        choices = [int(c.strip()) for c in raw_input.split(",")]

        if any(c < 1 or c > len(top_matches) for c in choices):
            print(
                "Invalid choice. Please enter numbers between 1 and "
                f"{len(top_matches)}."
            )
            return False

        for choice in choices:
            chosen_race_id = top_matches[choice - 1][0]
            match_results.newly_matched.append(
                {"filepath": path, "race_id": chosen_race_id}
            )
            match_results.manual_matches_log.append(f"{path},{chosen_race_id}")
            print(f"  -> Match recorded: {os.path.basename(path)} -> {chosen_race_id}")
        return True  # Exit the while loop for this file

    except ValueError:
        print("Invalid input. Please enter numbers, or press Enter.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return True


def match_elections_fuzzy(
    unmatched_filepaths: List[str], race_ids: List[str]
) -> Tuple[List[Dict], List[str]]:
    """
    Performs interactive fuzzy matching for unmatched files against a given
    list of RaceIDs, allowing for multiple selections.

    Args:
        unmatched_filepaths (List[str]): Files that failed exact matching.
        race_ids (List[str]): The list of possible RaceIDs for this category.

    Returns:
        A tuple containing a list of newly matched races and a list of files
    that remain unmatched.
    """
    match_results = MatchResults(
        newly_matched=[], still_unmatched=[], manual_matches_log=[]
    )

    if not unmatched_filepaths:
        return match_results.newly_matched, match_results.still_unmatched

    print("\n--- Starting Interactive Fuzzy Matching ---")
    for path in unmatched_filepaths:
        filename = os.path.splitext(os.path.basename(path))[0]
        top_matches = process.extract(filename, race_ids, scorer=fuzz.WRatio, limit=15)

        print(f"\nFile: {os.path.basename(path)}")
        print("Could not find an exact match. Here are the best suggestions:")

        page = 0
        while True:
            raw_input, page = _get_user_fuzzy_match_choice(top_matches, page, 5)

            if raw_input.strip() == "":  # More suggestions already handled
                continue

            if _process_user_choice(
                raw_input,
                top_matches,
                path,
                match_results,
            ):
                break

    if match_results.manual_matches_log:
        log_path = os.path.join(PROCESSED_DATA_DIR, "manual_matches.log")
        # Append to the log file
        with open(log_path, "a") as f:
            if f.tell() == 0:  # Write header if file is new/empty
                f.write("# Manual matches chosen by the user\n")
                f.write("filepath,race_id\n")
            for entry in match_results.manual_matches_log:
                f.write(f"{entry}\n")
        print(f"\nManual matches logged at: {log_path}")

    return match_results.newly_matched, match_results.still_unmatched


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

        # Get all possible RaceIDs for this election type first
        race_ids_for_type = get_race_ids(metadata_path)

        matched, unmatched = match_elections_exact(metadata_path, data_path)

        # If there are unmatched files, try fuzzy matching them
        if unmatched:
            print(f"Found {len(unmatched)} files needing manual review.")
            fuzzy_matched, still_unmatched = match_elections_fuzzy(
                unmatched, race_ids_for_type
            )
            matched.extend(fuzzy_matched)
            unmatched = still_unmatched  # Update unmatched list

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
                "# The following files from data/raw could not be automatically "
                "matched to a RaceID.\n"
            )
            for filepath in all_unmatched_files:
                f.write(f"{filepath}\n")
        print(f"Log of unmatched files saved at: {log_path}")
    else:
        print("No unmatched files found.")

    print("\n--- Data Processing Complete ---")


if __name__ == "__main__":
    main()
