

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.milestone import MilestoneStatus


class MilestoneCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    due_date: date
    status: MilestoneStatus = MilestoneStatus.PLANNED


class MilestoneUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    due_date: date | None = None
    status: MilestoneStatus | None = None


class MilestoneRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    title: str
    due_date: date
    status: MilestoneStatus