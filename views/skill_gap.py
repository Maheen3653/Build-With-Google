import pandas as pd
import streamlit as st

from src.data_loader import (
    load_skills_catalog,
    load_roles_skills,
    validate_data,
    get_role_requirements,
)
from src.skill_matcher import analyze_skills


def _show_banner():
    st.info(
        "Illustrative role profiles for demonstration — "
        "not verified market data."
    )



def _show_skill_table(analysis):

    rows = []

    for status, key in [
        ("Matched", "matched"),
        ("Partial", "partial"),
        ("Missing", "missing")
    ]:

        for item in analysis.get(key, []):

            rows.append({
                "Skill": item.get("skill", ""),
                "Category": item.get("category", ""),
                "Your Level": item.get("student_level", 0),
                "Required Level": item.get("required_level", 0),
                "Status": status
            })

    if not rows:
        st.info("No skill requirements are available.")
        return

    df = pd.DataFrame(rows)

    # Display using Streamlit's native table component.
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


def render():
    st.title("Skill Gap Analysis")
    st.write(
        "Understand where you stand, which skills need improvement, "
        "and what deserves your attention first."
    )

    profile = st.session_state.get("profile")

    if not profile:
        st.info("Create your profile first to see your skill gaps.")
        if st.button("Go to Profile", type="primary"):
            st.session_state["pending_page"] = "Profile"
            st.rerun()
        return

    _show_banner()

    # Load and validate datasets
    try:
        catalog = load_skills_catalog()
        roles_data = load_roles_skills()

        problems = validate_data(catalog, roles_data)

        if problems:
            st.error("The project datasets contain problems:")
            for problem in problems:
                st.write(f"- {problem}")
            return

        requirements = get_role_requirements(
            roles_data,
            profile["target_role"]
        )

        analysis = analyze_skills(
            profile.get("skills", {}),
            requirements,
            catalog
        )

    except Exception as error:
        st.error(f"Could not calculate your skill gaps: {error}")
        return

    st.markdown(f"### Target Role: {profile['target_role']}")

    if analysis.get("empty"):
        st.warning("No skill requirements are available for this role.")
        return

    matched = len(analysis.get("matched", []))
    partial = len(analysis.get("partial", []))
    missing = len(analysis.get("missing", []))
    coverage = analysis.get("weighted_coverage_pct", 0)

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Weighted Coverage", f"{coverage:.1f}%")
    col2.metric("Matched Skills", matched)
    col3.metric("Partial Skills", partial)
    col4.metric("Missing Skills", missing)

    st.divider()

    # Full skill breakdown
    st.markdown("### Complete Skill Breakdown")
    st.write(
        "Compare your current skill levels with the levels required "
        "by your selected role."
    )

    _show_skill_table(analysis)

    st.divider()

    # Priority gaps
    st.markdown("### Your Priority Gaps")

    priority_gaps = analysis.get("priority_gaps", [])

    if priority_gaps:
        st.write(
            "These skills need attention. Higher priority scores indicate "
            "a combination of greater importance and a larger skill gap."
        )

        for index, gap in enumerate(priority_gaps, start=1):
            with st.container(border=True):
                st.markdown(f"**{index}. {gap['skill']}**")

                col1, col2, col3 = st.columns(3)

                col1.metric("Your Level", gap["student_level"])
                col2.metric("Required Level", gap["required_level"])
                col3.metric("Priority Score", f"{gap['priority_score']:.2f}")

    else:
        st.success("You have no priority gaps for this role.")

    st.divider()

    # Strong areas
    st.markdown("### Your Strong Areas")

    strengths = analysis.get("strengths", [])

    if strengths:
        st.write(
            "These are matched skills with importance level 2 or higher:"
        )
        st.write(", ".join(strengths))
    else:
        st.info(
            "No strong areas have been identified yet. "
            "Keep developing your skills."
        )

    st.divider()

    # Category chart
    st.markdown("### Coverage by Category")

    by_category = analysis.get("by_category", {})

    if by_category:
        chart_data = pd.DataFrame({
            "Category": list(by_category.keys()),
            "Coverage": list(by_category.values())
        }).set_index("Category")

        st.bar_chart(chart_data, y="Coverage")
    else:
        st.info("Category coverage is not available.")

    # Explain calculations
    with st.expander("How this was calculated"):
        st.markdown("""
        **Skill status**

        - Matched: Your level is equal to or greater than the required level.
        - Partial: Your level is above zero but below the required level.
        - Missing: Your level is zero.

        **Skill credit**

        The smaller of your current level and the required level is
        divided by the required level.

        **Weighted coverage**

        Each skill's credit is multiplied by its importance.
        All earned weighted credits are added together, divided by
        the total importance, and multiplied by 100.

        **Simple coverage**

        Matched skills are divided by the total number of required skills,
        then multiplied by 100.

        **Gap fraction**

        The remaining skill-level gap is divided by the required level.

        **Priority score**

        The gap fraction is multiplied by the skill's importance.
        This helps identify skills that are both important and incomplete.

        The figures describe your coverage against an illustrative role
        profile. They do not predict employment or hiring outcomes.
        """)

    st.divider()

    if st.button("Back to Dashboard"):
        st.session_state["pending_page"] = "Dashboard"
        st.rerun()
