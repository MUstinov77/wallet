import uuid

from pydantic import BaseModel, ConfigDict


class UserSignupSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    username: str
    password: str


class UserResponseSchema(BaseModel):
    id: uuid.UUID
    username: str
    api_token: str
