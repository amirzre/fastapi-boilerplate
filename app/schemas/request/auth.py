from pydantic import BaseModel, EmailStr, Field


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(description="User Email")
    password: str = Field(description="User Password")
