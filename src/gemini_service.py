import json
import hashlib
import re
import time
from dataclasses import dataclass

import streamlit as st

from src.config import GEMINI_MODEL, get_gemini_api_key

from src.fallback_content import (
    explain_gaps_fallback,
    roadmap_guidance_fallback,
    generate_projects_fallback
)


# --------------------------------------------------
# RESULT STRUCTURE
# --------------------------------------------------

@dataclass
class AIResult:
    ok: bool
    text: str = ""
    data: object = None
    reason: str = ""
    used_fallback: bool = False


# --------------------------------------------------
# CACHE
# --------------------------------------------------

def get_cache():
    """
    Creates an AI cache inside Streamlit session state.
    """

    if "ai_cache" not in st.session_state:
        st.session_state["ai_cache"] = {}

    return st.session_state["ai_cache"]


def make_cache_key(function_name, content):
    """
    Creates a unique cache key for each AI request.
    """

    raw_text = function_name + json.dumps(
        content,
        sort_keys=True,
        default=str
    )

    return hashlib.md5(raw_text.encode()).hexdigest()


# --------------------------------------------------
# GEMINI CONNECTION
# --------------------------------------------------

def call_gemini(prompt):
    """
    Sends a prompt to Google Gemini.

    Retries temporary 429 (per-minute rate limit) and 503 errors.
    Returns:
        (True, response_text, "") on success
        (False, "", error_message) on failure
    """

    api_key = get_gemini_api_key()

    if not api_key:
        return False, "", "Gemini API key was not found."

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

    except ImportError:
        return False, "", "The google-genai package is not installed."

    except Exception as error:
        return False, "", str(error)

    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )

            response_text = response.text

            if not response_text:
                return False, "", "Gemini returned an empty response."

            return True, response_text.strip(), ""

        except Exception as error:
            error_message = str(error)
            error_upper = error_message.upper()

            is_503 = "503" in error_message or "UNAVAILABLE" in error_upper
            is_429 = "429" in error_message or "RESOURCE_EXHAUSTED" in error_upper

            # Do not retry errors that are not temporary rate/service limits.
            if not (is_503 or is_429):
                return False, "", error_message

            # A 429 may mean the daily/monthly quota is exhausted rather than
            # a short per-minute limit. Retry only when the message indicates
            # a short wait or a per-minute limit.
            if is_429:
                temporary_limit = (
                    "PER MINUTE" in error_upper
                    or "RETRY IN" in error_upper
                    or "RETRYDELAY" in error_upper
                )

                if not temporary_limit:
                    return False, "", error_message

            if attempt == max_attempts - 1:
                return False, "", error_message

            # Use Google's suggested delay when it is present.
            match = re.search(
                r"retry in ([\d.]+)s",
                error_message,
                re.IGNORECASE
            )

            if not match:
                match = re.search(
                    r"retryDelay['\"]?\s*:\s*['\"](\d+)s",
                    error_message,
                    re.IGNORECASE
                )

            if match:
                wait_time = float(match.group(1))
            else:
                wait_time = 2 ** (attempt + 1)

            # Keep the app responsive; retry on the next user action if
            # Google asks for a longer wait or the quota is exhausted.
            wait_time = min(max(wait_time, 1), 10)
            time.sleep(wait_time)

    return False, "", "Gemini request failed after retries."

# --------------------------------------------------
# TEXT GENERATION
# --------------------------------------------------

def generate_text(function_name, prompt, fallback_function, cache_data):
    """
    Common function for text-based Gemini features.

    Uses cached results when available.
    Uses fallback content if Gemini fails.
    """

    cache = get_cache()

    cache_key = make_cache_key(function_name, cache_data)

    if cache_key in cache:
        return cache[cache_key]

    success, response, error = call_gemini(prompt)

    if success:
        result = AIResult(
            ok=True,
            text=response,
            reason="",
            used_fallback=False
        )

    else:
        fallback_text = fallback_function()

        result = AIResult(
            ok=False,
            text=fallback_text,
            reason=error,
            used_fallback=True
        )

    # Cache successful responses only. Failed requests can be retried
    # when the user tries again instead of reusing an old error.
    if result.ok:
        cache[cache_key] = result

    return result


# --------------------------------------------------
# SKILL GAP EXPLANATION
# --------------------------------------------------

def explain_gaps(analysis, profile):
    """
    Explains the user's skill gaps in simple language.
    """

    prompt = f"""
You are DataSphere, a friendly career-learning assistant.

Explain the student's skill gaps in simple, encouraging language.

Student profile:
{json.dumps(profile, default=str)}

Skill analysis:
{json.dumps(analysis, default=str)}

Include:
1. What the student is already doing well.
2. Which skills need improvement.
3. Why those skills matter for the selected target role.
4. Three practical next steps.

Do not promise employment or claim that the analysis
is a verified job-readiness score.

Keep the answer clear and concise.
"""

    return generate_text(
        "explain_gaps",
        prompt,
        lambda: explain_gaps_fallback(analysis, profile),
        {
            "analysis": analysis,
            "profile": profile
        }
    )


# --------------------------------------------------
# QUESTION ANSWERING
# --------------------------------------------------

def answer_question(question, analysis, profile):
    """
    Answers a student's question using their profile
    and skill-gap analysis.
    """

    prompt = f"""
You are DataSphere, a helpful learning and career assistant.

Student profile:
{json.dumps(profile, default=str)}

Skill analysis:
{json.dumps(analysis, default=str)}

Student's question:
{question}

Give a useful, beginner-friendly answer.

Keep your answer under 150 words.
Do not invent job-market facts or guarantee employment.
"""

    result = generate_text(
        "answer_question",
        prompt,
        lambda: (
            "I cannot connect to Gemini right now. "
            "Please review your skill-gap analysis and roadmap "
            "while the AI service is unavailable."
        ),
        {
            "question": question,
            "analysis": analysis,
            "profile": profile
        }
    )

    return result


# --------------------------------------------------
# ROADMAP GUIDANCE
# --------------------------------------------------

def roadmap_guidance(roadmap_df, analysis, profile):
    """
    Generates AI guidance for the deterministic roadmap.
    """

    roadmap_text = roadmap_df.to_string(index=False)

    prompt = f"""
You are DataSphere, a friendly learning-roadmap assistant.

Student profile:
{json.dumps(profile, default=str)}

Skill-gap analysis:
{json.dumps(analysis, default=str)}

Student's roadmap:
{roadmap_text}

Explain how the student should follow this roadmap.

Include:
1. A short overview of the roadmap.
2. Which skills should receive the most attention.
3. How to approach the learning sequence.
4. Practical advice for managing weekly study hours.
5. Suggestions for practising and applying the skills.

Keep the guidance encouraging and practical.

Important:
- The roadmap is based on illustrative planning estimates.
- Do not guarantee employment.
- Do not present the skill analysis as a validated
  job-readiness score.
"""

    return generate_text(
        "roadmap_guidance",
        prompt,
        lambda: roadmap_guidance_fallback(
            roadmap_df,
            analysis,
            profile
        ),
        {
            "roadmap": roadmap_text,
            "analysis": analysis,
            "profile": profile
        }
    )


# --------------------------------------------------
# PROJECT GENERATION HELPERS
# --------------------------------------------------

def get_gap_skill_names(analysis):
    """
    Extracts skill names from priority gaps.
    """

    gaps = analysis.get("priority_gaps", [])

    skill_names = []

    for gap in gaps:
        if isinstance(gap, dict):
            skill = gap.get("skill")

            if skill:
                skill_names.append(skill)

        elif isinstance(gap, str):
            skill_names.append(gap)

    return skill_names


def extract_json(text):
    """
    Extracts JSON from Gemini's response.
    Also handles responses wrapped in Markdown code fences.
    """

    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(r"\s*```$", "", cleaned)

    start = cleaned.find("[")
    end = cleaned.rfind("]")

    if start == -1 or end == -1:
        raise ValueError("Gemini did not return a JSON list.")

    return json.loads(cleaned[start:end + 1])


def validate_projects(projects, gap_skills):
    """
    Checks the structure of generated project ideas.
    """

    if not isinstance(projects, list):
        raise ValueError("Projects must be a list.")

    if len(projects) != 3:
        raise ValueError("Exactly three projects are required.")

    required_fields = [
        "title",
        "problem_statement",
        "required_skills",
        "suggested_tools",
        "difficulty",
        "expected_deliverable",
        "evaluation_criteria"
    ]

    validated = []

    allowed_skills = {
        skill.lower(): skill for skill in gap_skills
    }

    for project in projects:

        if not isinstance(project, dict):
            raise ValueError("Invalid project format.")

        for field in required_fields:
            if field not in project:
                raise ValueError(
                    f"Project is missing the {field} field."
                )

        for field in [
            "title",
            "problem_statement",
            "difficulty",
            "expected_deliverable"
        ]:
            if not isinstance(project[field], str) or not project[field].strip():
                raise ValueError(
                    f"Project has an invalid {field}."
                )

        for field in [
            "required_skills",
            "suggested_tools",
            "evaluation_criteria"
        ]:
            if not isinstance(project[field], list):
                raise ValueError(
                    f"Project {field} must be a list."
                )

        if not project["required_skills"]:
            raise ValueError(
                "A project must include at least one required skill."
            )

        # Keep only skills that are actual priority gaps.
        matched_skills = []

        for skill in project["required_skills"]:
            if not isinstance(skill, str):
                continue

            original_name = allowed_skills.get(skill.lower())

            if original_name and original_name not in matched_skills:
                matched_skills.append(original_name)

        if not matched_skills:
            raise ValueError(
                "A project must address at least one priority gap."
            )

        validated.append({
            "title": project["title"].strip(),
            "problem_statement": project["problem_statement"].strip(),
            "required_skills": matched_skills,
            "suggested_tools": [
                str(item) for item in project["suggested_tools"]
            ],
            "difficulty": project["difficulty"].strip(),
            "expected_deliverable": (
                project["expected_deliverable"].strip()
            ),
            "evaluation_criteria": [
                str(item) for item in project["evaluation_criteria"]
            ]
        })

    return validated


# --------------------------------------------------
# PROJECT GENERATION
# --------------------------------------------------

def generate_projects(analysis, profile):
    """
    Generates three project ideas based on the student's
    priority skill gaps.

    If Gemini fails or returns invalid data,
    built-in project ideas are provided instead.
    """

    gap_skills = get_gap_skill_names(analysis)

    if not gap_skills:
        fallback_projects = generate_projects_fallback(
            analysis,
            profile
        )

        return AIResult(
            ok=False,
            data=fallback_projects,
            reason="No priority gaps were found.",
            used_fallback=True
        )

    prompt = f"""
You are DataSphere, a practical project recommendation assistant.

Student profile:
{json.dumps(profile, default=str)}

Skill-gap analysis:
{json.dumps(analysis, default=str)}

The student's priority gap skills are:
{json.dumps(gap_skills)}

Generate exactly THREE beginner-friendly or intermediate
portfolio project ideas.

Rules:
- Every project must address at least one skill from the
  student's priority gap skills.
- Use only the exact skill names provided above in required_skills.
- Projects should be realistic for a student to build.
- Do not claim that a project guarantees employment.
- Do not mention salaries, vacancies or specific employers.
- Include practical tools and clear evaluation criteria.

Return ONLY a valid JSON array.
Do not include Markdown or explanations outside the JSON.

Use this exact structure:

[
  {{
    "title": "Project title",
    "problem_statement": "What problem does it solve?",
    "required_skills": ["Skill name"],
    "suggested_tools": ["Tool 1", "Tool 2"],
    "difficulty": "Beginner",
    "expected_deliverable": "What will the student build?",
    "evaluation_criteria": [
      "Criterion 1",
      "Criterion 2",
      "Criterion 3"
    ]
  }}
]
"""

    cache = get_cache()

    cache_key = make_cache_key(
        "generate_projects",
        {
            "analysis": analysis,
            "profile": profile
        }
    )

    if cache_key in cache:
        return cache[cache_key]

    success, response, error = call_gemini(prompt)

    if success:
        try:
            raw_projects = extract_json(response)

            projects = validate_projects(
                raw_projects,
                gap_skills
            )

            result = AIResult(
                ok=True,
                data=projects,
                text="Three project ideas generated successfully.",
                reason="",
                used_fallback=False
            )

        except Exception as validation_error:

            fallback_projects = generate_projects_fallback(
                analysis,
                profile
            )

            result = AIResult(
                ok=False,
                data=fallback_projects,
                reason=str(validation_error),
                used_fallback=True
            )

    else:
        fallback_projects = generate_projects_fallback(
            analysis,
            profile
        )

        result = AIResult(
            ok=False,
            data=fallback_projects,
            reason=error,
            used_fallback=True
        )

    # Cache successful responses only. Do not cache temporary API failures
    # or validation fallbacks, so the user can try again later.
    if result.ok:
        cache[cache_key] = result

    return result