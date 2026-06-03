import uuid

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserSignupSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    username: str
    password: str


class UserResponseSchema(BaseModel):
    id: uuid.UUID
    username: str
