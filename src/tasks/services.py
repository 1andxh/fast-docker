from sqlalchemy.orm import Session
from .models import Task
from .schemas import TaskCreate, TaskRead
from sqlalchemy import select


def create_task(task: TaskCreate, db: Session) -> Task:
    new_task = Task(title=task.title)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def get_tasks(db: Session) -> list[TaskRead]:
    stmt = db.execute(select(Task))
    tasks = stmt.scalars().all()
    return list(tasks)
