"""
This script automates the download and extraction of voting data from various sources.

It performs two main tasks:
1.  Downloads and unzips datasets from the Harvard Dataverse.
2.  Downloads specific tabs from Google Sheets as CSV files.

The script is designed to be run from the command line and will place the downloaded
data into the appropriate subdirectories within the `data/raw` directory.

Usage:
    python download_data.py
"""

import os
import zipfile
import requests

# --- Constants and Configuration ---

# The base folder for all raw data
BASE_DATA_FOLDER = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

# A mapping of Harvard Dataverse persistent IDs to their destination subfolders.
HARVARD_DATAVERSE_SETS = {
    "doi:10.7910/DVN/STVUET": "rcv_proportional",
    "doi:10.7910/DVN/04LOQX": "rcv_sequential",
    "doi:10.7910/DVN/AMK8PJ": "rcv_single"
}

# A mapping of Google Sheet identifiers to their destination subfolders and the specific tabs to download.
GOOGLE_SHEETS_CONFIG = {
    "rcv_database": {
        "id": "1lU6viuXfay323Gl6zkH5itwmrUIUo9rAzalK_ntu-ZY",
        "tabs": [
            "About", "SingleWinnerRCV", "ProportionalRCV", "OtherMultiWinnerRCV",
            "Party RCV Use", "CandidateDetails", "Upcoming RCV Elections",
            "RCV Ballot Measures", "Data Directory", "Other Resources"
        ]
    },
    "rcv_used": {
        "id": "17hMetWAVvF5iFDcwikavl0pHtXyQ7jI31cFFgsa0k0w",
        "tabs": [
            "Full list", "Trimmed list for sharing", "By type breakdown",
            "List of States", "Totals by category (including potential)",
            "Totals by category (not including potential)"
        ]
    },
    "rcv_tabulation": {
        "id": "1JKTHia4iSNT16dhEOmsEtS0muisUgT3_1WD3PvIAoBU",
        "tabs": ["2023 update", "2021 Summary", "Old"]
    }
}

# --- Function Definitions ---

def download_and_unzip(persistent_id: str, dest_folder: str) -> None:
    """
    Downloads and unzips a dataset from the Harvard Dataverse.

    Args:
        persistent_id (str): The persistent identifier of the dataset.
        dest_folder (str): The local directory to save the unzipped data.
    """
    # Construct the API URL for the dataset
    url = f"https://dataverse.harvard.edu/api/access/dataset/:persistentId/?persistentId={persistent_id}"

    # Ensure the destination folder exists
    os.makedirs(dest_folder, exist_ok=True)

    print(f"Downloading dataset {persistent_id}...")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes

        zip_path = os.path.join(dest_folder, "dataverse_files.zip")
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Unzipping dataset {persistent_id}...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(dest_folder)

        # Clean up by removing the downloaded zip file
        os.remove(zip_path)

        print(f"Successfully downloaded and unzipped dataset {persistent_id} to {dest_folder}.")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading dataset {persistent_id}: {e}")
    except zipfile.BadZipFile:
        print(f"Error: The downloaded file for {persistent_id} is not a valid zip file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def download_google_sheet_tab(sheet_id: str, tab_name: str, dest_folder: str) -> None:
    """
    Downloads a specific tab from a Google Sheet as a CSV file.

    Args:
        sheet_id (str): The identifier of the Google Sheet.
        tab_name (str): The name of the tab to download.
        dest_folder (str): The local directory to save the CSV file.
    """
    # URL encode the tab name to handle spaces and other special characters
    encoded_tab_name = requests.utils.quote(tab_name)
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_tab_name}"

    # Ensure the destination folder exists
    os.makedirs(dest_folder, exist_ok=True)

    print(f"Downloading tab '{tab_name}' from sheet {sheet_id}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        if response.content:
            # Sanitize the tab name to create a safe filename
            safe_filename = "".join(c for c in tab_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
            file_path = os.path.join(dest_folder, f"{safe_filename}.csv")
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            
            print(f"Successfully downloaded tab '{tab_name}' to {file_path}.")
        else:
            print(f"Warning: No content for tab '{tab_name}' from sheet {sheet_id}. It might be empty.")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading tab '{tab_name}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Main Execution ---

def main():
    """
    Main function to orchestrate the data download process.
    """
    print("--- Starting Data Download Process ---")

    # Download and unzip each dataset from Harvard Dataverse
    print("\n--- Downloading Harvard Dataverse Datasets ---")
    for dataset_id, subfolder in HARVARD_DATAVERSE_SETS.items():
        dataset_folder = os.path.join(BASE_DATA_FOLDER, subfolder)
        download_and_unzip(dataset_id, dataset_folder)

    # Download each specified tab from each Google Sheet
    print("\n--- Downloading Google Sheets Tabs ---")
    for sheet_name, sheet_info in GOOGLE_SHEETS_CONFIG.items():
        print(f"\nProcessing Google Sheet: {sheet_name}")
        sheet_destination_folder = os.path.join(BASE_DATA_FOLDER, sheet_name)
        for tab in sheet_info["tabs"]:
            download_google_sheet_tab(sheet_info["id"], tab, sheet_destination_folder)
            
    print("\n--- Data Download Complete ---")

if __name__ == "__main__":
    main()
