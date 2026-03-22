from .dispatcher import handlers
from ..queue import dequeue, enqueue

import time

MAX_RETRIES = 3


def process_job(job):
    job_type = job["type"]
    payload = job["payload"]

    handler = handlers.get(job_type)

    if not handler:
        print(f"Unknown job type: {job_type}")
        return

    handler(payload)


def worker_loop():
    print("Worker started...")

    while True:
        job = dequeue()  # get job from queue
        if not job:
            continue

        try:  # try to execute job
            process_job(job)
            print(f"Successfully finished job {job["id"]}")

        except Exception as e:  # worker handles failures
            print(f"Job failed: {e}")

            retries = job.get("retries", 0)

            if retries < MAX_RETRIES:
                job["retries"] = retries + 1
                delay = 2**retries  # add backooff between retries

                print(f"Retring job...[retry_count: {job["retries"]}/3]")
                time.sleep(delay)

                enqueue(job)  # queue the job again
            else:
                print(print("Max retries reached. Sending to DLQ."))


if __name__ == "__main__":
    worker_loop()
