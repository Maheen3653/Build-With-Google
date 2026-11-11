from pathlib import Path

import pandas as pd


# Project data directory
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_skills_catalog() -> pd.DataFrame:
    """Load the skills catalog CSV from the project's data folder."""
    file_path = DATA_DIR / "skills_catalog.csv"
    return pd.read_csv(file_path)


def load_roles_skills() -> pd.DataFrame:
    """Load the role requirements CSV from the project's data folder."""
    file_path = DATA_DIR / "roles_skills.csv"
    return pd.read_csv(file_path)


def validate_data(catalog: pd.DataFrame, roles: pd.DataFrame) -> list[str]:
    """
    Validate the skills catalog and role requirements datasets.

    Returns a list of validation problems.
    An empty list means both datasets are valid.
    """

    problems = []

    catalog_columns = [
        "skill",
        "category",
        "prerequisite",
        "est_hours_to_level",
        "description"
    ]

    roles_columns = [
        "role",
        "skill",
        "category",
        "importance",
        "required_level",
        "data_status"
    ]

    # 1. Check whether required columns exist
    missing_catalog_columns = [
        column for column in catalog_columns
        if column not in catalog.columns
    ]

    missing_roles_columns = [
        column for column in roles_columns
        if column not in roles.columns
    ]

    if missing_catalog_columns:
        problems.append(
            f"Skills catalog is missing columns: {missing_catalog_columns}"
        )

    if missing_roles_columns:
        problems.append(
            f"Roles skills is missing columns: {missing_roles_columns}"
        )

    # Stop if required columns are missing to avoid KeyErrors
    if missing_catalog_columns or missing_roles_columns:
        return problems

    # 2. Check whether datasets are empty
    if catalog.empty:
        problems.append("Skills catalog is empty.")

    if roles.empty:
        problems.append("Roles skills dataset is empty.")

    if catalog.empty or roles.empty:
        return problems

    # 3. Check for missing values
    # prerequisite is optional, so blank/NaN values are allowed.
    for column in catalog_columns:
        if column == "prerequisite":
            continue

        if catalog[column].isna().any():
            problems.append(
                f"Skills catalog contains missing values in: {column}"
            )

    for column in roles_columns:
        if roles[column].isna().any():
            problems.append(
                f"Roles skills contains missing values in: {column}"
            )

    # Stop further checks if important values are missing
    if any(catalog[column].isna().any()
           for column in catalog_columns if column != "prerequisite"):
        return problems

    if any(roles[column].isna().any() for column in roles_columns):
        return problems

    # 4. Check importance and required_level
    # Both must be integers between 1 and 3.
    for column in ["importance", "required_level"]:

        values = pd.to_numeric(roles[column], errors="coerce")

        invalid_values = (
            values.isna()
            | (values % 1 != 0)
            | (values < 1)
            | (values > 3)
        )

        if invalid_values.any():
            problems.append(
                f"{column} must contain integers between 1 and 3."
            )

    # 5. Check whether every role skill exists in the catalog
    catalog_skills = set(catalog["skill"])
    role_skills = set(roles["skill"])

    unknown_skills = role_skills - catalog_skills

    for skill in sorted(unknown_skills):
        problems.append(
            f"Unknown skill found in roles dataset: {skill}"
        )

    # 6. Check duplicate role-skill combinations
    duplicates = roles.duplicated(subset=["role", "skill"])

    if duplicates.any():
        problems.append(
            "Duplicate role-skill combinations found."
        )

    # 7. Check prerequisites
    # Blank prerequisites are allowed.
    for prerequisite in catalog["prerequisite"]:

        if pd.notna(prerequisite) and prerequisite != "":
            if prerequisite not in catalog_skills:
                problems.append(
                    f"Unknown prerequisite found: {prerequisite}"
                )

    # 8. Check data_status
    if not (roles["data_status"] == "illustrative").all():
        problems.append(
            "Every data_status value must be 'illustrative'."
        )

    return problems

def get_roles(roles: pd.DataFrame) -> list[str]:
    """Return sorted unique role names."""
    return sorted(roles["role"].unique().tolist())


def get_role_requirements(
    roles: pd.DataFrame,
    role: str
) -> pd.DataFrame:
    """Return all skill requirements belonging to one role."""
    return roles[roles["role"] == role].copy()