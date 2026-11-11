
from datetime import datetime


def get_skill_names(items):
    """Extract skill names from analysis lists."""

    names = []

    for item in items or []:
        if isinstance(item, dict):
            skill = item.get("skill", "")
        else:
            skill = str(item)

        if skill:
            names.append(skill)

    return names


def get_tracker_summary(tracker):
    """Calculate basic progress statistics."""

    tracker = tracker or {}

    practice = tracker.get("practised_skills", [])
    projects = tracker.get("projects", [])
    learning_log = tracker.get("learning_log", [])

    total_hours = 0

    for entry in learning_log:
        try:
            total_hours += float(entry.get("hours", 0))
        except (ValueError, TypeError, AttributeError):
            pass

    completed_projects = sum(
        1 for project in projects
        if project.get("status") == "Completed"
    )

    return {
        "practised_skills": len(practice),
        "total_projects": len(projects),
        "completed_projects": completed_projects,
        "total_hours": total_hours
    }


def build_report(profile, analysis, tracker):
    """
    Builds a complete Markdown progress and skill-gap report.

    Parameters:
        profile: Student profile dictionary
        analysis: Skill analysis dictionary
        tracker: Student progress dictionary

    Returns:
        Markdown report as a string
    """

    profile = profile or {}
    analysis = analysis or {}
    tracker = tracker or {}

    # ------------------------------------------
    # PROFILE INFORMATION
    # ------------------------------------------

    name = profile.get("name", "Student")
    degree = profile.get("degree", "Not specified")
    semester = profile.get("semester", "Not specified")
    target_role = profile.get("target_role", "Not specified")
    weekly_hours = profile.get("weekly_hours", 0)

    # ------------------------------------------
    # SKILL ANALYSIS
    # ------------------------------------------

    weighted_coverage = analysis.get(
        "weighted_coverage_pct", 0
    )

    simple_coverage = analysis.get(
        "simple_coverage_pct", 0
    )

    strengths = get_skill_names(
        analysis.get("strengths", [])
    )

    matched = get_skill_names(
        analysis.get("matched", [])
    )

    partial = get_skill_names(
        analysis.get("partial", [])
    )

    missing = get_skill_names(
        analysis.get("missing", [])
    )

    priority_gaps = get_skill_names(
        analysis.get("priority_gaps", [])
    )

    # ------------------------------------------
    # PROGRESS SUMMARY
    # ------------------------------------------

    progress = get_tracker_summary(tracker)

    # ------------------------------------------
    # NEXT ACTIONS
    # ------------------------------------------

    next_actions = []

    for skill in priority_gaps[:3]:
        next_actions.append(
            f"Focus on improving **{skill}**."
        )

    projects = tracker.get("projects", [])

    planned_projects = [
        project for project in projects
        if project.get("status") != "Completed"
    ]

    for project in planned_projects[:3]:
        next_actions.append(
            f"Work on the project **{project.get('title', 'Untitled Project')}**."
        )

    if not next_actions:
        next_actions.append(
            "Continue practising your skills and build a portfolio project."
        )

    # ------------------------------------------
    # BUILD MARKDOWN REPORT
    # ------------------------------------------

    report = []

    report.append("# DataSphere — Student Progress Report")
    report.append("")

    report.append(
        f"**Generated:** {datetime.now().strftime('%d %B %Y, %I:%M %p')}"
    )

    report.append("")
    report.append("---")
    report.append("")

    # Student profile

    report.append("## 1. Student Profile")
    report.append("")
    report.append(f"- **Name:** {name}")
    report.append(f"- **Degree:** {degree}")
    report.append(f"- **Semester:** {semester}")
    report.append(f"- **Target Role:** {target_role}")
    report.append(f"- **Weekly Study Hours:** {weekly_hours}")
    report.append("")

    # Skill analysis

    report.append("## 2. Skill Gap Analysis")
    report.append("")

    report.append(
        f"- **Weighted Coverage:** {weighted_coverage:.1f}%"
        if isinstance(weighted_coverage, (int, float))
        else f"- **Weighted Coverage:** {weighted_coverage}"
    )

    report.append(
        f"- **Simple Coverage:** {simple_coverage:.1f}%"
        if isinstance(simple_coverage, (int, float))
        else f"- **Simple Coverage:** {simple_coverage}"
    )

    report.append("")

    report.append(
        "> Coverage is calculated from illustrative sample "
        "requirements; this is not a guarantee of employment "
        "or a validated job-readiness score."
    )

    report.append("")

    # Skill categories

    report.append("### Matched Skills")
    report.append("")

    if matched:
        report.extend([f"- {skill}" for skill in matched])
    else:
        report.append("- No matched skills recorded.")

    report.append("")
    report.append("### Partially Matched Skills")
    report.append("")

    if partial:
        report.extend([f"- {skill}" for skill in partial])
    else:
        report.append("- No partially matched skills recorded.")

    report.append("")
    report.append("### Missing Skills")
    report.append("")

    if missing:
        report.extend([f"- {skill}" for skill in missing])
    else:
        report.append("- No missing skills recorded.")

    report.append("")
    report.append("### Strengths")
    report.append("")

    if strengths:
        report.extend([f"- {skill}" for skill in strengths])
    else:
        report.append("- Continue building your existing strengths.")

    report.append("")
    report.append("### Priority Skill Gaps")
    report.append("")

    if priority_gaps:
        report.extend([f"- {skill}" for skill in priority_gaps])
    else:
        report.append("- No priority gaps recorded.")

    report.append("")

    # Progress

    report.append("## 3. Learning Progress")
    report.append("")

    report.append(
        f"- **Skills Practised:** {progress['practised_skills']}"
    )

    report.append(
        f"- **Projects Added:** {progress['total_projects']}"
    )

    report.append(
        f"- **Completed Projects:** {progress['completed_projects']}"
    )

    report.append(
        f"- **Learning Hours:** {progress['total_hours']:g}"
    )

    report.append("")

    # Project evidence

    report.append("### Project Portfolio")
    report.append("")

    if projects:
        for project in projects:
            report.append(
                f"#### {project.get('title', 'Untitled Project')}"
            )

            report.append(
                f"- **Status:** {project.get('status', 'Planned')}"
            )

            skills = project.get("skills", [])

            if skills:
                report.append(
                    f"- **Skills:** {', '.join(skills)}"
                )

            github_url = project.get("github_url", "")

            if github_url:
                report.append(
                    f"- **GitHub:** {github_url}"
                )

            evidence = project.get("evidence_note", "")

            if evidence:
                report.append(
                    f"- **Evidence:** {evidence}"
                )

            report.append("")

    else:
        report.append("No projects have been added yet.")
        report.append("")

    # Practice history

    report.append("## 4. Practice History")
    report.append("")

    practice = tracker.get("practised_skills", [])

    if practice:
        for entry in practice:
            report.append(
                f"- **{entry.get('skill', 'Unknown skill')}** "
                f"({entry.get('date', 'No date')})"
            )

            if entry.get("notes"):
                report.append(f"  - {entry['notes']}")

    else:
        report.append("No practice sessions recorded.")

    report.append("")

    # Learning log

    report.append("## 5. Learning Log")
    report.append("")

    learning_log = tracker.get("learning_log", [])

    if learning_log:
        for entry in learning_log:
            report.append(
                f"- **{entry.get('date', 'No date')}** — "
                f"{entry.get('hours', 0)} hours"
            )

            if entry.get("note"):
                report.append(f"  - {entry['note']}")

    else:
        report.append("No learning hours have been logged.")

    report.append("")

    # Recommendations

    report.append("## 6. Recommended Next Actions")
    report.append("")

    for index, action in enumerate(next_actions, start=1):
        report.append(f"{index}. {action}")

    report.append("")

    # Disclaimer

    report.append("## 7. Important Notes")
    report.append("")

    report.append(
        "This report uses illustrative sample role requirements "
        "for demonstration. Skill coverage should not be treated "
        "as a hiring prediction or validated job-readiness score."
    )

    report.append("")

    report.append(
        "Includes AI-generated suggestions from Google Gemini "
        "where indicated."
    )

    report.append("")
    report.append("---")
    report.append("")
    report.append("*Generated by DataSphere.*")

    return "\n".join(report)
