
import importlib

import streamlit as st

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
# 3. LOAD AND VALIDATE DATA
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


# Make datasets available to view modules
st.session_state["catalog"] = catalog
st.session_state["roles"] = roles


# --------------------------------------------------
# 4. NAVIGATION ROUTES
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
# 5. HANDLE PAGE REDIRECTION
# --------------------------------------------------

# A page can request navigation by setting pending_page.
# We process it BEFORE creating the sidebar radio widget.

if "pending_page" in st.session_state:

    requested_page = st.session_state.pop("pending_page")

    if requested_page in VIEW_MODULES:
        st.session_state["navigation_choice"] = requested_page


# Initialize navigation
if st.session_state.get("navigation_choice") not in VIEW_MODULES:

    st.session_state["navigation_choice"] = "Home"


# --------------------------------------------------
# 6. SIDEBAR
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

    selected_page = st.radio(
        "Navigation",
        options=list(VIEW_MODULES.keys()),
        key="navigation_choice",
        label_visibility="collapsed",
    )

    st.divider()

    st.caption("Your personal skill development space")


# --------------------------------------------------
# 7. MAIN CONTENT AND PAGE ROUTING
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
