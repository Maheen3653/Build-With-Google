import streamlit as st

from src.data_loader import load_skills_catalog, load_roles_skills, get_role_requirements
from src.skill_matcher import analyze_skills
from src.gemini_service import generate_projects
from src.ui_components import page_header, illustrative_banner


def render():
    page_header(
        "Project Challenges",
        "Turn your learning into practical portfolio evidence."
    )
    illustrative_banner()

    profile = st.session_state.get("profile")

    if not profile:
        st.warning("Create your profile first to get relevant projects.")
        if st.button("Go to Profile"):
            st.session_state["page"] = "Profile"
            st.rerun()
        return

    catalog = load_skills_catalog()
    roles = load_roles_skills()

    requirements = get_role_requirements(
        roles, profile["target_role"]
    )

    analysis = analyze_skills(
        profile["skills"], requirements, catalog
    )

    if analysis.get("empty"):
        st.info("No role requirements are available for project matching.")
        return

    if st.button("Generate project challenges", type="primary"):
        with st.spinner("Creating projects based on your skill gaps..."):
            result = generate_projects(analysis, profile)

        if result.ok and result.data:
            projects = result.data
            st.session_state["generated_projects"] = projects
            st.session_state["projects_notice"] = ""
        else:
            gaps = analysis["priority_gaps"]
            skills = [gap["skill"] for gap in gaps[:3]]

            projects = [
                {
                    "title": f"Practical {skill} Challenge",
                    "problem_statement": (
                        f"Build a small project that demonstrates "
                        f"your understanding of {skill}."
                    ),
                    "required_skills": [skill],
                    "suggested_tools": [skill],
                    "difficulty": "Beginner",
                    "expected_deliverable": (
                        "A working project with a README and examples."
                    ),
                    "evaluation_criteria": [
                        "Correct implementation",
                        "Clear documentation",
                        "Useful demonstration"
                    ]
                }
                for skill in skills
            ]

            st.session_state["generated_projects"] = projects
            st.session_state["projects_notice"] = (
                "AI is unavailable. Showing built-in project ideas instead."
            )

    projects = st.session_state.get("generated_projects", [])

    if st.session_state.get("projects_notice"):
        st.warning(st.session_state["projects_notice"])

    if not projects:
        st.info("Generate project challenges to see your recommendations.")
        return

    gap_names = {
        item["skill"] for item in analysis["priority_gaps"]
    }

    for index, project in enumerate(projects):
        with st.container(border=True):
            st.subheader(project["title"])
            st.write(project["problem_statement"])

            st.markdown("**Required skills**")
            for skill in project["required_skills"]:
                if skill in gap_names:
                    st.markdown(f"- 🔶 {skill} — current skill gap")
                else:
                    st.markdown(f"- {skill}")

            st.write("**Suggested tools:** " +
                     ", ".join(project["suggested_tools"]))
            st.write("**Difficulty:** " + project["difficulty"])
            st.write("**Expected deliverable:**")
            st.write(project["expected_deliverable"])

            st.markdown("**Evaluation criteria**")
            for criterion in project["evaluation_criteria"]:
                st.write(f"- {criterion}")

            linked_gaps = [
                skill for skill in project["required_skills"]
                if skill in gap_names
            ]

            st.caption(
                "Linked to gaps: " +
                (", ".join(linked_gaps) if linked_gaps else "No direct gap match")
            )

            if st.button("Add to tracker", key=f"add_project_{index}"):
                tracker = st.session_state.setdefault(
                    "tracker",
                    {
                        "practised_skills": [],
                        "projects": [],
                        "learning_log": []
                    }
                )

                existing = any(
                    item["title"] == project["title"]
                    for item in tracker["projects"]
                )

                if existing:
                    st.info("This project is already in your tracker.")
                else:
                    tracker["projects"].append({
                        "title": project["title"],
                        "status": "Planned",
                        "github_url": "",
                        "evidence_note": "",
                        "skills": project["required_skills"]
                    })
                    st.success("Project added to your tracker.")