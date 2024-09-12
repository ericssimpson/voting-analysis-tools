import os
import zipfile
import requests

def download_and_unzip(dataset_id, destination_folder):
    """
    Downloads and unzips a dataset from the Harvard Dataverse.
    """
    # Construct the URL for the dataset
    url = f"https://dataverse.harvard.edu/api/access/dataset/:persistentId/?persistentId={dataset_id}"

    # Create the destination folder if it doesn't exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Download the dataset
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        zip_path = os.path.join(destination_folder, "dataverse_files.zip")
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)

        # Unzip the dataset
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(destination_folder)

        # Remove the zip file
        os.remove(zip_path)

        print(f"Dataset {dataset_id} downloaded and unzipped successfully.")
    else:
        print(f"Failed to download dataset {dataset_id}. Status code: {response.status_code}")

if __name__ == "__main__":
    # The persistent IDs for the datasets
    dataset_ids = [
        "doi:10.7910/DVN/04LOQX",
        "doi:10.7910/DVN/AMK8PJ",
        "doi:10.7910/DVN/STVUET"
    ]

    # The destination folder for the data
    data_folder = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

    # Download and unzip each dataset
    for ds_id in dataset_ids:
        download_and_unzip(ds_id, data_folder)
