from datetime import datetime

import gspread
from google.oauth2.credentials import Credentials
import os
from dotenv import load_dotenv

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
]

load_dotenv()
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")


def get_sheet():
    creds = Credentials.from_authorized_user_file(
        "token.json",
        SCOPES,
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    return spreadsheet.sheet1


def save_jobs_to_sheet(jobs):
    sheet = get_sheet()

    existing_job_ids = set(sheet.col_values(2))

    rows = []

    for job in jobs:
        if job["job_id"] in existing_job_ids:
            continue

        rows.append(
            [
                datetime.now().strftime("%Y-%m-%d"),
                job["job_id"],
                job["title"],
                job["link"],
                "LinkedIn",
                "New",
            ]
        )

    if rows:
        sheet.append_rows(rows)
        print(f"Saved {len(rows)} new jobs to Google Sheet.")
    else:
        print("No new jobs to save.")