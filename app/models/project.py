from sqlalchemy import Column, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.task_project import task_project


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    budget = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    hours_used = Column(Float, nullable=False, default=0)

    tasks = relationship("Task", secondary=task_project, back_populates="projects")
