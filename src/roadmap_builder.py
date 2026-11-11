
import math

import pandas as pd


def build_roadmap(
    priority_gaps: list,
    catalog: pd.DataFrame,
    weekly_hours: int
) -> pd.DataFrame:
    """
    Build an illustrative learning roadmap from priority gaps.

    Prerequisites that are also gaps are scheduled before
    the skills that depend on them.
    """

    columns = [
        "order",
        "skill",
        "status",
        "hours_needed",
        "start_week",
        "end_week",
        "prerequisite",
        "note",
    ]

    if not priority_gaps:
        return pd.DataFrame(columns=columns)

    if weekly_hours <= 0:
        raise ValueError("weekly_hours must be greater than zero.")

    catalog_data = catalog.copy()

    catalog_lookup = catalog_data.set_index("skill").to_dict("index")

    pending = {
        gap["skill"]: gap.copy()
        for gap in priority_gaps
    }

    ordered_gaps = []

    # Schedule skills in priority order while respecting prerequisites.
    while pending:

        available = []

        for skill, gap in pending.items():

            prerequisite = catalog_lookup.get(
                skill, {}
            ).get("prerequisite")

            # A skill can be scheduled if its prerequisite is
            # not another remaining gap.
            if (
                pd.isna(prerequisite)
                or prerequisite == ""
                or prerequisite not in pending
            ):
                available.append(gap)

        # Protect against circular prerequisite data.
        if not available:
            raise ValueError(
                "Circular prerequisite dependency found in the catalog."
            )

        # Highest priority first; alphabetical order breaks ties.
        available.sort(
            key=lambda item: (
                -item["priority_score"],
                item["skill"].lower()
            )
        )

        selected = available[0]
        skill = selected["skill"]

        ordered_gaps.append(selected)
        del pending[skill]

    roadmap_rows = []
    cumulative_hours = 0

    for index, gap in enumerate(ordered_gaps, start=1):

        skill = gap["skill"]
        required_level = gap["required_level"]
        student_level = gap["student_level"]

        skill_data = catalog_lookup.get(skill)

        if skill_data is None:
            raise ValueError(
                f"Skill '{skill}' was not found in the catalog."
            )

        estimated_hours = float(
            skill_data["est_hours_to_level"]
        )

        # Estimate time for the missing level fraction.
        hours_needed = max(
            1,
            estimated_hours * (
                required_level - student_level
            ) / 2
        )

        # Determine whether the student has started this skill.
        status = (
            "partial" if student_level > 0 else "missing"
        )

        prerequisite = skill_data.get("prerequisite")

        if pd.isna(prerequisite):
            prerequisite = ""

        # Calculate the week in which this task starts and ends.
        start_week = (
            math.floor(cumulative_hours / weekly_hours) + 1
        )

        cumulative_hours += hours_needed

        end_week = math.ceil(
            cumulative_hours / weekly_hours
        )

        if end_week < start_week:
            end_week = start_week

        if prerequisite:
            note = (
                f"Complete {prerequisite} first if you have not "
                "already learned it. Illustrative planning estimates."
            )
        else:
            note = "Illustrative planning estimates."

        roadmap_rows.append({
            "order": index,
            "skill": skill,
            "status": status,
            "hours_needed": round(hours_needed, 1),
            "start_week": start_week,
            "end_week": end_week,
            "prerequisite": prerequisite,
            "note": note,
        })

    return pd.DataFrame(roadmap_rows, columns=columns)
