def handle_task_created(payload: dict):
    task_id = payload["task_id"]

    print(f"Processing task_created for task_id={task_id}")
