from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    tags: list[str] = Field(default_factory=list)


class TaskCreate(TaskBase):
    project_ids: list[int] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    tags: list[str] | None = None
    project_ids: list[int] | None = None


class TaskOut(TaskBase):
    id: int
    project_ids: list[int] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
