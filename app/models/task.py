from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.task_project import task_project


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    tags = relationship("TaskTag", cascade="all, delete-orphan", back_populates="task")
    projects = relationship("Project", secondary=task_project, back_populates="tasks")


class TaskTag(Base):
    __tablename__ = "task_tags"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    value = Column(String(64), nullable=False, index=True)

    task = relationship("Task", back_populates="tags")
