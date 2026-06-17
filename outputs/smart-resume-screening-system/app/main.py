from fastapi import FastAPI

from app.matcher import screen_resumes
from app.schemas import ScreeningRequest, ScreeningResponse


app = FastAPI(
    title="Smart Resume Screening System",
    description="AI-powered resume screening API using TF-IDF and skill matching.",
    version="1.0.0",
)


@app.get("/")
def health_check():
    return {"message": "Smart Resume Screening System API is running"}


@app.post("/screen-resumes", response_model=ScreeningResponse)
def screen_resume_endpoint(payload: ScreeningRequest):
    return ScreeningResponse(
        results=screen_resumes(
            job_description=payload.job_description,
            resumes=payload.resumes,
        )
    )

