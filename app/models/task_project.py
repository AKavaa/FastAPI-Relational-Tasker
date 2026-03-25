from sqlalchemy import Column, ForeignKey, Integer, Table, UniqueConstraint

from app.db.database import Base

task_project = Table(
    "task_project",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("project_id", Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("task_id", "project_id", name="uq_task_project"),
)
