#!/usr/bin/env python3
import argparse
import datetime
import os
import yaml

# File names
PAPERS_FILE = "papers.yml"
PROGRESS_FILE = "papers_progress.yml"

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
    Load papers from the progress file if it exists,
    otherwise from the original papers.yml, assign ids, and add a default progress section.
    """
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            papers = yaml.safe_load(f)
    else:
        with open(PAPERS_FILE, "r") as f:
            papers = yaml.safe_load(f)
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
    """
    if os.path.exists(PROGRESS_FILE):
        print(f"{PROGRESS_FILE} already exists.")
        return
    with open(PAPERS_FILE, "r") as f:
        papers = yaml.safe_load(f)
    papers = assign_ids(papers)
    for paper in papers:
        paper["progress"] = {
            "status": "not started",
            "start_date": None,
            "finished_date": None,
        }
    save_papers(papers)
    print(f"Initialized {PROGRESS_FILE} from {PAPERS_FILE} with paper IDs.")

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
    For 'read', a finished_date is recorded (default: today) and a start_date if not already set.
    """
    papers = load_papers()
    found = False
    for paper in papers:
        if paper.get("id") == paper_id:
            found = True
            status_lower = status.lower()
            if status_lower not in ["not started", "in progress", "read"]:
                print("Invalid status. Use 'not started', 'in progress', or 'read'.")
                return

            paper["progress"]["status"] = status_lower

            if status_lower == "in progress":
                paper["progress"]["start_date"] = start_date or datetime.date.today().isoformat()
                paper["progress"]["finished_date"] = None
            elif status_lower == "read":
                if not paper["progress"].get("start_date"):
                    paper["progress"]["start_date"] = start_date or datetime.date.today().isoformat()
                paper["progress"]["finished_date"] = finished_date or datetime.date.today().isoformat()
            elif status_lower == "not started":
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
    """
    papers = load_papers()
    count = 0
    for paper in papers:
        status = paper.get("progress", {}).get("status", "not started")
        if status_filter and status.lower() != status_filter.lower():
            continue
        count += 1
        print(f"ID: {paper.get('id')}")
        print(f"Title: {paper.get('title')}")
        print(f"  Status: {status}")
        print(f"  Start Date: {paper.get('progress', {}).get('start_date')}")
        print(f"  Finished Date: {paper.get('progress', {}).get('finished_date')}")
        print("-" * 60)
    if count == 0:
        print("No papers found with the specified filter.")

def main():
    parser = argparse.ArgumentParser(description="CLI for managing paper reading progress using paper IDs")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Init command to create progress file from papers.yml
    parser_init = subparsers.add_parser("init", help="Initialize the papers_progress.yml file from papers.yml")

    # Reset command
    parser_reset = subparsers.add_parser("reset", help="Reset progress on all papers to 'not started'")

    # Set command to update the status of a paper by ID
    parser_set = subparsers.add_parser("set", help="Set the status for a paper by ID")
    parser_set.add_argument("--id", required=True, type=int, help="ID of the paper to update")
    parser_set.add_argument("--status", required=True, help="Status to set (not started, in progress, read)")
    parser_set.add_argument("--start_date", help="Optional start date (YYYY-MM-DD) for 'in progress' or 'read' statuses")
    parser_set.add_argument("--finished_date", help="Optional finished date (YYYY-MM-DD) for 'read' status")

    # List command to view papers by status
    parser_list = subparsers.add_parser("list", help="List papers by progress status")
    parser_list.add_argument("--status", help="Filter papers by status (not started, in progress, read)")

    args = parser.parse_args()

    if args.command == "init":
        init_papers()
    elif args.command == "reset":
        reset_papers()
    elif args.command == "set":
        set_paper_status(args.id, args.status, args.start_date, args.finished_date)
    elif args.command == "list":
        list_papers(args.status)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
