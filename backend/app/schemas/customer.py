from pydantic import BaseModel, Field, field_validator


class FavoriteStatus(BaseModel):
    car_id: int
    saved: bool


class ComparisonUpdate(BaseModel):
    car_ids: list[int] = Field(max_length=3)

    @field_validator("car_ids")
    @classmethod
    def unique_cars(cls, value: list[int]) -> list[int]:
        if len(value) != len(set(value)):
            raise ValueError("Comparison cannot contain duplicate vehicles")
        return value
