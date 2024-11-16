from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    database: bool = Field(examples=[True])
    redis: bool = Field(examples=[True])
