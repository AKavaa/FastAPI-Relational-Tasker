from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.project import Project
from app.models.task import Task, TaskTag
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/api")


def _task_to_out(task: Task) -> TaskOut:
    return TaskOut(
        id=task.id,
        title=task.title,
        description=task.description,
        tags=[t.value for t in task.tags],
        project_ids=[p.id for p in task.projects],
    )


@router.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(Project).where(Project.name == payload.name))
    if exists:
        raise HTTPException(status_code=409, detail="Project name already exists")
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return list(db.scalars(select(Project)).all())


@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    updates = payload.model_dump(exclude_unset=True)
    if "name" in updates and updates["name"] != project.name:
        exists = db.scalar(select(Project).where(Project.name == updates["name"]))
        if exists:
            raise HTTPException(status_code=409, detail="Project name already exists")

    for key, value in updates.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()


@router.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(title=payload.title, description=payload.description)
    tag_values = list(dict.fromkeys([tag.strip().lower() for tag in payload.tags if tag.strip()]))
    task.tags = [TaskTag(value=value) for value in tag_values]

    if payload.project_ids:
        projects = list(db.scalars(select(Project).where(Project.id.in_(payload.project_ids))).all())
        if len(projects) != len(set(payload.project_ids)):
            raise HTTPException(status_code=400, detail="One or more projects not found")
        task.projects = projects

    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_to_out(task)


@router.get("/tasks", response_model=list[TaskOut])
def list_tasks(tag: str | None = Query(default=None), db: Session = Depends(get_db)):
    if tag:
        tag_normalized = tag.strip().lower()
        tasks = list(
            db.scalars(
                select(Task).join(TaskTag).where(TaskTag.value == tag_normalized).distinct()
            ).all()
        )
    else:
        tasks = list(db.scalars(select(Task)).all())
    return [_task_to_out(task) for task in tasks]


@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return _task_to_out(task)


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    updates = payload.model_dump(exclude_unset=True)
    if "title" in updates:
        task.title = updates["title"]
    if "description" in updates:
        task.description = updates["description"]
    if "tags" in updates:
        tag_values = list(dict.fromkeys([tag.strip().lower() for tag in updates["tags"] if tag.strip()]))
        task.tags = [TaskTag(value=value) for value in tag_values]
    if "project_ids" in updates:
        ids = updates["project_ids"]
        projects = list(db.scalars(select(Project).where(Project.id.in_(ids))).all()) if ids else []
        if ids is not None and len(projects) != len(set(ids)):
            raise HTTPException(status_code=400, detail="One or more projects not found")
        task.projects = projects

    db.commit()
    db.refresh(task)
    return _task_to_out(task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()


@router.get("/projects/{project_id}/tasks", response_model=list[TaskOut])
def list_tasks_by_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return [_task_to_out(task) for task in project.tasks]
