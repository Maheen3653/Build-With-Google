
import streamlit as st
from supabase import Client, create_client


def get_supabase_client() -> Client:
    """
    Get a Supabase client isolated to the current Streamlit session.
    """

    # Reuse the client only within this user's session.
    existing_client = st.session_state.get("_supabase_client")

    if existing_client is not None:
        return existing_client

    try:
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]

    except KeyError as error:
        raise RuntimeError(
            f"Missing Supabase configuration: {error}. "
            "Check your .streamlit/secrets.toml file."
        ) from error

    if not supabase_url or not supabase_key:
        raise RuntimeError(
            "Supabase URL or publishable key is empty."
        )

    try:
        client = create_client(
            supabase_url,
            supabase_key
        )

        st.session_state["_supabase_client"] = client

        return client

    except Exception as error:
        raise RuntimeError(
            f"Could not initialize Supabase client: {error}"
        ) from error
