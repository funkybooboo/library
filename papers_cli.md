# Papers CLI

The **Papers CLI** is a command-line tool that helps you track your reading progress on academic papers. It uses a base YAML file (`papers.yml`) containing the paper metadata and creates a progress file (`papers_progress.yml`) that tracks whether each paper is "not started", "in progress", or "read", along with corresponding start and finish dates. Each paper is assigned a unique numeric ID for easy reference.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
    - [Initializing the Progress File](#initializing-the-progress-file)
    - [Resetting Progress](#resetting-progress)
    - [Setting a Paper’s Status](#setting-a-papers-status)
    - [Listing Papers](#listing-papers)
- [Commands Overview](#commands-overview)
- [Examples](#examples)
- [YAML File Structure](#yaml-file-structure)
- [Troubleshooting](#troubleshooting)

## Requirements

- **Python 3.6+**: The CLI script is written in Python.
- **PyYAML**: To handle YAML parsing. Install it using pip:
  ```bash
  pip install pyyaml
  ```

## Installation

1. Save the CLI script as `papers_cli.py` in your project directory.
2. Ensure your `papers.yml` file (with the list of papers) is present in the same directory.
3. Make the script executable (optional):
   ```bash
   chmod +x papers_cli.py
   ```

## Usage

Run the CLI program from the command line. The program supports several sub-commands:

### Initializing the Progress File

Before tracking your progress, initialize the progress file from your `papers.yml`. This command assigns unique IDs to each paper and sets the default progress state.

```bash
python papers_cli.py init
```

If `papers_progress.yml` already exists, the command will inform you instead of overwriting it.

### Resetting Progress

To reset the progress of all papers to "not started", use the reset command:

```bash
python papers_cli.py reset
```

This sets the progress status of every paper to "not started" and clears any start or finish dates.

### Setting a Paper’s Status

Update the progress status for a paper by its ID. The CLI supports three statuses: `not started`, `in progress`, and `read`.

- **In Progress**: Records the start date (defaults to today if not provided).
- **Read**: Records the finished date (defaults to today if not provided) and sets a start date if none exists.

Usage:

```bash
python papers_cli.py set --id <paper_id> --status "<status>" [--start_date YYYY-MM-DD] [--finished_date YYYY-MM-DD]
```

Example (mark paper ID 3 as in progress):

```bash
python papers_cli.py set --id 3 --status "in progress" --start_date 2025-03-30
```

Example (mark paper ID 2 as read):

```bash
python papers_cli.py set --id 2 --status "read" --finished_date 2025-03-30
```

### Listing Papers

List papers with an optional filter based on their progress status. If no filter is provided, the CLI lists all papers.

Usage:

```bash
python papers_cli.py list [--status "<status>"]
```

Example (list papers that haven't been started):

```bash
python papers_cli.py list --status "not started"
```

Example (list all papers):

```bash
python papers_cli.py list
```

## Commands Overview

- **init**:  
  Initializes `papers_progress.yml` from `papers.yml`, assigns unique IDs, and sets default progress.

- **reset**:  
  Resets the progress of all papers to "not started".

- **set**:  
  Updates the status of a specific paper using its ID. Accepts additional optional arguments for start and finish dates.

- **list**:  
  Lists papers and their progress. Optionally filter by progress status.

## Examples

1. **Initialize Progress File**
   ```bash
   python papers_cli.py init
   ```

2. **Mark Paper ID 4 as "in progress" with today's date as the start date**
   ```bash
   python papers_cli.py set --id 4 --status "in progress"
   ```

3. **Mark Paper ID 1 as "read" with a specific finished date**
   ```bash
   python papers_cli.py set --id 1 --status "read" --finished_date 2025-03-30
   ```

4. **List only papers that are "read"**
   ```bash
   python papers_cli.py list --status "read"
   ```

## YAML File Structure

### papers.yml (Input File)

This file contains an array of paper objects with keys like `title`, `author`, `year`, `link`, and optionally `topics` and `related` papers.

Example snippet:
```yaml
- title: Von Neumann's First Computer Program
  author: Knuth
  year: 1970
  link: https://example.com/paper.pdf
  topics: [Computer History, Early Programming]
  related:
    - title: The Education of a Computer
      author: Hopper
      year: 1952
      link: https://example.com/related.pdf
```

### papers_progress.yml (Generated Progress File)

After initialization, each paper will include:
- A unique `id`
- A `progress` dictionary with:
    - `status`: "not started", "in progress", or "read"
    - `start_date`: date when reading was started
    - `finished_date`: date when reading was completed

## Troubleshooting

- **PyYAML Not Installed**:  
  If you receive an error about the `yaml` module, install PyYAML:
  ```bash
  pip install pyyaml
  ```
- **File Not Found**:  
  Ensure that `papers.yml` is in the same directory as `papers_cli.py`.
- **Invalid Status**:  
  When using the `set` command, make sure the status is exactly one of: `"not started"`, `"in progress"`, or `"read"` (case insensitive).
