import os
import json
import re

import requests
import uuid

from copyleaks.copyleaks import Copyleaks

from copyleaks.models.submit.ai_detection_document import (
    NaturalLanguageDocument
)
import google.generativeai as genai

from dotenv import load_dotenv


# ---------------------------------------------------
# ENV CONFIG
# ---------------------------------------------------

load_dotenv()

genai.configure(
    api_key=st.secrets[
        "GEMINI_API_KEY"
    ]
)

model = genai.GenerativeModel(
    "gemini-3.1-pro-preview"
)

AI_DETECT_API = st.secrets[
    "UNDETECTABLE_API_KEY"
]


# ---------------------------------------------------
# CLEAN JSON RESPONSE
# ---------------------------------------------------

def clean_json(text):

    text = re.sub(
        r"```json|```",
        "",
        text
    )

    match = re.search(
        r"\{[\s\S]*\}",
        text
    )

    return (
        match.group(0)
        if match
        else text.strip()
    )


# ---------------------------------------------------
# BASIC RESUME VALIDATION
# ---------------------------------------------------

def is_valid_resume(text):

    if not text or len(
        text.strip()
    ) < 50:

        return (
            False,
            "Resume is too short or empty"
        )

    keywords = [

        "experience",

        "project",

        "skills",

        "education"
    ]

    matches = sum(

        keyword in text.lower()

        for keyword in keywords
    )

    return (

        (True, "")

        if matches >= 2

        else (
            False,
            "Content lacks standard "
            "resume markers"
        )
    )


# ---------------------------------------------------
# AI AUTHENTICITY API
# ---------------------------------------------------

def detect_ai(text):

    try:

        # -----------------------------------
        # LOGIN TOKEN
        # -----------------------------------

        login_token = (
            "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJtM1dwZkh3bjlHbzFQZ0M5ekhiaUoycXl3MGZwWmdwUi03QUdiODQ4dmJZIn0.eyJleHAiOjE3Nzg1NzAzNTUsImlhdCI6MTc3ODM5NzU1NSwianRpIjoib25sdG5hOmQ0YTlmNmU2LTlhY2UtYjdiMC03NmFmLTIyYWE5NjJkNjBmYiIsImlzcyI6Imh0dHBzOi8vYXV0aC5jb3B5bGVha3MuY29tL3JlYWxtcy9jb3B5bGVha3MiLCJhdWQiOlsiYWktZ2VuZXJhdGVkLXRleHQtYXBpIiwiYXBpLWJhY2tlbmQiXSwidHlwIjoiQmVhcmVyIiwiYXpwIjoiYXBpLXVzZXJzIiwic2lkIjoiWmlTTG1meTlPbDdWV0l3YXc1YV80ejk0Iiwic2NvcGUiOiJyb2xlcyBhcGktYmFja2VuZCBhaS1nZW5lcmF0ZWQtdGV4dC1hcGkgb3JnYW5pemF0aW9uIn0.E2xMowoKZpoWYFy5ofkilMbIeDL1hnkq3Wca7OPjWNHLvPiFx4cTkuj8JEDljFt7dnecUpMvwJFrBR9YP9ORkLFzD8jxlHyMxWOA18R3MJUtZ-YXvqu177rlDBhJjhH2JKxHkVRJLc6tJNNj6xk2qd--LL2Om5COtzAt_53j4uLRk8wvNiwrmqITATdIn5R1i65jTayVEDz3aYS3wum7k4J4HhCRpgoltA1KXRxPSs6s7sJL_9l9vLtTDkibw9rYH9TEXODLnTwbRQ48P6pYuSj3qr8EAi9ikQN6mXDoeu3g3A5a5x6cF-DKk918-cYXDIfBp5ru2wE6G3_fFJg6MQ"
        )

        # -----------------------------------
        # UNIQUE SCAN ID
        # -----------------------------------

        scan_id = str(
            uuid.uuid4()
        )

        # -----------------------------------
        # API URL
        # -----------------------------------

        url = (

            f"https://api.copyleaks.com/"
            f"v2/writer-detector/"
            f"{scan_id}/check"
        )

        # -----------------------------------
        # PAYLOAD
        # -----------------------------------

        payload = {

            "text": text,

            "sandbox": True,

            "explain": True,

            "sensitivity": 2
        }

        # -----------------------------------
        # HEADERS
        # -----------------------------------

        headers = {

            "Authorization":

                f"Bearer {login_token}",

            "Content-Type":
                "application/json",

            "Accept":
                "application/json"
        }

        # -----------------------------------
        # REQUEST
        # -----------------------------------

        response = requests.post(

            url,

            json=payload,

            headers=headers,

            timeout=30
        )

        result = response.json()

        print(
            "COPYLEAKS:",
            result
        )

        # -----------------------------------
        # EXTRACT AI SCORE
        # -----------------------------------

        ai_score = (

    result.get(
        "summary",
        {}
    ).get(
        "ai",
        0.5
    )
)

        human_score = (
    1 - ai_score
) * 100

        # -----------------------------------
        # EMOJI PENALTY
        # -----------------------------------

        suspicious_symbols = [

            "✨",
            "🔥",
            "🚀",
            "💡",
            "😊",
            "👍",
            "🎯",
            "🤖",
            "—"
        ]

        symbol_hits = sum(

            symbol in text

            for symbol in suspicious_symbols
        )

        if symbol_hits > 0:

            human_score -= (
                symbol_hits * 5
            )

        # -----------------------------------
        # CLAMP
        # -----------------------------------

        human_score = max(

            0,

            min(
                human_score,
                100
            )
        )

        return round(
            human_score,
            2
        )

    except Exception as e:

        print(
            "AI Detection Error:",
            str(e)
        )

        return 70


# ---------------------------------------------------
# RESUME EVALUATION
# ---------------------------------------------------

def evaluate_resume(
    resume,
    jd
):

    valid, message = is_valid_resume(
        resume
    )

    if not valid:

        return {

            "name": "Invalid",

            "skill_match": 0,

            "depth_of_experience": 0,

            "role_alignment": 0,

            "additional_strengths": 0,

            "final_score": 0,

            "verdict": "REJECTED",

            "reason": message,

            "validation": {

                "credibility_score": 0,

                "severity": "High",

                "red_flags": [
                    "Invalid Resume"
                ]
            }
        }

    prompt = f"""
    You are an expert technical hiring evaluator.

    Evaluate this candidate resume against
    the provided trainer requirement.

    Evaluate:

    1. Skill Match
    2. Depth of Experience
    3. Role Alignment
    4. Additional Strengths

    Return ONLY valid JSON.

    Resume:
    {resume}

    Requirement:
    {jd}

    JSON FORMAT:

    {{
        "name": "candidate_name",

        "skill_match": 0-100,

        "depth_of_experience": 0-100,

        "role_alignment": 0-100,

        "additional_strengths": 0-100,

        "verdict": "SELECTED/REJECTED",

        "reason": "short summary"
    }}
    """

    try:

        response = model.generate_content(
            prompt
        )

        data = json.loads(
            clean_json(
                response.text
            )
        )

        # -------------------------------------------
        # BASE SCORE
        # -------------------------------------------

        base_score = (

            data.get(
                "skill_match",
                0
            ) * 0.35

            +

            data.get(
                "depth_of_experience",
                0
            ) * 0.30

            +

            data.get(
                "role_alignment",
                0
            ) * 0.25

            +

            data.get(
                "additional_strengths",
                0
            ) * 0.10
        )

        # -------------------------------------------
        # VALIDATION PASS
        # -------------------------------------------

        validation = validate_candidate(
            data,
            jd
        )

        credibility = validation.get(
            "credibility_score",
            70
        )

        severity = validation.get(
            "severity",
            "Low"
        )

        # -------------------------------------------
        # FINAL WEIGHTED SCORE
        # -------------------------------------------

        final_score = (

            base_score * 0.70

            +

            credibility * 0.30
        )

        # -------------------------------------------
        # RISK PENALTIES
        # -------------------------------------------

        if severity == "High":

            final_score *= 0.75

        elif severity == "Medium":

            final_score *= 0.90

        final_score = round(
            final_score,
            2
        )

        # -------------------------------------------
        # FINAL ENRICHMENT
        # -------------------------------------------

        data["final_score"] = final_score

        data["validation"] = validation

        return data

    except Exception as e:

        return {

            "name": "ERROR",

            "skill_match": 0,

            "depth_of_experience": 0,

            "role_alignment": 0,

            "additional_strengths": 0,

            "final_score": 0,

            "verdict": "REJECTED",

            "reason": str(e),

            "validation": {

                "credibility_score": 0,

                "severity": "High",

                "red_flags": [
                    "Evaluation Failure"
                ]
            }
        }


# ---------------------------------------------------
# VALIDATION PASS
# ---------------------------------------------------

def validate_candidate(
    candidate_data,
    jd
):

    prompt = f"""
    Critically validate this candidate profile.

    Requirement:
    {jd}

    Candidate:
    {candidate_data}

    Evaluate:
    - credibility
    - suspicious exaggerations
    - inconsistencies
    - unrealistic claims

    Return ONLY JSON.

    FORMAT:

    {{
        "credibility_score": 0-100,

        "severity": "Low/Medium/High",

        "red_flags": [
            "flag 1",
            "flag 2"
        ]
    }}
    """

    try:

        response = model.generate_content(
            prompt
        )

        data = json.loads(
            clean_json(
                response.text
            )
        )

        return {

            "credibility_score":

                data.get(
                    "credibility_score",
                    70
                ),

            "severity":

                data.get(
                    "severity",
                    "Low"
                ),

            "red_flags":

                data.get(
                    "red_flags",
                    []
                )
        }

    except Exception:

        return {

            "credibility_score": 60,

            "severity": "Medium",

            "red_flags": [
                "Validation service failure"
            ]
        }
