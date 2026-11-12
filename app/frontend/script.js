
const form = document.getElementById("screeningForm");
const resumeInput = document.getElementById("resumeFile");
const fileName = document.getElementById("fileName");
const fileHint = document.getElementById("fileHint");
const button = document.getElementById("analyzeButton");
const buttonText = document.getElementById("buttonText");
const message = document.getElementById("message");
const resultsPanel = document.getElementById("results");

resumeInput.addEventListener("change", () => {
  const file = resumeInput.files[0];

  fileName.textContent = file ? file.name : "Choose a resume PDF";
  fileHint.textContent = file
    ? `${(file.size / 1024 / 1024).toFixed(2)} MB · PDF document`
    : "Click to browse · PDF only · Maximum 5 MB";
});

function renderSkills(containerId, skills, isMissing = false) {
  const container = document.getElementById(containerId);
  container.replaceChildren();

  if (!skills || skills.length === 0) {
    const empty = document.createElement("span");
    empty.className = "empty-skill";
    empty.textContent = isMissing
      ? "No missing skills detected."
      : "No matched skills detected.";
    container.appendChild(empty);
    return;
  }

  skills.forEach((skill) => {
    const badge = document.createElement("span");
    badge.className = isMissing ? "skill-tag missing" : "skill-tag";
    badge.textContent = skill;
    container.appendChild(badge);
  });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  message.textContent = "";
  resultsPanel.hidden = true;

  const file = resumeInput.files[0];
  const jobDescription = document
    .getElementById("jobDescription").value.trim();
  const candidateName = document
    .getElementById("candidateName").value.trim();

  if (!file) {
    message.textContent = "Please choose a PDF resume.";
    return;
  }

  if (!file.name.toLowerCase().endsWith(".pdf") ||
      (file.type && file.type !== "application/pdf")) {
    message.textContent = "Please upload a valid PDF file.";
    return;
  }

  if (file.size > 5 * 1024 * 1024) {
    message.textContent = "The PDF must be 5 MB or smaller.";
    return;
  }

  if (file.size === 0) {
    message.textContent = "The selected PDF is empty.";
    return;
  }

  if (jobDescription.length < 20) {
    message.textContent = "Please enter a job description of at least 20 characters.";
    return;
  }

  const formData = new FormData();
  formData.append("job_description", jobDescription);
  formData.append("candidate_name", "");
  formData.append("resume_file", file);

  button.disabled = true;
  buttonText.textContent = "Analyzing resume...";

  try {
    const response = await fetch("/screen-pdf", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      const detail = data.detail;
      throw new Error(
        typeof detail === "string"
          ? detail
          : "Screening failed. Please check the submitted details."
      );
    }

    const result = data.results?.[0];

    if (!result) {
      throw new Error("The API returned no screening results.");
    }

    const score = Number(result.match_score);

    document.getElementById("scoreValue").textContent =
      `${score.toFixed(2)}%`;

    document.getElementById("scoreBar").style.width =
      `${Math.max(0, Math.min(100, score))}%`;

    document.getElementById("matchedCount").textContent =
      (result.matched_skills || []).length;

    document.getElementById("missingCount").textContent =
      (result.missing_skills || []).length;

    document.getElementById("resultSummary").textContent =
      `Screening results for ${result.candidate_name || candidateName || "Candidate"}`;

    renderSkills("matchedSkills", result.matched_skills);
    renderSkills("missingSkills", result.missing_skills, true);

    document.getElementById("explanation").textContent =
      result.explanation || "No additional explanation was returned.";

    document.getElementById("experience").textContent =
      result.experience_years == null
        ? "Not detected"
        : `${result.experience_years} years`;

    resultsPanel.hidden = false;
    resultsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    message.textContent = error.message ||
      "Unable to connect to the screening API.";
  } finally {
    button.disabled = false;
    buttonText.textContent = "Analyze Resume";
  }
});

document.getElementById("resetButton").addEventListener("click", () => {
  form.reset();
  document.getElementById("candidateName").value = "Komal";
  fileName.textContent = "Choose a resume PDF";
  fileHint.textContent = "Click to browse · PDF only · Maximum 5 MB";
  message.textContent = "";
  resultsPanel.hidden = true;
  document.getElementById("analyzer")
    .scrollIntoView({ behavior: "smooth", block: "start" });
});
