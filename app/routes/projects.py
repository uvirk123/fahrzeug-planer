


from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import DbSession
from app.models import Project
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_or_404(project_id: int, db: Session) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, db: DbSession):
    project = Project(**data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectRead])
def list_projects(db: DbSession):
    return db.scalars(select(Project).order_by(Project.id)).all()


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: DbSession):
    return get_project_or_404(project_id, db)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, data: ProjectUpdate, db: DbSession):
    project = get_project_or_404(project_id, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    if project.end_date < project.start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="end_date must not be before start_date",
        )

    outside = [
        m for m in project.milestones
        if not project.start_date <= m.due_date <= project.end_date
    ]
    if outside:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="existing milestones would fall outside the project timeframe",
        )

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: DbSession):
    project = get_project_or_404(project_id, db)
    db.delete(project)
    db.commit()