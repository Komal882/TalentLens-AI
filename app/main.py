
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pypdf import PdfReader

from app.matcher import screen_resumes
from app.schemas import (
    ResumeInput,
    ScreeningRequest,
    ScreeningResponse,
)

app = FastAPI(
    title="Smart Resume Screening System",
    description="AI-powered resume screening with PDF upload, TF-IDF and skill matching.",
    version="1.1.0",
)


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount(
    "/frontend",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="frontend",
)




@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/screen-resumes", response_model=ScreeningResponse)
def screen_resume_endpoint(payload: ScreeningRequest):
    results = screen_resumes(
        job_description=payload.job_description,
        resumes=payload.resumes,
    )
    return ScreeningResponse(results=results)


@app.post("/screen-pdf", response_model=ScreeningResponse)
async def screen_pdf_endpoint(
    job_description: str = Form(...),
    candidate_name: str = Form(""),
    resume_file: UploadFile = File(...),
):
    filename = resume_file.filename or ""

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF resume.",
        )

    temp_path = None

    try:
        content = await resume_file.read()

        if not content:
            raise HTTPException(status_code=400, detail="The PDF is empty.")

        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="PDF size must be 5 MB or less.",
            )

        if not content.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is not a valid PDF.",
            )

        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=".pdf",
            delete=False,
        ) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        reader = PdfReader(temp_path)

        if reader.is_encrypted:
            raise HTTPException(
                status_code=400,
                detail="Password-protected PDFs are not supported.",
            )

        
        resume_text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        ).strip()

        if not resume_text:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No readable text found. Please upload a "
                    "text-based PDF, not a scanned image."
                ),
            )

        # Automatically extract candidate name from resume
        if not candidate_name or candidate_name == "Candidate":
            lines = [
                line.strip()
                for line in resume_text.splitlines()
                if line.strip()
            ]

            if lines:
                candidate_name = lines[0]

        resume = ResumeInput(
            candidate_name=candidate_name,
            text=resume_text,
        )


        results = screen_resumes(
            job_description=job_description,
            resumes=[resume],
        )

        return ScreeningResponse(results=results)

    except HTTPException:
        raise

    except Exception as exc:
        print("PDF ERROR:", repr(exc))
        raise HTTPException(
            status_code=400,
            detail=f"PDF processing failed: {str(exc)}",
        ) from exc

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        await resume_file.close()
