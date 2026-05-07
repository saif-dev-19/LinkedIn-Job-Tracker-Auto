# LinkedIn Job Automation

An AI-powered LinkedIn job tracking automation built with Python.

This project automatically:

* Reads LinkedIn job alert emails from Gmail
* Extracts and filters relevant jobs
* Saves jobs to Notion
* Prevents duplicate jobs
* Generates AI-powered cover letters on demand
* Calculates AI match scores for jobs
* Supports multiple job roles (Backend, Frontend, Fullstack)
* Runs automatically using cron jobs

---

# Features

## Gmail Job Parsing

Reads LinkedIn job alert emails directly from Gmail using the Gmail API.

## Smart Job Filtering

Filters jobs based on:

* Selected role
* Remote jobs
* Bangladesh jobs
* Excludes India and Pakistan jobs

## AI Match Score

Uses Gemini AI to calculate how well your resume matches a job.

## AI Cover Letter Generation

Generate cover letters only when needed using Notion checkboxes.

## Notion Integration

Automatically stores jobs in a structured Notion database.

## Duplicate Prevention

Prevents duplicate jobs using local job ID tracking.

## Cron Automation

Runs automatically every day using Linux cron jobs.

---

# Tech Stack

* Python
* Gmail API
* Notion API
* Gemini AI
* BeautifulSoup4
* Cron
* dotenv

---

# Project Structure

```bash
linkedin_job_automations/
│
├── main.py
├── notion_db.py
├── ai.py
├── resume.md
├── saved_jobs.json
├── token.json
├── credentials.json
├── .env
├── requirements.txt
└── README.md
```

---

# Setup Guide

## 1. Clone Repository

```bash
git clone <your_repo_url>
cd linkedin_job_automations
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

### Linux / Mac

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Gmail API Setup

## Enable APIs

Enable:

* Gmail API

From:

https://console.cloud.google.com/

---

## Create OAuth Credentials

Create:

OAuth Client ID

Download credentials JSON file.

Rename it:

```text
credentials.json
```

Put it in project root.

---

# Notion Setup

## Create Notion Integration

Go to:

https://www.notion.so/my-integrations

Create integration and copy:

* NOTION_TOKEN

---

## Create Notion Database

Recommended properties:

| Property               | Type     |
| ---------------------- | -------- |
| Title                  | Title    |
| Company                | Text     |
| Location               | Text     |
| Job ID                 | Text     |
| Link                   | URL      |
| Match Score            | Number   |
| Cover Letter           | Text     |
| Generate Cover Letter  | Checkbox |
| Cover Letter Generated | Checkbox |
| Status                 | Select   |
| Priority               | Select   |
| Source                 | Select   |
| Date Added             | Date     |

---

## Share Database With Integration

Inside Notion database:

Share → Invite → Select your integration

---

# Gemini AI Setup

Get API key from:

https://aistudio.google.com/

---

# Environment Variables

Create `.env`

```env
NOTION_TOKEN=your_notion_token
DATABASE_ID=your_database_id

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

JOB_ROLE=backend
```

---

# Supported Roles

## Backend

```env
JOB_ROLE=backend
```

## Frontend

```env
JOB_ROLE=frontend
```

## Fullstack

```env
JOB_ROLE=fullstack
```

---

# Resume Setup

Create:

```text
resume.md
```

Add your resume information there.

This resume is used for:

* AI cover letters
* AI match score generation

---

# Run Project

```bash
python main.py
```

---

# Workflow

## Job Collection

```text
LinkedIn Job Alert Email
        ↓
Gmail API
        ↓
Job Parsing
        ↓
Role & Location Filtering
        ↓
Save to Notion
```

---

## AI Cover Letter Workflow

```text
Check "Generate Cover Letter"
        ↓
Run automation
        ↓
AI generates cover letter
        ↓
Saved to Notion
```

---

# Remote Job Filtering

Allowed:

* Worldwide Remote
* Bangladesh Onsite/Hybrid/Remote

Blocked:

* India
* Pakistan

---

# Recent Job Filtering

Only jobs from:

```text
Last 5 days
```

are processed.

---

# Cron Automation

Open crontab:

```bash
crontab -e
```

Example:

```cron
0 9 * * * cd /home/user/linkedin_job_automations && /home/user/linkedin_job_automations/venv/bin/python main.py >> cron.log 2>&1
```

Runs every day at 9 AM.

---

# AI Cover Letter Generation

Cover letters are NOT automatically generated for every job.

This prevents:

* unnecessary AI usage
* quota exhaustion
* slow automation

Instead:

1. Open Notion
2. Check:
   Generate Cover Letter
3. Run automation
4. Cover letter will be generated

---

# Duplicate Prevention

The system uses:

```text
saved_jobs.json
```

to prevent duplicate job entries.

---

# Future Improvements

* Telegram notifications
* Easy Apply filtering
* Salary filtering
* Playwright-based live scraping
* Auto application support
* Multi-user support
* Dashboard analytics

---

# Disclaimer

This project uses LinkedIn job alert emails and does NOT scrape LinkedIn directly.

Use responsibly and follow LinkedIn policies.

---

# License

MIT License
