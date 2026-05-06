import os
from datetime import datetime
from dotenv import load_dotenv
from notion_client import Client
import json
from ai import generate_cover_letter

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

SAVED_JOBS_FILE = "saved_jobs.json"

# --- Local duplicate tracking ---
def load_saved_job_ids():
    if not os.path.exists(SAVED_JOBS_FILE):
        return set()
    with open(SAVED_JOBS_FILE, "r", encoding="utf-8") as file:
        return set(json.load(file))

def save_job_ids(job_ids):
    with open(SAVED_JOBS_FILE, "w", encoding="utf-8") as file:
        json.dump(list(job_ids), file, indent=2)

# --- Get jobs manually checked for AI cover letter generation ---
def get_jobs_to_generate():
    response = notion.databases.query(
        database_id=DATABASE_ID,
        filter={
            "and": [
                {"property": "Generate Cover Letter", "checkbox": {"equals": True}},
                {"property": "Cover Letter Generated", "checkbox": {"equals": False}}
            ]
        }
    )
    jobs = []
    for page in response.get("results", []):
        job = {
            "title": page["properties"]["Title"]["title"][0]["text"]["content"],
            "company": page["properties"].get("Company", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
            "location": page["properties"].get("Location", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
            "job_id": page["properties"]["Job ID"]["rich_text"][0]["text"]["content"],
            "link": page["properties"]["Link"]["url"]
        }
        jobs.append((job, page["id"]))  # Keep page ID for updating later
    return jobs

# --- Generate AI cover letters only for selected jobs ---
def generate_and_save_cover_letters():
    jobs = get_jobs_to_generate()
    for job, page_id in jobs:
        try:
            cover_letter = generate_cover_letter(job)
            notion.pages.update(
                page_id=page_id,
                properties={
                    "Cover Letter": {"rich_text": [{"text": {"content": cover_letter[:1900]}}]},
                    "Cover Letter Generated": {"checkbox": True},
                    "Generate Cover Letter": {"checkbox": False}
                }
            )
            print(f"Cover letter generated for: {job['title']}")
        except Exception as e:
            print(f"Failed for {job['title']}: {e}")

# --- Save new jobs to Notion (without auto AI generation) ---
def save_jobs_to_notion(jobs):
    saved_job_ids = load_saved_job_ids()
    saved_count = 0

    for job in jobs:
        if job["job_id"] in saved_job_ids:
            continue

        # Do NOT generate AI cover letter here, only save job
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Title": {"title": [{"text": {"content": job["title"]}}]},
                "Company": {"rich_text": [{"text": {"content": job.get("company", "")}}]},
                "Location": {"rich_text": [{"text": {"content": job.get("location", "")}}]},
                "Cover Letter": {"rich_text": [{"text": {"content": ""}}]},  # empty initially
                "Job ID": {"rich_text": [{"text": {"content": job["job_id"]}}]},
                "Link": {"url": job["link"]},
                "Status": {"select": {"name": "New"}},
                "Source": {"select": {"name": "LinkedIn"}},
                "Priority": {"select": {"name": "Medium"}},
                "Date Added": {"date": {"start": datetime.now().isoformat()}},
                "Generate Cover Letter": {"checkbox": False},
                "Cover Letter Generated": {"checkbox": False}
            }
        )

        saved_job_ids.add(job["job_id"])
        saved_count += 1

    save_job_ids(saved_job_ids)
    print(f"Saved {saved_count} new jobs to Notion.")