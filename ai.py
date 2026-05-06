import os

from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(os.getenv("GEMINI_MODEL"))


def read_resume():
    with open("resume.md", "r", encoding="utf-8") as file:
        return file.read()


def generate_cover_letter(job):
    resume_text = read_resume()

    prompt = f"""
You are an expert career assistant.

Write a short, professional, human-sounding cover letter based on the resume and job information.

Resume:
{resume_text}

Job Information:
Title: {job.get("title")}
Company: {job.get("company")}
Location: {job.get("location")}

Rules:
- Keep it concise.
- Do not invent experience.
- Focus on Python, Django, DRF, APIs, backend systems, PostgreSQL, Redis, Celery when relevant.
- Make it suitable for job application email/message.
- Do not include fake salary, fake years, or unavailable information.
"""

    response = model.generate_content(prompt)

    return response.text.strip()