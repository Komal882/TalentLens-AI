import math
import re
from collections import Counter
from typing import Dict, List

from app.parser import extract_experience_years, extract_skills
from app.schemas import ResumeInput, ResumeScreeningResult


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9+#.]+", text.lower())


def build_tfidf_vectors(documents: List[str]) -> List[Dict[str, float]]:
    tokenized_documents = [tokenize(document) for document in documents]
    document_count = len(tokenized_documents)
    vocabulary = sorted(set(token for tokens in tokenized_documents for token in tokens))
    document_frequency = {
        token: sum(1 for tokens in tokenized_documents if token in tokens)
        for token in vocabulary
    }

    vectors = []
    for tokens in tokenized_documents:
        token_counts = Counter(tokens)
        total_tokens = len(tokens) or 1
        vector = {}

        for token in vocabulary:
            term_frequency = token_counts[token] / total_tokens
            inverse_document_frequency = math.log((document_count + 1) / (document_frequency[token] + 1)) + 1
            vector[token] = term_frequency * inverse_document_frequency

        vectors.append(vector)

    return vectors


def cosine_score(vector_a: Dict[str, float], vector_b: Dict[str, float]) -> float:
    common_tokens = set(vector_a).intersection(vector_b)
    dot_product = sum(vector_a[token] * vector_b[token] for token in common_tokens)
    magnitude_a = math.sqrt(sum(value * value for value in vector_a.values()))
    magnitude_b = math.sqrt(sum(value * value for value in vector_b.values()))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def calculate_similarity_scores(job_description: str, resumes: List[ResumeInput]) -> List[float]:
    documents = [job_description] + [resume.text for resume in resumes]
    vectors = build_tfidf_vectors(documents)
    job_description_vector = vectors[0]
    return [cosine_score(job_description_vector, resume_vector) for resume_vector in vectors[1:]]


def build_explanation(score: float, matched_skills: List[str], missing_skills: List[str]) -> str:
    if score >= 70:
        fit_level = "Strong match"
    elif score >= 50:
        fit_level = "Moderate match"
    else:
        fit_level = "Low match"

    matched_text = ", ".join(matched_skills[:6]) if matched_skills else "no key JD skills"
    if missing_skills:
        missing_text = "Missing skills include " + ", ".join(missing_skills[:6]) + "."
    else:
        missing_text = "No major JD skills were missing."

    return (
        f"{fit_level} based on resume similarity and skill overlap. "
        f"Matched skills include {matched_text}. {missing_text}"
    )


def screen_resumes(job_description: str, resumes: List[ResumeInput]) -> List[ResumeScreeningResult]:
    jd_skills = set(extract_skills(job_description))
    similarity_scores = calculate_similarity_scores(job_description, resumes)
    results = []

    for resume, similarity_score in zip(resumes, similarity_scores):
        resume_skills = set(extract_skills(resume.text))
        matched_skills = sorted(jd_skills.intersection(resume_skills))
        missing_skills = sorted(jd_skills.difference(resume_skills))

        skill_overlap = len(matched_skills) / len(jd_skills) if jd_skills else 0
        final_score = (similarity_score * 40) + (skill_overlap * 60)
        final_score = round(min(final_score, 100), 2)

        results.append(
            ResumeScreeningResult(
                candidate_name=resume.candidate_name or "Unknown Candidate",
                match_score=final_score,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                experience_years=extract_experience_years(resume.text),
                explanation=build_explanation(final_score, matched_skills, missing_skills),
            )
        )

    return sorted(results, key=lambda item: item.match_score, reverse=True)
