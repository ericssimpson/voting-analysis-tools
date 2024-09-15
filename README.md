# Voting Analysis Tools

Scripts and notebooks for analyzing and understanding electoral reforms.

## Project Setup

This project uses [Poetry](https://python-poetry.org/) for dependency management and to ensure a reproducible environment. Follow these steps to get started:

### 1. Prerequisites

Ensure you have Poetry installed. You can find installation instructions on the [official website](https://python-poetry.org/docs/#installation).

### 2. Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ericssimpson/voting-analysis-tools.git
    cd voting-analysis-tools
    ```

2.  **Install dependencies:**
    Poetry will create a virtual environment in the project's root and install all the necessary packages listed in `pyproject.toml`.
    ```bash
    poetry install
    ```

## Running the Data Pipeline

Once the setup is complete, you can run the data pipeline scripts. It's recommended to run these commands from within the Poetry-managed environment.

1.  **Activate the virtual environment:**
    ```bash
    poetry shell
    ```

2.  **Run the scripts sequentially:**
    First, download the raw data from the various sources.
    ```bash
    python scripts/download_data.py
    ```
    Next, process the raw data to create the unified elections database.
    ```bash
    python scripts/process_data.py
    ```

    After these scripts complete, you will have the raw data in `data/raw` and the processed database in `data/processed`.

## Working with Notebooks

To ensure the Jupyter notebooks use the correct project environment, you need to point to the Poetry environment.



*NOTE: This README is a work in progress...*