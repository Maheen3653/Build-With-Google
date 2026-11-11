
import pandas as pd


def analyze_skills(
    profile_skills: dict,
    role_requirements: pd.DataFrame,
    catalog: pd.DataFrame
) -> dict:
    """
    Compare a student's skill levels with the requirements of a selected role.

    Calculates weighted coverage, simple coverage, skill gaps, priority scores,
    strengths, and category-wise coverage.
    """

    requirements = role_requirements.copy()
    catalog_data = catalog.copy()

    extra_skills = [
        skill
        for skill in profile_skills
        if skill not in requirements["skill"].tolist()
    ]

    # Handle an empty role requirement list.
    if requirements.empty:
        return {
            "role": "",
            "weighted_coverage_pct": 0.0,
            "simple_coverage_pct": 0.0,
            "matched": [],
            "partial": [],
            "missing": [],
            "priority_gaps": [],
            "strengths": [],
            "by_category": {},
            "extra_skills": extra_skills,
            "empty": True,
        }

    # Get prerequisite information from the skills catalog.
    prerequisites = dict(
        zip(catalog_data["skill"], catalog_data["prerequisite"])
    )

    matched = []
    partial = []
    missing = []
    priority_gaps = []
    strengths = []

    total_weight = 0
    earned_weight = 0

    category_totals = {}
    category_earned = {}

    for _, requirement in requirements.iterrows():

        skill = requirement["skill"]
        category = requirement["category"]
        importance = float(requirement["importance"])
        required_level = int(requirement["required_level"])

        # Get the student's level. If the skill is absent, use 0.
        try:
            student_level = int(profile_skills.get(skill, 0))
        except (ValueError, TypeError):
            student_level = 0

        # Keep the student level between 0 and 3.
        student_level = max(0, min(student_level, 3))

        # Calculate skill credit.
        credit = min(student_level, required_level) / required_level

        weighted_credit = importance * credit

        total_weight += importance
        earned_weight += weighted_credit

        # Track category-wise coverage.
        category_totals[category] = (
            category_totals.get(category, 0) + importance
        )

        category_earned[category] = (
            category_earned.get(category, 0) + weighted_credit
        )

        skill_info = {
            "skill": skill,
            "category": category,
            "importance": importance,
            "required_level": required_level,
            "student_level": student_level,
        }

        # Determine the skill status.
        if student_level >= required_level:

            matched.append(skill_info)

            if importance >= 2:
                strengths.append(skill)

        elif student_level > 0:

            partial.append(skill_info)

        else:

            missing.append(skill_info)

        # Calculate the remaining gap.
        gap_fraction = (
            required_level - min(student_level, required_level)
        ) / required_level

        priority_score = importance * gap_fraction

        if gap_fraction > 0:
            priority_gaps.append({
                "skill": skill,
                "importance": importance,
                "required_level": required_level,
                "student_level": student_level,
                "gap_fraction": gap_fraction,
                "priority_score": priority_score,
            })

    # Calculate weighted coverage percentage.
    weighted_coverage_pct = (
        100 * earned_weight / total_weight
        if total_weight > 0
        else 0.0
    )

    # Calculate simple coverage percentage.
    simple_coverage_pct = (
        100 * len(matched) / len(requirements)
    )

    # Calculate coverage for each category.
    by_category = {}

    for category in category_totals:
        category_coverage = (
            100 * category_earned[category] / category_totals[category]
        )

        by_category[category] = round(category_coverage, 1)

    # Identify skills that are prerequisites for other incomplete skills.
    gap_skill_names = {
        item["skill"] for item in priority_gaps
    }

    # Find skills that are prerequisites for other incomplete skills.
    prerequisite_skills = {
        prerequisites.get(item["skill"])
        for item in priority_gaps
        if pd.notna(prerequisites.get(item["skill"]))
        and prerequisites.get(item["skill"]) != ""
        and prerequisites.get(item["skill"]) in gap_skill_names
    }

    def gap_sort_key(gap):
        return (
            -gap["priority_score"],
            0 if gap["skill"] in prerequisite_skills else 1,
            gap["skill"].lower(),
        )

    priority_gaps.sort(key=gap_sort_key)

    return {
        "role": requirements.iloc[0]["role"],
        "weighted_coverage_pct": round(weighted_coverage_pct, 1),
        "simple_coverage_pct": round(simple_coverage_pct, 1),
        "matched": matched,
        "partial": partial,
        "missing": missing,
        "priority_gaps": priority_gaps,
        "strengths": strengths,
        "by_category": by_category,
        "extra_skills": extra_skills,
        "empty": False,
    }
