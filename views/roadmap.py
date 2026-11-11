
import streamlit as st

from src.data_loader import (
    load_skills_catalog,
    load_roles_skills,
    get_role_requirements
)
from src.skill_matcher import analyze_skills
from src.roadmap_builder import build_roadmap
from src.gemini_service import roadmap_guidance
from src.ui_components import (
    page_header,
    illustrative_banner,
    ai_block
)


def render():
    page_header(
        "Your Learning Roadmap",
        "A structured learning plan based on your current skill gaps."
    )

    illustrative_banner()

    profile = st.session_state.get("profile")

    if not profile:
        st.warning(
            "Please create your profile before viewing your roadmap."
        )

        if st.button("Go to Profile"):
            st.session_state["pending_page"] = "Profile"
            st.rerun()

        return

    # Load data
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
        st.info(
            "No role requirements are available for this selection."
        )
        return

    # Weekly study hours
    default_hours = int(profile.get("weekly_hours", 5))

    weekly_hours = st.slider(
        "Hours you can study each week",
        min_value=1,
        max_value=40,
        value=max(1, min(default_hours, 40))
    )

    # Build roadmap
    roadmap = build_roadmap(
        analysis["priority_gaps"],
        catalog,
        weekly_hours
    )

    st.caption(
        "Illustrative planning estimates — actual learning time varies."
    )

    if roadmap.empty:
        st.success("Great! No priority skill gaps were found.")
        return

    # Display learning plan
    st.subheader("Your learning plan")

    display_columns = [
        "order",
        "skill",
        "hours_needed",
        "start_week",
        "end_week",
        "prerequisite"
    ]

    st.dataframe(
        roadmap[display_columns],
        use_container_width=True,
        hide_index=True
    )

    # Learning phases
    st.subheader("Learning phases")

    for _, item in roadmap.iterrows():

        week = int(item["start_week"])

        if week <= 2:
            phase = "Foundation"
        elif week <= 5:
            phase = "Skill building"
        else:
            phase = "Advanced practice"

        with st.expander(f"{phase} · {item['skill']}"):

            st.write(item["note"])

            st.write(
                f"Estimated hours: {item['hours_needed']}"
            )

            st.write(
                f"Weeks: {item['start_week']}–{item['end_week']}"
            )

            if item["prerequisite"]:
                st.write(
                    f"Prerequisite: {item['prerequisite']}"
                )

    # Gemini AI guidance
    st.divider()

    st.subheader("AI-powered learning guidance")

    st.write(
        "Ask Gemini to analyse your roadmap and provide "
        "personalized learning guidance."
    )

    if st.button("Get AI guidance", type="primary"):

        with st.spinner("Connecting to Gemini..."):

            # Clear previous AI cache so we test the current API key.
            st.session_state["ai_cache"] = {}

            try:
                result = roadmap_guidance(
                    roadmap,
                    analysis,
                    profile
                )

                st.session_state["roadmap_guidance_result"] = result

            except Exception as error:
                st.session_state["roadmap_guidance_result"] = None
                st.session_state["roadmap_guidance_error"] = str(error)

            else:
                st.session_state.pop(
                    "roadmap_guidance_error",
                    None
                )

    # Display result
    result = st.session_state.get(
        "roadmap_guidance_result"
    )

    error = st.session_state.get(
        "roadmap_guidance_error"
    )

    if error:
        st.error("Something went wrong while requesting Gemini.")
        with st.expander("View technical error"):
            st.code(error)

    elif result:

        st.subheader("Guidance for your journey")

        if result.ok:

            st.success("Gemini AI guidance generated successfully!")
            ai_block(result.text)

        else:

            st.warning(
                "Gemini could not generate AI guidance. "
                "Your learning roadmap is still available below."
            )

            st.write(
                "Start with the first priority gap, follow its "
                "prerequisites, and practise consistently each week."
            )

            # Show actual reason for failure
            with st.expander("Why is Gemini unavailable?"):

                reason = getattr(
                    result,
                    "reason",
                    None
                )

                if reason:
                    st.code(str(reason))
                else:
                    st.write(
                        "No technical error details were returned."
                    )
