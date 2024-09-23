"""
This script generates a Markdown checklist for tracking the refactoring of files
from the /.archive directory into the main project structure.

The script performs the following tasks:
1.  Scans the `/.archive` directory recursively to find all files.
2.  For each file, it retrieves metadata from Git, including the last edit date
    and the total number of commits.
3.  It generates a `CHECKLIST.md` file in the `/.napkin` directory.
4.  If `CHECKLIST.md` already exists, it preserves the checked/unchecked state
    of each item to prevent losing progress.

The purpose of this checklist is to provide a clear and actionable overview of the
refactoring effort, ensuring that every file in the archive is reviewed and
either integrated into the new structure or explicitly marked as obsolete.

This script is intended to be a temporary tool to aid in project refactoring and
will remain in the `/.napkin` directory until it is no longer needed.

Usage:
    python .napkin/generate_checklist.py
"""

import os
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Tuple

# --- Constants and Configuration ---

# Determine the root directory of the project, which is one level up from the
# directory containing this script.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE_DIR = os.path.join(BASE_DIR, ".archive")
NAPKIN_DIR = os.path.join(BASE_DIR, ".napkin")
CHECKLIST_PATH = os.path.join(NAPKIN_DIR, "CHECKLIST.md")


# --- Data Structures ---


@dataclass
class GitFileInfo:
    """Holds all metadata for a file to be included in the checklist."""

    first_edit_date: str = "N/A"
    first_committer: str = "N/A"
    median_edit_date: str = "N/A"
    top_committer: str = "N/A"
    commit_count: int = 0
    line_count: int = 0
    file_size_kb: float = 0.0


# --- Function Definitions ---


def get_file_stats(file_path: str) -> Tuple[int, float]:
    """
    Gets the line count and file size for a given file.

    Args:
        file_path (str): The absolute path to the file.

    Returns:
        A tuple containing the line count and file size in kilobytes.
    """
    try:
        line_count = 0
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            line_count = len(f.readlines())
        file_size_kb = os.path.getsize(file_path) / 1024
        return line_count, file_size_kb
    except OSError:
        return 0, 0.0


def get_git_file_info(file_path: str) -> GitFileInfo:
    """
    Gets metadata for a file using Git, including commit history and file stats.

    Args:
        file_path (str): The absolute path to the file.

    Returns:
        A GitFileInfo object containing all collected metadata.
    """
    info = GitFileInfo()
    try:
        relative_path = os.path.relpath(file_path, BASE_DIR)

        # Get all commit dates and authors for calculating median date and top committer
        all_commits_str = subprocess.check_output(
            ["git", "log", "--follow", "--pretty=format:%cI,%an", "--", relative_path],
            cwd=BASE_DIR,
            text=True,
            encoding="utf-8",
            stderr=subprocess.PIPE,
        ).strip()

        if all_commits_str:
            commit_lines = all_commits_str.splitlines()
            info.commit_count = len(commit_lines)

            # Calculate median date
            dates = [
                datetime.fromisoformat(line.split(",", 1)[0]) for line in commit_lines
            ]
            dates.sort()
            median_date = dates[len(dates) // 2]
            info.median_edit_date = median_date.strftime("%Y-%m-%d")

            # Calculate top committer
            authors = [line.split(",", 1)[1] for line in commit_lines]
            if authors:
                info.top_committer = Counter(authors).most_common(1)[0][0]

        # Get first commit info (date and author)
        first_commit_str = subprocess.check_output(
            [
                "git",
                "log",
                "--diff-filter=A",
                "--follow",
                "--pretty=format:%cI,%an",
                "--",
                relative_path,
            ],
            cwd=BASE_DIR,
            text=True,
            encoding="utf-8",
            stderr=subprocess.PIPE,
        ).strip()
        if first_commit_str:
            first_commit_lines = first_commit_str.splitlines()
            if first_commit_lines:
                date_str, author = first_commit_lines[-1].split(",", 1)
                info.first_edit_date = datetime.fromisoformat(date_str).strftime(
                    "%Y-%m-%d"
                )
                info.first_committer = author

        # Get file line count and size
        info.line_count, info.file_size_kb = get_file_stats(file_path)

    except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as e:
        # This can happen for files not tracked by git, or other errors
        print(f"Warn: Could not get full git info for {file_path}. Error: {e}")

    return info


def preserve_checkbox_states(checklist_path: str) -> Dict[str, bool]:
    """
    Reads an existing checklist to preserve the state of checkboxes.

    Args:
        checklist_path (str): The path to the CHECKLIST.md file.

    Returns:
        A dictionary mapping the file path (relative to archive) to its checked state.
    """
    states = {}
    if not os.path.exists(checklist_path):
        return states

    try:
        with open(checklist_path, "r", encoding="utf-8") as f:
            for line in f:
                # Match checkboxes followed by a file path in backticks
                match = re.search(r"^\s*- \[(x| )\] `(.*?)`", line)
                if match:
                    is_checked = match.group(1).strip() == "x"
                    file_path_key = match.group(2)

                    # Handle directory entries, which end with a slash
                    if file_path_key.endswith("/"):
                        # Normalize by removing markdown and the trailing slash
                        file_path_key = file_path_key.replace("**", "").strip("/")

                    states[file_path_key] = is_checked
    except OSError as e:
        print(f"Error reading existing checklist: {e}")

    return states


# --- Main Execution ---


def main():
    """
    Main function to generate the Markdown checklist.
    """
    print("--- Generating Refactor Checklist ---")

    # Ensure the output directory exists
    os.makedirs(NAPKIN_DIR, exist_ok=True)

    # Preserve existing checkbox states to avoid losing work
    existing_states = preserve_checkbox_states(CHECKLIST_PATH)
    if existing_states:
        print(f"Loaded {len(existing_states)} existing states from checklist.")

    # Start the markdown content
    md_content = [
        "# Archive Refactoring Checklist",
        "",
        "This tracks the transfer of functionality from the `/.archive` directory.",
        "It is generated by `/.napkin/generate_checklist.py` and can be safely re-run.",
        "",
        "- `[ ]` - To Do",
        "- `[x]` - Done (Transferred/Refactored)",
        "",
        "## Checklist",
        "",
    ]

    # Walk through the archive directory
    for root, dirs, files in os.walk(ARCHIVE_DIR):
        # Skip hidden directories (e.g., .git)
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        dirs.sort()

        level = root.replace(ARCHIVE_DIR, "").count(os.sep)
        indent = "  " * (level - 1) if level > 0 else ""

        # Add directory header as a checkable item for better nesting
        relative_dir_path = os.path.relpath(root, ARCHIVE_DIR)
        if relative_dir_path != ".":
            dir_name = os.path.basename(root)
            is_checked = existing_states.get(dir_name, False)
            checkbox = "[x]" if is_checked else "[ ]"
            dir_item = f"{indent}- {checkbox} `{dir_name}/`"
            md_content.append(dir_item)

        # Indent files one level deeper than their parent directory
        file_indent = "  " * level

        # List files in the directory
        for file in sorted(files):
            # Skip hidden files
            if file.startswith("."):
                continue

            full_path = os.path.join(root, file)
            file_key = os.path.basename(full_path)
            relative_file_path = os.path.relpath(full_path, ARCHIVE_DIR)

            # Get all the rich metadata for the file
            info = get_git_file_info(full_path)

            # Get the checkbox state, default to unchecked
            is_checked = existing_states.get(relative_file_path, False)
            checkbox = "[x]" if is_checked else "[ ]"

            # Format the detailed checklist item
            details = (
                f"First: {info.first_edit_date} by {info.first_committer}, "
                f"Top: {info.top_committer}, Median Date: {info.median_edit_date}, "
                f"{info.commit_count} commits, "
                f"{info.line_count} lines, {info.file_size_kb:.2f} KB"
            )
            file_item = f"{file_indent}- {checkbox} `{file_key}` ({details})"
            md_content.append(file_item)

    # Write the new checklist content
    try:
        with open(CHECKLIST_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(md_content))
        print(f"Successfully generated checklist at: {CHECKLIST_PATH}")
    except OSError as e:
        print(f"Error writing checklist file: {e}")

    print("\n--- Checklist Generation Complete ---")


if __name__ == "__main__":
    main()
