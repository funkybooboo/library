# Papers CLI (`papers-cli`)

A command-line tool for tracking your reading progress on academic papers and downloading their PDFs. It reads `papers.yml` (the list of papers and their related papers), produces a flattened `papers_progress.yml` where each paper has a unique ID and tracked progress, and can bulk-download every PDF.

## Quick reference

```bash
./papers-cli init                          # build papers_progress.yml (assigns IDs)
./papers-cli list [--status ip]            # list papers / filter by status
./papers-cli set --id 3 --status ip --page 42   # update one paper's progress
./papers-cli download                      # bulk-download all PDFs -> papers/<topic>/
./papers-cli download 3                    # download one paper by ID -> cwd/
./papers-cli open failed                   # open failed URLs in your browser (ACM/Cloudflare)
./papers-cli open all                      # open every paper link URL in your browser
./papers-cli open downloaded [--topic X]    # open papers/ (or one topic) in your file manager
./check_links.py                           # audit every link is reachable (CI-friendly)
./gen_readme.py > README.md                # regenerate README from papers.yml (run after edits)
```

## Requirements

- **uv** -- the only prerequisite. Each script is self-contained: its Python dependencies (`pyyaml`, `requests`) are declared in a PEP 723 inline `# /// script` block at the top of the file, so uv provisions an isolated environment automatically the first time you run it (cached under `~/.cache/uv`). No virtualenv, no `pip install`, no `pyproject.toml`/lockfile to maintain.

Install uv once (any one):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # standalone installer (recommended)
# or
pip install --user uv
# or (with mise)
mise use -g uv@latest
```

## Installation

1. Clone this repo and `cd` into it.
2. Make the scripts executable (they already ship with the executable bit):
   ```bash
   chmod +x papers-cli gen_readme.py check_links.py
   ```
3. Run any command -- uv will provision the deps on first use.

Run from the repo root. The CLI is the extensionless `papers-cli` (it uses a `#!/usr/bin/env -S uv run --script` shebang so uv reads its inline metadata). The other two tools (`gen_readme.py`, `check_links.py`) keep the `.py` extension and a plain `uv run` shebang.

## Usage

```bash
./papers-cli <command> [options]
```

### 1. Initialize progress tracking

Reads `papers.yml`, flattens it (related papers become their own entries), assigns each paper a unique numeric ID, and sets progress to "not started" with a cleared current page. If `papers_progress.yml` already exists it is left intact.
```bash
./papers-cli init
```

### 2. Reset progress

Reset every paper back to "not started", clearing start/finish dates and current page.
```bash
./papers-cli reset
```

### 3. Set a paper's status and current page

Update a paper by its ID. Statuses and their aliases:
- **not started** / `ns`
- **in progress** / `ip`
- **read** / `d`

`--start_date` defaults to today for `ip`/`read`; `--finished_date` defaults to today for `read`; `--page` sets the current page.

```bash
# Mark paper #3 in-progress, on page 42
./papers-cli set --id 3 --status ip --page 42

# Mark paper #2 read, finished 2025-03-30
./papers-cli set --id 2 --status d --finished_date 2025-03-30
```

### 4. List papers

List every paper with its ID, title, status, dates, and current page. Filter by status (full name or alias) with `--status`.
```bash
./papers-cli list
./papers-cli list --status ip
```

### 5. Download PDFs

The `download` subcommand does two jobs:

**Bulk download** -- every PDF in `papers.yml` into `papers/<topic>/<title>.pdf`, organized by each paper's first topic (related papers inherit their parent's topic). Links are deduped, already-downloaded files are skipped, and fetches use browser headers plus a referer fallback so hosts that block hotlinking still work. Responses that aren't actually PDFs (HTML login walls / interstitials) are detected and reported rather than saved as fake PDFs.
```bash
./papers-cli download all        # bulk; 'all' is the default target
./papers-cli download            # shorthand for 'download all'
./papers-cli download all -j 8   # 8 parallel workers (default 6)
```
At the end it writes `papers/index.md` (a topic-grouped list of successes) and `papers/failed.md` (the `WARN` + `FAIL` entries with URL and reason). Re-running skips files already on disk, so it's safe to resume.

**Single download** -- one PDF by paper ID, saved to the current directory as `<title>.pdf`:
```bash
./papers-cli download 3          # by positional ID
./papers-cli download --id 3     # equivalent form
```

Note: links on `dl.acm.org` (the ACM Digital Library) sit behind Cloudflare's "Just a moment..." JavaScript challenge, so any CLI downloader gets HTTP 403. These papers appear in `papers/failed.md`; use `./papers-cli open failed` (see section 6) to fetch them in your browser.

### 6. Open URLs/files in your browser

The `open` command launches things in your default browser or file manager. Three targets:

**`open failed`** (the default) parses `papers/failed.md` and opens every failed URL in your browser in small batches. This is the way to get the ACM/Cloudflare-gated papers: a real browser solves the JS challenge, and for any paywalled ones your institution entitles you to, your browser session carries the access.
```bash
./papers-cli open failed                 # default target; open every failed URL
./papers-cli open failed --dry-run       # just list them
./papers-cli open failed --batch 10      # open 10 tabs per batch (default 8)
./papers-cli open failed --pause 2       # seconds between batches (default 1.5)
./papers-cli open failed --file other.md # use a different failed.md
```

**`open all`** opens every paper link URL from `papers.yml` (flattened, deduped) in your browser -- useful for browsing the source pages directly.
```bash
./papers-cli open all
./papers-cli open all --dry-run
```

**`open downloaded`** opens the `papers/` folder in your file manager so you can browse the PDFs already on disk. Use `--topic` to open a single topic subdir.
```bash
./papers-cli open downloaded                       # open papers/ in file manager
./papers-cli open downloaded --topic Computer_History  # just that subdir
./papers-cli open downloaded --dry-run
```
Tip: to open a single PDF, double-click it in your file manager, or run `xdg-open papers/<topic>/<title>.pdf`.

After you've manually saved some ACM PDFs into `papers/<topic>/`, re-running `./papers-cli download` will skip them (already on disk) and `open failed` will show a shorter list. To refresh `failed.md`, delete `papers/failed.md` and re-run `./papers-cli download`.

## Commands Overview

- **init** -- Initialize `papers_progress.yml` from `papers.yml`: flatten (including related papers), assign IDs, default progress.
- **reset** -- Reset all progress to "not started", clearing dates and current page.
- **set** -- Update a paper's status by ID. Options: `--status`, `--start_date`, `--finished_date`, `--page`. Aliases: `ns`, `ip`, `d`.
- **list** -- List papers and progress; `--status` filters (full name or alias).
- **download** -- `download all` (default) bulk-downloads every PDF into `papers/<topic>/<title>.pdf`, dedupes by link, skips files on disk, retries with a referer fallback, and writes `papers/index.md` + `papers/failed.md`. `download <id>` (or `download --id <id>`) downloads one paper to the current directory. `--jobs`/`-j` sets parallelism (default 6).
- **open** -- `open failed` (default) opens failed.md URLs in your browser; `open all` opens every paper link URL from `papers.yml`; `open downloaded` opens the `papers/` folder in your file manager (`--topic` narrows to a subdir). URL opens are batched (`--batch`/`--pause`); `--dry-run` lists without launching. The path for ACM/Cloudflare-gated papers a CLI can't fetch.

## Companion scripts

- **`gen_readme.py`** -- regenerate `README.md` from `papers.yml`. Run after editing `papers.yml`:
  ```bash
  ./gen_readme.py > README.md
  ```
- **`check_links.py`** -- audit that every link in `papers.yml` is reachable (HEAD, GET-on-405). Skips `.acm.org` links (ACM needs JS). Prints a per-paper result and exits `1` if any failed. Run it before committing a `papers.yml` change to catch dead/typo'd URLs:
  ```bash
  ./check_links.py
  ```

## YAML File Structure

### Input (`papers.yml`)

An array of paper objects. Each may include:
- `title`, `author`, `year`, `link`
- `topics` (optional, a list; the first topic is used as the download subdirectory)
- `related` (optional, a list of related paper objects)

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

### Generated (`papers_progress.yml`)

After `init`, this contains the flattened list (including related papers, each with an optional `parent_title`) plus:
- `id`: unique numeric identifier.
- **Progress dict**: `status` ("not started" / "in progress" / "read"), `start_date`, `finished_date`, `current_page`.

## Troubleshooting

- **`ModuleNotFoundError`** -- you're running the script with plain `python`/`python3` instead of through uv. Run it directly (`./papers-cli ...`) so the `uv run --script` shebang provisions the deps, or invoke `uv run --script papers-cli ...`.
- **`env: 'uv': No such file or directory`** -- uv isn't on `PATH`. Install it (see Requirements) or, with mise, ensure your shell loads the shims.
- **`uv run was recursively invoked ...` (shebang) on a renamed/extensionless copy** -- the inline `# /// script` block is what tells uv this is a self-contained script. Keep that block intact, and make sure no prose comment in the file literally contains the string `# /// script` (uv's scanner will mistake it for a second metadata opener and fail to provision).
- **`open failed` says "No failed URLs recorded" even though downloads failed** -- you need a current `papers/failed.md`. Run `./papers-cli download` first; the file is written at the end of a bulk download.
- **File Not Found** -- run from the repo root so `papers.yml` is in the current directory.
- **Invalid Status / Invalid Page** -- `set` accepts only `ns`/`ip`/`d` (or the full names), and `--page` must be an integer.