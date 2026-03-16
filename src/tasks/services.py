from sqlalchemy.orm import Session
from .models import Task
from .schemas import TaskCreate, TaskRead
from sqlalchemy import select
import json
from src.redis import redis_client
from typing import Sequence


def create_task(task: TaskCreate, db: Session) -> Task:
    new_task = Task(title=task.title)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def get_tasks(db: Session):
    # define predictable key
    cache_key = "tasks:list"
    cached = redis_client.get(cache_key)

    #   check redis
    if cached:
        return json.loads(cache_key)

    #   cachec miss? hit db
    stmt = db.execute(select(Task))
    result = stmt.scalars().all()
    tasks = list(result)

    # save to redis for next hit
    tasks_data = [
        {"id": t.id, "title": t.title, "completed": t.completed} for t in tasks
    ]

    redis_client.set(cache_key, json.dumps(tasks_data), ex=60)
    return tasks_data
