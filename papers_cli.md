# Papers Progress CLI

The **Papers Progress CLI** is a command-line tool that helps you track your reading progress on academic papers. It reads an input YAML file (`papers.yml`) containing your papers (and their related papers) and produces a flattened progress file (`papers_progress.yml`) where each paper is assigned a unique ID and its reading progress is tracked. You can update the status, set the current page you're on, list papers, download PDFs, and more-all using simple subcommands.

Run any command through `uv run` so dependencies are picked up from the project's locked environment (run `uv sync` first, or let `uv run` create the environment on demand):
```bash
uv run papers_cli.py init
```
All examples below assume the `uv run ` prefix (or that you have activated the `.venv` via `source .venv/bin/activate`).

## Features

- **Flattened Paper List:** Related papers are included as separate entries.
- **Unique IDs:** Each paper is assigned a unique numeric ID.
- **Status Tracking:** Track papers with statuses:
  - "not started" (alias: **ns**)
  - "in progress" (alias: **ip**)
  - "read" (alias: **d**)
- **Current Page Tracking:** Record the current page you are at in a paper using the `--page` option.
- **PDF Download:** Download the PDF of any paper using its URL.
- **Easy CLI:** Update, list, and reset your paper progress via subcommands.

## Requirements

- **Python >=3.12**
- **uv** manages dependencies (pyyaml, requests, python-slugify) automatically via `pyproject.toml` / `uv.lock`.

Install uv once (any one of these):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # standalone installer (recommended)
# or
pip install --user uv
# or (with mise)
mise use -g uv@latest
```

## Installation

1. Save the updated CLI script as `papers_cli.py` in your project directory.
2. Place your `papers.yml` file (which contains your list of papers) in the same directory.
3. (Optional) Make the script executable:
   ```bash
   chmod +x papers_cli.py
   ```
4. Sync dependencies (creates a local `.venv` and installs everything from the lockfile):
  ```bash
  uv sync
  ```

## Usage

Run the CLI program from the command line. The tool supports the following subcommands:

### 1. Initialization

This command reads `papers.yml`, flattens the structure to include related papers as separate entries, assigns unique IDs, and initializes each paper’s progress to "not started" (with a cleared current page).

```bash
python papers_cli.py init
```

If `papers_progress.yml` already exists, the command will notify you and leave it intact.

### 2. Reset Progress

Reset the progress for all papers back to "not started" and clear any start date, finish date, and current page information.

```bash
python papers_cli.py reset
```

### 3. Setting a Paper's Status and Current Page

Update the reading status of a paper by its unique ID. You can use full status names or their aliases:

- **not started** or **ns**
- **in progress** or **ip**
- **read** or **d**

In addition, you can set the current page you're on by providing the `--page` option (an integer).

Examples:

Mark paper ID 3 as "in progress" (alias `ip`), set the start date, and record that you are on page 42:
```bash
python papers_cli.py set --id 3 --status ip --start_date 2025-03-30 --page 42
```

Mark paper ID 2 as "read" (alias `d`), with a finished date:
```bash
python papers_cli.py set --id 2 --status d --finished_date 2025-03-30
```

### 4. Listing Papers

List papers along with their progress details. The output will include the paper's ID, title, progress status, start date, finished date, and the current page (if set). You can optionally filter by status, using either the full status or its alias.

List all papers:
```bash
python papers_cli.py list
```

List only papers that are "in progress" (alias `ip`):
```bash
python papers_cli.py list --status ip
```

### 5. Downloading PDFs

The `download` subcommand does two things:

**Download every PDF (bulk)** into `papers/<topic>/<title>.pdf`, organized by each paper's first topic. Related papers inherit their parent's topic. Links are deduped, already-downloaded files are skipped, and fetches use browser headers + a referer fallback so hosts that block hotlinking still work. Responses that aren't actually PDFs (HTML login walls / interstitials) are detected and reported rather than saved as fake PDFs.
```bash
./papers_cli.py download all        # bulk download; default target is 'all'
./papers_cli.py download            # shorthand for 'download all'
./papers_cli.py download all -j 8   # 8 parallel workers (default 6)
```
At the end it writes `papers/index.md` (a topic-grouped list of what succeeded) and `papers/failed.md` (WARN + FAIL entries with the URL and reason). Re-running skips files already on disk, so it's safe to resume.

**Download one PDF** by its paper ID, saved to the current directory as `<title>.pdf`:
```bash
./papers_cli.py download 3          # by positional ID
./papers_cli.py download --id 3    # equivalent (kept for back-compat)
```

Note: links on `dl.acm.org` (the ACM Digital Library) return HTTP 403 to non-JavaScript clients, so they will show up in `papers/failed.md`. This is a known limitation of any CLI downloader; those papers need a browser (or a JS-enabled fetch). Every other reachable host downloads fine.

## Commands Overview

- **init**:  
  Initializes `papers_progress.yml` from `papers.yml`. It flattens the papers (including related papers), assigns unique IDs, and sets the default progress (with current page cleared).

- **reset**:  
  Resets the progress of every paper to "not started", clearing the start date, finish date, and current page.

- **set**:  
  Updates the status for a paper using its ID. Accepts optional parameters:
  - `--start_date` for "in progress" or "read" statuses (defaults to today if not provided).
  - `--finished_date` for "read" status (defaults to today if not provided).
  - `--page` for the current page number.
    Supports status aliases: `ns` (not started), `ip` (in progress), and `d` (read).

- **list**:  
  Lists the papers with all progress information, including current page. You can filter the list by status using either full names or aliases.

- **download**:  
  `download all` (the default) bulk-downloads every PDF in `papers.yml` into `papers/<topic>/<title>.pdf`, dedupes by link, skips files already on disk, retries with a referer fallback, and writes `papers/index.md` + `papers/failed.md`. `download <id>` (or `download --id <id>`) downloads a single paper to the current directory. Parallelism via `--jobs` (default 6). Replaces the old `download_papers.sh`.

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
- **Paper Metadata:** Standard metadata from the original entry (and for related papers, an optional `parent_title`).
- **Progress Dictionary:** Contains:
  - `status`: "not started", "in progress", or "read"
  - `start_date`: The date when reading began.
  - `finished_date`: The date when reading was completed.
  - `current_page`: The current page you are on (if set).

## Troubleshooting

- **Missing Dependencies:**  
  If you encounter a `ModuleNotFoundError`, run `uv sync` (or prefix the command with `uv run `) so the project's locked environment is used.
- **File Not Found:**  
  Verify that `papers.yml` is in the same directory as `papers_cli.py`.
- **Invalid Status:**  
  When using the `set` command, ensure you use one of the allowed statuses or their aliases: `not started`/`ns`, `in progress`/`ip`, or `read`/`d`.
- **Invalid Page Number:**  
  Ensure the value passed to `--page` is a valid integer.
