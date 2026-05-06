import os
from datetime import datetime

from dotenv import load_dotenv
from notion_client import Client
import json

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)



# def job_exists(job_id: str) -> bool:
#     response = notion.data_sources.query(
#         data_source_id=DATABASE_ID,
#         filter={
#             "property": "Job ID",
#             "rich_text": {
#                 "equals": job_id,
#             },
#         },
#         page_size=1,
#     )

#     return len(response["results"]) > 0

SAVED_JOBS_FILE = "saved_jobs.json"


def load_saved_job_ids():
    if not os.path.exists(SAVED_JOBS_FILE):
        return set()

    with open(SAVED_JOBS_FILE, "r", encoding="utf-8") as file:
        return set(json.load(file))


def save_job_ids(job_ids):
    with open(SAVED_JOBS_FILE, "w", encoding="utf-8") as file:
        json.dump(list(job_ids), file, indent=2)



def save_jobs_to_notion(jobs):
    saved_job_ids = load_saved_job_ids()
    saved_count = 0

    for job in jobs:
        if job["job_id"] in saved_job_ids:
            continue

        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Title": {
                    "title": [{"text": {"content": job["title"]}}],
                },
                "Company": {
                    "rich_text": [{"text": {"content": job.get("company", "")}}],
                },
                "Location": {
                    "rich_text": [{"text": {"content": job.get("location", "")}}],
                },
                "Job ID": {
                    "rich_text": [{"text": {"content": job["job_id"]}}],
                },
                "Link": {
                    "url": job["link"],
                },
                "Status": {
                    "select": {"name": "New"},
                },
                "Source": {
                    "select": {"name": "LinkedIn"},
                },
                "Priority": {
                    "select": {"name": "Medium"},
                },
                "Date Added": {
                    "date": {"start": datetime.now().isoformat()},
                },
            },
        )

        saved_job_ids.add(job["job_id"])
        saved_count += 1

    save_job_ids(saved_job_ids)

    print(f"Saved {saved_count} new jobs to Notion.")
