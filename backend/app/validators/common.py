"""Common validators for API inputs."""

import re
from typing import Annotated

from fastapi import HTTPException, Path
from pydantic import BaseModel, Field, field_validator


class TeamNameValidator(BaseModel):
    """Validator for team name input."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Team name (letters, spaces, hyphens, periods only)",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate team name format.

        Args:
            v: Team name to validate

        Returns:
            Cleaned team name

        Raises:
            ValueError: If name is invalid
        """
        if not v or len(v.strip()) == 0:
            raise ValueError("Team name cannot be empty")

        # Clean the input
        v = v.strip()

        # Check length
        if len(v) > 100:
            raise ValueError("Team name too long (max 100 characters)")

        # Check for valid characters (letters, spaces, hyphens, periods)
        if not re.match(r"^[a-zA-Z\s\-\.]+$", v):
            raise ValueError("Team name can only contain letters, spaces, hyphens, and periods")

        # Check for SQL injection patterns
        sql_patterns = [
            r"(?i)(select|insert|update|delete|drop|create|alter|exec|execute|union|script)",
            r"[;'\"]",
            r"--",
            r"/\*.*\*/",
        ]
        for pattern in sql_patterns:
            if re.search(pattern, v):
                raise ValueError("Invalid characters in team name")

        return v


def validate_team_name(team_name: str) -> str:
    """Validate team name using Path parameter.

    Args:
        team_name: Team name from URL path

    Returns:
        Validated team name

    Raises:
        HTTPException: If validation fails
    """
    try:
        validator = TeamNameValidator(name=team_name)
        return validator.name
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# FastAPI Path parameter with validation
TeamNamePath = Annotated[
    str,
    Path(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z\s\-\.]+$",
        description="Team name (letters, spaces, hyphens, periods only)",
    ),
]
