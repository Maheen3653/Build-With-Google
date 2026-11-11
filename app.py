
import importlib

import streamlit as st

from src.auth import render_auth_page, logout_user
from src.supabase_client import get_supabase_client
from src.ui_components import load_css, illustrative_banner
from src.data_loader import (
    load_skills_catalog,
    load_roles_skills,
    validate_data,
)


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="DataSphere",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# 2. LOAD CUSTOM CSS
# --------------------------------------------------

css = load_css()

st.markdown(
    f"<style>{css}</style>",
    unsafe_allow_html=True
)


# --------------------------------------------------
# 3. SUPABASE AUTHENTICATION
# --------------------------------------------------

try:
    supabase = get_supabase_client()

except Exception as error:
    st.error("DataSphere could not connect to Supabase.")
    st.caption(f"Technical detail: {error}")
    st.stop()


# Check whether the current Streamlit session
# has an active Supabase authentication session.

try:
    auth_session = supabase.auth.get_session()

except Exception as error:
    st.error("Could not verify your login session.")
    st.caption(f"Technical detail: {error}")
    st.stop()


# If there is no authenticated session,
# show the login and registration page.

if auth_session is None or auth_session.user is None:

    st.session_state.pop("auth_user", None)

    render_auth_page(supabase)

    st.stop()


# Keep the authenticated user's basic information
# available to the rest of the application.

authenticated_user = auth_session.user

st.session_state["auth_user"] = {
    "id": authenticated_user.id,
    "email": authenticated_user.email,
}


# --------------------------------------------------
# 4. LOAD AND VALIDATE APPLICATION DATA
# --------------------------------------------------

@st.cache_data
def get_application_data():

    catalog = load_skills_catalog()
    roles = load_roles_skills()
    problems = validate_data(catalog, roles)

    return catalog, roles, problems


try:
    catalog, roles, problems = get_application_data()

except Exception as error:

    st.error(
        "DataSphere could not load its data files. "
        "Please check that both CSV files exist in the data folder."
    )

    st.caption(f"Technical detail: {error}")
    st.stop()


if problems:

    st.error("Data validation failed. Please fix these issues:")

    for problem in problems:
        st.write(f"- {problem}")

    st.stop()


# Make datasets available to view modules.

st.session_state["catalog"] = catalog
st.session_state["roles"] = roles


# --------------------------------------------------
# 5. NAVIGATION ROUTES
# --------------------------------------------------

VIEW_MODULES = {
    "Home": "landing",
    "Profile": "profile",
    "Dashboard": "dashboard",
    "Skill Gap": "skill_gap",
    "Roadmap": "roadmap",
    "Projects": "projects",
    "Tracker": "tracker",
    "Report": "report_view",
}


# --------------------------------------------------
# 6. HANDLE PAGE REDIRECTION
# --------------------------------------------------

# Process pending navigation BEFORE creating
# the sidebar radio widget.

if "pending_page" in st.session_state:

    requested_page = st.session_state.pop("pending_page")

    if requested_page in VIEW_MODULES:
        st.session_state["navigation_choice"] = requested_page


# Initialize navigation.

if st.session_state.get("navigation_choice") not in VIEW_MODULES:

    st.session_state["navigation_choice"] = "Home"


# --------------------------------------------------
# 7. SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown(
        """
        <div class="ds-brand">DataSphere</div>
        <p>Discover your skills. Shape your future.</p>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # Logged-in user information.

    st.caption("SIGNED IN AS")

    st.write(st.session_state["auth_user"]["email"])

    if st.button(
        "Log out",
        use_container_width=True
    ):
        logout_user(supabase)

    st.divider()

    # Main navigation.

    selected_page = st.radio(
        "Navigation",
        options=list(VIEW_MODULES.keys()),
        key="navigation_choice",
        label_visibility="collapsed",
    )

    st.divider()

    st.caption("Your personal skill development space")


# --------------------------------------------------
# 8. MAIN CONTENT AND PAGE ROUTING
# --------------------------------------------------

illustrative_banner()

module_name = VIEW_MODULES[selected_page]

try:

    page_module = importlib.import_module(
        f"views.{module_name}"
    )

    if not hasattr(page_module, "render"):

        st.error(
            f"The {selected_page} view does not have a render() function."
        )

        st.stop()

    page_module.render()


except ModuleNotFoundError as error:

    if error.name != f"views.{module_name}":
        raise

    st.title(selected_page)

    st.info(
        f"The {selected_page} page is not ready yet. "
        "Its view file will be added during the next implementation step."
    )
