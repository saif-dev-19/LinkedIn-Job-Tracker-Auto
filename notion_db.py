import json
import os
from datetime import datetime
import requests
from dotenv import load_dotenv
from notion_client import Client

from ai import generate_cover_letter, generate_match_score


load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

SAVED_JOBS_FILE = "saved_jobs.json"


def load_saved_job_ids():
    if not os.path.exists(SAVED_JOBS_FILE):
        return set()

    with open(SAVED_JOBS_FILE, "r", encoding="utf-8") as file:
        return set(json.load(file))


def save_job_ids(job_ids):
    with open(SAVED_JOBS_FILE, "w", encoding="utf-8") as file:
        json.dump(list(job_ids), file, indent=2)


def get_jobs_to_generate():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    payload = {
        "filter": {
            "and": [
                {
                    "property": "Generate Cover Letter",
                    "checkbox": {
                        "equals": True,
                    },
                },
                {
                    "property": "Cover Letter Generated",
                    "checkbox": {
                        "equals": False,
                    },
                },
            ]
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    data = response.json()

    jobs = []

    for page in data.get("results", []):
        properties = page["properties"]

        job = {
            "title": properties["Title"]["title"][0]["text"]["content"],
            "company": properties.get("Company", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
            "location": properties.get("Location", {}).get("rich_text", [{}])[0].get("text", {}).get("content", ""),
            "job_id": properties["Job ID"]["rich_text"][0]["text"]["content"],
            "link": properties["Link"]["url"],
        }

        jobs.append((job, page["id"]))

    return jobs


def generate_and_save_cover_letters():
    jobs = get_jobs_to_generate()

    for job, page_id in jobs:
        try:
            cover_letter = generate_cover_letter(job)

            notion.pages.update(
                page_id=page_id,
                properties={
                    "Cover Letter": {
                        "rich_text": [{"text": {"content": cover_letter[:1900]}}],
                    },
                    "Cover Letter Generated": {"checkbox": True},
                    "Generate Cover Letter": {"checkbox": False},
                },
            )

            print(f"Cover letter generated for: {job['title']}")

        except Exception as e:
            print(f"Failed for {job['title']}: {e}")


def get_match_score(job):
    try:
        return generate_match_score(job)

    except Exception as e:
        print("AI match score failed:", e)
        return 0


def save_jobs_to_notion(jobs):
    saved_job_ids = load_saved_job_ids()
    saved_count = 0

    for job in jobs:
        if job["job_id"] in saved_job_ids:
            continue

        match_score = get_match_score(job)

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
                "Cover Letter": {
                    "rich_text": [{"text": {"content": ""}}],
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
                "Match Score": {
                    "number": match_score,
                },
                "Date Added": {
                    "date": {"start": datetime.now().isoformat()},
                },
                "Generate Cover Letter": {
                    "checkbox": False,
                },
                "Cover Letter Generated": {
                    "checkbox": False,
                },
            },
        )

        saved_job_ids.add(job["job_id"])
        saved_count += 1

    save_job_ids(saved_job_ids)

    print(f"Saved {saved_count} new jobs to Notion.")