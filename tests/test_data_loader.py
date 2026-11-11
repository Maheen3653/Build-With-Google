
import pandas as pd

from src.data_loader import (
    validate_data,
    get_roles,
    get_role_requirements
)


def create_catalog():
    """Create a small sample skills catalog for testing."""
    return pd.DataFrame({
        "skill": ["Python", "SQL", "Pandas"],
        "category": ["Programming", "Data Analysis", "Data Analysis"],
        "prerequisite": ["", "", "Python"],
        "est_hours_to_level": [40, 25, 20],
        "description": [
            "Learn Python",
            "Learn SQL",
            "Learn Pandas"
        ]
    })


def create_roles():
    """Create a small sample role requirements dataset."""
    return pd.DataFrame({
        "role": ["Data Analyst", "Data Analyst"],
        "skill": ["Python", "SQL"],
        "category": ["Programming", "Data Analysis"],
        "importance": [3, 2],
        "required_level": [2, 2],
        "data_status": ["illustrative", "illustrative"]
    })


def test_valid_data():
    """Valid datasets should return no problems."""
    catalog = create_catalog()
    roles = create_roles()

    problems = validate_data(catalog, roles)

    assert problems == []


def test_missing_column():
    """Missing required columns should be reported."""
    catalog = create_catalog()
    roles = create_roles()

    roles = roles.drop(columns=["importance"])

    problems = validate_data(catalog, roles)

    assert any("importance" in problem for problem in problems)


def test_invalid_importance():
    """Importance values outside 1-3 should be rejected."""
    catalog = create_catalog()
    roles = create_roles()

    roles.loc[0, "importance"] = 5

    problems = validate_data(catalog, roles)

    assert any("importance" in problem for problem in problems)


def test_unknown_skill():
    """Skills not found in the catalog should be reported."""
    catalog = create_catalog()
    roles = create_roles()

    roles.loc[0, "skill"] = "Deep Learning"

    problems = validate_data(catalog, roles)

    assert any("Deep Learning" in problem for problem in problems)


def test_duplicate_row():
    """Duplicate role-skill combinations should be rejected."""
    catalog = create_catalog()
    roles = create_roles()

    roles = pd.concat(
        [roles, roles.iloc[[0]]],
        ignore_index=True
    )

    problems = validate_data(catalog, roles)

    assert any("Duplicate" in problem for problem in problems)


def test_get_roles():
    """Role names should be unique and sorted."""
    roles = create_roles()

    roles.loc[2] = [
        "Data Scientist",
        "Python",
        "Programming",
        3,
        2,
        "illustrative"
    ]

    assert get_roles(roles) == [
        "Data Analyst",
        "Data Scientist"
    ]


def test_get_role_requirements():
    """Only requirements for the requested role should be returned."""
    roles = create_roles()

    result = get_role_requirements(roles, "Data Analyst")

    assert len(result) == 2
    assert all(result["role"] == "Data Analyst")
