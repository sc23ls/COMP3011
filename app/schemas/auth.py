from pydantic import BaseModel, field_validator
import re


class RegisterRequest(BaseModel):

    username: str
    password: str
    confirm_password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):

        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain a capital letter")

        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain a number")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain a special character")

        return value

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, value, values):

        if "password" in values.data and value != values.data["password"]:
            raise ValueError("Passwords do not match")

        return value


class LoginRequest(BaseModel):

    username: str
    password: str