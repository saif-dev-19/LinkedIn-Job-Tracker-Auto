import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL_NAME = os.getenv("GEMINI_MODEL")


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
- Keep it concise
- Keep it human and natural
- Do not invent fake experience
- Focus on Python, Django, DRF, APIs, backend systems, PostgreSQL, Redis, Celery when relevant
- Make it suitable for a real job application
- No fake salary or fake years of experience
- Maximum 250 words
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return response.text.strip()

def generate_match_score(job):
    resume_text = read_resume()

    prompt = f"""
You are an expert technical recruiter.

Analyze how well the candidate resume matches this job.

Resume:
{resume_text}

Job:
Title: {job.get("title")}
Company: {job.get("company")}
Location: {job.get("location")}

Rules:
- Return ONLY a number
- Score between 0 to 100
- Consider backend engineering relevance
- Consider Python/Django relevance
- No explanation
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    text = response.text.strip()

    try:
        return int(text)
    except:
        return 0