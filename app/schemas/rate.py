from pydantic import BaseModel, field_validator
from datetime import date as DateType


class RateCreate(BaseModel):

    base_currency: str
    target_currency: str
    rate: float
    date: DateType


class RateUpdate(BaseModel):

    rate: float


class RatePatch(BaseModel):

    base_currency: str | None = None
    target_currency: str | None = None
    rate: float | None = None
    date: DateType | None = None

    @field_validator("rate")
    @classmethod
    def validate_rate(cls, value):
        if value is not None and value <= 0:
            raise ValueError("rate must be greater than 0")
        return value


class RateBulkCreate(BaseModel):

    rates: list[RateCreate]

    @field_validator("rates")
    @classmethod
    def validate_rates(cls, value):
        if not value:
            raise ValueError("At least one rate is required")
        if len(value) > 200:
            raise ValueError("A maximum of 200 rates can be created per request")
        return value


class RateBulkDelete(BaseModel):

    ids: list[int]

    @field_validator("ids")
    @classmethod
    def validate_ids(cls, value):
        if not value:
            raise ValueError("At least one id is required")
        if len(value) > 500:
            raise ValueError("A maximum of 500 ids can be deleted per request")
        if any(rate_id <= 0 for rate_id in value):
            raise ValueError("All ids must be positive integers")
        return sorted(set(value))
