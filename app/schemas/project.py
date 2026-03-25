from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    budget: float = Field(ge=0)
    description: str | None = None
    hours_used: float = Field(ge=0, default=0)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    budget: float | None = Field(default=None, ge=0)
    description: str | None = None
    hours_used: float | None = Field(default=None, ge=0)


class ProjectOut(ProjectBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
