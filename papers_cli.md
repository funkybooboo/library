# Papers Progress CLI

The **Papers Progress CLI** is a command-line tool that helps you track your reading progress on academic papers. It reads an input YAML file (`papers.yml`) that contains your papers (and their related papers) and produces a flattened progress file (`papers_progress.yml`) where each paper is given a unique ID and its reading progress is tracked. You can update the status, list papers, download PDFs, and more—all using simple subcommands.

## Features

- **Flattened Paper List:** Related papers are included as separate entries.
- **Unique IDs:** Each paper is assigned a unique numeric ID.
- **Status Tracking:** Track papers with statuses:
    - "not started" (alias: **ns**)
    - "in progress" (alias: **ip**)
    - "read" (alias: **d**)
- **PDF Download:** Download the PDF of any paper using its URL.
- **Easy CLI:** Update, list, and reset your paper progress via subcommands.

## Requirements

- **Python 3.6+**
- **PyYAML:** Install with:
  ```bash
  pip install pyyaml
  ```
- **Requests:** Install with:
  ```bash
  pip install requests
  ```

## Installation

1. Save the updated CLI script as `papers_cli.py` in your project directory.
2. Place your `papers.yml` file (which contains your list of papers) in the same directory.
3. (Optional) Make the script executable:
   ```bash
   chmod +x papers_cli.py
   ```

## Usage

Run the CLI program from the command line. The tool supports the following subcommands:

### 1. Initialization

This command reads `papers.yml`, flattens the structure to include related papers as separate entries, assigns unique IDs, and initializes each paper’s progress to "not started."

```bash
python papers_cli.py init
```

If `papers_progress.yml` already exists, the command will notify you and leave it intact.

### 2. Reset Progress

Reset the progress for all papers back to "not started" and clear any start or finish dates.

```bash
python papers_cli.py reset
```

### 3. Setting a Paper's Status

Update the reading status of a paper by its unique ID. You can use full status names or their aliases:

- **not started** or **ns**
- **in progress** or **ip**
- **read** or **d**

You can also supply optional dates:
- `--start_date YYYY-MM-DD` for starting a paper or marking it as in progress/read.
- `--finished_date YYYY-MM-DD` for marking a paper as read.

Examples:

Mark paper ID 3 as "in progress" using the alias `ip`:
```bash
python papers_cli.py set --id 3 --status ip --start_date 2025-03-30
```

Mark paper ID 2 as "read" using the alias `d`:
```bash
python papers_cli.py set --id 2 --status d --finished_date 2025-03-30
```

### 4. Listing Papers

List papers along with their progress details. You can optionally filter by status.

List all papers:
```bash
python papers_cli.py list
```

List only papers that are "not started":
```bash
python papers_cli.py list --status "not started"
```

### 5. Downloading PDFs

Download the PDF for a paper using its unique ID. The tool will fetch the PDF from the paper's link and save it using a sanitized version of the paper’s title.

Example:
```bash
python papers_cli.py download --id 3
```

If the paper has a valid URL, the PDF will be downloaded into the current directory.

## YAML File Structure

### Input File (`papers.yml`)

This file should contain an array of paper objects. Each object may include keys such as:
- `title`
- `author`
- `year`
- `link`
- `topics` (optional)
- `related` (optional, a list of related paper objects)

Example snippet:
```yaml
- title: Von Neumann's First Computer Program
  author: Knuth
  year: 1970
  link: https://dl.acm.org/doi/pdf/10.1145/356580.356581
  topics: [Computer History, Early Programming]
  related:
    - title: The Education of a Computer
      author: Hopper
      year: 1952
      link: https://example.com/related.pdf
```

### Generated Progress File (`papers_progress.yml`)

After initialization, this file will contain a flattened list of all papers (including related papers) with additional fields:
- `id`: Unique numeric identifier.
- `progress`: A dictionary with:
    - `status`: "not started", "in progress", or "read"
    - `start_date`: Date when reading began.
    - `finished_date`: Date when reading was completed.
- For related papers, an optional `parent_title` field shows the title of the main paper.

## Troubleshooting

- **Missing Dependencies:**  
  If you encounter a `ModuleNotFoundError`, ensure PyYAML and Requests are installed:
  ```bash
  pip install pyyaml requests
  ```
- **File Not Found:**  
  Verify that `papers.yml` is in the same directory as `papers_cli.py`.
- **Invalid Status:**  
  When using the `set` command, ensure you use one of the allowed statuses or their aliases: `not started`/`ns`, `in progress`/`ip`, or `read`/`d`.
