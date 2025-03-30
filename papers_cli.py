#!/usr/bin/env python3
import argparse
import datetime
import os
import re
import yaml
import requests

# File names
PAPERS_FILE = "papers.yml"
PROGRESS_FILE = "papers_progress.yml"

# Mapping of aliases to full status strings
STATUS_ALIASES = {
    "ns": "not started",
    "ip": "in progress",
    "d": "read"
}

def sanitize_filename(s):
    """
    Create a safe filename from a given string.
    Replaces spaces with underscores and removes unsafe characters.
    """
    return re.sub(r'(?u)[^-\w.]', '', s.strip().replace(" ", "_"))

def flatten_papers(papers):
    """
    Flatten the list of papers to include all related papers as separate entries.
    For each top-level paper, add the main paper (without its 'related' field)
    and then add each related paper. For related papers, add a 'parent_title'
    field to indicate from which paper they came.
    """
    flat_list = []
    for paper in papers:
        main_paper = paper.copy()
        if "related" in main_paper:
            del main_paper["related"]
        flat_list.append(main_paper)
        if "related" in paper and isinstance(paper["related"], list):
            for related in paper["related"]:
                related_copy = related.copy()
                related_copy["parent_title"] = paper.get("title")
                flat_list.append(related_copy)
    return flat_list

def assign_ids(papers):
    """
    Assign a unique numeric id to each paper if not already present.
    """
    for idx, paper in enumerate(papers, start=1):
        if "id" not in paper:
            paper["id"] = idx
    return papers

def load_papers():
    """
    Load papers from the progress file if it exists;
    otherwise load from papers.yml, flatten the list to include related papers,
    assign ids, and add a default progress section.
    """
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            papers = yaml.safe_load(f)
    else:
        with open(PAPERS_FILE, "r") as f:
            papers = yaml.safe_load(f)
        papers = flatten_papers(papers)
        papers = assign_ids(papers)
        for paper in papers:
            paper["progress"] = {
                "status": "not started",
                "start_date": None,
                "finished_date": None,
            }
        save_papers(papers)
    return papers

def save_papers(papers):
    with open(PROGRESS_FILE, "w") as f:
        yaml.safe_dump(papers, f)

def init_papers():
    """
    Initialize the progress file from papers.yml.
    This will flatten the papers, assign IDs, and add the default progress.
    """
    if os.path.exists(PROGRESS_FILE):
        print(f"{PROGRESS_FILE} already exists.")
        return
    with open(PAPERS_FILE, "r") as f:
        papers = yaml.safe_load(f)
    papers = flatten_papers(papers)
    papers = assign_ids(papers)
    for paper in papers:
        paper["progress"] = {
            "status": "not started",
            "start_date": None,
            "finished_date": None,
        }
    save_papers(papers)
    print(f"Initialized {PROGRESS_FILE} from {PAPERS_FILE} with paper IDs (including related papers).")

def reset_papers():
    """
    Reset progress for all papers to default (not started).
    """
    papers = load_papers()
    for paper in papers:
        paper["progress"] = {
            "status": "not started",
            "start_date": None,
            "finished_date": None,
        }
    save_papers(papers)
    print("Reset progress for all papers.")

def set_paper_status(paper_id, status, start_date=None, finished_date=None):
    """
    Set the progress status for a given paper by id.
    For 'in progress', a start_date is recorded (default: today).
    For 'read', a finished_date is recorded (default: today) and a start_date is set if not already.
    Supports aliases: 'ns' for not started, 'ip' for in progress, and 'd' for read.
    """
    # Convert aliases to full status strings if applicable
    status = STATUS_ALIASES.get(status.lower(), status).lower()

    papers = load_papers()
    found = False
    for paper in papers:
        if paper.get("id") == paper_id:
            found = True
            if status not in ["not started", "in progress", "read"]:
                print("Invalid status. Use 'not started' (or 'ns'), 'in progress' (or 'ip'), or 'read' (or 'd').")
                return

            paper["progress"]["status"] = status

            if status == "in progress":
                paper["progress"]["start_date"] = start_date or datetime.date.today().isoformat()
                paper["progress"]["finished_date"] = None
            elif status == "read":
                if not paper["progress"].get("start_date"):
                    paper["progress"]["start_date"] = start_date or datetime.date.today().isoformat()
                paper["progress"]["finished_date"] = finished_date or datetime.date.today().isoformat()
            elif status == "not started":
                paper["progress"]["start_date"] = None
                paper["progress"]["finished_date"] = None
            break

    if not found:
        print(f"Paper with ID '{paper_id}' not found.")
    else:
        save_papers(papers)
        print(f"Updated status for paper ID: {paper_id}")

def list_papers(status_filter=None):
    """
    List papers, optionally filtering by progress status.
    Supports aliases: 'ns' for not started, 'ip' for in progress, and 'd' for read.
    """
    if status_filter:
        # Convert alias to full status if applicable.
        status_filter = STATUS_ALIASES.get(status_filter.lower(), status_filter).lower()
    papers = load_papers()
    count = 0
    for paper in papers:
        status = paper.get("progress", {}).get("status", "not started")
        if status_filter and status.lower() != status_filter:
            continue
        count += 1
        print(f"ID: {paper.get('id')}")
        print(f"Title: {paper.get('title')}")
        if "parent_title" in paper:
            print(f"  (Related to: {paper.get('parent_title')})")
        print(f"  Status: {status}")
        print(f"  Start Date: {paper.get('progress', {}).get('start_date')}")
        print(f"  Finished Date: {paper.get('progress', {}).get('finished_date')}")
        print("-" * 60)
    if count == 0:
        print("No papers found with the specified filter.")

def download_paper(paper_id):
    """
    Download the PDF for the paper with the given id.
    The PDF is saved using a sanitized version of the paper's title.
    """
    papers = load_papers()
    paper = next((p for p in papers if p.get("id") == paper_id), None)
    if paper is None:
        print(f"Paper with ID '{paper_id}' not found.")
        return
    link = paper.get("link")
    if not link:
        print("No link found for this paper.")
        return
    title = paper.get("title", f"paper_{paper_id}")
    filename = sanitize_filename(title) + ".pdf"
    try:
        print(f"Downloading '{title}' from {link} ...")
        response = requests.get(link, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded and saved to {filename}")
    except Exception as e:
        print(f"Error downloading paper: {e}")

def main():
    parser = argparse.ArgumentParser(description="CLI for managing paper reading progress using paper IDs")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # init: Initialize progress file from papers.yml (including related papers)
    parser_init = subparsers.add_parser("init", help="Initialize the papers_progress.yml file from papers.yml")

    # reset: Reset progress for all papers
    parser_reset = subparsers.add_parser("reset", help="Reset progress on all papers to 'not started'")

    # set: Update the status of a paper by ID
    parser_set = subparsers.add_parser("set", help="Set the status for a paper by ID")
    parser_set.add_argument("--id", required=True, type=int, help="ID of the paper to update")
    parser_set.add_argument("--status", required=True, help="Status to set (not started/ns, in progress/ip, read/d)")
    parser_set.add_argument("--start_date", help="Optional start date (YYYY-MM-DD) for 'in progress' or 'read' statuses")
    parser_set.add_argument("--finished_date", help="Optional finished date (YYYY-MM-DD) for 'read' status")

    # list: View papers by progress status (optional filter)
    parser_list = subparsers.add_parser("list", help="List papers by progress status")
    parser_list.add_argument("--status", help="Filter papers by status (not started/ns, in progress/ip, read/d)")

    # download: Download the PDF for a paper by ID
    parser_download = subparsers.add_parser("download", help="Download the PDF for a paper by ID")
    parser_download.add_argument("--id", required=True, type=int, help="ID of the paper to download")

    args = parser.parse_args()

    if args.command == "init":
        init_papers()
    elif args.command == "reset":
        reset_papers()
    elif args.command == "set":
        set_paper_status(args.id, args.status, args.start_date, args.finished_date)
    elif args.command == "list":
        list_papers(args.status)
    elif args.command == "download":
        download_paper(args.id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
