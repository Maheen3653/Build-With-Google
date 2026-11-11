import pandas as pd
import streamlit as st

from src.data_loader import (
    load_skills_catalog,
    load_roles_skills,
    validate_data,
    get_role_requirements,
)

from src.skill_matcher import analyze_skills


# --------------------------------------------------
# BANNER
# --------------------------------------------------

def _show_banner():

    st.info(
        "Illustrative role profiles for demonstration — "
        "not verified market data."
    )


# --------------------------------------------------
# SKILL BREAKDOWN TABLE
# --------------------------------------------------

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

        st.info("There are no skill requirements to display.")
        return

    df = pd.DataFrame(rows)

    # Style status cells without manually writing HTML.
    def style_status(column):

        styles = []

        for value in column:

            if value == "Matched":
                styles.append(
                    "background-color: #E6F0E8; "
                    "color: #3F7550; "
                    "font-weight: 600;"
                )

            elif value == "Partial":
                styles.append(
                    "background-color: #FDF1DC; "
                    "color: #9A5B00; "
                    "font-weight: 600;"
                )

            else:
                styles.append(
                    "background-color: #FBE9E4; "
                    "color: #B2412C; "
                    "font-weight: 600;"
                )

        return styles

    styled_df = (
        df.style
        .apply(style_status, subset=["Status"])
        .format({
            "Your Level": "{:.0f}",
            "Required Level": "{:.0f}"
        })
    )

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

def render():

    st.title("Dashboard")

    st.write("Your learning progress at a glance.")

    # --------------------------------------------------
    # CHECK PROFILE
    # --------------------------------------------------

    profile = st.session_state.get("profile")

    if not profile:

        st.info("You haven't created your profile yet.")

        if st.button("Create Your Profile", type="primary"):

            st.session_state["pending_page"] = "Profile"
            st.rerun()

        return

    _show_banner()

    # --------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------

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

        st.error(f"Could not analyze your skills: {error}")
        return

    # --------------------------------------------------
    # WELCOME
    # --------------------------------------------------

    st.markdown(
        f"### Welcome, {profile.get('name', 'Student')}!"
    )

    st.caption(
        f"Target role: {profile['target_role']}"
    )

    if analysis.get("empty"):

        st.warning(
            "There are no requirements available for this role."
        )

        return

    # --------------------------------------------------
    # SKILL METRICS
    # --------------------------------------------------

    matched = len(analysis.get("matched", []))
    partial = len(analysis.get("partial", []))
    missing = len(analysis.get("missing", []))

    coverage = analysis.get(
        "weighted_coverage_pct", 0
    )

    st.markdown("### Your Skill Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Skill Coverage",
        f"{coverage:.1f}%"
    )

    col2.metric(
        "Matched",
        matched
    )

    col3.metric(
        "Partial",
        partial
    )

    col4.metric(
        "Missing",
        missing
    )

    st.divider()

    # --------------------------------------------------
    # PRIORITY GAPS
    # --------------------------------------------------

    st.markdown("### Top 3 Priority Gaps")

    priority_gaps = analysis.get("priority_gaps", [])

    if priority_gaps:

        for index, gap in enumerate(
            priority_gaps[:3],
            start=1
        ):

            st.markdown(
                f"**{index}. {gap['skill']}**  \n"
                f"Your level: {gap['student_level']} · "
                f"Required level: {gap['required_level']} · "
                f"Priority score: {gap['priority_score']:.2f}"
            )

    else:

        st.success(
            "Great work! No priority skill gaps were found."
        )

    st.divider()

    # --------------------------------------------------
    # COMPLETE SKILL BREAKDOWN
    # --------------------------------------------------

    st.markdown("### Complete Skill Breakdown")

    _show_skill_table(analysis)

    st.divider()

    # --------------------------------------------------
    # CATEGORY COVERAGE
    # --------------------------------------------------

    st.markdown("### Coverage by Category")

    by_category = analysis.get("by_category", {})

    if by_category:

        chart_data = pd.DataFrame({
            "Category": list(by_category.keys()),
            "Coverage": list(by_category.values())
        }).set_index("Category")

        st.bar_chart(
            chart_data,
            y="Coverage"
        )

        st.caption(
            "Coverage percentages are calculated separately "
            "for each category."
        )

    else:

        st.info("Category coverage is not available.")

    # --------------------------------------------------
    # CALCULATION EXPLANATION
    # --------------------------------------------------

    with st.expander("How this was calculated"):

        st.markdown("""
        **1. Skill status**

        - Matched: Your skill level is equal to or higher than the required level.
        - Partial: You have some knowledge, but your level is below the requirement.
        - Missing: Your current skill level is zero.

        **2. Skill credit**

        Your credit for each skill is the smaller of your level and the required level,
        divided by the required level.

        **3. Weighted coverage**

        Each skill's credit is multiplied by its importance. The total earned
        weighted credit is divided by the total importance and multiplied by 100.

        **4. Simple coverage**

        The number of matched skills is divided by the total required skills,
        then multiplied by 100.

        **5. Priority score**

        Importance is multiplied by the fraction of the required skill level
        that you still need to develop.

        These results describe coverage against an illustrative role profile.
        They are not a job-readiness score or a hiring prediction.
        """)

    st.divider()

    # --------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------

    if st.button(
        "Explore My Skill Gaps",
        type="primary"
    ):

        st.session_state["pending_page"] = "Skill Gap"
        st.rerun()