import streamlit as st

from src.data_loader import (
    load_skills_catalog,
    load_roles_skills,
    validate_data,
    get_roles,
)


def render():

    st.title("Your Profile")

    st.write(
        "Tell DataSphere about your learning background so it can "
        "analyze your skills and build a learning plan."
    )

    # --------------------------------------------------
    # 1. LOAD DATASETS
    # --------------------------------------------------

    try:

        catalog = load_skills_catalog()
        roles_data = load_roles_skills()

        problems = validate_data(catalog, roles_data)

        if problems:

            st.error("There are problems in the project datasets:")

            for problem in problems:
                st.write(f"- {problem}")

            return

        roles = get_roles(roles_data)

        all_skills = sorted(
            catalog["skill"].dropna().unique().tolist()
        )

    except Exception as error:

        st.error(f"Could not load the project data: {error}")
        return


    # --------------------------------------------------
    # 2. EXISTING PROFILE
    # --------------------------------------------------

    profile = st.session_state.get("profile", {})


    # --------------------------------------------------
    # 3. PERSONAL INFORMATION
    # --------------------------------------------------

    st.markdown("### Personal Information")

    name = st.text_input(
        "Your name",
        value=profile.get("name", ""),
        placeholder="Enter your name"
    )

    semester_options = list(range(1, 9))

    old_semester = profile.get("semester", 1)

    try:
        old_semester = int(old_semester)
    except (ValueError, TypeError):
        old_semester = 1

    if old_semester not in semester_options:
        old_semester = 1

    semester = st.selectbox(
        "Current semester",
        semester_options,
        index=semester_options.index(old_semester)
    )

    degree = st.text_input(
        "Degree / Program",
        value=profile.get("degree", "BS Data Science"),
        placeholder="e.g. BS Data Science"
    )


    # --------------------------------------------------
    # 4. SKILLS
    # --------------------------------------------------

    st.divider()

    st.markdown("### Your Skills")

    st.write(
        "Select the skills you already have. Then choose your current "
        "level for each selected skill."
    )

    old_skills = profile.get("skills", {})

    default_skills = [
        skill for skill in old_skills
        if skill in all_skills
    ]

    selected_skills = st.multiselect(
        "Select your skills",
        options=all_skills,
        default=default_skills,
        help="You can select multiple skills."
    )

    skill_levels = {}

    if selected_skills:

        st.markdown("#### Set your skill levels")

        level_options = {
            "Beginner": 1,
            "Working knowledge": 2,
            "Strong": 3
        }

        level_names = {
            1: "Beginner",
            2: "Working knowledge",
            3: "Strong"
        }

        for skill in selected_skills:

            old_level = old_skills.get(skill, 1)

            try:
                old_level = int(old_level)
            except (ValueError, TypeError):
                old_level = 1

            old_level = max(1, min(3, old_level))

            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**{skill}**")

            with col2:

                selected_level = st.selectbox(
                    f"Level for {skill}",
                    options=list(level_options.keys()),
                    index=list(level_options.values()).index(old_level),
                    key=f"profile_level_{skill}"
                )

            skill_levels[skill] = level_options[selected_level]

    else:

        st.info(
            "You haven't selected any skills yet. "
            "You can still save your profile and add skills later."
        )


    # --------------------------------------------------
    # 5. CAREER DIRECTION
    # --------------------------------------------------

    st.divider()

    st.markdown("### Career Direction")

    old_role = profile.get("target_role", "")

    if old_role in roles:
        role_index = roles.index(old_role)
    else:
        role_index = 0

    target_role = st.selectbox(
        "What role are you working towards?",
        options=roles,
        index=role_index if roles else None
    )

    old_interests = profile.get("interests", [])

    interests_text = st.text_input(
        "Your interests",
        value=", ".join(old_interests),
        placeholder="e.g. Artificial Intelligence, Data Visualization"
    )


    # --------------------------------------------------
    # 6. WEEKLY STUDY HOURS
    # --------------------------------------------------

    old_hours = profile.get("weekly_hours", 5)

    try:
        old_hours = int(old_hours)
    except (ValueError, TypeError):
        old_hours = 5

    old_hours = max(1, min(40, old_hours))

    weekly_hours = st.slider(
        "How many hours can you study per week?",
        min_value=1,
        max_value=40,
        value=old_hours
    )


    # --------------------------------------------------
    # 7. SAVE PROFILE
    # --------------------------------------------------

    st.divider()

    if st.button(
        "Save My Profile",
        type="primary",
        use_container_width=True
    ):

        if not name.strip():

            st.error("Please enter your name.")
            return

        if not target_role:

            st.error("Please select a target role.")
            return

        interests = [
            item.strip()
            for item in interests_text.split(",")
            if item.strip()
        ]

        # Save profile
        st.session_state["profile"] = {

            "name": name.strip(),

            "semester": semester,

            "degree": degree.strip(),

            "skills": skill_levels,

            "target_role": target_role,

            "interests": interests,

            "weekly_hours": weekly_hours
        }

        # Request navigation to Dashboard.
        # app.py will process this BEFORE creating its radio widget.

        st.session_state["pending_page"] = "Dashboard"

        st.success("Your profile has been saved successfully!")

        st.rerun()