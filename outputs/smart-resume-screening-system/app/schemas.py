from typing import List, Optional

from pydantic import BaseModel, Field


class ResumeInput(BaseModel):
    candidate_name: Optional[str] = Field(default="Unknown Candidate")
    text: str = Field(..., min_length=20)


class ScreeningRequest(BaseModel):
    job_description: str = Field(..., min_length=20)
    resumes: List[ResumeInput] = Field(..., min_length=1)


class ResumeScreeningResult(BaseModel):
    candidate_name: str
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    experience_years: Optional[float]
    explanation: str


class ScreeningResponse(BaseModel):
    results: List[ResumeScreeningResult]

