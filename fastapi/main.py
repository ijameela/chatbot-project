
from fastapi import FastAPI, Path, Query
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime

app = FastAPI()

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[datetime] = None
    priority: int = Field(1, ge=1, le=5)
    tags: List[str] = Field(default_factory=list)

    @validator('title')
    def title_must_be_meaningful(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Title must be meaningful (at least 3 characters)')
        return v.strip()

    @validator('due_date')
    def due_date_must_be_future(cls, v):
        if v and v < datetime.now():
            raise ValueError('Due date must be in the future')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        # Convert tags to lowercase
        tags = [tag.lower() for tag in v]
        # Remove duplicates while preserving order
        unique_tags = list(dict.fromkeys(tags))
        return unique_tags   

# Task model
class Task(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: int = 1
    tags: List[str] = []
    completed: bool = False

    

# In-memory database
tasks = {}


# GET tasks with query parameters
@app.get("/tasks/search/")
def search_tasks(
    title: Optional[str] = Query(None, description="Search by title"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="Filter by priority"),
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of tasks to return")
):
    filtered_tasks = {}

    for task_id, task in tasks.items():
        if title and title.lower() not in task.title.lower():
            continue
        if priority and task.priority != priority:
            continue
        filtered_tasks[task_id] = task

    # Apply pagination
    start = skip
    end = skip + limit
    return dict(list(filtered_tasks.items())[start:end])

# POST new task
@app.post("/tasks/")
def create_task(task: Task):
    task_id = len(tasks) + 1
    tasks[task_id] = task
    return {"task_id": task_id, **task.dict()}

# GET all tasks
@app.get("/tasks/")
def get_tasks():
    return tasks

# GET single task
@app.get("/tasks/{task_id}")
def get_task(task_id: int = Path(..., title="The ID of the task to get")):
    if task_id not in tasks:
        return {"error": "Task not found"}
    return tasks[task_id]

# PUT update task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    if task_id not in tasks:
        return {"error": "Task not found"}
    tasks[task_id] = task
    return {"task_id": task_id, **task.dict()}

# DELETE task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    if task_id not in tasks:
        return {"error": "Task not found"}
    del tasks[task_id]
    return {"message": "Task deleted"}
