# --------------------------------------------------
# DATASPHERE FALLBACK CONTENT
# --------------------------------------------------

def get_priority_skills(analysis):
    """
    Extracts priority-gap skill names from the analysis.
    """

    gaps = analysis.get("priority_gaps", [])

    skills = []

    for gap in gaps:
        if isinstance(gap, dict):
            skill = gap.get("skill")

            if skill:
                skills.append(skill)

        elif isinstance(gap, str):
            skills.append(gap)

    return skills


def explain_gaps_fallback(analysis, profile):
    """
    Provides a basic explanation of the user's skill gaps.
    """

    gaps = get_priority_skills(analysis)

    if not gaps:
        return (
            "Your current skill profile does not show any "
            "priority gaps for the selected role. Keep practising "
            "your existing skills and build projects to demonstrate "
            "your knowledge."
        )

    gap_text = ", ".join(gaps)

    return (
        f"Your selected career goal is {profile.get('target_role', 'your target role')}.\n\n"
        f"Based on your current skill profile, the main areas "
        f"to focus on are: **{gap_text}**.\n\n"
        "Start with the highest-priority skills and build your "
        "knowledge gradually. Practise each skill through small "
        "exercises before using it in a complete project."
    )


def roadmap_guidance_fallback(roadmap_df, analysis, profile):
    """
    Provides guidance for the generated learning roadmap.
    """

    gaps = get_priority_skills(analysis)

    if not gaps:
        return (
            "Your roadmap currently has no major priority gaps. "
            "Continue strengthening your existing skills through "
            "practice and practical projects."
        )

    first_skills = gaps[:3]

    skill_text = ", ".join(first_skills)

    return (
        "### Your Roadmap Guidance\n\n"
        f"Your roadmap is designed around your target role: "
        f"**{profile.get('target_role', 'your selected role')}**.\n\n"
        f"Your first focus should be: **{skill_text}**.\n\n"
        "### How to follow this roadmap\n"
        "1. Start with the first skill in your roadmap.\n"
        "2. Learn its fundamentals before moving to advanced topics.\n"
        "3. Practise through small coding exercises or activities.\n"
        "4. Move to the next skill after you understand the basics.\n"
        "5. Apply what you learn through practical projects.\n\n"
        "The roadmap contains illustrative planning estimates. "
        "Adjust the pace according to your understanding and "
        "available weekly study hours."
    )


def generate_projects_fallback(analysis, profile):
    """
    Generates three template-based project ideas using
    the user's current skill gaps.
    """

    gaps = get_priority_skills(analysis)

    if not gaps:
        gaps = ["Python", "SQL", "Data Analysis"]

    project_templates = {
        "python": {
            "title": "Python Data Exploration Toolkit",
            "problem_statement": (
                "Create a small application that loads, cleans, "
                "analyses and summarizes a dataset."
            ),
            "suggested_tools": ["Python", "Pandas", "Matplotlib"],
            "difficulty": "Beginner",
            "expected_deliverable": (
                "A Python project containing data-cleaning "
                "functions, analysis and visualizations."
            ),
            "evaluation_criteria": [
                "Correct data loading and cleaning",
                "Clear analysis and visualizations",
                "Readable and organized code"
            ]
        },
        "sql": {
            "title": "Sales Database Analysis",
            "problem_statement": (
                "Design a database for a small business and use "
                "SQL queries to explore its sales performance."
            ),
            "suggested_tools": ["SQL", "SQLite", "Database Design"],
            "difficulty": "Beginner",
            "expected_deliverable": (
                "A database with sample records and a collection "
                "of useful SQL analysis queries."
            ),
            "evaluation_criteria": [
                "Well-designed tables and relationships",
                "Correct SQL queries",
                "Meaningful business insights"
            ]
        },
        "data analysis": {
            "title": "Exploratory Data Analysis Report",
            "problem_statement": (
                "Explore a real-world dataset and discover "
                "patterns, trends and unusual observations."
            ),
            "suggested_tools": ["Python", "Pandas", "Matplotlib"],
            "difficulty": "Beginner",
            "expected_deliverable": (
                "A Jupyter Notebook containing an exploratory "
                "analysis and visual report."
            ),
            "evaluation_criteria": [
                "Appropriate data exploration",
                "Useful charts and visualizations",
                "Clear findings and conclusions"
            ]
        },
        "machine learning": {
            "title": "Beginner Prediction Model",
            "problem_statement": (
                "Build a simple machine learning model to make "
                "predictions using a structured dataset."
            ),
            "suggested_tools": [
                "Python",
                "Pandas",
                "Scikit-learn"
            ],
            "difficulty": "Intermediate",
            "expected_deliverable": (
                "A notebook containing data preparation, "
                "model training and evaluation."
            ),
            "evaluation_criteria": [
                "Correct data preparation",
                "Appropriate model selection",
                "Clear model evaluation"
            ]
        },
        "statistics": {
            "title": "Statistical Data Investigation",
            "problem_statement": (
                "Investigate a dataset using descriptive "
                "statistics and basic statistical methods."
            ),
            "suggested_tools": ["Python", "Pandas", "NumPy"],
            "difficulty": "Beginner",
            "expected_deliverable": (
                "A report explaining statistical findings "
                "with supporting calculations."
            ),
            "evaluation_criteria": [
                "Correct statistical calculations",
                "Clear interpretation of results",
                "Well-organized report"
            ]
        }
    }

    projects = []
    used_titles = []

    for skill in gaps:
        skill_key = skill.lower()

        template = project_templates.get(skill_key)

        if template is None:
            template = {
                "title": f"{skill} Practice Project",
                "problem_statement": (
                    f"Create a practical project that helps you "
                    f"understand and apply {skill}."
                ),
                "suggested_tools": [skill],
                "difficulty": "Beginner",
                "expected_deliverable": (
                    f"A completed project demonstrating your "
                    f"understanding of {skill}."
                ),
                "evaluation_criteria": [
                    f"Correct use of {skill}",
                    "Clear and organized implementation",
                    "Practical application of the concept"
                ]
            }

        if template["title"] in used_titles:
            continue

        project = {
            "title": template["title"],
            "problem_statement": template["problem_statement"],
            "required_skills": [skill],
            "suggested_tools": template["suggested_tools"],
            "difficulty": template["difficulty"],
            "expected_deliverable": template["expected_deliverable"],
            "evaluation_criteria": template["evaluation_criteria"]
        }

        projects.append(project)
        used_titles.append(template["title"])

        if len(projects) == 3:
            break

    return projects