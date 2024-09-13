import os
import zipfile
import requests

def download_and_unzip(persistent_id, dest_folder):
    """
    Downloads and unzips a dataset from the Harvard Dataverse.
    """
    # Construct the URL for the dataset
    url = f"https://dataverse.harvard.edu/api/access/dataset/:persistentId/?persistentId={persistent_id}"

    # Create the destination folder if it doesn't exist
    os.makedirs(dest_folder, exist_ok=True)

    # Download the dataset
    print(f"Downloading dataset {persistent_id}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        zip_path = os.path.join(dest_folder, "dataverse_files.zip")
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Unzip the dataset
        print(f"Unzipping dataset {persistent_id}...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(dest_folder)

        # Remove the zip file
        os.remove(zip_path)

        print(f"Dataset {persistent_id} downloaded and unzipped to {dest_folder}.")
    else:
        print(f"Failed to download dataset {persistent_id}. Status code: {response.status_code}")

def download_google_sheet_tab(sheet_id, tab_name, dest_folder):
    """
    Downloads a specific tab from a Google Sheet as a CSV.
    """
    # URL encode the tab name to handle spaces and other special characters
    encoded_tab_name = requests.utils.quote(tab_name)
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_tab_name}"

    # Create the destination folder if it doesn't exist
    os.makedirs(dest_folder, exist_ok=True)

    # Download the sheet
    print(f"Downloading tab '{tab_name}' from sheet {sheet_id}...")
    response = requests.get(url)
    if response.status_code == 200 and response.content:
        # Sanitize tab name for use as a filename
        safe_filename = "".join(c for c in tab_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
        file_path = os.path.join(dest_folder, f"{safe_filename}.csv")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"Tab '{tab_name}' downloaded successfully to {file_path}.")
    else:
        print(f"Failed to download tab '{tab_name}' from sheet {sheet_id}. Status: {response.status_code}. It might be an empty or invalid tab name.")

if __name__ == "__main__":
    # The base folder for the data
    base_data_folder = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

    # Map dataset persistent IDs to their destination subfolders
    datasets = {
        "doi:10.7910/DVN/STVUET": "rcv_proportional",
        "doi:10.7910/DVN/04LOQX": "rcv_sequential",
        "doi:10.7910/DVN/AMK8PJ": "rcv_single"
    }

    # Download and unzip each dataset into its respective folder
    for dataset_id, subfolder in datasets.items():
        dataset_folder = os.path.join(base_data_folder, subfolder)
        download_and_unzip(dataset_id, dataset_folder)

    # Define the Google Sheets and their tabs
    google_sheets = {
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

    # Download each tab from each Google Sheet
    for sheet_name, sheet_info in google_sheets.items():
        sheet_destination_folder = os.path.join(base_data_folder, sheet_name)
        for tab in sheet_info["tabs"]:
            download_google_sheet_tab(sheet_info["id"], tab, sheet_destination_folder)
