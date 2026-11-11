import streamlit as st

from src.data_loader import (
    load_skills_catalog,
    load_roles_skills,
    get_role_requirements
)
from src.skill_matcher import analyze_skills
from src.report import build_report
from src.ui_components import page_header, illustrative_banner


def render():
    page_header(
        "Readiness Report",
        "A summary of your current skills, learning priorities, and progress."
    )

    illustrative_banner()

    profile = st.session_state.get("profile")

    if not profile:
        st.warning(
            "Your report will be available after you create your profile."
        )

        if st.button("Create Profile"):
            st.session_state["page"] = "Profile"
            st.rerun()

        return

    catalog = load_skills_catalog()
    roles = load_roles_skills()

    requirements = get_role_requirements(
        roles,
        profile["target_role"]
    )

    analysis = analyze_skills(
        profile["skills"],
        requirements,
        catalog
    )

    if analysis.get("empty"):
        st.info("There are no requirements available for this role yet.")
        return

    if "tracker" not in st.session_state:
        st.session_state["tracker"] = {
        "practised_skills": [],
        "projects": [],
        "learning_log": []
    }

    tracker = st.session_state["tracker"]

    report = build_report(
        profile,
        analysis,
        tracker
    )

    st.subheader("Your report")
    st.markdown(report)

    st.download_button(
        label="Download report",
        data=report,
        file_name="datasphere_readiness_report.md",
        mime="text/markdown",
        type="primary"
    )

    st.caption(
        "Your skill coverage is calculated from illustrative sample "
        "requirements. It is not a guarantee of employment or a "
        "validated job-readiness score."
    )