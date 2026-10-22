

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def check_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")
        return self


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int