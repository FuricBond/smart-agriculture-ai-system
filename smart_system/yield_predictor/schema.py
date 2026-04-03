"""
yield_predictor/schema.py
=========================
Pydantic input schema for the AI-based Yield Prediction pipeline.

Validates: crop, state (mapped to Area), season, year.
"""

from pydantic import BaseModel, validator

VALID_SEASONS = {"Kharif", "Rabi", "Whole Year", "Autumn", "Summer", "Winter"}


class YieldInput(BaseModel):
    crop: str
    state: str
    season: str
    year: int

    @validator("crop")
    def val_crop(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("crop cannot be empty")
        return v

    @validator("state")
    def val_state(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("state cannot be empty")
        return v

    @validator("season")
    def val_season(cls, v: str) -> str:
        v = v.strip()
        if v not in VALID_SEASONS:
            raise ValueError(
                f"season must be one of: {sorted(VALID_SEASONS)}"
            )
        return v

    @validator("year")
    def val_year(cls, v: int) -> int:
        if not (1990 <= v <= 2035):
            raise ValueError("year must be between 1990 and 2035")
        return v