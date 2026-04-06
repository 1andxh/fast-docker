from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..db import get_db
from .schemas import TaskCreate, TaskPatch, TaskRead, TaskUpdate
from .services import (
    create_task,
    delete_task,
    get_task,
    get_tasks,
    patch_task,
    update_task,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create(task: TaskCreate, db: Session = Depends(get_db)):
    return create_task(task, db)


@router.get("/", response_model=list[TaskRead])
def get_list(db: Session = Depends(get_db)):
    return get_tasks(db)


@router.get("/{task_id}", response_model=TaskRead)
def get_one(task_id: int, db: Session = Depends(get_db)):
    return get_task(task_id, db)


@router.put("/{task_id}", response_model=TaskRead)
def update(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    return update_task(task_id, payload, db)


@router.patch("/{task_id}", response_model=TaskRead)
def patch(task_id: int, payload: TaskPatch, db: Session = Depends(get_db)):
    return patch_task(task_id, payload, db)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(task_id: int, db: Session = Depends(get_db)):
    delete_task(task_id, db)
    return None
