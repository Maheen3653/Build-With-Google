import streamlit as st


def render():
    st.markdown(
        """
        <div style="padding: 35px 0 20px 0;">
            <p style="color:#0B7A6B; font-weight:700; letter-spacing:2px;">
                YOUR SKILLS. YOUR DIRECTION.
            </p>
            <h1 style="font-size:46px; color:#0B1F3A;">
                From Classroom Knowledge<br>
                to Industry-Ready Skills.
            </h1>
            <p style="font-size:18px; color:#526174; max-width:750px;">
                DataSphere helps students understand their current skills,
                discover learning gaps, and build a practical path toward
                their chosen career.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.subheader("Your journey in three steps")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 01 · Build your profile")
        st.write(
            "Add your academic background, current skills, "
            "interests, and weekly learning hours."
        )

    with col2:
        st.markdown("### 02 · Discover your gaps")
        st.write(
            "Compare your skills with the selected role's "
            "illustrative skill requirements."
        )

    with col3:
        st.markdown("### 03 · Take action")
        st.write(
            "Explore a learning roadmap, project challenges, "
            "and a personal progress tracker."
        )

    st.markdown("---")

    left, right = st.columns([2, 1])

    with left:
        st.subheader("A clearer way to plan your growth")
        st.write(
            "Instead of guessing what to learn next, use your profile "
            "and skill-gap analysis to identify practical next steps."
        )

        if st.button("Get started", type="primary", use_container_width=True):
            st.session_state["page"] = "Profile"
            st.rerun()

    with right:
        st.info(
            "**SDG 4 — Quality Education**\n\n"
            "Supporting relevant learning and skills development."
        )

    st.caption(
        "DataSphere uses illustrative role profiles for demonstration. "
        "These are not verified market requirements."
    )