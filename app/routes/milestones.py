

from datetime import date

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import DbSession
from app.models import Milestone, MilestoneStatus, Project
from app.routes.projects import get_project_or_404
from app.schemas.milestone import MilestoneCreate, MilestoneRead, MilestoneUpdate

router = APIRouter(tags=["milestones"])


def get_milestone_or_404(milestone_id: int, db: Session) -> Milestone:
    milestone = db.get(Milestone, milestone_id)
    if milestone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")
    return milestone


def check_due_date(due_date: date, project: Project) -> None:
    if not project.start_date <= due_date <= project.end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="due_date must be within the project timeframe",
        )


@router.post(
    "/projects/{project_id}/milestones",
    response_model=MilestoneRead,
    status_code=status.HTTP_201_CREATED,
)
def create_milestone(project_id: int, data: MilestoneCreate, db: DbSession):
    project = get_project_or_404(project_id, db)
    check_due_date(data.due_date, project)

    milestone = Milestone(**data.model_dump(), project_id=project.id)
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


@router.get("/projects/{project_id}/milestones", response_model=list[MilestoneRead])
def list_milestones(project_id: int, db: DbSession):
    project = get_project_or_404(project_id, db)
    query = (
        select(Milestone)
        .where(Milestone.project_id == project.id)
        .order_by(Milestone.due_date)
    )
    return db.scalars(query).all()


@router.get("/milestones/overdue", response_model=list[MilestoneRead])
def list_overdue_milestones(db: DbSession):
    query = (
        select(Milestone)
        .where(Milestone.due_date < date.today())
        .where(Milestone.status != MilestoneStatus.DONE)
        .order_by(Milestone.due_date)
    )
    return db.scalars(query).all()


@router.get("/milestones/{milestone_id}", response_model=MilestoneRead)
def get_milestone(milestone_id: int, db: DbSession):
    return get_milestone_or_404(milestone_id, db)


@router.patch("/milestones/{milestone_id}", response_model=MilestoneRead)
def update_milestone(milestone_id: int, data: MilestoneUpdate, db: DbSession):
    milestone = get_milestone_or_404(milestone_id, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(milestone, field, value)

    check_due_date(milestone.due_date, milestone.project)

    db.commit()
    db.refresh(milestone)
    return milestone


@router.delete("/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_milestone(milestone_id: int, db: DbSession):
    milestone = get_milestone_or_404(milestone_id, db)
    db.delete(milestone)
    db.commit()