# Smart Resume Screening System

AI-powered resume screening API built with FastAPI. It accepts a job description and one or more resumes, then returns a match score, matched skills, missing skills, extracted experience, and a short explanation for each resume.

## Features

- Basic resume parsing for skills and experience
- Pure-Python TF-IDF + cosine similarity based matching
- Skill gap analysis
- One FastAPI endpoint for screening multiple resumes
- Clean, simple code suitable for a machine test submission

## Project Structure

```text
.
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── matcher.py
│   ├── parser.py
│   └── schemas.py
├── samples
│   └── request.json
├── requirements.txt
└── README.md
```

## Setup Steps

1. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/Mac:

```bash
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## How To Run API

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

## Endpoint

### `POST /screen-resumes`

Request body:

```json
{
  "job_description": "We need a Python developer with FastAPI, SQL, Docker, and machine learning experience.",
  "resumes": [
    {
      "candidate_name": "Asha Sharma",
      "text": "Python developer with 3 years experience in FastAPI, SQL, Docker, pandas, and ML projects."
    }
  ]
}
```

Example curl:

```bash
curl -X POST "http://127.0.0.1:8000/screen-resumes" \
  -H "Content-Type: application/json" \
  -d @samples/request.json
```

Response:

```json
{
  "results": [
    {
      "candidate_name": "Asha Sharma",
      "match_score": 83.21,
      "matched_skills": ["docker", "fastapi", "machine learning", "python", "sql"],
      "missing_skills": [],
      "experience_years": 3.0,
      "explanation": "Strong match based on resume similarity and skill overlap. Matched skills include docker, fastapi, machine learning, python, sql. No major JD skills were missing."
    }
  ]
}
```

## Approach Explanation

1. The API receives a job description and a list of resume texts.
2. A simple parser extracts known technical skills from the JD and each resume.
3. Experience is extracted using regular expressions such as `3 years experience`, `2+ years`, or `1.5 years`.
4. A lightweight pure-Python TF-IDF implementation converts the JD and resume text into vectors.
5. Cosine similarity measures how close each resume is to the JD.
6. Final score combines semantic text similarity and skill overlap:

```text
final_score = 40% TF-IDF similarity + 60% skill overlap
```

This keeps the implementation simple, explainable, and easy to run without external services or large ML dependencies.

## Timeline

Estimated completion time: 4-6 hours

- Project setup and FastAPI endpoint: 1 hour
- Resume parsing and matching logic: 2 hours
- Response formatting and explanation generation: 1 hour
- README, sample request, and testing: 1-2 hours
