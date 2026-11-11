
import pandas as pd
import pytest

from src.skill_matcher import analyze_skills
from src.roadmap_builder import build_roadmap


def make_catalog():
    return pd.DataFrame({
        "skill": ["Python", "SQL", "Excel", "Pandas"],
        "category": [
            "Programming",
            "Data Analysis",
            "Data Analysis",
            "Data Analysis"
        ],
        "prerequisite": ["", "", "", "Python"],
        "est_hours_to_level": [40, 25, 15, 20],
        "description": [
            "Python basics",
            "SQL basics",
            "Excel basics",
            "Pandas basics"
        ]
    })


def make_requirements():
    return pd.DataFrame({
        "role": [
            "Data Analyst",
            "Data Analyst",
            "Data Analyst"
        ],
        "skill": ["SQL", "Excel", "Python"],
        "category": [
            "Data Analysis",
            "Data Analysis",
            "Programming"
        ],
        "importance": [3, 3, 2],
        "required_level": [2, 2, 2],
        "data_status": [
            "illustrative",
            "illustrative",
            "illustrative"
        ]
    })


# --------------------------------------------------
# 1. Hand-calculated Phase 5 example
# --------------------------------------------------

def test_hand_calculated_data_analyst_example():
    catalog = make_catalog()
    requirements = make_requirements()

    profile = {
        "Python": 2,
        "Excel": 1,
        "SQL": 0
    }

    result = analyze_skills(
        profile,
        requirements,
        catalog
    )

    # SQL:     3 * (0 / 2) = 0
    # Excel:   3 * (1 / 2) = 1.5
    # Python:  2 * (2 / 2) = 2
    #
    # Weighted coverage = (3.5 / 8) * 100 = 43.75%

    assert result["weighted_coverage_pct"] == 43.8

    # Only Python is fully matched.
    # Simple coverage = (1 / 3) * 100 = 33.3%

    assert result["simple_coverage_pct"] == 33.3

    assert len(result["matched"]) == 1
    assert len(result["partial"]) == 1
    assert len(result["missing"]) == 1


# --------------------------------------------------
# 2. All skills matched
# --------------------------------------------------

def test_all_skills_matched():
    result = analyze_skills(
        {
            "Python": 3,
            "SQL": 3,
            "Excel": 3
        },
        make_requirements(),
        make_catalog()
    )

    assert result["weighted_coverage_pct"] == 100.0
    assert result["simple_coverage_pct"] == 100.0
    assert len(result["matched"]) == 3
    assert result["partial"] == []
    assert result["missing"] == []
    assert result["priority_gaps"] == []


# --------------------------------------------------
# 3. No skills matched
# --------------------------------------------------

def test_no_skills_matched():
    result = analyze_skills(
        {},
        make_requirements(),
        make_catalog()
    )

    assert result["weighted_coverage_pct"] == 0.0
    assert result["simple_coverage_pct"] == 0.0
    assert result["matched"] == []
    assert result["partial"] == []
    assert len(result["missing"]) == 3


# --------------------------------------------------
# 4. One partial skill
# --------------------------------------------------

def test_one_partial_skill():
    requirements = pd.DataFrame({
        "role": ["Data Analyst"],
        "skill": ["Python"],
        "category": ["Programming"],
        "importance": [3],
        "required_level": [2],
        "data_status": ["illustrative"]
    })

    result = analyze_skills(
        {"Python": 1},
        requirements,
        make_catalog()
    )

    # Credit = 1 / 2 = 0.5
    assert result["weighted_coverage_pct"] == 50.0
    assert result["simple_coverage_pct"] == 0.0
    assert len(result["partial"]) == 1


# --------------------------------------------------
# 5. Priority ordering
# --------------------------------------------------

def test_priority_ordering():
    result = analyze_skills(
        {},
        make_requirements(),
        make_catalog()
    )

    # SQL and Excel both score 3.
    # Python scores 2.
    assert [
        gap["skill"]
        for gap in result["priority_gaps"]
    ] == ["Excel", "SQL", "Python"]


# --------------------------------------------------
# 6. Extra skills are ignored in role scoring
# --------------------------------------------------

def test_unknown_student_skill_is_extra():
    result = analyze_skills(
        {
            "Python": 2,
            "Machine Learning": 3
        },
        make_requirements(),
        make_catalog()
    )

    assert result["weighted_coverage_pct"] == 25.0
    assert result["extra_skills"] == ["Machine Learning"]


# --------------------------------------------------
# 7. Empty role requirements
# --------------------------------------------------

def test_empty_role():
    empty_requirements = pd.DataFrame(
        columns=[
            "role",
            "skill",
            "category",
            "importance",
            "required_level",
            "data_status"
        ]
    )

    result = analyze_skills(
        {"Python": 2},
        empty_requirements,
        make_catalog()
    )

    assert result["weighted_coverage_pct"] == 0.0
    assert result["simple_coverage_pct"] == 0.0
    assert result["empty"] is True
    assert result["priority_gaps"] == []


# --------------------------------------------------
# 8. Invalid student levels are clamped
# --------------------------------------------------

def test_level_clamping():
    result = analyze_skills(
        {
            "Python": 8,
            "SQL": -2,
            "Excel": 1
        },
        make_requirements(),
        make_catalog()
    )

    # Python 8 becomes 3 and is matched.
    # SQL -2 becomes 0 and is missing.
    # Excel remains 1 and is partial.

    assert result["matched"][0]["student_level"] == 3
    assert result["missing"][0]["student_level"] == 0
    assert result["partial"][0]["student_level"] == 1


# --------------------------------------------------
# 9. Weighted and simple coverage can differ
# --------------------------------------------------

def test_weighted_and_simple_coverage_differ():
    result = analyze_skills(
        {"Python": 2},
        make_requirements(),
        make_catalog()
    )

    assert result["weighted_coverage_pct"] == 25.0
    assert result["simple_coverage_pct"] == 33.3


# --------------------------------------------------
# 10. Roadmap prerequisite ordering
# --------------------------------------------------

def test_roadmap_prerequisite_comes_first():
    catalog = make_catalog()

    # Pandas has a higher priority, but Python is its prerequisite.
    gaps = [
        {
            "skill": "Pandas",
            "importance": 3,
            "required_level": 2,
            "student_level": 0,
            "gap_fraction": 1.0,
            "priority_score": 3.0
        },
        {
            "skill": "Python",
            "importance": 1,
            "required_level": 2,
            "student_level": 0,
            "gap_fraction": 1.0,
            "priority_score": 1.0
        }
    ]

    roadmap = build_roadmap(
        gaps,
        catalog,
        weekly_hours=10
    )

    assert roadmap.iloc[0]["skill"] == "Python"
    assert roadmap.iloc[1]["skill"] == "Pandas"


# --------------------------------------------------
# 11. Roadmap hours calculation
# --------------------------------------------------

def test_roadmap_hours_calculation():
    catalog = make_catalog()

    gaps = [
        {
            "skill": "Python",
            "importance": 2,
            "required_level": 2,
            "student_level": 1,
            "gap_fraction": 0.5,
            "priority_score": 1.0
        }
    ]

    roadmap = build_roadmap(
        gaps,
        catalog,
        weekly_hours=10
    )

    # Python: 40 * (2 - 1) / 2 = 20 hours.
    assert roadmap.iloc[0]["hours_needed"] == 20.0

    assert roadmap.iloc[0]["start_week"] == 1
    assert roadmap.iloc[0]["end_week"] == 2


# --------------------------------------------------
# 12. Empty roadmap
# --------------------------------------------------

def test_empty_roadmap():
    roadmap = build_roadmap(
        [],
        make_catalog(),
        weekly_hours=10
    )

    assert roadmap.empty
    assert list(roadmap.columns) == [
        "order",
        "skill",
        "status",
        "hours_needed",
        "start_week",
        "end_week",
        "prerequisite",
        "note"
    ]


# --------------------------------------------------
# 13. Invalid weekly hours
# --------------------------------------------------

def test_invalid_weekly_hours():
    gaps = [
        {
            "skill": "Python",
            "importance": 2,
            "required_level": 2,
            "student_level": 0,
            "gap_fraction": 1.0,
            "priority_score": 2.0
        }
    ]

    with pytest.raises(ValueError):
        build_roadmap(
            gaps,
            make_catalog(),
            weekly_hours=0
        )
