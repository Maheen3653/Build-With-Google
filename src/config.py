import os
import streamlit as st

APP_NAME = "DataSphere"
APP_VERSION = "1.0.0"

GEMINI_MODEL = "gemini-3.8-flash"
GEMINI_API_KEY_NAME = "GEMINI_API_KEY"


def get_gemini_api_key():
    try:
        api_key = st.secrets.get(GEMINI_API_KEY_NAME)
        if api_key:
            return api_key
    except Exception:
        pass

    api_key = os.getenv(GEMINI_API_KEY_NAME)
    return api_key