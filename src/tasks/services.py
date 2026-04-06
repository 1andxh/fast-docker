import json
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.redis import redis_client

from .models import Task
from .schemas import TaskCreate, TaskPatch, TaskUpdate


CACHE_KEY = "tasks:list"


def _invalidate_tasks_cache() -> None:
    redis_client.delete(CACHE_KEY)


def _serialize_task(task: Task) -> dict[str, Any]:
    return {"id": task.id, "title": task.title, "completed": task.completed}


def _get_task_or_404(task_id: int, db: Session) -> Task:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return task


def create_task(task: TaskCreate, db: Session) -> Task:
    new_task = Task(title=task.title)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    _invalidate_tasks_cache()
    return new_task


def get_tasks(db: Session) -> list[dict[str, Any]]:
    cached = redis_client.get(CACHE_KEY)

    if cached:
        cached_tasks: list[dict[str, Any]] = json.loads(cached)
        return cached_tasks

    stmt = db.execute(select(Task))
    tasks = list(stmt.scalars().all())

    tasks_data: list[dict[str, Any]] = []
    for task in tasks:
        tasks_data.append(_serialize_task(task))

    redis_client.set(CACHE_KEY, json.dumps(tasks_data), ex=60)
    return tasks_data


def get_task(task_id: int, db: Session) -> Task:
    return _get_task_or_404(task_id, db)


def update_task(task_id: int, payload: TaskUpdate, db: Session) -> Task:
    task = _get_task_or_404(task_id, db)

    task.title = payload.title
    task.completed = payload.completed

    db.commit()
    db.refresh(task)
    _invalidate_tasks_cache()
    return task


def patch_task(task_id: int, payload: TaskPatch, db: Session) -> Task:
    task = _get_task_or_404(task_id, db)

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    _invalidate_tasks_cache()
    return task


def delete_task(task_id: int, db: Session) -> None:
    task = _get_task_or_404(task_id, db)
    db.delete(task)
    db.commit()
    _invalidate_tasks_cache()
