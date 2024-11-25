from pydantic import BaseModel, ConfigDict, Field


class HealthCheckResponse(BaseModel):
    database: bool = Field(examples=[True])
    redis: bool = Field(examples=[True])

    model_config = ConfigDict(from_attributes=True)
