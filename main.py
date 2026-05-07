from __future__ import print_function

import base64
import os.path

from bs4 import BeautifulSoup

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from notion_db import save_jobs_to_notion, generate_and_save_cover_letters


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
]

ROLE_PRESETS = {
    "backend": [
        "python",
        "django",
        "backend",
        "back end",
        "software engineer",
        "software developer",
        "drf",
        "api",
    ],
    "frontend": [
        "frontend",
        "front end",
        "react",
        "next.js",
        "javascript",
        "typescript",
        "tailwind",
        "web developer",
    ],
    "fullstack": [
        "full stack",
        "fullstack",
        "software engineer",
        "software developer",
        "django",
        "react",
        "api",
    ],
}

JOB_ROLE = os.getenv("JOB_ROLE", "backend").lower()

ROLE_KEYWORDS = ROLE_PRESETS.get(
    JOB_ROLE,
    ROLE_PRESETS["backend"],
)

BANGLADESH_KEYWORDS = [
    "bangladesh",
    "dhaka",
    "chattogram",
    "chittagong",
    "mirpur",
]

REMOTE_KEYWORDS = [
    "remote",
]

EXCLUDED_COUNTRIES = [
    "india",
    "pakistan",
]


def get_gmail_service():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def extract_html(payload):
    parts = payload.get("parts", [])

    for part in parts:
        if part.get("mimeType") == "text/html":
            data = part["body"]["data"]
            decoded_data = base64.urlsafe_b64decode(data)
            return decoded_data.decode("utf-8")

    return None


def clean_link(url: str) -> str:
    return url.split("?")[0]


def clean_title(title: str) -> str:
    return " ".join(title.split())


def is_relevant_job(title: str) -> bool:
    title = title.lower()
    return any(keyword in title for keyword in ROLE_KEYWORDS)


def is_allowed_location(text: str) -> bool:
    text = text.lower()

    if any(country in text for country in EXCLUDED_COUNTRIES):
        return False

    is_remote = any(keyword in text for keyword in REMOTE_KEYWORDS)
    is_bangladesh = any(keyword in text for keyword in BANGLADESH_KEYWORDS)

    return is_remote or is_bangladesh


def parse_jobs_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    jobs = []
    seen_job_ids = set()

    links = soup.find_all("a")

    for link in links:
        href = link.get("href", "")
        title = clean_title(link.get_text(" ", strip=True))

        job_card = link.find_parent(attrs={"data-test-id": "job-card"})

        if not job_card:
            continue

        card_text = clean_title(job_card.get_text(" ", strip=True))

        if "/jobs/view/" not in href:
            continue

        if "jobcard_body" not in href:
            continue

        clean_url = clean_link(href)

        try:
            job_id = clean_url.split("/jobs/view/")[1].strip("/")
        except IndexError:
            continue

        if job_id in seen_job_ids:
            continue

        if len(title) < 5:
            continue

        if not is_relevant_job(title):
            continue

        if not is_allowed_location(card_text):
            continue

        seen_job_ids.add(job_id)

        parts = card_text.split(title)
        extra_text = parts[1].strip() if len(parts) > 1 else ""

        company = ""
        location = ""

        extra_parts = extra_text.split("·")

        if len(extra_parts) >= 1:
            company = extra_parts[0].strip()

        if len(extra_parts) >= 2:
            location = extra_parts[1].strip()

        jobs.append(
            {
                "job_id": job_id,
                "title": title,
                "company": company,
                "location": location,
                "link": clean_url,
            }
        )

    return jobs


def get_linkedin_jobs(service):
    results = (
        service.users()
        .messages()
        .list(
            userId="me",
            q="from:jobs-listings@linkedin.com newer_than:5d",
            maxResults=10,
        )
        .execute()
    )

    messages = results.get("messages", [])

    if not messages:
        print("No recent LinkedIn emails found.")
        return []

    all_jobs = []
    seen_job_ids = set()

    for msg in messages:
        message = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=msg["id"],
            )
            .execute()
        )

        html = extract_html(message["payload"])

        if not html:
            continue

        jobs = parse_jobs_from_html(html)

        for job in jobs:
            if job["job_id"] in seen_job_ids:
                continue

            seen_job_ids.add(job["job_id"])
            all_jobs.append(job)

    print("\nFound Jobs:\n")

    for job in all_jobs:
        print("Title:", job["title"])
        print("Company:", job.get("company", ""))
        print("Location:", job.get("location", ""))
        print("Link :", job["link"])
        print("-" * 50)

    save_jobs_to_notion(all_jobs)

    return all_jobs


if __name__ == "__main__":
    print("Automation started...")
    print(f"Selected job role: {JOB_ROLE}")
    service = get_gmail_service()
    get_linkedin_jobs(service)

    print("Checking cover letter queue...")
    generate_and_save_cover_letters()

    print("Automation finished.")