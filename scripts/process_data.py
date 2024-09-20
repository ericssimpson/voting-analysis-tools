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
1.  `election_database.csv`: A master CSV file containing all successfully matched
    elections, linking each `RaceID` to its `metadata_csv_name` and the
    `election_csv_name` of the raw ballot data.
2.  `unmatched_files.csv`: A log CSV file listing all the raw data files that could
    not be matched to a `RaceID`.
3.  `manual_matches.csv`: A log CSV file that records any manual matches made by the
    user during the fuzzy matching process.

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
ELECTION_DB_FILENAME = "election_database.csv"
UNMATCHED_LOG_FILENAME = "unmatched_files.csv"
MANUAL_MATCHES_FILENAME = "manual_matches.csv"

# Defines the relationship between metadata files and the directories containing
# the corresponding raw ballot data.
ELECTION_SOURCES = {
    "proportional": ("ProportionalRCV.csv", "rcv_proportional"),
    "single": ("SingleWinnerRCV.csv", "rcv_single"),
    "sequential": ("OtherMultiWinnerRCV.csv", "rcv_sequential"),
}

# --- Function Definitions ---


def load_manual_matches(manual_matches_path: str) -> Dict[str, str]:
    """
    Loads the manually matched CSV data into a dictionary for quick lookups.

    Args:
        manual_matches_path (str): The path to the manual_matches.csv file.

    Returns:
        Dict[str, str]: A dictionary mapping election_csv_name to race_id.
    """
    if not os.path.exists(manual_matches_path):
        return {}
    try:
        df = pd.read_csv(manual_matches_path)
        # Ensure correct column names are used, handling potential errors
        if "election_csv_name" in df.columns and "race_id" in df.columns:
            return pd.Series(df.race_id.values, index=df.election_csv_name).to_dict()
        else:
            print(
                "Warning: manual_matches.csv is missing 'election_csv_name' or 'race_id' columns."
            )
            return {}
    except Exception as e:
        print(f"Error loading manual matches: {e}")
        return {}


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
            matched_races.append(
                {"election_csv_name": os.path.basename(path), "race_id": filename}
            )
        else:
            unmatched_filepaths.append(path)

    return matched_races, unmatched_filepaths


def match_elections_from_manual_log(
    filepaths: List[str], manual_matches: Dict[str, str]
) -> Tuple[List[Dict], List[str]]:
    """
    Matches files based on the pre-loaded manual_matches.csv log.

    Args:
        filepaths (List[str]): A list of filepaths to try matching.
        manual_matches (Dict[str, str]): The dictionary of known matches.

    Returns:
        A tuple containing a list of newly matched races and a list of files
        that remain unmatched.
    """
    matched_races = []
    unmatched_filepaths = []
    for path in filepaths:
        filename = os.path.basename(path)
        if filename in manual_matches:
            matched_races.append(
                {"election_csv_name": filename, "race_id": manual_matches[filename]}
            )
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


def _handle_fuzzy_match_for_file(
    path: str, top_matches: List[Tuple[str, int]]
) -> Tuple[List[Dict], bool]:
    """
    Handles the interactive fuzzy matching process for a single file.

    Args:
        path (str): The filepath being matched.
        top_matches (List[Tuple[str, int]]): A list of potential RaceID matches.

    Returns:
        A tuple containing a list of new matches and a boolean indicating if the
        file was skipped.
    """
    page = 0
    newly_matched_for_file = []
    was_skipped = False

    while True:
        raw_input, page = _get_user_fuzzy_match_choice(top_matches, page, 5)

        if raw_input.strip() == "":
            continue

        if raw_input.strip() == "0":
            print(f"Skipped file: {os.path.basename(path)}")
            was_skipped = True
            break

        try:
            choices = [int(c.strip()) for c in raw_input.split(",")]
            if any(c < 1 or c > len(top_matches) for c in choices):
                print(
                    "Invalid choice. Please enter numbers between 1 and "
                    f"{len(top_matches)}."
                )
                continue

            for choice in choices:
                chosen_race_id = top_matches[choice - 1][0]
                match_data = {
                    "election_csv_name": os.path.basename(path),
                    "race_id": chosen_race_id,
                }
                newly_matched_for_file.append(match_data)
                match_log_message = (
                    f"  -> Match recorded: {os.path.basename(path)} -> {chosen_race_id}"
                )
                print(match_log_message)
            break  # Exit after successful selection

        except ValueError:
            print("Invalid input. Please enter numbers separated by commas.")
            continue

    return newly_matched_for_file, was_skipped


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
    newly_matched = []
    still_unmatched = []
    manual_matches = []

    if not unmatched_filepaths:
        return newly_matched, still_unmatched

    print("\n--- Starting Interactive Fuzzy Matching ---")
    for path in unmatched_filepaths:
        filename = os.path.splitext(os.path.basename(path))[0]
        top_matches = process.extract(filename, race_ids, scorer=fuzz.WRatio, limit=15)

        print(f"\nFile: {os.path.basename(path)}")
        print("Could not find an exact match. Here are the best suggestions:")

        new_matches, skipped = _handle_fuzzy_match_for_file(path, top_matches)

        if skipped:
            still_unmatched.append(path)
        else:
            newly_matched.extend(new_matches)
            manual_matches.extend(new_matches)

    if manual_matches:
        log_path = os.path.join(PROCESSED_DATA_DIR, MANUAL_MATCHES_FILENAME)
        manual_matches_df = pd.DataFrame(manual_matches)

        # Check if file exists to append or write new
        try:
            existing_df = pd.read_csv(log_path)
            combined_df = pd.concat([existing_df, manual_matches_df], ignore_index=True)
            combined_df.drop_duplicates(inplace=True)
        except FileNotFoundError:
            combined_df = manual_matches_df

        combined_df.to_csv(log_path, index=False)
        print(f"\nManual matches saved to: {log_path}")

    return newly_matched, still_unmatched


# --- Main Execution ---


def main():
    """
    Main function to orchestrate the data processing pipeline.
    """
    print("--- Starting Data Processing ---")

    # Ensure the processed data directory exists
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    print(f"Processed data will be saved to: {PROCESSED_DATA_DIR}")

    # Load any existing manual matches to automate the process
    manual_matches_path = os.path.join(PROCESSED_DATA_DIR, MANUAL_MATCHES_FILENAME)
    manual_matches = load_manual_matches(manual_matches_path)
    if manual_matches:
        print(f"Loaded {len(manual_matches)} known manual matches.")

    all_matched_races = []
    all_unmatched_files = []

    # Process each defined election source
    for election_type, (metadata_filename, data_dirname) in ELECTION_SOURCES.items():
        print(f"\n--- Processing {election_type} elections ---")

        metadata_path = os.path.join(RAW_DATA_DIR, "rcv_database", metadata_filename)
        data_path = os.path.join(RAW_DATA_DIR, data_dirname)

        # Get all possible RaceIDs for this election type first
        race_ids_for_type = get_race_ids(metadata_path)

        # 1. Attempt exact filename match
        matched, unmatched = match_elections_exact(metadata_path, data_path)

        # 2. Attempt to match using the manual log
        if unmatched:
            logged_matches, unmatched = match_elections_from_manual_log(
                unmatched, manual_matches
            )
            matched.extend(logged_matches)

        # 3. For remaining files, try interactive fuzzy matching
        if unmatched:
            print(f"Found {len(unmatched)} files needing manual review.")
            fuzzy_matched, still_unmatched = match_elections_fuzzy(
                unmatched, race_ids_for_type
            )
            matched.extend(fuzzy_matched)
            unmatched = still_unmatched  # Update unmatched list

        # Add the metadata filename to the matched data for better traceability
        for race in matched:
            race["metadata_csv_name"] = metadata_filename

        all_matched_races.extend(matched)
        all_unmatched_files.extend(unmatched)

        print(f"Found {len(matched)} matched elections.")
        print(f"Found {len(unmatched)} unmatched files.")

    # Create and save the final election database
    if all_matched_races:
        elections_df = pd.DataFrame(all_matched_races)
        # Reorder columns for clarity
        elections_df = elections_df[
            ["race_id", "metadata_csv_name", "election_csv_name"]
        ]
        output_path = os.path.join(PROCESSED_DATA_DIR, ELECTION_DB_FILENAME)
        elections_df.to_csv(output_path, index=False)
        print(f"\nSuccessfully created election database at: {output_path}")
    else:
        print("\nNo matched elections found. The database file was not created.")

    # Create and save the log of unmatched files
    if all_unmatched_files:
        log_path = os.path.join(PROCESSED_DATA_DIR, UNMATCHED_LOG_FILENAME)
        unmatched_df = pd.DataFrame(
            {"election_csv_name": [os.path.basename(p) for p in all_unmatched_files]}
        )
        unmatched_df.to_csv(log_path, index=False)
        print(f"Log of unmatched files saved at: {log_path}")
    else:
        print("No unmatched files found.")

    print("\n--- Data Processing Complete ---")


if __name__ == "__main__":
    main()
