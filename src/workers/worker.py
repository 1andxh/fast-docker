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
        job = dequeue()

        try:
            process_job(job)

        except Exception as e:
            print(f"Job failed: {e}")

            retries = job.get("retries", 0)

            if retries < MAX_RETRIES:
                job["retries"] = retries + 1

                print(f"Retring job ({job["retries"]})...")

                enqueue(job)
            else:
                print(print("Max retries reached. Sending to DLQ."))


if __name__ == "__main__":
    worker_loop()
