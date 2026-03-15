from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..db import get_db
from .schemas import TaskCreate, TaskRead
from .services import get_tasks, create_task

router = APIRouter()


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create(task: TaskCreate, db: Session = Depends(get_db)):
    return create_task(task, db)


@router.get("/", response_model=list[TaskRead])
def get_list(db: Session = Depends(get_db)):
    return get_tasks(db)
