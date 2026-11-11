import streamlit as st
from datetime import date

from src.ui_components import page_header


def get_tracker():
    if "tracker" not in st.session_state:
        st.session_state["tracker"] = {
            "practised_skills": [],
            "projects": [],
            "learning_log": []
        }

    return st.session_state["tracker"]


def render():
    page_header(
        "Progress Tracker",
        "Record your learning, projects, and practical evidence."
    )

    tracker = get_tracker()

    total_hours = sum(
        float(item.get("hours", 0))
        for item in tracker["learning_log"]
    )

    completed_projects = sum(
        1 for project in tracker["projects"]
        if project.get("status") == "Completed"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Hours logged", f"{total_hours:g}")
    col2.metric("Projects completed", completed_projects)
    col3.metric("Skills practised", len(tracker["practised_skills"]))

    st.caption(
        "Your tracker is stored in this browser session. "
        "Refreshing or closing the session may clear it."
    )

    practice_tab, project_tab, log_tab = st.tabs([
        "Practice", "Projects & Evidence", "Learning Log"
    ])

    # PRACTICE TAB
    with practice_tab:
        st.subheader("Record skill practice")

        profile = st.session_state.get("profile", {})
        available_skills = list(profile.get("skills", {}).keys())

        if not available_skills:
            available_skills = ["Python", "SQL", "Excel"]

        with st.form("practice_form"):
            skill = st.selectbox("Skill practised", available_skills)
            practice_date = st.date_input("Date", value=date.today())
            notes = st.text_area("What did you practise?")
            submitted = st.form_submit_button("Save practice")

            if submitted:
                tracker["practised_skills"].append({
                    "skill": skill,
                    "date": str(practice_date),
                    "notes": notes.strip()
                })
                st.success("Practice entry saved.")
                st.rerun()

        if tracker["practised_skills"]:
            st.markdown("**Your practice history**")

            for item in reversed(tracker["practised_skills"]):
                with st.container(border=True):
                    st.write(f"**{item['skill']}** · {item['date']}")
                    st.write(item.get("notes") or "No notes added.")
        else:
            st.info("No practice entries yet. Add your first one above.")

    # PROJECTS TAB
    with project_tab:
        st.subheader("Your projects")

        if not tracker["projects"]:
            st.info(
                "No projects added yet. Visit Project Challenges "
                "and add a project to your tracker."
            )

        for index, project in enumerate(tracker["projects"]):
            with st.container(border=True):
                st.write(f"**{project['title']}**")

                status_options = [
                    "Planned", "In progress", "Completed"
                ]

                current_status = project.get("status", "Planned")

                new_status = st.selectbox(
                    "Project status",
                    status_options,
                    index=status_options.index(current_status),
                    key=f"project_status_{index}"
                )

                project["status"] = new_status

                st.write(
                    "Skills: " +
                    ", ".join(project.get("skills", []))
                )

                github_url = st.text_input(
                    "GitHub repository URL",
                    value=project.get("github_url", ""),
                    key=f"github_{index}"
                )

                evidence = st.text_area(
                    "Evidence / project notes",
                    value=project.get("evidence_note", ""),
                    key=f"evidence_{index}"
                )

                if st.button("Save project details", key=f"save_project_{index}"):
                    if github_url and not github_url.startswith(
                        "https://github.com/"
                    ):
                        st.error("Enter a valid GitHub repository URL.")
                    else:
                        project["github_url"] = github_url.strip()
                        project["evidence_note"] = evidence.strip()
                        st.success("Project details saved.")
                        st.rerun()

    # LEARNING LOG TAB
    with log_tab:
        st.subheader("Log your learning hours")

        with st.form("learning_log_form"):
            log_date = st.date_input("Date", value=date.today())
            hours = st.number_input(
                "Hours studied",
                min_value=0.5,
                max_value=24.0,
                value=1.0,
                step=0.5
            )
            note = st.text_area("What did you work on?")
            submitted = st.form_submit_button("Save learning log")

            if submitted:
                tracker["learning_log"].append({
                    "date": str(log_date),
                    "hours": hours,
                    "note": note.strip()
                })
                st.success("Learning hours saved.")
                st.rerun()

        if tracker["learning_log"]:
            st.markdown("**Your learning history**")

            for item in reversed(tracker["learning_log"]):
                with st.container(border=True):
                    st.write(
                        f"**{item['hours']} hours** · {item['date']}"
                    )
                    st.write(item.get("note") or "No notes added.")
        else:
            st.info("No learning hours logged yet.")