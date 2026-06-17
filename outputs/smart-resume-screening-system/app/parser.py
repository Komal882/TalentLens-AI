import re
from typing import List, Optional


SKILL_KEYWORDS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "redis",
    "fastapi",
    "flask",
    "django",
    "react",
    "angular",
    "node.js",
    "node",
    "html",
    "css",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "git",
    "linux",
    "machine learning",
    "deep learning",
    "nlp",
    "computer vision",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "sklearn",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "data analysis",
    "data science",
    "etl",
    "airflow",
    "spark",
    "hadoop",
    "rest api",
    "api",
    "microservices",
    "ci/cd",
    "jenkins",
    "testing",
    "pytest",
    "agile",
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def extract_skills(text: str) -> List[str]:
    normalized_text = normalize_text(text)
    found_skills = set()

    for skill in SKILL_KEYWORDS:
        pattern = r"(?<![a-z0-9+#.])" + re.escape(skill) + r"(?![a-z0-9+#.])"
        if re.search(pattern, normalized_text):
            found_skills.add(skill)

    if "sklearn" in found_skills:
        found_skills.add("scikit-learn")
        found_skills.discard("sklearn")

    if "node" in found_skills:
        found_skills.add("node.js")
        found_skills.discard("node")

    return sorted(found_skills)


def extract_experience_years(text: str) -> Optional[float]:
    normalized_text = normalize_text(text)
    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years|year|yrs|yr)\s+(?:of\s+)?(?:experience|exp)",
        r"(?:experience|exp)\s*(?:of\s*)?(\d+(?:\.\d+)?)\+?\s*(?:years|year|yrs|yr)",
        r"(\d+(?:\.\d+)?)\+?\s*(?:years|year|yrs|yr)",
    ]

    matches = []
    for pattern in patterns:
        matches.extend(float(value) for value in re.findall(pattern, normalized_text))

    return max(matches) if matches else None

