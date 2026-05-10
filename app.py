import streamlit as st
import uuid
import hashlib
import pandas as pd
import os
import time
import requests
from firebase_service import (

    save_evaluation,

    save_talent_vault,

    save_form_response,

    save_resume_metadata,

    save_video_metadata,

    save_conversation_metadata,

    save_requirement
)
from dotenv import load_dotenv

from ingestion import ImpexusIngestor
from evaluation_engine import MultiStageEval
from evaluator import evaluate_resume
from evaluator import detect_ai
from resume_processor import extract_text_from_pdf
from talent_vault import TalentVault
from eye import analyze_video


# ---------------------------------------------------
# ENV
# ---------------------------------------------------

load_dotenv()


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(

    page_title="AI Trainer Evaluation Engine",

    layout="wide"
)


# ---------------------------------------------------
# TAVUS
# ---------------------------------------------------

def create_tavus_conversation():

    url = (
        "https://tavusapi.com/v2/conversations"
    )

    payload = {

        "replica_id": "rf4e9d9790f0",

        "persona_id": "pa37215d10e6"
    }

    headers = {

        "x-api-key":
            os.getenv("TAVUS_API_KEY"),

        "Content-Type":
            "application/json"
    }

    try:

        response = requests.post(

            url,

            json=payload,

            headers=headers,

            timeout=30
        )

        data = response.json()

        print("TAVUS:", data)

        return data

    except Exception as e:

        print(
            "Tavus Error:",
            str(e)
        )

        return None


# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if "requirement" not in st.session_state:

    st.session_state.requirement = None


# ---------------------------------------------------
# INIT
# ---------------------------------------------------

vault = TalentVault()

engine = MultiStageEval()


# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.title(
    "AI-Powered Trainer Evaluation Engine"
)

st.caption(
    "Evaluating pedagogical capability under friction."
)


# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:

    st.header(
        "Requirement Ingestion"
    )

    if st.button(
        "Load Java + DSA Requirement"
    ):

        ingestor = ImpexusIngestor()

        st.session_state.requirement = (

            ingestor.derive_engagement(

                subject="Java with DSA",

                toc=[
                    "Recursion",
                    "Trees",
                    "Sorting"
                ],

                duration=40,

                budget=40000,

                mode="online",

                batch_size=30,

                project="mini"
            )
        )

        st.success(
            "Requirement Loaded"
        )
        save_requirement(
    st.session_state.requirement
)


# ---------------------------------------------------
# REQUIREMENT DISPLAY
# ---------------------------------------------------

if st.session_state.requirement:

    req = st.session_state.requirement

    st.subheader(
        "Engagement Requirement"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Subject",
        req["meta"]["subject"]
    )

    c2.metric(
        "Duration",
        f"{req['meta']['duration']} hrs"
    )

    c3.metric(
        "Batch Size",
        req["meta"]["batch_size"]
    )

    st.info(
        req["persona"]
    )


# ---------------------------------------------------
# CANDIDATE FORM
# ---------------------------------------------------

if st.session_state.requirement:

    st.divider()

    st.header(
        "Candidate Evaluation Form"
    )

    st.warning(
        "This evaluation intentionally includes "
        "high-friction tasks to assess patience, "
        "reasoning, and pedagogical depth."
    )

    # ---------------------------------------------
    # BASIC DETAILS
    # ---------------------------------------------

    name = st.text_input(
        "Full Name"
    )

    email = st.text_input(
        "Email"
    )

    # ---------------------------------------------
    # TASK RESPONSES
    # ---------------------------------------------

    responses = {}

    for task in req["tasks"]:

        st.write(
            f"### {task['cap']}"
        )

        responses[task["id"]] = st.text_area(

            task["task"],

            height=180,

            key=task["id"]
        )

    # ---------------------------------------------
    # ADAPTIVE BRANCH
    # ---------------------------------------------

    diag_response = responses.get(
        "CAP_DIAG",
        ""
    )

    if len(diag_response.split()) < 25:

        st.error(
            "Low-detail diagnostic reasoning detected."
        )

        responses["ADAPTIVE"] = st.text_area(

            "Adaptive Challenge:\n\n"
            "Explain stack memory behavior during "
            "recursive Fibonacci execution in Java.",

            height=180
        )

    # ---------------------------------------------
    # VIDEO UPLOAD
    # ---------------------------------------------

    st.subheader(
        "Mandatory Demo Video"
    )

    st.caption(
        "Upload a short teaching demo video."
    )

    video_file = st.file_uploader(

        "Upload Demo Video",

        type=["mp4"]
    )

    # ---------------------------------------------
    # RESUME UPLOAD
    # ---------------------------------------------

    st.subheader(
        "Resume Upload"
    )

    resume_file = st.file_uploader(

        "Upload Resume PDF",

        type=["pdf"]
    )

    # ---------------------------------------------
    # CONVERSATIONAL AI INTERVIEW
    # ---------------------------------------------



    st.subheader(
        "Conversational AI Interview"
    )

    st.caption(
        "Take a live adaptive interview "
        "with the AI evaluator."
    )

    st.link_button(

        "Start AI Interview",

        "https://tavus.daily.co/ce4d32ba69301466"
    )

    # ---------------------------------------------
    # SUBMIT
    # ---------------------------------------------

    if st.button(
        "Run Evaluation"
    ):

        # -----------------------------------------
        # VALIDATION
        # -----------------------------------------

        if not name:

            st.error(
                "Name required."
            )

            st.stop()

        if not email:

            st.error(
                "Email required."
            )

            st.stop()

        if not video_file:

            st.error(
                "Demo video mandatory."
            )

            st.stop()

        if not resume_file:

            st.error(
                "Resume mandatory."
            )

            st.stop()

        # -----------------------------------------
        # MINIMUM FRICTION CHECK
        # -----------------------------------------

        total_words = len(

            " ".join(
                responses.values()
            ).split()
        )

        if total_words < 120:

            st.error(
                "Responses too short for meaningful "
                "evaluation."
            )

            st.stop()

        # -----------------------------------------
        # EVALUATION START
        # -----------------------------------------

        with st.spinner(
            "Running multi-stage evaluation..."
        ):

            time.sleep(1)

            # -------------------------------------
            # SAVE VIDEO
            # -------------------------------------

            temp_video_path = (
                "temp_video.mp4"
            )

            with open(
                temp_video_path,
                "wb"
            ) as f:

                f.write(
                    video_file.read()
                )

            # -------------------------------------
            # VIDEO ANALYSIS
            # -------------------------------------

            video_results = analyze_video(
                temp_video_path
            )

            # -------------------------------------
            # RESUME EXTRACTION
            # -------------------------------------

            resume_text = extract_text_from_pdf(
                resume_file
            )

            # -------------------------------------
            # AI AUTHENTICITY
            # -------------------------------------

            combined_text = " ".join(
                responses.values()
            )

            ai_score = detect_ai(
                combined_text
            )

            # -------------------------------------
            # FORM EVALUATION
            # -------------------------------------

            form_results = (
                engine.evaluate_candidate(

                    responses,

                    ai_score
                )
            )

            # -------------------------------------
            # RESUME EVALUATION
            # -------------------------------------

            resume_results = evaluate_resume(

                resume_text,

                str(req)
            )

            # -------------------------------------
            # FINAL COMPOSITE SCORE
            # -------------------------------------

            final_score = (

                form_results["final_score"]
                * 0.70

                +

                resume_results["final_score"]
                * 0.20

                +

                ai_score
                * 0.10
            )

            # -------------------------------------
            # VIDEO PENALTY
            # -------------------------------------

            if video_results["risk"] == "HIGH":

                final_score -= 15

            elif video_results["risk"] == "MEDIUM":

                final_score -= 7

            elif video_results["risk"] == "INVALID":

                final_score -= 20

            final_score = round(
                final_score,
                2
            )

            # -------------------------------------
            # FINAL STATUS
            # -------------------------------------

            status = (

                "SELECTED"

                if final_score >= 70

                else "REJECTED"
            )

            # -------------------------------------
            # BUILD VAULT ENTRY
            # -------------------------------------

            candidate = {

                "candidate_id":

                    str(
                        uuid.uuid4()
                    )[:8],

                "name": name,

                "hashed_email":

                    hashlib.sha256(
                        email.encode()
                    ).hexdigest(),

                "status": status,

                "final_score": final_score,

                # Resume metrics
                "skill_match":

                    resume_results.get(
                        "skill_match",
                        0
                    ),

                "experience_score":

                    resume_results.get(
                        "depth_of_experience",
                        0
                    ),

                "role_alignment":

                    resume_results.get(
                        "role_alignment",
                        0
                    ),

                "additional_strengths":

                    resume_results.get(
                        "additional_strengths",
                        0
                    ),

                # Validation
                "credibility_score":

                    resume_results.get(
                        "validation",
                        {}
                    ).get(
                        "credibility_score",
                        0
                    ),

                "severity":

                    resume_results.get(
                        "validation",
                        {}
                    ).get(
                        "severity",
                        "Low"
                    ),

                "red_flags":

                    resume_results.get(
                        "validation",
                        {}
                    ).get(
                        "red_flags",
                        []
                    ),

                # Capability scores
                "capabilities":

                    form_results.get(
                        "capabilities",
                        {}
                    ),

                # Video analytics
                "video_integrity":
                    video_results,

                # Tavus
                "conversational_ai_used":
                    True,

                "subjects": [
                    "Java",
                    "DSA"
                ],

                "reason":

                    form_results.get(
                        "reason",
                        "Evaluation complete."
                    )
            }
            # -------------------------------------
            # SAVE FORM RESPONSES
            # -------------------------------------

            save_form_response({

                "candidate_id":
                    candidate["candidate_id"],

                "responses":
                    responses,

                "word_count":

                    len(
                        combined_text.split()
                    ),

                "adaptive_triggered":

                    "ADAPTIVE" in responses
            })


            # -------------------------------------
            # SAVE RESUME METADATA
            # -------------------------------------

            save_resume_metadata({

                "candidate_id":
                    candidate["candidate_id"],

                "skill_match":

                    resume_results.get(
                        "skill_match",
                        0
                    ),

                "experience_score":

                    resume_results.get(
                        "depth_of_experience",
                        0
                    ),

                "role_alignment":

                    resume_results.get(
                        "role_alignment",
                        0
                    ),

                "credibility_score":

                    resume_results.get(
                        "validation",
                        {}
                    ).get(
                        "credibility_score",
                        0
                    ),

                "severity":

                    resume_results.get(
                        "validation",
                        {}
                    ).get(
                        "severity",
                        "Low"
                    )
            })


            # -------------------------------------
            # SAVE VIDEO METADATA
            # -------------------------------------

            save_video_metadata({

                "candidate_id":
                    candidate["candidate_id"],

                "video_results":
                    video_results
            })


            # -------------------------------------
            # SAVE CONVERSATION METADATA
            # -------------------------------------

            save_conversation_metadata({

                "candidate_id":
                    candidate["candidate_id"],

                "platform":
                    "Tavus",

                "conversation_url":

                    "https://tavus.daily.co/c2555bed6337a4d8",

                "status":
                    "initiated"
            })


            # -------------------------------------
            # SAVE EVALUATION
            # -------------------------------------

            save_evaluation(candidate)


            # -------------------------------------
            # SAVE TALENT VAULT
            # -------------------------------------

            if status == "SELECTED":

                save_talent_vault(candidate)


            

            # -------------------------------------
            # SAVE TO VAULT
            # -------------------------------------

            saved = vault.save_candidate(
                candidate
            )

            # -------------------------------------
            # DISPLAY RESULTS
            # -------------------------------------

            st.success(
                f"Final Score: {final_score}"
            )

            st.write(
                f"Final Status: {status}"
            )

            if not saved:

                st.warning(
                    "Candidate already exists in vault."
                )

            # -------------------------------------
            # ANALYTICS
            # -------------------------------------
            # -------------------------------------
# AI AUTHENTICITY ANALYSIS
# -------------------------------------

            st.subheader(
                "AI Authenticity Analysis"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.metric(

                    "Human Authenticity Score",

                    f"{round(ai_score, 2)}%"
                )

            with col2:

                if ai_score >= 75:

                    st.success(
                        "Likely authentic response behavior."
                    )

                elif ai_score >= 45:

                    st.warning(
                        "Moderate AI-assisted patterns detected."
                    )

                else:

                    st.error(
                        "Strong synthesized response patterns detected."
                    )
            st.subheader(
                "Capability Breakdown"
            )

            st.json(
                form_results["capabilities"]
            )

            st.subheader(
                "Resume Intelligence"
            )

            st.json(
                resume_results
            )

            st.subheader(
                "Video Integrity Signals"
            )

            st.json(
                video_results
            )


# ---------------------------------------------------
# TALENT VAULT
# ---------------------------------------------------

st.divider()

st.header(
    "Talent Vault Analytics"
)

analytics = vault.get_analytics()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Candidates",
    analytics["total_candidates"]
)

c2.metric(
    "Selected",
    analytics["selected"]
)

c3.metric(
    "Rejected",
    analytics["rejected"]
)

c4.metric(
    "Selection Rate",
    f"{analytics['selection_rate']}%"
)

# ---------------------------------------------------
# TOP CANDIDATES
# ---------------------------------------------------

top_candidates = vault.get_top_candidates()

if top_candidates:

    st.subheader(
        "Top Ranked Candidates"
    )

    df = pd.DataFrame(
        top_candidates
    ).fillna(0)

    st.dataframe(df)

# ---------------------------------------------------
# REQUIREMENT MATCHING
# ---------------------------------------------------

if (

    st.session_state.requirement

    and

    st.button(
        "Run Auto-Matching"
    )
):

    matches = vault.match_requirement(

        st.session_state.requirement[
            "meta"
        ]
    )

    st.subheader(
        "Recommended Trainers"
    )

    st.dataframe(
        pd.DataFrame(matches)
    )