from pydantic import BaseModel, ConfigDict


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    csrf_token: str

    model_config = ConfigDict(from_attributes=True)
