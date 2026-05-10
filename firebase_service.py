from firebase_config import db

from datetime import datetime


# ---------------------------------------------------
# EVALUATIONS
# ---------------------------------------------------

def save_evaluation(data):

    data["created_at"] = (
        datetime.utcnow().isoformat()
    )

    db.collection(
        "evaluations"
    ).add(data)


# ---------------------------------------------------
# TALENT VAULT
# ---------------------------------------------------

def save_talent_vault(data):

    data["created_at"] = (
        datetime.utcnow().isoformat()
    )

    db.collection(
        "talent_vault"
    ).add(data)


# ---------------------------------------------------
# FORM RESPONSES
# ---------------------------------------------------

def save_form_response(data):

    data["created_at"] = (
        datetime.utcnow().isoformat()
    )

    db.collection(
        "form_responses"
    ).add(data)


# ---------------------------------------------------
# RESUME METADATA
# ---------------------------------------------------

def save_resume_metadata(data):

    data["created_at"] = (
        datetime.utcnow().isoformat()
    )

    db.collection(
        "resume_metadata"
    ).add(data)


# ---------------------------------------------------
# VIDEO METADATA
# ---------------------------------------------------

def save_video_metadata(data):

    data["created_at"] = (
        datetime.utcnow().isoformat()
    )

    db.collection(
        "video_metadata"
    ).add(data)


# ---------------------------------------------------
# CONVERSATION METADATA
# ---------------------------------------------------

def save_conversation_metadata(data):

    data["created_at"] = (
        datetime.utcnow().isoformat()
    )

    db.collection(
        "conversation_metadata"
    ).add(data)


# ---------------------------------------------------
# REQUIREMENTS
# ---------------------------------------------------

def save_requirement(data):

    data["created_at"] = (
        datetime.utcnow().isoformat()
    )

    db.collection(
        "requirements"
    ).add(data)