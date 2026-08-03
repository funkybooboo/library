# Papers CLI (`papers-cli`)

A tiny tool to download and open the academic papers listed in `papers.yml`. Two commands, that's it.

```bash
./papers-cli download          # bulk-download every PDF -> papers/<topic>/
./papers-cli open failed       # open the ones that failed (ACM/Cloudflare) in your browser
./papers-cli open all          # open every paper link URL in your browser
./papers-cli open downloaded   # open the papers/ folder in your file manager
```

## Requirements

- **uv** -- the only prerequisite. `papers-cli` is self-contained: its Python deps (`pyyaml`, `requests`) are declared in a PEP 723 inline `# /// script` block at the top of the file, so uv provisions an isolated environment automatically on first run (cached under `~/.cache/uv`). No virtualenv, no `pip install`, no lockfile.

Install uv once (any one):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # standalone installer (recommended)
# or
pip install --user uv
# or (with mise)
mise use -g uv@latest
```

## Installation

```bash
git clone <this-repo> && cd library
chmod +x papers-cli   # already executable in the repo
./papers-cli download  # uv provisions deps on first run
```

The CLI is the extensionless `papers-cli` (uses a `#!/usr/bin/env -S uv run --script` shebang so uv reads its inline metadata and provisions deps). Run it from the repo root so `papers.yml` is in the current directory.

## Commands

### `download` -- bulk-download every PDF

Downloads every PDF in `papers.yml` into `papers/<topic>/<title>.pdf`, organized by each paper's first topic (related papers inherit their parent's topic). Links are deduped, files already on disk are skipped, and fetches use browser headers plus a referer fallback so hosts that block hotlinking still work. Responses that aren't actually PDFs (HTML login walls / interstitials) are detected and reported rather than saved as fake PDFs.
```bash
./papers-cli download          # 6 parallel workers (default)
./papers-cli download -j 8     # 8 parallel workers
```
Re-running skips files already on disk, so it's safe to resume. When it finishes it writes:
- `papers/index.md` -- a topic-grouped list of what succeeded.
- `papers/failed.md` -- the `WARN` + `FAIL` entries with URL and reason.

**ACM/Cloudflare caveat:** links on `dl.acm.org` sit behind Cloudflare's "Just a moment..." JavaScript challenge, so any CLI downloader gets HTTP 403. Those papers appear in `papers/failed.md`; use `./papers-cli open failed` (below) to fetch them in your browser.

### `open` -- launch URLs/files in your browser or file manager

Three targets (default: `failed`):

**`open failed`** parses `papers/failed.md` and opens every failed URL in your browser in small batches. A real browser solves the Cloudflare JS challenge and, for any paywalled ones your institution entitles you to, carries the access session.
```bash
./papers-cli open failed                 # default target
./papers-cli open failed --dry-run       # just list them
./papers-cli open failed --batch 10      # 10 tabs per batch (default 8)
./papers-cli open failed --pause 2       # seconds between batches (default 1.5)
./papers-cli open failed --file other.md # use a different failed.md
```

**`open all`** opens every paper link URL from `papers.yml` (flattened, deduped) -- useful for browsing the source pages directly.
```bash
./papers-cli open all
./papers-cli open all --dry-run
```

**`open downloaded`** opens the `papers/` folder in your file manager so you can browse the PDFs already on disk. Use `--topic` to open just one topic subdir.
```bash
./papers-cli open downloaded                       # open papers/
./papers-cli open downloaded --topic Computer_History  # just that subdir
./papers-cli open downloaded --dry-run
```

After you've manually saved some ACM PDFs into `papers/<topic>/`, re-running `./papers-cli download` will skip them (already on disk) and `open failed` will show a shorter list. To refresh `failed.md`, delete `papers/failed.md` and re-run `./papers-cli download`.

## Companion scripts

- **`gen_readme.py`** -- regenerate `README.md` from `papers.yml`. Run after editing `papers.yml`:
  ```bash
  ./gen_readme.py > README.md
  ```
- **`check_links.py`** -- audit that every link in `papers.yml` is reachable (HEAD, GET-on-405). Skips `.acm.org` links. Prints a per-paper result and exits `1` if any failed. Run before committing a `papers.yml` change:
  ```bash
  ./check_links.py
  ```

## YAML File Structure (`papers.yml`)

An array of paper objects. Each may include `title`, `author`, `year`, `link`, `topics` (optional list; the first is used as the download subdirectory), and `related` (optional list of related paper objects, which inherit the parent's topic).
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

## Troubleshooting

- **`ModuleNotFoundError`** -- you ran it with plain `python`/`python3` instead of through uv. Run it directly (`./papers-cli ...`) so the `uv run --script` shebang provisions the deps, or invoke `uv run --script papers-cli ...`.
- **`env: 'uv': No such file or directory`** -- uv isn't on `PATH`. Install it (see Requirements) or, with mise, ensure your shell loads the shims.
- **`open failed` says "No failed URLs recorded" though downloads failed** -- you need a current `papers/failed.md`. Run `./papers-cli download` first; it's written at the end.
- **File Not Found** -- run from the repo root so `papers.yml` is in the current directory.
- **Editing the inline metadata block** -- keep the `# /// script ... # ///` block intact, and make sure no prose comment in the file literally contains the string `# /// script` (uv's scanner mistakes it for a second metadata opener and provisioning silently fails).