import streamlit as st
import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore

# -----------------------------------------

# PREVENT MULTIPLE INITIALIZATIONS

# -----------------------------------------

if not firebase_admin._apps:
    cred = credentials.Certificate(

    dict(
        st.secrets["firebase"]
    )
)

    firebase_admin.initialize_app(
    cred
)


# -----------------------------------------

# FIRESTORE CLIENT

# -----------------------------------------

db = firestore.client()
